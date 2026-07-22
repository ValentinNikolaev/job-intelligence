from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from jobintel.models import NormalizedJob
from jobintel.registry import Registry


def make_job(**overrides: object) -> NormalizedJob:
    values: dict[str, object] = {
        "source": "adzuna",
        "source_job_id": "a-1",
        "source_url": "https://jobs.test/a-1",
        "title": "Senior Backend Engineer",
        "company": "Acme Ltd.",
        "description": "Aggregator description.",
        "location": "Remote Europe",
        "remote": True,
        "employment_type": "full-time",
        "published_at": "2026-07-20T10:00:00Z",
    }
    values.update(overrides)
    return NormalizedJob(**values)  # type: ignore[arg-type]


class RegistryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name) / "registry"
        self.now = datetime(2026, 7, 22, 18, 30, 15, tzinfo=timezone.utc)
        self.registry = Registry(
            self.root,
            clock=lambda: self.now,
            id_factory=lambda: "31d603fe-5bcb-4ea0-9d39-8fb214f17750",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _directories(self) -> list[Path]:
        return [path for path in (self.root / "jobs").iterdir() if path.is_dir()]

    def _meta(self) -> dict[str, object]:
        path = self._directories()[0] / "meta.yaml"
        return yaml.safe_load(path.read_text(encoding="utf-8"))

    def test_repeated_source_record_is_byte_for_byte_unchanged(self) -> None:
        first = self.registry.upsert(make_job())
        directory = self._directories()[0]
        before = {path.name: path.read_bytes() for path in directory.iterdir()}
        second = self.registry.upsert(make_job())
        after = {path.name: path.read_bytes() for path in directory.iterdir()}

        self.assertEqual("created", first.status)
        self.assertEqual("unchanged", second.status)
        self.assertEqual(before, after)
        self.assertEqual(1, len(self._directories()))

    def test_status_is_initialized_and_manual_updates_preserve_history(self) -> None:
        created = self.registry.upsert(make_job())
        meta = self._meta()
        self.assertEqual("found", meta["status"])
        self.assertEqual(
            [{"status": "found", "changed_at": "2026-07-22T18:30:15Z"}],
            meta["status_history"],
        )

        self.now = datetime(2026, 7, 25, 14, 0, tzinfo=timezone.utc)
        self.assertTrue(self.registry.update_status(created.vacancy_id, "interview"))
        self.assertFalse(self.registry.update_status(created.directory, "interview"))
        meta = self._meta()
        self.assertEqual("interview", meta["status"])
        self.assertEqual(2, len(meta["status_history"]))
        self.assertEqual(
            {"status": "interview", "changed_at": "2026-07-25T14:00:00Z"},
            meta["status_history"][-1],
        )

    def test_schema_v1_metadata_is_migrated_once(self) -> None:
        self.registry.upsert(make_job())
        directory = self._directories()[0]
        meta_path = directory / "meta.yaml"
        legacy = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        legacy["schema_version"] = 1
        legacy.pop("status")
        legacy.pop("status_history")
        meta_path.write_text(yaml.safe_dump(legacy, sort_keys=False), encoding="utf-8")

        self.registry.regenerate_index()
        migrated_once = meta_path.read_bytes()
        self.registry.regenerate_index()

        migrated = yaml.safe_load(migrated_once.decode("utf-8"))
        self.assertEqual(2, migrated["schema_version"])
        self.assertEqual("found", migrated["status"])
        self.assertEqual(
            [{"status": "found", "changed_at": migrated["discovered_at"]}],
            migrated["status_history"],
        )
        self.assertEqual(migrated_once, meta_path.read_bytes())

    def test_cross_source_match_merges_into_one_directory(self) -> None:
        self.registry.upsert(make_job())
        self.now = datetime(2026, 7, 22, 19, 10, tzinfo=timezone.utc)
        result = self.registry.upsert(
            make_job(
                source="direct",
                source_job_id="d-9",
                source_url="https://careers.acme.test/jobs/d-9",
                company="Acme",
                description="Direct and substantially more complete description.",
            )
        )

        meta = self._meta()
        self.assertEqual("merged", result.status)
        self.assertEqual(1, len(self._directories()))
        self.assertEqual(2, len(meta["sources"]))  # type: ignore[arg-type]
        self.assertEqual("2026-07-22T18:30:15Z", meta["discovered_at"])
        self.assertEqual("2026-07-22T19:10:00Z", meta["updated_at"])
        self.assertEqual("direct", meta["data_source"])
        self.assertIn("Direct and substantially", (self._directories()[0] / "job.md").read_text(encoding="utf-8"))

    def test_same_source_fingerprint_collision_stays_separate(self) -> None:
        ids = iter(("id-one", "id-two"))
        registry = Registry(self.root, clock=lambda: self.now, id_factory=lambda: next(ids))
        registry.upsert(make_job(source_job_id="opening-1"))
        registry.upsert(make_job(source_job_id="opening-2", source_url="https://jobs.test/opening-2"))
        self.assertEqual(2, len(self._directories()))

    def test_lower_ranked_source_does_not_replace_direct_content(self) -> None:
        self.registry.upsert(
            make_job(
                source="direct",
                source_job_id="d-1",
                source_url="https://careers.acme.test/jobs/d-1",
                company="Acme",
                description="Authoritative direct description.",
                employment_type="Permanent",
            )
        )
        self.registry.upsert(
            make_job(
                source="jooble",
                source_job_id="j-1",
                source_url="https://jooble.test/j-1",
                description="A much longer aggregator description that must not win. " * 5,
                employment_type="Contract",
            )
        )
        meta = self._meta()
        body = (self._directories()[0] / "job.md").read_text(encoding="utf-8")
        self.assertEqual("Permanent", meta["employment_type"])
        self.assertIn("Authoritative direct description.", body)
        self.assertNotIn("aggregator description", body)

    def test_known_source_update_keeps_directory_and_discovery_time(self) -> None:
        created = self.registry.upsert(make_job())
        self.now = datetime(2026, 7, 23, 8, 0, tzinfo=timezone.utc)
        updated = self.registry.upsert(make_job(title="Principal Backend Engineer"))
        meta = self._meta()
        self.assertEqual("updated", updated.status)
        self.assertEqual(created.directory, updated.directory)
        self.assertEqual("2026-07-22T18:30:15Z", meta["discovered_at"])
        self.assertEqual("Principal Backend Engineer", meta["title"])

    def test_source_specific_metadata_is_stored_with_source_reference(self) -> None:
        self.registry.upsert(
            make_job(
                source="ashby",
                source_job_id="ashby-1",
                source_url="https://jobs.ashbyhq.com/acme/ashby-1",
                source_metadata={
                    "board": "acme",
                    "application_url": "https://jobs.ashbyhq.com/acme/ashby-1/application",
                    "compensation": {"currency": "EUR"},
                },
            )
        )
        source = self._meta()["sources"][0]  # type: ignore[index]
        self.assertEqual("acme", source["metadata"]["board"])
        self.assertEqual("EUR", source["metadata"]["compensation"]["currency"])

    def test_index_is_sorted_escaped_and_not_rewritten_when_current(self) -> None:
        ids = iter(("old-id", "new-id"))
        registry = Registry(self.root, clock=lambda: self.now, id_factory=lambda: next(ids))
        registry.upsert(make_job(title="Backend | Platform"))
        self.now = datetime(2026, 7, 23, 9, 0, tzinfo=timezone.utc)
        registry.upsert(
            make_job(
                source_job_id="a-2",
                source_url="https://jobs.test/a-2",
                title="Frontend Engineer",
            )
        )
        self.assertTrue(registry.regenerate_index())
        index = (self.root / "index.md").read_text(encoding="utf-8")
        self.assertLess(index.index("Frontend Engineer"), index.index("Backend \\| Platform"))
        self.assertFalse(registry.regenerate_index())


if __name__ == "__main__":
    unittest.main()
