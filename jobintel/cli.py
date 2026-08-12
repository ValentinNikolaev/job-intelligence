from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable, Sequence

import yaml

from .api_usage import ApiUsageLog
from .catalog import generate_catalog
from .manual_status_log import ManualStatusEvent, append_manual_status_event
from .applications import (
    ApplicationGenerator,
    CodexApplicationDraftClient,
    HostMarkdownDocxConverter,
    PreparationSummary,
    resolve_job_directories,
    validate_application_draft,
)
from .collector import Collector, discover_collectors
from .config import load_env
from .matching import (
    AnalysisSummary,
    CodexMatchDraftClient,
    MatchAnalyzer,
    analysis_should_skip_status,
    build_analysis_pack,
    dump_analysis_pack,
    load_analysis_pack,
    publish_analysis_batch,
)
from .models import CollectorSummary, NormalizedJob
from .prefilter import RejectedRegistry, load_company_retry_rules, prefilter_job
from .registry import Registry
from .workflows import WorkflowPolicy, load_workflow_policy
from .triage import should_skip_model, write_triage
from .usage import CodexUsageLog
from .workflow_lock import (
    LOCK_ENV_TOKEN,
    WorkflowLockError,
    acquire_workflow_lock,
    release_workflow_lock,
    workflow_lock,
    workflow_lock_status,
)


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect vacancies into a local filesystem registry.")
    parser.add_argument(
        "target", help="collector name, 'all', 'list', 'add-manual', 'reindex', 'catalog', 'top', 'doctor', 'api', 'triage', 'usage', 'status', 'pending', 'analyze', 'analyze-batch', 'validate-application', 'workflow-lock', or 'prepare'"
    )
    parser.add_argument("arguments", nargs="*", help="target-specific arguments")
    parser.add_argument("--sources", type=Path, help="sources directory (default: <project>/sources)")
    parser.add_argument("--registry", type=Path, help="registry directory (default: <project>/registry)")
    parser.add_argument("--env", type=Path, help=".env path (default: <sources>/.env)")
    parser.add_argument(
        "--profile",
        type=Path,
        action="append",
        help="Candidate Profile file; repeat to combine authoritative files",
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="Codex draft file/directory to validate and publish",
    )
    parser.add_argument(
        "--workflow",
        help="configured Codex workflow: analyze or prepare",
    )
    parser.add_argument(
        "--document",
        choices=("cv", "cover-letter", "analysis", "interview-preparation"),
        help="prepare or validate exactly one application document; default: full package",
    )
    parser.add_argument(
        "--model-profile",
        help="model profile from config/codex-workflows.yaml; defaults to the workflow profile",
    )
    parser.add_argument(
        "--collection-limit",
        type=int,
        help="maximum fetched vacancies to process per collector; default: 100; use 0 for unlimited",
    )
    parser.add_argument("--limit", type=int, help="maximum rows for API queue commands")
    parser.add_argument("--pack", type=Path, help="analysis pack path for pending analyze")
    parser.add_argument("--run-id", help="external Codex run identifier for usage recording")
    parser.add_argument("--model", help="model label for usage recording")
    parser.add_argument("--input-tokens", type=int, help="reported input token count")
    parser.add_argument("--output-tokens", type=int, help="reported output token count")
    parser.add_argument("--total-tokens", type=int, help="reported total token count")
    parser.add_argument("--credits", type=float, help="reported credit cost")
    parser.add_argument("--measurement", choices=("reported", "estimated"), default="reported")
    parser.add_argument("--note", help="optional usage note")
    parser.add_argument("--reason", help="status only: user/LLM reason for a manual status change")
    parser.add_argument("--actor", default="codex", help="status only: actor recording the manual decision")
    parser.add_argument("--interaction-id", help="status only: optional user/LLM interaction identifier")
    parser.add_argument("--status-note", help="status only: optional note for the manual status audit log")
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON where supported")
    parser.add_argument("--force", action="store_true", help="force analysis even when cached versions match")
    parser.add_argument(
        "--lock-timeout-seconds",
        type=float,
        default=0,
        help="seconds to wait for the collection/analysis workflow lock; default: fail fast",
    )
    parser.add_argument(
        "--lock-token-file",
        type=Path,
        help="workflow-lock only: file used to persist or read a lock token",
    )
    parser.add_argument(
        "--ci",
        action="store_true",
        help="doctor only: skip host-local Codex runtime checks unavailable on CI runners",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = _parser().parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    sources_dir = (args.sources or project_root / "sources").resolve()
    registry_dir = (args.registry or project_root / "registry").resolve()
    env_path = (args.env or sources_dir / ".env").resolve()

    target = args.target.casefold()
    if args.document and target not in {"prepare", "pending", "validate-application"}:
        print(
            "--document is valid only with prepare, pending prepare, or validate-application",
            file=sys.stderr,
        )
        return 2
    if target == "workflow-lock":
        return _run_workflow_lock(args, project_root)
    if args.ci and target != "doctor":
        print("--ci is only valid with doctor", file=sys.stderr)
        return 2
    if target == "catalog":
        if args.arguments or args.force or args.profile or args.input or args.workflow or args.model_profile:
            print("Usage: python run.py catalog", file=sys.stderr)
            return 2
        try:
            result = generate_catalog(registry_dir, project_root / "catalog")
        except Exception as exc:
            print(f"Catalog error: {exc}", file=sys.stderr)
            return 1
        mode = "monthly" if result.monthly else "single-file"
        changed = ", ".join(result.changed_files) or "none"
        print(f"Catalog: {result.vacancies} vacancies, {mode}, changed: {changed}")
        return 0
    if target in {"add-manual", "manual"}:
        if args.arguments or args.force or args.profile or args.workflow or args.model_profile or not args.input:
            print("Usage: python run.py add-manual --input <manual-job.yaml>", file=sys.stderr)
            return 2
        try:
            payload = _read_yaml_file(args.input, "manual job draft")
            job = _manual_job_from_payload(payload)
            with workflow_lock(project_root, "manual:add", timeout_seconds=args.lock_timeout_seconds):
                registry = Registry(registry_dir, cache_entries=True)
                result = registry.upsert(job)
                registry.regenerate_index()
        except Exception as exc:
            print(f"Manual job error: {exc}", file=sys.stderr)
            return 1
        print(f"Manual job {result.status}: {result.directory} ({result.vacancy_id})")
        return 0
    if target == "status":
        if (
            len(args.arguments) != 2
            or args.force
            or args.profile
            or args.input
            or args.workflow
            or args.model_profile
        ):
            print(
                "Usage: python run.py status <job-directory|vacancy-id> <status> "
                "[--reason <reason>] [--actor <actor>] [--interaction-id <id>] [--status-note <note>]",
                file=sys.stderr,
            )
            return 2
        try:
            with workflow_lock(project_root, "status", timeout_seconds=args.lock_timeout_seconds):
                directories = resolve_job_directories(registry_dir, args.arguments[0])
                if len(directories) != 1:
                    raise ValueError("status updates exactly one vacancy")

                def audit_status_change(
                    before: dict[str, Any], after: dict[str, Any], directory: Path
                ) -> None:
                    append_manual_status_event(
                        registry_dir / "manual-status-log.yaml",
                        ManualStatusEvent(
                            changed_at=str(after["updated_at"]),
                            vacancy_id=str(after["id"]),
                            directory=directory.name,
                            company=str(after.get("company") or ""),
                            title=str(after.get("title") or ""),
                            from_status=str(before.get("status") or ""),
                            to_status=str(after.get("status") or ""),
                            reason=(args.reason or "unspecified").strip() or "unspecified",
                            actor=(args.actor or "codex").strip() or "codex",
                            interaction_id=(args.interaction_id or "").strip() or None,
                            note=(args.status_note or "").strip() or None,
                        ),
                    )

                changed = Registry(registry_dir).update_status(
                    args.arguments[0], args.arguments[1], on_updated=audit_status_change
                )
        except Exception as exc:
            print(f"Status error: {exc}", file=sys.stderr)
            return 1
        print("Status updated." if changed else "Status already current.")
        print("Regenerate the catalog through the separate $generate-vacancy-catalog process.")
        return 0

    if target == "triage":
        if len(args.arguments) > 1 or args.input or args.workflow or args.model_profile or args.force or args.json or args.pack:
            print("Usage: python run.py triage [all|job-directory|vacancy-id]", file=sys.stderr)
            return 2
        try:
            with workflow_lock(project_root, "triage", timeout_seconds=args.lock_timeout_seconds):
                selector = args.arguments[0] if args.arguments else "all"
                directories = resolve_job_directories(registry_dir, selector)
                counts = {"high": 0, "medium": 0, "low": 0, "skip_model": 0}
                for directory in directories:
                    result = write_triage(directory)
                    counts[str(result["confidence"])] += 1
                    counts["skip_model"] += int(bool(result["skip_model"]))
            print(json.dumps({"triaged": len(directories), **counts}, indent=2, sort_keys=True))
            return 0
        except (Exception, WorkflowLockError) as exc:
            print(f"Triage error: {exc}", file=sys.stderr)
            return 1

    if target == "validate-application":
        if (
            len(args.arguments) != 1
            or not args.input
            or args.profile
            or args.workflow
            or args.model_profile
            or args.force
            or args.json
            or args.pack
        ):
            print(
                "Usage: python run.py validate-application "
                "<job-directory|vacancy-id> --input <draft-directory> "
                "[--document cv|cover-letter|analysis|interview-preparation]",
                file=sys.stderr,
            )
            return 2
        try:
            directories = resolve_job_directories(registry_dir, args.arguments[0])
            if len(directories) != 1:
                raise ValueError("validate-application requires exactly one vacancy")
            directory = directories[0]
            draft_directory = _preparation_draft_directory(
                args.input,
                directory,
                selection_size=1,
                document=args.document,
            )
            validate_application_draft(
                directory,
                draft_directory,
                document=args.document,
            )
        except Exception as exc:
            print(f"Application draft validation failed: {exc}", file=sys.stderr)
            return 1
        print(f"Application draft valid: {directory.name}")
        return 0

    if target == "usage":
        return _run_usage(args, project_root, registry_dir)

    if target == "reindex":
        if args.arguments or args.force or args.profile or args.input or args.workflow or args.model_profile:
            print("Usage: python run.py reindex", file=sys.stderr)
            return 2
        try:
            with workflow_lock(project_root, "registry:reindex", timeout_seconds=args.lock_timeout_seconds):
                changed = Registry(registry_dir).regenerate_index()
        except Exception as exc:
            print(f"Index error: {exc}", file=sys.stderr)
            return 1
        print("Index regenerated." if changed else "Index already current.")
        return 0

    if target == "top":
        if args.force or args.profile or args.input or args.workflow or args.model_profile:
            print("Usage: python run.py top [limit]", file=sys.stderr)
            return 2
        try:
            limit = _top_limit(args.arguments)
            rows = _top_vacancies(registry_dir, limit=limit)
        except Exception as exc:
            print(f"Top vacancies error: {exc}", file=sys.stderr)
            return 1
        if not rows:
            print("Top vacancies: no analyzed active vacancies.")
            return 0
        print(f"Top vacancies: {len(rows)}")
        for index, row in enumerate(rows, start=1):
            print(
                f"{index}. {row['score']}/100 "
                f"{row['company']} — {row['title']} "
                f"({row['recommendation']}, {row['directory']})"
            )
            if row["url"]:
                print(f"   {row['url']}")
        return 0

    if target == "api":
        return _run_api(args, project_root, sources_dir, registry_dir, env_path)

    if target == "doctor":
        return _run_doctor(args, project_root, sources_dir, registry_dir, env_path)

    try:
        config = load_env(env_path)
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if target == "analyze":
        return _run_analysis(args, config, project_root, registry_dir)
    if target == "analyze-batch":
        return _run_analysis_batch(args, config, project_root, registry_dir)
    if target == "prepare":
        return _run_preparation(args, config, project_root, registry_dir)
    if target == "pending":
        return _run_pending(args, config, project_root, registry_dir)

    if args.force or args.profile or args.input or args.workflow or args.model_profile or args.limit or args.json:
        print(
            "--force, --profile, --input, --workflow, --model-profile, --limit, and --json are only valid "
            "with supported targets.",
            file=sys.stderr,
        )
        return 2
    try:
        collection_limit = _collection_limit(args.collection_limit, config)
    except ValueError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if target == "ashby" and args.arguments[:1] == ["discover"]:
        if len(args.arguments) == 1:
            print("Ashby discovery needs at least one board name or jobs.ashbyhq.com URL.", file=sys.stderr)
            return 2
        try:
            from discovery.ashby.discovery import discover_boards

            return discover_boards(
                args.arguments[1:],
                config,
                sources_dir / "ashby" / "config.yaml",
            )
        except Exception as exc:
            print(f"Ashby discovery error: {exc}", file=sys.stderr)
            return 1

    try:
        collectors = discover_collectors(sources_dir, config)
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if args.arguments:
        print(f"Unexpected arguments for '{args.target}': {' '.join(args.arguments)}", file=sys.stderr)
        return 2

    if target == "list":
        if collectors:
            print("Available collectors:")
            for name in sorted(collectors):
                print(f"  {name}")
        else:
            print("No collectors found.")
        return 0

    registry = Registry(registry_dir, cache_entries=True)
    rejected_registry = RejectedRegistry(registry_dir, cache_entries=True)
    try:
        company_retry_rules = load_company_retry_rules(
            project_root / "config" / "application-profile.yaml"
        )
    except ValueError as exc:
        print(f"Profile policy error: {exc}", file=sys.stderr)
        return 2
    api_usage = ApiUsageLog(registry_dir / "source-api-usage.yaml")
    run_started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")

    if target == "all":
        selected: Iterable[tuple[str, Collector]] = sorted(collectors.items())
    elif target in collectors:
        selected = [(target, collectors[target])]
    else:
        available = ", ".join(sorted(collectors)) or "none"
        print(f"Unknown collector '{args.target}'. Available: {available}", file=sys.stderr)
        return 2

    try:
        with workflow_lock(project_root, f"collection:{target}", timeout_seconds=args.lock_timeout_seconds):
            failed = False
            collected = _collect_selected_jobs(
                selected,
                limit=collection_limit,
                error_log_dir=registry_dir,
            )
            for name, summary, jobs in collected:
                summary = _store_collected_jobs(
                    name,
                    summary,
                    jobs,
                    registry,
                    rejected_registry,
                    company_retry_rules=company_retry_rules,
                )
                _print_summary(summary)
                try:
                    api_usage.record(summary, run_started_at=run_started_at)
                except Exception as exc:
                    failed = True
                    print(f"API usage log error: {exc}", file=sys.stderr)
                failed = failed or summary.errors > 0
            registry.regenerate_index()
    except (Exception, WorkflowLockError) as exc:
        print(f"Collection error: {exc}", file=sys.stderr)
        return 1
    return 1 if failed else 0


def _run_collector(
    name: str,
    collector: Collector,
    registry: Registry,
    rejected_registry: RejectedRegistry,
    *,
    limit: int | None,
    company_retry_rules=(),
) -> CollectorSummary:
    summary, jobs = _fetch_collector_jobs(name, collector, limit=limit)
    return _store_collected_jobs(
        name,
        summary,
        jobs,
        registry,
        rejected_registry,
        company_retry_rules=company_retry_rules,
    )


def _collect_selected_jobs(
    selected: Iterable[tuple[str, Collector]],
    *,
    limit: int | None,
    error_log_dir: Path | None = None,
) -> list[tuple[str, CollectorSummary, list[NormalizedJob]]]:
    collector_items = list(selected)
    if len(collector_items) <= 1:
        return [
            (name, *(_fetch_collector_jobs(name, collector, limit=limit, error_log_dir=error_log_dir)))
            for name, collector in collector_items
        ]

    results: dict[str, tuple[CollectorSummary, list[NormalizedJob]]] = {}
    with ThreadPoolExecutor(max_workers=len(collector_items)) as executor:
        futures = {
            executor.submit(_fetch_collector_jobs, name, collector, limit=limit, error_log_dir=error_log_dir): name
            for name, collector in collector_items
        }
        for future in as_completed(futures):
            name = futures[future]
            results[name] = future.result()
    return [(name, *results[name]) for name, _ in collector_items]


def _fetch_collector_jobs(
    name: str,
    collector: Collector,
    *,
    limit: int | None,
    error_log_dir: Path | None = None,
) -> tuple[CollectorSummary, list[NormalizedJob]]:
    summary = CollectorSummary(source=name)
    jobs: list[NormalizedJob] = []
    try:
        for job in collector.fetch():
            if limit is not None and summary.fetched >= limit:
                summary.limit_reached = True
                break
            summary.fetched += 1
            jobs.append(job)
    except Exception as exc:
        summary.errors += 1
        print(f"{name}: collection failed: {exc}", file=sys.stderr)
        if name == "cleanjobdata" and error_log_dir is not None:
            error_log_dir.mkdir(parents=True, exist_ok=True)
            (error_log_dir / "cleanjobdata-latest-error.txt").write_text(
                f"{type(exc).__name__}: {exc}\n", encoding="utf-8"
            )
    collector_errors = getattr(collector, "errors", 0)
    if isinstance(collector_errors, int) and collector_errors > 0:
        summary.errors += collector_errors
    requests = getattr(collector, "api_requests", 0)
    if isinstance(requests, int) and requests > 0:
        summary.api_requests = requests
    return summary, jobs


def _store_collected_jobs(
    name: str,
    summary: CollectorSummary,
    jobs: Sequence[NormalizedJob],
    registry: Registry,
    rejected_registry: RejectedRegistry,
    *,
    company_retry_rules=(),
) -> CollectorSummary:
    for job in jobs:
        try:
            rejection = prefilter_job(job, company_retry_rules=company_retry_rules)
            if rejection is not None:
                rejected_registry.upsert(job, rejection)
                summary.record("rejected")
                continue
            result = registry.upsert(job)
            summary.record(result.status)
        except Exception as exc:
            summary.errors += 1
            print(
                f"{name}: failed to store {job.source_job_id}: {exc}",
                file=sys.stderr,
            )
    return summary


def _collection_limit(cli_limit: int | None, config: dict[str, str]) -> int | None:
    raw = cli_limit if cli_limit is not None else config.get("JOBINTEL_COLLECTION_LIMIT", "100")
    if raw in (None, ""):
        return 100
    try:
        limit = int(raw)
    except (TypeError, ValueError) as exc:
        raise ValueError("JOBINTEL_COLLECTION_LIMIT must be a positive integer or 0 for unlimited") from exc
    if limit < 0:
        raise ValueError("JOBINTEL_COLLECTION_LIMIT must be a positive integer or 0 for unlimited")
    return None if limit == 0 else limit


def _print_summary(summary: CollectorSummary) -> None:
    print(f"Source: {summary.source}")
    print(f"Fetched: {summary.fetched}")
    print(f"Created: {summary.created}")
    print(f"Updated: {summary.updated}")
    print(f"Duplicates merged: {summary.merged}")
    print(f"Unchanged: {summary.unchanged}")
    print(f"Rejected: {summary.rejected}")
    print(f"Errors: {summary.errors}")
    print(f"API requests: {summary.api_requests}")
    if summary.limit_reached:
        print(f"Limit reached: {summary.limit_reached}")


def _top_limit(arguments: list[str]) -> int:
    if len(arguments) > 1:
        raise ValueError("usage: python run.py top [limit]")
    if not arguments:
        return 20
    try:
        limit = int(arguments[0])
    except ValueError as exc:
        raise ValueError("top limit must be a positive integer") from exc
    if limit <= 0:
        raise ValueError("top limit must be a positive integer")
    return limit


def _top_vacancies(registry_dir: Path, *, limit: int = 5) -> list[dict[str, Any]]:
    inactive_statuses = {"rejected", "withdrawn", "closed"}
    rows: list[dict[str, Any]] = []
    for meta_path in sorted((registry_dir / "jobs").glob("*/meta.yaml")):
        match_path = meta_path.parent / "match.yaml"
        if not match_path.is_file():
            continue
        meta = _read_yaml_file(meta_path, "vacancy metadata")
        if str(meta.get("status", "")).strip().casefold() in inactive_statuses:
            continue
        match = _read_yaml_file(match_path, "match analysis")
        score = match.get("score")
        recommendation = match.get("recommendation")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            raise ValueError(f"match analysis has invalid score: {match_path}")
        if recommendation not in {
            "strong_match",
            "match",
            "possible_match",
            "weak_match",
            "not_match",
        }:
            raise ValueError(f"match analysis has invalid recommendation: {match_path}")
        sources = meta.get("sources")
        url = ""
        if isinstance(sources, list) and sources:
            first_source = sources[0]
            if isinstance(first_source, dict):
                url = str(first_source.get("url") or "")
        rows.append(
            {
                "score": score,
                "recommendation": str(recommendation).replace("_", " "),
                "discovered_at": str(meta.get("discovered_at") or ""),
                "company": str(meta.get("company") or ""),
                "title": str(meta.get("title") or ""),
                "directory": meta_path.parent.name,
                "url": url,
            }
        )
    rows.sort(
        key=lambda row: (
            int(row["score"]),
            str(row["discovered_at"]),
            str(row["directory"]),
        ),
        reverse=True,
    )
    return rows[:limit]


def _read_yaml_file(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read {label} {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"{label} must be a YAML mapping: {path}")
    return loaded


def _manual_job_from_payload(payload: dict[str, Any]) -> NormalizedJob:
    source_url = _required_manual_text(payload, "source_url")
    title = _required_manual_text(payload, "title")
    company = _required_manual_text(payload, "company")
    description = _required_manual_text(payload, "description")
    source_job_id = _optional_manual_text(payload.get("source_job_id")) or _manual_source_job_id(source_url)
    source_metadata: dict[str, Any] = {}
    for key in ("source_name", "source_notes", "apply_url", "contact", "extraction_notes"):
        value = _optional_manual_text(payload.get(key))
        if value is not None:
            source_metadata[key] = value
    job = NormalizedJob(
        source="manual",
        source_job_id=source_job_id,
        source_url=source_url,
        title=title,
        company=company,
        description=description,
        company_url=_optional_manual_text(payload.get("company_url")),
        location=_optional_manual_text(payload.get("location")),
        remote=_optional_manual_bool(payload.get("remote")),
        employment_type=_optional_manual_text(payload.get("employment_type")),
        published_at=_optional_manual_text(payload.get("published_at")),
        company_description=_optional_manual_text(payload.get("company_description")),
        source_metadata=source_metadata,
        analysis_priority=_manual_priority(payload.get("analysis_priority")),
    )
    job.validate()
    return job


def _required_manual_text(payload: dict[str, Any], field: str) -> str:
    value = _optional_manual_text(payload.get(field))
    if value is None:
        raise ValueError(f"manual job draft missing required field: {field}")
    return value


def _optional_manual_text(value: Any) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("manual job text fields must be strings")
    cleaned = value.strip()
    return cleaned or None


def _optional_manual_bool(value: Any) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ValueError("manual job remote must be true, false, or omitted")


def _manual_priority(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("manual job analysis_priority must be an integer from 0 to 100")
    if not 0 <= value <= 100:
        raise ValueError("manual job analysis_priority must be an integer from 0 to 100")
    return value


def _manual_source_job_id(source_url: str) -> str:
    digest = hashlib.sha256(source_url.encode("utf-8")).hexdigest()[:16]
    return f"manual-{digest}"


def _run_api(
    args: argparse.Namespace,
    project_root: Path,
    sources_dir: Path,
    registry_dir: Path,
    env_path: Path,
) -> int:
    if args.force or args.input or args.model_profile:
        print("--force, --input, and --model-profile are not valid with api", file=sys.stderr)
        return 2
    if not args.json:
        print("api commands require --json", file=sys.stderr)
        return 2
    if not args.arguments:
        print(
            "Usage: python run.py api <workflow-summary|workflow-limits|source-usage|"
            "codex-usage|catalog-vacancies|queues> --json",
            file=sys.stderr,
        )
        return 2

    try:
        config = load_env(env_path)
    except Exception:
        config = {}
    try:
        profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
        try:
            collection_limit = _collection_limit(args.collection_limit, config)
        except ValueError:
            collection_limit = 100
        from .workflow_api import (
            catalog_vacancies,
            codex_usage,
            queue_response,
            source_usage,
            workflow_limits,
            workflow_summary,
        )

        command = args.arguments[0].replace("_", "-").casefold()
        if command == "workflow-summary":
            payload = workflow_summary(project_root, registry_dir, config, profile_paths)
        elif command == "workflow-limits":
            payload = workflow_limits(project_root, collection_limit)
        elif command == "source-usage":
            payload = source_usage(registry_dir)
        elif command == "codex-usage":
            payload = codex_usage(registry_dir)
        elif command == "catalog-vacancies":
            payload = catalog_vacancies(registry_dir)
        elif command == "queues":
            if len(args.arguments) != 2:
                raise ValueError("api queues requires one workflow: analyze or prepare")
            workflow = args.arguments[1].replace("_", "-")
            payload = queue_response(
                workflow,
                project_root,
                registry_dir,
                profile_paths,
                limit=args.limit,
            )
        else:
            raise ValueError(f"unknown api command: {args.arguments[0]}")
    except Exception as exc:
        print(f"API command failed: {exc}", file=sys.stderr)
        return 1

    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _run_analysis(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    try:
        with workflow_lock(project_root, "analysis:single", timeout_seconds=args.lock_timeout_seconds):
            return _run_analysis_locked(args, config, project_root, registry_dir)
    except WorkflowLockError as exc:
        print(f"Analysis failed: {exc}", file=sys.stderr)
        return 1


def _run_analysis_locked(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    if len(args.arguments) != 1:
        print(
            "Usage: python run.py analyze <job-directory|vacancy-id> --input <draft.yaml> "
            "--workflow analyze [--force]",
            file=sys.stderr,
        )
        return 2
    if not args.input or not args.workflow:
        print("analyze requires --input and --workflow analyze", file=sys.stderr)
        return 2

    try:
        _, model_label = _selected_workflow(
            args.workflow, project_root, {"analyze"}, args.model_profile
        )
        Registry(registry_dir).migrate_metadata()
        profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
        directories = resolve_job_directories(registry_dir, args.arguments[0])
        if len(directories) != 1:
            raise ValueError("analyze publishes exactly one Codex draft at a time")
    except Exception as exc:
        print(f"Analysis configuration error: {exc}", file=sys.stderr)
        return 2

    summary = AnalysisSummary(selected=len(directories))
    for directory in directories:
        try:
            client = CodexMatchDraftClient(args.input, model=model_label)
            analyzer = MatchAnalyzer(registry_dir, profile_paths, client)
            result = analyzer.analyze_directory(directory, force=args.force)
            if result.status == "skipped":
                summary.skipped += 1
            else:
                summary.analyzed += 1
            score = f" ({result.score}/100)" if result.score is not None else ""
            print(f"{directory.name}: {result.status}{score}")
        except Exception as exc:
            summary.errors += 1
            print(f"{directory.name}: analysis failed: {exc}", file=sys.stderr)

    try:
        Registry(registry_dir).regenerate_index()
    except Exception as exc:
        print(f"Index error: {exc}", file=sys.stderr)
        return 1

    print(f"Selected: {summary.selected}")
    print(f"Analyzed: {summary.analyzed}")
    print(f"Skipped unchanged: {summary.skipped}")
    print(f"Errors: {summary.errors}")
    return 1 if summary.errors else 0


def _run_analysis_batch(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    if args.arguments or not args.input or not args.workflow or args.workflow.replace("-", "_") != "analyze":
        print("Usage: python run.py analyze-batch --input <batch.yaml> --workflow analyze", file=sys.stderr)
        return 2
    try:
        with workflow_lock(project_root, "analysis:batch-publish", timeout_seconds=args.lock_timeout_seconds):
            _, model_label = _selected_workflow(
                args.workflow, project_root, {"analyze"}, args.model_profile
            )
            pack = load_analysis_pack(args.input)
            results = pack.get("results")
            if not isinstance(results, dict):
                raise ValueError("batch input must contain a results mapping keyed by directory")
            profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
            analyzer = MatchAnalyzer(
                registry_dir,
                profile_paths,
                CodexMatchDraftClient(project_root / ".codex-work" / "unused-match.yaml", model=model_label),
            )
            summary = publish_analysis_batch(pack, results, analyzer)
            Registry(registry_dir).regenerate_index()
    except Exception as exc:
        print(f"Batch analysis failed: {exc}", file=sys.stderr)
        return 1
    print(f"Selected: {summary.selected}")
    print(f"Analyzed: {summary.analyzed}")
    print(f"Skipped unchanged: {summary.skipped}")
    print("Errors: 0")
    return 0


def _run_usage(args: argparse.Namespace, project_root: Path, registry_dir: Path) -> int:
    if len(args.arguments) != 1 or args.arguments[0] not in {"record", "summary"}:
        print("Usage: python run.py usage record --workflow <name> --model <label> [usage fields]", file=sys.stderr)
        return 2
    if args.arguments[0] == "summary":
        from .workflow_api import codex_usage

        print(json.dumps(codex_usage(registry_dir), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    if args.model_profile:
        print("usage record accepts --model directly; --model-profile is not valid here", file=sys.stderr)
        return 2
    if not args.workflow or not args.model:
        print("usage record requires --workflow and --model", file=sys.stderr)
        return 2
    try:
        with workflow_lock(project_root, "usage:record", timeout_seconds=args.lock_timeout_seconds):
            run = CodexUsageLog(registry_dir / "codex-usage.yaml").record(
                workflow=args.workflow,
                model=args.model,
                run_id=args.run_id,
                input_tokens=args.input_tokens,
                output_tokens=args.output_tokens,
                total_tokens=args.total_tokens,
                credits=args.credits,
                measurement=args.measurement,
                note=args.note,
            )
    except Exception as exc:
        print(f"Usage record error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(run, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


def _run_workflow_lock(args: argparse.Namespace, project_root: Path) -> int:
    if not args.arguments or args.arguments[0] not in {"acquire", "release", "status"}:
        print(
            "Usage: python run.py workflow-lock <acquire owner|release|status> "
            "[--lock-token-file <path>] [--lock-timeout-seconds <seconds>]",
            file=sys.stderr,
        )
        return 2
    command = args.arguments[0]
    if command == "status":
        if len(args.arguments) != 1:
            print("Usage: python run.py workflow-lock status", file=sys.stderr)
            return 2
        print(json.dumps(workflow_lock_status(project_root), indent=2, sort_keys=True))
        return 0
    if command == "acquire":
        if len(args.arguments) != 2:
            print("Usage: python run.py workflow-lock acquire <owner>", file=sys.stderr)
            return 2
        try:
            lease = acquire_workflow_lock(
                project_root,
                args.arguments[1],
                timeout_seconds=args.lock_timeout_seconds,
            )
        except WorkflowLockError as exc:
            print(f"Workflow lock error: {exc}", file=sys.stderr)
            return 1
        if args.lock_token_file:
            args.lock_token_file.parent.mkdir(parents=True, exist_ok=True)
            args.lock_token_file.write_text(lease.token + "\n", encoding="utf-8")
        print(
            json.dumps(
                {
                    "locked": True,
                    "owner": lease.owner,
                    "path": str(lease.path),
                    "token_env": LOCK_ENV_TOKEN,
                    "token_file": str(args.lock_token_file) if args.lock_token_file else None,
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 0
    if len(args.arguments) != 1:
        print("Usage: python run.py workflow-lock release", file=sys.stderr)
        return 2
    token = os.environ.get(LOCK_ENV_TOKEN, "").strip()
    if args.lock_token_file and args.lock_token_file.is_file():
        token = args.lock_token_file.read_text(encoding="utf-8").strip()
    if not token:
        print(
            f"Workflow lock error: missing lock token; set {LOCK_ENV_TOKEN} or pass --lock-token-file",
            file=sys.stderr,
        )
        return 2
    try:
        release_workflow_lock(project_root, token)
    except WorkflowLockError as exc:
        print(f"Workflow lock error: {exc}", file=sys.stderr)
        return 1
    if args.lock_token_file and args.lock_token_file.exists():
        args.lock_token_file.unlink()
    print(json.dumps({"locked": False}, indent=2, sort_keys=True))
    return 0


def _profile_paths(
    cli_paths: list[Path] | None,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> list[Path]:
    if cli_paths:
        return [path.resolve() for path in cli_paths]
    configured = config.get("CANDIDATE_PROFILE_PATHS", "").strip()
    if configured:
        paths = [Path(value.strip()) for value in configured.split(os.pathsep) if value.strip()]
        return [(path if path.is_absolute() else project_root / path).resolve() for path in paths]
    candidate_dir = registry_dir / "candidate"
    clarification = candidate_dir / "user-confirmed-career-clarifications.md"
    compact = candidate_dir / "match-profile.md"
    if compact.is_file():
        paths = [compact.resolve()]
    else:
        paths = [
            (candidate_dir / "linkedin-profile.md").resolve(),
            (candidate_dir / "backend-engineer-cv.md").resolve(),
        ]
    if clarification.is_file():
        paths.append(clarification.resolve())
    return paths


def _run_preparation(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    try:
        with workflow_lock(project_root, "preparation:batch", timeout_seconds=args.lock_timeout_seconds):
            return _run_preparation_locked(args, config, project_root, registry_dir)
    except WorkflowLockError as exc:
        print(f"Preparation failed: {exc}", file=sys.stderr)
        return 1


def _run_preparation_locked(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    if not args.arguments:
        print(
            "Usage: python run.py prepare <job-directory|vacancy-id> "
            "[<job-directory|vacancy-id> ...] --input <draft-root> "
            "--workflow prepare [--document cv|cover-letter|analysis|interview-preparation] "
            "[--force] (maximum 10 vacancies)",
            file=sys.stderr,
        )
        return 2
    if not args.input or not args.workflow:
        print("prepare requires --input and --workflow", file=sys.stderr)
        return 2

    try:
        policy, model_label = _selected_workflow(
            args.workflow, project_root, {"prepare"}, args.model_profile
        )
        Registry(registry_dir).migrate_metadata()
        profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
        directories = _resolve_explicit_preparation_directories(
            registry_dir,
            args.arguments,
            limit=policy.prepare_batch_size,
        )
        for directory in directories:
            if not _vacancy_is_fresh(directory, policy.prepare_max_age_days):
                raise ValueError(
                    f"{directory.name}: vacancy is older than prepare_max_age_days "
                    f"{policy.prepare_max_age_days}; do not prepare stale vacancies"
                )
            if not _analysis_is_current(
                directory,
                registry_dir,
                profile_paths,
                policy,
                project_root,
                model_profile=args.model_profile,
            ):
                raise ValueError(
                    f"{directory.name}: match analysis is missing or stale; "
                    "run workflow analyze first"
                )
            score = _match_score(directory)
            if not policy.prepare_score_is_eligible(args.workflow, score):
                raise ValueError(
                    f"{directory.name}: "
                    + _ineligible_score_message(policy, args.workflow, score)
                )
    except Exception as exc:
        print(f"Preparation configuration error: {exc}", file=sys.stderr)
        return 2

    summary = PreparationSummary(selected=len(directories))
    for directory in directories:
        try:
            draft_directory = _preparation_draft_directory(
                args.input,
                directory,
                selection_size=len(directories),
                document=args.document,
            )
            generator = ApplicationGenerator(
                registry_dir,
                profile_paths,
                project_root / "prompts" / "vacancy-application.md",
                CodexApplicationDraftClient(
                    draft_directory,
                    model=model_label,
                    document=args.document,
                ),
                HostMarkdownDocxConverter(project_root),
                document=args.document,
            )
            result = generator.generate_directory(directory, force=args.force)
        except Exception as exc:
            summary.errors += 1
            print(f"{directory.name}: preparation failed: {exc}", file=sys.stderr)
            continue
        print(f"{directory.name}: {result.status}")
        if result.status == "skipped":
            summary.skipped += 1
        else:
            summary.prepared += 1

    print(f"Selected: {summary.selected}")
    print(f"Prepared: {summary.prepared}")
    print(f"Skipped unchanged: {summary.skipped}")
    print(f"Errors: {summary.errors}")
    return 1 if summary.errors else 0


def _resolve_explicit_preparation_directories(
    registry_dir: Path,
    selectors: Sequence[str],
    *,
    limit: int,
) -> list[Path]:
    if not selectors:
        raise ValueError("preparation requires at least one explicit vacancy selector")
    if len(selectors) > limit:
        raise ValueError(
            f"preparation accepts at most {limit} vacancies per Codex task; "
            f"received {len(selectors)}"
        )

    directories: list[Path] = []
    selected_by_path: dict[Path, str] = {}
    for selector in selectors:
        if selector.casefold() == "all":
            raise ValueError(
                "automatic preparation selection is disabled; use explicit vacancy IDs "
                "or registry directories"
            )
        matches = resolve_job_directories(registry_dir, selector)
        if len(matches) != 1:
            raise ValueError(f"preparation selector must resolve to one vacancy: {selector}")
        directory = matches[0].resolve()
        previous = selected_by_path.get(directory)
        if previous is not None:
            raise ValueError(
                f"duplicate vacancy selection {selector!r}; already selected as {previous!r}"
            )
        selected_by_path[directory] = selector
        directories.append(directory)
    return directories


def _preparation_draft_directory(
    input_root: Path,
    directory: Path,
    *,
    selection_size: int,
    document: str | None = None,
) -> Path:
    root = input_root.resolve()
    filename = {
        "cv": "cv.md",
        "cover-letter": "cover-letter.md",
        "analysis": "analysis.md",
        "interview-preparation": "interview-preparation.md",
    }.get(document, "cv.md")
    if selection_size == 1 and (root / filename).is_file():
        return root
    return root / directory.name


def _run_pending(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    try:
        with workflow_lock(project_root, "pending", timeout_seconds=args.lock_timeout_seconds):
            return _run_pending_locked(args, config, project_root, registry_dir)
    except WorkflowLockError as exc:
        print(f"Pending check failed: {exc}", file=sys.stderr)
        return 1


def _run_pending_locked(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    if not args.arguments or args.arguments[0] not in {"analyze", "prepare"}:
        print(
            "Usage: python run.py pending analyze [all|job-directory|vacancy-id] "
            "--workflow analyze; or python run.py pending prepare "
            "<job-directory|vacancy-id> [<job-directory|vacancy-id> ...] "
            "--workflow prepare (maximum 10 vacancies)",
            file=sys.stderr,
        )
        return 2
    if not args.workflow:
        print("pending requires --workflow", file=sys.stderr)
        return 2
    if args.input or args.force:
        print("--input and --force are not valid with pending", file=sys.stderr)
        return 2

    stage = args.arguments[0]
    if args.document and stage != "prepare":
        print("--document is valid only with pending prepare", file=sys.stderr)
        return 2
    selectors = args.arguments[1:]
    if stage == "analyze" and len(selectors) > 1:
        print("pending analyze accepts at most one selector", file=sys.stderr)
        return 2
    try:
        allowed = {"analyze"} if stage == "analyze" else {"prepare"}
        policy, model_label = _selected_workflow(
            args.workflow, project_root, allowed, args.model_profile
        )
        Registry(registry_dir).migrate_metadata()
        profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
        if args.pack and stage != "analyze":
            print("--pack is valid only for pending analyze", file=sys.stderr)
            return 2
        if stage == "prepare" and (not selectors or selectors == ["all"]):
            print(
                "Automatic preparation queue is disabled. "
                "Run prepare only for one to ten explicit job directories or vacancy IDs."
            )
            return 0
        if stage == "prepare":
            directories = _resolve_explicit_preparation_directories(
                registry_dir,
                selectors,
                limit=policy.prepare_batch_size,
            )
        else:
            selector = selectors[0] if selectors else "all"
            directories = resolve_job_directories(registry_dir, selector)
        if stage == "analyze":
            directories = sorted(directories, key=_pending_analysis_queue_key, reverse=True)
        if stage == "analyze" and args.pack:
            pack = build_analysis_pack(
                registry_dir,
                profile_paths,
                directories=directories,
                limit=args.limit,
                triage_skip=should_skip_model,
                model=model_label,
            )
            dump_analysis_pack(pack, args.pack.resolve())
            print(f"Analysis pack: {args.pack.resolve()} ({len(pack.items)} vacancies)")
            return 0
        pending_prepare: list[Path] = []
        for directory in directories:
            if stage == "analyze":
                if _vacancy_status_skips_analysis(directory):
                    continue
                if should_skip_model(directory):
                    continue
                checker = MatchAnalyzer(
                    registry_dir,
                    profile_paths,
                    CodexMatchDraftClient(
                        project_root / ".codex-work" / "unused-match.yaml",
                        model=model_label,
                    ),
                )
            else:
                if not _vacancy_is_fresh(directory, policy.prepare_max_age_days):
                    continue
                if not _analysis_is_current(
                    directory,
                    registry_dir,
                    profile_paths,
                    policy,
                    project_root,
                    model_profile=args.model_profile,
                ):
                    continue
                score = _optional_match_score(directory)
                if score is None or not policy.prepare_score_is_eligible(args.workflow, score):
                    continue
                checker = ApplicationGenerator(
                    registry_dir,
                    profile_paths,
                    project_root / "prompts" / "vacancy-application.md",
                    CodexApplicationDraftClient(
                        project_root / ".codex-work" / "unused-application",
                        model=model_label,
                        document=args.document,
                    ),
                    HostMarkdownDocxConverter(project_root),
                    document=args.document,
                )
            if not checker.is_current(directory):
                if stage == "analyze":
                    print(directory)
                else:
                    pending_prepare.append(directory)
        if stage == "prepare":
            for directory in sorted(pending_prepare, key=_pending_prepare_queue_key, reverse=True):
                print(directory)
    except Exception as exc:
        print(f"Pending check failed: {exc}", file=sys.stderr)
        return 1
    return 0


def _selected_workflow(
    requested: str,
    project_root: Path,
    allowed: set[str],
    model_profile: str | None = None,
) -> tuple[WorkflowPolicy, str]:
    policy = load_workflow_policy(project_root / "config" / "codex-workflows.yaml")
    workflow = policy.workflow(requested)
    if workflow.name not in allowed:
        choices = ", ".join(sorted(name.replace("_", "-") for name in allowed))
        raise ValueError(f"workflow {requested!r} is invalid here; expected: {choices}")
    return policy, policy.resolve_model_profile(workflow.name, model_profile).model_label


def _optional_match_score(directory: Path) -> int | None:
    path = directory / "match.yaml"
    if not path.is_file():
        return None
    return _match_score(directory)


def _vacancy_status_skips_analysis(directory: Path) -> bool:
    try:
        meta = _read_yaml_file(directory / "meta.yaml", "vacancy metadata")
    except ValueError:
        return False
    return analysis_should_skip_status(meta)


def _analysis_is_current(
    directory: Path,
    registry_dir: Path,
    profile_paths: list[Path],
    policy: WorkflowPolicy,
    project_root: Path,
    *,
    model_profile: str | None = None,
) -> bool:
    checker = MatchAnalyzer(
        registry_dir,
        profile_paths,
        CodexMatchDraftClient(
            project_root / ".codex-work" / "unused-match.yaml",
            model=policy.resolve_model_profile("analyze", model_profile).model_label,
        ),
    )
    return checker.is_current(directory)


def _match_score(directory: Path) -> int:
    path = directory / "match.yaml"
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"match analysis is required before preparation: {path}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid match analysis YAML {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"match analysis must be a YAML mapping: {path}")
    score = loaded.get("score")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise ValueError(f"match analysis has invalid score: {path}")
    return score


def _pending_analysis_queue_key(directory: Path) -> tuple[int, str, str]:
    try:
        meta = _read_yaml_file(directory / "meta.yaml", "vacancy metadata")
    except ValueError:
        return (0, "", directory.name)
    priority = meta.get("analysis_priority")
    if isinstance(priority, bool) or not isinstance(priority, int) or not 0 <= priority <= 100:
        priority = 0
    return (priority, str(meta.get("discovered_at") or ""), directory.name)


def _pending_prepare_queue_key(directory: Path) -> tuple[int, str, str]:
    score = _optional_match_score(directory) or 0
    try:
        meta = _read_yaml_file(directory / "meta.yaml", "vacancy metadata")
    except ValueError:
        return (score, "", directory.name)
    return (score, str(meta.get("discovered_at") or ""), directory.name)


def _ineligible_score_message(policy: WorkflowPolicy, workflow: str, score: int) -> str:
    del workflow
    if score < policy.prepare_min_score:
        return (
            f"vacancy score {score} is below prepare_min_score {policy.prepare_min_score}; "
            "no application package should be prepared"
        )
    return f"vacancy score {score} is eligible for prepare"


def _vacancy_is_fresh(directory: Path, max_age_days: int) -> bool:
    try:
        meta = _read_yaml_file(directory / "meta.yaml", "vacancy metadata")
    except ValueError:
        return False
    discovered_at = str(meta.get("discovered_at") or "")
    try:
        discovered = datetime.fromisoformat(discovered_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    if discovered.tzinfo is None:
        discovered = discovered.replace(tzinfo=timezone.utc)
    return discovered.astimezone(timezone.utc) >= datetime.now(timezone.utc) - timedelta(days=max_age_days)


def _run_doctor(
    args: argparse.Namespace,
    project_root: Path,
    sources_dir: Path,
    registry_dir: Path,
    env_path: Path,
) -> int:
    if args.arguments or args.force or args.profile or args.input or args.workflow or getattr(args, "model_profile", None):
        print("Usage: python run.py doctor [--ci]", file=sys.stderr)
        return 2
    ci_mode = bool(getattr(args, "ci", False))

    failures: list[str] = []

    def check(label: str, action: object) -> None:
        try:
            if callable(action):
                action()
            print(f"OK: {label}")
        except Exception as exc:
            failures.append(label)
            print(f"ERROR: {label}: {exc}", file=sys.stderr)

    check("workflow policy", lambda: load_workflow_policy(project_root / "config" / "codex-workflows.yaml"))
    try:
        config = load_env(env_path)
        print(f"OK: source environment ({env_path})")
    except Exception as exc:
        config = {}
        failures.append("source environment")
        print(f"ERROR: source environment: {exc}", file=sys.stderr)
    for path in _profile_paths(args.profile, config, project_root, registry_dir):
        check(f"candidate source {path}", lambda path=path: _require_nonempty(path))
    for path in (
        project_root / "prompts" / "vacancy-match.md",
        project_root / "prompts" / "vacancy-application.md",
    ):
        check(f"prompt {path}", lambda path=path: _require_nonempty(path))
    if ci_mode:
        print("SKIP: host-local DOCX converter checks (--ci)")
    else:
        converter = HostMarkdownDocxConverter(project_root)
        check("DOCX converter script", lambda: _require_file(converter.script_path))
        check("DOCX options", lambda: _require_file(converter.options_path))
        if converter.powershell:
            print(f"OK: PowerShell ({converter.powershell})")
        else:
            failures.append("PowerShell")
            print("ERROR: PowerShell executable not found", file=sys.stderr)
    print("NOTE: Codex model, network, and sandbox permissions are configured outside the repository.")
    return 1 if failures else 0


def _require_file(path: Path) -> None:
    if not path.is_file():
        raise FileNotFoundError(path)


def _require_nonempty(path: Path) -> None:
    _require_file(path)
    if not path.read_text(encoding="utf-8").strip():
        raise ValueError("file is empty")
