from __future__ import annotations

import unittest
from pathlib import Path

from jobintel.commit_messages import (
    ARCHIVE_TEMPLATES,
    COLLECTION_TEMPLATES,
    archive_subject,
    collection_subject,
)


class CommitMessageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parents[1]

    def test_collection_rotates_through_five_distinct_templates(self) -> None:
        subjects = {
            collection_subject(run_number, active=3, rejected=2)
            for run_number in range(1, 6)
        }

        self.assertEqual(5, len(COLLECTION_TEMPLATES))
        self.assertEqual(5, len(subjects))
        self.assertEqual(
            collection_subject(1, active=3, rejected=2),
            collection_subject(6, active=3, rejected=2),
        )

    def test_archive_rotates_through_five_distinct_templates(self) -> None:
        subjects = {
            archive_subject(run_number, count=4, reason="stale")
            for run_number in range(1, 6)
        }

        self.assertEqual(5, len(ARCHIVE_TEMPLATES))
        self.assertEqual(5, len(subjects))
        self.assertEqual(
            archive_subject(1, count=4, reason="stale"),
            archive_subject(6, count=4, reason="stale"),
        )

    def test_subjects_use_singular_nouns_for_one_vacancy(self) -> None:
        self.assertIn("1 active vacancy", collection_subject(1, active=1, rejected=1))
        self.assertIn("1 reject", collection_subject(1, active=1, rejected=1))
        self.assertIn("1 stale vacancy", archive_subject(1, count=1, reason="stale"))

    def test_invalid_values_are_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "at least 1"):
            collection_subject(0, active=1, rejected=0)
        with self.assertRaisesRegex(ValueError, "negative"):
            archive_subject(1, count=-1, reason="stale")
        with self.assertRaisesRegex(ValueError, "empty"):
            archive_subject(1, count=1, reason=" ")

    def test_github_mutation_workflows_use_the_template_selector(self) -> None:
        workflow_names = (
            "job-intelligence-collection.yml",
            "job-intelligence-archive-low-score.yml",
            "job-intelligence-archive-skipped.yml",
            "job-intelligence-archive-stale.yml",
            "job-intelligence-archive-rejected.yml",
        )

        for workflow_name in workflow_names:
            with self.subTest(workflow=workflow_name):
                workflow = (
                    self.project_root / ".github" / "workflows" / workflow_name
                ).read_text(encoding="utf-8")
                self.assertIn("python -m jobintel.commit_messages", workflow)
                self.assertIn('${GITHUB_RUN_NUMBER}', workflow)
                self.assertIn('-m "${commit_subject}"', workflow)


if __name__ == "__main__":
    unittest.main()
