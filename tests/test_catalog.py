from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from jobintel.catalog import generate_catalog
from jobintel.models import NormalizedJob
from jobintel.registry import Registry


def make_job(source_job_id: str, title: str) -> NormalizedJob:
    return NormalizedJob(
        source="direct",
        source_job_id=source_job_id,
        source_url=f"https://jobs.example.test/{source_job_id}",
        title=title,
        company="Example Inc",
        description="Build backend services.",
        company_description="Example builds useful products.",
        location="Remote EU",
        remote=True,
    )


class CatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.registry_root = self.project / "registry"
        self.catalog_root = self.project / "catalog"
        self.now = datetime(2026, 7, 22, 10, 0, tzinfo=timezone.utc)
        ids = iter(("vacancy-old", "vacancy-new"))
        self.registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: next(ids),
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_single_catalog_links_artifacts_and_sorts_newest_first(self) -> None:
        old = self.registry.upsert(make_job("old", "Backend Engineer"))
        old_dir = self.registry_root / "jobs" / old.directory
        application = old_dir / "application"
        application.mkdir()
        for filename in (
            "cv.md",
            "cv.docx",
            "cover-letter.md",
            "cover-letter.docx",
            "analysis.md",
            "interview-preparation.md",
        ):
            (application / filename).write_bytes(b"content")
        self.now = datetime(2026, 7, 23, 9, 0, tzinfo=timezone.utc)
        new = self.registry.upsert(make_job("new", "Platform Engineer"))
        self.registry.update_status(new.vacancy_id, "reviewing")

        first = generate_catalog(self.registry_root, self.catalog_root)
        second = generate_catalog(self.registry_root, self.catalog_root)
        content = (self.catalog_root / "index.md").read_text(encoding="utf-8")

        self.assertEqual(2, first.vacancies)
        self.assertFalse(first.monthly)
        self.assertEqual((), second.changed_files)
        self.assertIn("- Found: 1", content)
        self.assertIn("- Reviewing: 1", content)
        self.assertLess(content.index("Platform Engineer"), content.index("Backend Engineer"))
        self.assertIn("[Direct](https://jobs.example.test/old)", content)
        self.assertIn("[MD](../registry/jobs/", content)
        self.assertIn("[DOCX](../registry/jobs/", content)
        self.assertIn("company.md", content)

    def test_large_catalog_splits_by_month(self) -> None:
        self.registry.upsert(make_job("july", "July Engineer"))
        self.now = datetime(2026, 8, 2, 9, 0, tzinfo=timezone.utc)
        self.registry.upsert(make_job("august", "August Engineer"))

        result = generate_catalog(
            self.registry_root, self.catalog_root, monthly_threshold=1
        )
        index = (self.catalog_root / "index.md").read_text(encoding="utf-8")

        self.assertTrue(result.monthly)
        self.assertTrue((self.catalog_root / "2026-07.md").is_file())
        self.assertTrue((self.catalog_root / "2026-08.md").is_file())
        self.assertLess(index.index("2026-08"), index.index("2026-07"))


if __name__ == "__main__":
    unittest.main()
