from __future__ import annotations

import base64
import copy
import gzip
import json
import tempfile
import unittest
from dataclasses import asdict
from pathlib import Path

from jobintel.job_alerts import JobAlertCollector, normalize_batch
from jobintel.arc_alerts import go_php_cards, resolve_tracking
from jobintel.registry import Registry


def batch(source="reteinformaticalavoro", *, html=False):
    url = ("https://reteinformaticalavoro.it/lavoro/61566/senior-php?utm_source=mail"
           if source != "indeed" else "https://it.indeed.com/rc/clk?jk=0123456789abcdef&from=mail")
    remote = "Totale" if source != "indeed" else "Lavoro da casa"
    description = f"Senior PHP Developer\nExample Company\nRoma\nRemote working: {remote}\nPHP Laravel\n02/10/26"
    body = description + "\n" + url
    body_key = "body_text"
    if html:
        body = f'<div><h2>Senior PHP Developer</h2><p>Example Company</p><p>Roma</p><p>Remote working: {remote}</p><p>PHP Laravel</p><p>02/10/26</p><a href="{url}">Visualizza</a></div>'
        body_key = "body_html"
    return {"schema_version": 1, "emails": [{
        "message_id": "gmail-123", "sender": f"Indeed <donotreply@jobalert.indeed.com>" if source == "indeed" else "noreply@reteinformaticalavoro.it",
        "subject": "Job Alert PHP", "received_at": "2026-10-04T10:00:00+02:00", body_key: body,
        "jobs": [{"title": "Senior PHP Developer", "company": "Example Company", "source_url": url,
                  "description": description, "location": "Roma", "remote_working": remote,
                  "published_date": "02/10/26"}],
    }]}


