from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .applications import ApplicationGenerator, CodexApplicationDraftClient, HostMarkdownDocxConverter
from .catalog_data import CatalogVacancy, load_catalog_vacancies
from .matching import CodexMatchDraftClient, MatchAnalyzer
from .triage import should_skip_model
from .workflows import WorkflowPolicy, load_workflow_policy


DEFAULT_ANALYZE_MAX_ESTIMATED_INPUT_TOKENS = 9000
DEFAULT_PREPARE_MAX_ESTIMATED_INPUT_TOKENS = 18000
DEFAULT_PREPARE_PRIORITY_MAX_ESTIMATED_INPUT_TOKENS = 22000


class WorkflowApiError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class QueueItem:
    vacancy: CatalogVacancy
    workflow: str
    estimated_input_tokens: int
    budget_status: str
    reasons: tuple[str, ...]

    def to_api_dict(self, *, base: Path | None = None) -> dict[str, Any]:
        return {
            "vacancy_id": self.vacancy.vacancy_id,
            "directory": self.vacancy.directory.name if base is None else self.vacancy.to_api_dict(base=base)["directory"],
            "company": self.vacancy.company,
            "title": self.vacancy.title,
            "status": self.vacancy.status,
            "analysis_priority": self.vacancy.analysis_priority,
            "score": self.vacancy.score,
            "workflow": self.workflow,
            "estimated_input_tokens": self.estimated_input_tokens,
            "budget_status": self.budget_status,
            "reasons": list(self.reasons),
        }


def _queue_priority(item: QueueItem) -> tuple[int, str, str]:
    return (
        item.vacancy.analysis_priority,
        item.vacancy.discovered_at,
        item.vacancy.directory.name,
    )


def workflow_summary(
    project_root: Path,
    registry_root: Path,
    config: dict[str, str],
    profile_paths: list[Path],
) -> dict[str, Any]:
    del config
    policy = _policy(project_root)
    vacancies = load_catalog_vacancies(registry_root)
    inactive = {"rejected", "withdrawn", "closed"}
    active = [vacancy for vacancy in vacancies if vacancy.status not in inactive]
    prepared = [vacancy for vacancy in vacancies if vacancy.artifacts.cv_md and vacancy.artifacts.cover_letter_md]
    return {
        "vacancies_total": len(vacancies),
        "vacancies_active": len(active),
        "rejected_total": _rejected_count(registry_root),
        "analyzed_total": sum(1 for vacancy in vacancies if vacancy.score is not None),
        "pending_analyze": len(queue_items("analyze", project_root, registry_root, profile_paths, policy)),
        "pending_prepare": len(queue_items("prepare", project_root, registry_root, profile_paths, policy)),
        "pending_prepare_priority": len(
            queue_items("prepare_priority", project_root, registry_root, profile_paths, policy)
        ),
        "prepared_total": len(prepared),
    }


def workflow_limits(project_root: Path, collection_limit: int | None) -> dict[str, Any]:
    policy = _policy(project_root)
    return {
        "collection_limit_per_source": collection_limit,
        "analyze_batch_size": 10,
        "analyze_max_estimated_input_tokens": DEFAULT_ANALYZE_MAX_ESTIMATED_INPUT_TOKENS,
        "prepare_max_estimated_input_tokens": DEFAULT_PREPARE_MAX_ESTIMATED_INPUT_TOKENS,
        "prepare_priority_max_estimated_input_tokens": DEFAULT_PREPARE_PRIORITY_MAX_ESTIMATED_INPUT_TOKENS,
        "prepare_min_score": policy.prepare_min_score,
        "priority_score": policy.priority_score,
    }


def source_usage(registry_root: Path) -> dict[str, Any]:
    path = registry_root / "source-api-usage.yaml"
    if not path.is_file():
        return {"sources": []}
    loaded = _read_yaml_mapping(path, "source API usage")
    rows = []
    for source, data in sorted((loaded.get("sources") or {}).items()):
        if not isinstance(data, dict):
            continue
        runs = data.get("runs") if isinstance(data.get("runs"), list) else []
        last = runs[-1] if runs else {}
        rows.append(
            {
                "source": str(source),
                "total_requests": _int(data.get("total_requests")),
                "last_run_at": data.get("last_run_at"),
                "last_status": data.get("last_status"),
                "last_requests": _int(last.get("requests")),
                "last_fetched": _int(last.get("fetched")),
                "last_created": _int(last.get("created")),
                "last_updated": _int(last.get("updated")),
                "last_rejected": _int(last.get("rejected")),
                "last_errors": _int(last.get("errors")),
                "limit_reached": bool(last.get("limit_reached")),
                "runs": len(runs),
            }
        )
    return {"sources": rows}


def codex_usage(registry_root: Path) -> dict[str, Any]:
    path = registry_root / "codex-usage.yaml"
    if not path.is_file():
        return {"runs": []}
    loaded = _read_yaml_mapping(path, "Codex usage")
    runs = loaded.get("runs")
    return {"runs": runs if isinstance(runs, list) else []}


def catalog_vacancies(registry_root: Path) -> dict[str, Any]:
    base = registry_root.parent
    rows = [vacancy.to_api_dict(base=base) for vacancy in load_catalog_vacancies(registry_root)]
    return {"vacancies": rows}


