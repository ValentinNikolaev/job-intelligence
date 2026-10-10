from __future__ import annotations

import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from jobintel.models import NormalizedJob
from jobintel.remote_feeds import PublicRemoteFeedCollector, exclusion_reason, normalize_json_job, parse_larajobs_feed, timestamp


NOW = datetime(2026, 10, 10, 16, tzinfo=timezone.utc)
DESCRIPTION = "<p>Build production PHP and Go backend services with AWS, Kubernetes, PostgreSQL and queues. Design reliable APIs, work with distributed systems, mentor engineers and own production performance, monitoring and incident resolution.</p>"


def row(**changes):
    value = {"id": 42, "title": "Senior Backend Engineer", "company_name": "Acme",
             "url": "https://remotive.com/remote-jobs/software-dev/42", "description": DESCRIPTION,
             "candidate_required_location": "Europe", "publication_date": "2026-10-09T08:00:00Z"}
    value.update(changes)
    return value


class Response:
    def __init__(self, value):
        self.body = value if isinstance(value, bytes) else json.dumps(value).encode()
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return None
    def read(self, size=-1):
        return self.body[:size] if size >= 0 else self.body


class FeedTests(unittest.TestCase):
    def collector(self, payload, *, source="remotive", **settings):
        folder = tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        path = Path(folder.name) / "config.yaml"
        values = {"version": 1, "enabled": True, "pilot_until": "2026-10-24",
                  "timeout_seconds": 15, "max_items": 100, "max_detail_requests": 0}
        values.update(settings)
        path.write_text(yaml.safe_dump(values))
        self.requests = []
        def open_response(request, **kwargs):
            self.requests.append(request.full_url)
            return Response(payload)
        return PublicRemoteFeedCollector(source, {}, path, opener=open_response, clock=lambda: NOW)

    def test_normalizes_attribution_and_original_date(self):
        job = normalize_json_job("remotive", row())
        self.assertIn("PHP and Go", job.description)
        self.assertEqual("42", job.source_job_id)
        self.assertEqual("2026-10-09T08:00:00Z", job.published_at)
        self.assertEqual(job.source_url, job.source_metadata["attribution_url"])

    def test_one_request_deduplicates_and_rejects_bad_rows_without_losing_valid_jobs(self):
        collector = self.collector({"jobs": [row(), row(), {"title": "broken"}, row(id=43)]})
        self.assertEqual(["42", "43"], [job.source_job_id for job in collector.fetch()])
        self.assertEqual(1, collector.api_requests)
        self.assertEqual(1, collector.errors)
        self.assertEqual(1, collector.filtered["duplicate_id"])

    def test_remoteok_legal_entry_is_not_a_vacancy(self):
        job = {"id": 42, "position": "Senior PHP Backend Engineer", "company": "Acme",
               "url": "https://remoteok.com/remote-jobs/42", "date": "2026-10-09T08:00:00Z",
               "description": DESCRIPTION, "location": "Worldwide"}
        collector = self.collector([{"legal": "Link back to Remote OK"}, job], source="remoteok")
        self.assertEqual(1, len(list(collector.fetch())))
        self.assertEqual(0, collector.errors)

    def test_tags_do_not_make_unrelated_role_a_backend_job(self):
        job = normalize_json_job("remotive", row(title="Voice Artist", tags=["golang", "php"]))
        self.assertEqual("role_mismatch", exclusion_reason(job, NOW))

    def test_go_and_backend_capable_product_titles_are_not_blanket_excluded(self):
        for title in ("Senior Go Engineer", "Senior Product Engineer (Laravel)", "Full-stack Developer (PHP)"):
            with self.subTest(title=title):
                self.assertIsNone(exclusion_reason(normalize_json_job("remotive", row(title=title)), NOW))

    def test_country_and_freshness_guards(self):
        for changes, reason in [
            ({"candidate_required_location": "Poland"}, "unconfirmed_italy_eligibility"),
            ({"candidate_required_location": ""}, "unconfirmed_italy_eligibility"),
            ({"candidate_required_location": "Europe", "description": DESCRIPTION + " UK-only."}, "country_restriction"),
            ({"candidate_required_location": "Europe", "description": DESCRIPTION + " Candidates must be based in France or Spain."}, "country_restriction"),
            ({"publication_date": "2026-09-01"}, "stale"),
            ({"publication_date": "invalid"}, "unknown_publication_date"),
            ({"publication_date": "2026-10-12"}, "future_publication_date"),
        ]:
            with self.subTest(changes=changes):
                self.assertEqual(reason, exclusion_reason(normalize_json_job("remotive", row(**changes)), NOW))

    def test_pilot_expiration_and_disabled_mode_make_no_requests(self):
        for settings in ({"enabled": False}, {"pilot_until": "2026-10-09"}):
            collector = self.collector({"jobs": [row()]}, **settings)
            self.assertEqual([], list(collector.fetch()))
            self.assertEqual(0, collector.api_requests)

    def test_item_cap_and_description_completeness(self):
        collector = self.collector({"jobs": [row(description="PHP"), row(id=43)]}, max_items=1)
        self.assertEqual([], list(collector.fetch()))
        self.assertEqual(1, collector.filtered["incomplete_description"])

    def test_bad_payload_or_oversized_response_fails(self):
        for payload in ({"unexpected": []}, b"x" * 3_000_001):
            collector = self.collector(payload)
            with self.assertRaises(ValueError):
                list(collector.fetch())

    def test_invalid_budget_and_config_fail_closed(self):
        for settings in ({"max_items": 101}, {"max_detail_requests": 1}, {"timeout_seconds": True}, {"unknown": 1}):
            with self.subTest(settings=settings), self.assertRaises(ValueError):
                self.collector({"jobs": []}, **settings)

    def test_rss_employer_location_and_date_are_preserved(self):
        rss = b'<rss xmlns:lj="https://larajobs.com"><channel><item><title>Senior PHP Developer</title><link>https://larajobs.com/job/42</link><pubDate>Fri, 09 Oct 2026 08:00:00 +0000</pubDate><lj:company>Acme</lj:company><lj:location>Remote / Europe</lj:location><description>PHP</description></item></channel></rss>'
        jobs = parse_larajobs_feed(rss)
        self.assertEqual(("Acme", "Remote / Europe", "2026-10-09T08:00:00Z"), (jobs[0].company, jobs[0].location, jobs[0].published_at))
        collector = self.collector(rss, source="larajobs", max_detail_requests=0)
        self.assertEqual([], list(collector.fetch()))
        self.assertEqual(1, collector.api_requests)
        self.assertEqual(1, collector.filtered["detail_budget"])

    def test_rss_external_items_and_entity_declarations_are_rejected(self):
        for rss in (b'<!DOCTYPE rss><rss><channel/></rss>', b'<rss><channel><item><link>https://other.test/job/1</link></item></channel></rss>'):
            with self.subTest(rss=rss), self.assertRaises(ValueError):
                parse_larajobs_feed(rss)

    def test_timestamp_does_not_replace_unknown_with_today(self):
        self.assertIsNone(timestamp("broken"))
        self.assertIsNone(timestamp(None))


if __name__ == "__main__":
    unittest.main()
