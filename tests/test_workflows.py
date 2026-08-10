from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from jobintel.workflows import WorkflowError, load_workflow_policy


class WorkflowPolicyTests(unittest.TestCase):
    def test_repository_policy_routes_prepare_scores_without_overlap(self) -> None:
        root = Path(__file__).resolve().parents[1]
        policy = load_workflow_policy(root / "config" / "codex-workflows.yaml")

        self.assertFalse(policy.prepare_score_is_eligible("prepare", 64))
        self.assertTrue(policy.prepare_score_is_eligible("prepare", 65))
        self.assertTrue(policy.prepare_score_is_eligible("prepare", 74))
        self.assertTrue(policy.prepare_score_is_eligible("prepare", 75))
        self.assertEqual(7, policy.prepare_max_age_days)
        self.assertEqual(10, policy.prepare_batch_size)
        self.assertEqual(
            "codex:gpt-5.6-terra:medium",
            policy.workflow("prepare").model_label,
        )
        self.assertEqual("luna_low", policy.workflow("analyze").default_profile)
        self.assertEqual(
            "codex:gpt-5.6-terra:medium",
            policy.resolve_model_profile("analyze", "terra-medium").model_label,
        )

    def test_model_profile_must_be_allowed_by_workflow(self) -> None:
        root = Path(__file__).resolve().parents[1]
        policy = load_workflow_policy(root / "config" / "codex-workflows.yaml")

        with self.assertRaisesRegex(WorkflowError, "not allowed"):
            policy.resolve_model_profile("analyze", "unknown")

    def test_invalid_prepare_min_score_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "workflows.yaml"
            path.write_text(
                "schema_version: 1\nprepare_min_score: invalid\nworkflows: {}\n",
                encoding="utf-8",
            )
            with self.assertRaises(WorkflowError):
                load_workflow_policy(path)

    def test_prepare_batch_size_cannot_exceed_hard_limit(self) -> None:
        root = Path(__file__).resolve().parents[1]
        source = (root / "config" / "codex-workflows.yaml").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "workflows.yaml"
            path.write_text(
                source.replace("prepare_batch_size: 10", "prepare_batch_size: 11"),
                encoding="utf-8",
            )

            with self.assertRaisesRegex(WorkflowError, "must not exceed 10"):
                load_workflow_policy(path)


if __name__ == "__main__":
    unittest.main()
