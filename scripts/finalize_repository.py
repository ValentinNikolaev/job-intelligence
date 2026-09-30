"""Review and publish one isolated worktree change without touching a shared checkout."""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import subprocess
import sys
from pathlib import Path


EXCLUDED_PARTS = {".codex-work", ".venv", "venv", "__pycache__", ".idea", ".pytest_cache"}
TELEGRAM_OUTBOX_PREFIX = "notifications/telegram/outbox/"


def is_intended_telegram_outbox(path: str) -> bool:
    return (path.startswith(TELEGRAM_OUTBOX_PREFIX) and
            path.endswith(".json") and
            "/" not in path[len(TELEGRAM_OUTBOX_PREFIX):])


class FinalizationError(RuntimeError):
    pass


def command(*args: str, cwd: Path, check: bool = True) -> bytes:
    result = subprocess.run(args, cwd=cwd, capture_output=True, check=False)
    if check and result.returncode:
        detail = (result.stderr or result.stdout).decode("utf-8", "replace").strip()
        raise FinalizationError(f"{' '.join(args[:3])} failed: {detail[:1000]}")
    return result.stdout if result.returncode == 0 else b""


def git(root: Path, *args: str) -> bytes:
    return command("git", "-c", "core.longpaths=true", *args, cwd=root)


def gh(root: Path, *args: str) -> bytes:
    return command("gh", *args, cwd=root)


def gh_api(root: Path, method: str, endpoint: str, payload: dict | None = None) -> dict:
    args = ["gh", "api", "-X", method, endpoint]
    encoded = None
    if payload is not None:
        args.extend(["--input", "-"])
        encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    result = subprocess.run(args, cwd=root, input=encoded, capture_output=True)
    if result.returncode:
        raise FinalizationError(f"GitHub API {method} {endpoint} failed: {result.stderr.decode('utf-8', 'replace')[:1000]}")
    return json.loads(result.stdout)


def remote_info(root: Path) -> tuple[str, str, str]:
    info = json.loads(gh(root, "repo", "view", "--json", "nameWithOwner,defaultBranchRef"))
    repo = info["nameWithOwner"]
    branch = info["defaultBranchRef"]["name"]
    sha = gh(root, "api", f"repos/{repo}/git/ref/heads/{branch}", "--jq", ".object.sha").decode().strip()
    if len(sha) != 40 or any(c not in "0123456789abcdef" for c in sha):
        raise FinalizationError("remote branch did not return a commit SHA")
    return repo, branch, sha


def ensure_worktree(root: Path) -> None:
    actual = Path(git(root, "rev-parse", "--show-toplevel").decode().strip()).resolve()
    if not (root / ".git").is_file() or actual != root.resolve():
        raise FinalizationError("use an isolated managed Git worktree, not the shared checkout")
    rebase_merge = Path(git(root, "rev-parse", "--git-path", "rebase-merge").decode().strip())
    rebase_apply = Path(git(root, "rev-parse", "--git-path", "rebase-apply").decode().strip())
    if rebase_merge.exists() or rebase_apply.exists():
        raise FinalizationError("resolve the interrupted rebase before finalization")


def status(root: Path) -> bytes:
    return git(root, "status", "--porcelain=v1", "-z", "--untracked-files=all")


def head(root: Path) -> str:
    return git(root, "rev-parse", "HEAD").decode().strip()


def ancestor(root: Path, older: str, newer: str) -> bool:
    result = subprocess.run(["git", "-c", "core.longpaths=true", "merge-base", "--is-ancestor", older, newer], cwd=root, capture_output=True)
    if result.returncode not in {0, 1}:
        raise FinalizationError(result.stderr.decode("utf-8", "replace"))
    return result.returncode == 0


def fetch(root: Path, branch: str, expected: str) -> None:
    git(root, "fetch", "--no-tags", "origin", branch)
    git(root, "cat-file", "-e", f"{expected}^{{commit}}")


def preflight(root: Path) -> dict[str, str]:
    ensure_worktree(root)
    if status(root):
        raise FinalizationError("isolated checkout has local changes; preserve and account for them before preflight")
    repo, branch, remote = remote_info(root)
    fetch(root, branch, remote)
    local = head(root)
    if local != remote:
        if not ancestor(root, local, remote):
            raise FinalizationError("local and remote history diverged; inspect both histories before proceeding")
        git(root, "merge", "--ff-only", remote)
    return {"repo": repo, "branch": branch, "base": head(root)}


def changed_paths(root: Path, *diff_args: str) -> list[str]:
    raw = git(root, "diff", *diff_args, "--name-only", "--no-renames", "-z")
    return sorted(part.decode("utf-8", "surrogateescape") for part in raw.split(b"\0") if part)


