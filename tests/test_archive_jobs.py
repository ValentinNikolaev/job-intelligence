from __future__ import annotations

import importlib.util
import tempfile
import unittest
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path

import yaml


SCRIPT = Path(__file__).parents[1] / "scripts" / "archive_jobs.py"
SPEC = importlib.util.spec_from_file_location("archive_jobs", SCRIPT)
assert SPEC and SPEC.loader
archive_jobs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(archive_jobs)


class ArchiveJobsTests(unittest.TestCase):
    def make_job(
        self,
        root: Path,
        number: int,
        *,
        score: int | None = None,
        skipped: bool = False,
        discovered_at: str | None = None,
    ) -> None:
        directory = root / "registry" / "jobs" / f"job-{number:03d}"
        directory.mkdir(parents=True)
        meta = {"id": str(number)}
        if discovered_at is not None:
            meta["discovered_at"] = discovered_at
        (directory / "meta.yaml").write_text(yaml.safe_dump(meta), encoding="utf-8")
        (directory / "job.md").write_text(f"job {number}", encoding="utf-8")
        if score is not None:
            (directory / "match.yaml").write_text(yaml.safe_dump({"score": score}), encoding="utf-8")
        if skipped:
            (directory / "triage.yaml").write_text(yaml.safe_dump({"skip_model": True}), encoding="utf-8")

    def test_does_not_archive_below_minimum(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for number in range(100):
                self.make_job(root, number, score=10)
            self.assertEqual(0, archive_jobs.archive(root, "low-score", 65, min_items=101))
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

    def test_archives_stale_vacancies_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            stale_day = date.today() - timedelta(days=8)
            stale = datetime.combine(stale_day, time(12, 0), tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
            fresh_day = date.today() - timedelta(days=7)
            fresh = datetime.combine(fresh_day, time(12, 0), tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
            for number in range(101):
                self.make_job(root, number, discovered_at=stale)
            self.make_job(root, 999, discovered_at=fresh)
            self.assertEqual(101, archive_jobs.archive(root, "stale", 65, max_age_days=7))
            self.assertFalse((root / "registry" / "jobs" / "job-000").exists())
            self.assertTrue((root / "registry" / "jobs" / "job-999").exists())


if __name__ == "__main__":
    unittest.main()
