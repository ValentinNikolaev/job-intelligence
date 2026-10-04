from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

from jobintel import cli
from jobintel.preparation_timing import main, record_event, report, timed_call


class PreparationTimingTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)

    def test_independent_events_aggregate_by_vacancy_and_stage(self) -> None:
        started = datetime.now(timezone.utc)
        record_event(self.root, "preview", started, 1.25, vacancy="a")
        record_event(self.root, "preview", started, 2.5, vacancy="a")
        record_event(self.root, "preview", started, 3, vacancy="b")
        result = report(self.root)
        self.assertEqual(3, len(result["events"]))
        self.assertEqual(3.75, result["totals_seconds"]["a:preview"])
        self.assertEqual(3, result["totals_seconds"]["b:preview"])
        self.assertEqual(result, json.loads((self.root / ".codex-work" / "preparation-timing.json").read_text()))

    def test_timed_call_records_failure_without_changing_exception(self) -> None:
        def fail() -> None:
            raise RuntimeError("conversion failed")

        with self.assertRaisesRegex(RuntimeError, "conversion failed"):
            timed_call(self.root, "conversion", "a", fail)
        self.assertEqual("error", report(self.root)["events"][0]["status"])

    def test_preparation_cli_records_validation_in_fixture_workspace(self) -> None:
        registry = self.root / "registry"
        registry.mkdir()
        with patch("jobintel.cli._main", return_value=0):
            self.assertEqual(0, cli.main(["validate-application", "vacancy", "--registry", str(registry)]))
        event = report(self.root)["events"][0]
        self.assertEqual("validation", event["stage"])
        self.assertEqual("vacancy", event["vacancy"])

    def test_manual_editorial_stage_requires_matching_start_and_stop(self) -> None:
        with redirect_stdout(io.StringIO()):
            self.assertEqual(0, main(["start", "editorial_drafting", "--vacancy", "a"], root=self.root))
            self.assertEqual(1, main(["start", "editorial_drafting", "--vacancy", "a"], root=self.root))
            self.assertEqual(0, main(["stop", "editorial_drafting", "--vacancy", "a"], root=self.root))
        events = report(self.root)["events"]
        self.assertEqual(1, len(events))
        self.assertEqual("editorial_drafting", events[0]["stage"])
        self.assertGreaterEqual(events[0]["elapsed_seconds"], 0)