def index_entries(root: Path, paths: list[str]) -> dict[str, str | None]:
    entries: dict[str, str] = {}
    for row in git(root, "ls-files", "--stage", "-z").split(b"\0"):
        if row:
            meta, name = row.split(b"\t", 1)
            mode, blob, stage = meta.decode().split()
            if stage == "0":
                entries[name.decode("utf-8", "surrogateescape")] = f"{mode}:{blob}"
    return {path: entries.get(path) for path in paths}


def tree_entries(root: Path, revision: str, paths: list[str]) -> dict[str, str | None]:
    entries = {}
    for row in git(root, "ls-tree", "-r", "-z", revision).split(b"\0"):
        if row:
            meta, name = row.split(b"\t", 1)
            mode, kind, blob = meta.decode().split()
            if kind == "blob":
                entries[name.decode("utf-8", "surrogateescape")] = f"{mode}:{blob}"
    return {path: entries.get(path) for path in paths}


def api_tree(root: Path, repo: str, tree_sha: str) -> dict[str, str]:
    result = gh_api(root, "GET", f"repos/{repo}/git/trees/{tree_sha}?recursive=1")
    if result.get("truncated"):
        raise FinalizationError("GitHub truncated the remote tree; cannot verify exact changes")
    return {item["path"]: f"{item['mode']}:{item['sha']}" for item in result["tree"]
            if item["type"] == "blob"}


