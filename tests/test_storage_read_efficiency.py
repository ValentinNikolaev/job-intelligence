from __future__ import annotations

import copy
import os
import tempfile
import unittest
import uuid
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from jobintel import storage_bridge as bridge
from jobintel.registry import Registry, RegistryError


def vacancy_document(number: int) -> dict:
    return {
        "_id": f"vacancy-{number}", "scope": "jobs", "archived": False,
        "directory": f"directory-{number}",
        "meta": {
            "schema_version": 2, "id": f"vacancy-{number}", "title": f"Backend | Engineer {number}",
            "company": "Example", "fingerprint": f"fingerprint-{number}",
            "discovered_at": "2026-10-31T00:00:00Z", "status": "found",
            "status_history": [{"status": "found", "changed_at": "2026-10-31T00:00:00Z"}],
            "sources": [{"source": "test", "source_job_id": str(number), "url": f"https://example.test/jobs/{number}"}],
        },
        "match": {"score": number, "recommendation": "possible_match"},
        "job_text": "# Backend Engineer\n\nBuild services.\n",
        "company_text": "# Example\n\nA product company.\n",
    }


class StorageReadEfficiencyTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.registry = Registry(self.root / "registry", cache_entries=True)
        self.documents = [vacancy_document(0), vacancy_document(80)]
        self.documents[0]["match"] = None
        self.store = Mock()
        self.store.list_vacancies.side_effect = lambda **kwargs: copy.deepcopy(self.documents)
        self.store.get_by_directory.side_effect = lambda name, **kwargs: next(
            (copy.deepcopy(doc) for doc in self.documents if doc["directory"] == name), None
        )

    def test_index_matches_file_backend_without_per_vacancy_reads(self) -> None:
        for document in self.documents:
            directory = self.registry.jobs_dir / document["directory"]
            directory.mkdir()
            (directory / "meta.yaml").write_text(yaml.safe_dump(document["meta"]), encoding="utf-8")
            if document["match"] is not None:
                (directory / "match.yaml").write_text(yaml.safe_dump(document["match"]), encoding="utf-8")
        self.registry.regenerate_index()
        expected = self.registry.index_path.read_bytes()
        self.registry = Registry(self.root / "registry", cache_entries=True)
        with patch.object(bridge, "get_store", return_value=self.store):
            self.assertFalse(self.registry.regenerate_index())
        self.assertEqual(expected, self.registry.index_path.read_bytes())
        self.store.list_vacancies.assert_called_once_with(scope="jobs")
        self.store.get_by_directory.assert_not_called()

    def test_index_refreshes_mongo_snapshot_despite_cached_entries_and_frozen_files(self) -> None:
        with patch.object(bridge, "get_store", return_value=self.store):
            self.registry._scan()
            self.documents[1]["meta"]["title"] = "Updated title"
            self.documents[1]["match"]["score"] = 99
            self.registry.regenerate_index()
            self.assertIn("| 99 |", self.registry.index_path.read_text())
            self.assertIn("Updated title", self.registry.index_path.read_text())
            self.documents.clear()
            self.registry.regenerate_index()
            self.assertNotIn("Updated title", self.registry.index_path.read_text())
        self.store.get_by_directory.assert_not_called()

    def test_invalid_match_does_not_replace_existing_index(self) -> None:
        self.registry.index_path.write_text("previous index", encoding="utf-8")
        for match in ([], {}, {"score": True, "recommendation": "match"},
                      {"score": 101, "recommendation": "match"},
                      {"score": 50, "recommendation": "unknown"}):
            with self.subTest(match=match), patch.object(bridge, "get_store", return_value=self.store):
                self.documents[0]["match"] = match
                with self.assertRaises(RegistryError):
                    self.registry.regenerate_index()
                self.assertEqual("previous index", self.registry.index_path.read_text())

    def test_snapshot_reads_one_revision_and_reuses_unchanged_bytes(self) -> None:
        first = vacancy_document(80)
        later = copy.deepcopy(first)
        later["meta"]["title"] = "New revision"
        later["job_text"] = "New job text"
        self.store.get_by_directory.side_effect = lambda *args, **kwargs: (
            first if self.store.get_by_directory.call_count == 1 else later
        )
        directory = self.registry.jobs_dir / first["directory"]
        with patch.object(bridge, "get_store", return_value=self.store):
            snapshot = bridge.materialize_vacancy_snapshot(directory)
            self.assertEqual(1, self.store.get_by_directory.call_count)
            self.assertEqual(first["meta"], yaml.safe_load((snapshot / "meta.yaml").read_text()))
            self.assertEqual(first["job_text"], (snapshot / "job.md").read_text())
            changed = bridge.materialize_vacancy_snapshot(directory)
            self.assertNotEqual(snapshot, changed)
            timestamps = {path.name: path.stat().st_mtime_ns for path in changed.iterdir()}
            self.assertEqual(changed, bridge.materialize_vacancy_snapshot(directory))
            self.assertEqual(timestamps, {path.name: path.stat().st_mtime_ns for path in changed.iterdir()})
        self.assertEqual(first["job_text"], (snapshot / "job.md").read_text())
        self.assertFalse(directory.exists())

    def test_missing_snapshot_fields_never_fall_back_to_frozen_yaml(self) -> None:
        directory = self.registry.jobs_dir / self.documents[0]["directory"]
        directory.mkdir()
        (directory / "match.yaml").write_text("score: 100\n", encoding="utf-8")
        self.documents[0]["company_text"] = None
        with patch.object(bridge, "get_store", return_value=self.store):
            snapshot = bridge.materialize_vacancy_snapshot(directory)
            self.assertEqual({"meta.yaml", "job.md"}, {path.name for path in snapshot.iterdir()})
            self.documents.clear()
            missing = bridge.materialize_vacancy_snapshot(directory)
            self.assertEqual([], list(missing.iterdir()))


@unittest.skipUnless(os.environ.get("JOBINTEL_TEST_MONGODB_URI"), "Mongo replica-set test environment is required")
class MongoReadEfficiencyTests(unittest.TestCase):
    def test_real_store_reindex_and_snapshot_have_bounded_reads(self) -> None:
        from jobintel.mongodb_storage import MongoStore

        store = MongoStore(os.environ["JOBINTEL_TEST_MONGODB_URI"], f"jobintel_test_{uuid.uuid4().hex}")
        try:
            store.ensure_schema()
            documents = [vacancy_document(number) for number in range(30)]
            store.database.vacancies.insert_many(documents)
            with tempfile.TemporaryDirectory() as temporary:
                registry = Registry(Path(temporary) / "registry")
                with patch.object(bridge, "get_store", return_value=store), patch.object(
                    store, "get_by_directory", wraps=store.get_by_directory
                ) as reads, patch.object(store, "list_vacancies", wraps=store.list_vacancies) as lists:
                    registry.regenerate_index()
                    reads.assert_not_called()
                    lists.assert_called_once_with(scope="jobs")
                    snapshot = bridge.materialize_vacancy_snapshot(registry.jobs_dir / "directory-0")
                    reads.assert_called_once_with("directory-0", scope="jobs")
                    self.assertEqual(documents[0]["meta"], yaml.safe_load((snapshot / "meta.yaml").read_text()))
        finally:
            store.client.drop_database(store.database_name)
            store.close()
