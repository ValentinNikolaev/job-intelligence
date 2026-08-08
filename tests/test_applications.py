from __future__ import annotations

import tempfile
import unittest
import os
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Mapping
from unittest.mock import patch

import yaml

from jobintel.applications import (
    ApplicationError,
    ApplicationGenerator,
    CodexApplicationDraftClient,
    _apply_simple_life_cv_end_date,
    _cv_export_stem,
    _simple_life_cv_end_date,
    _publish_staged_package,
    resolve_job_directories,
    validate_application_package,
)
from jobintel.cli import main
from jobintel.matching import MatchAnalyzer
from jobintel.models import NormalizedJob
from jobintel.registry import Registry


def application_payload() -> dict[str, str]:
    analysis_headings = (
        "Vacancy Summary",
        "Company Research",
        "Initial Resume Audit",
        "Strict Hiring Manager Review",
        "Red Flags",
        "ATS Keyword Analysis",
        "Major CV Changes",
        "Final Quality Gate",
        "Recommendation",
    )
    interview_headings = (
        "Recruiter / HR Screening",
        "Culture Fit / Behavioral Interview",
        "Technical Interview",
        "CV Deep-Dive Questions",
        "Company-Specific Preparation",
        "Preparation Plan",
        "Questions to Ask",
    )
    return {
        "cv_markdown": "# Candidate\nBackend Engineer\n\n## Summary\n\nBackend engineer.\n",
        "cover_letter_markdown": "# Cover Letter\n\nDear Hiring Team,\n\nRelevant experience.\n",
        "analysis_markdown": "# Application Analysis\n\n"
        + "\n\n".join(f"## {heading}\n\nEvidence." for heading in analysis_headings)
        + "\n",
        "interview_preparation_markdown": "# Interview Preparation\n\n"
        + "\n\n".join(f"## {heading}\n\nPrepare evidence." for heading in interview_headings)
        + "\n",
    }


