from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any
from urllib.error import URLError
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
DEFAULT_CONFIG_PATH = custom_module.DEFAULT_CONFIG_PATH
load_settings = custom_module._load_settings
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

    def test_extract_headings_creates_distinct_inline_jobs(self) -> None:
        self._write_config(
            "\n".join(
                [
                    "    extract_headings: true",
                    "    heading_title_terms: [senior backend engineer, php developer]",
                ]
            )
        )
        pages = {
            "https://careers.acme.test/jobs": (
                "<main><h1>Senior Backend Engineer</h1><h2>PHP Developer</h2>"
                "<h3>Sales Manager</h3><p>Build reliable services.</p></main>"
            )
        }

        def opener(request: Request, **_: Any) -> FakeResponse:
            return FakeResponse(pages[request.full_url])

        jobs = list(CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener).fetch())

        self.assertEqual(["PHP Developer", "Senior Backend Engineer"], sorted(job.title for job in jobs))
        self.assertEqual({"https://careers.acme.test/jobs"}, {job.source_url for job in jobs})
        self.assertEqual(2, len({job.source_job_id for job in jobs}))
        self.assertTrue(all(job.source_job_id.startswith("inline-sha256:") for job in jobs))

    def test_heading_does_not_duplicate_json_ld_job(self) -> None:
        self._write_config(
            "\n".join(
                [
                    "    extract_headings: true",
                    "    heading_title_terms: [php developer]",
                ]
            )
        )
        page = (
            '<script type="application/ld+json">'
            '{"@type":"JobPosting","title":"PHP Developer",'
            '"url":"https://careers.acme.test/jobs/php"}'
            "</script><main><h1>PHP Developer</h1><p>Build APIs.</p></main>"
        )

        def opener(_: Request, **__: Any) -> FakeResponse:
            return FakeResponse(page)

        jobs = list(CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener).fetch())

        self.assertEqual(["PHP Developer"], [job.title for job in jobs])
        self.assertTrue(jobs[0].source_job_id.startswith("url-sha256:"))

    def test_extract_headings_requires_specific_heading_terms(self) -> None:
        self._write_config("    extract_headings: true")

        with self.assertRaisesRegex(ValueError, "heading_title_terms are required"):
            load_settings(self.config_path)

    def test_follows_only_allowlisted_external_job_host(self) -> None:
        self._write_config("    allowed_job_hosts: [jobs.workable.test]")
        pages = {
            "https://careers.acme.test/jobs": (
                '<a href="https://jobs.workable.test/j/backend">Backend Engineer</a>'
                '<a href="https://other-ats.test/j/php">PHP Developer</a>'
            ),
            "https://jobs.workable.test/j/backend": "<h1>Backend Engineer</h1><p>Build APIs.</p>",
        }
        requested: list[str] = []

        def opener(request: Request, **_: Any) -> FakeResponse:
            requested.append(request.full_url)
            return FakeResponse(pages[request.full_url])

        jobs = list(CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener).fetch())

        self.assertEqual(["Backend Engineer"], [job.title for job in jobs])
        self.assertIn("https://jobs.workable.test/j/backend", requested)
        self.assertNotIn("https://other-ats.test/j/php", requested)

    def test_detail_failure_preserves_other_jobs(self) -> None:
        self._write_config()
        pages = {
            "https://careers.acme.test/jobs": (
                '<a href="/jobs/backend">Backend Engineer</a>'
                '<a href="/jobs/php">PHP Developer</a>'
            ),
            "https://careers.acme.test/jobs/backend": "<h1>Backend Engineer</h1><p>Build APIs.</p>",
        }

        def opener(request: Request, **_: Any) -> FakeResponse:
            if request.full_url.endswith("/jobs/php"):
                raise URLError("temporary outage")
            return FakeResponse(pages[request.full_url])

        collector = CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener)
        stderr = StringIO()
        with redirect_stderr(stderr):
            jobs = list(collector.fetch())

        self.assertEqual(["Backend Engineer"], [job.title for job in jobs])
        self.assertEqual(1, collector.errors)
        self.assertEqual((1, 0), (collector.sources_total, collector.sources_failed))
        events = [json.loads(line) for line in stderr.getvalue().splitlines()]
        failure = next(event for event in events if event.get("status") == "failed")
        self.assertEqual("custom.page.finished", failure["event"])
        self.assertEqual("detail", failure["phase"])
        self.assertEqual("https://careers.acme.test/jobs/php", failure["url"])
        self.assertEqual("RuntimeError", failure["error_type"])
        self.assertIn("temporary outage", failure["error"])
        self.assertGreaterEqual(failure["elapsed_ms"], 0)
        source = next(event for event in events if event["event"] == "custom.source.finished")
        self.assertEqual("partial", source["status"])
        self.assertEqual(1, source["errors"])
        self.assertEqual(1, source["fetched"])
        self.assertGreaterEqual(source["elapsed_ms"], 0)

    def test_complete_custom_source_failure_is_counted_and_logged(self) -> None:
        self._write_config()

        def offline(*_args: Any, **_kwargs: Any) -> FakeResponse:
            raise URLError("offline")

        collector = CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=offline)
        stderr = StringIO()

        with redirect_stderr(stderr):
            jobs = list(collector.fetch())

        self.assertEqual([], jobs)
        self.assertEqual((1, 1), (collector.sources_total, collector.sources_failed))
        events = [json.loads(line) for line in stderr.getvalue().splitlines()]
        self.assertEqual("custom.source.started", events[0]["event"])
        self.assertEqual("custom.source.finished", events[-1]["event"])
        self.assertEqual("failed", events[-1]["status"])

    def test_board_failure_does_not_suppress_seed(self) -> None:
        self._write_config(
            "\n".join(
                [
                    "    seed_jobs:",
                    "      - title: PHP Developer",
                    "        url: https://careers.acme.test/jobs/php-developer",
                ]
            )
        )
        pages = {"https://careers.acme.test/jobs/php-developer": "<h1>PHP Developer</h1><p>Build APIs.</p>"}

        def opener(request: Request, **_: Any) -> FakeResponse:
            if request.full_url == "https://careers.acme.test/jobs":
                raise URLError("temporary outage")
            return FakeResponse(pages[request.full_url])

        collector = CustomCollector({"CUSTOM_CONFIG": str(self.config_path)}, opener=opener)
        jobs = list(collector.fetch())

        self.assertEqual(["PHP Developer"], [job.title for job in jobs])
        self.assertEqual(1, collector.errors)

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
                source="jooble",
                source_job_id="j-1",
                source_url="https://jooble.test/1",
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

    def test_default_config_monitors_requested_italian_company_boards(self) -> None:
        settings = load_settings(DEFAULT_CONFIG_PATH)
        sources = {source.name: source for source in settings.sources}
        expected = {
            "papa-chat": "https://pappachat.com/lavora-con-noi/",
            "hubcore": "https://hubcore.ai/it/lavora-con-noi",
            "watuppa": "https://www.watuppa.it/en/careers/",
            "motork": "https://www.motork.ai/jobs",
            "madisoft-nuvola": "https://labs.madisoft.it/entra-nel-team/",
            "trustfull": "https://jobs.workable.com/company/5FbNAZwFhraGUvm3uU3MxU/jobs-at-trustfull",
            "hinto-group": "https://www.hintogroup.eu/it/posizioni-aperte",
            "cuborio": "https://cuborio.com/azienda/lavora-con-noi",
            "brain-computing": "https://recruiting.braincomputing.com/job/VFNSTmxmN2xkeEJWbGNnQlNFa3AwQT09",
            "intesys": "https://www.intesys.it/lavora-con-noi/posizioni-aperte-y-career/",
            "bsd-software": "https://www.bsdsoftware.it/LavoraConNoi/",
            "brownie-suite": "https://www.browniesuite.com/en/careers",
            "web2emotions": "https://www.web2emotions.com/agenzia/lavora-con-noi/",
            "gruppo-yec": "https://gruppoyec.com/careers",
            "queryo": "https://www.queryo.com/lavora-con-noi.html",
            "joint-tech": "https://www.joint-tech.com/it/lavora-con-noi/",
            "youco": "https://www.youco.eu/lavora-con-noi/",
            "gkt-group": "https://gktgroup.it/career/",
            "alion-docebo": "https://alion.io/company/docebo#co_jobs",
            "webeetle": "https://www.webeetle.com/join-us/",
            "scf-group": "https://www.scfgroup.it/lavora-con-noi/",
            "techseed": "https://www.techseed.it/lavora-con-noi",
            "joker": "https://jokersrl.it/lavora-con-noi/",
            "beliven": "https://careers.beliven.com/recruiting/",
            "advinser": "https://advinser.it/unisciti-al-team",
            "hnrg": "https://hnrg.it/job/back-end-developer/",
            "atomica-studio": "https://www.atomicastudio.com/en/careers",
            "romiltec": "https://romiltec.it/lavora-con-noi/",
            "trinaware": "https://www.trinaware.it/azienda/lavora-con-noi",
            "retesi": "https://www.retesi.it/#careers",
            "brb-development": "https://www.brbdevelopment.com/lavora-con-noi",
            "neting": "https://www.neting.it/careers/sviluppatore-laravel-remote/",
            "nextip": "https://www.nextip.com/job-position-backend/",
            "reverse": "https://reverse.hr/en/internal-development-team/",
            "facile-engineering": "https://engineering.facile.it/ita/careers/",
            "onpage": "https://onpage.it/lavora-con-noi/",
            "shippypro": "https://shippypro.factorialhr.com/",
        }

        self.assertEqual(100, settings.analysis_priority)
        self.assertEqual(len(settings.sources), len(sources))
        self.assertEqual(
            len(settings.sources),
            len({source.board_url for source in settings.sources}),
        )
        for name, url in expected.items():
            self.assertIn(name, sources)
            source_urls = {sources[name].board_url, *(seed.url for seed in sources[name].seed_jobs)}
            self.assertIn(url, source_urls)


if __name__ == "__main__":
    unittest.main()
