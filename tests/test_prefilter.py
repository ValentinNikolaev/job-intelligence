from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

import yaml

from jobintel.models import NormalizedJob
from jobintel.prefilter import RejectedRegistry, prefilter_job


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

    def test_english_requirement_is_green_light_for_local_language_text(self) -> None:
        rejection = prefilter_job(
            make_job(
                description=(
                    "Fluent German is required for local stakeholders. "
                    "Professional English required across the engineering team."
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

    def test_requires_go_or_php_stack(self) -> None:
        rejection = prefilter_job(
            make_job(description="Build Java services with PostgreSQL."),
            now=self.now,
        )

        self.assertIsNotNone(rejection)
        self.assertEqual("tech_stack", rejection.category)
        self.assertIn("Go/Golang or PHP", rejection.reason)

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


if __name__ == "__main__":
    unittest.main()
