from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import finalize_repository as fin


def run(*args: str, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class RepositoryFinalizationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="jobintel-finalize-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.bare = self.root / "remote.git"
        self.seed = self.root / "seed"
        self.work = self.root / "managed"
        run("git", "init", "--bare", "--initial-branch=main", str(self.bare), cwd=self.root)
        run("git", "clone", str(self.bare), str(self.seed), cwd=self.root)
        run("git", "config", "user.name", "Fixture", cwd=self.seed)
        run("git", "config", "user.email", "fixture@example.test", cwd=self.seed)
        run("git", "config", "commit.gpgsign", "false", cwd=self.seed)
        (self.seed / ".gitignore").write_text(".codex-work/\n", encoding="utf-8")
        (self.seed / "existing.txt").write_text("original\n", encoding="utf-8")
        run("git", "add", "-A", cwd=self.seed)
        run("git", "commit", "-m", "Seed fixture", cwd=self.seed)
        run("git", "push", "origin", "HEAD:main", cwd=self.seed)
        run("git", "worktree", "add", "--detach", str(self.work), "HEAD", cwd=self.seed)
        self.patch_remote = patch.object(fin, "remote_info", side_effect=lambda _root: (
            "example/fixture", "main", run("git", "--git-dir", str(self.bare), "rev-parse", "refs/heads/main", cwd=self.root)
        ))
        self.patch_remote.start()
        self.addCleanup(self.patch_remote.stop)

    def test_isolated_review_refusal_concurrency_and_non_force_publication(self) -> None:
        with self.assertRaisesRegex(fin.FinalizationError, "managed Git worktree"):
            fin.preflight(self.seed)
        ignored = self.work / ".codex-work" / "private.txt"
        ignored.parent.mkdir()
        ignored.write_text("keep", encoding="utf-8")
        unrelated = self.work / "unrelated.txt"
        unrelated.write_text("keep", encoding="utf-8")
        with self.assertRaisesRegex(fin.FinalizationError, "local changes"):
            fin.preflight(self.work)
        self.assertEqual("keep", unrelated.read_text(encoding="utf-8"))
        self.assertEqual("keep", ignored.read_text(encoding="utf-8"))
        unrelated.unlink()
        self.assertEqual("main", fin.preflight(self.work)["branch"])
        run("git", "config", "core.autocrlf", "true", cwd=self.work)
        (self.work / "existing.txt").write_bytes(b"original\r\n")
        with self.assertRaisesRegex(fin.FinalizationError, "no project changes"):
            fin.review(self.work)
        (self.work / "task.txt").write_text("first\n", encoding="utf-8")
        fin.review(self.work)
        (self.work / "task.txt").write_text("changed after review\n", encoding="utf-8")
        with self.assertRaisesRegex(fin.FinalizationError, "working tree changed"):
            fin.publish(self.work, "Add fixture", "")
        self.assertEqual("first", run("git", "show", ":task.txt", cwd=self.work))
        (self.work / "task.txt").write_text("first\n", encoding="utf-8")
        long_path = self.work / ("directory-" + "x" * 100) / ("file-" + "y" * 100 + ".txt")
        long_path.parent.mkdir()
        long_native = Path("\\\\?\\" + str(long_path)) if os.name == "nt" else long_path
        long_native.write_text("long path\n", encoding="utf-8")
        self.addCleanup(lambda: long_native.unlink(missing_ok=True))
        (self.work / "binary.bin").write_bytes(bytes([0, 255, 10, 0]))
        (self.work / "existing.txt").write_text("reviewed\n", encoding="utf-8")
        snapshot = fin.review(self.work)
        self.assertEqual(4, len(snapshot["files"]))
        self.assertIn(b"GIT binary patch", Path(snapshot["patch"]).read_bytes())
        self.assertTrue(fin.review(self.work)["reused"])
        with patch.object(fin, "fetch", side_effect=fin.FinalizationError("temporary fetch failure")):
            with self.assertRaisesRegex(fin.FinalizationError, "temporary fetch failure"):
                fin.publish(self.work, "Preserve reviewed fixture changes", "Fixture run")
        (self.seed / "parallel.txt").write_text("parallel\n", encoding="utf-8")
        run("git", "add", "-A", cwd=self.seed)
        run("git", "commit", "-m", "Parallel fixture", cwd=self.seed)
        run("git", "push", "origin", "HEAD:main", cwd=self.seed)
        result = fin.publish(self.work, "Preserve reviewed fixture changes", "Fixture run")
        self.assertEqual("first\n", (self.work / "task.txt").read_text(encoding="utf-8"))
        self.assertEqual("parallel\n", (self.work / "parallel.txt").read_text(encoding="utf-8"))
        self.assertEqual("keep", ignored.read_text(encoding="utf-8"))
        self.assertEqual("1", run("git", "rev-list", "--count", "HEAD^..HEAD", cwd=self.work))
        self.assertEqual(result["commit"], run("git", "--git-dir", str(self.bare), "rev-parse", "refs/heads/main", cwd=self.root))
        self.assertEqual("", run("git", "-c", "core.longpaths=true", "status", "--porcelain", cwd=self.work))
        self.assertEqual("original\n", (self.seed / "existing.txt").read_text(encoding="utf-8"))
        api_review = fin.review_committed(self.work)
        self.assertEqual(4, len(api_review["files"]))
        self.assertEqual(result["commit"], fin.verify_committed_review(self.work)["commit"])

    def test_reports_exact_remote_overlap_before_rebase(self) -> None:
        fin.preflight(self.work)
        (self.work / "existing.txt").write_text("reviewed\n", encoding="utf-8")
        fin.review(self.work)
        (self.seed / "existing.txt").write_text("parallel\n", encoding="utf-8")
        run("git", "add", "-A", cwd=self.seed)
        run("git", "commit", "-m", "Overlap fixture", cwd=self.seed)
        run("git", "push", "origin", "HEAD:main", cwd=self.seed)
        with self.assertRaisesRegex(fin.FinalizationError, r"remote advanced on reviewed paths.*existing.txt"):
            fin.publish(self.work, "Preserve reviewed fixture", "Fixture run")


if __name__ == "__main__":
    unittest.main()
