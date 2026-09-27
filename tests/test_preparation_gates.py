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
from jobintel.document_quality import DocumentQualityError, preview_capabilities
from jobintel.document_quality_cli import main as document_main
from jobintel.preparation_preflight import PreparationPreflightError, run_preflight, selected_preparation_directories


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
        with patch("jobintel.preparation_preflight.load_env", return_value={}):
            with self.assertRaisesRegex(PreparationPreflightError, "MongoDB configuration"):
                run_preflight(self.root, ["vacancy"], workflow="prepare")

    def test_preflight_rejects_automatic_or_duplicate_selection(self) -> None:
        with self.assertRaisesRegex(PreparationPreflightError, "explicit"):
            selected_preparation_directories(self.root / "registry", ["all"], limit=1)
        with self.assertRaisesRegex(PreparationPreflightError, "duplicate"):
            selected_preparation_directories(self.root / "registry", ["vacancy", "vacancy"], limit=2)

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
        (draft / "cv.md").write_text("## Summary\nCandidate\n\n## Skills\nPHP\n\n## Experience\n### Acme | 2024 - Present\n- Same result\n- Same result\n- Technologies: PHP\n### Old | 2010 - 2011\n- Technologies: PHP\n\n## Education\nCS\n\n## Languages\nEnglish\n", encoding="utf-8")
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
        self.assertTrue({"HANDOFF_MARKER", "ARTIFACT_HASH_STALE", "CV_AUDIT_ANCHOR", "CV_DUPLICATE_BULLET", "CV_TECHNOLOGIES_NOT_BULLETS", "EVIDENCE_UNAVAILABLE", "CLAIM_ROLE_INCOMPATIBLE", "CANDIDATE_QUOTE_NOT_EXACT", "JOB_QUOTE_NOT_EXACT", "COMBINED_VALIDATOR"}.issubset(codes))


if __name__ == "__main__":
    unittest.main()