def review_committed(root: Path) -> dict:
    """Review a clean unpublished commit for the API fallback after a push refusal."""
    ensure_worktree(root)
    if status(root):
        raise FinalizationError("committed API fallback requires a clean isolated checkout")
    paths = changed_paths(root, "HEAD^", "HEAD")
    if not paths or any(EXCLUDED_PARTS.intersection(Path(path).parts) for path in paths):
        raise FinalizationError("commit has no reviewable project changes or includes local work")
    patch = git(root, "diff", "HEAD^", "HEAD", "--binary", "--full-index", "--no-ext-diff")
    work = root / ".codex-work" / "finalization"
    work.mkdir(parents=True, exist_ok=True)
    (work / "api-review.patch").write_bytes(patch)
    record = {"commit": head(root), "parent": git(root, "rev-parse", "HEAD^").decode().strip(),
              "entries": index_entries(root, paths), "patch_sha256": hashlib.sha256(patch).hexdigest()}
    (work / "api-review.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"commit": record["commit"], "files": paths, "patch": str(work / "api-review.patch")}


def verify_committed_review(root: Path) -> dict:
    path = root / ".codex-work" / "finalization" / "api-review.json"
    if not path.is_file():
        raise FinalizationError("run review-commit and inspect its complete patch first")
    record = json.loads(path.read_text(encoding="utf-8"))
    if status(root) or head(root) != record["commit"]:
        raise FinalizationError("unpublished commit or checkout changed after API review")
    paths = changed_paths(root, "HEAD^", "HEAD")
    patch_path = root / ".codex-work" / "finalization" / "api-review.patch"
    if (index_entries(root, paths) != record["entries"] or not patch_path.is_file() or
            hashlib.sha256(patch_path.read_bytes()).hexdigest() != record["patch_sha256"]):
        raise FinalizationError("committed project changes differ from the API review")
    return record


def api_commit_is_published(root: Path, repo: str, commit: str, remote: str) -> bool:
    if commit == remote:
        return True
    comparison = gh_api(root, "GET", f"repos/{repo}/compare/{commit}...{remote}")
    return comparison.get("status") == "ahead"


def publish_api(root: Path) -> dict[str, str]:
    """Publish a reviewed local commit with gh when this host cannot push via Git."""
    ensure_worktree(root)
    record = verify_committed_review(root)
    repo, branch, _ = remote_info(root)
    attempt_path = root / ".codex-work" / "finalization" / "api-attempt.json"
    if attempt_path.is_file():
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
        if attempt.get("reviewed_commit") == record["commit"]:
            latest = remote_info(root)[2]
            if api_commit_is_published(root, repo, attempt["created_commit"], latest):
                return {"repo": repo, "branch": branch, "commit": attempt["created_commit"],
                        "remote_head": latest, "result": "published and verified by GitHub API"}
    paths = sorted(record["entries"])
    base_entries = tree_entries(root, record["parent"], paths)
    message = git(root, "log", "-1", "--format=%B").decode("utf-8").strip()
    blob_shas: dict[str, str] = {}
    for path, value in record["entries"].items():
        if value is not None:
            mode, local_sha = value.split(":", 1)
            content = git(root, "cat-file", "blob", local_sha)
            result = gh_api(root, "POST", f"repos/{repo}/git/blobs", {
                "content": base64.b64encode(content).decode("ascii"), "encoding": "base64"})
            if result["sha"] != local_sha:
                raise FinalizationError(f"uploaded blob hash differs for {path}")
            blob_shas[path] = local_sha
    for _ in range(4):
        remote = remote_info(root)[2]
        remote_commit = gh_api(root, "GET", f"repos/{repo}/git/commits/{remote}")
        base_tree_sha = remote_commit["tree"]["sha"]
        remote_entries = api_tree(root, repo, base_tree_sha)
        overlap = sorted(path for path in paths if remote_entries.get(path) != base_entries[path])
        if overlap:
            raise FinalizationError("remote changed reviewed paths before API publication: " + ", ".join(overlap))
        updates = []
        for path, value in record["entries"].items():
            mode = value.split(":", 1)[0] if value else (base_entries[path] or "100644").split(":", 1)[0]
            updates.append({"path": path, "mode": mode, "type": "blob",
                            "sha": blob_shas.get(path)})
        created_tree = gh_api(root, "POST", f"repos/{repo}/git/trees", {
            "base_tree": base_tree_sha, "tree": updates})["sha"]
        published_entries = api_tree(root, repo, created_tree)
        differences = {path for path in set(remote_entries) | set(published_entries)
                       if remote_entries.get(path) != published_entries.get(path)}
        if differences != set(paths) or any(published_entries.get(path) != record["entries"][path] for path in paths):
            raise FinalizationError("API tree differs from the reviewed project changes")
        created_commit = gh_api(root, "POST", f"repos/{repo}/git/commits", {
            "message": message, "tree": created_tree, "parents": [remote]})["sha"]
        attempt_path.write_text(json.dumps({"reviewed_commit": record["commit"],
                                            "created_commit": created_commit}, sort_keys=True) + "\n", encoding="utf-8")
        try:
            gh_api(root, "PATCH", f"repos/{repo}/git/refs/heads/{branch}", {
                "sha": created_commit, "force": False})
        except FinalizationError:
            latest = remote_info(root)[2]
            if api_commit_is_published(root, repo, created_commit, latest):
                return {"repo": repo, "branch": branch, "commit": created_commit,
                        "remote_head": latest, "result": "published and verified by GitHub API"}
            if latest != remote:
                continue
            raise
        verified = remote_info(root)[2]
        if not api_commit_is_published(root, repo, created_commit, verified):
            raise FinalizationError(f"API update returned success, but remote head is {verified}; inspect commit {created_commit}")
        return {"repo": repo, "branch": branch, "commit": created_commit,
                "remote_head": verified, "result": "published and verified by GitHub API"}
    raise FinalizationError("remote branch advanced repeatedly during API publication")


def reviewed_snapshot(root: Path) -> dict[str, str | None]:
    paths = changed_paths(root, "--cached")
    if not paths:
        raise FinalizationError("no project changes to publish")
    for path in paths:
        if EXCLUDED_PARTS.intersection(Path(path).parts) or path.startswith("~$"):
            raise FinalizationError(f"local work or cache file was staged: {path}")
    ignored = subprocess.run(
        ["git", "-c", "core.longpaths=true", "check-ignore", "--no-index", "-z", "--stdin"],
        cwd=root, input=b"\0".join(path.encode("utf-8", "surrogateescape") for path in paths) + b"\0",
        capture_output=True,
    )
    if ignored.returncode not in {0, 1}:
        raise FinalizationError("could not check staged paths against Git ignore rules")
    if ignored.stdout:
        ignored_paths = [part.decode("utf-8", "replace") for part in ignored.stdout.split(b"\0") if part]
        unexpected = [path for path in ignored_paths if not is_intended_telegram_outbox(path)]
        if unexpected:
            raise FinalizationError(f"ignored file was staged: {unexpected[0]}")
    return index_entries(root, paths)


def review(root: Path) -> dict:
    ensure_worktree(root)
    git(root, "add", "-A")
    outbox = sorted((root / TELEGRAM_OUTBOX_PREFIX).glob("*.json"))
    if outbox:
        git(root, "add", "-f", "--", *(str(path.relative_to(root)) for path in outbox))
    git(root, "diff", "--cached", "--check")
    entries = reviewed_snapshot(root)
    work = root / ".codex-work" / "finalization"
    record_path = work / "review.json"
    current_status = hashlib.sha256(status(root)).hexdigest()
    if record_path.is_file():
        try:
            cached = json.loads(record_path.read_text(encoding="utf-8"))
            cached_patch = work / "review.patch"
            if (cached.get("base") == head(root) and cached.get("entries") == entries and
                    cached.get("status_sha256") == current_status and cached_patch.is_file() and
                    hashlib.sha256(cached_patch.read_bytes()).hexdigest() == cached.get("patch_sha256")):
                return {"base": cached["base"], "files": list(entries), "patch": str(cached_patch), "reused": True}
        except (OSError, ValueError, TypeError):
            pass
    # Take the remote snapshot before generating an expensive binary patch.  Later
    # publication still rechecks it, so this is an optimization rather than trust.
    repo, branch, remote = remote_info(root)
    patch = git(root, "diff", "--cached", "--binary", "--full-index", "--no-ext-diff")
    work.mkdir(parents=True, exist_ok=True)
    (work / "review.patch").write_bytes(patch)
    result = {"base": head(root), "remote_head": remote, "repo": repo, "branch": branch, "entries": entries,
              "patch_sha256": hashlib.sha256(patch).hexdigest(),
              "status_sha256": current_status}
    (work / "review.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"base": result["base"], "files": list(entries), "patch": str(work / "review.patch"), "reused": False}


def verify_review(root: Path, record: dict) -> None:
    if head(root) != record["base"]:
        raise FinalizationError("HEAD changed after review; review the complete diff again")
    if reviewed_snapshot(root) != record["entries"]:
        raise FinalizationError("staged project files changed after review")
    patch_path = root / ".codex-work" / "finalization" / "review.patch"
    if (not patch_path.is_file() or
            hashlib.sha256(patch_path.read_bytes()).hexdigest() != record["patch_sha256"] or
            hashlib.sha256(status(root)).hexdigest() != record["status_sha256"]):
        raise FinalizationError("working tree changed after review; review again")


def verify_commit_content(root: Path, entries: dict[str, str | None]) -> None:
    paths = changed_paths(root, "HEAD^", "HEAD")
    if index_entries(root, paths) != entries:
        raise FinalizationError("remote integration changed the reviewed project files; inspect and review the new diff before pushing")


def publish(root: Path, subject: str, body: str) -> dict[str, str]:
    ensure_worktree(root)
    if not subject.strip() or "\n" in subject:
        raise FinalizationError("provide one concise commit subject")
    review_path = root / ".codex-work" / "finalization" / "review.json"
    if not review_path.is_file():
        raise FinalizationError("review the staged diff before publishing")
    record = json.loads(review_path.read_text(encoding="utf-8"))
    if head(root) == record["base"]:
        verify_review(root, record)
        repo, branch, remote = remote_info(root)
        git(root, "-c", "commit.gpgsign=false", "commit", "-m", subject,
            "-m", body or "Reviewed project changes")
        base = record["base"]
    else:
        if status(root) or git(root, "log", "-1", "--format=%s").decode().strip() != subject:
            raise FinalizationError("unpublished commit or local files changed; inspect before retrying")
        verify_commit_content(root, record["entries"])
        base = git(root, "rev-parse", "HEAD^").decode().strip()
        repo, branch, remote = remote_info(root)
    for _ in range(4):
        fetch(root, branch, remote)
        if remote != base:
            if not ancestor(root, base, remote):
                raise FinalizationError("remote branch no longer descends from reviewed base; inspect remote history")
            overlap = sorted(set(changed_paths(root, base, remote)).intersection(record["entries"]))
            if overlap:
                raise FinalizationError("remote advanced on reviewed paths; inspect before integration: " + ", ".join(overlap))
            git(root, "-c", "commit.gpgsign=false", "rebase", "--no-gpg-sign", remote)
            verify_commit_content(root, record["entries"])
        commit = head(root)
        result = subprocess.run(["git", "-c", "core.longpaths=true", "push", "origin", f"HEAD:refs/heads/{branch}"], cwd=root, capture_output=True)
        if result.returncode == 0:
            verified = remote_info(root)[2]
            if verified != commit:
                fetch(root, branch, verified)
                if not ancestor(root, commit, verified):
                    raise FinalizationError(f"push returned success but remote head is {verified}; published commit ancestry could not be verified")
            if status(root):
                raise FinalizationError("published commit is verified, but isolated checkout has local changes")
            return {"repo": repo, "branch": branch, "commit": commit,
                    "remote_head": verified, "result": "published and verified" if verified == commit else "published; remote advanced afterward"}
        latest = remote_info(root)[2]
        if latest == remote:
            raise FinalizationError("non-force push failed without a remote advance: " + result.stderr.decode("utf-8", "replace")[:1000])
        base, remote = remote, latest
    raise FinalizationError("remote branch advanced repeatedly; review its current head and retry")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="action", required=True)
    commands.add_parser("preflight")
    commands.add_parser("review")
    commands.add_parser("review-commit")
    commands.add_parser("publish-api")
    release = commands.add_parser("publish")
    release.add_argument("--subject", required=True)
    release.add_argument("--body", default="")
    args = parser.parse_args(argv)
    root = Path.cwd().resolve()
    try:
        if args.action == "preflight":
            result = preflight(root)
        elif args.action == "review":
            result = review(root)
        elif args.action == "review-commit":
            result = review_committed(root)
        elif args.action == "publish-api":
            result = publish_api(root)
        else:
            result = publish(root, args.subject, args.body)
    except (FinalizationError, OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Repository finalization stopped: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
