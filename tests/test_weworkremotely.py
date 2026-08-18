from __future__ import annotations

import importlib.util, sys, tempfile, unittest
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

PATH = Path(__file__).parents[1] / "sources" / "weworkremotely" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_wwr_collector", PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC); sys.modules[SPEC.name] = MODULE; SPEC.loader.exec_module(MODULE)
Collector, parse_feed = MODULE.WeWorkRemotelyCollector, MODULE.parse_feed
PROGRAMMING = "https://weworkremotely.com/categories/remote-programming-jobs.rss"
DEVOPS = "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss"


class Response:
    def __init__(self, value: str): self.value = value.encode()
    def __enter__(self): return self
    def __exit__(self, *args): return None
    def read(self): return self.value


def feed(title="Acme: Senior Platform Engineer", guid="wwr-9988"):
    return f'''<rss xmlns:content="http://purl.org/rss/1.0/modules/content/" xmlns:w="https://weworkremotely.com/rss/"><channel><item>
<title>{title}</title><link>https://weworkremotely.com/remote-jobs/acme-role?source=rss</link><guid>{guid}</guid>
<pubDate>Tue, 18 Aug 2026 09:15:00 +0000</pubDate><w:expires_at>Thu, 17 Sep 2026 09:15:00 +0000</w:expires_at><w:region>Europe</w:region><w:country>Italy</w:country><w:state>Italy</w:state>
<w:skills>Go, Kubernetes; PostgreSQL</w:skills><w:category>Programming</w:category><w:type>Full-Time</w:type>
<description><![CDATA[Short.]]></description><content:encoded><![CDATA[<h2>Role</h2><p>Own the platform.</p><ul><li>Build Go services</li></ul>]]></content:encoded>
</item></channel></rss>'''


class Tests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.path = Path(self.temp.name) / "c.yaml"
        self.path.write_text(f"version: 1\ntimeout_seconds: 8\nfeeds:\n  - name: programming\n    url: {PROGRAMMING}\n  - name: devops\n    url: {DEVOPS}\n", encoding="utf-8")
    def tearDown(self): self.temp.cleanup()
    def config(self): return {"WEWORKREMOTELY_CONFIG": str(self.path)}

    def test_normalizes_full_official_fields(self):
        job = parse_feed(feed())[0]
        self.assertEqual(("weworkremotely", "wwr-9988", "Acme", "Senior Platform Engineer"), (job.source, job.source_job_id, job.company, job.title))
        self.assertEqual(("Europe, Italy", "Full-Time", "2026-08-18T09:15:00Z"), (job.location, job.employment_type, job.published_at))
        self.assertIn("Build Go services", job.description); self.assertNotIn("Short.", job.description)
        self.assertEqual(["Go", "Kubernetes", "PostgreSQL"], job.source_metadata["skills"])
        self.assertEqual(["Europe", "Italy"], job.source_metadata["location_restrictions"])
        self.assertEqual("2026-09-17T09:15:00Z", job.source_metadata["expires_at"])

    def test_dedupes_feeds_and_records_provenance(self):
        requested = []
        def opener(request: Any, timeout: float): requested.append(request.full_url); self.assertEqual(8.0, timeout); return Response(feed())
        collector = Collector(self.config(), opener=opener); jobs = list(collector.fetch())
        self.assertEqual([PROGRAMMING, DEVOPS], requested); self.assertEqual((2, 1), (collector.api_requests, len(jobs)))
        self.assertEqual(["programming", "devops"], [x["feed"] for x in jobs[0].source_metadata["discovered_by"]])

    def test_stable_guid_and_retry(self):
        self.assertEqual(parse_feed(feed())[0].source_job_id, parse_feed(feed(title="Acme: Principal Engineer"))[0].source_job_id)
        self.path.write_text(f"version: 1\nfeeds:\n  - name: p\n    url: {PROGRAMMING}\n", encoding="utf-8")
        attempts = 0; sleeps = []
        def opener(request, timeout):
            nonlocal attempts
            attempts += 1
            if attempts == 1: raise HTTPError(request.full_url, 429, "rate", None, None)
            return Response(feed())
        collector = Collector(self.config(), opener=opener, sleep=sleeps.append); self.assertEqual(1, len(list(collector.fetch())))
        self.assertEqual((2, [1]), (collector.api_requests, sleeps))

    def test_strict_config_and_invalid_xml_title(self):
        self.path.write_text("version: 1\nfeeds:\n  - name: bad\n    url: https://example.com/jobs.rss\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "official HTTPS"): Collector(self.config())
        self.path.write_text("version: 1\nunsupported: true\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "unsupported"): Collector(self.config())
        with self.assertRaisesRegex(RuntimeError, "invalid XML"): parse_feed("<rss>")
        with self.assertRaisesRegex(ValueError, "Company: Role"): parse_feed(feed(title="Engineer"))


if __name__ == "__main__": unittest.main()
