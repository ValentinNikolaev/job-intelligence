"""Observable failures for the next application review contract."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml

from jobintel.applications import ApplicationError, _validate_v2_grounding
from jobintel.evidence import bootstrap_evidence_bank, validate_claims_ledger, EvidenceError
from jobintel.application_review import validate_role_inventory, validate_letter_review, review_digest, letter_basis
from tests.application_review_fixtures import add_letter_review
from tests.preparation_fixtures import write_preparation_config
from jobintel.preparation_context import load_preparation_context


def digest(text):
    return 'sha256:' + hashlib.sha256((text.strip() + '\n').encode()).hexdigest()


class ApplicationReviewTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        write_preparation_config(self.root, evidence_bank="registry/evidence/bank.yaml")
        self.draft = self.root / '.codex-work/draft'
        self.draft.mkdir(parents=True)
        self.source = self.root / 'registry/candidate/linkedin-profile.md'
        self.source.parent.mkdir(parents=True)
        self.bullets = ['Designed PHP billing APIs that enabled customer self-service.',
                        'Led API migration that allowed the support team to retire manual reconciliation.']
        self.source.write_text('# Candidate\n## Experience\n### Example\nBackend Engineer\nJanuary 2022 - Present\n' + '\n'.join(self.bullets) + '\n## Education\n', encoding='utf-8')
        self.bank = bootstrap_evidence_bank(self.root, [dict(id=f'proof-{i}', employer='Example', role='Backend Engineer',
            source=dict(path='registry/candidate/linkedin-profile.md', quote=text,
                        context_quote='Example\nBackend Engineer\nJanuary 2022 - Present')) for i, text in enumerate(self.bullets)])
        for entry in self.bank['entries']:
            entry.update(status='verified', verification=dict(reviewer='source-editor', reviewed_at='2026-10-15', method='source review'))
        cv = '## Experience\n### Example — Backend Engineer | January 2022 - Present\n' + '\n'.join('- ' + b for b in self.bullets) + '\n## Education\n' + 'Supporting chronology. ' * 100
        cv = cv.strip() + '\n'
        self.package = dict(cv_markdown=cv)
        self.ledger = dict(schema_version=1, claims=[dict(document='cv', text=b, evidence_ids=[f'proof-{i}']) for i, b in enumerate(self.bullets)])
        self.quality = dict(schema_version=3, preparation_context_version=load_preparation_context(self.root).version, evidence_bank='registry/evidence/bank.yaml', claims_ledger='claims.yaml',
            final_review=dict(reviewer='final-editor', quality_gate=True, document_sha256={'cv': digest(cv)}),
            cv_audit=dict(target_role='Senior Backend Engineer', top_third_evidence_ids=['proof-0', 'proof-1'],
                editorial_review=dict(knowledge_base_version=1, verdict='approve', reviewer='independent-editor', mode='independent'),
                bullet_decisions=[dict(text=b, decision='keep', reason='Answers billing API requirement', verdict='approve',
                    weight='high', signal_type='impact', ordering_rationale='Distinct customer consequence',
                    contribution='API delivery', affected_scope='Billing product', consequence='Self-service and reconciliation') for b in self.bullets]),
            requirements=[dict(requirement='Billing APIs', importance='high', basis='stated', jd_quote='Build billing APIs.',
                match='strong', candidate_quote=self.bullets[0], risk='', mitigation='', hard_blocker=False, evidence_ids=['proof-0'])])
        self.save()

    def save(self):
        path = self.root / 'registry/evidence/bank.yaml'
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(self.bank), encoding='utf-8')
        (self.draft / 'claims.yaml').write_text(yaml.safe_dump(self.ledger), encoding='utf-8')

    def validate(self):
        return _validate_v2_grounding(self.quality, self.package, self.draft, self.root, 'Build billing APIs.')

    def test_new_cv_rejects_missing_role_inventory(self):
        with self.assertRaisesRegex(ApplicationError, 'role_coverage'):
            self.validate()

    def test_new_metric_claim_cannot_reuse_a_number_for_a_different_measure(self):
        text = 'Example Backend Engineer reduced team onboarding time by 35%.'
        self.source.write_text(text, encoding='utf-8')
        bank = bootstrap_evidence_bank(self.root, [dict(id='onboarding', source=dict(path='registry/candidate/linkedin-profile.md', quote=text))])
        bank['entries'][0].update(status='verified', verification=dict(reviewer='editor', reviewed_at='2026-10-15', method='review'))
        bank['entries'][0]['measurements'] = [dict(id='time', value='35%', measure='onboarding time', unit='%', scope='team',
            baseline=None, period=None, method=None, quote=text)]
        claim = 'Reduced latency by 35%.'
        ledger = dict(schema_version=1, claims=[dict(document='cover-letter', text=claim, evidence_ids=['onboarding'],
            measurements=[dict(evidence_id='onboarding', measurement_id='time', claim_quote=claim)])])
        with self.assertRaisesRegex(EvidenceError, 'measurement.*measure'):
            validate_claims_ledger(ledger, bank, dict(cover_letter_markdown=claim), self.root)

    def test_letter_requires_review_of_exact_final_text(self):
        from tests.test_applications import ApplicationTests
        fixture = ApplicationTests()
        fixture.setUp()
        self.addCleanup(fixture.temp.cleanup)
        self.addCleanup(fixture.doCleanups)
        draft, package, quality = fixture.v2_letter_draft()
        quality['schema_version'] = 3
        quality['preparation_context_version'] = load_preparation_context(fixture.project).version
        with self.assertRaisesRegex(ApplicationError, 'letter.*review'):
            _validate_v2_grounding(quality, package, draft, fixture.project, 'Build Go services.')

    def valid_cv(self):
        self.ledger['schema_version'] = 2
        for claim in self.ledger['claims']:
            claim['support'] = {field: dict(evidence_id=claim['evidence_ids'][0], quote=claim['text'])
                                for field in ('contribution', 'scope', 'consequence')}
        self.save()
        audit = self.quality['cv_audit']
        audit['editorial_review']['author'] = 'cv-author'
        audit['role_coverage'] = [dict(employer='Example', decision='include', source_period=dict(start=[2022, 1], end=None),
            heading='Example — Backend Engineer | January 2022 - Present', reason='Relevant billing delivery',
            reviewer='independent-editor', sources=[dict(path='registry/candidate/linkedin-profile.md',
                quote='Example\nBackend Engineer\nJanuary 2022 - Present', sha256=hashlib.sha256(self.source.read_text(encoding='utf-8').encode()).hexdigest())])]
        return audit

    def test_valid_qualitative_cv_passes_and_retains_inventory(self):
        audit = self.valid_cv()
        receipt = self.validate()
        self.assertEqual(audit['role_coverage'], receipt['application_review']['role_coverage'])
        self.assertEqual(self.bullets[0], receipt['claims'][0]['text'])

    def test_cv_editorial_policy_comes_from_the_bound_project(self):
        self.valid_cv()
        self.validate()
        path = self.root / 'config/cv-editorial-knowledge.yaml'
        policy = yaml.safe_load(path.read_text(encoding='utf-8'))
        policy['rejected_anti_patterns'].append(dict(id='alternate-project-rule', regex=r'(?i)\bself-service\b'))
        path.write_text(yaml.safe_dump(policy), encoding='utf-8')
        self.quality['preparation_context_version'] = load_preparation_context(self.root).version
        with self.assertRaisesRegex(ApplicationError, 'alternate-project-rule'):
            self.validate()

    def test_inventory_detects_unreviewed_omission_wrong_dates_and_headings(self):
        for field, value, message in [('reviewer', 'unreviewed', 'reviewed'), ('source_period', dict(start=[2023, 1], end=None), 'stale source dates'),
                ('heading', 'Another employer', 'absent from final CV'), ('decision', 'exclude', 'career policy')]:
            with self.subTest(field=field):
                audit = self.valid_cv()
                audit['role_coverage'][0][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_role_inventory(audit, self.package['cv_markdown'], self.root)

    def test_inventory_detects_new_source_employer_and_actual_cv_omission(self):
        audit = self.valid_cv()
        original = self.source.read_text(encoding='utf-8')
        self.source.write_text(original.replace('## Education', '### Beta\nEngineer\nJanuary 2019 - January 2021\n## Education'), encoding='utf-8')
        audit['role_coverage'][0]['sources'][0]['sha256'] = hashlib.sha256(self.source.read_text(encoding='utf-8').encode()).hexdigest()
        cv = self.package['cv_markdown'].replace('## Education', '### Beta — Engineer | January 2019 - January 2021\n\n## Education')
        with self.assertRaisesRegex(ValueError, 'omits source employers'):
            validate_role_inventory(audit, cv, self.root)
        with self.assertRaisesRegex(ValueError, 'missing a dated employer entry'):
            validate_role_inventory(audit, self.package['cv_markdown'], self.root)

    def letter_fixture(self):
        from tests.test_applications import ApplicationTests
        fixture = ApplicationTests()
        fixture.setUp()
        self.addCleanup(fixture.temp.cleanup)
        self.addCleanup(fixture.doCleanups)
        draft, package, quality = fixture.v2_letter_draft()
        add_letter_review(fixture.project, draft, quality, package)
        ledger = yaml.safe_load((draft / 'claims.yaml').read_text(encoding='utf-8'))
        return fixture.project, draft, quality, package, ledger

    def test_one_example_supports_two_letter_strands(self):
        root, draft, quality, package, ledger = self.letter_fixture()
        receipt = _validate_v2_grounding(quality, package, draft, root, 'Build Go services.')
        self.assertEqual(1, len(receipt['application_review']['letter_review']['narrated_examples']))
        quality['cover_letter']['channel'] = 'email'
        quality['cover_letter']['editorial_review']['basis_sha256'] = review_digest(letter_basis(quality))
        validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger)

    def test_company_fact_can_be_translated_with_an_explicit_source_mapping(self):
        root, draft, quality, package, ledger = self.letter_fixture()
        review = quality['cover_letter']['editorial_review']
        translation = 'Example sviluppa software di fatturazione.'
        package['cover_letter_markdown'] = package['cover_letter_markdown'].replace(review['company_claim'], translation)
        review.update(company_claim=translation, document_sha256=digest(package['cover_letter_markdown']),
                      company_grounding='The Italian sentence preserves the captured fact about billing software.')
        review['voice']['language'] = 'Italian'
        validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger)
        review.pop('company_grounding')
        with self.assertRaisesRegex(ValueError, 'source-to-final-text'):
            validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger)


    def test_letter_text_basis_company_and_voice_changes_invalidate_review(self):
        for mutation, message in [('text', 'final text'), ('basis', 'priorities'), ('company', 'snapshot is stale'), ('voice', 'voice review is stale')]:
            with self.subTest(mutation=mutation):
                root, draft, quality, package, ledger = self.letter_fixture()
                if mutation == 'text':
                    package['cover_letter_markdown'] += 'Later edit.\n'
                elif mutation == 'basis':
                    quality['cover_letter']['evidence_stories'][0]['requirement'] = 'Other'
                elif mutation == 'company':
                    (draft / 'parts/company-source.txt').write_text('Changed source', encoding='utf-8')
                else:
                    (root / 'config/social-voice.md').write_text('Changed voice', encoding='utf-8')
                with self.assertRaisesRegex(ValueError, message):
                    validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger)

    def test_priority_mapping_cannot_refer_to_unrelated_or_duplicate_points(self):
        for field, value, message in [('requirement', 'Invented', 'real requirement'), ('point', 'Backend delivery', 'distinct points'),
                ('letter_quote', 'Not in final letter', 'anchor a final')]:
            with self.subTest(field=field):
                root, draft, quality, package, ledger = self.letter_fixture()
                quality['cover_letter']['editorial_review']['priority_mapping'][1][field] = value
                with self.assertRaisesRegex(ValueError, message):
                    validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger)

    def test_email_rejects_two_narrated_examples_even_with_two_valid_strands(self):
        root, draft, quality, package, ledger = self.letter_fixture()
        letter = quality['cover_letter']
        letter['channel'] = 'email'
        letter['editorial_review']['basis_sha256'] = review_digest(letter_basis(quality))
        letter['editorial_review']['narrated_examples'] *= 2
        with self.assertRaisesRegex(ValueError, 'channel limit'):
            validate_letter_review(quality, package['cover_letter_markdown'], draft, root, ledger)

    def test_lint_reports_missing_letter_review_before_publication(self):
        from jobintel.application_lint import lint_application_draft
        root, draft, quality, package, ledger = self.letter_fixture()
        directory = next((root / 'registry/jobs').iterdir())
        receipt = lint_application_draft(directory, draft, document='cover-letter', vacancy_text='Build Go services.')
        self.assertTrue(receipt['ok'], receipt['diagnostics'])
        quality['cover_letter'].pop('editorial_review')
        (draft / 'quality.yaml').write_text(yaml.safe_dump(quality), encoding='utf-8')
        receipt = lint_application_draft(directory, draft, document='cover-letter', vacancy_text='Build Go services.')
        self.assertFalse(receipt['ok'])
        self.assertIn('LETTER_REVIEW', {item['code'] for item in receipt['diagnostics']})

    def test_new_contract_requires_measurement_aware_ledger(self):
        self.valid_cv()
        self.ledger['schema_version'] = 1
        self.save()
        with self.assertRaisesRegex(ApplicationError, 'claims ledger schema_version 2'):
            self.validate()

    def test_legacy_v2_is_inspectable_but_cannot_replace_an_existing_package(self):
        from jobintel.applications import ApplicationGenerator, CodexApplicationDraftClient, _validate_draft_quality
        from tests.test_applications import ApplicationTests, FakeConverter
        fixture = ApplicationTests()
        fixture.setUp()
        self.addCleanup(fixture.temp.cleanup)
        self.addCleanup(fixture.doCleanups)
        draft, package, quality = fixture.v2_letter_draft()
        (draft / 'cover-letter.md').write_text(package['cover_letter_markdown'], encoding='utf-8')
        old = fixture.directory / 'application/cover-letter.md'
        old.parent.mkdir()
        old.write_bytes(b'Existing exact sent artifact')
        receipt = _validate_draft_quality(draft, package, document='cover-letter', project_root=fixture.project, vacancy_text='Build Go services.')
        self.assertIn('Legacy contract 2', receipt['migration_note'])
        converter = FakeConverter()
        generator = ApplicationGenerator(fixture.registry_root, [fixture.profile], fixture.prompt,
            CodexApplicationDraftClient(draft, model='fixture', document='cover-letter'), converter, document='cover-letter')
        with self.assertRaisesRegex(ApplicationError, 'schema_version 3'):
            generator.generate_directory(fixture.directory)
        self.assertEqual(b'Existing exact sent artifact', old.read_bytes())
        self.assertEqual([], converter.calls)



if __name__ == '__main__':
    unittest.main()
