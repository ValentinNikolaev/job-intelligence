from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlparse


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "jobicy" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_jobicy_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
JobicyCollector = MODULE.JobicyCollector
normalize_job = MODULE.normalize_job
parse_api_response = MODULE.parse_api_response


class FakeResponse:
    def __init__(self, value: Any, *, raw: bool = False) -> None:
        self.payload = value if raw else json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def api_job(**overrides: Any) -> dict[str, Any]:
    value = {
        "id": 12345,
        "url": "https://jobicy.com/jobs/senior-backend-engineer",
        "jobTitle": "Senior Backend &amp; API Engineer",
        "companyName": "Acme",
        "companyLogo": "https://cdn.example.test/acme.png",
        "jobIndustry": ["Development", "Programming"],
        "jobType": "Full-time",
        "jobGeo": "Italy",
        "jobLevel": "Senior",
        "jobExcerpt": "Build reliable APIs.",
        "jobDescription": "<h2>Role</h2><p>Build the API.</p><p>Full description.</p>",
        "pubDate": "2026-07-21 10:30:00",
        "salaryMin": 70000,
        "salaryMax": 95000,
        "salaryCurrency": "eur",
        "salaryPeriod": "Yearly",
    }
    value.update(overrides)
    return value


class JobicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "jobicy.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, text: str) -> None:
        self.config_path.write_text(text, encoding="utf-8")

    def _config(self) -> dict[str, str]:
        return {"JOBICY_CONFIG": str(self.config_path)}

    def test_generates_queries_from_supported_profile_fields(self) -> None:
        self._write_config(
            """version: 1
timeout_seconds: 15
queries:
  - geo: italy
    industry: current-taxonomy-value
    tag: backend engineer
    count: 100
"""
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            parsed = urlparse(request.full_url)
            self.assertEqual("https", parsed.scheme)
            self.assertEqual("jobicy.com", parsed.netloc)
            self.assertEqual("/api/v2/remote-jobs", parsed.path)
            self.assertEqual(15.0, timeout)
            self.assertEqual(
                {
                    "geo": ["italy"],
                    "industry": ["current-taxonomy-value"],
                    "tag": ["backend engineer"],
                    "count": ["100"],
                },
                parse_qs(parsed.query),
            )
            return FakeResponse({"job-count": 0, "jobs": []})

        self.assertEqual([], list(JobicyCollector(self._config(), opener=opener).fetch()))

    def test_parses_response_jobs(self) -> None:
        jobs = parse_api_response({"job-count": 1, "jobs": [api_job()]})
        self.assertEqual(1, len(jobs))
        self.assertEqual("12345", jobs[0].source_job_id)

        with self.assertRaisesRegex(ValueError, "no jobs list"):
            parse_api_response({"job-count": 0})

    def test_normalizes_full_job_and_source_metadata(self) -> None:
        job = normalize_job(api_job())

        self.assertEqual("jobicy", job.source)
        self.assertEqual("12345", job.source_job_id)
        self.assertEqual("https://jobicy.com/jobs/senior-backend-engineer", job.source_url)
        self.assertEqual("Senior Backend & API Engineer", job.title)
        self.assertEqual("Acme", job.company)
        self.assertEqual("Italy", job.location)
        self.assertTrue(job.remote)
        self.assertEqual("Full-time", job.employment_type)
        self.assertEqual("2026-07-21T10:30:00Z", job.published_at)
        self.assertIn("## Role", job.description)
        self.assertIn("Full description.", job.description)
        self.assertEqual(
            "https://cdn.example.test/acme.png", job.source_metadata["company_logo"]
        )
        self.assertEqual(
            ["Development", "Programming"], job.source_metadata["industry"]
        )
        self.assertEqual("Senior", job.source_metadata["level"])
        self.assertEqual("Build reliable APIs.", job.source_metadata["excerpt"])

    def test_normalizes_salary_values(self) -> None:
        salary = normalize_job(
            api_job(salaryMin="70,000", salaryMax="95000.50")
        ).source_metadata["salary"]
        self.assertEqual(
            {
                "min": 70000,
                "max": 95000.5,
                "currency": "EUR",
                "period": "yearly",
            },
            salary,
        )

        undisclosed = normalize_job(
            api_job(
                salaryMin=None,
                salaryMax=None,
                salaryCurrency=None,
                salaryPeriod=None,
            )
        )
        self.assertNotIn("salary", undisclosed.source_metadata)

    def test_deduplicates_jobicy_id_across_query_profiles(self) -> None:
        self._write_config(
            """queries:
  - geo: italy
    count: 100
  - geo: europe
    tag: backend
    count: 100
"""
        )
        requested_geos: list[str] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            query = parse_qs(urlparse(request.full_url).query)
            requested_geos.append(query["geo"][0])
            return FakeResponse({"job-count": 1, "jobs": [api_job()]})

        jobs = list(JobicyCollector(self._config(), opener=opener).fetch())

        self.assertEqual(["italy", "europe"], requested_geos)
        self.assertEqual(1, len(jobs))
        self.assertEqual("12345", jobs[0].source_job_id)
        discoveries = jobs[0].source_metadata["discovered_by"]
        self.assertEqual([1, 2], [item["query_index"] for item in discoveries])

    def test_jobicy_id_is_stable_when_other_fields_change(self) -> None:
        first = normalize_job(api_job())
        changed = normalize_job(
            api_job(
                url="https://jobicy.com/jobs/renamed-role",
                jobTitle="Renamed role",
                pubDate=datetime.now(timezone.utc).isoformat(),
            )
        )
        self.assertEqual("12345", first.source_job_id)
        self.assertEqual(first.source_job_id, changed.source_job_id)

    def test_api_failure_is_reported_without_retry(self) -> None:
        self._write_config("queries:\n  - geo: italy\n    count: 100\n")
        attempts = 0

        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal attempts
            attempts += 1
            raise HTTPError(request.full_url, 503, "Unavailable", None, None)

        with self.assertRaisesRegex(RuntimeError, "Jobicy query 1 returned HTTP 503"):
            list(JobicyCollector(self._config(), opener=opener).fetch())
        self.assertEqual(1, attempts)

    def test_rejects_unknown_fields_and_invalid_count(self) -> None:
        self._write_config("queries:\n  - geo: italy\n    unsupported: value\n")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            JobicyCollector(self._config())

        self._write_config("queries:\n  - geo: italy\n    count: 101\n")
        with self.assertRaisesRegex(ValueError, "1 to 100"):
            JobicyCollector(self._config())


if __name__ == "__main__":
    unittest.main()
