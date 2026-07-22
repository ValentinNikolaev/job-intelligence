from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "jooble" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_jooble_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
JoobleCollector = MODULE.JoobleCollector


class FakeResponse:
    def __init__(self, value: dict[str, Any]) -> None:
        self.payload = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class JoobleTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "jooble.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, text: str) -> None:
        self.config_path.write_text(text, encoding="utf-8")

    def _config(self) -> dict[str, str]:
        return {
            "JOOBLE_API_KEY": "test-key",
            "JOOBLE_CONFIG": str(self.config_path),
        }

    def test_fetches_pages_normalizes_and_deduplicates(self) -> None:
        self._write_config(
            """version: 1
request_budget: 3
results_per_page: 2
query_profiles:
  - name: backend-italy
    keywords: python developer
    location: Italy
    radius: "80"
    company_search: false
"""
        )
        pages = {
            1: {
                "totalCount": 3,
                "jobs": [
                    {
                        "id": 101,
                        "title": "Python &amp; API Developer",
                        "snippet": "<p>Fully remote role.</p>",
                        "updated": "2026-07-21T10:00:00",
                        "link": "https://example.test/101",
                        "company": "Acme S.r.l.",
                        "location": "Roma, Lazio",
                        "type": "Full-time",
                    },
                    {
                        "id": "102",
                        "title": "Platform Engineer",
                        "snippet": "Build systems.",
                        "link": "https://example.test/102",
                        "company": "Widgets",
                        "location": "Milano",
                    },
                ],
            },
            2: {
                "totalCount": 3,
                "jobs": [
                    {
                        "id": "102",
                        "title": "Platform Engineer",
                        "snippet": "Duplicate result.",
                        "link": "https://example.test/102",
                    }
                ],
            },
        }
        requested_pages: list[int] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            self.assertEqual("https://jooble.org/api/test-key", request.full_url)
            self.assertEqual("POST", request.get_method())
            self.assertEqual(30.0, timeout)
            body = json.loads(request.data.decode("utf-8"))
            requested_pages.append(body["page"])
            self.assertEqual("python developer", body["keywords"])
            self.assertEqual("Italy", body["location"])
            self.assertEqual("80", body["radius"])
            self.assertIs(body["companysearch"], False)
            self.assertEqual(2, body["ResultOnPage"])
            return FakeResponse(pages[body["page"]])

        jobs = list(JoobleCollector(self._config(), opener=opener, sleep=lambda _: None).fetch())

        self.assertEqual([1, 2], requested_pages)
        self.assertEqual(["101", "102"], [job.source_job_id for job in jobs])
        self.assertEqual("Python & API Developer", jobs[0].title)
        self.assertEqual("Acme S.r.l.", jobs[0].company)
        self.assertEqual("Full-time", jobs[0].employment_type)
        self.assertTrue(jobs[0].remote)
        self.assertIn("Fully remote role.", jobs[0].description)

    def test_profiles_are_round_robin_under_global_budget(self) -> None:
        self._write_config(
            """request_budget: 3
results_per_page: 1
max_pages_per_profile: 5
query_profiles:
  - name: italy
    keywords: python
    location: Italy
  - name: uk
    keywords: golang
    location: United Kingdom
"""
        )
        requests: list[tuple[str, int]] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            body = json.loads(request.data.decode("utf-8"))
            requests.append((body["location"], body["page"]))
            identifier = f"{body['location']}-{body['page']}"
            return FakeResponse(
                {
                    "totalCount": 100,
                    "jobs": [{
                        "id": identifier,
                        "title": "Engineer",
                        "snippet": "Role",
                        "link": f"https://example.test/{identifier}",
                    }],
                }
            )

        jobs = list(JoobleCollector(self._config(), opener=opener, sleep=lambda _: None).fetch())
        self.assertEqual(3, len(jobs))
        self.assertEqual(
            [("Italy", 1), ("United Kingdom", 1), ("Italy", 2)],
            requests,
        )

    def test_disabled_profiles_are_ignored(self) -> None:
        self._write_config(
            """query_profiles:
  - name: disabled
    enabled: false
    keywords: python
    location: Italy
  - name: enabled
    keywords: golang
    location: Italy
    max_pages: 1
"""
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            body = json.loads(request.data.decode("utf-8"))
            self.assertEqual("golang", body["keywords"])
            return FakeResponse({"totalCount": 0, "jobs": []})

        collector = JoobleCollector(self._config(), opener=opener, sleep=lambda _: None)
        self.assertEqual(["enabled"], [profile.name for profile in collector.profiles])
        self.assertEqual([], list(collector.fetch()))

    def test_rejects_unknown_profile_fields_and_invalid_radius(self) -> None:
        self._write_config(
            "query_profiles:\n  - name: bad\n    keywords: python\n    location: Italy\n    unsupported: value\n"
        )
        with self.assertRaisesRegex(ValueError, "unsupported"):
            JoobleCollector(self._config())

        self._write_config(
            "query_profiles:\n  - name: bad\n    keywords: python\n    location: Italy\n    radius: 10\n"
        )
        with self.assertRaisesRegex(ValueError, "radius"):
            JoobleCollector(self._config())

    def test_zero_budget_performs_no_requests(self) -> None:
        self._write_config(
            "request_budget: 0\nquery_profiles:\n  - name: python\n    keywords: python\n    location: Italy\n"
        )
        collector = JoobleCollector(
            self._config(), opener=lambda *args, **kwargs: self.fail("request made")
        )
        self.assertEqual([], list(collector.fetch()))


if __name__ == "__main__":
    unittest.main()
