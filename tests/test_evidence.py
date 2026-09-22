from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from jobintel.evidence import EvidenceError, bootstrap_evidence_bank, validate_claims_ledger, validate_evidence_bank


class EvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "registry/candidate/cv.md"
        self.path.parent.mkdir(parents=True)
        self.quote = "Example РІР‚вЂќ Backend Engineer | 2020 - 2024\nBuilt PHP APIs and reduced latency by 35%."
        self.path.write_text(self.quote, encoding="utf-8")
        self.bank = bootstrap_evidence_bank(self.root, [{"id": "api", "employer": "Example", "role": "Backend Engineer",
            "period": "2020 - 2024", "technologies": ["PHP"], "source": {"path": "registry/candidate/cv.md", "quote": self.quote}}])
        self.bank["entries"][0].update(status="verified", verification={"reviewer": "test", "reviewed_at": "2026-09-22", "method": "source review"})
        self.package = {"cv_markdown": "## Experience\n### Example вЂ” Backend Engineer\n- Built PHP APIs and reduced latency by 35%.\n"}
        self.ledger = {"schema_version": 1, "claims": [{"document": "cv", "text": "Built PHP APIs and reduced latency by 35%.",
            "evidence_ids": ["api"], "employer": "Example", "role": "Backend Engineer", "technologies": ["PHP"]}]}

    def test_bootstrap_cannot_self_verify(self):
        bank = bootstrap_evidence_bank(self.root, self.bank["entries"])
        self.assertEqual("unverified", bank["entries"][0]["status"])
        self.assertEqual(self.quote, self.path.read_text(encoding="utf-8"))

    def test_verified_claim_receipt(self):
        receipt = validate_claims_ledger(self.ledger, self.bank, self.package, self.root)
        self.assertEqual(["api"], receipt["evidence_ids"])
        self.assertTrue(receipt["semantic_review_required"])

    def test_changed_source_and_fabricated_quote_rejected(self):
        self.path.write_text(self.quote + "\nNew text", encoding="utf-8")
        with self.assertRaisesRegex(EvidenceError, "stale source hash"):
            validate_evidence_bank(self.bank, self.root)
        self.bank["entries"][0]["source"]["quote"] = "Invented result"
        with self.assertRaisesRegex(EvidenceError, "quote is absent"):
            validate_evidence_bank(self.bank, self.root)

    def test_derived_outputs_are_never_candidate_evidence(self):
        for path in ["registry/jobs/a/application/cv.md", "registry/candidate/../../cv.md"]:
            with self.subTest(path=path):
                bank = copy.deepcopy(self.bank)
                bank["entries"][0]["source"]["path"] = path
                with self.assertRaisesRegex(EvidenceError, "registry/candidate"):
                    validate_evidence_bank(bank, self.root)

    def test_unusable_statuses_cannot_ground_claims(self):
        for status in ["unverified", "cannot-confirm", "retracted"]:
            with self.subTest(status=status):
                self.bank["entries"][0].update(status=status, reason="Not confirmed")
                with self.assertRaisesRegex(EvidenceError, "unavailable verified evidence"):
                    validate_claims_ledger(self.ledger, self.bank, self.package, self.root)

    def test_metric_inflation_rejected(self):
        self.ledger["claims"][0]["text"] = "Reduced latency by 95%."
        self.package["cv_markdown"] = "## Experience\n- Reduced latency by 95%."
        with self.assertRaisesRegex(EvidenceError, "unsupported numeric"):
            validate_claims_ledger(self.ledger, self.bank, self.package, self.root)

    def test_employer_or_technology_laundering_rejected(self):
        self.ledger["claims"][0]["employer"] = "Another employer"
        with self.assertRaisesRegex(EvidenceError, "employer does not match"):
            validate_claims_ledger(self.ledger, self.bank, self.package, self.root)
        self.ledger["claims"][0]["employer"] = "Example"
        self.ledger["claims"][0]["technologies"] = ["Go"]
        with self.assertRaisesRegex(EvidenceError, "technology lacks"):
            validate_claims_ledger(self.ledger, self.bank, self.package, self.root)

    def test_uncovered_cv_bullet_rejected(self):
        self.package["cv_markdown"] += "- Owned a different project.\n"
        with self.assertRaisesRegex(EvidenceError, "every CV experience bullet"):
            validate_claims_ledger(self.ledger, self.bank, self.package, self.root)

    def test_duplicate_id_and_unproven_attribution_rejected(self):
        self.bank["entries"].append(copy.deepcopy(self.bank["entries"][0]))
        with self.assertRaisesRegex(EvidenceError, "duplicate evidence"):
            validate_evidence_bank(self.bank, self.root)

        self.bank["entries"].pop()
        self.bank["entries"][0]["role"] = "Director"
        with self.assertRaisesRegex(EvidenceError, "role is absent"):
            validate_evidence_bank(self.bank, self.root)

    def test_same_quote_cannot_be_resurrected_under_another_id(self):
        blocked = copy.deepcopy(self.bank["entries"][0])
        blocked.update(id="old-claim", status="cannot-confirm", reason="Candidate cannot confirm this result")
        self.bank["entries"].append(blocked)
        with self.assertRaisesRegex(EvidenceError, "both verified"):
            validate_evidence_bank(self.bank, self.root)

    def test_actual_cv_heading_prevents_omitted_attribution_bypass(self):
        self.ledger["claims"][0].pop("employer")
        self.package["cv_markdown"] = self.package["cv_markdown"].replace("### Example", "### Another employer")
        with self.assertRaisesRegex(EvidenceError, "actual role heading"):
            validate_claims_ledger(self.ledger, self.bank, self.package, self.root)


if __name__ == "__main__":
    unittest.main()
