from __future__ import annotations

import asyncio
from contextlib import nullcontext
import json
import os
import subprocess
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import yaml

from jobintel.accounts import AccountConfigurationError, load_account_context
from jobintel.catalog_data import load_catalog_vacancies
from scripts import archive_jobs, deliver_telegram_outbox, notify_telegram, verify_restored_backup


ROOT = Path(__file__).resolve().parents[1]


def seed_account(root: Path):
    (root / "config").mkdir(parents=True)
    (root / "config/accounts.yaml").write_bytes((ROOT / "config/accounts.yaml").read_bytes())
    return load_account_context(root)


def document():
    return {
        "directory": "synthetic-vacancy",
        "meta": {"id": "synthetic-id", "company": "Example", "title": "Engineer", "sources": [],
                 "discovered_at": "2026-10-20T00:00:00Z", "status": "found",
                 "status_history": [{"status": "found", "changed_at": "2026-10-20T00:00:00Z"}]},
        "match": None, "job_text": "Synthetic vacancy",
    }


class AccountScriptTests(unittest.TestCase):
    def test_direct_processes_use_their_own_checkout_and_reject_before_payload_parsing(self):
        environment = dict(os.environ)
        environment.pop("JOBINTEL_ACCOUNT", None)
        cases = (
            (environment, "requested account is not enabled"),
            (dict(environment, JOBINTEL_ACCOUNT="current"),
             "command-line and environment account selectors disagree"),
        )
        for child_environment, expected_error in cases:
            for script in ("archive_jobs.py", "notify_telegram.py", "deliver_telegram_outbox.py", "verify_restored_backup.py"):
                with self.subTest(script=script, account=child_environment.get("JOBINTEL_ACCOUNT")):
                    result = subprocess.run(
                        [sys.executable, str(ROOT / "scripts" / script), "--account=unknown"],
                        cwd=ROOT.parent, env=child_environment, capture_output=True, text=True, timeout=20,
                    )
                    self.assertEqual(2, result.returncode, result.stderr)
                    self.assertIn(expected_error, result.stderr)
                    self.assertNotIn("ModuleNotFoundError", result.stderr)

    def test_notification_credentials_follow_context_without_process_environment_leaks(self):
        with TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            contexts = [seed_account(root / name) for name in ("first", "second")]
            for number, context in enumerate(contexts):
                context.path("sources").mkdir()
                context.path("environment").write_text(f"TELEGRAM_BOT_TOKEN=token-{number}\nTELEGRAM_CHAT_ID=chat-{number}\n", encoding="utf-8")
            self.assertEqual(("token-0", "chat-0"), notify_telegram.notification_config(context=contexts[0]))
            self.assertEqual(("token-1", "chat-1"), notify_telegram.notification_config(context=contexts[1]))
            self.assertEqual(("token-0", "chat-0"), notify_telegram.notification_config(context=contexts[0]))
            self.assertEqual({}, dict(os.environ))

    def test_operational_actions_select_current_and_validate_before_probes(self):
        names = ["job-intelligence-collection.yml", "job-intelligence-archive-low-score.yml",
                 "job-intelligence-archive-skipped.yml", "job-intelligence-archive-stale.yml",
                 "job-intelligence-archive-rejected.yml", "job-intelligence-telegram.yml",
                 "atlas-connectivity.yml"]
        for name in names:
            with self.subTest(workflow=name):
                workflow = yaml.safe_load((ROOT / ".github/workflows" / name).read_text(encoding="utf-8"))
                for job in workflow["jobs"].values():
                    self.assertEqual("current", job["env"]["JOBINTEL_ACCOUNT"])
                    steps = job["steps"]
                    gates = [index for index, step in enumerate(steps)
                             if step.get("run") == "python -m jobintel.accounts --account current"]
                    self.assertEqual(1, len(gates))
                    operational = [index for index, step in enumerate(steps)
                                   if any(marker in step.get("run", "") for marker in
                                          ("config/data-services.yaml", "jobintel.atlas_network grant", "deliver_telegram_outbox.py"))]
                    self.assertTrue(operational)
                    self.assertLess(gates[0], min(operational))
                    for step in steps:
                        if "jobintel.atlas_network revoke" in step.get("run", ""):
                            self.assertIn("always()", step["if"])

    def test_unknown_or_conflicting_account_stops_all_direct_scripts_before_payload_or_side_effects(self):
        for environment in ({}, {"JOBINTEL_ACCOUNT": "current"}):
            with self.subTest(environment=environment), TemporaryDirectory() as temporary, patch.dict(os.environ, environment, clear=True):
                root = Path(temporary)
                common = ["--project-root", str(root), "--account=unknown"]
                with patch.object(archive_jobs, "archive") as archive, patch.object(archive_jobs, "workflow_lock") as lock:
                    with self.assertRaises(SystemExit) as failure:
                        archive_jobs.main(["low-score", *common])
                    self.assertEqual(2, failure.exception.code)
                    archive.assert_not_called()
                    lock.assert_not_called()
                with patch.object(notify_telegram, "enrich_vacancy_urls") as enrich, patch.object(notify_telegram, "notification_config") as credentials:
                    self.assertEqual(2, asyncio.run(notify_telegram._main(["--message-file", str(root / "missing"), *common])))
                    enrich.assert_not_called()
                    credentials.assert_not_called()
                delivery = ["--outbox-file", str(root / "missing"), "--sent-dir", str(root / "sent"), "--receipt-dir", str(root / "receipts"), *common]
                with patch.object(deliver_telegram_outbox, "load_notification") as payload, patch.object(deliver_telegram_outbox, "notification_config") as credentials:
                    self.assertEqual(2, asyncio.run(deliver_telegram_outbox._main(delivery)))
                    payload.assert_not_called()
                    credentials.assert_not_called()
                restore = ["--input", str(root / "missing"), "--database", "jobintel_restore_test", "--artifact-output", str(root / "restore"), "--output", str(root / "receipt.json"), *common]
                with patch.object(verify_restored_backup, "verify_restored_backup") as verify:
                    self.assertEqual(2, verify_restored_backup.main(restore))
                    verify.assert_not_called()
                    self.assertFalse((root / "receipt.json").exists())

    def test_archive_default_and_explicit_current_have_same_root_and_parameters(self):
        with TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            seed_account(root)
            calls = []
            for selector in ([], ["--account", "current"], ["--account=current"]):
                with patch.object(archive_jobs, "workflow_lock", return_value=nullcontext()), patch.object(archive_jobs, "archive", return_value=0) as archive:
                    self.assertEqual(0, archive_jobs.main(["low-score", "--project-root", str(root), *selector]))
                    calls.append(archive.call_args)
            self.assertEqual(calls[0], calls[1])
            self.assertEqual(calls[1], calls[2])
            self.assertEqual(root.resolve(), calls[0].args[0])

    def test_delivery_rejects_foreign_state_before_reading_or_sending(self):
        with TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            seed_account(root)
            base = root / "notifications/telegram"
            arguments = ["--project-root", str(root), "--outbox-file", str(base / "outbox/item.json"), "--sent-dir", str(base / "sent"), "--receipt-dir", str(root / "foreign")]
            with patch.object(deliver_telegram_outbox, "load_notification") as payload, patch.object(deliver_telegram_outbox, "send_message_once") as send:
                self.assertEqual(2, asyncio.run(deliver_telegram_outbox._main(arguments)))
                payload.assert_not_called()
                send.assert_not_called()
                self.assertFalse((root / "foreign").exists())

    def test_delivery_keeps_duplicate_state_in_selected_account(self):
        with TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            seed_account(root)
            base = root / "notifications/telegram"
            outbox = base / "outbox/item.json"
            outbox.parent.mkdir(parents=True)
            outbox.write_text("synthetic", encoding="utf-8")
            arguments = ["--project-root", str(root), "--account=current", "--outbox-file", str(outbox), "--sent-dir", str(base / "sent"), "--receipt-dir", str(base / "receipts")]
            notification = {"notification_id": "synthetic", "initiator": "test", "items": []}
            with patch.object(deliver_telegram_outbox, "load_notification", return_value=notification), patch.object(deliver_telegram_outbox, "undelivered_items", return_value=[]), patch.object(deliver_telegram_outbox, "notification_config") as credentials, patch.object(deliver_telegram_outbox, "send_message_once") as send:
                self.assertEqual(0, asyncio.run(deliver_telegram_outbox._main(arguments)))
                credentials.assert_not_called()
                send.assert_not_called()
            self.assertFalse(outbox.exists())
            receipt = json.loads((base / "sent/item.json").read_text(encoding="utf-8"))
            self.assertEqual("duplicate_skipped", receipt["delivery_status"])
            self.assertEqual([], receipt["delivered_vacancy_ids"])

    def test_delivery_passes_selected_root_to_credentials_and_transport(self):
        with TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            context = seed_account(root)
            base = root / "notifications/telegram"
            outbox = base / "outbox/item.json"
            outbox.parent.mkdir(parents=True)
            outbox.write_text("synthetic", encoding="utf-8")
            arguments = ["--project-root", str(root), "--outbox-file", str(outbox), "--sent-dir", str(base / "sent"), "--receipt-dir", str(base / "receipts")]
            item = {"vacancy_id": "synthetic-id"}
            notification = {"notification_id": "synthetic", "initiator": "test", "items": [item]}
            with patch.object(deliver_telegram_outbox, "load_notification", return_value=notification), patch.object(deliver_telegram_outbox, "undelivered_items", return_value=[item]), patch.object(deliver_telegram_outbox, "render_notification_message", return_value="Synthetic message"), patch.object(deliver_telegram_outbox, "notification_config", return_value=("synthetic-token", "synthetic-chat")) as credentials, patch.object(deliver_telegram_outbox, "send_message_once", new=AsyncMock(return_value=({"result": {"message_id": 42}}, True))) as send:
                self.assertEqual(0, asyncio.run(deliver_telegram_outbox._main(arguments)))
                credentials.assert_called_once_with(context=context)
                self.assertEqual(context.project_root, send.await_args.kwargs["repository_root"])
                self.assertEqual(base / "receipts", send.await_args.kwargs["receipt_dir"])
            receipt = json.loads((base / "sent/item.json").read_text(encoding="utf-8"))
            self.assertEqual("sent", receipt["delivery_status"])
            self.assertEqual(["synthetic-id"], receipt["delivered_vacancy_ids"])
            self.assertEqual(42, receipt["telegram_message_id"])

    def test_explicit_catalog_store_never_discovers_account_or_ambient_store(self):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            cv = root / "registry/jobs/synthetic-vacancy/application/cv.md"
            cv.parent.mkdir(parents=True)
            cv.write_text("Synthetic artifact", encoding="utf-8")
            store = MagicMock()
            store.list_vacancies.return_value = [document()]
            with patch("jobintel.catalog_data.op.get_store", side_effect=AssertionError("ambient store")), patch("jobintel.catalog_data.op.exists", side_effect=AssertionError("ambient read")):
                vacancies = load_catalog_vacancies(root / "registry", store=store)
            self.assertEqual(["synthetic-id"], [item.vacancy_id for item in vacancies])
            self.assertEqual(str(cv), vacancies[0].artifacts.cv_md)
            self.assertFalse((root / "config/accounts.yaml").exists())

    def test_restore_public_boundary_rejects_unknown_selector_before_backup_read(self):
        with patch.dict(os.environ, {"JOBINTEL_ACCOUNT": "unknown"}, clear=True), patch.object(verify_restored_backup, "verify_backup") as read:
            with self.assertRaises(AccountConfigurationError):
                verify_restored_backup.verify_restored_backup(Path("missing"), "jobintel_restore_test", Path("missing"))
            read.assert_not_called()

    def test_restore_legacy_artifacts_use_only_validated_test_store_without_environment_mutation(self):
        with TemporaryDirectory() as temporary, patch.dict(os.environ, {}, clear=True):
            root = Path(temporary)
            context = seed_account(root / "source")
            restored = root / "restored/project"
            restored.mkdir(parents=True)
            backup = root / "backup"
            backup.mkdir()
            (backup / "manifest.json").write_text("{}", encoding="utf-8")
            store = MagicMock()
            store.client.admin.command.return_value = {"setName": "rs0"}
            store.lease.return_value = nullcontext()
            store.snapshot.return_value = {"collections": {"vacancies": {"documents": []}}}
            store.list_vacancies.return_value = []
            manifest = {"backup_id": "synthetic", "backup_type": "mongodb-logical"}
            environment = {"JOBINTEL_TEST_MONGODB_URI": "mongodb://127.0.0.1:27019/?replicaSet=rs0&directConnection=true", "MONGODB_URI": "mongodb://production.invalid"}
            export = {"applications": [], "events": [], "source_revision": 1, "payload_sha256": "synthetic"}
            before = dict(os.environ)
            with patch.object(verify_restored_backup, "verify_backup", return_value={"ok": True}), patch.object(verify_restored_backup, "_load_manifest", return_value=(backup, manifest)), patch.object(verify_restored_backup, "_snapshot_from_backup", return_value={}), patch.object(verify_restored_backup, "resource_environment", return_value=environment), patch.object(verify_restored_backup, "MongoStore", return_value=store) as factory, patch.object(verify_restored_backup, "_compare_snapshots", return_value={"exact_match": True}), patch.object(verify_restored_backup, "_validate_artifact_references", return_value={}), patch.object(verify_restored_backup, "_validate_links_and_history", return_value={}), patch.object(verify_restored_backup, "export_applications", return_value={}), patch.object(verify_restored_backup, "build_export", return_value=export), patch.object(verify_restored_backup, "_manifest_summary", return_value={}), patch("jobintel.catalog_data.op.get_store", side_effect=AssertionError("ambient store")):
                receipt = verify_restored_backup.verify_restored_backup(backup, "jobintel_restore_test", root / "restored", context=context)
            self.assertEqual("success", receipt["state"])
            self.assertEqual(before, dict(os.environ))
            factory.assert_called_once_with(environment["JOBINTEL_TEST_MONGODB_URI"], "jobintel_restore_test")
            store.close.assert_called_once()
            self.assertFalse((restored / "config/accounts.yaml").exists())


if __name__ == "__main__":
    unittest.main()
