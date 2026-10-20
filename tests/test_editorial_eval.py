import copy
import tempfile
import shutil
import unittest
from pathlib import Path

from jobintel.editorial_eval import POLICY_FILES, export_pack, evaluate_decisions


class EditorialEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.pack = export_pack(self.root)
        import yaml
        self.corpus = yaml.safe_load((self.root / 'tests/fixtures/editorial-corpus.yaml').read_text(encoding='utf-8'))
        self.answers = dict(schema_version=1, reviewer='fixture evaluator', corpus_sha256=self.pack['corpus_sha256'],
            policy_sha256=self.pack['policy_sha256'], decisions=[dict(id=case['id'], decision=case['expected']['decision'],
                reason_codes=case['expected']['reason_codes'], reason=case['expected']['rationale'], source_quotes=[case['source']]) for case in self.corpus['cases']])

    def test_blind_pack_has_no_answer_keys(self):
        self.assertEqual(10, len(self.pack['cases']))
        self.assertTrue(all('expected' not in case for case in self.pack['cases']))
        self.assertTrue(evaluate_decisions(self.root, self.answers)['ok'])

    def test_matching_prompt_and_policy_are_bound_to_editorial_receipt(self):
        self.assertIn('prompts/vacancy-match.md', POLICY_FILES)
        self.assertIn('config/matching-policy.yaml', POLICY_FILES)
        self.assertEqual((self.root / 'prompts/vacancy-match.md').read_text(encoding='utf-8'),
                         self.pack['policies']['prompts/vacancy-match.md'])
        self.assertEqual((self.root / 'config/matching-policy.yaml').read_text(encoding='utf-8'),
                         self.pack['policies']['config/matching-policy.yaml'])

    def test_wrong_disposition_or_reason_code_fails(self):
        for field, value in [('decision', 'keep'), ('reason_codes', [])]:
            with self.subTest(field=field):
                answers = copy.deepcopy(self.answers)
                answers['decisions'][0][field] = value
                receipt = evaluate_decisions(self.root, answers)
                self.assertFalse(receipt['ok'])
                self.assertEqual('routine-repair', receipt['failures'][0]['id'])

    def test_effective_preparation_policy_is_bound_without_contact_data_or_source_reads(self):
        import yaml
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in (*POLICY_FILES, 'tests/fixtures/editorial-corpus.yaml',
                         'config/application-profile.yaml', 'config/application-review.yaml'):
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(self.root / name, path)
            pack = export_pack(root)
            self.assertEqual(self.pack['policy_sha256'], pack['policy_sha256'])
            self.assertNotIn('email:', pack['policies']['config/application-profile.yaml#preparation'])
            path = root / 'config/application-profile.yaml'
            profile = yaml.safe_load(path.read_text(encoding='utf-8'))
            profile['candidate']['full_name'] = 'Unrelated contact-only edit'
            path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding='utf-8')
            self.assertEqual(pack['policy_sha256'], export_pack(root)['policy_sha256'])
            profile['preparation']['career_scope']['maximum_years_since_end'] -= 1
            path.write_text(yaml.safe_dump(profile, sort_keys=False), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'stale'):
                evaluate_decisions(root, self.answers)

    def test_missing_duplicate_fabricated_and_stale_results_are_rejected(self):
        for mutation in ('missing', 'duplicate', 'fabricated', 'stale'):
            with self.subTest(mutation=mutation):
                answers = copy.deepcopy(self.answers)
                if mutation == 'missing':
                    answers['decisions'].pop()
                elif mutation == 'duplicate':
                    answers['decisions'][1]['id'] = answers['decisions'][0]['id']
                elif mutation == 'fabricated':
                    answers['decisions'][0]['source_quotes'] = ['Not in input']
                else:
                    answers['policy_sha256'] = 'outdated'
                with self.assertRaises(ValueError):
                    evaluate_decisions(self.root, answers)
