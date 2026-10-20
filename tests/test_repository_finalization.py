from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts import finalize_repository as fin


def run(*args: str, cwd: Path) -> str:
    return subprocess.run(args, cwd=cwd, check=True, capture_output=True, text=True).stdout.strip()


class PublicationBranchResolutionTests(unittest.TestCase):
    def test_explicit_branch_uses_exact_ref_or_default_base_when_missing(self) -> None:
        for refs, expected in (([], "a" * 40), ([
            {"ref": "refs/heads/review/python/other", "object": {"sha": "c" * 40}},
            {"ref": "refs/heads/review/python", "object": {"sha": "b" * 40}},
        ], "b" * 40)):
            with self.subTest(refs=refs), tempfile.TemporaryDirectory() as temporary:
                def gh(_root, *args):
                    if args[0] == "repo":
                        return json.dumps({"nameWithOwner": "example/fixture", "defaultBranchRef": {"name": "main"}}).encode()
                    if "matching-refs" in args[1]:
                        return json.dumps(refs).encode()
                    return ("a" * 40).encode()

                with patch.object(fin, "gh", side_effect=gh):
                    self.assertEqual(("example/fixture", "review/python", expected),
                                     fin.remote_info(Path(temporary), "review/python"))

    def test_invalid_branch_is_rejected_before_remote_access(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch.object(fin, "gh") as gh:
            with self.assertRaises(fin.FinalizationError):
                fin.remote_info(Path(temporary), "../invalid")
            gh.assert_not_called()

    def test_publication_rejects_a_changed_remote_destination(self) -> None:
        record = {"repo": "example/fixture", "branch": "main", "target_branch": None}
        with patch.object(fin, "remote_info", return_value=("example/fixture", "other", "a" * 40)):
            with self.assertRaisesRegex(fin.FinalizationError, "branch changed after review"):
                fin.reviewed_remote_info(Path.cwd(), record)


class MatchPolicyFinalizationGateTests(unittest.TestCase):
    def test_only_relevant_increment_dependencies_are_checked(self) -> None:
        self.assertEqual(set(), fin.evaluation_dependencies(["docs/unrelated.md"]))
        matching = fin.evaluation_dependencies(["jobintel/matching.py"])
        self.assertIn("config/matching-policy.yaml", matching)
        self.assertIn("tests/fixtures/match-policy-baseline-schema.json", matching)
        self.assertNotIn("jobintel/matching.py", matching)
        self.assertNotIn("config/cv-editorial-knowledge.yaml", matching)
        both = fin.evaluation_dependencies(["prompts/vacancy-match.md"])
        self.assertIn("config/cv-editorial-knowledge.yaml", both)
        self.assertIn("jobintel/editorial_eval.py", both)

    def test_dependency_blob_changes_block_even_outside_reviewed_paths(self) -> None:
        for dependency in fin.evaluation_dependencies(["prompts/vacancy-match.md"]):
            with self.subTest(dependency=dependency):
                with self.assertRaisesRegex(fin.FinalizationError, "remote changed evaluation dependencies"):
                    fin.require_unchanged_evaluation_dependencies(
                        {dependency: "100644:old"}, {dependency: "100644:new"}, ["prompts/vacancy-match.md"],
                    )
        fin.require_unchanged_evaluation_dependencies({}, {"config/matching-policy.yaml": "new"}, ["docs/unrelated.md"])

    def test_unrelated_changes_do_not_run_match_evaluation(self) -> None:
        with patch.object(fin, "command") as command:
            fin.require_match_policy_evaluation(Path.cwd(), ["docs/unrelated.md"])
        command.assert_not_called()

    def test_each_matching_input_requires_exact_decisions_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            ignored = root / ".codex-work"
            ignored.mkdir()
            (ignored / "match-policy-receipt.json").write_text('{"ok":true}', encoding="utf-8")
            (ignored / "match-policy-pack.json").write_text('{}', encoding="utf-8")
            (ignored / "other-decisions.json").write_text('{}', encoding="utf-8")
            for changed in fin.MATCH_POLICY_PATHS:
                with self.subTest(changed=changed), patch.object(fin, "command") as command:
                    with self.assertRaisesRegex(fin.FinalizationError, "match-policy-decisions.json"):
                        fin.require_match_policy_evaluation(root, [changed])
                    command.assert_not_called()

    def test_existing_decisions_are_recomputed_with_project_cli(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decisions = root / ".codex-work/match-policy-decisions.json"
            decisions.parent.mkdir()
            decisions.write_text('{}', encoding="utf-8")
            with patch.object(fin, "command") as command:
                fin.require_match_policy_evaluation(root, ["jobintel/matching.py"])
            command.assert_called_once_with(
                sys.executable, "scripts/evaluate_match_policy.py", "evaluate", "--input", str(decisions),
                "--output", ".codex-work/match-policy-receipt.json", cwd=root,
            )

    def test_evaluator_failure_blocks_finalization(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            decisions = root / ".codex-work/match-policy-decisions.json"
            decisions.parent.mkdir()
            decisions.write_text('{}', encoding="utf-8")
            with patch.object(fin, "command", side_effect=fin.FinalizationError("stale decisions")):
                with self.assertRaisesRegex(fin.FinalizationError, "stale decisions"):
                    fin.require_match_policy_evaluation(root, ["config/matching-policy.yaml"])

    def test_matching_inputs_also_trigger_editorial_gate(self) -> None:
        self.assertTrue({"config/matching-policy.yaml", "prompts/vacancy-match.md"}.issubset(fin.EDITORIAL_POLICY_PATHS))

    def test_publication_verification_and_commit_reviews_recheck_decisions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            record = root / ".codex-work/finalization/api-review.json"
            record.parent.mkdir(parents=True)
            record.write_text(json.dumps({"commit": "a" * 40}), encoding="utf-8")
            with patch.object(fin, "ensure_worktree"), patch.object(fin, "status", return_value=b""), \
                    patch.object(fin, "head", return_value="a" * 40), \
                    patch.object(fin, "tree_entries", return_value={}), \
                    patch.object(fin, "require_complete_project_tree"), \
                    patch.object(fin, "changed_paths", return_value=["jobintel/matching.py"]):
                for entrypoint in ("verify_review", "review_committed", "verify_committed_review"):
                    with self.subTest(entrypoint=entrypoint):
                        with self.assertRaisesRegex(fin.FinalizationError, "match-policy-decisions.json"):
                            if entrypoint == "verify_review":
                                fin.verify_review(root, {"entries": {"jobintel/matching.py": "blob"}})
                            else:
                                getattr(fin, entrypoint)(root)


class RepositoryFinalizationTests(unittest.TestCase):
    def test_publish_retry_rechecks_evaluation_before_push(self) -> None:
        path = self.work / "jobintel/matching.py"
        path.parent.mkdir(parents=True)
        path.write_text("# reviewed matching change\n", encoding="utf-8")
        subject = "Review matching changes"
        with patch.object(fin, "require_match_policy_evaluation"):
            fin.review(self.work)
            with patch.object(fin, "fetch", side_effect=fin.FinalizationError("first publication interrupted")):
                with self.assertRaisesRegex(fin.FinalizationError, "interrupted"):
                    fin.publish(self.work, subject, "")
        with patch.object(fin, "require_match_policy_evaluation", side_effect=fin.FinalizationError("stale evaluation")) as gate:
            with self.assertRaisesRegex(fin.FinalizationError, "stale evaluation"):
                fin.publish(self.work, subject, "")
        gate.assert_called_once()
        self.assertNotEqual(run("git", "rev-parse", "HEAD", cwd=self.work), self.remote_info(self.work)[2])

    def test_remote_evaluation_dependency_change_stops_before_rebase(self) -> None:
        path = self.work / "jobintel/matching.py"
        path.parent.mkdir(parents=True)
        path.write_text("# reviewed matching change\n", encoding="utf-8")
        with patch.object(fin, "require_match_policy_evaluation"):
            fin.review(self.work)
        remote_policy = self.seed / "config/matching-policy.yaml"
        remote_policy.write_text("changed remote analysis preferences\n", encoding="utf-8")
        run("git", "add", "-A", cwd=self.seed)
        run("git", "commit", "-m", "Change remote analysis preferences", cwd=self.seed)
        run("git", "push", "origin", "HEAD:main", cwd=self.seed)
        with patch.object(fin, "require_match_policy_evaluation"):
            with self.assertRaisesRegex(fin.FinalizationError, r"evaluation dependencies.*config/matching-policy.yaml"):
                fin.publish(self.work, "Review matching changes", "")
        self.assertFalse((self.work / "config/matching-policy.yaml").exists())

    def test_evaluation_is_rechecked_immediately_before_push(self) -> None:
        path = self.work / "jobintel/matching.py"
        path.parent.mkdir(parents=True)
        path.write_text("# reviewed matching change\n", encoding="utf-8")
        with patch.object(fin, "require_match_policy_evaluation"):
            fin.review(self.work)
        remote_before = self.remote_info(self.work)[2]
        with patch.object(fin, "require_match_policy_evaluation", side_effect=[None, fin.FinalizationError("pre-push stale evaluation")]) as gate:
            with self.assertRaisesRegex(fin.FinalizationError, "pre-push stale evaluation"):
                fin.publish(self.work, "Review matching changes", "")
        self.assertEqual(2, gate.call_count)
        self.assertEqual(remote_before, self.remote_info(self.work)[2])

    def test_api_remote_dependency_change_stops_before_tree_composition(self) -> None:
        path = self.work / "jobintel/matching.py"
        path.parent.mkdir(parents=True)
        path.write_text("# reviewed matching change\n", encoding="utf-8")
        with patch.object(fin, "require_match_policy_evaluation"):
            fin.review(self.work)
            with patch.object(fin, "fetch", side_effect=fin.FinalizationError("interrupted")):
                with self.assertRaises(fin.FinalizationError):
                    fin.publish(self.work, "Review matching changes", "")
            fin.review_committed(self.work)
            record = fin.verify_committed_review(self.work)
        paths = run("git", "ls-files", cwd=self.work).splitlines()
        remote_tree = fin.tree_entries(self.work, "HEAD^", paths)
        remote_tree["config/matching-policy.yaml"] = "100644:changed-policy"
        requests = []

        def api(_root, method, endpoint, payload=None):
            requests.append((method, endpoint))
            if endpoint.endswith("/git/blobs"):
                return {"sha": record["entries"]["jobintel/matching.py"].split(":")[1]}
            if method == "GET" and "/git/commits/" in endpoint:
                return {"tree": {"sha": "remote-tree"}}
            self.fail(f"API mutation reached after changed dependency: {method} {endpoint}")

        with patch.object(fin, "verify_committed_review", return_value=record), \
                patch.object(fin, "gh_api", side_effect=api), patch.object(fin, "api_tree", return_value=remote_tree):
            with self.assertRaisesRegex(fin.FinalizationError, r"evaluation dependencies.*config/matching-policy.yaml"):
                fin.publish_api(self.work)
        self.assertFalse(any(endpoint.endswith(("/git/trees", "/git/commits", "/git/refs")) for _, endpoint in requests))

    def test_editorial_policy_change_requires_executable_evaluation(self) -> None:
        path = self.work / 'config/cv-editorial-knowledge.yaml'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text('schema_version: 1\n', encoding='utf-8')
        with self.assertRaisesRegex(fin.FinalizationError, 'editorial decisions'):
            fin.review(self.work)

    def test_matching_runtime_change_requires_independent_evaluation_on_review(self) -> None:
        path = self.work / "jobintel/matching.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# changed runtime matching inputs\n", encoding="utf-8")
        with self.assertRaisesRegex(fin.FinalizationError, "match-policy-decisions.json"):
            fin.review(self.work)

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
        for required in fin.REQUIRED_PROJECT_FILES:
            path = self.seed / required
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n", encoding="utf-8")
        run("git", "add", "-A", cwd=self.seed)
        run("git", "commit", "-m", "Seed fixture", cwd=self.seed)
        run("git", "push", "origin", "HEAD:main", cwd=self.seed)
        run("git", "worktree", "add", "--detach", str(self.work), "HEAD", cwd=self.seed)
        self.patch_remote = patch.object(fin, "remote_info", side_effect=self.remote_info)
        self.patch_remote.start()
        self.addCleanup(self.patch_remote.stop)

    def remote_info(self, _root: Path, branch: str | None = None):
        selected = branch or "main"
        remote = subprocess.run(
            ["git", "--git-dir", str(self.bare), "rev-parse", "--verify", f"refs/heads/{selected}"],
            cwd=self.root, capture_output=True, text=True,
        )
        sha = remote.stdout.strip() if remote.returncode == 0 else run(
            "git", "--git-dir", str(self.bare), "rev-parse", "refs/heads/main", cwd=self.root,
        )
        return "example/fixture", selected, sha

    def test_explicit_branch_publication_preserves_main(self) -> None:
        original_main = self.remote_info(self.work)[2]
        branch = "review/python-fixes"
        run("git", "switch", "-c", branch, cwd=self.work)
        self.assertEqual(branch, fin.preflight(self.work, branch=branch)["branch"])
        (self.work / "fix.txt").write_text("reviewed fix\n", encoding="utf-8")
        fin.review(self.work, branch=branch)

        result = fin.publish(self.work, "Fix reviewed Python behavior", "Regression checks passed")

        self.assertEqual(branch, result["branch"])
        self.assertEqual(original_main, self.remote_info(self.work)[2])
        self.assertEqual(result["commit"], self.remote_info(self.work, branch)[2])
        api_review = fin.review_committed(self.work)
        self.assertEqual(branch, fin.verify_committed_review(self.work)["target_branch"])
        self.assertEqual(result["commit"], api_review["commit"])

    def test_review_cache_is_bound_to_publication_branch(self) -> None:
        (self.work / "fix.txt").write_text("reviewed fix\n", encoding="utf-8")
        fin.review(self.work)
        fin.review(self.work, branch="review/python-fixes")
        record = json.loads((self.work / ".codex-work/finalization/review.json").read_text(encoding="utf-8"))
        self.assertEqual("review/python-fixes", record["target_branch"])

    def test_new_branch_integrates_concurrent_main_without_publishing_to_main(self) -> None:
        branch = "review/python-fixes"
        (self.work / "fix.txt").write_text("reviewed fix\n", encoding="utf-8")
        fin.review(self.work, branch=branch)
        (self.seed / "parallel.txt").write_text("parallel change\n", encoding="utf-8")
        run("git", "add", "-A", cwd=self.seed)
        run("git", "commit", "-m", "Concurrent main change", cwd=self.seed)
        run("git", "push", "origin", "HEAD:main", cwd=self.seed)
        remote_main = self.remote_info(self.work)[2]

        result = fin.publish(self.work, "Fix reviewed Python behavior", "")

        self.assertEqual(remote_main, self.remote_info(self.work)[2])
        self.assertEqual(result["commit"], self.remote_info(self.work, branch)[2])
        self.assertEqual("parallel change\n", (self.work / "parallel.txt").read_text(encoding="utf-8"))
        fin.review_committed(self.work)
        self.assertEqual(branch, fin.verify_committed_review(self.work)["target_branch"])

    def test_api_fallback_creates_only_the_reviewed_feature_branch(self) -> None:
        branch = "review/api-fixes"
        original_main = self.remote_info(self.work)[2]
        (self.work / "fix.txt").write_text("reviewed fix\n", encoding="utf-8")
        fin.review(self.work, branch=branch)
        with patch.object(fin, "fetch", side_effect=fin.FinalizationError("fetch failed")):
            with self.assertRaisesRegex(fin.FinalizationError, "fetch failed"):
                fin.publish(self.work, "Fix reviewed Python behavior", "")
        fin.review_committed(self.work)
        record = fin.verify_committed_review(self.work)
        paths = run("git", "ls-files", cwd=self.work).splitlines()
        base_tree = fin.tree_entries(self.work, "HEAD^", paths)
        updated_tree = {**base_tree, **record["entries"]}
        remote_sha = original_main
        requests = []

        def api(_root, method, endpoint, payload=None):
            nonlocal remote_sha
            requests.append((method, endpoint, payload))
            if endpoint.endswith("/git/blobs"):
                return {"sha": record["entries"]["fix.txt"].split(":")[1]}
            if method == "GET" and "/git/commits/" in endpoint:
                return {"tree": {"sha": "base-tree"}}
            if endpoint.endswith("/git/trees"):
                return {"sha": "updated-tree"}
            if endpoint.endswith("/git/commits"):
                return {"sha": "f" * 40}
            if endpoint.endswith("/git/refs"):
                self.assertEqual(f"refs/heads/{branch}", payload["ref"])
                remote_sha = payload["sha"]
                return {}
            self.fail(f"unexpected API call: {method} {endpoint}")

        with patch.object(fin, "remote_info", side_effect=lambda _root, target=None: (
            "example/fixture", target or "main", remote_sha,
        )), patch.object(fin, "remote_branch_sha", return_value=None), patch.object(
            fin, "api_tree", side_effect=lambda _root, _repo, sha: base_tree if sha == "base-tree" else updated_tree,
        ), patch.object(fin, "gh_api", side_effect=api):
            result = fin.publish_api(self.work)

        self.assertEqual(branch, result["branch"])
        self.assertEqual("f" * 40, result["commit"])
        self.assertEqual(original_main, self.remote_info(self.work)[2])
        self.assertFalse(any(method == "PATCH" for method, _, _ in requests))

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

    def test_review_includes_only_top_level_telegram_outbox_manifests(self) -> None:
        fin.preflight(self.work)
        outbox = self.work / "notifications" / "telegram" / "outbox"
        nested = outbox / "nested"
        nested.mkdir(parents=True)
        manifest = outbox / "manifest.json"
        manifest.write_text("{}\n", encoding="utf-8")
        (nested / "not-a-manifest.json").write_text("{}\n", encoding="utf-8")
        private = self.work / ".secret.json"
        private.write_text("secret\n", encoding="utf-8")
        exclude = self.root / "exclude"
        run("git", "config", "core.excludesfile", str(exclude), cwd=self.work)
        exclude.write_text("notifications/telegram/outbox/\n.secret.json\n", encoding="utf-8")
        snapshot = fin.review(self.work)
        self.assertIn("notifications/telegram/outbox/manifest.json", snapshot["files"])
        self.assertNotIn("notifications/telegram/outbox/nested/not-a-manifest.json", snapshot["files"])
        self.assertNotIn(".secret.json", snapshot["files"])

    def test_review_rejects_missing_repository_spine_file(self) -> None:
        fin.preflight(self.work)
        (self.work / "run.py").unlink()
        with self.assertRaisesRegex(fin.FinalizationError, r"staged project tree is missing required project files: run.py"):
            fin.review(self.work)


if __name__ == "__main__":
    unittest.main()
