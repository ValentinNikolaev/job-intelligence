from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

import yaml

from discovery.ashby.discovery import AshbyBoardDiscovery
from jobintel.ashby_boards import (
    AshbyBoard,
    AshbyBoardRegistry,
    AshbyFilters,
    extract_board_name,
)


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "ashby" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_ashby_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
AshbyCollector = MODULE.AshbyCollector
parse_board_response = MODULE.parse_board_response


class FakeResponse:
    def __init__(self, value: Any) -> None:
        self.payload = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def api_job(**overrides: Any) -> dict[str, Any]:
    value = {
        "id": "job-1",
        "title": "Backend Engineer",
        "location": "Milan, Italy",
        "secondaryLocations": [{"location": "Rome, Italy"}],
        "department": "Engineering",
        "team": "Platform",
        "isRemote": True,
        "workplaceType": "Hybrid",
        "descriptionPlain": "Build the public API.",
        "descriptionHtml": "<p>HTML fallback.</p>",
        "publishedAt": "2026-07-20T09:00:00Z",
        "employmentType": "FullTime",
        "jobUrl": "https://jobs.ashbyhq.com/acme/job-1",
        "applyUrl": "https://jobs.ashbyhq.com/acme/job-1/application",
        "compensation": {"summaryComponents": [{"compensationType": "Salary"}]},
        "isListed": True,
    }
    value.update(overrides)
    return value


class AshbyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "ashby.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, boards: list[dict[str, str]]) -> None:
        self.config_path.write_text(
            yaml.safe_dump({"version": 1, "timeout_seconds": 12, "boards": boards}),
            encoding="utf-8",
        )

    def test_extracts_board_name_from_job_url(self) -> None:
        self.assertEqual(
            "satispay",
            extract_board_name("https://jobs.ashbyhq.com/satispay/some-job-id?ref=search"),
        )

    def test_rejects_invalid_and_non_ashby_urls(self) -> None:
        invalid = (
            "https://example.com/satispay/job",
            "http://jobs.ashbyhq.com/satispay/job",
            "https://jobs.ashbyhq.com/",
            "https://jobs.ashbyhq.com/bad%20board/job",
        )
        for value in invalid:
            with self.subTest(value=value), self.assertRaises(ValueError):
                extract_board_name(value)

    def test_board_registry_deduplicates_case_insensitively(self) -> None:
        registry = AshbyBoardRegistry(self.config_path)
        self.assertTrue(registry.add(AshbyBoard("Satispay", "Satispay")))
        self.assertFalse(registry.add(AshbyBoard("satispay")))
        registry.save()
        loaded = AshbyBoardRegistry.load(self.config_path)
        self.assertEqual(["Satispay"], [board.name for board in loaded.boards])
        self.assertEqual("Satispay", loaded.boards[0].company)

    def test_parses_response_and_skips_unlisted_jobs(self) -> None:
        jobs = parse_board_response(
            AshbyBoard("acme", "Acme"),
            {"jobs": [api_job(), api_job(id="hidden", isListed=False)]},
        )
        self.assertEqual(1, len(jobs))
        self.assertEqual("job-1", jobs[0].source_job_id)

    def test_normalizes_common_fields_and_preserves_source_metadata(self) -> None:
        job = parse_board_response(AshbyBoard("acme", "Acme"), {"jobs": [api_job()]})[0]
        self.assertEqual("ashby", job.source)
        self.assertEqual("Acme", job.company)
        self.assertEqual("Build the public API.", job.description)
        self.assertEqual("Milan, Italy", job.location)
        self.assertTrue(job.remote)
        self.assertEqual("FullTime", job.employment_type)
        self.assertEqual("2026-07-20T09:00:00Z", job.published_at)
        self.assertEqual(
            "https://jobs.ashbyhq.com/acme/job-1/application",
            job.source_metadata["application_url"],
        )
        self.assertEqual("Platform", job.source_metadata["team"])
        self.assertIn("compensation", job.source_metadata)

    def test_filters_remote_jobs_by_title_and_primary_or_secondary_location(self) -> None:
        filters = AshbyFilters(
            remote_only=True,
            location_terms=("Italy", "Europe"),
            title_terms=("backend", "platform engineer"),
        )
        jobs = parse_board_response(
            AshbyBoard("acme", "Acme"),
            {
                "jobs": [
                    api_job(id="italy", title="Backend Engineer"),
                    api_job(id="onsite", isRemote=False, workplaceType="OnSite"),
                    api_job(id="sales", title="Account Executive"),
                    api_job(id="usa", location="United States", secondaryLocations=[]),
                    api_job(
                        id="europe-secondary",
                        title="Platform Engineer",
                        location="Berlin Office",
                        secondaryLocations=[{"location": "Remote - Europe"}],
                    ),
                ]
            },
            filters,
        )
        self.assertEqual(["italy", "europe-secondary"], [job.source_job_id for job in jobs])

    def test_registry_preserves_global_filters_when_saved(self) -> None:
        self.config_path.write_text(
            """version: 1
timeout_seconds: 12
filters:
  remote_only: true
  location_terms: [Italy, Europe]
  title_terms: [backend, platform engineer]
boards:
  - name: satispay
    company: Satispay
""",
            encoding="utf-8",
        )
        registry = AshbyBoardRegistry.load(self.config_path)
        self.assertTrue(registry.filters.remote_only)
        self.assertEqual(("Italy", "Europe"), registry.filters.location_terms)
        registry.save()
        reloaded = AshbyBoardRegistry.load(self.config_path)
        self.assertEqual(registry.filters, reloaded.filters)

    def test_failing_board_does_not_stop_other_boards(self) -> None:
        self._write_config(
            [
                {"name": "broken", "company": "Broken"},
                {"name": "working", "company": "Working"},
            ]
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            self.assertEqual(12.0, timeout)
            if "/broken?" in request.full_url:
                raise HTTPError(request.full_url, 404, "Not Found", None, None)
            return FakeResponse(
                {"jobs": [api_job(jobUrl="https://jobs.ashbyhq.com/working/job-1")]}
            )

        collector = AshbyCollector({"ASHBY_CONFIG": str(self.config_path)}, opener=opener)
        jobs = list(collector.fetch())
        self.assertEqual(["Working"], [job.company for job in jobs])
        self.assertEqual(1, collector.errors)

    def test_discovery_validates_and_adds_only_valid_boards(self) -> None:
        self._write_config([])
        registry = AshbyBoardRegistry.load(self.config_path)

        def opener(request: Any, timeout: float) -> FakeResponse:
            if request.full_url.endswith("/invalid"):
                return FakeResponse({"error": "not found"})
            return FakeResponse({"jobs": []})

        result = AshbyBoardDiscovery(registry, opener=opener).discover(
            ["https://jobs.ashbyhq.com/acme/job-1", "invalid"]
        )
        self.assertEqual(["acme"], result.added)
        self.assertIn("invalid", result.invalid)
        self.assertTrue(AshbyBoardRegistry.load(self.config_path).contains("acme"))


if __name__ == "__main__":
    unittest.main()
