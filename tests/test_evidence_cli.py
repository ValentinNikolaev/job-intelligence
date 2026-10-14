from __future__ import annotations

import contextlib
import copy
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel.evidence import bootstrap_evidence_bank
from jobintel.evidence_cli import main
from jobintel.cli import main as root_main


class EvidenceCommandTests(unittest.TestCase):
    def test_context_questions_are_nonleading_selected_and_read_only(self):
        self.write('registry/evidence/achievements.yaml', self.bank)
        before = {str(path): path.read_bytes() for path in self.root.rglob('*') if path.is_file()}
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(['questions', '--id', 'php'], root=self.root)
        self.assertEqual(0, result)
        receipt = json.loads(output.getvalue())
        self.assertFalse(receipt['candidate_sources_changed'])
        self.assertTrue(all(row['evidence_id'] == 'php' for row in receipt['questions']))
        self.assertEqual({'problem', 'contribution', 'scope', 'decision', 'consequence', 'delivery_status', 'responsibility'}, {row['field'] for row in receipt['questions']})
        self.assertEqual(before, {str(path): path.read_bytes() for path in self.root.rglob('*') if path.is_file()})
        self.assertEqual(1, self.call('questions', '--id', 'unknown'))

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'registry/candidate').mkdir(parents=True)
        (self.root / '.codex-work').mkdir()
        (self.root / 'registry/candidate/cv.md').write_text('Example: Backend Engineer using PHP.\n', encoding='utf-8')
        self.extracts = [{'id': 'php', 'source': {'path': 'registry/candidate/cv.md', 'quote': 'Example: Backend Engineer using PHP.'}}]
        self.bank = bootstrap_evidence_bank(self.root, self.extracts)

    def write(self, name, value):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(yaml.safe_dump(value), encoding='utf-8')
        return path

    def call(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return main(list(args), root=self.root)

    def test_bootstrap_never_overwrites_confirmation_history(self):
        self.write('.codex-work/extracts.yaml', self.extracts)
        self.assertEqual(0, self.call('bootstrap', '--input', '.codex-work/extracts.yaml', '--output', '.codex-work/bank.yaml'))
        before = (self.root / '.codex-work/bank.yaml').read_bytes()
        self.assertEqual(1, self.call('bootstrap', '--input', '.codex-work/extracts.yaml', '--output', '.codex-work/bank.yaml'))
        self.assertEqual(before, (self.root / '.codex-work/bank.yaml').read_bytes())

    def test_cannot_confirm_cannot_be_laundered_into_verified(self):
        entry = self.bank['entries'][0]
        entry.update(status='cannot-confirm', reason='Candidate cannot establish ownership')
        self.write('registry/evidence/achievements.yaml', self.bank)
        revised = copy.deepcopy(self.bank)
        revised['entries'][0].update(status='verified', verification=dict(reviewer='test', reviewed_at='2026-09-22', method='review'))
        self.write('.codex-work/revised.yaml', revised)
        self.assertEqual(1, self.call('publish', '--input', '.codex-work/revised.yaml'))
        saved = yaml.safe_load((self.root / 'registry/evidence/achievements.yaml').read_text())
        self.assertEqual('cannot-confirm', saved['entries'][0]['status'])

    def test_source_tree_cannot_be_output(self):
        self.write('.codex-work/bank.yaml', self.bank)
        self.assertEqual(1, self.call('publish', '--input', '.codex-work/bank.yaml', '--output', 'registry/candidate/source.yaml'))
        self.assertFalse((self.root / 'registry/candidate/source.yaml').exists())

    def test_stale_source_prevents_publish(self):
        self.write('.codex-work/bank.yaml', self.bank)
        (self.root / 'registry/candidate/cv.md').write_text('Changed factual source', encoding='utf-8')
        self.assertEqual(1, self.call('publish', '--input', '.codex-work/bank.yaml'))
        self.assertFalse((self.root / 'registry/evidence/achievements.yaml').exists())

    def test_publish_then_validate(self):
        self.write('.codex-work/bank.yaml', self.bank)
        self.assertEqual(0, self.call('publish', '--input', '.codex-work/bank.yaml'))
        self.assertEqual(0, self.call('validate'))

    def test_cli_dispatch_preserves_subcommand_arguments(self):
        for command, module in [('evidence', 'evidence_cli'), ('documents', 'document_quality_cli'), ('applications', 'lifecycle_cli')]:
            with self.subTest(command=command), patch(f'jobintel.{module}.main', return_value=0) as handler:
                self.assertEqual(0, root_main([command, '--help']))
                self.assertEqual(['--help'], handler.call_args.args[0])


if __name__ == '__main__':
    unittest.main()
