from __future__ import annotations

import tempfile
import unittest
import os
from contextlib import redirect_stdout
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
    _publish_staged_package,
    resolve_job_directories,
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
        "cv_markdown": "# Candidate\n\n## Summary\n\nBackend engineer.\n",
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
        self.now = datetime(2026, 7, 22, 20, 0, tzinfo=timezone.utc)
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
        self.assertEqual("2026-07-22T20:00:00Z", manifest["generated_at"])

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

    def test_invalid_markdown_contract_is_not_published(self) -> None:
        payload = application_payload()
        payload["analysis_markdown"] = "# Missing required sections\n"
        generator = self._generator(FakeClient(payload), FakeConverter())

        with self.assertRaises(ApplicationError):
            generator.generate_directory(self.directory)

        self.assertFalse((self.directory / "application").exists())

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

    def test_pending_prepare_queues_are_disjoint_and_exclude_low_scores(self) -> None:
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

        normal = StringIO()
        with redirect_stdout(normal):
            normal_exit = main(
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
        priority = StringIO()
        with redirect_stdout(priority):
            priority_exit = main(
                [
                    "pending",
                    "prepare",
                    "all",
                    "--registry",
                    str(self.registry_root),
                    "--profile",
                    str(self.profile),
                    "--workflow",
                    "prepare-priority",
                ]
            )

        self.assertEqual(0, normal_exit)
        self.assertEqual(0, priority_exit)
        self.assertNotIn(directories[64], normal.getvalue())
        self.assertIn(directories[65], normal.getvalue())
        self.assertIn(directories[74], normal.getvalue())
        self.assertNotIn(directories[75], normal.getvalue())
        self.assertNotIn(directories[65], priority.getvalue())
        self.assertIn(directories[75], priority.getvalue())


if __name__ == "__main__":
    unittest.main()
