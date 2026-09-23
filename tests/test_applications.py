from __future__ import annotations

from functools import partial
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
    APPLICATION_FILES,
    ApplicationError,
    ApplicationGenerator,
    CodexApplicationDraftClient,
    QUALITY_CONTRACT_VERSION,
    _cv_export_stem,
    _validate_draft_quality,
    _publish_staged_package,
    resolve_job_directories,
    validate_application_draft,
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
    skills = ", ".join(
        ("PHP", "Laravel", "Symfony", "Go", "MySQL", "PostgreSQL", "SQL", "REST APIs", "Git", "AWS", "Kubernetes", "RabbitMQ")
    )
    bullets = "\n".join(
        f"- Delivered backend outcome {number} through careful system design, automated testing, production monitoring, cross-functional collaboration, and a controlled release process for customer-facing services with documented rollback steps and measurable service-level checks."
        for number in range(1, 11)
    )
    cv_filler = (
        "Experienced backend engineer with more than ten years of work across PHP and Go "
        "services, API design, relational databases, cloud infrastructure, and production "
        "reliability. Combines hands-on delivery with system design, technical leadership, "
        "performance improvement, and collaboration with product teams. Focuses on maintainable "
        "architecture, measurable operational outcomes, and dependable releases for evolving "
        "customer-facing platforms."
    )
    letter_paragraph = " ".join(["I connect verified backend delivery experience to the role's PHP, Laravel, API, and reliability priorities."] * 6)
    analysis_body = " ".join(["Evidence is grounded in the candidate record and the vacancy, with gaps framed as confirmation items rather than claims."] * 5)
    interview_body = " ".join(["Prepare a concise, truthful example, identify the candidate's individual contribution, and connect it to the stated role requirement."] * 7)
    return {
        "cv_markdown": "# Candidate\nBackend Engineer\n\nhttps://linkedin.com/in/candidate | https://github.com/candidate\n\n## Summary\n\n" + cv_filler + "\n\n## Skills\n\n" + skills + "\n\n## Experience\n\n### Example Р Р†Р вЂљРІР‚Сњ Backend Engineer | January 2020 - Present\n" + bullets + "\nTechnologies: PHP, Laravel, MySQL\n\n## Education\n\nMSc in Computer Science\n\n## Languages\n\nEnglish\n",
        "cover_letter_markdown": "Dear Hiring Team,\n\n" + "\n\n".join([letter_paragraph] * 4) + "\n\nCandidate\n",
        "analysis_markdown": "# Application Analysis\n\n"
        + "\n\n".join(f"## {heading}\n\n{analysis_body}" for heading in analysis_headings)
        + "\n",
        "interview_preparation_markdown": "# Interview Preparation\n\n"
        + "\n\n".join(f"## {heading}\n\n{interview_body}" for heading in interview_headings)
        + "\n",
    }


