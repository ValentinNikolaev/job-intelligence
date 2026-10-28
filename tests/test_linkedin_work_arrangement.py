from __future__ import annotations

import unittest
from dataclasses import replace
from datetime import datetime, timezone
from unittest.mock import MagicMock, patch

from jobintel.cli import _store_collected_jobs
from jobintel.job_alerts import normalize_batch
from jobintel.models import CollectorSummary
from jobintel.prefilter import prefilter_job
from jobintel.selection_policy import DEFAULT_SELECTION_POLICY_PATH, load_selection_policy


def linkedin_batch(location="Berlin, Germany", arrangement="Hybrid", *, posting=False, explicit=True):
    title, company = "PHP Backend Engineer", "Example Company"
    card = f"{title}\n{company}\n{location}\n{arrangement}"
    url = "https://www.linkedin.com/comm/jobs/view/4481423757/?trackingId=private"
    item = dict(title=title, company=company, source_url=url, description=card, location=location)
    if explicit:
        item["remote_working"] = arrangement
    if posting:
        item["posting_text"] = card + "\nBuild PHP services."
        item["description"] = item["posting_text"]
    return {"schema_version": 1, "emails": [dict(
        message_id="gmail-linkedin", sender="jobalerts-noreply@linkedin.com",
        subject="PHP jobs", received_at="2026-10-28T06:00:00Z",
        body_text=card + "\n" + url, jobs=[item],
    )]}


class LinkedInWorkArrangementTests(unittest.TestCase):
    def check_job(self, **kwargs):
        job, = normalize_batch(linkedin_batch(**kwargs), "linkedin")
        return job, prefilter_job(job, now=datetime(2026, 10, 28, tzinfo=timezone.utc))

    def test_hybrid_outside_italy_or_without_confirmed_country_is_rejected(self):
        for location in ("Berlin, Germany", "London, UK", "European Union", "Rome", "", "It concerns London"):
            with self.subTest(location=location):
                data = linkedin_batch(location=location)
                if not location:
                    del data["emails"][0]["jobs"][0]["location"]
                job, = normalize_batch(data, "linkedin")
                rejection = prefilter_job(job)
                self.assertIsNotNone(rejection)
                self.assertEqual("location_requirement", rejection.category)
                self.assertIn("hybrid", rejection.reason)
                self.assertIsNone(job.remote)

    def test_hybrid_with_confirmed_italian_location_is_allowed(self):
        for location in ("Rome, Italy", "Milano, Italia", "Bologna, IT", "Italy"):
            with self.subTest(location=location):
                job, rejection = self.check_job(location=location)
                self.assertIsNone(rejection)
                self.assertIsNone(job.remote)

    def test_remote_europe_remains_allowed_and_onsite_remains_rejected(self):
        self.assertIsNone(self.check_job(location="Europe", arrangement="Remote")[1])
        self.assertIsNotNone(self.check_job(location="Rome, Italy", arrangement="On-site")[1])

    def test_omitting_optional_field_does_not_hide_explicit_hybrid_label(self):
        job, rejection = self.check_job(explicit=False)
        self.assertEqual("Hybrid", job.source_metadata["remote_working"])
        self.assertIsNotNone(rejection)

    def test_location_and_labeled_arrangement_do_not_bypass_hybrid_filter(self):
        for location, label in (("Berlin, Germany (Hybrid)", ""),
                                ("Berlin, Germany", "Workplace type: Hybrid")):
            data = linkedin_batch(location=location, arrangement=label, explicit=False)
            job, = normalize_batch(data, "linkedin")
            self.assertIsNotNone(prefilter_job(job))

    def test_collector_routes_foreign_hybrid_to_rejections_without_active_upsert(self):
        job, = normalize_batch(linkedin_batch(), "linkedin")
        registry, rejected = MagicMock(), MagicMock()
        policy = load_selection_policy(DEFAULT_SELECTION_POLICY_PATH)
        with patch("jobintel.cli.op.get_store", return_value=None):
            summary = _store_collected_jobs(
                "linkedin", CollectorSummary(source="linkedin", fetched=1),
                [job], registry, rejected, selection_policy=policy,
            )
        registry.upsert.assert_not_called()
        rejected.upsert.assert_called_once()
        self.assertEqual(1, summary.rejected)

    def test_italian_company_or_european_hours_do_not_bypass_hybrid_country(self):
        job, = normalize_batch(linkedin_batch(), "linkedin")
        job = replace(job, description=job.description + "\nCompany founded in Italy. EMEA working hours available.")
        self.assertIsNotNone(prefilter_job(job))

    def test_hybrid_cloud_does_not_change_remote_work_arrangement(self):
        job, = normalize_batch(linkedin_batch(location="Europe", arrangement="Remote"), "linkedin")
        job = replace(job, description=job.description + "\nBuild hybrid cloud infrastructure.")
        self.assertIsNone(prefilter_job(job))

    def test_hybrid_policy_is_configured_and_changes_fingerprint(self):
        job, = normalize_batch(linkedin_batch(), "linkedin")
        policy = load_selection_policy(DEFAULT_SELECTION_POLICY_PATH)
        disabled = replace(policy, location=replace(policy.location, hybrid_italy_only=False))
        self.assertIsNone(prefilter_job(job, policy=disabled))
        self.assertNotEqual(policy.prefilter_fingerprint(), disabled.prefilter_fingerprint())

    def test_browser_posting_can_supply_hybrid_location_and_is_hashed(self):
        data = linkedin_batch(posting=True)
        email = data["emails"][0]
        email["body_text"] = "PHP Backend Engineer\nExample Company\n" + email["jobs"][0]["source_url"]
        job, = normalize_batch(data, "linkedin")
        self.assertEqual("posting_text", job.source_metadata["description_scope"])
        self.assertIn("posting_text_sha256", job.source_metadata)
        self.assertIsNotNone(prefilter_job(job))
        email["jobs"][0]["posting_text"] = email["jobs"][0]["posting_text"].replace("Example Company", "Wrong Company")
        with self.assertRaises(ValueError):
            normalize_batch(data, "linkedin")

    def test_posting_fields_cannot_borrow_evidence_from_another_mail_card(self):
        data = linkedin_batch(posting=True)
        data["emails"][0]["body_text"] += "\nRome, Italy"
        data["emails"][0]["jobs"][0]["location"] = "Rome, Italy"
        with self.assertRaises(ValueError):
            normalize_batch(data, "linkedin")
