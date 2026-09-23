from __future__ import annotations

import os
import threading
import unittest
import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from pymongo import MongoClient

from jobintel.mongodb_storage import MongoStore
from jobintel.storage_contract import (
    SourceIdentityConflict,
    StorageConfigurationError,
    StorageConflictError,
    StorageLeaseError,
    StorageRestoreError,
    WriterLease,
)


class MongoStoreLeaseUnitTests(unittest.TestCase):
    def test_ambiguous_identity_with_one_active_owner_is_resolved(self) -> None:
        client = MagicMock()
        database = MagicMock()
        vacancies = MagicMock()
        client.__getitem__.return_value = database
        database.__getitem__.return_value = vacancies
        vacancies.find.return_value = [{"_id": "active-vacancy"}]
        store = MongoStore("mongodb://example", "jobintel_test", client=client)
        identity = {
            "vacancy_ids": ["archived-vacancy", "active-vacancy"],
            "ambiguous": True,
        }
        active = {"_id": "active-vacancy", "directory": "active", "archived": False}
        store.get = MagicMock(side_effect=[identity, active])

        resolved = store.resolve_source("custom", "historical-duplicate")

        self.assertEqual(active, resolved)
        vacancies.find.assert_called_once()

    def test_transaction_checks_current_lease_outside_snapshot(self) -> None:
        client = MagicMock()
        database = MagicMock()
        client.__getitem__.return_value = database

        session = MagicMock()
        session_manager = MagicMock()
        session_manager.__enter__.return_value = session
        session_manager.__exit__.return_value = False
        client.start_session.return_value = session_manager

        writer_leases = MagicMock()
        fence_guards = MagicMock()
        fence_guards.update_one.return_value = MagicMock(matched_count=1)
        database.__getitem__.side_effect = lambda name: {
            "writer_leases": writer_leases,
            "writer_fence_guards": fence_guards,
        }[name]

        now = datetime.now(timezone.utc)
        lease = WriterLease(
            "test:snapshot",
            "token",
            7,
            now,
            now + timedelta(seconds=30),
        )
        current = {
            "_id": "operational-writer",
            "owner": lease.owner,
            "token": lease.token,
            "fence": lease.fence,
            "expires_at": now + timedelta(seconds=30),
        }

        def find_lease(_query, *, session=None):
            return None if session is not None else current

        writer_leases.find_one.side_effect = find_lease
        store = MongoStore("mongodb://example", "jobintel_test", client=client)
        store._local.lease_state = {
            "lease": lease,
            "depth": 1,
            "stop": threading.Event(),
            "lost": threading.Event(),
            "error": None,
            "last_renewed_at": now,
            "loss_cause": None,
        }

        with store.transaction():
            pass

        session.commit_transaction.assert_called_once_with()
        self.assertEqual(2, fence_guards.update_one.call_count)
        self.assertTrue(
            all(
                call.kwargs.get("session") is None
                for call in writer_leases.find_one.call_args_list
            )
        )


class MongoStoreTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.uri = os.environ.get("JOBINTEL_TEST_MONGODB_URI", "").strip()
        if not cls.uri:
            raise unittest.SkipTest("JOBINTEL_TEST_MONGODB_URI is not configured")
        cls.database_name = "jobintel_test_" + uuid.uuid4().hex
        cls.store = MongoStore(cls.uri, cls.database_name, lease_seconds=2)
        cls.store.ensure_schema()

    @classmethod
    def tearDownClass(cls) -> None:
        cls.store.close()
        client = MongoClient(cls.uri)
        try:
            client.drop_database(cls.database_name)
        finally:
            client.close()

    def tearDown(self) -> None:
        with self.store.lease("test:cleanup", timeout_seconds=5):
            for name in self.store.database.list_collection_names():
                if name not in {"writer_leases", "storage_schema"}:
                    self.store.database[name].delete_many({})

    def test_mutations_require_lease_and_revisions_are_idempotent(self) -> None:
        with self.assertRaises(StorageLeaseError):
            self.store.put("audit_events", "event-1", {"value": 1})

        with self.store.lease("test:put"):
            first = self.store.put("audit_events", "event-1", {"value": 1})
            repeated = self.store.put("audit_events", "event-1", {"value": 1})
            second = self.store.put(
                "audit_events", "event-1", {"value": 2}, expected_revision=1
            )
            idempotent_retry = self.store.put(
                "audit_events", "event-1", {"value": 2}, expected_revision=1
            )
            with self.assertRaises(StorageConflictError):
                self.store.put(
                    "audit_events", "event-1", {"value": 3}, expected_revision=1
                )

        self.assertEqual(1, first["revision"])
        self.assertEqual(first, repeated)
        self.assertEqual(2, second["revision"])
        self.assertEqual(second, idempotent_retry)

    def test_nested_transaction_rolls_back_all_documents(self) -> None:
        with self.store.lease("test:rollback"):
            with self.assertRaisesRegex(RuntimeError, "injected"):
                with self.store.transaction():
                    self.store.put("vacancy_events", "one", {"value": 1})
                    self.store.put("vacancy_events", "two", {"value": 2})
                    raise RuntimeError("injected")

        self.assertEqual([], self.store.list("vacancy_events"))

    def test_insert_batch_adds_storage_envelope_without_mutating_inputs(self) -> None:
        documents = [
            {"_id": "batch-one", "value": {"nested": [1]}},
            {"_id": "batch-two", "value": {"nested": [2]}},
        ]
        original = [
            {"_id": "batch-one", "value": {"nested": [1]}},
            {"_id": "batch-two", "value": {"nested": [2]}},
        ]

        with self.store.lease("test:insert-batch") as lease:
            inserted = self.store.insert_batch("vacancy_events", documents)

        self.assertEqual(original, documents)
        documents[0]["value"]["nested"].append(99)
        rows = self.store.list("vacancy_events", sort=[("_id", 1)])
        self.assertEqual(2, inserted)
        self.assertEqual(original[0]["value"], rows[0]["value"])
        self.assertEqual(original[1]["value"], rows[1]["value"])
        self.assertEqual([1, 1], [row["revision"] for row in rows])
        self.assertEqual(
            [lease.fence, lease.fence], [row["writer_fence"] for row in rows]
        )
        self.assertEqual(rows[0]["updated_at"], rows[1]["updated_at"])

    def test_insert_batch_duplicate_rolls_back_entire_batch(self) -> None:
        with self.store.lease("test:insert-batch-rollback"):
            existing = self.store.put("vacancy_events", "existing", {"value": 1})
            with self.assertRaises(StorageConflictError):
                self.store.insert_batch(
                    "vacancy_events",
                    [
                        {"_id": "would-have-been-inserted", "value": 2},
                        {"_id": "existing", "value": 3},
                    ],
                )

        self.assertIsNone(
            self.store.get("vacancy_events", "would-have-been-inserted")
        )
        self.assertEqual(existing, self.store.get("vacancy_events", "existing"))

    def test_insert_batch_rejects_missing_id_and_storage_envelope(self) -> None:
        with self.assertRaisesRegex(StorageConfigurationError, "requires an _id"):
            self.store.insert_batch("vacancy_events", [{"value": 1}])
        with self.assertRaisesRegex(
            StorageConfigurationError, "contains storage envelope fields"
        ):
            self.store.insert_batch(
                "vacancy_events", [{"_id": "invalid", "revision": 8}]
            )

        self.assertEqual([], self.store.list("vacancy_events"))

    def test_bulk_vacancy_conflict_rolls_back_prior_identity_writes(self) -> None:
        with self.store.lease("test:bulk-conflict"):
            with self.assertRaises(StorageConflictError):
                with self.store.vacancy_batch(source_keys=[("adzuna", "one"), ("adzuna", "two")]):
                    self.store.save_vacancy("same-directory", self._meta("one", "one", "first"), "first", None)
                    self.store.save_vacancy("same-directory", self._meta("two", "two", "second"), "second", None)
        self.assertEqual([], self.store.list("vacancies"))
        self.assertEqual([], self.store.list("source_identities"))

    def test_bulk_vacancy_commit_checks_lease_after_buffered_mutations(self) -> None:
        with self.assertRaises(StorageLeaseError):
            with self.store.lease("test:bulk-fenced"):
                with self.store.vacancy_batch(source_keys=[("adzuna", "one")]):
                    self.store.save_vacancy("one", self._meta("one", "one", "first"), "first", None)
                    self.store.database["writer_leases"].update_one(
                        {"_id": "operational-writer"},
                        {"$set": {"expires_at": datetime.now(timezone.utc) - timedelta(seconds=10)}},
                    )
        self.assertEqual([], self.store.list("vacancies"))
        self.assertEqual([], self.store.list("source_identities"))

    def test_source_identity_is_unique_and_fingerprint_is_not(self) -> None:
        first = self._meta("vacancy-1", "source-1", "same-fingerprint")
        second = self._meta("vacancy-2", "source-2", "same-fingerprint")
        conflict = self._meta("vacancy-3", "source-1", "different")

        with self.store.lease("test:vacancies"):
            self.store.save_vacancy("one", first, "job one", None)
            self.store.save_vacancy("two", second, "job two", None)
            with self.assertRaises(SourceIdentityConflict):
                self.store.save_vacancy("three", conflict, "job three", None)

        rows = self.store.list_vacancies()
        self.assertEqual(["one", "two"], [row["directory"] for row in rows])
        self.assertTrue(
            any(
                index["name"] == "fingerprint_nonunique" and not index.get("unique", False)
                for index in self.store.database["vacancies"].list_indexes()
            )
        )

    def test_prefilter_identity_does_not_block_later_active_vacancy(self) -> None:
        rejected = {
            "schema_version": 1,
            "source": "adzuna",
            "source_job_id": "shared-source",
            "source_url": "https://example.test/shared-source",
            "title": "Backend Engineer",
            "company": "Example",
            "rejection_category": "location",
            "rejection_reason": "outside target geography",
        }
        active = self._meta("vacancy-active", "shared-source", "same-fingerprint")

        with self.store.lease("test:prefilter-promotion"):
            prefilter = self.store.save_vacancy(
                "rejected-one", rejected, "rejected", None, scope="rejected"
            )
            repeated = self.store.save_vacancy(
                "rejected-one",
                rejected,
                "rejected",
                None,
                scope="rejected",
                expected_revision=prefilter["revision"],
            )
            self.store.save_vacancy("active-one", active, "active", None)

        identity = self.store.list("source_identities")[0]
        self.assertNotIn("id", prefilter["meta"])
        self.assertEqual(prefilter["revision"], repeated["revision"])
        self.assertEqual([prefilter["_id"]], identity["prefilter_ids"])
        self.assertEqual(["vacancy-active"], identity["vacancy_ids"])
        self.assertFalse(identity["ambiguous"])
        self.assertIsNone(self.store.get("vacancies", prefilter["_id"]))
        self.assertEqual(
            prefilter,
            self.store.get("prefilter_rejections", prefilter["_id"]),
        )

    def test_imported_prefilter_is_a_noop_on_repeated_runtime_save(self) -> None:
        meta = {
            "schema_version": 1,
            "source": "adzuna",
            "source_job_id": "imported-prefilter",
            "source_url": "https://example.test/imported-prefilter",
            "title": "Backend Engineer",
            "company": "Example",
            "rejection_category": "location",
            "rejection_reason": "outside target geography",
        }
        reference = {
            "source": "adzuna",
            "source_job_id": "imported-prefilter",
            "url": "https://example.test/imported-prefilter",
        }
        vacancy_id = MongoStore._rejected_vacancy_id(
            [("adzuna", "imported-prefilter", reference)], "imported-prefilter"
        )
        identity_id = MongoStore._source_identity_id(
            "adzuna", "imported-prefilter"
        )
        imported = {
            "directory": "imported-prefilter",
            "scope": "rejected",
            "archived": False,
            "meta": meta,
            "job_text": "rejected",
            "company_text": None,
            "match": None,
            "triage": None,
            "evidence": [{"archive": "rejected.zip"}],
            "observation_count": 4,
        }
        with self.store.lease("test:imported-prefilter"):
            self.store.put(
                "source_identities",
                identity_id,
                {
                    "source": "adzuna",
                    "source_job_id": "imported-prefilter",
                    "vacancy_ids": [],
                    "prefilter_ids": [vacancy_id],
                    "ambiguous": False,
                    "reference": reference,
                },
            )
            stored = self.store.put(
                "prefilter_rejections", vacancy_id, imported
            )
            repeated = self.store.save_vacancy(
                "imported-prefilter",
                meta,
                "rejected",
                None,
                scope="rejected",
                expected_revision=stored["revision"],
            )

        self.assertEqual(stored, repeated)
        self.assertEqual(4, repeated["observation_count"])
        self.assertEqual(imported["evidence"], repeated["evidence"])
        self.assertEqual(
            ["imported-prefilter"],
            [row["directory"] for row in self.store.list_vacancies(scope="rejected")],
        )

    def test_historical_ambiguous_identity_blocks_runtime_resolution(self) -> None:
        source_id = MongoStore._source_identity_id("adzuna", "ambiguous")
        with self.store.lease("test:ambiguous"):
            self.store.put(
                "source_identities",
                source_id,
                {
                    "source": "adzuna",
                    "source_job_id": "ambiguous",
                    "vacancy_ids": ["old-one", "old-two"],
                    "prefilter_ids": [],
                    "ambiguous": True,
                    "reference": {
                        "source": "adzuna",
                        "source_job_id": "ambiguous",
                    },
                },
            )
            with self.assertRaises(SourceIdentityConflict):
                self.store.save_vacancy(
                    "incoming",
                    self._meta("incoming", "ambiguous", "fingerprint"),
                    "job",
                    None,
                )
        with self.assertRaises(SourceIdentityConflict):
            self.store.resolve_source("adzuna", "ambiguous")

    def test_historical_ambiguous_identity_resolves_single_active_owner(self) -> None:
        source_id = MongoStore._source_identity_id("custom", "historical-duplicate")
        archived = self._meta("old-vacancy", "old-source", "same-fingerprint")
        active = self._meta("active-vacancy", "active-source", "same-fingerprint")
        active["sources"] = [
            {
                "source": "custom",
                "source_job_id": "historical-duplicate",
                "url": "https://example.test/active",
            }
        ]
        with self.store.lease("test:historical-duplicate"):
            old = self.store.save_vacancy("old", archived, "old", None)
            current = self.store.save_vacancy("active", active, "active", None)
            old_payload = {
                key: value
                for key, value in old.items()
                if key not in {"_id", "revision", "writer_fence", "updated_at"}
            }
            old_payload["archived"] = True
            self.store.put(
                "vacancies", old["_id"], old_payload, expected_revision=old["revision"]
            )
            self.store.put(
                "source_identities",
                source_id,
                {
                    "source": "custom",
                    "source_job_id": "historical-duplicate",
                    "vacancy_ids": [old["_id"], current["_id"]],
                    "prefilter_ids": [],
                    "ambiguous": True,
                    "reference": None,
                },
            )

            resolved = self.store.resolve_source("custom", "historical-duplicate")
            updated = self.store.save_vacancy(
                "active",
                active,
                "active",
                None,
                expected_revision=current["revision"],
            )

        self.assertEqual("active-vacancy", resolved["_id"])
        self.assertEqual("active-vacancy", updated["_id"])

    def test_resolve_source_returns_archived_vacancy_and_ignores_prefilter_only(self) -> None:
        rejected = {
            "schema_version": 1,
            "source": "adzuna",
            "source_job_id": "rejected-only",
            "source_url": "https://example.test/rejected-only",
            "title": "Backend Engineer",
            "company": "Example",
            "rejection_category": "location",
            "rejection_reason": "outside target geography",
        }
        active = self._meta("active-archived", "active-source", "active")
        with self.store.lease("test:resolve-source"):
            self.store.save_vacancy(
                "rejected-only", rejected, "rejected", None, scope="rejected"
            )
            saved = self.store.save_vacancy("active", active, "active", None)
            payload = {
                key: value
                for key, value in saved.items()
                if key not in {"_id", "revision", "writer_fence", "updated_at"}
            }
            payload["archived"] = True
            payload["archive_path"] = "archives/jobs.zip"
            self.store.put(
                "vacancies", saved["_id"], payload, expected_revision=saved["revision"]
            )
            archived = self.store.get("vacancies", saved["_id"])
            self.store.save_vacancy(
                "active",
                active,
                "active updated",
                None,
                expected_revision=archived["revision"],
            )

        self.assertIsNone(self.store.resolve_source("adzuna", "rejected-only"))
        resolved = self.store.resolve_source("adzuna", "active-source")
        self.assertIsNotNone(resolved)
        self.assertTrue(resolved["archived"])
        self.assertEqual("archives/jobs.zip", resolved["archive_path"])

    def test_runtime_save_preserves_migration_provenance_and_artifact_fields(self) -> None:
        original_meta = self._meta("preserved", "preserved-source", "fingerprint")
        original_meta["migration_provenance"] = {
            "source_path": "archives/jobs.zip",
            "source_sha256": "abc123",
        }
        with self.store.lease("test:preserve-migration-fields"):
            saved = self.store.save_vacancy(
                "preserved", original_meta, "original", None
            )
            payload = {
                key: value
                for key, value in saved.items()
                if key not in {"_id", "revision", "writer_fence", "updated_at"}
            }
            payload.update(
                {
                    "archive_path": "archives/jobs.zip",
                    "provenance": {"import_run_id": "run-1"},
                    "evidence": [{"path": "feedback/rejection.md", "sha256": "def456"}],
                    "history": [{"status": "applied", "effective_at": None}],
                    "artifact_refs": ["artifact-1"],
                }
            )
            enriched = self.store.put(
                "vacancies",
                saved["_id"],
                payload,
                expected_revision=saved["revision"],
            )
            runtime_meta = self._meta(
                "preserved", "preserved-source", "fingerprint"
            )
            runtime_meta["title"] = "Updated Backend Engineer"
            updated = self.store.save_vacancy(
                "preserved",
                runtime_meta,
                "updated",
                None,
                expected_revision=enriched["revision"],
            )

        self.assertEqual("archives/jobs.zip", updated["archive_path"])
        self.assertEqual({"import_run_id": "run-1"}, updated["provenance"])
        self.assertEqual(payload["evidence"], updated["evidence"])
        self.assertEqual(payload["history"], updated["history"])
        self.assertEqual(["artifact-1"], updated["artifact_refs"])
        self.assertEqual(
            original_meta["migration_provenance"],
            updated["meta"]["migration_provenance"],
        )

    def test_only_one_thread_holds_writer_lease(self) -> None:
        contender = MongoStore(self.uri, self.database_name, lease_seconds=2)
        errors: list[Exception] = []

        def attempt() -> None:
            try:
                with contender.lease("test:contender", timeout_seconds=0):
                    pass
            except Exception as exc:
                errors.append(exc)

        try:
            with self.store.lease("test:holder") as first:
                thread = threading.Thread(target=attempt)
                thread.start()
                thread.join(timeout=5)
                with self.store.lease("test:nested") as nested:
                    self.assertEqual(first.token, nested.token)
            self.assertEqual(1, len(errors))
            self.assertIsInstance(errors[0], StorageLeaseError)
        finally:
            contender.close()

    def test_fenced_writer_cannot_start_a_transaction(self) -> None:
        with self.assertRaises(StorageLeaseError):
            with self.store.lease("test:stale-writer") as lease:
                self.store.database["writer_fence_guards"].update_one(
                    {"_id": "operational-writer", "fence": lease.fence},
                    {"$inc": {"fence": 1}},
                )
                self.store.put("audit_events", "stale", {"value": 1})

        self.assertIsNone(self.store.get("audit_events", "stale"))

    def test_snapshot_contains_documents_and_indexes(self) -> None:
        with self.store.lease("test:snapshot"):
            self.store.put("applications", "application-1", {"vacancy_id": "vacancy-1"})
            snapshot = self.store.snapshot()

        self.assertIn("applications", snapshot["collections"])
        self.assertEqual(
            "application-1",
            snapshot["collections"]["applications"]["documents"][0]["_id"],
        )
        self.assertTrue(snapshot["collections"]["applications"]["indexes"])

    def test_snapshot_restores_exact_documents_and_indexes_to_isolated_database(self) -> None:
        with self.store.lease("test:backup-source"):
            source = self.store.put(
                "applications", "application-restore", {"vacancy_id": "vacancy-1"}
            )
            self.store.database["applications"].create_index(
                [("vacancy_id", 1)], name="vacancy_restore_index"
            )
            snapshot = self.store.snapshot()

        target_name = "jobintel_restore_" + uuid.uuid4().hex
        target = MongoStore(self.uri, target_name, lease_seconds=2)
        try:
            with target.lease("test:restore", timeout_seconds=5):
                report = target.restore_snapshot(snapshot)
                with self.assertRaises(StorageRestoreError):
                    target.restore_snapshot(snapshot)

            restored = target.get("applications", "application-restore")
            self.assertEqual(source, restored)
            self.assertGreaterEqual(report["documents"], 1)
            index = target.database["applications"].index_information()[
                "vacancy_restore_index"
            ]
            self.assertEqual([("vacancy_id", 1)], index["key"])
        finally:
            target.close()
            client = MongoClient(self.uri)
            try:
                client.drop_database(target_name)
            finally:
                client.close()

    def test_incompatible_existing_schema_is_rejected_before_overwrite(self) -> None:
        target_name = "jobintel_test_" + uuid.uuid4().hex
        client = MongoClient(self.uri)
        client[target_name]["storage_schema"].insert_one(
            {"_id": "operational", "schema_version": 99}
        )
        target = MongoStore(self.uri, target_name, lease_seconds=2)
        try:
            with self.assertRaises(StorageConfigurationError):
                target.ensure_schema()
            self.assertEqual(
                99,
                client[target_name]["storage_schema"].find_one(
                    {"_id": "operational"}
                )["schema_version"],
            )
        finally:
            target.close()
            client.drop_database(target_name)
            client.close()

    @staticmethod
    def _meta(vacancy_id: str, source_job_id: str, fingerprint: str) -> dict[str, object]:
        return {
            "id": vacancy_id,
            "title": "Backend Engineer",
            "company": "Example",
            "fingerprint": fingerprint,
            "status": "found",
            "sources": [
                {
                    "source": "adzuna",
                    "source_job_id": source_job_id,
                    "url": f"https://example.test/{source_job_id}",
                }
            ],
        }


if __name__ == "__main__":
    unittest.main()
