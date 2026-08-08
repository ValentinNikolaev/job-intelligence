from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from jobintel.models import NormalizedJob
from jobintel.prefilter import (
    CompanyRetryRule,
    RejectedRegistry,
    load_company_retry_rules,
    prefilter_job,
)


def make_job(**overrides: object) -> NormalizedJob:
    values: dict[str, object] = {
        "source": "direct",
        "source_job_id": "job-1",
        "source_url": "https://jobs.test/job-1",
        "title": "Senior Backend Engineer",
        "company": "Acme",
        "description": "Build Go backend services.",
        "published_at": "2026-07-22T12:00:00Z",
    }
    values.update(overrides)
    return NormalizedJob(**values)  # type: ignore[arg-type]


class PrefilterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.now = datetime(2026, 7, 23, 12, tzinfo=timezone.utc)

    def test_rejects_jobs_older_than_one_week(self) -> None:
        rejection = prefilter_job(
            make_job(published_at="2026-07-15T11:59:59Z"),
            now=self.now,
        )

        self.assertIsNotNone(rejection)
        self.assertEqual("stale", rejection.category)

    def test_rejects_obvious_role_mismatches(self) -> None:
        for title in ("QA Automation Engineer", "Android Developer", "iOS Engineer"):
            with self.subTest(title=title):
                rejection = prefilter_job(make_job(title=title), now=self.now)
                self.assertIsNotNone(rejection)
                self.assertEqual("role_mismatch", rejection.category)

    def test_rejects_explicitly_non_remote_vacancies(self) -> None:
        rejection = prefilter_job(
            make_job(
                description="Build Go services in our Berlin office.",
                remote=False,
                employment_type="Permanent, Full time",
            ),
            now=self.now,
        )

        self.assertIsNotNone(rejection)
        self.assertEqual("location_requirement", rejection.category)
        self.assertIn("non-remote", rejection.reason)

    def test_english_requirement_is_green_light_for_local_language_text(self) -> None:
        rejection = prefilter_job(
            make_job(
                description=(
                    "Fluent German is required for local stakeholders. "
                    "Professional English required across the engineering team. "
                    "Build Go backend services."
                )
            ),
            now=self.now,
        )

        self.assertIsNone(rejection)

    def test_rejects_hard_european_language_without_english(self) -> None:
        for description in (
            "Fluent German is mandatory for this role.",
            "French C1 required for customer workshops.",
            "Spanish B2 required for customer workshops.",
            "Fluent Polish is mandatory for local stakeholders.",
            "Italiano fluente mandatory for daily work with the team.",
        ):
            with self.subTest(description=description):
                rejection = prefilter_job(make_job(description=description), now=self.now)
                self.assertIsNotNone(rejection)
                self.assertEqual("language_requirement", rejection.category)

    def test_allows_russian_ukrainian_and_optional_european_languages(self) -> None:
        for description in (
            "Fluent Russian is required for this Go role.",
            "Ukrainian C1 required for Go partner conversations.",
            "Italian is nice to have for local onboarding on PHP services.",
            "Spanish is optional and only nice to have for Go services.",
            "German would be a plus for PHP development.",
        ):
            with self.subTest(description=description):
                self.assertIsNone(prefilter_job(make_job(description=description), now=self.now))

    def test_rejects_american_continent_time_requirements(self) -> None:
        for description in (
            "Build Go services while working US time zones.",
            "Candidates must be based in North America for this PHP backend role.",
            "Availability required for LATAM time zones on Go platform calls.",
            "Build Go services. Location: Remote (U.S.).",
            "Build Go services. Location: United States (Remote).",
            "Remote work from home, limited to United States candidates for this PHP role.",
        ):
            with self.subTest(description=description):
                rejection = prefilter_job(make_job(description=description), now=self.now)
                self.assertIsNotNone(rejection)
                self.assertIn(rejection.category, {"timezone_requirement", "location_requirement"})

    def test_allows_roles_available_in_emea_and_americas_without_us_time_requirement(self) -> None:
        rejection = prefilter_job(
            make_job(description="Build Go services. Location: available in EMEA and the Americas."),
            now=self.now,
        )

        self.assertIsNone(rejection)

    def test_english_requirement_does_not_bypass_stack_rejections(self) -> None:
        for description, expected in (
            ("Professional English required. Build Java services.", "Go/Golang or PHP"),
            ("Professional English required. Maintain WordPress plugins in PHP.", "WordPress"),
            ("Professional English required. Build Spring Boot services with PHP integrations.", "Spring Boot"),
        ):
            with self.subTest(description=description):
                rejection = prefilter_job(make_job(description=description), now=self.now)
                self.assertIsNotNone(rejection)
                self.assertEqual("tech_stack", rejection.category)
                self.assertIn(expected, rejection.reason)

    def test_allows_remote_us_when_eu_work_availability_is_explicit(self) -> None:
        for description in (
            "Build Go services. Location: Remote (U.S.), but EMEA working hours are available.",
            "Remote United States role for Go engineers working CET hours.",
            "US remote PHP role with explicit Europe timezone overlap.",
        ):
            with self.subTest(description=description):
                self.assertIsNone(prefilter_job(make_job(description=description), now=self.now))

    def test_requires_go_or_php_stack(self) -> None:
        rejection = prefilter_job(
            make_job(description="Build Java services with PostgreSQL."),
            now=self.now,
        )

        self.assertIsNotNone(rejection)
        self.assertEqual("tech_stack", rejection.category)
        self.assertIn("Go/Golang or PHP", rejection.reason)

    def test_rejects_reported_non_target_stack_regressions(self) -> None:
        cases = (
            (
                "Strong hands-on experience with Java, Spring Boot, React, and AWS.",
                "Spring Boot",
            ),
            (
                "Very proficient in Node.js and JavaScript programming for backend services.",
                "Go/Golang or PHP",
            ),
        )
        for description, expected_reason in cases:
            with self.subTest(description=description):
                rejection = prefilter_job(make_job(description=description), now=self.now)
                self.assertIsNotNone(rejection)
                self.assertEqual("tech_stack", rejection.category)
                self.assertIn(expected_reason, rejection.reason)

    def test_allows_go_and_php_aliases(self) -> None:
        for description in (
            "Build Golang APIs.",
            "Build Go backend services.",
            "Maintain PHP 8.3 applications.",
            "Maintain PHP8 applications.",
        ):
            with self.subTest(description=description):
                self.assertIsNone(prefilter_job(make_job(description=description), now=self.now))

    def test_rejects_blacklisted_stacks(self) -> None:
        for description, reason in (
            ("Build Java services with Spring Boot and PHP integrations.", "Spring Boot"),
            ("Build Python and R data services with a small PHP API.", "Python + R"),
            ("Build Python and Julia data services with a small Go backend.", "Python + Julia"),
        ):
            with self.subTest(description=description):
                rejection = prefilter_job(make_job(description=description), now=self.now)
                self.assertIsNotNone(rejection)
                self.assertEqual("tech_stack", rejection.category)
                self.assertIn(reason, rejection.reason)

    def test_rejects_cms_vacancies(self) -> None:
        cases = (
            ("TYPO3 Certified Developer", "Build PHP extensions.", "TYPO3"),
            ("Senior Backend Engineer", "Maintain WordPress plugins in PHP.", "WordPress"),
            ("Senior Backend Engineer", "Build Word Press themes and PHP APIs.", "WordPress"),
            ("Senior PHP Developer", "Own Drupal modules for customer sites.", "Drupal"),
        )
        for title, description, reason in cases:
            with self.subTest(title=title, description=description):
                rejection = prefilter_job(
                    make_job(title=title, description=description),
                    now=self.now,
                )
                self.assertIsNotNone(rejection)
                self.assertEqual("tech_stack", rejection.category)
                self.assertIn(reason, rejection.reason)

    def test_rejected_registry_always_writes_reason(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "registry"
            job = make_job(title="QA Automation Engineer")
            rejection = prefilter_job(job, now=self.now)
            self.assertIsNotNone(rejection)

            RejectedRegistry(root).upsert(job, rejection)
            directories = list((root / "rejected").iterdir())
            self.assertEqual(1, len(directories))
            meta = yaml.safe_load((directories[0] / "meta.yaml").read_text(encoding="utf-8"))
            markdown = (directories[0] / "job.md").read_text(encoding="utf-8")

            self.assertEqual("role_mismatch", meta["rejection_category"])
            self.assertTrue(meta["rejection_reason"])
            self.assertIn("Posted: 2026-07-22T12:00:00Z", markdown)
            self.assertIn("## Rejection", markdown)
            self.assertIn("Reason:", markdown)

    def test_rejects_company_before_cv_retry_date(self) -> None:
        rejection = prefilter_job(
            make_job(company="Grafana Labs", description="Build Go backend services."),
            now=datetime(2026, 7, 23, 12, tzinfo=timezone.utc),
            company_retry_rules=(
                CompanyRetryRule(
                    company="Grafana",
                    aliases=("Grafana Labs",),
                    allow_after=datetime(2027, 2, 1, tzinfo=timezone.utc).date(),
                    reason="CV rejected; retry allowed from February 2027.",
                ),
            ),
        )

        self.assertIsNotNone(rejection)
        self.assertEqual("company_retry_block", rejection.category)
        self.assertIn("2027-02-01", rejection.reason)

    def test_allows_company_on_retry_date(self) -> None:
        rejection = prefilter_job(
            make_job(
                company="Grafana Labs",
                description="Build Go backend services.",
                published_at="2027-02-01T09:00:00Z",
            ),
            now=datetime(2027, 2, 1, 12, tzinfo=timezone.utc),
            company_retry_rules=(
                CompanyRetryRule(
                    company="Grafana",
                    aliases=("Grafana Labs",),
                    allow_after=datetime(2027, 2, 1, tzinfo=timezone.utc).date(),
                    reason="CV rejected; retry allowed from February 2027.",
                ),
            ),
        )

        self.assertIsNone(rejection)

    def test_loads_company_retry_rules_from_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            profile = Path(temporary) / "profile.yaml"
            profile.write_text(
                yaml.safe_dump(
                    {
                        "company_retry_after": [
                            {
                                "company": "Grafana",
                                "aliases": ["Grafana Labs"],
                                "allow_after": "2027-02-01",
                                "reason": "Retry later.",
                            },
                            {
                                "company": "SparkFabrik",
                                "aliases": ["SparkFabrik S.r.l."],
                                "allow_after": "2027-02-01",
                                "reason": "Strong Italian language level required.",
                            }
                        ]
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )

            rules = load_company_retry_rules(profile)

            self.assertEqual(2, len(rules))
            self.assertTrue(rules[0].matches("Grafana Labs"))
            self.assertTrue(rules[1].matches("SparkFabrik S.r.l."))
            self.assertEqual(
                datetime(2027, 2, 1, tzinfo=timezone.utc).date(),
                rules[0].allow_after,
            )


if __name__ == "__main__":
    unittest.main()
