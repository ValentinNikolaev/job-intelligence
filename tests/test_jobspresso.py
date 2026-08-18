from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.error import HTTPError


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "jobspresso" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_jobspresso_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
JobspressoCollector = MODULE.JobspressoCollector
parse_feed = MODULE.parse_feed


class FakeResponse:
    def __init__(self, payload: bytes | str) -> None:
        self.payload = payload.encode("utf-8") if isinstance(payload, str) else payload
    def __enter__(self) -> "FakeResponse": return self
    def __exit__(self, *args: object) -> None: return None
    def read(self) -> bytes: return self.payload


def feed(*, post_id: str = "8421", title: str = "Senior Backend Engineer",
         link: str = "https://jobspresso.co/remote-work/backend-engineer/") -> str:
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:content="http://purl.org/rss/1.0/modules/content/"
 xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:job="https://jobspresso.co/rss/">
<channel><item><title><![CDATA[{title}]]></title><link>{link}</link>
<guid>https://jobspresso.co/?post_type=job_listing&amp;p={post_id}</guid>
<job:post-id>{post_id}</job:post-id>
<dc:creator><![CDATA[Acme &amp; Co<br />⚲&nbsp;Remote, Europe]]></dc:creator>
<pubDate>Tue, 18 Aug 2026 10:30:00 +0200</pubDate><category>Engineering</category>
<description><![CDATA[Short excerpt.]]></description>
<content:encoded><![CDATA[<h2>Role</h2><p>Build reliable APIs.</p><ul><li>Go</li><li>PostgreSQL</li></ul>]]></content:encoded>
</item></channel></rss>'''


class JobspressoTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "jobspresso.yaml"
        self.config_path.write_text("version: 1\ntimeout_seconds: 7\n", encoding="utf-8")
    def tearDown(self) -> None: self.temp.cleanup()
    def _config(self) -> dict[str, str]: return {"JOBSPRESSO_CONFIG": str(self.config_path)}

    def test_fetches_only_official_latest_feed_and_counts_request(self) -> None:
        def opener(request: Any, timeout: float) -> FakeResponse:
            self.assertEqual("https://jobspresso.co/jobs/feed/", request.full_url)
            self.assertNotIn("?", request.full_url)
            self.assertEqual(7.0, timeout)
            return FakeResponse(feed())
        collector = JobspressoCollector(self._config(), opener=opener)
        self.assertEqual(1, len(list(collector.fetch())))
        self.assertEqual(1, collector.api_requests)

    def test_normalizes_stable_id_creator_date_and_full_description(self) -> None:
        job = parse_feed(feed())[0]
        self.assertEqual(("jobspresso", "8421"), (job.source, job.source_job_id))
        self.assertEqual(("Acme & Co", "Remote, Europe"), (job.company, job.location))
        self.assertTrue(job.remote)
        self.assertEqual("2026-08-18T08:30:00Z", job.published_at)
        self.assertIn("## Role", job.description)
        self.assertIn("- PostgreSQL", job.description)
        self.assertNotIn("Short excerpt", job.description)
        self.assertEqual(["Engineering"], job.source_metadata["categories"])

    def test_post_id_is_stable_when_title_and_link_change(self) -> None:
        first = parse_feed(feed())[0]
        changed = parse_feed(feed(title="Principal Engineer", link="https://jobspresso.co/new/?ref=x"))[0]
        self.assertEqual(first.source_job_id, changed.source_job_id)

    def test_retries_transient_http_errors(self) -> None:
        attempts = 0
        sleeps: list[float] = []
        def opener(request: Any, timeout: float) -> FakeResponse:
            nonlocal attempts
            attempts += 1
            if attempts < 3: raise HTTPError(request.full_url, 503, "Unavailable", None, None)
            return FakeResponse(feed())
        collector = JobspressoCollector(self._config(), opener=opener, sleep=sleeps.append)
        self.assertEqual(1, len(list(collector.fetch())))
        self.assertEqual((3, [1, 2]), (collector.api_requests, sleeps))

    def test_rejects_unknown_config_and_invalid_xml(self) -> None:
        self.config_path.write_text("version: 1\nunsupported: true\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsupported"):
            JobspressoCollector(self._config())
        with self.assertRaisesRegex(RuntimeError, "invalid XML"):
            parse_feed(b"<rss><item>")


if __name__ == "__main__": unittest.main()
