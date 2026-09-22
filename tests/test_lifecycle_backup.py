from __future__ import annotations

import tempfile
import unittest
from datetime import date
from pathlib import Path

from jobintel.application_lifecycle import ApplicationLifecycle
from jobintel.backup import _validate_artifact_references, _validate_payload_references
from tests.test_application_lifecycle import MemoryStore


class LifecycleBackupTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.store = MemoryStore()
        source = self.root / 'registry/jobs/example-job/application/cv.md'
        source.parent.mkdir(parents=True)
        source.write_bytes(b'Exact submitted CV\n')
        service = ApplicationLifecycle(self.root, store=self.store, today=date(2026, 9, 23))
        self.event = service.record_submission('v1', submission_id='sent', sent_on='2026-09-01', artifacts=[source], confirmed=True)
        self.snapshot = {'collections': {'operational_logs': {'documents': self.store.list('operational_logs')}}}

    def test_backup_requires_exact_snapshot_and_receipt(self):
        receipt = _validate_artifact_references(self.snapshot, self.root)
        self.assertEqual(2, receipt['lifecycle_files'])
        self.assertEqual(2, len(receipt['_required']))
        payloads = {item['object']: (self.root / item['locator']).read_bytes() for item in receipt['_required']}
        _validate_payload_references(payloads, receipt['_required'])
        with self.assertRaisesRegex(ValueError, 'missing required reference'):
            _validate_payload_references({}, receipt['_required'])

    def test_changed_sent_file_blocks_backup(self):
        path = self.root / self.event['snapshot'] / self.event['artifacts'][0]['snapshot']
        path.write_bytes(b'Changed')
        with self.assertRaisesRegex(ValueError, 'snapshot differs'):
            _validate_artifact_references(self.snapshot, self.root)

    def test_forged_receipt_blocks_backup(self):
        path = self.root / self.event['snapshot'] / 'receipt.json'
        path.write_text('{}', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'receipt differs'):
            _validate_artifact_references(self.snapshot, self.root)


if __name__ == '__main__':
    unittest.main()
