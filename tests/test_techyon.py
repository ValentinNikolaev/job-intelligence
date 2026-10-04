from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
from urllib.error import HTTPError

from jobintel.collector import discover_collectors


ROOT = Path(__file__).parents[1]
SPEC = importlib.util.spec_from_file_location("test_techyon_collector", ROOT / "sources/techyon/collector.py")
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
URL = "https://www.techyon.it/candidati/backend-lead-roma.html"


def detail(*, title: str = "Backend Team Lead", graph: bool = False) -> str:
    payload = {
        "@type": "JobPosting", "title": title,
        "description": "&lt;p&gt;Hiring Company: software house.&lt;/p&gt;"
                       "&lt;h6&gt;Requirements&lt;/h6&gt;&lt;ul&gt;&lt;li&gt;PHP &amp;amp; Go&lt;/li&gt;&lt;/ul&gt;"
                       "&lt;p&gt;Compensation: &amp;euro; 40.000 - 46.000&lt;/p&gt;",
        "datePosted": "Fri, 02 Oct 2026 00:00:00 +0200",
        "validThrough": "Tue, 01 Dec 2026 00:00:00 +0100",
        "employmentType": "",
        "jobLocation": {"address": {"addressLocality": "Roma", "addressCountry": "IT"}},
        "hiringOrganization": {"name": "Techyon SRL", "sameAs": "https://www.techyon.it"},
    }
    if graph:
        payload = {"@graph": [{"@type": "Organization"}, payload]}
    return '<script type="application/ld+json">' + json.dumps(payload) + '</script>' + \
           '<form>Upload CV and personal data</form><footer>Newsletter</footer>'


def board(*links: str, pages: tuple[int, ...] = ()) -> str:
    return '<section class="job-advertisements">' + ''.join(
        f'<a class="item" href="{link}"><p>02/10/2026</p><strong>Role</strong></a>' for link in links
    ) + ''.join(f'<a class="page-link" href="/candidati.html?page={page}">{page}</a>' for page in pages) + '</section>'


class Response:
    def __init__(self, value: str) -> None:
        self.value = value
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self):
        return self.value.encode("utf-8")


class TechyonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "config.yaml"
        self.path.write_text("version: 1\ntimeout_seconds: 7\nmax_pages: 10\n", encoding="utf-8")
        self.config = {"TECHYON_CONFIG": str(self.path)}
    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_full_structured_description_excludes_forms_and_preserves_recruiter(self) -> None:
        job = MODULE.normalize_detail(detail(), URL)
        self.assertEqual(("techyon", "backend-lead-roma", "Techyon SRL"),
                         (job.source, job.source_job_id, job.company))
        self.assertEqual("Roma, IT", job.location)
        self.assertEqual("2026-10-01T22:00:00Z", job.published_at)
        self.assertIn("- PHP & Go", job.description)
        self.assertIn("€ 40.000 - 46.000", job.description)
        self.assertNotIn("Upload CV", job.description)
        self.assertNotIn("Newsletter", job.description)
        self.assertIsNone(job.remote)
        self.assertIsNone(job.employment_type)
        self.assertEqual("headhunter", job.source_metadata["source_type"])

    def test_graph_and_stable_identity_despite_title_query_changes(self) -> None:
        first = MODULE.normalize_detail(detail(), URL)
        second = MODULE.normalize_detail(detail(title="Principal Engineer", graph=True), URL + "?ref=alert#apply")
        self.assertEqual(first.source_job_id, second.source_job_id)
        self.assertEqual(URL, second.source_url)

    def test_pagination_deduplication_and_official_host_boundary(self) -> None:
        second_url = "https://www.techyon.it/candidati/php-milano.html"
        responses = {
            MODULE.BOARD_URL: board(URL, URL + "?ref=home", "https://evil.example/candidati/fake.html", pages=(1, 2)),
            MODULE.BOARD_URL + "?page=2": board(URL, second_url, pages=(1, 2)),
            URL: detail(), second_url: detail(title="PHP Engineer"),
        }
        requests = []
        def opener(request, timeout):
            requests.append(request.full_url)
            self.assertEqual(7, timeout)
            return Response(responses[request.full_url])
        collector = MODULE.TechyonCollector(self.config, opener=opener)
        self.assertEqual(["backend-lead-roma", "php-milano"], [j.source_job_id for j in collector.fetch()])
        self.assertEqual(4, collector.api_requests)
        self.assertEqual(4, len(set(requests)))

    def test_listing_limit_is_configurable(self) -> None:
        self.path.write_text("max_pages: 1\n", encoding="utf-8")
        responses = {MODULE.BOARD_URL: board(URL, pages=(2,)), URL: detail()}
        collector = MODULE.TechyonCollector(self.config, opener=lambda req, **kw: Response(responses[req.full_url]))
        self.assertEqual(1, len(list(collector.fetch())))
        self.assertEqual(2, collector.api_requests)

    def test_partial_detail_failure_preserves_other_jobs_and_reports_error(self) -> None:
        bad_url = "https://www.techyon.it/candidati/removed.html"
        def opener(req, **kwargs):
            if req.full_url == bad_url:
                raise HTTPError(bad_url, 404, "Removed", None, None)
            return Response(board(bad_url, URL) if req.full_url == MODULE.BOARD_URL else detail())
        collector = MODULE.TechyonCollector(self.config, opener=opener)
        with redirect_stderr(StringIO()) as log:
            jobs = list(collector.fetch())
        self.assertEqual(1, len(jobs))
        self.assertEqual(1, collector.errors)
        self.assertEqual(3, collector.api_requests)
        self.assertIn("techyon.page.failed", log.getvalue())

    def test_later_listing_failure_is_reported_as_partial(self) -> None:
        def opener(req, **kwargs):
            if "page=2" in req.full_url:
                return Response("<html>Error page</html>")
            return Response(board(URL, pages=(2,)) if req.full_url == MODULE.BOARD_URL else detail())
        collector = MODULE.TechyonCollector(self.config, opener=opener)
        with redirect_stderr(StringIO()):
            self.assertEqual(1, len(list(collector.fetch())))
        self.assertEqual(1, collector.errors)

    def test_transient_errors_retry_and_count_every_request(self) -> None:
        attempts = []
        sleeps = []
        def opener(req, **kwargs):
            attempts.append(req.full_url)
            if len(attempts) < 3:
                raise HTTPError(req.full_url, 503, "Unavailable", None, None)
            return Response(board())
        collector = MODULE.TechyonCollector(self.config, opener=opener, sleep=sleeps.append)
        self.assertEqual([], list(collector.fetch()))
        self.assertEqual((3, [1, 2]), (collector.api_requests, sleeps))

    def test_initial_board_failure_is_not_an_empty_success(self) -> None:
        collector = MODULE.TechyonCollector(self.config, opener=lambda *a, **kw: Response("<html>Login</html>"))
        with self.assertRaisesRegex(ValueError, "missing the vacancy board"):
            list(collector.fetch())

    def test_invalid_or_incomplete_detail_is_rejected(self) -> None:
        for html in ("<html>Not found</html>", detail() + detail(), detail().replace('"title": "Backend Team Lead"', '"title": ""')):
            with self.subTest(html=html[:50]), self.assertRaises(ValueError):
                MODULE.normalize_detail(html, URL)
        with self.assertRaises(ValueError):
            MODULE.normalize_detail(detail(), "https://evil.example/candidati/fake.html")

    def test_invalid_config_fails_closed(self) -> None:
        for text in ("max_pages: true", "max_pages: 0", "max_pages: 1.5", "timeout_seconds: .nan",
                     "timeout_seconds: false", "typo: 3", "version: 2", "[]"):
            self.path.write_text(text, encoding="utf-8")
            with self.subTest(text=text), self.assertRaises(ValueError):
                MODULE.TechyonCollector(self.config)

    def test_discovered_by_standard_collector_factory(self) -> None:
        self.assertIn("techyon", discover_collectors(ROOT / "sources", {}))


if __name__ == "__main__":
    unittest.main()
