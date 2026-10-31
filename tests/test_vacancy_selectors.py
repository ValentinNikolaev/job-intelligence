from __future__ import annotations

import os
import tempfile
import unittest
import uuid
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

from pymongo import MongoClient

from jobintel import storage_bridge as bridge
from jobintel.matching import MatchAnalyzer, MatchError
from jobintel.mongodb_storage import MongoStore


class VacancySelectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.registry = Path(self.temp.name) / "registry"
        self.jobs = self.registry / "jobs"

    def test_exact_mongo_selector_uses_bounded_query(self) -> None:
        store = MongoStore("mongodb://example", "jobintel_test", client=MagicMock())
        store.list = MagicMock(return_value=[{"_id": "vacancy-1", "directory": "role-1"}])

        with patch.object(bridge, "get_store", return_value=store):
            self.assertEqual([self.jobs / "role-1"], bridge.resolve_vacancy_directories(self.registry, "vacancy-1"))

        store.list.assert_called_once_with(
            "vacancies",
            {"scope": "jobs", "archived": False,
             "$or": [{"_id": "vacancy-1"}, {"directory": "vacancy-1"}]},
            sort=[("directory", 1)],
        )

    def test_id_directory_collision_keeps_both_application_matches(self) -> None:
        store = MongoStore("mongodb://example", "jobintel_test", client=MagicMock())
        store.list = MagicMock(return_value=[
            {"_id": "other", "directory": "vacancy-1"},
            {"_id": "vacancy-1", "directory": "role-1"},
        ])
        with patch.object(bridge, "get_store", return_value=store):
            self.assertEqual(
                [self.jobs / "role-1", self.jobs / "vacancy-1"],
                bridge.resolve_vacancy_directories(self.registry, "vacancy-1"),
            )
            analyzer = MatchAnalyzer(self.registry, [], SimpleNamespace(model="fixture"))
            self.assertEqual([self.jobs / "vacancy-1"], analyzer.resolve("vacancy-1"))

    def test_missing_mongo_selector_does_not_use_frozen_file(self) -> None:
        frozen = self.jobs / "legacy" / "meta.yaml"
        frozen.parent.mkdir(parents=True)
        frozen.write_text("id: legacy\n", encoding="utf-8")
        store = MongoStore("mongodb://example", "jobintel_test", client=MagicMock())
        store.list = MagicMock(return_value=[])
        with patch.object(bridge, "get_store", return_value=store):
            self.assertEqual([], bridge.resolve_vacancy_directories(self.registry, "legacy"))
            analyzer = MatchAnalyzer(self.registry, [], SimpleNamespace(model="fixture"))
            with self.assertRaisesRegex(MatchError, "vacancy not found"):
                analyzer.resolve("legacy")

    def test_batch_selector_excludes_archived_and_preserves_collision(self) -> None:
        store = MongoStore("mongodb://example", "jobintel_test", client=MagicMock())
        store._local.vacancy_batch = {"documents": {"vacancies": {
            "one": {"_id": "one", "scope": "jobs", "archived": False, "directory": "role"},
            "two": {"_id": "two", "scope": "jobs", "archived": False, "directory": "one"},
            "old": {"_id": "old", "scope": "jobs", "archived": True, "directory": "one"},
        }}}
        self.assertEqual(["one", "role"], [row["directory"] for row in store.find_vacancy_selector("one")])

    def test_real_mongo_selector_returns_only_active_id_and_directory_matches(self) -> None:
        uri = os.environ.get("JOBINTEL_TEST_MONGODB_URI", "").strip()
        if not uri:
            self.skipTest("JOBINTEL_TEST_MONGODB_URI is not configured")
        client = MongoClient(uri, serverSelectionTimeoutMS=5_000)
        database_name = "jobintel_selector_test_" + uuid.uuid4().hex
        self.addCleanup(client.close)
        self.addCleanup(client.drop_database, database_name)
        store = MongoStore(uri, database_name, client=client)
        store.database["vacancies"].insert_many([
            {"_id": "one", "scope": "jobs", "archived": False, "directory": "role"},
            {"_id": "two", "scope": "jobs", "archived": False, "directory": "one"},
            {"_id": "old", "scope": "jobs", "archived": True, "directory": "one"},
        ])
        self.assertEqual(["one", "role"], [row["directory"] for row in store.find_vacancy_selector("one")])


if __name__ == "__main__":
    unittest.main()
