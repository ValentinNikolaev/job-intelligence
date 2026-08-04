from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "cleanjobdata" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_cleanjobdata_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
CleanJobDataCollector = MODULE.CleanJobDataCollector


class FakeResponse:
    def __init__(self, value: dict[str, Any]) -> None:
        self.payload = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class CleanJobDataTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "cleanjobdata.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, text: str) -> None:
        self.config_path.write_text(text, encoding="utf-8")

    def _config(self) -> dict[str, str]:
        return {
            "CLEANJOBDATA_API_KEY": "test-key",
            "CLEANJOBDATA_CONFIG": str(self.config_path),
        }

    def test_fetches_pages_normalizes_and_deduplicates(self) -> None:
        self._write_config(
            """version: 1
request_budget: 3
limit: 2
min_request_interval_seconds: 0
search_profiles:
  - name: backend-italy
    search: python developer
    location: IT
    remote: true
    max_age: 7d
    sort_by: relevance
    max_pages: 2
"""
        )
        pages = {
            None: {
                "data": [
                    {
                        "id": 101,
                        "title": "Python &amp; API Developer",
                        "description": "<p>Fully remote role.</p>",
                        "published": "2026-08-01T10:00:00Z",
                        "application_url": "https://jobs.example.test/101",
                        "location": "Rome, IT; Remote",
                        "has_remote": True,
                        "remote_type": "fully_remote",
                        "employment_type": "FULL_TIME",
                        "salary_min": 100000,
                        "salary_currency": "EUR",
                        "company": {
                            "name": "Acme S.r.l.",
                            "website_url": "https://acme.example",
                            "description": "Builds APIs.",
                            "industry": "SaaS",
                        },
                    },
                    {
                        "id": "102",
                        "title": "Platform Engineer",
                        "description": "Build systems.",
                        "application_url": "https://jobs.example.test/102",
                        "locations": [{"display_label": "Milan, IT"}],
                        "company": {"name": "Widgets"},
                    },
                ],
                "pagination": {"limit": 2, "next_page": "cursor-2"},
            },
            "cursor-2": {
                "data": [
                    {
                        "id": "102",
                        "title": "Platform Engineer",
                        "description": "Duplicate result.",
                        "application_url": "https://jobs.example.test/102",
                        "company": {"name": "Widgets"},
                    }
                ],
                "pagination": {"limit": 2, "next_page": None},
            },
        }
        requested_cursors: list[str | None] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            self.assertEqual("Bearer test-key", request.get_header("Authorization"))
            self.assertEqual(30.0, timeout)
            parsed = urlparse(request.full_url)
            self.assertEqual("https://api.cleanjobdata.com/jobs", f"{parsed.scheme}://{parsed.netloc}{parsed.path}")
            parameters = parse_qs(parsed.query)
            cursor = parameters.get("cursor", [None])[0]
            requested_cursors.append(cursor)
            self.assertEqual(["python developer"], parameters["search"])
            self.assertEqual(["IT"], parameters["location"])
            self.assertEqual(["true"], parameters["remote"])
            self.assertEqual(["description"], parameters["extra_fields"])
            self.assertEqual(["2"], parameters["limit"])
            return FakeResponse(pages[cursor])

        collector = CleanJobDataCollector(self._config(), opener=opener, sleep=lambda _: None)
        jobs = list(collector.fetch())

        self.assertEqual([None, "cursor-2"], requested_cursors)
        self.assertEqual(["101", "102"], [job.source_job_id for job in jobs])
        self.assertEqual("Python & API Developer", jobs[0].title)
        self.assertEqual("Acme S.r.l.", jobs[0].company)
        self.assertEqual("https://acme.example", jobs[0].company_url)
        self.assertEqual("FULL_TIME", jobs[0].employment_type)
        self.assertTrue(jobs[0].remote)
        self.assertEqual("SaaS", jobs[0].source_metadata["company_industry"])
        self.assertEqual("Milan, IT", jobs[1].location)

    def test_profiles_are_round_robin_under_global_budget(self) -> None:
        self._write_config(
            """request_budget: 3
limit: 1
max_pages_per_profile: 5
min_request_interval_seconds: 0
search_profiles:
  - name: italy
    search: python
    location: IT
  - name: uk
    search: golang
    location: GB
"""
        )
        requests: list[str] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            parameters = parse_qs(urlparse(request.full_url).query)
            location = parameters["location"][0]
            cursor = parameters.get("cursor", ["1"])[0]
            requests.append(f"{location}-{cursor}")
            return FakeResponse(
                {
                    "data": [{
                        "id": f"{location}-{cursor}",
                        "title": "Engineer",
                        "description": "Role",
                        "application_url": f"https://example.test/{location}/{cursor}",
                    }],
                    "pagination": {"next_page": f"{int(cursor) + 1}"},
                }
            )

        jobs = list(CleanJobDataCollector(self._config(), opener=opener, sleep=lambda _: None).fetch())
        self.assertEqual(3, len(jobs))
        self.assertEqual(["IT-1", "GB-1", "IT-2"], requests)

    def test_disabled_profiles_and_unknown_fields(self) -> None:
        self._write_config(
            """search_profiles:
  - name: disabled
    enabled: false
    search: python
  - name: enabled
    search: golang
"""
        )
        collector = CleanJobDataCollector(self._config(), opener=lambda *args, **kwargs: self.fail("request made"))
        self.assertEqual(["enabled"], [profile.name for profile in collector.profiles])

        self._write_config("search_profiles:\n  - name: bad\n    search: python\n    unsupported: value\n")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            CleanJobDataCollector(self._config())

    def test_zero_budget_performs_no_requests(self) -> None:
        self._write_config("request_budget: 0\nsearch_profiles:\n  - name: python\n    search: python\n")
        collector = CleanJobDataCollector(
            self._config(), opener=lambda *args, **kwargs: self.fail("request made")
        )
        self.assertEqual([], list(collector.fetch()))


if __name__ == "__main__":
    unittest.main()
