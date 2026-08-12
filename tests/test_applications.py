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
    _cv_export_stem,
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

    def __init__(self, score: int, *, model: str | None = None) -> None:
        self.score = score
        if model is not None:
            self.model = model

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

    def _generator(
        self,
        client: FakeClient,
        converter: FakeConverter,
        *,
        document: str | None = None,
    ) -> ApplicationGenerator:
        return ApplicationGenerator(
            self.registry_root,
            [self.profile],
            self.prompt,
            client,
            converter,
            document=document,
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
        self.assertNotIn("simple_life_end_date", manifest)

    def test_cv_export_stem_keeps_company_and_role_focus_without_location_noise(self) -> None:
        self.assertEqual(
            "CV_ValentinNikolaev_grafana_SeniorBackendEngineerDatabasesLokiIngest",
            _cv_export_stem(
                company="Grafana Labs",
                title="Senior Backend Engineer - Databases - Loki Ingest | Germany | Remote",
            ),
        )

    def test_simple_life_cv_date_range_is_preserved_from_draft(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = (
            "# Candidate\n"
            "Backend Engineer\n\n"
            "## Experience\n\n"
            "### Simple.life\n\n"
            "**Software Developer**  \n"
            "November 2023 - July 2026\n\n"
            "- Built Go services.\n\n"
            "Technologies: Go | REST APIs\n\n"
            "### airSlate\n\n"
            "**Software Developer**  \n"
            "February 2021 - August 2023\n\n"
            "Technologies: PHP | Laravel\n"
        )

        self._generator(FakeClient(payload), FakeConverter()).generate_directory(self.directory)

        cv = (self.directory / "application" / "cv.md").read_text(encoding="utf-8")
        self.assertIn("November 2023 - July 2026", cv)
        self.assertIn("February 2021 - August 2023", cv)

    def test_package_does_not_expire_when_calendar_month_changes(self) -> None:
        client = FakeClient()
        generator = self._generator(client, FakeConverter())
        first = generator.generate_directory(self.directory)
        self.now = datetime(2026, 9, 1, tzinfo=timezone.utc)
        second = generator.generate_directory(self.directory)

        self.assertEqual("prepared", first.status)
        self.assertEqual("skipped", second.status)
        self.assertEqual(1, len(client.calls))

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

    def test_application_markdown_hard_word_limits_are_enforced(self) -> None:
        limits = {
            "cv_markdown": 800,
            "cover_letter_markdown": 450,
            "analysis_markdown": 1000,
            "interview_preparation_markdown": 1100,
        }
        for field, limit in limits.items():
            with self.subTest(field=field):
                payload = application_payload()
                payload[field] += "\n" + "word " * (limit + 1)
                with self.assertRaisesRegex(
                    ApplicationError,
                    rf"{field} exceeds {limit}-word limit",
                ):
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
            "Technologies: Go\n\n"
            "### New Co\nSeptember 2016 - Present\n\nTechnologies: PHP\n\n"
            "## Education\n\nUniversity, 2004 - 2008\n"
        )

        result = validate_application_package(
            payload,
            reference_date=datetime(2026, 8, 6, tzinfo=timezone.utc),
        )

        self.assertIn("University, 2004 - 2008", result["cv_markdown"])

    def test_cv_requires_evidence_backed_technologies_for_each_experience_role(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = (
            "# Candidate\nBackend Engineer\n\n"
            "## Experience\n\n"
            "### Complete Co\n\nTechnologies: PHP | Laravel\n\n"
            "### Missing Co\n\n- Built services.\n\n"
            "## Education\n\nUniversity\n"
        )

        with self.assertRaisesRegex(ApplicationError, "Missing Co"):
            validate_application_package(payload)

        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "- Built services.\n\n## Education",
            "- Built services.\n\n**Technologies**: Go | PostgreSQL\n\n## Education",
        )
        result = validate_application_package(payload)
        self.assertIn("**Technologies**: Go | PostgreSQL", result["cv_markdown"])

    def test_cover_letter_accepts_target_role_and_company_context(self) -> None:
        payload = application_payload()
        payload["cover_letter_markdown"] = (
            "# Cover Letter\n\nDear Hiring Team,\n\n"
            "I am applying for the Senior Backend Engineer role at Example.\n"
        )

        result = validate_application_package(
            payload,
            vacancy={
                "metadata": {
                    "title": "Senior Backend Engineer",
                    "company": "Example",
                }
            },
        )

        self.assertIn("Senior Backend Engineer role at Example", result["cover_letter_markdown"])

    def test_prompt_change_invalidates_and_republishes_application(self) -> None:
        generator = self._generator(FakeClient(), FakeConverter())
        first = generator.generate_directory(self.directory)
        application = self.directory / "application"
        manifest_before = yaml.safe_load(
            (application / "manifest.yaml").read_text(encoding="utf-8")
        )

        self.prompt.write_text(
            "Prepare exactly one package with $write-cover-letter.\n",
            encoding="utf-8",
        )

        self.assertFalse(generator.is_current(self.directory))
        second = generator.generate_directory(self.directory)
        manifest_after = yaml.safe_load(
            (application / "manifest.yaml").read_text(encoding="utf-8")
        )

        self.assertEqual("prepared", first.status)
        self.assertEqual("prepared", second.status)
        self.assertNotEqual(
            manifest_before["prompt_version"], manifest_after["prompt_version"]
        )

    def test_repository_prepare_contract_delegates_to_write_cover_letter(self) -> None:
        project_root = Path(__file__).resolve().parents[1]
        prompt = (project_root / "prompts" / "vacancy-application.md").read_text(
            encoding="utf-8"
        )
        prepare = (
            project_root
            / ".agents"
            / "skills"
            / "job-intelligence-workflow"
            / "references"
            / "prepare.md"
        ).read_text(encoding="utf-8")
        workflow = (
            project_root
            / ".agents"
            / "skills"
            / "job-intelligence-workflow"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        agents = (project_root / "AGENTS.md").read_text(encoding="utf-8")
        manual_agent = (
            project_root
            / ".agents"
            / "skills"
            / "manual-vacancy-application"
            / "SKILL.md"
        ).read_text(encoding="utf-8")
        manual_source = (
            project_root / "skills" / "manual-vacancy-application" / "SKILL.md"
        ).read_text(encoding="utf-8")

        self.assertIn("$write-cover-letter", prompt)
        self.assertIn("$write-cover-letter", prepare)
        for contract in (agents, workflow, prepare, prompt):
            self.assertRegex(contract, r"highest\s+installed\s+version")
            self.assertNotRegex(contract, r"version\s+`\d+\.\d+\.\d+")
        self.assertNotIn("Do not mention the exact vacancy title", prompt)
        self.assertNotIn("Use `stop-slop`", prompt)
        self.assertTrue(manual_agent.startswith("---\n"))
        self.assertEqual(manual_source, manual_agent)

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

    def test_codex_draft_client_reads_only_explicit_document(self) -> None:
        draft = self.project / "cv-only-draft"
        draft.mkdir()
        (draft / "cv.md").write_text(
            application_payload()["cv_markdown"], encoding="utf-8"
        )

        client = CodexApplicationDraftClient(
            draft,
            model="codex:gpt-5.6-terra:medium",
            document="cv",
        )

        self.assertEqual(
            {"cv_markdown"},
            set(client.generate(prompt="", candidate_profile="", vacancy={})),
        )

    def test_validate_application_cli_checks_draft_without_publishing(self) -> None:
        draft = self.project / "application-draft"
        draft.mkdir()
        filenames = {
            "cv_markdown": "cv.md",
            "cover_letter_markdown": "cover-letter.md",
            "analysis_markdown": "analysis.md",
            "interview_preparation_markdown": "interview-preparation.md",
        }
        payload = application_payload()
        for field, filename in filenames.items():
            (draft / filename).write_text(payload[field], encoding="utf-8")

        output = StringIO()
        with redirect_stdout(output):
            result = main(
                [
                    "validate-application",
                    self.directory.name,
                    "--registry",
                    str(self.registry_root),
                    "--input",
                    str(draft),
                ]
            )

        self.assertEqual(0, result)
        self.assertIn(f"Application draft valid: {self.directory.name}", output.getvalue())
        self.assertFalse((self.directory / "application").exists())

        (draft / "cover-letter.md").write_text("word " * 451, encoding="utf-8")
        errors = StringIO()
        with redirect_stderr(errors):
            result = main(
                [
                    "validate-application",
                    self.directory.name,
                    "--registry",
                    str(self.registry_root),
                    "--input",
                    str(draft),
                ]
            )
        self.assertEqual(1, result)
        self.assertIn("exceeds 450-word limit", errors.getvalue())
        self.assertFalse((self.directory / "application").exists())

    def test_validate_application_cli_accepts_explicit_cv_only_draft(self) -> None:
        draft = self.project / "cv-only-draft"
        draft.mkdir()
        (draft / "cv.md").write_text(
            application_payload()["cv_markdown"], encoding="utf-8"
        )

        result = main(
            [
                "validate-application",
                self.directory.name,
                "--registry",
                str(self.registry_root),
                "--input",
                str(draft),
                "--document",
                "cv",
            ]
        )

        self.assertEqual(0, result)
        self.assertFalse((self.directory / "application").exists())

    def test_partial_cv_publish_preserves_other_documents_and_cache_scope(self) -> None:
        full_converter = FakeConverter()
        full = self._generator(FakeClient(), full_converter)
        full.generate_directory(self.directory)
        application = self.directory / "application"
        preserved_names = (
            "cover-letter.md",
            "cover-letter.docx",
            "analysis.md",
            "interview-preparation.md",
        )
        preserved = {name: (application / name).read_bytes() for name in preserved_names}

        payload = {
            "cv_markdown": (
                "# Candidate\nBackend Engineer\n\n## Summary\n\n"
                "Updated backend engineer.\n"
            )
        }
        partial_converter = FakeConverter()
        partial = self._generator(
            FakeClient(payload),
            partial_converter,
            document="cv",
        )
        first = partial.generate_directory(self.directory, force=True)
        second = partial.generate_directory(self.directory)

        self.assertEqual("prepared", first.status)
        self.assertEqual("skipped", second.status)
        self.assertEqual(1, len(partial_converter.calls))
        self.assertIn("Updated backend engineer", (application / "cv.md").read_text())
        self.assertEqual(
            preserved,
            {name: (application / name).read_bytes() for name in preserved_names},
        )
        manifest = yaml.safe_load((application / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(
            {"cv", "cover-letter", "analysis", "interview-preparation"},
            set(manifest["documents"]),
        )

    def test_partial_cv_publish_creates_only_cv_outputs_when_no_package_exists(self) -> None:
        payload = {"cv_markdown": application_payload()["cv_markdown"]}
        generator = self._generator(
            FakeClient(payload),
            FakeConverter(),
            document="cv",
        )

        generator.generate_directory(self.directory)

        names = {path.name for path in (self.directory / "application").iterdir()}
        self.assertEqual(
            {
                "cv.md",
                "cv.docx",
                "CV_ValentinNikolaev_example_SeniorBackendEngineer.md",
                "CV_ValentinNikolaev_example_SeniorBackendEngineer.docx",
                "manifest.yaml",
            },
            names,
        )

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

    def test_prepare_cli_publishes_explicit_cv_only_draft(self) -> None:
        sources = self.project / "sources"
        sources.mkdir()
        draft = self.project / "cv-only-draft"
        draft.mkdir()
        (draft / "cv.md").write_text(
            application_payload()["cv_markdown"], encoding="utf-8"
        )
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
                    "--document",
                    "cv",
                ]
            )

        self.assertEqual(0, exit_code)
        application = self.directory / "application"
        self.assertTrue((application / "cv.md").is_file())
        self.assertFalse((application / "cover-letter.md").exists())

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

    def test_pending_prepare_uses_selected_model_profile_for_match_freshness(self) -> None:
        registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: "vacancy-terra",
        )
        created = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="job-terra",
                source_url="https://example.test/jobs/terra",
                title="Senior Backend Engineer Terra",
                company="Example",
                description="Build Go services.",
            )
        )
        directory = self.registry_root / "jobs" / created.directory
        MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeMatchClient(72, model="codex:gpt-5.6-terra:medium"),
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
                    "--model-profile",
                    "terra_medium",
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
