from __future__ import annotations

import json
import os
import shutil
import time
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator


LOCK_ENV_TOKEN = "JOBINTEL_WORKFLOW_LOCK_TOKEN"
LOCK_DIR = Path(".codex-work") / "workflow.lock"
METADATA_FILE = "owner.json"
DEFAULT_STALE_SECONDS = 6 * 60 * 60
STALE_CLAIM_FILE = ".stale-claim"
STALE_CLAIM_SECONDS = 30


class WorkflowLockError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class WorkflowLockLease:
    path: Path
    owner: str
    token: str
    acquired: bool = True

    def release(self) -> None:
        if not self.acquired:
            return
        release_workflow_lock(self.path.parent.parent, self.token)


@contextmanager
def workflow_lock(
    project_root: Path,
    owner: str,
    *,
    timeout_seconds: float = 0,
    stale_seconds: float = DEFAULT_STALE_SECONDS,
) -> Iterator[WorkflowLockLease]:
    lease = acquire_workflow_lock(
        project_root,
        owner,
        timeout_seconds=timeout_seconds,
        stale_seconds=stale_seconds,
    )
    try:
        yield lease
    finally:
        lease.release()


def acquire_workflow_lock(
    project_root: Path,
    owner: str,
    *,
    timeout_seconds: float = 0,
    stale_seconds: float = DEFAULT_STALE_SECONDS,
) -> WorkflowLockLease:
    root = project_root.resolve()
    lock_dir = _lock_dir(root)
    existing_token = os.environ.get(LOCK_ENV_TOKEN, "").strip()
    if existing_token and _token_matches(lock_dir, existing_token):
        return WorkflowLockLease(lock_dir, owner, existing_token, acquired=False)

    token = uuid.uuid4().hex
    deadline = time.monotonic() + max(0, timeout_seconds)
    while True:
        try:
            lock_dir.parent.mkdir(parents=True, exist_ok=True)
            lock_dir.mkdir()
            metadata = {
                "owner": owner,
                "token": token,
                "pid": os.getpid(),
                "created_at": _utc_iso(),
            }
            (lock_dir / METADATA_FILE).write_text(
                json.dumps(metadata, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            return WorkflowLockLease(lock_dir, owner, token)
        except FileExistsError:
            if _is_stale(lock_dir, stale_seconds) and _claim_stale_lock(lock_dir, stale_seconds):
                _remove_lock_dir(lock_dir)
                continue
            if time.monotonic() >= deadline:
                raise WorkflowLockError(_locked_message(lock_dir))
            time.sleep(min(1.0, max(0.05, deadline - time.monotonic())))


def release_workflow_lock(project_root: Path, token: str) -> None:
    lock_dir = _lock_dir(project_root.resolve())
    if not lock_dir.exists():
        return
    if not _token_matches(lock_dir, token):
        raise WorkflowLockError("workflow lock is held by another process")
    _remove_lock_dir(lock_dir)


def workflow_lock_status(project_root: Path) -> dict[str, object]:
    lock_dir = _lock_dir(project_root.resolve())
    metadata = _read_metadata(lock_dir)
    return {
        "locked": lock_dir.exists(),
        "path": str(lock_dir),
        "owner": metadata.get("owner"),
        "pid": metadata.get("pid"),
        "created_at": metadata.get("created_at"),
    }


def _lock_dir(project_root: Path) -> Path:
    return project_root / LOCK_DIR


def _token_matches(lock_dir: Path, token: str) -> bool:
    return str(_read_metadata(lock_dir).get("token") or "") == token


def _read_metadata(lock_dir: Path) -> dict[str, object]:
    try:
        loaded = json.loads((lock_dir / METADATA_FILE).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return loaded if isinstance(loaded, dict) else {}


def _is_stale(lock_dir: Path, stale_seconds: float) -> bool:
    try:
        metadata_path = lock_dir / METADATA_FILE
        age = time.time() - (metadata_path if metadata_path.exists() else lock_dir).stat().st_mtime
    except OSError:
        return False
    return age > stale_seconds


def _claim_stale_lock(lock_dir: Path, stale_seconds: float) -> bool:
    """Claim stale-lock recovery so only one contender may remove the directory."""
    claim_path = lock_dir / STALE_CLAIM_FILE
    try:
        with claim_path.open("x", encoding="utf-8") as handle:
            handle.write(f"{os.getpid()}:{uuid.uuid4().hex}\n")
    except FileExistsError:
        try:
            claim_age = time.time() - claim_path.stat().st_mtime
        except OSError:
            return False
        if claim_age > STALE_CLAIM_SECONDS:
            try:
                claim_path.unlink()
            except OSError:
                pass
        return False
    except OSError:
        return False

    # A contender may have observed the old directory and then created its claim
    # in a newly acquired lock. Revalidate after the exclusive claim is created.
    if _is_stale(lock_dir, stale_seconds):
        return True
    try:
        claim_path.unlink()
    except OSError:
        pass
    return False


def _remove_lock_dir(lock_dir: Path) -> None:
    try:
        shutil.rmtree(lock_dir)
    except FileNotFoundError:
        return


def _locked_message(lock_dir: Path) -> str:
    metadata = _read_metadata(lock_dir)
    owner = metadata.get("owner") or "unknown"
    created_at = metadata.get("created_at") or "unknown time"
    return f"workflow lock is already held by {owner} since {created_at}: {lock_dir}"


def _utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
