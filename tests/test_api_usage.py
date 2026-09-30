from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from jobintel.api_usage import ApiUsageLog
from jobintel.models import CollectorSummary


class ApiUsageLogTests(unittest.TestCase):
    def test_records_cumulative_requests_per_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "registry" / "source-api-usage.yaml"
            log = ApiUsageLog(path)
            first = CollectorSummary(source="adzuna", fetched=3, created=2, api_requests=2)
            second = CollectorSummary(source="adzuna", fetched=1, unchanged=1, api_requests=1)

            log.record(first, run_started_at="2026-07-23T10:00:00Z")
            log.record(second, run_started_at="2026-07-23T11:00:00Z")

            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            source = data["sources"]["adzuna"]
            self.assertEqual(3, source["total_requests"])
            self.assertEqual("completed", source["last_status"])
            self.assertEqual(2, len(source["runs"]))
            self.assertEqual(2, source["runs"][0]["requests"])
            self.assertEqual(1, source["runs"][1]["requests"])

    def test_records_multiple_sources_with_one_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "registry" / "source-api-usage.yaml"
            log = ApiUsageLog(path)
            summaries = [
                CollectorSummary(source="adzuna", fetched=3, api_requests=2),
                CollectorSummary(source="custom", fetched=8, api_requests=12, errors=1),
                CollectorSummary(source="empty", fetched=0, api_requests=0),
            ]

            log.record_many(summaries, run_started_at="2026-09-23T13:29:46Z")

            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            self.assertEqual({"adzuna", "custom"}, set(data["sources"]))
            self.assertEqual(2, data["sources"]["adzuna"]["total_requests"])
            self.assertEqual(12, data["sources"]["custom"]["total_requests"])
            self.assertEqual("failed", data["sources"]["custom"]["last_status"])
            self.assertEqual(
                "2026-09-23T13:29:46Z",
                data["sources"]["custom"]["runs"][0]["run_started_at"],
            )

    def test_skips_zero_request_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "registry" / "source-api-usage.yaml"
            ApiUsageLog(path).record(CollectorSummary(source="direct"))

            self.assertFalse(path.exists())


if __name__ == "__main__":
    unittest.main()
