from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml

from .api_usage import ApiUsageLog
from .catalog import generate_catalog
from .applications import (
    ApplicationGenerator,
    CodexApplicationDraftClient,
    HostMarkdownDocxConverter,
    PreparationSummary,
    resolve_job_directories,
)
from .collector import Collector, discover_collectors
from .config import load_env
from .matching import AnalysisSummary, CodexMatchDraftClient, MatchAnalyzer
from .models import CollectorSummary
from .prefilter import RejectedRegistry, prefilter_job
from .registry import Registry
from .workflows import WorkflowPolicy, load_workflow_policy


def _configure_stdio() -> None:
    for stream in (sys.stdout, sys.stderr):
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None:
            reconfigure(encoding="utf-8", errors="backslashreplace")


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Collect vacancies into a local filesystem registry.")
    parser.add_argument(
        "target", help="collector name, 'all', 'list', 'reindex', 'catalog', 'top', 'doctor', 'status', 'pending', 'analyze', or 'prepare'"
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
        help="configured Codex workflow: analyze, prepare, or prepare-priority",
    )
    parser.add_argument(
        "--collection-limit",
        type=int,
        help="maximum fetched vacancies to process per collector; default: 100; use 0 for unlimited",
    )
    parser.add_argument("--force", action="store_true", help="force analysis even when cached versions match")
    return parser


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    args = _parser().parse_args(argv)
    project_root = Path(__file__).resolve().parents[1]
    sources_dir = (args.sources or project_root / "sources").resolve()
    registry_dir = (args.registry or project_root / "registry").resolve()
    env_path = (args.env or sources_dir / ".env").resolve()

    target = args.target.casefold()
    if target == "catalog":
        if args.arguments or args.force or args.profile or args.input or args.workflow:
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
    if target == "status":
        if (
            len(args.arguments) != 2
            or args.force
            or args.profile
            or args.input
            or args.workflow
        ):
            print("Usage: python run.py status <job-directory|vacancy-id> <status>", file=sys.stderr)
            return 2
        try:
            changed = Registry(registry_dir).update_status(args.arguments[0], args.arguments[1])
        except Exception as exc:
            print(f"Status error: {exc}", file=sys.stderr)
            return 1
        print("Status updated." if changed else "Status already current.")
        print("Regenerate the catalog through the separate $generate-vacancy-catalog process.")
        return 0

    if target == "reindex":
        if args.arguments or args.force or args.profile or args.input or args.workflow:
            print("Usage: python run.py reindex", file=sys.stderr)
            return 2
        try:
            changed = Registry(registry_dir).regenerate_index()
        except Exception as exc:
            print(f"Index error: {exc}", file=sys.stderr)
            return 1
        print("Index regenerated." if changed else "Index already current.")
        return 0

    if target == "top":
        if args.force or args.profile or args.input or args.workflow:
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

    if target == "doctor":
        return _run_doctor(args, project_root, sources_dir, registry_dir, env_path)

    try:
        config = load_env(env_path)
    except Exception as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    if target == "analyze":
        return _run_analysis(args, config, project_root, registry_dir)
    if target == "prepare":
        return _run_preparation(args, config, project_root, registry_dir)
    if target == "pending":
        return _run_pending(args, config, project_root, registry_dir)

    if args.force or args.profile or args.input or args.workflow:
        print(
            "--force, --profile, --input, and --workflow are only valid with "
            "'pending', 'analyze', or 'prepare'.",
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

    registry = Registry(registry_dir)
    rejected_registry = RejectedRegistry(registry_dir)
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

    failed = False
    for name, collector in selected:
        summary = _run_collector(
            name,
            collector,
            registry,
            rejected_registry,
            limit=collection_limit,
        )
        _print_summary(summary)
        try:
            api_usage.record(summary, run_started_at=run_started_at)
        except Exception as exc:
            failed = True
            print(f"API usage log error: {exc}", file=sys.stderr)
        failed = failed or summary.errors > 0

    try:
        registry.regenerate_index()
    except Exception as exc:
        print(f"Index error: {exc}", file=sys.stderr)
        return 1
    return 1 if failed else 0


def _run_collector(
    name: str,
    collector: Collector,
    registry: Registry,
    rejected_registry: RejectedRegistry,
    *,
    limit: int | None,
) -> CollectorSummary:
    summary = CollectorSummary(source=name)
    try:
        for job in collector.fetch():
            if limit is not None and summary.fetched >= limit:
                summary.limit_reached = True
                break
            summary.fetched += 1
            try:
                rejection = prefilter_job(job)
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
    except Exception as exc:
        summary.errors += 1
        print(f"{name}: collection failed: {exc}", file=sys.stderr)
    collector_errors = getattr(collector, "errors", 0)
    if isinstance(collector_errors, int) and collector_errors > 0:
        summary.errors += collector_errors
    requests = getattr(collector, "api_requests", 0)
    if isinstance(requests, int) and requests > 0:
        summary.api_requests = requests
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
        return 5
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


def _run_analysis(
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
        _, model_label = _selected_workflow(args.workflow, project_root, {"analyze"})
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
    return [
        (registry_dir / "candidate" / "linkedin-profile.md").resolve(),
        (registry_dir / "candidate" / "backend-engineer-cv.md").resolve(),
    ]


def _run_preparation(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    if len(args.arguments) != 1:
        print(
            "Usage: python run.py prepare <job-directory|vacancy-id> --input <draft-directory> "
            "--workflow <prepare|prepare-priority> [--force]",
            file=sys.stderr,
        )
        return 2
    if not args.input or not args.workflow:
        print("prepare requires --input and --workflow", file=sys.stderr)
        return 2

    try:
        policy, model_label = _selected_workflow(
            args.workflow, project_root, {"prepare", "prepare_priority"}
        )
        Registry(registry_dir).migrate_metadata()
        profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
        directories = resolve_job_directories(registry_dir, args.arguments[0])
        if len(directories) != 1:
            raise ValueError("prepare publishes exactly one Codex draft at a time")
        if not _analysis_is_current(directories[0], registry_dir, profile_paths, policy, project_root):
            raise ValueError("match analysis is missing or stale; run workflow analyze first")
        score = _match_score(directories[0])
        if not policy.prepare_score_is_eligible(args.workflow, score):
            raise ValueError(_ineligible_score_message(policy, args.workflow, score))
    except Exception as exc:
        print(f"Preparation configuration error: {exc}", file=sys.stderr)
        return 2

    summary = PreparationSummary(selected=len(directories))
    for directory in directories:
        try:
            generator = ApplicationGenerator(
                registry_dir,
                profile_paths,
                project_root / "prompts" / "vacancy-application.md",
                CodexApplicationDraftClient(args.input, model=model_label),
                HostMarkdownDocxConverter(project_root),
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


def _run_pending(
    args: argparse.Namespace,
    config: dict[str, str],
    project_root: Path,
    registry_dir: Path,
) -> int:
    if len(args.arguments) not in (1, 2) or args.arguments[0] not in {"analyze", "prepare"}:
        print(
            "Usage: python run.py pending <analyze|prepare> [all|job-directory|vacancy-id] "
            "--workflow <analyze|prepare|prepare-priority>",
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
    selector = args.arguments[1] if len(args.arguments) == 2 else "all"
    try:
        allowed = {"analyze"} if stage == "analyze" else {"prepare", "prepare_priority"}
        policy, model_label = _selected_workflow(args.workflow, project_root, allowed)
        Registry(registry_dir).migrate_metadata()
        profile_paths = _profile_paths(args.profile, config, project_root, registry_dir)
        directories = resolve_job_directories(registry_dir, selector)
        for directory in directories:
            if stage == "analyze":
                checker = MatchAnalyzer(
                    registry_dir,
                    profile_paths,
                    CodexMatchDraftClient(
                        project_root / ".codex-work" / "unused-match.yaml",
                        model=model_label,
                    ),
                )
            else:
                if not _analysis_is_current(
                    directory, registry_dir, profile_paths, policy, project_root
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
                    ),
                    HostMarkdownDocxConverter(project_root),
                )
            if not checker.is_current(directory):
                print(directory)
    except Exception as exc:
        print(f"Pending check failed: {exc}", file=sys.stderr)
        return 1
    return 0


def _selected_workflow(
    requested: str, project_root: Path, allowed: set[str]
) -> tuple[WorkflowPolicy, str]:
    policy = load_workflow_policy(project_root / "config" / "codex-workflows.yaml")
    workflow = policy.workflow(requested)
    if workflow.name not in allowed:
        choices = ", ".join(sorted(name.replace("_", "-") for name in allowed))
        raise ValueError(f"workflow {requested!r} is invalid here; expected: {choices}")
    return policy, workflow.model_label


def _optional_match_score(directory: Path) -> int | None:
    path = directory / "match.yaml"
    if not path.is_file():
        return None
    return _match_score(directory)


def _analysis_is_current(
    directory: Path,
    registry_dir: Path,
    profile_paths: list[Path],
    policy: WorkflowPolicy,
    project_root: Path,
) -> bool:
    checker = MatchAnalyzer(
        registry_dir,
        profile_paths,
        CodexMatchDraftClient(
            project_root / ".codex-work" / "unused-match.yaml",
            model=policy.workflow("analyze").model_label,
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


def _ineligible_score_message(policy: WorkflowPolicy, workflow: str, score: int) -> str:
    canonical = workflow.replace("-", "_")
    if score < policy.prepare_min_score:
        return (
            f"vacancy score {score} is below prepare_min_score {policy.prepare_min_score}; "
            "no application package should be prepared"
        )
    if canonical == "prepare":
        return f"vacancy score {score} belongs to prepare-priority (minimum {policy.priority_score})"
    return (
        f"vacancy score {score} belongs to prepare "
        f"({policy.prepare_min_score}-{policy.priority_score - 1})"
    )


def _run_doctor(
    args: argparse.Namespace,
    project_root: Path,
    sources_dir: Path,
    registry_dir: Path,
    env_path: Path,
) -> int:
    if args.arguments or args.force or args.profile or args.input or args.workflow:
        print("Usage: python run.py doctor", file=sys.stderr)
        return 2

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
