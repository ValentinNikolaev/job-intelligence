from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import yaml

from jobintel.collector import discover_collectors
from jobintel.hackernews import HackerNewsCollector, normalize_comment
from jobintel.prefilter import prefilter_job


NOW = datetime(2026, 10, 15, 20, tzinfo=timezone.utc)
DESCRIPTION = ("<p>Build reliable Go and PHP backend services, APIs and asynchronous "
               "processing with PostgreSQL, AWS and Kubernetes. Own production system "
               "design, performance and operational reliability. Mentor engineers.</p>")


def post(**changes):
    value = {"objectID": "123", "parent_id": 100, "created_at": "2026-10-14T12:00:00Z",
             "comment_text": "Acme | Senior Backend Engineer | REMOTE (Europe) | Full-time | EUR 100k-130k" + DESCRIPTION}
    value.update(changes)
    return value


def thread(identity="100", title="Ask HN: Who is hiring? (October 2026)", author="whoishiring"):
    return {"objectID": identity, "title": title, "author": author}


class Response:
    def __init__(self, payload):
        self.body = payload if isinstance(payload, bytes) else json.dumps(payload).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self, size):
        return self.body[:size]


class HackerNewsTests(unittest.TestCase):
    def collector(self, responses, *, now=NOW, **settings):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "config.yaml"
        config = {"version": 1, "enabled": True, "pilot_until": "2026-10-29",
                  "timeout_seconds": 15, "max_pages_per_thread": 3}
        config.update(settings)
        path.write_text(yaml.safe_dump(config), encoding="utf-8")
        values = iter(responses)
        self.requests = []
        def opener(request, **kwargs):
            self.requests.append(request.full_url)
            return Response(next(values))
        return HackerNewsCollector({}, path, opener=opener, clock=lambda: now)

    def test_preserves_identity_original_text_salary_and_date(self):
        job = normalize_comment(post(), "100")
        self.assertEqual("123", job.source_job_id)
        self.assertEqual("Acme", job.company)
        self.assertEqual("Senior Backend Engineer", job.title)
        self.assertEqual("2026-10-14T12:00:00Z", job.published_at)
        self.assertIn("EUR 100k-130k", job.description)
        self.assertIn("EUR 100k-130k", job.source_metadata["original_header"])
        self.assertEqual("https://news.ycombinator.com/item?id=123", job.source_url)
        self.assertIsNone(prefilter_job(job, now=NOW))

    def test_only_top_level_remote_employer_roles_are_normalized(self):
        for change in ({"parent_id": 99}, {"objectID": "bad"}, {"deleted": True},
                       {"comment_text": "Acme | Senior Backend Engineer | ONSITE" + DESCRIPTION},
                       {"comment_text": "Acme | Senior Backend Engineer | NOT REMOTE Europe" + DESCRIPTION},
                       {"comment_text": "Acme | Account Executive | REMOTE Europe" + DESCRIPTION},
                       {"comment_text": "Happy to announce that this role has been filled."}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                normalize_comment(post(**change), "100")

    def test_discovers_official_thread_and_rejects_stale_restricted_and_reply_posts(self):
        rows = [post(), post(), post(objectID="124", parent_id=99),
                post(objectID="125", created_at="2026-10-01T10:00:00Z"),
                post(objectID="126", comment_text="Acme | Senior Go Engineer | Europe / Remote (UK)" + DESCRIPTION),
                post(objectID="127", comment_text="Acme | Senior Go Engineer | REMOTE Europe" + DESCRIPTION + " Candidates must be based in Germany."),
                post(objectID="128", created_at=None)]
        collector = self.collector([
            {"hits": [thread(), thread("200", "Ask HN: Who wants to be hired? (October 2026)"),
                      thread("300", author="impostor")]}, {"hits": rows, "nbPages": 1}])
        self.assertEqual(["123"], [job.source_job_id for job in collector.fetch()])
        self.assertEqual(2, collector.api_requests)
        self.assertEqual(1, collector.filtered["duplicate_id"])
        self.assertEqual(2, collector.filtered["country_restriction"])
        query = parse_qs(urlsplit(self.requests[1]).query)
        self.assertEqual(["comment,story_100"], query["tags"])
        self.assertIn("created_at_i>=", query["numericFilters"][0])

    def test_previous_month_is_read_only_when_in_seven_day_window(self):
        now = datetime(2026, 11, 2, 20, tzinfo=timezone.utc)
        collector = self.collector([
            {"hits": [thread("200", "Ask HN: Who is hiring? (November 2026)"), thread(),
                      thread("50", "Ask HN: Who is hiring? (September 2026)")]},
            {"hits": [], "nbPages": 0}, {"hits": [], "nbPages": 0}],
            now=now, pilot_until="2026-11-15")
        self.assertEqual([], list(collector.fetch()))
        self.assertEqual(3, collector.api_requests)
        self.assertEqual(["comment,story_200", "comment,story_100"],
                         [parse_qs(urlsplit(url).query)["tags"][0] for url in self.requests[1:]])

    def test_page_budget_and_duplicate_ids_bound_work(self):
        collector = self.collector([{"hits": [thread()]},
                                    {"hits": [post()], "nbPages": 10},
                                    {"hits": [post(), post(objectID="124")], "nbPages": 10}],
                                   max_pages_per_thread=2)
        self.assertEqual(["123", "124"], [job.source_job_id for job in collector.fetch()])
        self.assertEqual(3, collector.api_requests)
        self.assertEqual(8, collector.filtered["page_budget"])

    def test_disabled_or_expired_pilot_makes_no_requests(self):
        for settings in ({"enabled": False}, {"pilot_until": "2026-10-14"}):
            collector = self.collector([], **settings)
            self.assertEqual([], list(collector.fetch()))
            self.assertEqual(0, collector.api_requests)

    def test_missing_thread_malformed_and_oversized_responses_fail(self):
        for payload in ({"hits": []}, {"wrong": []}, b"x" * 3_000_001):
            collector = self.collector([payload])
            with self.subTest(payload_type=type(payload)), self.assertRaises(ValueError):
                list(collector.fetch())

    def test_bad_page_count_is_not_a_successful_empty_run(self):
        collector = self.collector([{"hits": [thread()]}, {"hits": [], "nbPages": "bad"}])
        with self.assertRaises(ValueError):
            list(collector.fetch())

    def test_invalid_settings_fail_before_requests(self):
        for settings in ({"max_pages_per_thread": 4}, {"timeout_seconds": True},
                         {"enabled": "yes"}, {"unexpected": 1}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.collector([], **settings)

    def test_source_discovery_and_worldwide_search_configuration(self):
        root = Path(__file__).resolve().parents[1]
        self.assertIn("hackernews", discover_collectors(root / "sources", {}))
        settings = yaml.safe_load((root / "sources/himalayas/config.yaml").read_text())
        self.assertEqual(4, len(settings["queries"]))
        for query in settings["queries"]:
            self.assertEqual("IT", query["country"])
            self.assertIs(False, query["exclude_worldwide"])


if __name__ == "__main__":
    unittest.main()
