from __future__ import annotations

import subprocess
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jobintel.worktree import WorktreeError, create_codex_worktree, load_git_workflow_policy


POLICY = """\
schema_version: 1
remote: origin
main_branch: main
main_writer: github-actions
codex:
  branch_prefix: codex/
  worktree_root: .codex-work/worktrees
  short_path_length: 10
"""


class WorktreeTests(unittest.TestCase):
    def test_creates_short_isolated_branch_from_origin_main(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / ".git").mkdir()
            (root / "config").mkdir()
            (root / "config" / "git-workflow.yaml").write_text(POLICY, encoding="utf-8")
            commands: list[list[str]] = []

            def runner(command, **kwargs):
                del kwargs
                commands.append(list(command))
                stdout = ".git\n" if tuple(command[-2:]) == ("rev-parse", "--git-common-dir") else ""
                return subprocess.CompletedProcess(command, 0, stdout=stdout, stderr="")

            result = create_codex_worktree(
                root,
                "Prepare CoinsPaid vacancy",
                now=datetime(2026, 8, 11, 10, 0, tzinfo=timezone.utc),
                runner=runner,
            )

            self.assertEqual("origin/main", result.base)
            self.assertEqual(
                "codex/prepare-coinspaid-vacanc-20260811-100000",
                result.branch,
            )
            self.assertEqual(10, len(result.path.name))
            self.assertEqual(root / ".codex-work" / "worktrees" / result.path.name, result.path)
            self.assertIn(["git", "-C", str(root), "fetch", "origin", "main"], commands)
            self.assertEqual("worktree", commands[-1][3])
            self.assertEqual("origin/main", commands[-1][-1])

    def test_rejects_a_policy_that_allows_another_main_writer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "policy.yaml"
            path.write_text(POLICY.replace("github-actions", "codex"), encoding="utf-8")
            with self.assertRaisesRegex(WorktreeError, "main_writer"):
                load_git_workflow_policy(path)


if __name__ == "__main__":
    unittest.main()
