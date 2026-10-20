from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from jobintel.evidence import EvidenceError, bootstrap_evidence_bank, validate_claims_ledger, validate_evidence_bank
from tests.preparation_fixtures import write_preparation_config


class EvidenceTests(unittest.TestCase):
    def contextual_metric(self):
        text = 'Example Backend Engineer reduced team onboarding time by 35%.'
        self.path.write_text(text, encoding='utf-8')
        bank = bootstrap_evidence_bank(self.root, [dict(id='time', source=dict(path='registry/candidate/cv.md', quote=text))])
        entry = bank['entries'][0]
        entry.update(status='verified', verification=dict(reviewer='editor', reviewed_at='2026-10-15', method='source review'))
        entry['measurements'] = [dict(id='reduction', value='35%', measure='onboarding time', unit='%', scope='team',
            baseline=None, period=None, method=None, quote=text)]
        claim = 'Reduced team onboarding time by 35%.'
        ledger = dict(schema_version=2, claims=[dict(document='cover-letter', text=claim, evidence_ids=['time'],
            measurements=[dict(evidence_id='time', measurement_id='reduction', claim_quote=claim)])])
        return bank, ledger, dict(cover_letter_markdown=claim)

    def test_measurement_context_accepts_explicit_unknown_method_without_inventing_it(self):
        bank, ledger, package = self.contextual_metric()
        receipt = validate_claims_ledger(ledger, bank, package, self.root)
        self.assertIsNone(receipt['evidence_entries'][0]['measurements'][0]['method'])
        self.assertEqual(2, receipt['schema_version'])

    def test_strict_numeric_claim_requires_context(self):
        bank, ledger, package = self.contextual_metric()
        ledger['claims'][0].pop('measurements')
        with self.assertRaisesRegex(EvidenceError, 'numeric token requires'):
            validate_claims_ledger(ledger, bank, package, self.root)

    def test_measurement_cannot_change_unit_scope_or_reference(self):
        for mutation in ('unit', 'scope', 'reference'):
            with self.subTest(mutation=mutation):
                bank, ledger, package = self.contextual_metric()
                if mutation == 'reference':
                    ledger['claims'][0]['measurements'][0]['measurement_id'] = 'other'
                else:
                    claim = package['cover_letter_markdown'].replace('%', ' seconds') if mutation == 'unit' else package['cover_letter_markdown'].replace('team', 'customer')
                    ledger['claims'][0]['text'] = claim
                    ledger['claims'][0]['measurements'][0]['claim_quote'] = claim
                    package['cover_letter_markdown'] = claim
                with self.assertRaises(EvidenceError):
                    validate_claims_ledger(ledger, bank, package, self.root)

    def test_measurement_basis_must_be_sourced_or_explicitly_unknown(self):
        for field in ('baseline', 'period', 'method'):
            with self.subTest(field=field):
                bank, ledger, package = self.contextual_metric()
                bank['entries'][0]['measurements'][0][field] = 'Invented measurement context'
                with self.assertRaisesRegex(EvidenceError, 'absent from its source quote'):
                    validate_claims_ledger(ledger, bank, package, self.root)

    def test_translation_keeps_the_original_numeric_context_and_units(self):
        bank, ledger, package = self.contextual_metric()
        claim = 'Ridotto il tempo di onboarding della squadra del 35%.'
        binding = ledger['claims'][0]['measurements'][0]
        binding.update(claim_quote=claim, translation=dict(language='Italian', reviewer='Italian editor',
            reason='The translated measure and scope preserve onboarding time for the team.',
            source_quote=bank['entries'][0]['measurements'][0]['quote'], measure='tempo di onboarding', scope='squadra'))
        ledger['claims'][0]['text'] = package['cover_letter_markdown'] = claim
        validate_claims_ledger(ledger, bank, package, self.root)
        binding['translation']['language'] = 'English'
        with self.assertRaisesRegex(EvidenceError, 'source language'):
            validate_claims_ledger(ledger, bank, package, self.root)


    def test_achievement_context_cannot_claim_an_unsourced_fact(self):
        self.bank['entries'][0]['achievement_context'] = dict(responsibility=dict(status='supported', quote='Independently set business priorities'))
        with self.assertRaisesRegex(EvidenceError, 'primary evidence'):
            validate_evidence_bank(self.bank, self.root)
        self.bank['entries'][0]['achievement_context'] = dict(responsibility=dict(status='unknown'))
        validate_evidence_bank(self.bank, self.root)

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        write_preparation_config(self.root)
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
                with self.assertRaisesRegex(EvidenceError, "evidence|traversal"):
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

    def test_separate_candidate_source_can_establish_role_attribution(self):
        fact = self.root / "registry/candidate/fact.md"
        fact.write_text("Example delivered a Go gateway.", encoding="utf-8")
        bank = bootstrap_evidence_bank(self.root, [{"id": "gateway", "employer": "Example",
            "source": {"path": "registry/candidate/fact.md",
            "quote": "Example delivered a Go gateway."}}])
        bank["entries"][0].update(role="Backend Engineer", status="verified", verification={"reviewer": "test", "reviewed_at": "2026-09-26", "method": "source review"},
            attribution_source=self.bank["entries"][0]["source"])
        self.assertEqual(1, validate_evidence_bank(bank, self.root)["entry_count"])
        self.path.write_text(self.quote + "\nnew context", encoding="utf-8")
        with self.assertRaisesRegex(EvidenceError, "stale source hash"):
            validate_evidence_bank(bank, self.root)

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
