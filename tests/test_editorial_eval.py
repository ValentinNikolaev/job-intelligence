import copy
import tempfile
import unittest
from pathlib import Path

from jobintel.editorial_eval import export_pack, evaluate_decisions


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

    def test_wrong_disposition_or_reason_code_fails(self):
        for field, value in [('decision', 'keep'), ('reason_codes', [])]:
            with self.subTest(field=field):
                answers = copy.deepcopy(self.answers)
                answers['decisions'][0][field] = value
                receipt = evaluate_decisions(self.root, answers)
                self.assertFalse(receipt['ok'])
                self.assertEqual('routine-repair', receipt['failures'][0]['id'])

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
