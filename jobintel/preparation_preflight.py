"""Fail-closed preparation gates that run before an agent drafts a CV."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Sequence

from .applications import HostMarkdownDocxConverter, resolve_job_directories
from .config import load_env
from .document_quality import DocumentQualityError, preview_capabilities
from .matching import CodexMatchDraftClient, MatchAnalyzer
from .storage_cli import configured_store
from .workflows import load_workflow_policy


class PreparationPreflightError(ValueError):
    pass


def selected_preparation_directories(
    registry_root: Path, selectors: Sequence[str], *, limit: int
) -> list[Path]:
    if not selectors:
        raise PreparationPreflightError("preparation preflight requires at least one explicit vacancy selector")
    if len(selectors) > limit:
        raise PreparationPreflightError(f"preparation accepts at most {limit} vacancies; received {len(selectors)}")
    result: list[Path] = []
    seen: set[Path] = set()
    for selector in selectors:
        if not selector.strip() or selector.casefold() == "all":
            raise PreparationPreflightError("preparation selection must name explicit vacancies; all is not allowed")
        paths = resolve_job_directories(registry_root, selector)
        if len(paths) != 1:
            raise PreparationPreflightError(f"preparation selector must resolve to one vacancy: {selector}")
        path = paths[0].resolve()
        if path in seen:
            raise PreparationPreflightError(f"duplicate vacancy selection: {selector}")
        seen.add(path)
        result.append(path)
    return result


def run_preflight(
    project_root: Path,
    selectors: Sequence[str],
    *,
    workflow: str,
    model_profile: str | None = None,
    profile_paths: Sequence[Path] | None = None,
    worktree_check: Callable[[Path], dict[str, str]] | None = None,
    doctor: Callable[[Path], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return a JSON-safe receipt or raise before any model work can start."""
    root = project_root.resolve()
    policy = load_workflow_policy(root / "config" / "codex-workflows.yaml")
    if workflow != "prepare":
        raise PreparationPreflightError("preparation preflight requires --workflow prepare")
    profile = policy.resolve_model_profile("prepare", model_profile)
    directories = selected_preparation_directories(
        root / "registry", selectors, limit=policy.prepare_batch_size
    )
    # Do not accept the historical YAML backend here.  The direct store setup also
    # deliberately avoids printing the URI when a worktree has no usable secret.
    environment = load_env(root / "sources" / ".env")
    if not environment.get("MONGODB_URI", "").strip():
        raise PreparationPreflightError("MongoDB configuration is unavailable to this worktree")
    if doctor is None:
        store = configured_store(root)
        try:
            hello = store.client.admin.command("hello")
            schema = store.get("storage_schema", "operational")
            doctor_result = {
                "backend": "mongodb",
                "replica_set": bool(hello.get("setName")),
                "schema_version": schema.get("schema_version") if isinstance(schema, dict) else None,
            }
        finally:
            store.close()
    else:
        doctor_result = doctor(root)
    if doctor_result.get("backend") != "mongodb" or not doctor_result.get("replica_set") or doctor_result.get("schema_version") != 1:
        raise PreparationPreflightError("storage doctor did not confirm the required MongoDB replica-set schema")

    candidates = list(profile_paths or [])
    if not candidates:
        candidate_root = root / "registry" / "candidate"
        compact = candidate_root / "match-profile.md"
        candidates = [compact] if compact.is_file() else [
            candidate_root / "linkedin-profile.md", candidate_root / "backend-engineer-cv.md"]
        candidates.extend(sorted(candidate_root.glob("user-confirmed-*.md")))
    checker = MatchAnalyzer(
        root / "registry", candidates,
        CodexMatchDraftClient(root / ".codex-work" / "unused-match.yaml", model=profile.model_label),
    )
    stale = [directory.name for directory in directories if not checker.is_current(directory)]
    if stale:
        raise PreparationPreflightError("fresh match for the selected model profile is required: " + ", ".join(stale))

    converter = HostMarkdownDocxConverter(root)
    try:
        capabilities = preview_capabilities(
            converter.script_path, converter.options_path, converter.powershell
        )
    except DocumentQualityError as exc:
        raise PreparationPreflightError(f"CV preview is unavailable: {exc}") from exc
    if capabilities["status"] != "available":
        raise PreparationPreflightError("CV preview renderer is unavailable")
    if worktree_check is None:
        from scripts.finalize_repository import preflight as finalizer_preflight
        worktree = finalizer_preflight(root)
    else:
        worktree = worktree_check(root)
    return {
        "ok": True,
        "workflow": "prepare",
        "model_profile": profile.name,
        "model_label": profile.model_label,
        "selected": [{"selector": selector, "directory": directory.name}
                     for selector, directory in zip(selectors, directories)],
        "storage": doctor_result,
        "preview": capabilities,
        "worktree": worktree,
    }


def write_receipt(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
