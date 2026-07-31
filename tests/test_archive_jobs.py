from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts" / "archive_jobs.py"
SPEC = importlib.util.spec_from_file_location("archive_jobs", SCRIPT)
assert SPEC and SPEC.loader
archive_jobs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive_jobs)


class ArchiveJobsTests(unittest.TestCase):
    def make_job(self, root: Path, number: int, *, score: int | None = None, skipped: bool = False) -> None:
        directory = root / "registry" / "jobs" / f"job-{number:03d}"
        directory.mkdir(parents=True)
        (directory / "meta.yaml").write_text(yaml.safe_dump({"id": str(number)}), encoding="utf-8")
        (directory / "job.md").write_text(f"job {number}", encoding="utf-8")
        if score is not None:
            (directory / "match.yaml").write_text(yaml.safe_dump({"score": score}), encoding="utf-8")
        if skipped:
            (directory / "triage.yaml").write_text(yaml.safe_dump({"skip_model": True}), encoding="utf-8")

    def test_does_not_archive_at_threshold(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(100):
                self.make_job(root, number, score=10)
            self.assertEqual(0, archive_jobs.archive(root, "low-score", 65))
            self.assertFalse(any((root / "archives" / "low-score").glob("*.zip")))

    def test_archives_and_removes_low_scores_after_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(101):
                self.make_job(root, number, score=64)
            self.make_job(root, 999, score=65)
            self.assertEqual(101, archive_jobs.archive(root, "low-score", 65))
            archive = next((root / "archives" / "low-score").glob("*.zip"))
            self.assertTrue(archive.is_file())
            self.assertFalse((root / "registry" / "jobs" / "job-000").exists())
            self.assertTrue((root / "registry" / "jobs" / "job-999").exists())

    def test_archives_skipped_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(101):
                self.make_job(root, number, skipped=True)
            self.make_job(root, 999, score=1)
            self.assertEqual(101, archive_jobs.archive(root, "skipped", 65))
            self.assertFalse((root / "registry" / "jobs" / "job-000").exists())
            self.assertTrue((root / "registry" / "jobs" / "job-999").exists())


if __name__ == "__main__":
    unittest.main()
