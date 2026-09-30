from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.request import Request


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "dou" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_dou_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
dou_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = dou_module
SPEC.loader.exec_module(dou_module)

DouCollector = dou_module.DouCollector
DouQuery = dou_module.DouQuery
parse_detail_page = dou_module.parse_detail_page
parse_listing_page = dou_module.parse_listing_page


class FakeHeaders:
    def get_content_charset(self) -> str:
        return "utf-8"


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content.encode("utf-8")
        self.headers = FakeHeaders()

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.content


class DouCollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "dou.yaml"
        self.config_path.write_text(
            "\n".join(
                [
                    "version: 1",
                    "timeout_seconds: 10",
                    "analysis_priority: 100",
                    "queries:",
                    "  - name: php-remote",
                    "    url: https://jobs.dou.ua/vacancies/?remote&category=PHP",
                    "    category: PHP",
                    "  - name: golang-remote",
                    "    url: https://jobs.dou.ua/vacancies/?remote&category=Golang",
                    "    category: Golang",
                ]
            ),
            encoding="utf-8",
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_parses_listing_cards(self) -> None:
        jobs = parse_listing_page(_listing_html("PHP"), DouQuery(1, "php", "https://jobs.dou.ua/vacancies/?remote&category=PHP", "PHP"))

        self.assertEqual(1, len(jobs))
        self.assertEqual("Senior PHP Developer", jobs[0].title)
        self.assertEqual("Acme", jobs[0].company)
        self.assertEqual("https://jobs.dou.ua/companies/acme/vacancies/123/", jobs[0].source_url)
        self.assertEqual("Київ, віддалено", jobs[0].location)
        self.assertEqual("$3000-5000", jobs[0].salary)
        self.assertIn("Laravel services", jobs[0].summary)

    def test_parses_detail_description_and_ukrainian_date(self) -> None:
        detail = parse_detail_page(
            """
            <div class="l-vacancy">
              <div class="date">31 липня 2026</div>
              <div class="b-typo vacancy-section"><p>Build APIs.</p><ul><li>Go services</li></ul></div>
            </div>
            <div class="b-compinfo"><div class="info"><div class="l-t">Product company.</div></div></div>
            """
        )

        self.assertEqual("2026-07-31", detail.published_at)
        self.assertIn("Build APIs.", detail.description)
        self.assertIn("Go services", detail.description)
        self.assertEqual("Product company.", detail.company_description)

    def test_fetches_configured_queries_with_high_priority_and_dedupes(self) -> None:
        pages = {
            "https://jobs.dou.ua/vacancies/?remote&category=PHP": _listing_html("PHP"),
            "https://jobs.dou.ua/vacancies/?remote&category=Golang": _listing_html("Golang"),
            "https://jobs.dou.ua/companies/acme/vacancies/123/": (
                '<div class="date">31 липня 2026</div>'
                '<div class="b-typo vacancy-section"><p>Full DOU description.</p></div>'
            ),
        }

        def opener(request: Request, **_: Any) -> FakeResponse:
            return FakeResponse(pages[request.full_url])

        collector = DouCollector({"DOU_CONFIG": str(self.config_path)}, opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(1, len(jobs))
        self.assertEqual("dou", jobs[0].source)
        self.assertEqual("123", jobs[0].source_job_id)
        self.assertEqual("Acme", jobs[0].company)
        self.assertEqual(100, jobs[0].analysis_priority)
        self.assertTrue(jobs[0].remote)
        self.assertEqual("2026-07-31", jobs[0].published_at)
        self.assertIn("Full DOU description.", jobs[0].description)
        self.assertEqual(4, collector.api_requests)
        self.assertEqual(2, len(jobs[0].source_metadata["discovered_by"]))


def _listing_html(category: str) -> str:
    return f"""
    <ul class="lt">
      <li class="l-vacancy">
        <div class="date">31 липня</div>
        <div class="title">
          <a class="vt" href="https://jobs.dou.ua/companies/acme/vacancies/123/">Senior {category} Developer</a>
          <strong>в&nbsp;<a class="company" href="https://jobs.dou.ua/companies/acme/vacancies/"><img alt="" class="f-i" src="favicon.png">&nbsp;Acme</a></strong>
          <span class="salary">$3000-5000</span>
          <span class="cities bi bi-geo-alt-fill"> Київ, віддалено</span>
        </div>
        <div class="sh-info">Build<br>Laravel services.</div>
      </li>
    </ul>
    """


if __name__ == "__main__":
    unittest.main()
