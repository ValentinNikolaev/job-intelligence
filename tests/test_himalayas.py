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

from jobintel.registry import Registry


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "himalayas" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_himalayas_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
HimalayasCollector = MODULE.HimalayasCollector
normalize_job = MODULE.normalize_job


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
        "title": "Senior Backend Engineer",
        "excerpt": "Build reliable APIs.",
        "companyName": "Acme",
        "companySlug": "acme",
        "companyLogo": "https://cdn.example.test/acme.png",
        "employmentType": "Full Time",
        "seniority": ["Senior"],
        "locationRestrictions": [
            {"alpha2": "IT", "name": "Italy", "slug": "italy"},
            {"alpha2": "DE", "name": "Germany", "slug": "germany"},
        ],
        "timezoneRestrictions": ["UTC+1", "UTC+2"],
        "categories": ["Backend", "Python"],
        "parentCategories": ["Engineering"],
        "minSalary": 70000,
        "maxSalary": 95000,
        "salaryPeriod": "annual",
        "currency": "EUR",
        "description": "<h2>Role</h2><p>Build the API.</p><p>Full description.</p>",
        "pubDate": 1784649600000,
        "expiryDate": 1787241600000,
        "applicationLink": "https://himalayas.app/jobs/acme/senior-backend-engineer",
        "guid": "acme-senior-backend-engineer-123",
    }
    value.update(overrides)
    return value


class HimalayasTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "himalayas.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, text: str) -> None:
        self.config_path.write_text(text, encoding="utf-8")

    def _config(self) -> dict[str, str]:
        return {"HIMALAYAS_CONFIG": str(self.config_path)}

    def test_constructs_search_query_from_supported_filters(self) -> None:
        self._write_config(
            """version: 1
max_pages_per_query: 2
queries:
  - q: backend engineer
    country: IT
    worldwide: false
    exclude_worldwide: true
    seniority: [Senior, Manager]
    employment_type: Full Time
    company: [acme, widgets]
    timezone: UTC+01:00
    sort: recent
"""
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            parsed = urlparse(request.full_url)
            self.assertEqual("https", parsed.scheme)
            self.assertEqual("himalayas.app", parsed.netloc)
            self.assertEqual("/jobs/api/search", parsed.path)
            self.assertEqual(30.0, timeout)
            self.assertEqual(
                {
                    "q": ["backend engineer"],
                    "country": ["IT"],
                    "worldwide": ["false"],
                    "exclude_worldwide": ["true"],
                    "seniority": ["Senior,Manager"],
                    "employment_type": ["Full Time"],
                    "company": ["acme,widgets"],
                    "timezone": ["UTC+01:00"],
                    "sort": ["recent"],
                    "page": ["1"],
                },
                parse_qs(parsed.query),
            )
            return FakeResponse({"offset": 0, "limit": 20, "totalCount": 0, "jobs": []})

        self.assertEqual([], list(HimalayasCollector(self._config(), opener=opener).fetch()))

    def test_paginates_until_total_count_is_reached(self) -> None:
        self._write_config("max_pages_per_query: 5\nqueries:\n  - q: backend\n")
        requested_pages: list[int] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            page = int(parse_qs(urlparse(request.full_url).query)["page"][0])
            requested_pages.append(page)
            offset = (page - 1) * 2
            jobs = [
                api_job(
                    guid=f"job-{offset + index}",
                    applicationLink=f"https://himalayas.app/jobs/job-{offset + index}",
                )
                for index in range(1, 3 if page < 3 else 2)
            ]
            return FakeResponse(
                {"offset": offset, "limit": 2, "totalCount": 5, "jobs": jobs}
            )

        jobs = list(HimalayasCollector(self._config(), opener=opener).fetch())

        self.assertEqual([1, 2, 3], requested_pages)
        self.assertEqual(5, len(jobs))

    def test_per_query_max_pages_stops_full_result_pages(self) -> None:
        self._write_config(
            "max_pages_per_query: 5\nqueries:\n  - q: backend\n    max_pages: 2\n"
        )
        requested_pages: list[int] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            page = int(parse_qs(urlparse(request.full_url).query)["page"][0])
            requested_pages.append(page)
            return FakeResponse(
                {
                    "offset": (page - 1) * 2,
                    "limit": 2,
                    "totalCount": 100,
                    "jobs": [
                        api_job(
                            guid=f"job-{page}-{index}",
                            applicationLink=f"https://himalayas.app/jobs/job-{page}-{index}",
                        )
                        for index in range(2)
                    ],
                }
            )

        self.assertEqual(
            4, len(list(HimalayasCollector(self._config(), opener=opener).fetch()))
        )
        self.assertEqual([1, 2], requested_pages)

    def test_parses_location_restrictions_and_worldwide_jobs(self) -> None:
        restricted = normalize_job(api_job())
        worldwide = normalize_job(
            api_job(
                guid="worldwide-1",
                applicationLink="https://himalayas.app/jobs/worldwide-1",
                locationRestrictions=[],
            )
        )

        self.assertEqual("Italy, Germany", restricted.location)
        self.assertTrue(restricted.remote)
        self.assertEqual("IT", restricted.source_metadata["location_restrictions"][0]["alpha2"])
        self.assertEqual("Worldwide", worldwide.location)
        self.assertEqual([], worldwide.source_metadata["location_restrictions"])

    def test_parses_salary_fields_with_period_and_currency(self) -> None:
        salary = normalize_job(api_job()).source_metadata["salary"]
        self.assertEqual(
            {"period": "annual", "min": 70000, "max": 95000, "currency": "EUR"},
            salary,
        )

        undisclosed = normalize_job(
            api_job(
                guid="no-salary",
                applicationLink="https://himalayas.app/jobs/no-salary",
                minSalary=None,
                maxSalary=None,
            )
        )
        self.assertNotIn("salary", undisclosed.source_metadata)

    def test_normalizes_full_job_and_preserves_attribution_metadata(self) -> None:
        job = normalize_job(api_job())

        self.assertEqual("himalayas", job.source)
        self.assertEqual("acme-senior-backend-engineer-123", job.source_job_id)
        self.assertEqual(
            "https://himalayas.app/jobs/acme/senior-backend-engineer", job.source_url
        )
        self.assertEqual("Acme", job.company)
        self.assertEqual("Full Time", job.employment_type)
        self.assertIn("## Role", job.description)
        self.assertIn("Full description.", job.description)
        self.assertEqual(
            datetime.fromtimestamp(1784649600, timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            job.published_at,
        )
        self.assertEqual("acme", job.source_metadata["company_slug"])
        self.assertEqual(["Backend", "Python"], job.source_metadata["categories"])
        self.assertEqual(["UTC+1", "UTC+2"], job.source_metadata["timezone_restrictions"])
        self.assertIn("expiry_at", job.source_metadata)

    def test_deduplicates_across_queries_and_records_every_discovery(self) -> None:
        self._write_config(
            """max_pages_per_query: 1
queries:
  - q: backend engineer
    country: IT
  - q: golang
    worldwide: true
"""
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            return FakeResponse(
                {"offset": 0, "limit": 20, "totalCount": 1, "jobs": [api_job()]}
            )

        collector = HimalayasCollector(self._config(), opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(1, len(jobs))
        discoveries = jobs[0].source_metadata["discovered_by"]
        self.assertEqual([1, 2], [item["query_index"] for item in discoveries])
        self.assertEqual("backend engineer", discoveries[0]["parameters"]["q"])
        self.assertEqual("golang", discoveries[1]["parameters"]["q"])

        registry = Registry(Path(self.temp.name) / "registry")
        self.assertEqual(["created"], [registry.upsert(job).status for job in jobs])
        rerun = [registry.upsert(job).status for job in collector.fetch()]
        self.assertEqual(["unchanged"], rerun)
        self.assertEqual(1, len(list(registry.jobs_dir.glob("*/meta.yaml"))))

    def test_retries_http_429_then_fails_clearly(self) -> None:
        self._write_config("max_pages_per_query: 1\nqueries:\n  - q: backend\n")
        attempts = 0
        sleeps: list[float] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal attempts
            attempts += 1
            raise HTTPError(request.full_url, 429, "Too Many Requests", None, None)

        collector = HimalayasCollector(
            self._config(), opener=opener, sleep=sleeps.append
        )
        with self.assertRaisesRegex(RuntimeError, "HTTP 429 after retries"):
            list(collector.fetch())
        self.assertEqual(3, attempts)
        self.assertEqual([1, 2], sleeps)

    def test_rejects_managed_page_and_unknown_query_fields(self) -> None:
        self._write_config("queries:\n  - q: backend\n    page: 3\n")
        with self.assertRaisesRegex(ValueError, "managed by the collector"):
            HimalayasCollector(self._config())

        self._write_config("queries:\n  - q: backend\n    unsupported: value\n")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            HimalayasCollector(self._config())


if __name__ == "__main__":
    unittest.main()
