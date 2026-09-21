from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from jobintel.atlas_network import AtlasNetworkError, grant, revoke


PROJECT_ID = "0123456789abcdef01234567"
RUNNER_IP = "8.8.8.8"
CIDR = RUNNER_IP + "/32"
NOW = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)


class FakeAtlasAccess:
    def __init__(self) -> None:
        self.project_id = PROJECT_ID
        self.entries: dict[str, dict] = {}
        self.post_behaviors: list[str] = []
        self.delete_behaviors: list[str] = []
        self.calls: list[tuple[str, str | None, object]] = []
        self.receipt_to_check: Path | None = None

    def request(self, method="GET", entry=None, payload=None):
        self.calls.append((method, entry, payload))
        if method == "GET":
            if entry not in self.entries:
                raise AtlasNetworkError("not found", status_code=404)
            return dict(self.entries[entry])
        if method == "POST":
            if self.receipt_to_check is not None:
                assert self.receipt_to_check.is_file()
            behavior = self.post_behaviors.pop(0) if self.post_behaviors else "ok"
            row = dict(payload[0])
            cidr = row.pop("cidrBlock")
            if behavior in {"ok", "create_then_error"}:
                self.entries[cidr] = row
            if behavior in {"error", "create_then_error"}:
                raise AtlasNetworkError("ambiguous network failure")
            return {}
        if method == "DELETE":
            behavior = self.delete_behaviors.pop(0) if self.delete_behaviors else "ok"
            if behavior == "404":
                raise AtlasNetworkError("not found", status_code=404)
            if behavior in {"ok", "delete_then_error"}:
                self.entries.pop(entry, None)
            if behavior in {"error", "delete_then_error"}:
                raise AtlasNetworkError("ambiguous network failure")
            return {}
        raise AssertionError(f"unexpected method {method}")


class AtlasNetworkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.receipt = Path(self.temporary.name) / "atlas-network.json"
        self.access = FakeAtlasAccess()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_receipt_is_durable_before_post_and_ambiguous_success_is_reconciled(self) -> None:
        self.access.receipt_to_check = self.receipt
        self.access.post_behaviors = ["create_then_error"]

        receipt = grant(self.access, RUNNER_IP, self.receipt, now=NOW)

        self.assertTrue(receipt["created"])
        self.assertEqual(receipt, json.loads(self.receipt.read_text(encoding="utf-8")))
        self.assertEqual(receipt["comment"], self.access.entries[CIDR]["comment"])
        self.assertEqual(1, self._count_calls("POST"))

    def test_existing_owned_receipt_retries_after_not_found(self) -> None:
        receipt = self._owned_receipt()
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")

        result = grant(
            self.access,
            RUNNER_IP,
            self.receipt,
            now=NOW + timedelta(minutes=10),
        )

        self.assertEqual(receipt, result)
        self.assertEqual(receipt["comment"], self.access.entries[CIDR]["comment"])
        self.assertEqual(1, self._count_calls("POST"))

    def test_uncertain_create_without_entry_is_retried_and_verified(self) -> None:
        self.access.post_behaviors = ["error", "ok"]

        grant(self.access, RUNNER_IP, self.receipt, now=NOW)

        self.assertEqual(2, self._count_calls("POST"))
        self.assertIn(CIDR, self.access.entries)

    def test_preexisting_entry_is_never_modified_or_deleted(self) -> None:
        self.access.entries[CIDR] = {
            "comment": "managed-by-a-human",
            "deleteAfterDate": "2026-12-01T00:00:00Z",
        }

        receipt = grant(self.access, RUNNER_IP, self.receipt, now=NOW)
        revoke(self.access, self.receipt)

        self.assertFalse(receipt["created"])
        self.assertIsNone(receipt["comment"])
        self.assertEqual("managed-by-a-human", receipt["observed_comment"])
        self.assertEqual(0, self._count_calls("POST"))
        self.assertEqual(0, self._count_calls("DELETE"))
        self.assertIn(CIDR, self.access.entries)

    def test_wrong_owner_is_not_overwritten_or_revoked(self) -> None:
        receipt = self._owned_receipt()
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        self.access.entries[CIDR] = {"comment": "someone-else"}

        with self.assertRaisesRegex(AtlasNetworkError, "ownership changed"):
            grant(self.access, RUNNER_IP, self.receipt, now=NOW)
        with self.assertRaisesRegex(AtlasNetworkError, "another owner's entry"):
            revoke(self.access, self.receipt)

        self.assertEqual(0, self._count_calls("POST"))
        self.assertEqual(0, self._count_calls("DELETE"))

    def test_revoke_ignores_not_found_before_and_during_delete(self) -> None:
        receipt = self._owned_receipt()
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        revoke(self.access, self.receipt)

        self.access.entries[CIDR] = {"comment": receipt["comment"]}
        self.access.delete_behaviors = ["404"]
        revoke(self.access, self.receipt)

        self.assertEqual(1, self._count_calls("DELETE"))

    def test_revoke_reconciles_ambiguous_success_and_retries_ambiguous_failure(self) -> None:
        receipt = self._owned_receipt()
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        self.access.entries[CIDR] = {"comment": receipt["comment"]}
        self.access.delete_behaviors = ["delete_then_error"]

        revoke(self.access, self.receipt)

        self.assertNotIn(CIDR, self.access.entries)
        self.assertEqual(1, self._count_calls("DELETE"))

        self.access.entries[CIDR] = {"comment": receipt["comment"]}
        self.access.delete_behaviors = ["error", "ok"]
        revoke(self.access, self.receipt)
        self.assertEqual(3, self._count_calls("DELETE"))

    def test_legacy_owned_receipt_without_created_at_can_still_be_cleaned_up(self) -> None:
        receipt = self._owned_receipt()
        receipt.pop("created_at")
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        self.access.entries[CIDR] = {"comment": receipt["comment"]}

        revoke(self.access, self.receipt)

        self.assertNotIn(CIDR, self.access.entries)

    def test_unsafe_address_and_receipt_cidr_are_refused(self) -> None:
        for value in ("10.0.0.1", "8.8.8.0/24", "::1", "invalid"):
            with self.subTest(value=value):
                with self.assertRaises(AtlasNetworkError):
                    grant(self.access, value, self.receipt, now=NOW)

        receipt = self._owned_receipt()
        receipt["cidr"] = "0.0.0.0/0"
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")
        with self.assertRaisesRegex(AtlasNetworkError, "unsafe CIDR"):
            revoke(self.access, self.receipt)

    def test_receipt_expiry_cannot_exceed_two_hours(self) -> None:
        receipt = self._owned_receipt()
        receipt["expires_at"] = "2026-09-21T14:00:01Z"
        self.receipt.write_text(json.dumps(receipt), encoding="utf-8")

        with self.assertRaisesRegex(AtlasNetworkError, "two-hour limit"):
            grant(self.access, RUNNER_IP, self.receipt, now=NOW)

    @staticmethod
    def _owned_receipt() -> dict:
        return {
            "schema_version": 1,
            "project_id": PROJECT_ID,
            "cidr": CIDR,
            "created": True,
            "comment": "job-intelligence:" + "a" * 32,
            "created_at": "2026-09-21T12:00:00Z",
            "expires_at": "2026-09-21T14:00:00Z",
        }

    def _count_calls(self, method: str) -> int:
        return sum(call[0] == method for call in self.access.calls)


if __name__ == "__main__":
    unittest.main()
