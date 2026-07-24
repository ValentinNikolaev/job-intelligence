from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.request import Request

import yaml

from jobintel.models import NormalizedJob
from jobintel.registry import Registry


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "custom" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_custom_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
custom_module = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = custom_module
SPEC.loader.exec_module(custom_module)

CustomCollector = custom_module.CustomCollector
CustomSource = custom_module.CustomSource
PageData = custom_module.PageData
parse_source_page = custom_module.parse_source_page


class FakeResponse:
    def __init__(self, content: str) -> None:
        self.content = content.encode("utf-8")
        self.headers = self

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.content

    def get_content_charset(self) -> str:
        return "utf-8"


class CustomCollectorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "custom.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, extra: str = "") -> None:
        self.config_path.write_text(
            "\n".join(
                [
                    "version: 1",
                    "timeout_seconds: 10",
                    "analysis_priority: 100",
                    "default_title_terms: [backend, php, software]",
                    "sources:",
                    "  - name: acme",
                    "    company: Acme S.r.l.",
                    "    board_url: https://careers.acme.test/jobs",
                    "    company_url: https://acme.test",
                    "    remote: true",
                    "    location: Remote Italy",
                    "    notes: Direct company board.",
                    extra,
                ]
            ),
            encoding="utf-8",
        )

    def test_parses_json_ld_job_posting(self) -> None:
        source = CustomSource(
            name="acme",
            company="Acme",
            board_url="https://careers.acme.test/jobs",
            company_url="https://acme.test",
            remote=True,
            location="Remote",
            title_terms=("backend", "php"),
        )
        page = PageData(
            description="Senior PHP Backend Developer role.",
            canonical_url="https://careers.acme.test/jobs/senior-php",
            json_ld_jobs=(
                {
                    "@type": "JobPosting",
                    "title": "Senior PHP Backend Developer",
                    "url": "https://careers.acme.test/jobs/senior-php",
                    "description": "<p>Build Laravel integrations.</p>",
                    "employmentType": "FULL_TIME",
                    "datePosted": "2026-07-24",
                    "hiringOrganization": {"name": "Acme S.r.l."},
                },
            ),
        )

        jobs = parse_source_page(source, page, 100)

        self.assertEqual(1, len(jobs))
        self.assertEqual("custom", jobs[0].source)
        self.assertEqual("Senior PHP Backend Developer", jobs[0].title)
        self.assertEqual("Acme S.r.l.", jobs[0].company)
        self.assertEqual("FULL_TIME", jobs[0].employment_type)
        self.assertEqual(100, jobs[0].analysis_priority)
        self.assertIn("Build Laravel integrations.", jobs[0].description)

    def test_fetch_follows_matching_same_site_links_and_seeds(self) -> None:
        self._write_config(
            "\n".join(
                [
                    "    seed_jobs:",
                    "      - title: PHP Developer",
                    "        url: https://careers.acme.test/jobs/php-developer",
                ]
            )
        )
        pages = {
            "https://careers.acme.test/jobs": (
                '<a href="/jobs/senior-backend">Senior Backend Engineer</a>'
                '<a href="/jobs/sales-manager">Sales Manager</a>'
            ),
            "https://careers.acme.test/jobs/senior-backend": (
                "<html><title>Senior Backend Engineer</title>"
                "<main><h1>Senior Backend Engineer</h1><p>Work on PHP services.</p></main></html>"
            ),
            "https://careers.acme.test/jobs/php-developer": (
                "<html><title>PHP Developer</title><main><p>Permanent PHP role.</p></main></html>"
            ),
        }
        requested: list[str] = []

        def opener(request: Request, **_: Any) -> FakeResponse:
            url = request.full_url
            requested.append(url)
            return FakeResponse(pages[url])

        collector = CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(["PHP Developer", "Senior Backend Engineer"], sorted(job.title for job in jobs))
        self.assertNotIn("https://careers.acme.test/jobs/sales-manager", requested)
        self.assertTrue(all(job.remote is True for job in jobs))
        self.assertTrue(all(job.analysis_priority == 100 for job in jobs))
        self.assertEqual(3, collector.api_requests)

    def test_detail_page_heading_wins_over_generic_apply_link(self) -> None:
        self._write_config()
        pages = {
            "https://careers.acme.test/jobs": (
                '<a href="/jobs/software-engineering-team-lead-311256">Apply now</a>'
            ),
            "https://careers.acme.test/jobs/software-engineering-team-lead-311256": (
                "<html><title>Apply now</title><main>"
                "<h1>Software Engineering Team Lead</h1><p>Lead backend services.</p>"
                "</main></html>"
            ),
        }

        def opener(request: Request, **_: Any) -> FakeResponse:
            return FakeResponse(pages[request.full_url])

        collector = CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(1, len(jobs))
        self.assertEqual("Software Engineering Team Lead", jobs[0].title)

    def test_detail_page_heading_wins_over_long_card_text(self) -> None:
        self._write_config()
        pages = {
            "https://careers.acme.test/jobs": (
                '<a href="/jobs/senior-php-backend-developer/">'
                "Senior PHP Backend Developer Are you ready to build APIs for "
                "front-end and mobile apps? Read more and apply here! View Position"
                "</a>"
            ),
            "https://careers.acme.test/jobs/senior-php-backend-developer/": (
                "<html><title>Opening for Senior PHP Backend Developer | Acme</title>"
                "<main><h1>Opening for Senior PHP Backend Developer | Acme</h1>"
                "<p>Build PHP services.</p></main></html>"
            ),
        }

        def opener(request: Request, **_: Any) -> FakeResponse:
            return FakeResponse(pages[request.full_url])

        collector = CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(1, len(jobs))
        self.assertEqual("Senior PHP Backend Developer", jobs[0].title)

    def test_custom_source_replaces_aggregator_content_and_raises_priority(self) -> None:
        root = Path(self.temp.name) / "registry"
        now = datetime(2026, 7, 24, 12, 0, tzinfo=timezone.utc)
        registry = Registry(root, clock=lambda: now, id_factory=lambda: "custom-priority")
        registry.upsert(
            NormalizedJob(
                source="adzuna",
                source_job_id="a-1",
                source_url="https://adzuna.test/1",
                title="Senior Backend Engineer",
                company="Acme",
                description="Aggregator snippet.",
                location="Remote",
            )
        )
        registry.upsert(
            NormalizedJob(
                source="custom",
                source_job_id="c-1",
                source_url="https://careers.acme.test/jobs/senior-backend",
                title="Senior Backend Engineer",
                company="Acme",
                description="Direct company-board description.",
                location="Remote",
                analysis_priority=100,
            )
        )
        directory = next((root / "jobs").iterdir())
        meta = yaml.safe_load((directory / "meta.yaml").read_text(encoding="utf-8"))

        self.assertEqual("custom", meta["data_source"])
        self.assertEqual(100, meta["analysis_priority"])
        self.assertIn("Direct company-board description.", (directory / "job.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