class FakeClient:
    model = "test-model"

    def __init__(self, payload: Mapping[str, Any] | None = None) -> None:
        self.payload = payload or application_payload()
        self.calls: list[dict[str, Any]] = []

    def generate(
        self,
        *,
        prompt: str,
        candidate_profile: str,
        vacancy: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        self.calls.append(
            {
                "prompt": prompt,
                "candidate_profile": candidate_profile,
                "vacancy": vacancy,
            }
        )
        return self.payload


class FakeConverter:
    def __init__(self, *, fail: bool = False) -> None:
        self.fail = fail
        self.calls: list[tuple[Path, Path]] = []

    def convert(self, source: Path, target: Path) -> None:
        self.calls.append((source, target))
        if self.fail:
            raise ApplicationError("conversion failed")
        target.write_bytes(b"PK\x03\x04fake-docx")


class FakeMatchClient:
    model = "codex:gpt-5.6-luna:low"

    def __init__(self, score: int) -> None:
        self.score = score

    def analyze(self, **_: object) -> Mapping[str, Any]:
        return {
            "score": self.score,
            "recommendation": "strong_match" if self.score >= 80 else "possible_match",
            "summary": "Evidence-based match.",
            "strengths": ["Backend experience"],
            "gaps": [],
            "concerns": [],
            "hard_rejection": False,
            "hard_rejection_reason": None,
        }


class ApplicationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.registry_root = self.project / "registry"
        self.profile = self.project / "candidate.md"
        self.profile.write_text("# Candidate\n\nBackend engineer using Go.\n", encoding="utf-8")
        self.prompt = self.project / "prompt.md"
        self.prompt.write_text("Prepare exactly one application package.\n", encoding="utf-8")
        self.now = datetime.now(timezone.utc).replace(microsecond=0)
        registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: "vacancy-1",
        )
        created = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="job-1",
                source_url="https://example.test/jobs/1",
                title="Senior Backend Engineer",
                company="Example",
                description="Build Go services.",
                location="Remote Europe",
                remote=True,
            )
        )
        self.directory = self.registry_root / "jobs" / created.directory
        (self.directory / "company.md").write_text(
            "# Example\n\nA product company.\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _generator(self, client: FakeClient, converter: FakeConverter) -> ApplicationGenerator:
        return ApplicationGenerator(
            self.registry_root,
            [self.profile],
            self.prompt,
            client,
            converter,
            clock=lambda: self.now,
        )

    def test_generates_complete_package_and_skips_matching_versions(self) -> None:
        client = FakeClient()
        converter = FakeConverter()
        generator = self._generator(client, converter)
        profile_before = self.profile.read_bytes()

        first = generator.generate_directory(self.directory)
        second = generator.generate_directory(self.directory)

        application = self.directory / "application"
        expected = {
            "cv.md",
            "cv.docx",
            "CV_ValentinNikolaev_example_SeniorBackendEngineer.md",
            "CV_ValentinNikolaev_example_SeniorBackendEngineer.docx",
            "cover-letter.md",
            "cover-letter.docx",
            "analysis.md",
            "interview-preparation.md",
            "manifest.yaml",
        }
        self.assertEqual("prepared", first.status)
        self.assertEqual("skipped", second.status)
        self.assertEqual(expected, {path.name for path in application.iterdir()})
        self.assertEqual(1, len(client.calls))
        self.assertEqual(2, len(converter.calls))
        self.assertEqual(profile_before, self.profile.read_bytes())
        self.assertEqual(
            "A product company.",
            client.calls[0]["vacancy"]["provided_company_information"].splitlines()[-1],
        )
        manifest = yaml.safe_load((application / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual("test-model", manifest["model"])
        self.assertEqual(self.now.isoformat().replace("+00:00", "Z"), manifest["generated_at"])
        self.assertEqual(
            "CV_ValentinNikolaev_example_SeniorBackendEngineer",
            manifest["cv_export_stem"],
        )
        self.assertEqual(_simple_life_cv_end_date(self.now), manifest["simple_life_end_date"])

    def test_cv_export_stem_keeps_company_and_role_focus_without_location_noise(self) -> None:
        self.assertEqual(
            "CV_ValentinNikolaev_grafana_SeniorBackendEngineerDatabasesLokiIngest",
            _cv_export_stem(
                company="Grafana Labs",
                title="Senior Backend Engineer - Databases - Loki Ingest | Germany | Remote",
            ),
        )

    def test_simple_life_cv_end_date_uses_previous_calendar_month(self) -> None:
        self.assertEqual(
            "June 2026",
            _simple_life_cv_end_date(datetime(2026, 7, 24, tzinfo=timezone.utc)),
        )
        self.assertEqual(
            "December 2025",
            _simple_life_cv_end_date(datetime(2026, 1, 3, tzinfo=timezone.utc)),
        )

    def test_simple_life_cv_date_range_is_rewritten_before_publication(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = (
            "# Candidate\n"
            "Backend Engineer\n\n"
            "## Experience\n\n"
            "### Simple.life\n\n"
            "**Software Developer**  \n"
            "November 2023 - Present\n\n"
            "- Built Go services.\n\n"
            "### airSlate\n\n"
            "**Software Developer**  \n"
            "February 2021 - August 2023\n"
        )

        self._generator(FakeClient(payload), FakeConverter()).generate_directory(self.directory)

        cv = (self.directory / "application" / "cv.md").read_text(encoding="utf-8")
        self.assertIn(f"November 2023 - {_simple_life_cv_end_date(self.now)}", cv)
        self.assertIn("February 2021 - August 2023", cv)

    def test_simple_app_heading_is_supported_for_linkedin_drafts(self) -> None:
        markdown = (
            "# Candidate\n\n"
            "### Simple App\n\n"
            "#### Software Developer\n"
            "November 2023 - March 2026\n\n"
            "### airSlate\n"
            "February 2021 - August 2023\n"
        )

        updated = _apply_simple_life_cv_end_date(markdown, "June 2026")

        self.assertIn("November 2023 - June 2026", updated)
        self.assertIn("February 2021 - August 2023", updated)

    def test_conversion_failure_preserves_previous_complete_package(self) -> None:
        original = self._generator(FakeClient(), FakeConverter())
        original.generate_directory(self.directory)
        cv_before = (self.directory / "application" / "cv.md").read_bytes()
        manifest_before = (self.directory / "application" / "manifest.yaml").read_bytes()
        self.profile.write_text("# Candidate\n\nBackend engineer using Go and PHP.\n", encoding="utf-8")

        failing = self._generator(FakeClient(), FakeConverter(fail=True))
        with self.assertRaises(ApplicationError):
            failing.generate_directory(self.directory)

        self.assertEqual(cv_before, (self.directory / "application" / "cv.md").read_bytes())
        self.assertEqual(
            manifest_before, (self.directory / "application" / "manifest.yaml").read_bytes()
        )

    def test_directory_swap_failure_rolls_back_complete_previous_package(self) -> None:
        staging = self.directory / ".application-staging"
        target = self.directory / "application"
        staging.mkdir()
        target.mkdir()
        (staging / "cv.md").write_text("new", encoding="utf-8")
        (staging / "manifest.yaml").write_text("files: [cv.md]", encoding="utf-8")
        (target / "cv.md").write_text("old", encoding="utf-8")
        (target / "manifest.yaml").write_text("old: true", encoding="utf-8")
        real_replace = os.replace

        def fail_new_package(source: object, destination: object) -> None:
            if Path(source) == staging and Path(destination) == target:
                raise OSError("simulated directory swap failure")
            real_replace(source, destination)

        with patch("jobintel.applications.os.replace", side_effect=fail_new_package):
            with self.assertRaises(OSError):
                _publish_staged_package(staging, target, ["cv.md"])

        self.assertEqual("old", (target / "cv.md").read_text(encoding="utf-8"))
        self.assertEqual("old: true", (target / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual([], list(self.directory.glob(".application.*.backup")))

    def test_permission_denied_on_default_application_uses_marked_fallback_directory(self) -> None:
        target = self.directory / "application"
        target.mkdir()
        (target / "cv.md").write_text("old", encoding="utf-8")
        real_replace = os.replace

        def deny_default_application(source: object, destination: object) -> None:
            if Path(source) == target:
                raise PermissionError("access denied")
            real_replace(source, destination)

        with patch("jobintel.applications.os.replace", side_effect=deny_default_application):
            result = self._generator(FakeClient(), FakeConverter()).generate_directory(self.directory)

        fallback = self.directory / "application-codex"
        meta = yaml.safe_load((self.directory / "meta.yaml").read_text(encoding="utf-8"))
        self.assertEqual("prepared", result.status)
        self.assertEqual("application-codex", meta["application_directory"])
        self.assertTrue((fallback / "manifest.yaml").is_file())
        self.assertEqual("old", (target / "cv.md").read_text(encoding="utf-8"))
        self.assertTrue(self._generator(FakeClient(), FakeConverter()).is_current(self.directory))

    def test_invalid_markdown_contract_is_not_published(self) -> None:
        payload = application_payload()
        payload["analysis_markdown"] = "# Missing required sections\n"
        generator = self._generator(FakeClient(payload), FakeConverter())

        with self.assertRaises(ApplicationError):
            generator.generate_directory(self.directory)

        self.assertFalse((self.directory / "application").exists())

    def test_forbidden_zend_certification_phrase_is_rejected(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] += "\n## Certifications\n\n- Zend Certified PHP Developer\n"

        with self.assertRaisesRegex(ApplicationError, "forbidden phrase"):
            validate_application_package(payload)

    def test_cv_headline_must_immediately_follow_candidate_name(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = "# Candidate\n\nBackend Engineer\n\n## Summary\n\nBackend engineer.\n"

        with self.assertRaisesRegex(ApplicationError, "immediately after the candidate name"):
            validate_application_package(
                payload,
                vacancy={"metadata": {"title": "Senior Backend Engineer"}},
            )

    def test_cv_headline_must_align_with_vacancy_title_terms(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = "# Candidate\nSoftware Engineer\n\n## Summary\n\nBackend engineer.\n"

        with self.assertRaisesRegex(ApplicationError, "headline is not aligned"):
            validate_application_package(
                payload,
                vacancy={"metadata": {"title": "Senior Backend Engineer"}},
            )

    def test_cv_headline_accepts_vacancy_specific_supported_term(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = "# Candidate\nBackend Engineer\n\n## Summary\n\nBackend engineer.\n"

        result = validate_application_package(
            payload,
            vacancy={"metadata": {"title": "Senior Backend Engineer"}},
        )

        self.assertIn("Backend Engineer", result["cv_markdown"])

    def test_cv_experience_rejects_employment_older_than_ten_years(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = (
            "# Candidate\nBackend Engineer\n\n"
            "## Experience\n\n### Legacy Co\n2008 - 2015\n\n"
            "## Education\n\nUniversity, 2004 - 2008\n"
        )

        with self.assertRaisesRegex(ApplicationError, "more than 10 years ago"):
            validate_application_package(
                payload,
                reference_date=datetime(2026, 8, 6, tzinfo=timezone.utc),
            )

    def test_cv_age_rule_is_scoped_to_experience_and_allows_recent_roles(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = (
            "# Candidate\nBackend Engineer\n\n"
            "## Experience\n\n### Current Co\nJuly 2015 - August 2016\n\n"
            "### New Co\nSeptember 2016 - Present\n\n"
            "## Education\n\nUniversity, 2004 - 2008\n"
        )

        result = validate_application_package(
            payload,
            reference_date=datetime(2026, 8, 6, tzinfo=timezone.utc),
        )

        self.assertIn("University, 2004 - 2008", result["cv_markdown"])

    def test_cover_letter_must_not_repeat_vacancy_title(self) -> None:
        payload = application_payload()
        payload["cover_letter_markdown"] = (
            "# Cover Letter\n\nDear Hiring Team,\n\n"
            "I am interested in the Senior Backend Engineer role.\n"
        )

        with self.assertRaisesRegex(ApplicationError, "exact vacancy title"):
            validate_application_package(
                payload,
                vacancy={
                    "metadata": {
                        "title": "Senior Backend Engineer",
                        "company": "Example",
                    }
                },
            )

    def test_cover_letter_must_not_repeat_company_name(self) -> None:
        payload = application_payload()
        payload["cover_letter_markdown"] = (
            "# Cover Letter\n\nDear Hiring Team,\n\n"
            "Example seems to value reliable backend delivery.\n"
        )

        with self.assertRaisesRegex(ApplicationError, "company name"):
            validate_application_package(
                payload,
                vacancy={
                    "metadata": {
                        "title": "Senior Backend Engineer",
                        "company": "Example",
                    }
                },
            )

    def test_codex_draft_client_reads_markdown_without_network(self) -> None:
        draft = self.project / "application-draft"
        draft.mkdir()
        payload = application_payload()
        filenames = {
            "cv_markdown": "cv.md",
            "cover_letter_markdown": "cover-letter.md",
            "analysis_markdown": "analysis.md",
            "interview_preparation_markdown": "interview-preparation.md",
        }
        for field, filename in filenames.items():
            (draft / filename).write_text(payload[field], encoding="utf-8")
        client = CodexApplicationDraftClient(
            draft, model="codex:gpt-5.5:medium"
        )
        result = client.generate(
            prompt="One vacancy only.",
            candidate_profile="Candidate",
            vacancy={"title": "Engineer"},
        )

        self.assertIn("cv_markdown", result)
        self.assertEqual("codex:gpt-5.5:medium", client.model)

    def test_resolves_directory_name_id_and_all(self) -> None:
        by_name = resolve_job_directories(self.registry_root, self.directory.name)
        by_id = resolve_job_directories(self.registry_root, "vacancy-1")
        all_jobs = resolve_job_directories(self.registry_root, "all")

        self.assertEqual([self.directory.resolve()], by_name)
        self.assertEqual(by_name, by_id)
        self.assertEqual(by_name, all_jobs)

    def test_prepare_cli_publishes_one_codex_draft(self) -> None:
        sources = self.project / "sources"
        sources.mkdir()
        draft = self.project / "draft"
        draft.mkdir()
        for field, filename in {
            "cv_markdown": "cv.md",
            "cover_letter_markdown": "cover-letter.md",
            "analysis_markdown": "analysis.md",
            "interview_preparation_markdown": "interview-preparation.md",
        }.items():
            (draft / filename).write_text(application_payload()[field], encoding="utf-8")
        MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeMatchClient(72),
            clock=lambda: self.now,
        ).analyze_directory(self.directory)

        with patch("jobintel.cli.HostMarkdownDocxConverter", return_value=FakeConverter()):
            exit_code = main(
                [
                    "prepare",
                    self.directory.name,
                    "--registry",
                    str(self.registry_root),
                    "--sources",
                    str(sources),
                    "--profile",
                    str(self.profile),
                    "--input",
                    str(draft),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(0, exit_code)
        self.assertTrue((self.directory / "application" / "manifest.yaml").is_file())

    def test_prepare_cli_publishes_isolated_batch_drafts(self) -> None:
        sources = self.project / "sources"
        sources.mkdir()
        registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: "vacancy-2",
        )
        created = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="job-2",
                source_url="https://example.test/jobs/2",
                title="Senior Backend Engineer",
                company="Second Example",
                description="Build Go services.",
                location="Remote Europe",
                remote=True,
            )
        )
        second = self.registry_root / "jobs" / created.directory
        for directory in (self.directory, second):
            MatchAnalyzer(
                self.registry_root,
                [self.profile],
                FakeMatchClient(72),
                clock=lambda: self.now,
            ).analyze_directory(directory)

        draft_root = self.project / "draft-batch"
        markers: dict[str, str] = {}
        for index, directory in enumerate((self.directory, second), start=1):
            draft = draft_root / directory.name
            draft.mkdir(parents=True)
            payload = application_payload()
            marker = f"Isolated batch draft {index}."
            markers[directory.name] = marker
            payload["analysis_markdown"] += f"\n{marker}\n"
            for field, filename in {
                "cv_markdown": "cv.md",
                "cover_letter_markdown": "cover-letter.md",
                "analysis_markdown": "analysis.md",
                "interview_preparation_markdown": "interview-preparation.md",
            }.items():
                (draft / filename).write_text(payload[field], encoding="utf-8")

        with patch("jobintel.cli.HostMarkdownDocxConverter", return_value=FakeConverter()):
            exit_code = main(
                [
                    "prepare",
                    self.directory.name,
                    created.vacancy_id,
                    "--registry",
                    str(self.registry_root),
                    "--sources",
                    str(sources),
                    "--profile",
                    str(self.profile),
                    "--input",
                    str(draft_root),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(0, exit_code)
        for directory in (self.directory, second):
            analysis = (directory / "application" / "analysis.md").read_text(encoding="utf-8")
            self.assertIn(markers[directory.name], analysis)
            other_markers = set(markers.values()) - {markers[directory.name]}
            self.assertTrue(all(marker not in analysis for marker in other_markers))

    def test_prepare_cli_rejects_more_than_ten_vacancies(self) -> None:
        errors = StringIO()
        with redirect_stderr(errors):
            exit_code = main(
                [
                    "prepare",
                    *(f"vacancy-{index}" for index in range(11)),
                    "--registry",
                    str(self.registry_root),
                    "--profile",
                    str(self.profile),
                    "--input",
                    str(self.project / "draft-batch"),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(2, exit_code)
        self.assertIn("at most 10 vacancies", errors.getvalue())

    def test_prepare_cli_rejects_automatic_all_selection(self) -> None:
        errors = StringIO()
        with redirect_stderr(errors):
            exit_code = main(
                [
                    "prepare",
                    "all",
                    "--registry",
                    str(self.registry_root),
                    "--profile",
                    str(self.profile),
                    "--input",
                    str(self.project / "draft-batch"),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(2, exit_code)
        self.assertIn("automatic preparation selection is disabled", errors.getvalue())

    def test_pending_prepare_all_is_disabled_for_manual_selection(self) -> None:
        directories: dict[int, str] = {}
        for score in (64, 65, 74, 75):
            registry = Registry(
                self.registry_root,
                clock=lambda: self.now,
                id_factory=lambda score=score: f"vacancy-{score}",
            )
            created = registry.upsert(
                NormalizedJob(
                    source="direct",
                    source_job_id=f"job-{score}",
                    source_url=f"https://example.test/jobs/{score}",
                    title=f"Backend Engineer {score}",
                    company="Example",
                    description="Build Go services.",
                )
            )
            directory = self.registry_root / "jobs" / created.directory
            MatchAnalyzer(
                self.registry_root,
                [self.profile],
                FakeMatchClient(score),
                clock=lambda: self.now,
            ).analyze_directory(directory)
            directories[score] = directory.name

        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "pending",
                    "prepare",
                    "all",
                    "--registry",
                    str(self.registry_root),
                    "--profile",
                    str(self.profile),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(0, exit_code)
        self.assertIn("Automatic preparation queue is disabled", output.getvalue())
        self.assertNotIn(directories[64], output.getvalue())
        self.assertNotIn(directories[65], output.getvalue())
        self.assertNotIn(directories[74], output.getvalue())
        self.assertNotIn(directories[75], output.getvalue())

    def test_pending_prepare_explicit_vacancy_still_checks_eligibility(self) -> None:
        registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: "vacancy-eligible",
        )
        created = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="job-eligible",
                source_url="https://example.test/jobs/eligible",
                title="Backend Engineer Eligible",
                company="Example",
                description="Build Go services.",
            )
        )
        directory = self.registry_root / "jobs" / created.directory
        MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeMatchClient(72),
            clock=lambda: self.now,
        ).analyze_directory(directory)

        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "pending",
                    "prepare",
                    created.vacancy_id,
                    "--registry",
                    str(self.registry_root),
                    "--profile",
                    str(self.profile),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(0, exit_code)
        self.assertIn(created.directory, output.getvalue())

    def test_pending_prepare_accepts_explicit_batch(self) -> None:
        registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: "vacancy-batch-2",
        )
        created = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="job-batch-2",
                source_url="https://example.test/jobs/batch-2",
                title="Senior Backend Engineer",
                company="Batch Example",
                description="Build Go services.",
            )
        )
        second = self.registry_root / "jobs" / created.directory
        for directory in (self.directory, second):
            MatchAnalyzer(
                self.registry_root,
                [self.profile],
                FakeMatchClient(72),
                clock=lambda: self.now,
            ).analyze_directory(directory)

        output = StringIO()
        with redirect_stdout(output):
            exit_code = main(
                [
                    "pending",
                    "prepare",
                    "vacancy-1",
                    created.vacancy_id,
                    "--registry",
                    str(self.registry_root),
                    "--profile",
                    str(self.profile),
                    "--workflow",
                    "prepare",
                ]
            )

        self.assertEqual(0, exit_code)
        self.assertIn(self.directory.name, output.getvalue())
        self.assertIn(second.name, output.getvalue())


if __name__ == "__main__":
    unittest.main()
