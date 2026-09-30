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
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel import storage_bridge as bridge
from jobintel.api_usage import ApiUsageLog
from jobintel.matching import MatchAnalyzer
from jobintel.manual_status_log import ManualStatusEvent, append_manual_status_event
from jobintel.models import CollectorSummary, NormalizedJob
from jobintel.prefilter import RejectedRegistry, Rejection
from jobintel.registry import Registry
from jobintel.storage_contract import SourceIdentityConflict, StorageConflictError
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

    def test_collection_batch_uses_bulk_writes_and_replay_is_unchanged(self) -> None:
        from jobintel.cli import _store_collected_jobs
        jobs = [replace(self._job(), source_job_id=f"job-{index}", title=f"PHP Engineer {index}")
                for index in range(20)]
        registry = Registry(self.temp / "registry", clock=lambda: self.now, cache_entries=True)
        rejected = RejectedRegistry(self.temp / "registry")
        store = bridge.get_store(registry.root)
        collection_type = type(store.database["vacancies"])
        original_bulk = collection_type.bulk_write
        original_find_one = collection_type.find_one
        writes = []

        def bulk(collection, requests, **kwargs):
            writes.append((collection.name, len(requests)))
            return original_bulk(collection, requests, **kwargs)

        def find_one(collection, *args, **kwargs):
            if collection.name in {"vacancies", "source_identities", "prefilter_rejections"}:
                self.fail(f"per-record network read: {collection.name}")
            return original_find_one(collection, *args, **kwargs)

        with patch.object(store, "list", wraps=store.list) as reads, patch.object(
            collection_type, "bulk_write", bulk
        ), patch.object(collection_type, "find_one", find_one):
            first = _store_collected_jobs("test", CollectorSummary(source="test"), jobs, registry, rejected)
            self.assertEqual(20, first.created)
            self.assertEqual([("source_identities", 20), ("vacancies", 20)], writes)
            self.assertEqual(3, reads.call_count)
            writes.clear()
            reads.reset_mock()
            second = _store_collected_jobs("test", CollectorSummary(source="test"), jobs, registry, rejected)
            self.assertEqual(20, second.unchanged)
            self.assertEqual([], writes)
            self.assertEqual(3, reads.call_count)
        self.assertEqual([], list(registry.jobs_dir.iterdir()))
        self.assertTrue(all(row["revision"] == 1 for row in self.store.list_vacancies()))
        unrelated = replace(jobs[0], source_job_id="outside-batch", title="Unrelated PHP Engineer")
        with bridge.vacancy_batch(registry.root, jobs=[unrelated]):
            registry.upsert(unrelated)
        self.assertEqual(21, len(registry._scan()))

    def test_batch_cross_source_merge_and_prefilter_replay(self) -> None:
        first = replace(self._job(), source="adzuna", description="PHP backend")
        second = replace(first, source="custom", description="Detailed PHP backend requirements")
        with bridge.vacancy_batch(self.registry.root, jobs=[first, second]):
            created = self.registry.upsert(first)
            merged = self.registry.upsert(second)
        self.assertEqual("merged", merged.status)
        self.assertEqual(created.directory, merged.directory)
        row = self.store.get("vacancies", created.vacancy_id)
        self.assertEqual(2, len(row["meta"]["sources"]))
        self.assertIn(second.description, row["job_text"])
        rejected = RejectedRegistry(self.registry.root)
        rejected_job = replace(first, source_job_id="rejected")
        rejection = Rejection("tech_stack", "no target stack")
        with bridge.vacancy_batch(self.registry.root, jobs=[rejected_job]):
            rejected.upsert(rejected_job, rejection)
        prior = self.store.list_vacancies(scope="rejected")
        with bridge.vacancy_batch(self.registry.root, jobs=[rejected_job]):
            rejected.upsert(rejected_job, rejection)
        self.assertEqual(prior, self.store.list_vacancies(scope="rejected"))
        self.assertEqual([], list(rejected.root.iterdir()))

    def test_batch_failure_rolls_back_vacancies_identities_and_row_savepoints(self) -> None:
        first = self._job()
        failed = replace(first, source_job_id="failed", title="Different Engineer")
        self.registry._id_factory = lambda: str(uuid.uuid4())
        with bridge.vacancy_batch(self.registry.root, jobs=[first, failed]) as store:
            created = self.registry.upsert(first)
            with self.assertRaisesRegex(ValueError, "bad row"):
                with bridge.vacancy_batch_item(store):
                    self.registry.upsert(failed)
                    raise ValueError("bad row")
        self.assertEqual([created.vacancy_id], [row["_id"] for row in self.store.list_vacancies()])
        self.assertIsNone(self.store.resolve_source(failed.source, failed.source_job_id))
        before = self.store.list_vacancies()
        with self.assertRaisesRegex(RuntimeError, "failed batch"):
            with bridge.vacancy_batch(self.registry.root, jobs=[failed]):
                self.registry.upsert(failed)
                raise RuntimeError("failed batch")
        self.assertEqual(before, self.store.list_vacancies())
        self.assertIsNone(self.store.resolve_source(failed.source, failed.source_job_id))
        self.assertEqual([], list(self.registry.jobs_dir.iterdir()))

    def test_batch_resolves_single_active_history_and_blocks_multiple_active(self) -> None:
        first = self._job()
        old = self.registry.upsert(first)
        self.registry._id_factory = lambda: "vacancy-2"
        active = self.registry.upsert(replace(first, source_job_id="active", title="Active Engineer"))
        bridge.archive_vacancy(self.registry.jobs_dir / old.directory, "old.zip")
        identity_id = self.store._source_identity_id(first.source, first.source_job_id)
        with self.store.lease("test:historical-identity"):
            identity = self.store.get("source_identities", identity_id)
            self.store.put("source_identities", identity_id,
                           {**identity, "vacancy_ids": [old.vacancy_id, active.vacancy_id], "ambiguous": True})
        with bridge.vacancy_batch(self.registry.root, jobs=[first]):
            result = self.registry.upsert(first)
        self.assertEqual(active.vacancy_id, result.vacancy_id)
        self.assertTrue(self.store.get("vacancies", old.vacancy_id)["archived"])
        with self.store.lease("test:duplicate-active"):
            old_doc = self.store.get("vacancies", old.vacancy_id)
            self.store.put("vacancies", old.vacancy_id, {**old_doc, "archived": False})
        with self.assertRaises(SourceIdentityConflict):
            with bridge.vacancy_batch(self.registry.root, jobs=[first]):
                self.registry.upsert(first)

    def test_bulk_archive_is_atomic_revision_guarded_and_idempotent(self) -> None:
        self.registry._id_factory = lambda: str(uuid.uuid4())
        jobs = [self._job(), replace(self._job(), source_job_id="second", title="Second Engineer")]
        with bridge.vacancy_batch(self.registry.root, jobs=jobs):
            created = [self.registry.upsert(job) for job in jobs]
        directories = [self.registry.jobs_dir / row.directory for row in created]
        revisions = {row["directory"]: row["revision"] for row in self.store.list_vacancies()}
        with self.assertRaises(StorageConflictError):
            bridge.archive_vacancies(directories + [self.registry.jobs_dir / "missing"], None)
        self.assertEqual(2, len(self.store.list_vacancies()))
        stale = {**revisions, created[-1].directory: 0}
        with self.assertRaises(StorageConflictError):
            bridge.archive_vacancies(directories, None, stale)
        self.assertEqual(2, len(self.store.list_vacancies()))
        self.assertEqual(2, bridge.archive_vacancies(directories, None, revisions))
        self.assertEqual(0, bridge.archive_vacancies(directories, None))
        self.assertEqual([], self.store.list_vacancies())

    def test_triage_batch_reads_once_and_repeat_preserves_revisions(self) -> None:
        created = self.registry.upsert(self._job())
        directory = self.registry.jobs_dir / created.directory
        store = bridge.get_store(self.registry.root)
        with patch.object(store, "list", wraps=store.list) as reads:
            with bridge.vacancy_batch(self.registry.root, directories=[directory]):
                write_triage(directory)
            self.assertEqual(1, reads.call_count)
        prior = self.store.get("vacancies", created.vacancy_id)
        with bridge.vacancy_batch(self.registry.root, directories=[directory]):
            write_triage(directory)
        self.assertEqual(prior, self.store.get("vacancies", created.vacancy_id))

    def test_application_publication_creates_directory_for_database_only_vacancy(self) -> None:
        from jobintel.applications import ApplicationGenerator
        from tests.test_applications import FakeClient, FakeConverter
        created = self.registry.upsert(self._job())
        directory = self.registry.jobs_dir / created.directory
        self.assertFalse(directory.exists())
        prompt = self.temp / "prompt.md"
        prompt.write_text("Prepare a verified application.", encoding="utf-8")
        generator = ApplicationGenerator(
            self.registry.root, [self.temp / "registry" / "candidate" / "match-profile.md"],
            prompt, FakeClient(), FakeConverter(), clock=lambda: self.now,
        )
        result = generator.generate_directory(directory)
        self.assertEqual("prepared", result.status)
        self.assertTrue((directory / "application" / "manifest.yaml").is_file())
        self.assertFalse((directory / "meta.yaml").exists())
        self.assertFalse((directory / "job.md").exists())
        self.assertEqual(1, len(self.store.list("artifact_manifests")))

    def test_archived_source_identity_reuses_same_vacancy_and_status_callback_rolls_back(self) -> None:
        created = self.registry.upsert(self._job())
        directory = self.temp / "registry" / "jobs" / created.directory
        bridge.archive_vacancy(directory, "archive/test.zip")
        with bridge.vacancy_batch(self.registry.root, jobs=[self._job()]):
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
        target.mkdir(parents=True)
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
        # Existing migration artifacts remain files even for MongoDB-only vacancies.
        directory.mkdir(parents=True)
        (directory / "job.md").write_text("Frozen migration evidence", encoding="utf-8")
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
    def test_bulk_archive_rejects_mixed_scopes_and_duplicates_before_access(self) -> None:
        from jobintel.storage_contract import StorageConfigurationError
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            job = root / "registry" / "jobs" / "one"
            rejected = root / "registry" / "rejected" / "two"
            with patch.object(bridge, "get_store") as get_store:
                for paths in ([job, job], [job, rejected]):
                    with self.assertRaises(StorageConfigurationError):
                        bridge.archive_vacancies(paths, None)
                get_store.assert_not_called()
            self.assertEqual(0, bridge.archive_vacancies([job], None))

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