def write_quality_contract(draft: Path, *, include_cover_letter: bool = True) -> None:
    """Create the required two-wave handoffs and deterministic quality receipt."""
    parts = draft / "parts"
    parts.mkdir(parents=True, exist_ok=True)
    (parts / "research.md").write_text(
        "# Research\n\n## Fact\n" + "fact " * 35 + "\nhttps://example.test/company\n\n## Inference\n" + "inference " * 35 + "\n\n## Unknown\n" + "unknown " * 35,
        encoding="utf-8",
    )
    (parts / "evidence-map.md").write_text(
        "# Evidence map\n\n| Priority Requirement | Employer Wording | Candidate Evidence and Source | Match | Verified Metric | Story Theme or Gap |\n| --- | --- | --- | --- | --- | --- |\n| PHP | PHP | registry/candidate/candidate.md | Direct | none | delivery |\n\n## Proposed CV\n\n" + "evidence " * 440,
        encoding="utf-8",
    )
    (parts / "requirements-risks.md").write_text(
        "## Explicit Requirements\n" + "requirement " * 65 + "\n\n## Inferred Requirements\n" + "inference " * 65 + "\n\n## Gaps and Risks\n" + "risk " * 65 + "\n\n## ATS Terms\nPHP, Laravel, APIs\n\n## Interview Probes\n" + "probe " * 65,
        encoding="utf-8",
    )
    quality: dict[str, Any] = {
        "schema_version": 1,
        "workflow": "two-wave",
        "handoffs": {"research": "parts/research.md", "evidence_map": "parts/evidence-map.md", "requirements_risks": "parts/requirements-risks.md"},
        "final_review": {"claim_grounding": True, "cross_file_consistency": True, "quality_gate": True},
    }
    if include_cover_letter:
        quality["cover_letter"] = {"skill": "write-cover-letter", "version": "test", "workbench_complete": True, "evidence_stories": [{"requirement": "PHP", "candidate_source": "registry/candidate/candidate.md"}, {"requirement": "APIs", "candidate_source": "registry/candidate/candidate.md"}], "company_motivation": {"fact": "Product company", "source_url": "https://example.test/company"}}
    (draft / "quality.yaml").write_text(yaml.safe_dump(quality, sort_keys=False), encoding="utf-8")


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

    def v2_letter_draft(self):
        from jobintel.evidence import bootstrap_evidence_bank
        import hashlib

        draft = self.project / "v2-draft"
        draft.mkdir()
        write_quality_contract(draft)
        package = {"cover_letter_markdown": application_payload()["cover_letter_markdown"]}
        source = self.registry_root / "candidate" / "candidate.md"
        source.parent.mkdir(parents=True)
        source.write_text(package["cover_letter_markdown"], encoding="utf-8")
        quote = "I connect verified backend delivery experience to the role's PHP, Laravel, API, and reliability priorities."
        bank = bootstrap_evidence_bank(self.project, [{"id": "delivery", "source": {"path": "registry/candidate/candidate.md", "quote": quote}}])
        bank["entries"][0].update(status="verified", verification={"reviewer": "fixture", "reviewed_at": "2026-09-22", "method": "source review"})
        bank_path = self.registry_root / "evidence.yaml"
        bank_path.write_text(yaml.safe_dump(bank), encoding="utf-8")
        ledger = {"schema_version": 1, "claims": [{"document": "cover-letter", "text": quote, "evidence_ids": ["delivery"]}]}
        (draft / "claims.yaml").write_text(yaml.safe_dump(ledger), encoding="utf-8")
        quality = yaml.safe_load((draft / "quality.yaml").read_text(encoding="utf-8"))
        quality.update(schema_version=2, evidence_bank="registry/evidence.yaml", claims_ledger="claims.yaml")
        quality["final_review"].update(reviewer="fixture", document_sha256={"cover-letter": "sha256:" + hashlib.sha256(package["cover_letter_markdown"].encode()).hexdigest()})
        quality["requirements"] = [{"requirement": "Backend", "importance": "high", "basis": "stated", "jd_quote": "Build Go services.", "match": "partial", "candidate_quote": quote, "risk": "Confirm Go scope", "mitigation": "Ask candidate", "hard_blocker": False, "evidence_ids": ["delivery"]}]
        for story in quality["cover_letter"]["evidence_stories"]:
            story["evidence_ids"] = ["delivery"]
        (draft / "quality.yaml").write_text(yaml.safe_dump(quality), encoding="utf-8")
        return draft, package, quality

    def test_v2_quality_receipt_binds_evidence_and_final_document(self):
        draft, package, _ = self.v2_letter_draft()
        receipt = _validate_draft_quality(draft, package, document="cover-letter", project_root=self.project, vacancy_text="Build Go services.")
        self.assertEqual(2, receipt["contract_version"])
        self.assertEqual(["delivery"], receipt["grounding"]["evidence_ids"])
        package["cover_letter_markdown"] += "Changed after review.\n"
        with self.assertRaisesRegex(ApplicationError, "final review is stale"):
            _validate_draft_quality(draft, package, document="cover-letter", project_root=self.project)

    def test_v2_rejects_false_source_and_path_escape(self):
        draft, package, quality = self.v2_letter_draft()
        quality["claims_ledger"] = "../claims.yaml"
        (draft / "quality.yaml").write_text(yaml.safe_dump(quality), encoding="utf-8")
        with self.assertRaisesRegex(ApplicationError, "escapes its root"):
            _validate_draft_quality(draft, package, document="cover-letter", project_root=self.project)

    def test_v2_export_failure_prevents_publication(self):
        draft, package, _ = self.v2_letter_draft()
        (draft / "cover-letter.md").write_text(package["cover_letter_markdown"], encoding="utf-8")
        client = CodexApplicationDraftClient(draft, model="test-model", document="cover-letter")
        generator = self._generator(client, FakeConverter(), document="cover-letter")
        with self.assertRaisesRegex(ApplicationError, "export quality validation failed"):
            generator.generate_directory(self.directory)
        self.assertFalse((self.directory / "application" / "cover-letter.docx").exists())

    def test_v2_publishes_export_and_grounding_receipts(self):
        from tests.test_document_quality import write_docx

        class RealFixtureConverter:
            def convert(self, source, target):
                write_docx(target, source.read_text(encoding="utf-8").splitlines())

        draft, package, _ = self.v2_letter_draft()
        (draft / "cover-letter.md").write_text(package["cover_letter_markdown"], encoding="utf-8")
        client = CodexApplicationDraftClient(draft, model="test-model", document="cover-letter")
        generator = self._generator(client, RealFixtureConverter(), document="cover-letter")
        self.assertEqual("prepared", generator.generate_directory(self.directory).status)
        manifest = yaml.safe_load((self.directory / "application" / "manifest.yaml").read_text(encoding="utf-8"))
        self.assertEqual(2, manifest["quality_contract_version"])
        self.assertEqual("not_reviewed", manifest["quality"]["exports"]["cover-letter"]["visual_review"]["status"])
        self.assertEqual("delivery", manifest["quality"]["grounding"]["evidence_entries"][0]["id"])
        self.assertTrue(generator.is_current(self.directory))
        exported = self.directory / "application" / "cover-letter.docx"
        exported.write_bytes(b"corrupted after validation")
        self.assertFalse(generator.is_current(self.directory))

    def test_new_publication_rejects_legacy_quality_contract(self):
        draft = self.project / "legacy-draft"
        draft.mkdir()
        write_quality_contract(draft)
        (draft / "cover-letter.md").write_text(application_payload()["cover_letter_markdown"], encoding="utf-8")
        generator = ApplicationGenerator(self.registry_root, [self.profile], self.prompt,
            CodexApplicationDraftClient(draft, model="test", document="cover-letter"), FakeConverter(), document="cover-letter")
        with self.assertRaisesRegex(ApplicationError, "publication requires quality schema_version 2"):
            generator.generate_directory(self.directory)
        self.assertFalse((self.directory / "application" / "manifest.yaml").exists())

    def test_compact_letter_allows_three_substantive_paragraphs(self):
        paragraph = " ".join(["I connect verified backend experience to your delivery priorities."] * 6)
        letter = "Dear Hiring Team,\n\n" + "\n\n".join([paragraph] * 3) + "\n\nCandidate\n"
        package = {"cover_letter_markdown": letter}
        validate_application_package(package, document="cover-letter", document_format="compact")
        with self.assertRaisesRegex(ApplicationError, "300-word minimum"):
            validate_application_package(package, document="cover-letter")

    def test_cache_rejects_corrupted_named_cv_export(self):
        from jobintel.document_quality import file_sha256
        from jobintel.evidence import validate_evidence_bank

        generator = self._generator(FakeClient(), FakeConverter())
        generator.generate_directory(self.directory)
        application = self.directory / "application"
        manifest_path = application / "manifest.yaml"
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        bank = {"schema_version": 1, "entries": []}
        (self.registry_root / "evidence.yaml").write_text(yaml.safe_dump(bank), encoding="utf-8")
        manifest["quality"]["documents"]["cv"].update(evidence_bank_path="registry/evidence.yaml", evidence_bank_sha256=validate_evidence_bank(bank, self.project)["sha256"])
        manifest["quality"]["exports"] = {"cv": {"artifact_sha256": file_sha256(application / "cv.docx"), "source_sha256": file_sha256(application / "cv.md")}}
        manifest_path.write_text(yaml.safe_dump(manifest), encoding="utf-8")
        self.assertTrue(generator.is_current(self.directory))
        alias = application / f"{manifest['cv_export_stem']}.docx"
        alias.write_bytes(b"corrupted named export")
        self.assertFalse(generator.is_current(self.directory))

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
            allow_legacy_drafts=True,
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
        self.assertEqual(QUALITY_CONTRACT_VERSION, manifest["quality_contract_version"])
        self.assertIn("documents", manifest["quality"])

    def test_cv_export_stem_keeps_company_and_role_focus_without_location_noise(self) -> None:
        self.assertEqual(
            "CV_ValentinNikolaev_grafana_SeniorBackendEngineerDatabasesLokiIngest",
            _cv_export_stem(
                company="Grafana Labs",
                title="Senior Backend Engineer - Databases - Loki Ingest | Germany | Remote",
            ),
        )

    def test_cv_export_stem_shortens_long_windows_filename_deterministically(self) -> None:
        stem = _cv_export_stem(
            company="Cuborio Business Click S.r.l.",
            title="Sviluppatore Senior PHP Laravel AI Augmented",
        )
        changed_title = _cv_export_stem(
            company="Cuborio Business Click S.r.l.",
            title="Sviluppatore Senior PHP Laravel AI Platform",
        )

        self.assertLessEqual(len(stem), 72)
        self.assertTrue(stem.startswith("CV_ValentinNikolaev_cuboriobusinessclicksrl_"))
        self.assertEqual(
            stem,
            _cv_export_stem(
                company="Cuborio Business Click S.r.l.",
                title="Sviluppatore Senior PHP Laravel AI Augmented",
            ),
        )
        self.assertNotEqual(stem, changed_title)

    def test_simple_life_cv_date_range_is_preserved_from_draft(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "### Example Р Р†Р вЂљРІР‚Сњ Backend Engineer | January 2020 - Present",
            "### Simple.life Р Р†Р вЂљРІР‚Сњ Software Developer | November 2023 - July 2026",
        ).replace(
            "## Education",
            "### airSlate Р Р†Р вЂљРІР‚Сњ Software Developer | February 2021 - August 2023\n"
            "- Improved a supported backend workflow with measured engineering discipline.\n"
            "Technologies: PHP, Symfony, PostgreSQL\n\n## Education",
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
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "# Candidate\nBackend Engineer", "# Candidate\n\nBackend Engineer", 1
        )

        with self.assertRaisesRegex(ApplicationError, "immediately after the candidate name"):
            validate_application_package(
                payload,
                vacancy={"metadata": {"title": "Senior Backend Engineer"}},
            )

    def test_cv_headline_must_align_with_vacancy_title_terms(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "# Candidate\nBackend Engineer", "# Candidate\nSoftware Engineer", 1
        )

        with self.assertRaisesRegex(ApplicationError, "headline is not aligned"):
            validate_application_package(
                payload,
                vacancy={"metadata": {"title": "Senior Backend Engineer"}},
            )

    def test_cv_headline_accepts_vacancy_specific_supported_term(self) -> None:
        payload = application_payload()

        result = validate_application_package(
            payload,
            vacancy={"metadata": {"title": "Senior Backend Engineer"}},
        )

        self.assertIn("Backend Engineer", result["cv_markdown"])

    def test_cv_experience_rejects_employment_older_than_ten_years(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "Technologies: PHP, Laravel, MySQL\n\n## Education",
            "Technologies: PHP, Laravel, MySQL\n\n### Legacy Co | 2008 - 2015\n"
            "- Maintained services.\nTechnologies: PHP\n\n## Education",
        )

        with self.assertRaisesRegex(ApplicationError, "more than 10 years ago"):
            validate_application_package(
                payload,
                reference_date=datetime(2026, 8, 6, tzinfo=timezone.utc),
            )

    def test_cv_age_rule_is_scoped_to_experience_and_allows_recent_roles(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "### Example Р Р†Р вЂљРІР‚Сњ Backend Engineer | January 2020 - Present",
            "### Current Co | July 2015 - August 2016\nTechnologies: Go\n\n"
            "### New Co | September 2016 - Present",
        )

        result = validate_application_package(
            payload,
            reference_date=datetime(2026, 8, 6, tzinfo=timezone.utc),
        )

        self.assertIn("MSc in Computer Science", result["cv_markdown"])

    def test_cv_requires_evidence_backed_technologies_for_each_experience_role(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "Technologies: PHP, Laravel, MySQL\n\n## Education",
            "Technologies: PHP, Laravel, MySQL\n\n### Missing Co\n- Built services.\n\n## Education",
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
        payload["cover_letter_markdown"] = payload["cover_letter_markdown"].replace(
            "I connect verified backend delivery experience",
            "I am applying for the Senior Backend Engineer role at Example and connect verified backend delivery experience",
            1,
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
        write_quality_contract(draft)
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
        write_quality_contract(draft, include_cover_letter=False)

        client = CodexApplicationDraftClient(
            draft,
            model="codex:gpt-5.6-terra:medium",
            document="cv",
        )

        self.assertEqual(
            {"cv_markdown"},
            set(client.generate(prompt="", candidate_profile="", vacancy={})),
        )

    def test_validate_application_draft_rejects_missing_quality_contract(self) -> None:
        draft = self.project / "missing-quality"
        draft.mkdir()
        (draft / "cv.md").write_text(application_payload()["cv_markdown"], encoding="utf-8")
        with self.assertRaisesRegex(ApplicationError, "quality.yaml"):
            validate_application_draft(self.directory, draft, document="cv")

    def test_validate_application_draft_rejects_incomplete_handoff(self) -> None:
        draft = self.project / "incomplete-handoff"
        draft.mkdir()
        payload = application_payload()
        for field, filename in APPLICATION_FILES.items():
            (draft / filename).write_text(payload[field], encoding="utf-8")
        write_quality_contract(draft)
        (draft / "parts" / "research.md").write_text("## Fact\nshort", encoding="utf-8")
        with self.assertRaisesRegex(ApplicationError, "research"):
            validate_application_draft(self.directory, draft)

    def test_validate_application_package_rejects_internal_cv_evidence_markers(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "Experienced backend engineer", "Experienced backend engineer [support-platform]", 1
        )

        with self.assertRaisesRegex(ApplicationError, "internal evidence marker"):
            validate_application_package(payload)

    def test_validate_application_package_rejects_meta_summary_language(self) -> None:
        payload = application_payload()
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            "Experienced backend engineer", "The verified record supports an experienced backend engineer", 1
        )

        with self.assertRaisesRegex(ApplicationError, "internal review language"):
            validate_application_package(payload)

    def test_validate_application_package_rejects_fragmented_or_story_first_summary(self) -> None:
        payload = application_payload()
        summary = payload["cv_markdown"].split("## Summary\n\n", 1)[1].split(
            "\n\n## Skills", 1
        )[0]
        payload["cv_markdown"] = payload["cv_markdown"].replace(
            summary,
            "At Example, I delivered a backend platform.\n\n" + summary,
            1,
        )

        with self.assertRaisesRegex(ApplicationError, "one concise employer-facing paragraph"):
            validate_application_package(payload)

    def test_validate_application_package_rejects_story_first_summary(self) -> None:
        payload = application_payload()
        summary = payload["cv_markdown"].split("## Summary\n\n", 1)[1].split(
            "\n\n## Skills", 1
        )[0]
        story_first = (
            "At Example, I delivered a backend platform used by product teams while "
            "improving reliability and release safety. My background includes more than "
            "ten years of PHP and Go development, API design, relational databases, cloud "
            "infrastructure, performance optimization, system design, technical leadership, "
            "and cross-functional delivery for customer-facing production services with "
            "documented operational ownership and dependable release practices."
        )
        payload["cv_markdown"] = payload["cv_markdown"].replace(summary, story_first, 1)

        with self.assertRaisesRegex(ApplicationError, "professional identity"):
            validate_application_package(payload)

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
        write_quality_contract(draft)

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
        write_quality_contract(draft, include_cover_letter=False)

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
            "cv_markdown": application_payload()["cv_markdown"].replace(
                "Experienced backend engineer", "Updated backend engineer", 1
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
        write_quality_contract(draft)
        MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeMatchClient(72),
            clock=lambda: self.now,
        ).analyze_directory(self.directory)

        with patch("jobintel.cli.HostMarkdownDocxConverter", return_value=FakeConverter()), patch("jobintel.cli.ApplicationGenerator", side_effect=partial(ApplicationGenerator, allow_legacy_drafts=True)):
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
        manifest_path = self.directory / "application" / "manifest.yaml"
        self.assertTrue(manifest_path.is_file())
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
        self.assertEqual(1, manifest["quality_contract_version"])
        self.assertIn("Legacy contract 1", manifest["quality"]["migration_note"])
        self.assertEqual("two-wave", manifest["quality"]["method"]["workflow"])
        self.assertEqual(3, len(manifest["quality"]["handoffs"]))
        self.assertEqual(
            "write-cover-letter",
            manifest["quality"]["method"]["cover_letter"]["skill"],
        )

    def test_prepare_cli_publishes_explicit_cv_only_draft(self) -> None:
        sources = self.project / "sources"
        sources.mkdir()
        draft = self.project / "cv-only-draft"
        draft.mkdir()
        (draft / "cv.md").write_text(
            application_payload()["cv_markdown"], encoding="utf-8"
        )
        write_quality_contract(draft, include_cover_letter=False)
        MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeMatchClient(72),
            clock=lambda: self.now,
        ).analyze_directory(self.directory)

        with patch("jobintel.cli.HostMarkdownDocxConverter", return_value=FakeConverter()), patch("jobintel.cli.ApplicationGenerator", side_effect=partial(ApplicationGenerator, allow_legacy_drafts=True)):
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
            write_quality_contract(draft)

        with patch("jobintel.cli.HostMarkdownDocxConverter", return_value=FakeConverter()), patch("jobintel.cli.ApplicationGenerator", side_effect=partial(ApplicationGenerator, allow_legacy_drafts=True)):
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

