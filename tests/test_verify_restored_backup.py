from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.verify_restored_backup import (
    VerificationError,
    _compare_snapshots,
    _validate_links_and_history,
    _validate_test_uri,
    _write_receipt,
)


def snapshot() -> dict:
    return {
        "schema_version": 1,
        "collections": {
            "vacancies": {
                "documents": [{
                    "_id": "vac-1",
                    "archived": False,
                    "meta": {
                        "status": "rejected",
                        "status_history": [
                            {"status": "found", "changed_at": "2026-01-01T00:00:00Z"},
                            {"status": "rejected", "changed_at": "2026-01-02T00:00:00Z"},
                        ],
                    },
                }],
                "indexes": [
                    {"v": 2, "key": {"_id": 1}, "name": "_id_"},
                    {"v": 2, "key": {"scope": 1, "directory": 1}, "name": "scope_directory"},
                ],
            },
            "prefilter_rejections": {"documents": [], "indexes": []},
            "applications": {
                "documents": [{
                    "_id": "app-1", "application_id": "app-1", "vacancy_id": "vac-1",
                    "applied_event_id": "event-1",
                }],
                "indexes": [],
            },
            "status_events": {
                "documents": [{
                    "_id": "event-1", "event_id": "event-1", "vacancy_id": "vac-1",
                    "application_id": "app-1", "status": "rejected",
                }],
                "indexes": [],
            },
            "source_identities": {
                "documents": [{"_id": "source-1", "vacancy_ids": ["vac-1"], "prefilter_ids": []}],
                "indexes": [],
            },
            "feedback": {
                "documents": [{"_id": "feedback-1", "vacancy_id": "vac-1"}],
                "indexes": [],
            },
            "artifact_manifests": {
                "documents": [{"_id": "package-1", "vacancy_id": "vac-1"}],
                "indexes": [],
            },
        },
    }


class VerifyRestoredBackupTests(unittest.TestCase):
    def test_test_uri_must_be_loopback_and_distinct_from_production(self) -> None:
        local = "mongodb://127.0.0.1:27018/?replicaSet=rs0&directConnection=true"
        _validate_test_uri(local, "mongodb+srv://example.invalid/db")
        with self.assertRaisesRegex(VerificationError, "loopback"):
            _validate_test_uri("mongodb://mongo.example.test:27017/?replicaSet=rs0")
        with self.assertRaisesRegex(VerificationError, "must differ"):
            _validate_test_uri(local, local)

    def test_snapshot_comparison_preserves_compound_index_key_order(self) -> None:
        expected = snapshot()
        actual = snapshot()
        report = _compare_snapshots(expected, actual)
        self.assertTrue(report["exact_match"])
        self.assertEqual(6, report["documents"])

        actual["collections"]["vacancies"]["indexes"][1]["key"] = {
            "directory": 1,
            "scope": 1,
        }
        with self.assertRaisesRegex(VerificationError, "indexes differ"):
            _compare_snapshots(expected, actual)

    def test_reference_and_status_history_invariants(self) -> None:
        report = _validate_links_and_history(snapshot())
        self.assertEqual(0, report["dangling_references"])
        self.assertEqual(2, report["status_history_entries"])

        broken = snapshot()
        broken["collections"]["status_events"]["documents"][0]["application_id"] = "missing"
        with self.assertRaisesRegex(VerificationError, "dangling application"):
            _validate_links_and_history(broken)

    def test_receipts_are_never_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "receipts" / "receipt.json"
            _write_receipt(path, {"state": "success"})
            self.assertIn('"success"', path.read_text(encoding="utf-8"))
            with self.assertRaises(FileExistsError):
                _write_receipt(path, {"state": "failed"})


if __name__ == "__main__":
    unittest.main()
