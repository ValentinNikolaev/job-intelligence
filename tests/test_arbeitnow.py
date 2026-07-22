from __future__ import annotations

import hashlib
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


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "arbeitnow" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_arbeitnow_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
ArbeitnowCollector = MODULE.ArbeitnowCollector
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
        "slug": "backend-engineer-rome-12345",
        "company_name": "Acme S.r.l.",
        "title": "Backend &amp; API Engineer",
        "description": "<h2>Role</h2><p>Build the API.</p><p>Full description.</p>",
        "remote": True,
        "url": "https://www.arbeitnow.com/jobs/companies/acme/backend-engineer-rome-12345",
        "tags": ["Remote", "Backend"],
        "job_types": ["Full-time", "professional / experienced"],
        "location": "Rome, Italy",
        "created_at": 1721383200,
    }
    value.update(overrides)
    return value


class ArbeitnowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "arbeitnow.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, text: str) -> None:
        self.config_path.write_text(text, encoding="utf-8")

    def _config(self) -> dict[str, str]:
        return {"ARBEITNOW_CONFIG": str(self.config_path)}

    def test_parses_actual_response_envelope(self) -> None:
        next_url = "https://www.arbeitnow.com/api/job-board-api?page=2"
        page = parse_api_response(
            {
                "data": [api_job()],
                "links": {"first": f"{MODULE.API_ROOT}?page=1", "next": next_url},
                "meta": {"current_page": 1, "per_page": 100},
            }
        )

        self.assertEqual(1, len(page.jobs))
        self.assertEqual(next_url, page.next_url)
        self.assertEqual("backend-engineer-rome-12345", page.jobs[0].source_job_id)

    def test_normalizes_common_fields_and_useful_metadata(self) -> None:
        job = normalize_job(api_job())

        self.assertEqual("arbeitnow", job.source)
        self.assertEqual("Backend & API Engineer", job.title)
        self.assertEqual("Acme S.r.l.", job.company)
        self.assertEqual("Rome, Italy", job.location)
        self.assertTrue(job.remote)
        self.assertEqual("Full-time, professional / experienced", job.employment_type)
        self.assertIn("## Role", job.description)
        self.assertIn("Full description.", job.description)
        self.assertEqual(
            datetime.fromtimestamp(1721383200, timezone.utc)
            .replace(microsecond=0)
            .isoformat()
            .replace("+00:00", "Z"),
            job.published_at,
        )
        self.assertEqual(["Remote", "Backend"], job.source_metadata["tags"])
        self.assertEqual(
            ["Full-time", "professional / experienced"],
            job.source_metadata["job_types"],
        )

    def test_follows_next_links_and_sends_documented_visa_filter(self) -> None:
        self._write_config("max_pages: null\nvisa_sponsorship: true\ntimeout_seconds: 12\n")
        requested: list[str] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            requested.append(request.full_url)
            self.assertEqual(12.0, timeout)
            page = int(parse_qs(urlparse(request.full_url).query).get("page", ["1"])[0])
            if page == 1:
                return FakeResponse(
                    {
                        "data": [api_job()],
                        "links": {
                            "next": (
                                f"{MODULE.API_ROOT}?visa_sponsorship=true&page=2"
                            )
                        },
                    }
                )
            return FakeResponse({"data": [], "links": {"next": None}})

        jobs = list(
            ArbeitnowCollector(self._config(), opener=opener, sleep=lambda _: None).fetch()
        )

        self.assertEqual(1, len(jobs))
        self.assertEqual(2, len(requested))
        self.assertEqual(["true"], parse_qs(urlparse(requested[0]).query)["visa_sponsorship"])
        self.assertEqual(["2"], parse_qs(urlparse(requested[1]).query)["page"])

    def test_max_pages_stops_pagination(self) -> None:
        self._write_config("max_pages: 1\n")
        requests = 0

        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal requests
            requests += 1
            return FakeResponse(
                {
                    "data": [api_job()],
                    "links": {"next": f"{MODULE.API_ROOT}?page=2"},
                }
            )

        jobs = list(ArbeitnowCollector(self._config(), opener=opener).fetch())
        self.assertEqual(1, requests)
        self.assertEqual(1, len(jobs))

    def test_source_identity_uses_slug_then_deterministic_url_hash(self) -> None:
        with_slug = normalize_job(api_job())
        self.assertEqual("backend-engineer-rome-12345", with_slug.source_job_id)

        url = "https://www.arbeitnow.com/jobs/companies/acme/backend-engineer#apply"
        without_slug = normalize_job(api_job(slug=None, url=url))
        canonical_url = url.removesuffix("#apply")
        expected = hashlib.sha256(canonical_url.encode("utf-8")).hexdigest()
        self.assertEqual(f"url-sha256:{expected}", without_slug.source_job_id)

    def test_repeated_collection_is_unchanged_not_duplicated(self) -> None:
        self._write_config("max_pages: 1\n")

        def opener(request: Any, timeout: float) -> FakeResponse:
            return FakeResponse({"data": [api_job()], "links": {"next": None}})

        collector = ArbeitnowCollector(self._config(), opener=opener)
        registry = Registry(Path(self.temp.name) / "registry")
        first = [registry.upsert(job).status for job in collector.fetch()]
        second = [registry.upsert(job).status for job in collector.fetch()]

        self.assertEqual(["created"], first)
        self.assertEqual(["unchanged"], second)
        self.assertEqual(1, len(list(registry.jobs_dir.glob("*/meta.yaml"))))

    def test_retries_retryable_http_errors_then_fails_clearly(self) -> None:
        self._write_config("max_pages: 1\n")
        attempts = 0
        sleeps: list[float] = []

        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal attempts
            attempts += 1
            raise HTTPError(request.full_url, 503, "Unavailable", None, None)

        collector = ArbeitnowCollector(self._config(), opener=opener, sleep=sleeps.append)
        with self.assertRaisesRegex(RuntimeError, "HTTP 503 after retries"):
            list(collector.fetch())
        self.assertEqual(3, attempts)
        self.assertEqual([1, 2], sleeps)

    def test_invalid_json_and_repeated_pagination_url_fail(self) -> None:
        self._write_config("max_pages: null\n")
        invalid = ArbeitnowCollector(
            self._config(), opener=lambda *args, **kwargs: FakeResponse(b"not-json", raw=True)
        )
        with self.assertRaisesRegex(RuntimeError, "invalid JSON"):
            list(invalid.fetch())

        def repeated(request: Any, timeout: float) -> FakeResponse:
            return FakeResponse(
                {"data": [api_job()], "links": {"next": MODULE.API_ROOT}}
            )

        collector = ArbeitnowCollector(self._config(), opener=repeated)
        with self.assertRaisesRegex(RuntimeError, "repeated a page URL"):
            list(collector.fetch())


if __name__ == "__main__":
    unittest.main()
