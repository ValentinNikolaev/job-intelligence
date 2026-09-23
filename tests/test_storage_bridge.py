"""Real Mongo replica-set coverage for the legacy-path storage bridge.

Run with ``JOBINTEL_TEST_MONGODB_URI`` pointing at a disposable local replica set.
Each test run creates and drops only a randomized ``jobintel_test_`` database.
"""
from __future__ import annotations

import os
import shutil
import tempfile
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml

from jobintel import storage_bridge as bridge
from jobintel.api_usage import ApiUsageLog
from jobintel.matching import MatchAnalyzer
from jobintel.manual_status_log import ManualStatusEvent, append_manual_status_event
from jobintel.models import CollectorSummary, NormalizedJob
from jobintel.prefilter import RejectedRegistry, Rejection
from jobintel.registry import Registry
from jobintel.triage import should_skip_model, write_triage


TEST_URI = os.environ.get(
    "JOBINTEL_TEST_MONGODB_URI",
    "",
).strip()
try:
    from jobintel.mongodb_storage import MongoStore
except ModuleNotFoundError:  # Normal YAML-only test environments do not install PyMongo.
    MongoStore = None  # type: ignore[assignment,misc]


@unittest.skipUnless(TEST_URI and MongoStore is not None, "Mongo replica-set test environment is required")
class StorageBridgeIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = Path(tempfile.mkdtemp(prefix="jobintel-storage-bridge-"))
        self.database_name = f"jobintel_test_{uuid.uuid4().hex}"
        (self.temp / "config").mkdir()
        (self.temp / "sources").mkdir()
        (self.temp / "registry" / "candidate").mkdir(parents=True)
        (self.temp / "registry" / "candidate" / "match-profile.md").write_text("Candidate evidence", encoding="utf-8")
        (self.temp / "config" / "data-services.yaml").write_text(
            yaml.safe_dump({"storage": {"backend": "mongodb", "database_name": self.database_name, "schema_version": 1, "cutover_verified": True}}),
            encoding="utf-8",
        )
        (self.temp / "sources" / ".env").write_text(
            f"MONGODB_URI={TEST_URI}\nJOBINTEL_DATABASE_NAME={self.database_name}\nJOBINTEL_STORAGE_BACKEND=mongodb\n",
            encoding="utf-8",
        )
        self.store = MongoStore(TEST_URI, self.database_name)
        self.store.ensure_schema()
        self.now = datetime(2026, 9, 21, tzinfo=timezone.utc)
        self.registry = Registry(self.temp / "registry", clock=lambda: self.now, id_factory=lambda: "vacancy-1")

    def tearDown(self) -> None:
        try:
            self.store.client.drop_database(self.database_name)
        finally:
            self.store.close()
            for store in bridge._STORES.values():
                store.close()
            bridge._STORES.clear()
            shutil.rmtree(self.temp, ignore_errors=True)

    @staticmethod
    def _job() -> NormalizedJob:
        return NormalizedJob("test-source", "source-1", "https://example.test/jobs/1", "Backend Engineer", "Example", "Python backend role", location="Rome", remote=True)

    def test_bridge_uses_mongo_not_poisoned_operational_yaml_and_noop_collects(self) -> None:
        created = self.registry.upsert(self._job())
        self.assertEqual("created", created.status)
        directory = self.temp / "registry" / "jobs" / created.directory
        self.assertFalse((directory / "meta.yaml").exists())
        directory.mkdir(parents=True, exist_ok=True)
        (directory / "meta.yaml").write_text("id: poisoned\nstatus: rejected\n", encoding="utf-8")
        self.assertEqual("vacancy-1", self.registry._scan()[0]["meta"]["id"])
        revision = self.store.get("vacancies", "vacancy-1")["revision"]
        self.assertEqual("unchanged", self.registry.upsert(self._job()).status)
        self.assertEqual(revision, self.store.get("vacancies", "vacancy-1")["revision"])
        self.assertFalse((directory / "triage.yaml").exists())
        write_triage(directory)
        self.assertTrue(should_skip_model(directory) is False)

    def test_archived_source_identity_reuses_same_vacancy_and_status_callback_rolls_back(self) -> None:
        created = self.registry.upsert(self._job())
        directory = self.temp / "registry" / "jobs" / created.directory
        bridge.archive_vacancy(directory, "archive/test.zip")
        result = self.registry.upsert(self._job())
        self.assertEqual("vacancy-1", result.vacancy_id)
        with self.assertRaisesRegex(RuntimeError, "audit failure"):
            self.registry.update_status(created.directory, "applied", on_updated=lambda *_: (_ for _ in ()).throw(RuntimeError("audit failure")))
        stored = self.store.get("vacancies", "vacancy-1")
        self.assertEqual("found", stored["meta"]["status"])
        self.assertEqual(["found"], [event["status"] for event in stored["meta"]["status_history"]])

    def test_match_freshness_and_manual_usage_are_mongo_backed(self) -> None:
        created = self.registry.upsert(self._job())
        directory = self.temp / "registry" / "jobs" / created.directory
        analyzer = MatchAnalyzer(self.temp / "registry", [self.temp / "registry" / "candidate" / "match-profile.md"], _DraftClient())
        analyzer.publish_analysis(directory, _analysis())
        self.assertTrue(analyzer.is_current(directory))
        ApiUsageLog(self.temp / "registry" / "source-api-usage.yaml").record(CollectorSummary(source="test", api_requests=2))
        self.assertFalse((self.temp / "registry" / "source-api-usage.yaml").exists())
        log = self.store.get("operational_logs", "source-api-usage.yaml")
        self.assertEqual(2, log["payload"]["sources"]["test"]["total_requests"])

    def test_applied_and_interview_log_project_one_application_and_history(self) -> None:
        created = self.registry.upsert(self._job())
        log_path = self.temp / "registry" / "manual-status-log.yaml"
        self._status_with_audit(created.directory, "applied", log_path)
        applications = self.store.list("applications")
        history = self.store.list("status_events")
        self.assertEqual(1, len(applications))
        self.assertEqual("applied", applications[0]["current_status"])
        self.assertEqual(2, len(history))
        application_id = applications[0]["_id"]
        package_url = "https://github.com/example/jobs/tree/revision/application"
        with self.store.lease("imported-package-link"):
            imported = dict(applications[0], package_locator=package_url)
            self.store.put("applications", application_id, imported, expected_revision=applications[0]["revision"])
        event_ids = {row["_id"] for row in history}
        self._status_with_audit(created.directory, "interview", log_path)
        applications = self.store.list("applications")
        history = self.store.list("status_events")
        self.assertEqual(1, len(applications))
        self.assertEqual(application_id, applications[0]["_id"])
        self.assertEqual("interview", applications[0]["current_status"])
        self.assertEqual(package_url, applications[0]["package_locator"])
        self.assertEqual(3, len(history))
        self.assertTrue(event_ids.issubset({row["_id"] for row in history}))

    def test_log_failure_rolls_back_status_log_and_projection(self) -> None:
        created = self.registry.upsert(self._job())
        log_path = self.temp / "registry" / "manual-status-log.yaml"

        def fail_after_append(before: dict, after: dict, directory: Path) -> None:
            append_manual_status_event(log_path, _manual_event(before, after, directory))
            raise RuntimeError("audit failure after append")

        with self.assertRaisesRegex(RuntimeError, "audit failure after append"):
            self.registry.update_status(created.directory, "applied", on_updated=fail_after_append)
        self.assertIsNone(self.store.get("operational_logs", "manual-status-log.yaml"))
        self.assertEqual([], self.store.list("applications"))
        self.assertEqual([], self.store.list("status_events"))
        self.assertEqual("found", self.store.get("vacancies", "vacancy-1")["meta"]["status"])

    def test_archived_prefilter_recollection_keeps_stable_identity(self) -> None:
        rejected = RejectedRegistry(self.temp / "registry", cache_entries=True)
        rejection = Rejection("role_mismatch", "title is an obvious mismatch")
        rejected.upsert(self._job(), rejection)
        first = self.store.list("prefilter_rejections")
        self.assertEqual(1, len(first))
        first_id = first[0]["_id"]
        bridge.archive_vacancy(self.temp / "registry" / "rejected" / first[0]["directory"], "archive/prefilter.zip")
        archived_revision = self.store.get("prefilter_rejections", first_id)["revision"]
        rejected.upsert(self._job(), rejection)
        rows = self.store.list("prefilter_rejections")
        self.assertEqual([first_id], [row["_id"] for row in rows])
        self.assertEqual(archived_revision, rows[0]["revision"])

    def _status_with_audit(self, directory_name: str, status: str, log_path: Path) -> None:
        self.now += timedelta(seconds=1)
        self.registry.update_status(
            directory_name,
            status,
            on_updated=lambda before, after, directory: append_manual_status_event(
                log_path, _manual_event(before, after, directory)
            ),
        )

    def test_package_publication_failure_restores_files_and_database_receipt(self) -> None:
        from jobintel.applications import _publish_staged_package
        created = self.registry.upsert(self._job())
        directory = self.temp / "registry" / "jobs" / created.directory
        target = directory / "application"
        target.mkdir()
        for name, content in {"cv.md": "old CV", "manifest.yaml": "old: true"}.items():
            (target / name).write_text(content, encoding="utf-8")
        bridge.record_package(directory, target)
        old_receipt = self.store.list("artifact_manifests")
        old_vacancy = self.store.get("vacancies", "vacancy-1")
        staging = directory / ".application-staging"
        staging.mkdir()
        (staging / "cv.md").write_text("new CV", encoding="utf-8")
        (staging / "manifest.yaml").write_text("new: true", encoding="utf-8")

        def fail_after_record(published: Path) -> None:
            with bridge.mutation(directory):
                bridge.record_package(directory, published)
                raise RuntimeError("manifest publication failed")

        with self.assertRaisesRegex(RuntimeError, "manifest publication failed"):
            _publish_staged_package(staging, target, ["cv.md"], on_published=fail_after_record)
        self.assertEqual("old CV", (target / "cv.md").read_text(encoding="utf-8"))
        self.assertEqual("new CV", (staging / "cv.md").read_text(encoding="utf-8"))
        self.assertEqual(old_receipt, self.store.list("artifact_manifests"))
        self.assertEqual(old_vacancy, self.store.get("vacancies", "vacancy-1"))

    def test_mongo_archive_retains_original_artifacts_without_unpublished_zip(self) -> None:
        from scripts.archive_jobs import archive
        created = self.registry.upsert(self._job())
        directory = self.temp / "registry" / "jobs" / created.directory
        analyzer = MatchAnalyzer(self.temp / "registry", [self.temp / "registry" / "candidate" / "match-profile.md"], _DraftClient())
        analyzer.publish_analysis(directory, _analysis())
        original = (directory / "job.md").read_bytes()
        self.assertEqual(1, archive(self.temp, "low-score", 101))
        self.assertEqual(original, (directory / "job.md").read_bytes())
        self.assertEqual([], list((self.temp / "archives").rglob("*.zip")))
        doc = self.store.get("vacancies", "vacancy-1")
        self.assertTrue(doc["archived"])
        self.assertIsNone(doc["archive_path"])