class JobAlertsTests(unittest.TestCase):
    def test_arc_resolution_never_follows_final_destination_or_account_links(self):
        from unittest.mock import Mock
        opener = Mock()
        response = Mock(code=302, headers={"Location": "https://arc.dev/t/remote-jobs/senior-php-ab12cd3456?utm=email"})
        opener.open.return_value = response
        url = "http://url8035.arc.dev/ls/click?upn=private"
        self.assertEqual(resolve_tracking(url, opener=opener), "https://arc.dev/dashboard/d/remote-jobs/ab12cd3456")
        self.assertEqual(opener.open.call_count, 1)
        request = opener.open.call_args.args[0]
        self.assertEqual(request.get_method(), "HEAD")
        self.assertTrue(request.full_url.startswith("https://url8035.arc.dev/ls/click?"))
        for destination in ("https://evil.test/job", "https://arc.dev/profile", "https://url8035.arc.dev/wf/unsubscribe?upn=private", url):
            response.headers = {"Location": destination}
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                resolve_tracking(url, opener=opener)

    def test_arc_digest_selects_card_stack_not_subject_or_greeting(self):
        php = '<a href="https://url8035.arc.dev/ls/click?upn=php"><p>Example</p><p>4 days ago</p><p>Backend Engineer</p><p>Permanent</p><p>PHP</p></a>'
        python = php.replace('upn=php', 'upn=python').replace('<p>PHP</p>', '<p>Python</p>')
        selected, skipped = go_php_cards('<p>New Golang Job Recommendations</p>'+php+python)
        self.assertEqual(len(selected), 1)
        self.assertEqual(skipped, 1)
        self.assertEqual(selected[0]["company"], "Example")

    def test_arc_resolved_link_receipt_and_full_posting_grounding(self):
        data = self.arc_batch()
        email = data["emails"][0]
        job = email["jobs"][0]
        direct = job["source_url"]
        tracking = "https://url8035.arc.dev/ls/click?upn=private"
        email["body_html"] = email["body_html"].replace(direct, tracking)
        email["resolved_links"] = {tracking: direct}
        page = 'Example Company\nSenior PHP Developer\nRemote\nRequirements: PHP Laravel\nBenefit: https://example.test/benefits'
        job.update(posting_text=page, description=page, remote_working="Remote")
        del job["published_date"]
        del job["location"]
        normalized, = normalize_batch(data, "arc")
        self.assertEqual(normalized.source_metadata["description_scope"], "posting_text")
        self.assertIn("posting_text_sha256", normalized.source_metadata)
        self.assertNotIn("private", json.dumps(asdict(normalized)))
        job["description"] += '\nInvented requirement'
        with self.assertRaises(ValueError): normalize_batch(data, "arc")
        job["description"] = page
        email["resolved_links"] = {tracking+'missing': direct}
        with self.assertRaises(ValueError): normalize_batch(data, "arc")

    def arc_batch(self):
        data = batch("indeed", html=True)
        email = data["emails"][0]
        email["sender"] = "Arc <talent@arc.dev>"
        old_url = email["jobs"][0]["source_url"]
        url = "https://arc.dev/t/remote-jobs/example-senior-php-ab12cd3456?utm_source=mail#card"
        email["body_html"] = email["body_html"].replace(old_url, url)
        email["jobs"][0]["source_url"] = url
        del email["jobs"][0]["remote_working"]
        return data

    def test_arc_direct_posting_and_exact_sender(self):
        data = self.arc_batch()
        job, = normalize_batch(data, "arc")
        self.assertEqual(job.source_url, "https://arc.dev/dashboard/d/remote-jobs/ab12cd3456")
        self.assertEqual(job.source_job_id, "ab12cd3456")
        self.assertIsNone(job.remote)
        for sender in ("support@arc.dev", "talent@arc.dev.evil.test", "talent@evil.test"):
            data["emails"][0]["sender"] = sender
            with self.subTest(sender=sender), self.assertRaises(ValueError):
                normalize_batch(data, "arc")

    def test_arc_rejects_non_posting_and_unresolved_tracking_links(self):
        for url in ("https://arc.dev/profile", "https://arc.dev/remote-jobs",
                    "https://arc.dev/remote-jobs/j/", "https://evil.test/remote-jobs/j/example",
                    "https://url8035.arc.dev/ls/click?upn=private",
                    "https://arc.dev/remote-jobs/j/example/extra"):
            data = self.arc_batch()
            email = data["emails"][0]
            old = email["jobs"][0]["source_url"]
            email["body_html"] = email["body_html"].replace(old, url)
            email["jobs"][0]["source_url"] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                normalize_batch(data, "arc")

    def test_arc_relative_age_cannot_become_publication_date(self):
        data = self.arc_batch()
        email = data["emails"][0]
        email["body_html"] += "<p>4 days ago</p>"
        email["jobs"][0]["published_date"] = "4 days ago"
        with self.assertRaises(ValueError):
            normalize_batch(data, "arc")
        del email["jobs"][0]["published_date"]
        job, = normalize_batch(data, "arc")
        self.assertIsNone(job.published_at)

    def test_both_sources_normalize_text_and_html_without_tracking(self):
        for source in ("reteinformaticalavoro", "indeed"):
            for html in (False, True):
                with self.subTest(source=source, html=html):
                    job, = normalize_batch(batch(source, html=html), source)
                    self.assertEqual(job.source, source)
                    self.assertEqual(job.published_at, "2026-10-02")
                    self.assertTrue(job.remote)
                    self.assertNotIn("from=", job.source_url)
                    self.assertNotIn("utm_", job.source_url)
                    self.assertEqual(job.source_metadata["received_at"], "2026-10-04T08:00:00+00:00")

    def test_indeed_tracking_destination_decoded_without_network(self):
        data = batch("indeed")
        email = data["emails"][0]
        destination = email["jobs"][0]["source_url"]
        token = base64.urlsafe_b64encode(gzip.compress(json.dumps({"u": destination, "m": "private"}).encode())).decode().rstrip("=")
        tracking = f"https://cts.indeed.com/v3/{token}/signature"
        email["body_text"] = email["body_text"].replace(destination, tracking)
        email["jobs"][0]["source_url"] = tracking
        job, = normalize_batch(data, "indeed")
        self.assertEqual(job.source_url, "https://it.indeed.com/viewjob?jk=0123456789abcdef")
        self.assertNotIn("private", json.dumps(asdict(job)))

    def test_overlap_uses_stable_posting_id_and_newest_received_in_utc(self):
        data = batch()
        newer = copy.deepcopy(data["emails"][0])
        newer["message_id"] = "gmail-newer"
        newer["received_at"] = "2026-10-04T08:30:00Z"
        newer["jobs"][0]["source_url"] = "https://www.reteinformaticalavoro.it/lavoro/61566/changed-slug"
        data["emails"].append(newer)
        job, = normalize_batch(data, "reteinformaticalavoro")
        self.assertEqual(job.source_job_id, "61566")
        self.assertEqual(job.source_metadata["message_id"], "gmail-newer")

    def test_unknown_remote_and_publication_date_stay_unknown(self):
        data = batch()
        del data["emails"][0]["jobs"][0]["remote_working"]
        del data["emails"][0]["jobs"][0]["published_date"]
        job, = normalize_batch(data, "reteinformaticalavoro")
        self.assertIsNone(job.remote)
        self.assertIsNone(job.published_at)

    def test_invalid_evidence_sender_and_non_job_links_fail_closed(self):
        for mutation in ("sender", "description", "source_url", "remote_working", "missing_link", "date", "fields"):
            data = batch()
            email, job = data["emails"][0], data["emails"][0]["jobs"][0]
            if mutation == "sender": email["sender"] = "noreply@reteinformaticalavoro.it.evil.test"
            elif mutation == "description": job["description"] += " Invented salary"
            elif mutation == "source_url": job["source_url"] = "https://reteinformaticalavoro.it/offerte-di-lavoro"
            elif mutation == "remote_working": job["remote_working"] = "No"
            elif mutation == "missing_link": email["body_text"] = job["description"]
            elif mutation == "date": job["published_date"] = "2026-10-04"
            else: job["password"] = "forbidden"
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                normalize_batch(data, "reteinformaticalavoro")

    def test_indeed_rejects_tracking_account_or_external_destination(self):
        for destination in ("https://evil.test/viewjob?jk=0123456789abcdef", "https://it.indeed.com/account", "https://it.indeed.com/viewjob?jk=invalid"):
            data = batch("indeed")
            token = base64.urlsafe_b64encode(gzip.compress(json.dumps({"u": destination}).encode())).decode().rstrip("=")
            tracking = f"https://cts.indeed.com/v3/{token}/signature"
            data["emails"][0]["body_text"] += "\n" + tracking
            data["emails"][0]["jobs"][0]["source_url"] = tracking
            with self.assertRaises(ValueError): normalize_batch(data, "indeed")

    def test_raw_mail_links_and_account_addresses_cannot_become_description(self):
        for suffix in (" https://cts.indeed.com/private", " user@example.test"):
            data = batch()
            email = data["emails"][0]
            email["body_text"] += suffix
            email["jobs"][0]["description"] = email["body_text"]
            with self.assertRaises(ValueError): normalize_batch(data, "reteinformaticalavoro")

    def test_missing_input_is_empty_and_invalid_batch_emits_no_partial_jobs(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mail.json"
            collector = JobAlertCollector({"INDEED_INPUT": str(path)}, "indeed")
            self.assertEqual(list(collector.fetch()), [])
            data = batch("indeed")
            invalid = copy.deepcopy(data["emails"][0])
            invalid["jobs"][0]["company"] = "Invented Company"
            data["emails"].append(invalid)
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaises(ValueError): next(iter(collector.fetch()))
            self.assertEqual(collector.api_requests, 0)

    def test_registry_rerun_and_cross_source_deduplication(self):
        with tempfile.TemporaryDirectory() as directory:
            registry = Registry(Path(directory))
            ril, = normalize_batch(batch(), "reteinformaticalavoro")
            indeed, = normalize_batch(batch("indeed"), "indeed")
            first = registry.upsert(ril)
            again = registry.upsert(ril)
            merged = registry.upsert(indeed)
            self.assertEqual(first.directory, again.directory)
            self.assertEqual(first.directory, merged.directory)
            self.assertEqual(again.status, "unchanged")


if __name__ == "__main__":
    unittest.main()
