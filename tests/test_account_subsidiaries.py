from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel import (
    document_quality_cli,
    editorial_eval,
    evidence_cli,
    lifecycle_cli,
    preparation_timing,
    sheets_sync,
    storage_bridge,
)
from jobintel.accounts import load_account_context
from jobintel.evidence import bootstrap_evidence_bank
from tests.account_fixtures import write_file_account_config
from tests.preparation_fixtures import write_preparation_config
from tests.test_sheets_sync import source as sheets_source


ENTRIES = (
    (evidence_cli, evidence_cli.main, ["questions"]),
    (document_quality_cli, document_quality_cli.main, ["validate", "source.md", "artifact.docx"]),
    (lifecycle_cli, lifecycle_cli.main, ["report"]),
    (preparation_timing, preparation_timing.main, ["report"]),
    (editorial_eval, editorial_eval.main, ["export", "--output", ".codex-work/editorial.json"]),
    (sheets_sync, sheets_sync.cli_main,
     ["export", "--input", ".codex-work/input.json", "--output", ".codex-work/output.json"]),
)


class AccountSubsidiaryTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "selected"
        self.other = self.base / "working-directory"
        write_file_account_config(self.root)
        write_file_account_config(self.other)
        self.process_support = {
            key: os.environ[key] for key in ("SYSTEMROOT", "WINDIR", "SYSTEMDRIVE", "PATH", "TEMP", "TMP")
            if key in os.environ
        }
        environment = patch.dict(os.environ, {}, clear=True)
        environment.start()
        self.addCleanup(environment.stop)
        self.context = load_account_context(self.root)

    def write(self, relative, payload, *, root=None):
        target = (root or self.root) / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(payload), encoding="utf-8")
        return target

    def call(self, entrypoint, argv, **kwargs):
        output, errors = io.StringIO(), io.StringIO()
        with redirect_stdout(output), redirect_stderr(errors):
            code = entrypoint(argv, **kwargs)
        return code, output.getvalue(), errors.getvalue()

    def test_unknown_or_conflicting_account_never_reaches_any_leaf_handler(self):
        cases = [
            (["--account=another"], {}),
            (["--account=current", "--account=another"], {}),
            (["--account=current"], {"JOBINTEL_ACCOUNT": "another"}),
        ]
        for module, entrypoint, argv in ENTRIES:
            for selectors, environment in cases:
                with self.subTest(module=module.__name__, selectors=selectors, environment=environment):
                    with patch.dict(os.environ, environment, clear=True):
                        with patch.object(module, "_main", side_effect=AssertionError("leaf dispatched")):
                            code, output, errors = self.call(entrypoint, [*argv, *selectors], root=self.root)
                    self.assertEqual(2, code, errors)
                    self.assertEqual("", output)
                    self.assertIn("Account configuration error:", errors)
        self.assertFalse((self.root / ".codex-work").exists())

    def test_each_leaf_rejects_stale_context_before_payload_or_output(self):
        descriptor = self.root / "config/accounts.yaml"
        descriptor.write_bytes(descriptor.read_bytes() + b"# changed\n")
        for module, entrypoint, argv in ENTRIES:
            with self.subTest(module=module.__name__):
                with patch.object(module, "_main", side_effect=AssertionError("leaf dispatched")):
                    code, _, errors = self.call(entrypoint, argv, context=self.context)
                self.assertEqual(2, code)
                self.assertIn("stale", errors)
        self.assertFalse((self.root / ".codex-work").exists())

    def test_each_leaf_rejects_missing_descriptor_without_executable_root_fallback(self):
        (self.root / "config/accounts.yaml").unlink()
        for module, entrypoint, argv in ENTRIES:
            with self.subTest(module=module.__name__):
                with patch.object(module, "_main", side_effect=AssertionError("leaf dispatched")):
                    code, _, errors = self.call(entrypoint, argv, root=self.root)
                self.assertEqual(2, code)
                self.assertIn("cannot read", errors)

    def test_each_leaf_rejects_root_conflict_with_supplied_context(self):
        for module, entrypoint, argv in ENTRIES:
            with self.subTest(module=module.__name__):
                with patch.object(module, "_main", side_effect=AssertionError("leaf dispatched")):
                    code, _, errors = self.call(
                        entrypoint, [*argv, "--project-root", str(self.other)], context=self.context,
                    )
                self.assertEqual(2, code)
                self.assertIn("conflicts", errors)

    def test_each_leaf_preserves_context_root_and_resource_binding_without_loading_credentials(self):
        for module, entrypoint, argv in ENTRIES:
            with self.subTest(module=module.__name__):
                def verify(arguments, *, root):
                    self.assertEqual(argv, arguments)
                    self.assertEqual(self.root, root)
                    with self.assertRaisesRegex(ValueError, "another project root"):
                        storage_bridge.get_store(self.other)
                    return 0

                with patch.object(module, "_main", side_effect=verify):
                    with patch("jobintel.storage_bridge.load_env", side_effect=AssertionError("credentials read")):
                        code, _, errors = self.call(entrypoint, ["--account", "current", *argv], context=self.context)
                self.assertEqual(0, code, errors)
                self.assertIsNone(storage_bridge.get_store(self.other))
        self.assertFalse((self.root / ".codex-work").exists())

    def test_each_leaf_rejects_account_abbreviation_before_payload_access(self):
        for module, entrypoint, argv in ENTRIES:
            with self.subTest(module=module.__name__):
                with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                    entrypoint([*argv, "--acc=another"], root=self.root)
                self.assertEqual(2, error.exception.code)
        self.assertFalse((self.root / ".codex-work").exists())

    def test_sheets_export_resolves_relative_inputs_and_outputs_against_selected_root(self):
        self.write(".codex-work/input.json", sheets_source())
        self.write(".codex-work/input.json", {"poisoned": "wrong root"}, root=self.other)
        previous = Path.cwd()
        try:
            os.chdir(self.other)
            code, _, errors = self.call(
                sheets_sync.cli_main,
                ["export", "--input", ".codex-work/input.json", "--output", ".codex-work/output.json",
                 "--account=current", "--project-root", str(self.root)],
            )
        finally:
            os.chdir(previous)
        self.assertEqual(0, code, errors)
        result = json.loads((self.root / ".codex-work/output.json").read_text(encoding="utf-8"))
        self.assertEqual("vac-1", result["applications"][0]["vacancy_id"])
        self.assertFalse((self.other / ".codex-work/output.json").exists())

    def test_sheets_requests_use_selected_destination_configuration(self):
        destination = {"google": {"spreadsheet_id": "selected-spreadsheet",
                                  "parent_folder_id": "selected-parent", "backup_folder_id": "selected-backup"}}
        (self.root / "config/data-services.yaml").write_text(yaml.safe_dump(destination), encoding="utf-8")
        self.write(".codex-work/metadata.json", {"sheets": []})
        self.write(".codex-work/plan.json", {})
        previous = Path.cwd()
        try:
            os.chdir(self.other)
            with patch.object(sheets_sync, "build_batch_requests", return_value=[]):
                code, _, errors = self.call(
                    sheets_sync.cli_main,
                    ["requests", "--plan", ".codex-work/plan.json", "--metadata", ".codex-work/metadata.json",
                     "--application-next-row", "2", "--history-next-row", "2",
                     "--output", ".codex-work/requests.json"],
                    context=self.context,
                )
        finally:
            os.chdir(previous)
        self.assertEqual(0, code, errors)
        result = json.loads((self.root / ".codex-work/requests.json").read_text(encoding="utf-8"))
        self.assertEqual("selected-spreadsheet", result["spreadsheet_id"])
        self.assertFalse((self.other / ".codex-work/requests.json").exists())

    def test_sheets_reject_foreign_or_traversing_artifact_paths(self):
        self.write(".codex-work/input.json", sheets_source())
        outside_input = self.write(".codex-work/input.json", sheets_source(), root=self.other)
        for input_path, output_path in (
            (str(outside_input), ".codex-work/output.json"),
            (".codex-work/input.json", str(self.other / ".codex-work/output.json")),
            (".codex-work/input.json", ".codex-work/../escaped.json"),
        ):
            with self.subTest(input=input_path, output=output_path):
                code, _, errors = self.call(
                    sheets_sync.cli_main, ["export", "--input", input_path, "--output", output_path],
                    context=self.context,
                )
                self.assertEqual(1, code, errors)
                self.assertIn("JSON artifacts must be under", errors)
        self.assertFalse((self.root / ".codex-work/output.json").exists())
        self.assertFalse((self.other / ".codex-work/output.json").exists())
        self.assertFalse((self.root / "escaped.json").exists())

    def test_timing_start_stop_and_report_stay_in_selected_root(self):
        previous = Path.cwd()
        try:
            os.chdir(self.other)
            for argv in (["start", "analysis", "--vacancy", "synthetic"],
                         ["stop", "analysis", "--vacancy", "synthetic"], ["report"]):
                code, _, errors = self.call(preparation_timing.main, argv, context=self.context)
                self.assertEqual(0, code, errors)
        finally:
            os.chdir(previous)
        report = json.loads((self.root / ".codex-work/preparation-timing.json").read_text(encoding="utf-8"))
        self.assertEqual(1, len(report["events"]))
        self.assertEqual("synthetic", report["events"][0]["vacancy"])
        self.assertFalse((self.other / ".codex-work").exists())

    def test_lifecycle_relative_note_reads_selected_root_and_preserves_message_bytes(self):
        text = "Thank you.\r\n\r\nWe will not proceed.\r\n"
        (self.root / "note.txt").write_bytes(text.encode())
        (self.other / "note.txt").write_text("wrong root", encoding="utf-8")
        previous = Path.cwd()
        try:
            os.chdir(self.other)
            with patch.object(lifecycle_cli, "ApplicationLifecycle") as factory:
                factory.return_value.record_event.return_value = {"ok": True}
                code, _, errors = self.call(
                    lifecycle_cli.main,
                    ["record-event", "vacancy", "--submission-id", "s1", "--event-id", "e1",
                     "--kind", "rejection", "--occurred-on", "2026-10-20",
                     "--note-file", "note.txt", "--note-origin", "employer_message"],
                    context=self.context,
                )
                self.assertEqual(0, code, errors)
                factory.assert_called_once_with(self.root)
                self.assertEqual(text, factory.return_value.record_event.call_args.kwargs["note"])
        finally:
            os.chdir(previous)

    def test_evidence_questions_use_selected_profile_and_bank_without_credentials(self):
        source = self.root / "synthetic/person/resume.md"
        source.parent.mkdir(parents=True)
        source.write_text("Built services at Example.", encoding="utf-8")
        preparation = write_preparation_config(
            self.root, candidate_directory="synthetic/person", evidence_bank="synthetic/proofs/bank.yaml",
            profile_sources=["synthetic/person/resume.md"], cv_owner_stem="SyntheticPerson",
        )
        bank = bootstrap_evidence_bank(
            self.root, [{"id": "delivery", "source": {"path": "synthetic/person/resume.md",
                                                      "quote": "Built services at Example."}}],
            context=preparation,
        )
        preparation.evidence_bank.parent.mkdir(parents=True)
        preparation.evidence_bank.write_text(yaml.safe_dump(bank), encoding="utf-8")
        with patch("jobintel.storage_bridge.load_env", side_effect=AssertionError("credentials read")):
            code, output, errors = self.call(evidence_cli.main, ["questions", "--id", "delivery"], context=self.context)
        self.assertEqual(0, code, errors)
        self.assertEqual(preparation.version, json.loads(output)["preparation_context_version"])
        self.assertFalse((self.other / "synthetic").exists())

    def test_editorial_output_and_corpus_are_resolved_from_selected_root(self):
        with patch.object(editorial_eval, "export_pack", return_value={"cases": ["synthetic"]}) as export:
            code, _, errors = self.call(
                editorial_eval.main, ["export", "--output", ".codex-work/editorial.json"], context=self.context,
            )
        self.assertEqual(0, code, errors)
        export.assert_called_once_with(self.root)
        self.assertEqual({"cases": ["synthetic"]},
                         json.loads((self.root / ".codex-work/editorial.json").read_text(encoding="utf-8")))
        self.assertFalse((self.other / ".codex-work").exists())

    def test_module_entrypoints_reject_unknown_account_without_creating_outputs(self):
        repository = Path(__file__).resolve().parents[1]
        environment = dict(self.process_support, PYTHONPATH=str(repository))
        for module, _, argv in ENTRIES:
            with self.subTest(module=module.__name__):
                result = subprocess.run(
                    [sys.executable, "-m", module.__name__, *argv, "--account=another",
                     "--project-root", str(self.root)],
                    cwd=self.other, env=environment, capture_output=True, text=True, check=False,
                )
                self.assertEqual(2, result.returncode, result.stderr)
                self.assertIn("Account configuration error:", result.stderr)
        self.assertFalse((self.root / ".codex-work").exists())
        self.assertFalse((self.other / ".codex-work").exists())


if __name__ == "__main__":
    unittest.main()