def queue_items(
    workflow: str,
    project_root: Path,
    registry_root: Path,
    profile_paths: list[Path],
    policy: WorkflowPolicy | None = None,
    *,
    limit: int | None = None,
) -> list[QueueItem]:
    policy = policy or _policy(project_root)
    workflow = workflow.replace("-", "_")
    if workflow not in {"analyze", "prepare", "prepare_priority"}:
        raise WorkflowApiError(f"unsupported workflow queue: {workflow}")
    vacancies = load_catalog_vacancies(registry_root)
    rows = []
    for vacancy in vacancies:
        directory = vacancy.directory
        if workflow == "analyze":
            if should_skip_model(directory):
                continue
            checker = MatchAnalyzer(
                registry_root,
                profile_paths,
                CodexMatchDraftClient(project_root / ".codex-work" / "unused-match.yaml", model=policy.workflow("analyze").model_label),
            )
            if checker.is_current(directory):
                continue
        else:
            if vacancy.score is None:
                continue
            if not _analysis_is_current(directory, registry_root, profile_paths, policy, project_root):
                continue
            if not policy.prepare_score_is_eligible(workflow, vacancy.score):
                continue
            generator = ApplicationGenerator(
                registry_root,
                profile_paths,
                project_root / "prompts" / "vacancy-application.md",
                CodexApplicationDraftClient(
                    project_root / ".codex-work" / "unused-application",
                    model=policy.workflow(workflow).model_label,
                ),
                HostMarkdownDocxConverter(project_root),
            )
            if generator.is_current(directory):
                continue
        estimate = estimate_input_tokens(workflow, project_root, directory, profile_paths)
        budget = _budget_for(workflow)
        rows.append(
            QueueItem(
                vacancy=vacancy,
                workflow=workflow,
                estimated_input_tokens=estimate,
                budget_status=_budget_status(estimate, budget),
                reasons=_queue_reasons(workflow, vacancy),
            )
        )
    rows.sort(key=_queue_priority, reverse=True)
    return rows[:limit] if limit is not None else rows


def queue_response(
    workflow: str,
    project_root: Path,
    registry_root: Path,
    profile_paths: list[Path],
    *,
    limit: int | None = None,
) -> dict[str, Any]:
    policy = _policy(project_root)
    items = queue_items(workflow, project_root, registry_root, profile_paths, policy, limit=limit)
    return {
        "workflow": workflow.replace("-", "_"),
        "limit": limit,
        "items": [item.to_api_dict() for item in items],
    }


def estimate_input_tokens(
    workflow: str,
    project_root: Path,
    directory: Path,
    profile_paths: list[Path],
) -> int:
    workflow = workflow.replace("-", "_")
    paths = list(profile_paths)
    paths.extend([directory / "meta.yaml", directory / "job.md"])
    if (directory / "company.md").is_file():
        paths.append(directory / "company.md")
    if workflow == "analyze":
        paths.append(project_root / "prompts" / "vacancy-match.md")
    else:
        paths.append(project_root / "prompts" / "vacancy-application.md")
    return max(1, sum(_file_bytes(path) for path in paths) // 4)


def _queue_reasons(workflow: str, vacancy: CatalogVacancy) -> tuple[str, ...]:
    if workflow == "analyze":
        return ("analysis_missing_or_stale",)
    if vacancy.score is None:
        return ("score_missing",)
    return (f"score_{vacancy.score}",)


def _budget_for(workflow: str) -> int:
    if workflow == "analyze":
        return DEFAULT_ANALYZE_MAX_ESTIMATED_INPUT_TOKENS
    if workflow == "prepare":
        return DEFAULT_PREPARE_MAX_ESTIMATED_INPUT_TOKENS
    return DEFAULT_PREPARE_PRIORITY_MAX_ESTIMATED_INPUT_TOKENS


def _budget_status(estimate: int, budget: int) -> str:
    if estimate > budget:
        return "over"
    if estimate > int(budget * 0.8):
        return "warning"
    return "ok"


def _policy(project_root: Path) -> WorkflowPolicy:
    return load_workflow_policy(project_root / "config" / "codex-workflows.yaml")


def _analysis_is_current(
    directory: Path,
    registry_root: Path,
    profile_paths: list[Path],
    policy: WorkflowPolicy,
    project_root: Path,
) -> bool:
    checker = MatchAnalyzer(
        registry_root,
        profile_paths,
        CodexMatchDraftClient(
            project_root / ".codex-work" / "unused-match.yaml",
            model=policy.workflow("analyze").model_label,
        ),
    )
    return checker.is_current(directory)


def _rejected_count(registry_root: Path) -> int:
    rejected = registry_root / "rejected"
    if not rejected.is_dir():
        return 0
    return sum(1 for path in rejected.glob("*/meta.yaml") if path.is_file())


def _file_bytes(path: Path) -> int:
    try:
        return path.stat().st_size if path.is_file() else 0
    except OSError:
        return 0


def _read_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorkflowApiError(f"cannot read {label} {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise WorkflowApiError(f"{label} must be a YAML mapping: {path}")
    return loaded


def _int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) else 0
