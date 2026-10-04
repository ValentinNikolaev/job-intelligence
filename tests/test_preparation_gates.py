from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel.application_lint import lint_application_draft
from jobintel import cli
from jobintel.document_quality import DocumentQualityError, preview_capabilities
from jobintel.document_quality_cli import main as document_main
from jobintel.cli import _resolve_explicit_preparation_directories
from jobintel.cli import _shared_candidate_context


class PreparationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        (self.root / "config").mkdir()
        (self.root / "registry" / "jobs" / "vacancy").mkdir(parents=True)
        (self.root / "registry" / "candidate").mkdir(parents=True)
        (self.root / "registry" / "jobs" / "vacancy" / "meta.yaml").write_text("id: vacancy-id\n", encoding="utf-8")
        (self.root / "config" / "codex-workflows.yaml").write_text(
            "schema_version: 1\nprepare_min_score: 65\nprepare_max_age_days: 14\nprepare_batch_size: 1\nmodel_profiles:\n  p:\n    model: test\n    reasoning: low\n    model_label: codex:test:low\nworkflows:\n  analyze:\n    default_profile: p\n    allowed_profiles: [p]\n  prepare:\n    default_profile: p\n    allowed_profiles: [p]\n", encoding="utf-8")

    def test_preflight_rejects_missing_mongodb_before_drafting(self) -> None:
        from types import SimpleNamespace

        args = SimpleNamespace(
            arguments=["vacancy"], workflow="prepare", model_profile=None,
            document="cv", profile=None, allow_low_score_cv_refresh=False,
        )
        with patch("jobintel.storage_bridge.get_store", return_value=None):
            with self.assertRaisesRegex(ValueError, "storage doctor"):
                cli._preflight_preparation(
                    args, {}, self.root, self.root / "registry", verify_environment=True
                )

    def test_preflight_rejects_automatic_or_duplicate_selection(self) -> None:
        with self.assertRaisesRegex(ValueError, "automatic"):
            _resolve_explicit_preparation_directories(self.root / "registry", ["all"], limit=1)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            _resolve_explicit_preparation_directories(self.root / "registry", ["vacancy", "vacancy"], limit=2)

    def test_shared_candidate_packet_contains_only_verified_entries(self) -> None:
        candidate = self.root / "registry" / "candidate" / "candidate.md"
        candidate.write_text("Verified candidate source", encoding="utf-8")
        bank = self.root / "registry" / "evidence" / "achievements.yaml"
        bank.parent.mkdir(parents=True)
        bank.write_text(yaml.safe_dump({"schema_version": 1, "entries": [
            {"id": "good", "status": "verified", "source": {"quote": "Verified candidate source"}},
            {"id": "withdrawn", "status": "retracted", "source": {"quote": "Old claim"}},
        ]}), encoding="utf-8")
        with patch("jobintel.evidence.validate_evidence_bank"):
            result = _shared_candidate_context(self.root, self.root / "registry", [candidate])
        packet = Path(result["verified_evidence"]["path"])
        self.assertTrue(packet.is_relative_to(self.root / ".codex-work"))
        self.assertEqual(["good"], [entry["id"] for entry in json.loads(packet.read_text())["entries"]])

    def test_preview_capability_reports_unavailable_renderer(self) -> None:
        script, options = self.root / "converter.ps1", self.root / "options.json"
        script.write_text("convert", encoding="utf-8")
        options.write_text("{}", encoding="utf-8")
        with patch("jobintel.document_quality._tool", side_effect=DocumentQualityError("renderer absent")):
            with self.assertRaisesRegex(DocumentQualityError, "renderer absent"):
                preview_capabilities(script, options, "pwsh")

    def test_preview_command_returns_unavailable_json_without_writing_a_package(self) -> None:
        source = self.root / ".codex-work" / "application" / "vacancy" / "cv.md"
        source.parent.mkdir(parents=True)
        source.write_text("## Experience\n- Result\n", encoding="utf-8")
        converter = type("Converter", (), {"script_path": self.root / "missing.ps1", "options_path": self.root / "missing.json", "powershell": "pwsh"})()
        output = io.StringIO()
        with patch("jobintel.applications.HostMarkdownDocxConverter", return_value=converter), redirect_stdout(output):
            self.assertEqual(1, document_main(["preview-cv", str(source)], root=self.root))
        result = json.loads(output.getvalue())
        self.assertEqual("unavailable", result["status"])
        self.assertFalse((self.root / "application").exists())

    def test_lint_reports_all_predictable_draft_diagnostics(self) -> None:
        candidate = self.root / "registry" / "candidate" / "candidate.md"
        candidate.write_text("Candidate source", encoding="utf-8")
        source_hash = hashlib.sha256(candidate.read_text(encoding="utf-8").encode()).hexdigest()
        vacancy = self.root / "registry" / "jobs" / "vacancy"
        (vacancy / "job.md").write_text("Actual job wording", encoding="utf-8")
        draft = self.root / "draft"
        draft.mkdir()
        (draft / "parts").mkdir()
        (draft / "parts" / "evidence-map.md").write_text("incomplete handoff", encoding="utf-8")
        (draft / "cv.md").write_text("## Summary\nCandidate \n\n## Skills\nPHP\n\n## Experience\n### Acme | 2024 - Present\n- Same result\n- Same result\n- Technologies: PHP\n### Old | 2010 - 2011\n- Technologies: PHP\n\n## Education\nCS\n\n## Languages\nEnglish\n", encoding="utf-8")
        bank = {"schema_version": 1, "entries": [
            {"id": "verified", "status": "verified", "employer": "Acme", "role": "Engineer", "period": "2024", "technologies": [], "source": {"path": "registry/candidate/candidate.md", "quote": "Candidate source", "sha256": source_hash}, "verification": {"reviewer": "test", "reviewed_at": "2026-01-01", "method": "test"}},
            {"id": "blocked", "status": "retracted", "reason": "withdrawn", "employer": "Acme", "role": "Engineer", "period": "2024", "technologies": [], "source": {"path": "registry/candidate/candidate.md", "quote": "Candidate source", "sha256": source_hash}},
        ]}
        (self.root / "registry" / "evidence.yaml").write_text(yaml.safe_dump(bank), encoding="utf-8")
        (draft / "claims.yaml").write_text(yaml.safe_dump({"schema_version": 1, "claims": [{"document": "cv", "text": "Same result", "evidence_ids": ["verified", "blocked"], "employer": "Other", "role": "Other"}]}), encoding="utf-8")
        quality = {"schema_version": 2, "workflow": "two-wave", "evidence_bank": "registry/evidence.yaml", "claims_ledger": "claims.yaml", "final_review": {"claim_grounding": True, "cross_file_consistency": True, "reviewer": "test", "quality_gate": True, "document_sha256": {"cv": "sha256:stale"}}, "cv_audit": {"target_role": "Engineer", "top_third_evidence_ids": ["verified", "blocked"], "bullet_decisions": []}, "requirements": [{"requirement": "PHP", "importance": "high", "basis": "stated", "jd_quote": "Missing job quote", "match": "partial", "candidate_quote": "Missing candidate quote", "risk": "risk", "mitigation": "ask", "hard_blocker": False, "evidence_ids": ["verified"]}]}
        (draft / "quality.yaml").write_text(yaml.safe_dump(quality), encoding="utf-8")
        report = lint_application_draft(vacancy, draft, document="cv")
        codes = {item["code"] for item in report["diagnostics"]}
        self.assertFalse(report["ok"])
        self.assertTrue({"HANDOFF_MARKER", "ARTIFACT_HASH_STALE", "CV_AUDIT_ANCHOR", "CV_DUPLICATE_BULLET", "CV_TECHNOLOGIES_NOT_BULLETS", "EVIDENCE_UNAVAILABLE", "CLAIM_ROLE_INCOMPATIBLE", "CANDIDATE_QUOTE_NOT_EXACT", "JOB_QUOTE_NOT_EXACT", "TRAILING_WHITESPACE"}.issubset(codes))

    def test_lint_accepts_canonical_mongodb_job_text_without_local_projection(self) -> None:
        candidate = self.root / "registry" / "candidate" / "candidate.md"
        candidate.write_text("Candidate source", encoding="utf-8")
        source_hash = hashlib.sha256(candidate.read_text(encoding="utf-8").encode()).hexdigest()
        vacancy = self.root / "registry" / "jobs" / "vacancy"
        draft = self.root / "draft"
        (draft / "parts").mkdir(parents=True)
        (draft / "parts" / "evidence-map.md").write_text("Priority requirement Candidate evidence and source Match ## Proposed CV " * 100, encoding="utf-8")
        cv = "# Candidate\nBackend Engineer\n\n## Summary\n\nSenior backend engineer with relevant experience.\n\n## Skills\n\nGo, PHP, Laravel, Symfony, AWS, Kubernetes, EventBridge, SQS, REST APIs, OpenAPI, Webhooks, Queues\n\n## Experience\n\n### Acme — Engineer | January 2024 – Current\n\n- Delivered a supported backend outcome.\n- Improved a supported production workflow.\n- Built a supported integration.\n\nTechnologies: Go, AWS\n\n## Education\n\nMSc\n\n## Languages\n\nEnglish\n"
        (draft / "cv.md").write_text(cv, encoding="utf-8")
        bank = {"schema_version": 1, "entries": [{"id": "verified", "status": "verified", "employer": "Acme", "role": "Engineer", "period": "2024", "technologies": [], "source": {"path": "registry/candidate/candidate.md", "quote": "Candidate source", "sha256": source_hash}, "verification": {"reviewer": "test", "reviewed_at": "2026-01-01", "method": "test"}}]}
        (self.root / "registry" / "evidence.yaml").write_text(yaml.safe_dump(bank), encoding="utf-8")
        claims = {"schema_version": 1, "claims": [{"document": "cv", "text": bullet, "evidence_ids": ["verified"], "employer": "Acme", "role": "Engineer"} for bullet in ("Delivered a supported backend outcome.", "Improved a supported production workflow.", "Built a supported integration.")]}
        (draft / "claims.yaml").write_text(yaml.safe_dump(claims), encoding="utf-8")
        digest = "sha256:" + hashlib.sha256((cv.strip() + "\n").encode()).hexdigest()
        quality = {"schema_version": 2, "workflow": "two-wave", "evidence_bank": "registry/evidence.yaml", "claims_ledger": "claims.yaml", "final_review": {"claim_grounding": True, "cross_file_consistency": True, "reviewer": "test", "quality_gate": True, "document_sha256": {"cv": digest}}, "cv_audit": {"target_role": "Backend Engineer", "top_third_evidence_ids": ["verified", "verified"], "bullet_decisions": []}, "requirements": [{"requirement": "Go", "importance": "critical", "basis": "stated", "jd_quote": "Canonical MongoDB job wording", "match": "strong", "candidate_quote": "Candidate source", "risk": "", "mitigation": "", "hard_blocker": False, "evidence_ids": ["verified"]}]}
        (draft / "quality.yaml").write_text(yaml.safe_dump(quality), encoding="utf-8")
        report = lint_application_draft(vacancy, draft, document="cv", vacancy_text="Canonical MongoDB job wording")
        self.assertNotIn("JOB_QUOTE_NOT_EXACT", {item["code"] for item in report["diagnostics"]})


if __name__ == "__main__":
    unittest.main()
