from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "adzuna" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_adzuna_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
AdzunaCollector = MODULE.AdzunaCollector


class FakeResponse:
    def __init__(self, value: dict[str, Any]) -> None:
        self.payload = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


class AdzunaTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "adzuna.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, text: str) -> None:
        self.config_path.write_text(text, encoding="utf-8")

    def _config(self) -> dict[str, str]:
        return {
            "ADZUNA_APP_ID": "test-id",
            "ADZUNA_APP_KEY": "test-key",
            "ADZUNA_CONFIG": str(self.config_path),
        }

    def test_fetches_pages_normalizes_and_deduplicates(self) -> None:
        self._write_config(
            """version: 1
request_budget: 3
results_per_page: 2
queries:
  - country: it
    what: python developer
    where: Roma
    full_time: true
"""
        )
        pages = {
            1: {
                "count": 3,
                "results": [
                    {
                        "id": "a-1",
                        "title": "Python &amp; API Developer",
                        "description": "<p>Remote role.</p>",
                        "created": "2026-07-21T10:00:00Z",
                        "redirect_url": "https://www.adzuna.it/details/a-1",
                        "company": {"display_name": "Acme S.r.l."},
                        "location": {"display_name": "Roma, Lazio"},
                        "contract_time": "full_time",
                        "contract_type": "permanent",
                    },
                    {
                        "id": "a-2",
                        "title": "Platform Engineer",
                        "description": "Build systems.",
                        "created": "2026-07-20T09:00:00Z",
                        "redirect_url": "https://www.adzuna.it/details/a-2",
                        "company": {"canonical_name": "Widgets"},
                        "location": {"area": ["Italia", "Lazio", "Roma"]},
                    },
                ],
            },
            2: {
                "count": 3,
                "results": [
                    {
                        "id": "a-2",
                        "title": "Platform Engineer",
                        "description": "Duplicate result.",
                        "created": "2026-07-20T09:00:00Z",
                        "redirect_url": "https://www.adzuna.it/details/a-2",
                    }
                ],
            },
        }
        requested_pages: list[int] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            parsed = urlparse(request.full_url)
            page = int(parsed.path.rsplit("/", 1)[-1])
            requested_pages.append(page)
            parameters = parse_qs(parsed.query)
            self.assertEqual(["test-id"], parameters["app_id"])
            self.assertEqual(["test-key"], parameters["app_key"])
            self.assertEqual(["python developer"], parameters["what"])
            self.assertEqual(["1"], parameters["full_time"])
            self.assertEqual(30.0, timeout)
            return FakeResponse(pages[page])

        collector = AdzunaCollector(self._config(), opener=opener, sleep=lambda _: None)
        jobs = list(collector.fetch())

        self.assertEqual([1, 2], requested_pages)
        self.assertEqual(["a-1", "a-2"], [job.source_job_id for job in jobs])
        self.assertEqual("Python & API Developer", jobs[0].title)
        self.assertEqual("Acme S.r.l.", jobs[0].company)
        self.assertEqual("full-time, permanent", jobs[0].employment_type)
        self.assertTrue(jobs[0].remote)
        self.assertEqual("Roma, Lazio, Italia", jobs[1].location)

    def test_round_robin_respects_global_request_budget(self) -> None:
        self._write_config(
            """request_budget: 3
results_per_page: 1
max_pages_per_query: 5
queries:
  - country: it
    what: python
  - country: gb
    what: golang
"""
        )
        requests: list[str] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            requests.append(request.full_url)
            parsed = urlparse(request.full_url)
            identifier = f"{parsed.path.split('/')[-3]}-{parsed.path.rsplit('/', 1)[-1]}"
            return FakeResponse(
                {
                    "count": 100,
                    "results": [{
                        "id": identifier,
                        "title": "Engineer",
                        "description": "Role",
                        "created": "2026-07-20T09:00:00Z",
                        "redirect_url": f"https://jobs.test/{identifier}",
                    }],
                }
            )

        jobs = list(AdzunaCollector(self._config(), opener=opener, sleep=lambda _: None).fetch())
        self.assertEqual(3, len(requests))
        self.assertEqual(["it-1", "gb-1", "it-2"], [job.source_job_id for job in jobs])

    def test_rejects_unknown_query_fields(self) -> None:
        self._write_config("queries:\n  - country: it\n    what: python\n    unsupported: value\n")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            AdzunaCollector(self._config())

    def test_configurable_title_filter_skips_irrelevant_results(self) -> None:
        self._write_config(
            """request_budget: 1
title_include_terms: [backend, software engineer]
title_exclude_terms: [frontend, wordpress]
queries:
  - country: de
    title_only: backend
    what_or: php golang
    what_exclude: python java
"""
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            parameters = parse_qs(urlparse(request.full_url).query)
            self.assertEqual(["backend"], parameters["title_only"])
            self.assertEqual(["php golang"], parameters["what_or"])
            self.assertEqual(["python java"], parameters["what_exclude"])
            return FakeResponse(
                {
                    "count": 3,
                    "results": [
                        {
                            "id": "keep",
                            "title": "Senior Backend Engineer",
                            "description": "Golang services",
                            "redirect_url": "https://jobs.test/keep",
                        },
                        {
                            "id": "excluded",
                            "title": "Backend / Frontend Engineer",
                            "description": "PHP services",
                            "redirect_url": "https://jobs.test/excluded",
                        },
                        {
                            "id": "missing",
                            "title": "Product Manager",
                            "description": "Backend PHP product",
                            "redirect_url": "https://jobs.test/missing",
                        },
                    ],
                }
            )

        jobs = list(AdzunaCollector(self._config(), opener=opener, sleep=lambda _: None).fetch())
        self.assertEqual(["keep"], [job.source_job_id for job in jobs])

    def test_rejects_invalid_title_filter_config(self) -> None:
        self._write_config(
            "title_include_terms: backend\nqueries:\n  - country: it\n    what: php\n"
        )
        with self.assertRaisesRegex(ValueError, "title_include_terms must be a YAML list"):
            AdzunaCollector(self._config())

    def test_zero_budget_performs_no_requests(self) -> None:
        self._write_config("request_budget: 0\nqueries:\n  - country: it\n    what: python\n")
        collector = AdzunaCollector(self._config(), opener=lambda *args, **kwargs: self.fail("request made"))
        self.assertEqual([], list(collector.fetch()))


if __name__ == "__main__":
    unittest.main()