class StorageBridgeNoFallbackTests(unittest.TestCase):
    def test_mongodb_without_uri_fails_instead_of_falling_back_to_yaml(self) -> None:
        root = Path(tempfile.mkdtemp(prefix="jobintel-storage-no-uri-"))
        try:
            (root / "config").mkdir()
            (root / "registry" / "jobs").mkdir(parents=True)
            (root / "config" / "data-services.yaml").write_text("storage:\n  backend: mongodb\n", encoding="utf-8")
            (root / "registry" / "jobs" / "stale" / "meta.yaml").parent.mkdir()
            with self.assertRaisesRegex(RuntimeError, "requires MONGODB_URI"):
                bridge.metadata_paths(root / "registry" / "jobs")
        finally:
            shutil.rmtree(root, ignore_errors=True)


class _DraftClient:
    model = "test-model"

    def analyze(self, **_: object) -> dict:
        return _analysis()


def _analysis() -> dict:
    return {"score": 80, "recommendation": "match", "summary": "Strong backend fit.", "strengths": ["Python"], "gaps": ["None"], "concerns": ["None"], "hard_rejection": False, "hard_rejection_reason": None}


def _manual_event(before: dict, after: dict, directory: Path) -> ManualStatusEvent:
    return ManualStatusEvent(
        changed_at=str(after["updated_at"]), vacancy_id=str(after["id"]), directory=directory.name,
        company=str(after["company"]), title=str(after["title"]), from_status=str(before["status"]),
        to_status=str(after["status"]), reason="integration test status audit", actor="test",
        interaction_source="test",
    )


if __name__ == "__main__":
    unittest.main()
