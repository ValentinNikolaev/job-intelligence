from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel.application_lifecycle import ApplicationLifecycle, profile_questions
from jobintel.application_lint import lint_application_draft
from jobintel.cli import _preparation_profile_paths, _profile_paths, _shared_candidate_context
from jobintel.evidence import bootstrap_evidence_bank
from jobintel.evidence_cli import main as evidence_main
from tests.preparation_fixtures import write_preparation_config
from tests.test_application_lifecycle import MemoryStore


class PreparationContextIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "records/person/resume.md"
        self.source.parent.mkdir(parents=True)
        self.quote = "Built services at Example."
        self.source.write_text(self.quote + "\n", encoding="utf-8")
        self.options = dict(
            candidate_directory="records/person",
            evidence_bank="records/proofs/bank.yaml",
            cv_owner_stem="AnotherPerson",
            profile_sources=["records/person/resume.md"],
            career_sources=[dict(path="records/person/resume.md", section="Experience")],
            voice_sources=["unavailable-host-voice.md"],
        )
        self.context = write_preparation_config(self.root, **self.options)
        self.extracts = [dict(id="delivery", source=dict(path="records/person/resume.md", quote=self.quote))]
        self.bank = bootstrap_evidence_bank(self.root, self.extracts, context=self.context)
        self.bank["entries"][0].update(
            status="verified",
            verification=dict(reviewer="synthetic-reviewer", reviewed_at="2026-10-20", method="fixture"),
        )
        self.write(self.context.evidence_bank, self.bank)

    def write(self, path, value):
        path = self.root / path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(value), encoding="utf-8")
        return path

    def evidence(self, *args):
        output = io.StringIO()
        with redirect_stdout(output):
            code = evidence_main(list(args), root=self.root)
        return code, output.getvalue()

    def test_preparation_selects_configured_sources_without_changing_analysis_resolution(self):
        original = self.root / "registry/candidate"
        original.mkdir(parents=True)
        for name in ("match-profile.md", "user-confirmed-z.md", "user-confirmed-a.md"):
            (original / name).write_text(name, encoding="utf-8")
        before = _profile_paths(None, {}, self.root, self.root / "registry")
        profiles = _preparation_profile_paths(None, {}, self.root, self.root / "registry", self.context)
        self.assertEqual([self.source.resolve()], profiles)
        self.assertEqual(["match-profile.md", "user-confirmed-a.md", "user-confirmed-z.md"], [p.name for p in before])
        self.assertEqual(before, _profile_paths(None, {}, self.root, self.root / "registry"))
        with self.assertRaisesRegex(ValueError, "configured candidate"):
            _preparation_profile_paths([original / "match-profile.md"], {}, self.root, self.root / "registry", self.context)

    def test_shared_packet_is_context_bound_and_uses_configured_bank_without_loading_voice(self):
        first = _shared_candidate_context(self.root, self.root / "registry", [self.source], context=self.context)
        packet = json.loads(Path(first["verified_evidence"]["path"]).read_text(encoding="utf-8"))
        self.assertEqual(self.context.version, first["preparation_context_version"])
        self.assertEqual(self.context.version, packet["preparation_context_version"])
        self.assertEqual("records/person", first["candidate_directory"])
        self.assertEqual("records/proofs/bank.yaml", first["evidence_bank"])
        self.assertEqual(["delivery"], [entry["id"] for entry in packet["entries"]])
        self.assertFalse((self.root / "unavailable-host-voice.md").exists())
        changed = write_preparation_config(self.root, **{**self.options, "cv_owner_stem": "RevisedOwner"})
        second = _shared_candidate_context(self.root, self.root / "registry", [self.source], context=changed)
        self.assertNotEqual(first["verified_evidence"]["path"], second["verified_evidence"]["path"])
        self.context.evidence_bank.unlink()
        with self.assertRaises((ValueError, OSError)):
            _shared_candidate_context(self.root, self.root / "registry", [self.source], context=changed)

    def test_evidence_commands_resolve_configured_bank_and_reject_foreign_sources(self):
        code, output = self.evidence("validate")
        self.assertEqual(0, code, output)
        self.assertEqual(self.context.version, json.loads(output)["preparation_context_version"])
        draft = self.write(".codex-work/reviewed.yaml", self.bank)
        code, output = self.evidence("publish", "--input", str(draft))
        self.assertEqual(0, code, output)
        self.assertEqual("records/proofs/bank.yaml", json.loads(output)["output"])
        self.assertFalse((self.root / "registry/evidence/achievements.yaml").exists())
        old = self.root / "registry/candidate/foreign.md"
        old.parent.mkdir(parents=True)
        old.write_text(self.quote, encoding="utf-8")
        self.bank["entries"][0]["source"]["path"] = "registry/candidate/foreign.md"
        self.write(draft, self.bank)
        before = self.context.evidence_bank.read_bytes()
        code, output = self.evidence("publish", "--input", str(draft))
        self.assertEqual(1, code, output)
        self.assertEqual(before, self.context.evidence_bank.read_bytes())

    def test_evidence_outputs_cannot_target_previous_evidence_or_candidate_directories(self):
        draft = self.write(".codex-work/reviewed.yaml", self.bank)
        for output in ("registry/evidence/other.yaml", "records/person/facts.yaml", "records/proofs/../../outside.yaml"):
            with self.subTest(output=output):
                code, message = self.evidence("publish", "--input", str(draft), "--output", output)
                self.assertEqual(1, code, message)
                self.assertFalse((self.root / output).exists())

    def test_draft_directory_link_cannot_export_evidence_outside_the_project(self):
        external = tempfile.TemporaryDirectory()
        self.addCleanup(external.cleanup)
        destination = Path(external.name)
        alias = self.root / ".codex-work"
        try:
            alias.symlink_to(destination, target_is_directory=True)
        except OSError as exc:
            if os.name != "nt":
                self.skipTest(f"directory symlinks unavailable: {exc}")
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(destination)], capture_output=True)
            if result.returncode:
                self.skipTest("directory symlinks and junctions unavailable")
        code, message = self.evidence("publish", "--input", "records/proofs/bank.yaml", "--output", ".codex-work/bank.yaml")
        self.assertEqual(1, code, message)
        self.assertEqual([], list(destination.iterdir()))
        with self.assertRaisesRegex(ValueError, "escapes the project"):
            _shared_candidate_context(self.root, self.root / "registry", [self.source], context=self.context)
        self.assertEqual([], list(destination.iterdir()))

    def test_lint_rejects_foreign_bank_before_reading_it_and_checks_context_identity(self):
        vacancy = self.root / "registry/jobs/example-job"
        vacancy.mkdir(parents=True)
        draft = self.root / ".codex-work/draft"
        draft.mkdir(parents=True)
        (draft / "analysis.md").write_text("Synthetic analysis.\n", encoding="utf-8")
        quality = dict(
            schema_version=3, preparation_context_version=self.context.version,
            evidence_bank="registry/evidence/foreign.yaml", claims_ledger="../../outside.yaml",
        )
        self.write(draft / "quality.yaml", quality)
        from jobintel import application_lint
        with patch("jobintel.application_lint._load", wraps=application_lint._load) as reader:
            report = lint_application_draft(vacancy, draft, document="analysis", context=self.context)
        read_paths = [call.args[0] for call in reader.call_args_list]
        self.assertNotIn(self.root / quality["evidence_bank"], read_paths)
        self.assertNotIn((draft / quality["claims_ledger"]).resolve(), read_paths)
        codes = {row["code"] for row in report["diagnostics"]}
        self.assertIn("EVIDENCE_UNAVAILABLE", codes)
        self.assertIn("CLAIM_CONTEXT", codes)
        self.assertNotIn("PREPARATION_CONTEXT", codes)
        quality.pop("preparation_context_version")
        self.write(draft / "quality.yaml", quality)
        report = lint_application_draft(vacancy, draft, document="analysis", context=self.context)
        self.assertIn("PREPARATION_CONTEXT", {row["code"] for row in report["diagnostics"]})

    def test_lint_rejects_foreign_context_before_reading_any_draft_or_evidence(self):
        other = tempfile.TemporaryDirectory()
        self.addCleanup(other.cleanup)
        other_root = Path(other.name)
        other_context = write_preparation_config(other_root, **self.options)
        self.assertEqual(self.context.version, other_context.version)
        vacancy = other_root / "registry/jobs/other-job"
        vacancy.mkdir(parents=True)
        with patch("jobintel.application_lint._load") as reader:
            report = lint_application_draft(
                vacancy, self.root / ".codex-work/draft", document="analysis", context=self.context,
            )
        self.assertFalse(report["ok"])
        self.assertEqual(["PREPARATION_CONTEXT"], [item["code"] for item in report["diagnostics"]])
        self.assertIn("another project", report["diagnostics"][0]["message"])
        reader.assert_not_called()

    def test_lint_rejects_stale_context_before_reading_any_draft_or_evidence(self):
        vacancy = self.root / "registry/jobs/example-job"
        vacancy.mkdir(parents=True)
        current = write_preparation_config(self.root, **{**self.options, "cv_owner_stem": "ChangedOwner"})
        with patch("jobintel.application_lint._load") as reader:
            report = lint_application_draft(
                vacancy, self.root / ".codex-work/draft", document="analysis", context=self.context,
            )
        self.assertFalse(report["ok"])
        self.assertEqual(["PREPARATION_CONTEXT"], [item["code"] for item in report["diagnostics"]])
        self.assertIn("stale", report["diagnostics"][0]["message"])
        reader.assert_not_called()
        fresh = lint_application_draft(vacancy, self.root / ".codex-work/draft", document="analysis", context=current)
        self.assertNotIn("PREPARATION_CONTEXT", [item["code"] for item in fresh["diagnostics"]])

    def test_ancillary_draft_requires_current_identity_and_configured_candidate_source(self):
        store = MemoryStore()
        lifecycle = ApplicationLifecycle(self.root, store=store)
        draft = dict(
            schema_version=1, vacancy_id="v1", kind="answers", grounding_review=True,
            preparation_context_version=self.context.version,
            items=[dict(prompt="Relevant work?", status="confirmed", text=self.quote, sources=[
                dict(path="records/person/resume.md", sha256=hashlib.sha256(self.source.read_bytes()).hexdigest(), quote=self.quote)
            ])],
        )
        before = json.dumps(store.documents, sort_keys=True)
        for version in (None, "preparation-v1:sha256:stale"):
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "context_version"):
                lifecycle.publish_draft("v1", kind="answers", draft={**draft, "preparation_context_version": version}, approved_vacancy="v1")
        self.assertEqual(before, json.dumps(store.documents, sort_keys=True))
        self.assertFalse((self.root / "registry/application-history").exists())
        result = lifecycle.publish_draft("v1", kind="answers", draft=draft, approved_vacancy="v1")
        self.assertEqual(self.context.version, result["preparation_context_version"])
        self.assertFalse(result["sent"])
        old = self.root / "registry/candidate/foreign.md"
        old.parent.mkdir(parents=True)
        old.write_bytes(self.source.read_bytes())
        draft["items"][0]["sources"][0]["path"] = "registry/candidate/foreign.md"
        with self.assertRaisesRegex(ValueError, "configured immutable candidate"):
            lifecycle.publish_draft("v1", kind="answers", draft=draft, approved_vacancy="v1")
        self.assertEqual("analyzed", store.vacancies[0]["meta"]["status"])

    def test_optional_preparation_settings_do_not_become_candidate_questions(self):
        self.assertEqual([], profile_questions(self.root))

    def test_preparation_filename_setting_cannot_be_published_as_a_candidate_fact(self):
        lifecycle = ApplicationLifecycle(self.root, store=MemoryStore())
        draft = dict(
            schema_version=1, vacancy_id="v1", kind="answers", grounding_review=True,
            preparation_context_version=self.context.version,
            items=[dict(prompt="Your name?", status="confirmed", text=self.context.cv_owner_stem,
                        profile_field="preparation.cv_owner_stem")],
        )
        with self.assertRaisesRegex(ValueError, "not confirmed candidate facts"):
            lifecycle.publish_draft("v1", kind="answers", draft=draft, approved_vacancy="v1")
        self.assertFalse((self.root / "registry/application-history").exists())

    def test_composed_application_fixture_restores_cli_configuration_root(self):
        from jobintel import cli
        from tests.test_application_review import ApplicationReviewTests

        original_file = cli.__file__
        try:
            result = unittest.TestResult()
            ApplicationReviewTests("test_letter_requires_review_of_exact_final_text").run(result)
            self.assertTrue(result.wasSuccessful(), result.errors or result.failures)
            self.assertEqual(original_file, cli.__file__)
        finally:
            cli.__file__ = original_file


if __name__ == "__main__":
    unittest.main()
