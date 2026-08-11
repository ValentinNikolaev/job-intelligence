from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence

import yaml

from .normalization import slug


class WorktreeError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class GitWorkflowPolicy:
    remote: str
    main_branch: str
    main_writer: str
    branch_prefix: str
    worktree_root: Path
    short_path_length: int


@dataclass(frozen=True, slots=True)
class WorktreeResult:
    branch: str
    path: Path
    base: str


Runner = Callable[..., subprocess.CompletedProcess[str]]


def load_git_workflow_policy(path: Path) -> GitWorkflowPolicy:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise WorktreeError(f"cannot read Git workflow policy {path}: {exc}") from exc
    if not isinstance(loaded, Mapping) or loaded.get("schema_version") != 1:
        raise WorktreeError(f"unsupported Git workflow policy: {path}")
    codex = loaded.get("codex")
    if not isinstance(codex, Mapping):
        raise WorktreeError("Git workflow policy is missing codex settings")
    remote = _required_text(loaded, "remote")
    main_branch = _required_text(loaded, "main_branch")
    main_writer = _required_text(loaded, "main_writer")
    branch_prefix = _required_text(codex, "branch_prefix")
    worktree_root = Path(_required_text(codex, "worktree_root"))
    short_path_length = codex.get("short_path_length")
    if isinstance(short_path_length, bool) or not isinstance(short_path_length, int):
        raise WorktreeError("codex.short_path_length must be an integer")
    if not 6 <= short_path_length <= 20:
        raise WorktreeError("codex.short_path_length must be between 6 and 20")
    if worktree_root.is_absolute() or ".." in worktree_root.parts:
        raise WorktreeError("codex.worktree_root must be a repository-relative path")
    if main_writer != "github-actions":
        raise WorktreeError("main_writer must remain github-actions")
    if not branch_prefix.startswith("codex/"):
        raise WorktreeError("codex.branch_prefix must start with codex/")
    return GitWorkflowPolicy(
        remote=remote,
        main_branch=main_branch,
        main_writer=main_writer,
        branch_prefix=branch_prefix,
        worktree_root=worktree_root,
        short_path_length=short_path_length,
    )


def create_codex_worktree(
    project_root: Path,
    task_name: str,
    *,
    now: datetime | None = None,
    runner: Runner = subprocess.run,
) -> WorktreeResult:
    repository_root = _repository_root(project_root, runner)
    policy = load_git_workflow_policy(project_root.resolve() / "config" / "git-workflow.yaml")
    timestamp = (now or datetime.now(timezone.utc)).astimezone(timezone.utc).strftime("%Y%m%d-%H%M%S")
    task = slug(task_name, fallback="task", max_length=24)
    identity = hashlib.sha256(f"{task}|{timestamp}".encode("utf-8")).hexdigest()
    branch = f"{policy.branch_prefix}{task}-{timestamp}"
    short_name = identity[: policy.short_path_length]
    worktree_path = (repository_root / policy.worktree_root / short_name).resolve()
    base = f"{policy.remote}/{policy.main_branch}"
    if worktree_path.exists():
        raise WorktreeError(f"worktree path already exists: {worktree_path}")
    worktree_path.parent.mkdir(parents=True, exist_ok=True)

    _run_git(runner, repository_root, "config", "core.longpaths", "true")
    _run_git(runner, repository_root, "fetch", policy.remote, policy.main_branch)
    _run_git(runner, repository_root, "rev-parse", "--verify", base)
    _run_git(
        runner,
        repository_root,
        "worktree",
        "add",
        "-b",
        branch,
        str(worktree_path),
        base,
    )
    return WorktreeResult(branch=branch, path=worktree_path, base=base)


def _repository_root(project_root: Path, runner: Runner) -> Path:
    completed = _run_git(runner, project_root.resolve(), "rev-parse", "--git-common-dir")
    raw = completed.stdout.strip()
    if not raw:
        raise WorktreeError("git rev-parse returned an empty common directory")
    common_dir = Path(raw)
    if not common_dir.is_absolute():
        common_dir = project_root.resolve() / common_dir
    common_dir = common_dir.resolve()
    if common_dir.name != ".git":
        raise WorktreeError(f"unexpected Git common directory: {common_dir}")
    return common_dir.parent


def _run_git(runner: Runner, cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    command: Sequence[str] = ("git", "-C", str(cwd), *arguments)
    try:
        return runner(
            command,
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as exc:
        detail = (exc.stderr or exc.stdout or str(exc)).strip()
        raise WorktreeError(f"Git command failed ({' '.join(arguments)}): {detail}") from exc


def _required_text(payload: Mapping[str, Any], key: str) -> str:
    value = payload.get(key)
    if not isinstance(value, str) or not value.strip():
        raise WorktreeError(f"Git workflow policy is missing {key}")
    return value.strip()
