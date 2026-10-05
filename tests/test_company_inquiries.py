from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import date
from pathlib import Path
from unittest.mock import patch

from jobintel.application_lifecycle import ApplicationLifecycle
from jobintel.lifecycle_cli import main
from jobintel.migration import export_applications
from jobintel.sheets_sync import _application, build_sync_plan, SheetsSyncError
from tests.test_application_lifecycle import MemoryStore
from tests.test_sheets_sync import observed


class CompanyInquiryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.message = self.root / "message.txt"
        self.message.write_bytes(b"Buongiorno,\r\n\r\nAvete opportunita backend?\r\n")
        self.store = MemoryStore()
        self.lifecycle = ApplicationLifecycle(self.root, store=self.store, today=date(2026, 10, 5))
        self.options = dict(company_key="laser-romae", company="Laser Romae", inquiry_id="2026-10-05",
                            sent_on="2026-10-05", recipient="info@laserromae.it", subject="Backend opportunities",
                            message_file=self.message, confirmed=True)

    def test_inquiry_records_exact_message_once_without_vacancy_or_submission(self):
        result = self.lifecycle.record_company_inquiry(**self.options)
        self.assertEqual(self.lifecycle.record_company_inquiry(**self.options), result)
        self.assertEqual((self.root / result["snapshot"] / "message.txt").read_bytes(), self.message.read_bytes())
        self.assertIsNone(result["vacancy_id"])
        self.assertEqual("not_provided", result["attachments_status"])
        self.assertEqual(len(self.store.list("operational_logs")), 1)
        self.assertTrue(self.lifecycle.verify_company_inquiry(company_key="laser-romae", inquiry_id="2026-10-05")["verified"])
        report = self.lifecycle.report(as_of="2026-10-05")
        self.assertEqual(report["summary"]["submitted"], 0)
        self.assertEqual(report["company_inquiries"], [result])
        self.assertEqual(self.store.vacancies[0]["meta"]["status"], "analyzed")

    def test_conflicting_retry_preserves_original_record_and_message(self):
        result = self.lifecycle.record_company_inquiry(**self.options)
        original = self.message.read_bytes()
        self.message.write_bytes(b"Different letter")
        with self.assertRaisesRegex(ValueError, "different content"):
            self.lifecycle.record_company_inquiry(**self.options)
        self.assertEqual((self.root / result["snapshot"] / "message.txt").read_bytes(), original)

    def test_tampered_snapshot_is_rejected_and_excluded_from_export(self):
        result = self.lifecycle.record_company_inquiry(**self.options)
        (self.root / result["snapshot"] / "message.txt").write_bytes(b"Changed")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            self.lifecycle.verify_company_inquiry(company_key="laser-romae", inquiry_id="2026-10-05")
        exported = export_applications(self.store, package_root=self.root)
        self.assertEqual(exported["applications"], [])
        self.assertEqual(exported["coverage"]["confirmed_without_package"], 1)

    def test_confirmed_inquiry_exports_to_sheets_without_fake_vacancy(self):
        result = self.lifecycle.record_company_inquiry(**self.options)
        exported = export_applications(self.store, package_root=self.root)
        row = exported["applications"][0]
        self.assertEqual(row["application_id"], result["application_id"])
        self.assertEqual(_application(row)["vacancy_id"], "")
        self.assertEqual(row["status"], "contacted")
        self.assertEqual(exported["events"], [])
        plan = build_sync_plan(exported, observed([]), synced_at="2026-10-05T15:00:00Z")
        self.assertEqual(plan["summary"]["inserts"], 1)
        self.assertEqual(self.lifecycle.report(as_of="2026-10-04")["company_inquiries"], [])
        with self.assertRaises(SheetsSyncError):
            _application({**row, "entry_type": "vacancy"})
        with self.assertRaises(SheetsSyncError):
            _application({**row, "vacancy_id": "v1"})

    def test_invalid_or_unconfirmed_input_never_writes(self):
        for change in ({"confirmed": False}, {"sent_on": "2026-10-06"}, {"company_key": "../escape"},
                       {"recipient": "invalid"}, {"company": ""}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                self.lifecycle.record_company_inquiry(**{**self.options, **change})
        self.assertEqual(self.store.list("operational_logs"), [])

    def test_cli_routes_company_inquiry(self):
        with patch("jobintel.lifecycle_cli.ApplicationLifecycle") as factory, redirect_stdout(io.StringIO()):
            factory.return_value.record_company_inquiry.return_value = {"ok": True}
            self.assertEqual(main(["record-company-inquiry", "--company-key", "laser-romae",
                "--company", "Laser Romae", "--inquiry-id", "2026-10-05", "--sent-on", "2026-10-05",
                "--recipient", "info@laserromae.it", "--subject", "Backend opportunities",
                "--message-file", "sent.txt", "--confirm-sent"]), 0)
            self.assertTrue(factory.return_value.record_company_inquiry.call_args.kwargs["confirmed"])
