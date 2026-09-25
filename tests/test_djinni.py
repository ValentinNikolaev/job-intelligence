from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.request import Request


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "djinni" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_djinni_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
djinni = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = djinni
SPEC.loader.exec_module(djinni)


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content.encode("utf-8")
        self.headers = self

    def get_content_charset(self) -> str:
        return "utf-8"

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.content


def card(job_id: int, title: str, company: str, remote: str = "Full Remote") -> str:
    return f"""
    <div id="job-item-{job_id}" class="job-item card-link">
      <a class="job_item__header-link" href="/jobs/{job_id}-example/">
        <h2 class="job-item__position">{title}</h2>
        <span class="small text-gray-800">{company}</span>
      </a>
      <span class="text-nowrap">{remote}</span>
      <span class="location-text">EU</span>
      <span class="js-original-text"><p>Build APIs.</p><ul><li>Own services</li></ul></span>
      <span title="12:52 24.09.2026">1d</span>
    </div>
    """


class DjinniTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config = Path(self.temp.name) / "djinni.yaml"
        self.config.write_text(
            "version: 1\ntimeout_seconds: 5\nmax_pages_per_query: 3\nanalysis_priority: 100\n"
            "queries:\n"
            "  - name: php-remote\n    url: https://djinni.co/jobs/?primary_keyword=PHP&employment=remote\n    category: PHP\n"
            "  - name: golang-remote\n    url: https://djinni.co/jobs/?primary_keyword=Golang&employment=remote\n    category: Golang\n",
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_fetches_public_pages_and_deduplicates_overlap(self) -> None:
        pages = {
            "https://djinni.co/jobs/?primary_keyword=PHP&employment=remote": (
                card(850052, "Senior PHP Developer", "TrueLabel")
                + card(850053, "Office PHP Developer", "OfficeCo", "Office")
                + '<a class="page-link" href="?primary_keyword=PHP&amp;employment=remote&amp;page=2">2</a>'
            ),
            "https://djinni.co/jobs/?primary_keyword=PHP&employment=remote&page=2": (
                card(850054, "PHP / Go Developer", "JointCo")
            ),
            "https://djinni.co/jobs/?primary_keyword=Golang&employment=remote": (
                card(850054, "PHP / Go Developer", "JointCo")
            ),
        }

        def opener(request: Request, **_: Any) -> FakeResponse:
            return FakeResponse(pages[request.full_url])

        collector = djinni.DjinniCollector({"DJINNI_CONFIG": str(self.config)}, opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(2, len(jobs))
        self.assertEqual({"850052", "850054"}, {job.source_job_id for job in jobs})
        self.assertEqual(3, collector.api_requests)
        self.assertTrue(all(job.remote for job in jobs))
        self.assertEqual("2026-09-24", jobs[0].published_at)
        self.assertEqual("TrueLabel", jobs[0].company)
        self.assertIn("Own services", jobs[0].description)
        self.assertEqual(2, len(jobs[1].source_metadata["discovered_by"]))

    def test_rejects_non_remote_query_and_untrusted_job_url(self) -> None:
        with self.assertRaises(ValueError):
            djinni._validate_search_url("https://djinni.co/jobs/?primary_keyword=PHP&employment=office")
        query = djinni.Query(1, "php", "https://djinni.co/jobs/?primary_keyword=PHP&employment=remote", "PHP")
        markup = card(850052, "Senior PHP Developer", "TrueLabel").replace(
            "/jobs/850052-example/", "https://evil.example/jobs/850052-example/"
        )
        self.assertIsNone(djinni.parse_card("850052", markup, query, 100))


if __name__ == "__main__":
    unittest.main()
