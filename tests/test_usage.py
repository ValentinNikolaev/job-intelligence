from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from jobintel.usage import CodexUsageLog, UsageError


class UsageTests(unittest.TestCase):
    def test_records_reported_run_and_derives_total(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "registry" / "codex-usage.yaml"
            run = CodexUsageLog(path).record(
                workflow="prepare-priority",
                model="codex:test",
                run_id="run-1",
                input_tokens=100,
                output_tokens=25,
                credits=0.5,
            )
            self.assertEqual("prepare_priority", run["workflow"])
            self.assertEqual(125, run["total_tokens"])
            stored = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertEqual("run-1", stored["runs"][0]["run_id"])

    def test_rejects_negative_usage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            with self.assertRaises(UsageError):
                CodexUsageLog(Path(temporary) / "usage.yaml").record(
                    workflow="analyze", model="codex:test", input_tokens=-1
                )


if __name__ == "__main__":
    unittest.main()
