from __future__ import annotations

import hashlib
import json
import os
import re
import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import yaml

from . import storage_bridge as op
from .evidence import EvidenceError, validate_claims_ledger, validate_evidence_bank


APPLICATION_FILES = {
    "cv_markdown": "cv.md",
    "cover_letter_markdown": "cover-letter.md",
    "analysis_markdown": "analysis.md",
    "interview_preparation_markdown": "interview-preparation.md",
}
APPLICATION_DOCUMENTS = {
    "cv": "cv_markdown",
    "cover-letter": "cover_letter_markdown",
    "analysis": "analysis_markdown",
    "interview-preparation": "interview_preparation_markdown",
}
QUALITY_CONTRACT_VERSION = 2

_DEFAULT_APPLICATION_DIRECTORY = "application"
_FALLBACK_APPLICATION_DIRECTORY = "application-codex"
_CV_OWNER_STEM = "ValentinNikolaev"
_MAX_CV_EXPORT_STEM_LENGTH = 72
_ROLE_NOISE_TERMS = {
    "hybrid",
    "remote",
    "tags",
    "new",
}
_ROLE_LOCATION_TERMS = {
    "argentina",
    "australia",
    "austria",
    "belgium",
    "brazil",
    "canada",
    "denmark",
    "europe",
    "france",
    "germany",
    "ireland",
    "israel",
    "italy",
    "japan",
    "netherlands",
    "poland",
    "portugal",
    "singapore",
    "spain",
    "sweden",
    "switzerland",
    "uk",
    "united kingdom",
    "united states",
    "usa",
    "us",
}
_COMPANY_SUFFIX_TERMS = {
    "ag",
    "gmbh",
    "inc",
    "incorporated",
    "labs",
    "limited",
    "llc",
    "ltd",
    "srl",
}
_MONTH_NAMES = (
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
)
_MONTH_PATTERN = "|".join(_MONTH_NAMES)
_EXPERIENCE_DATE_RANGE_RE = re.compile(
    rf"(?P<start>\b(?:(?:{_MONTH_PATTERN})\s+)?\d{{4}})\s*[-–—]\s*"
    rf"(?P<end>Present|Current|(?:(?:{_MONTH_PATTERN})\s+)?\d{{4}})\b",
    re.IGNORECASE,
)

_REQUIRED_HEADINGS = {
    "cv_markdown": (
        "Summary",
        "Skills",
        "Experience",
        "Education",
        "Languages",
    ),
    "analysis_markdown": (
        "Vacancy Summary",
        "Company Research",
        "Initial Resume Audit",
        "Strict Hiring Manager Review",
        "Red Flags",
        "ATS Keyword Analysis",
        "Major CV Changes",
        "Final Quality Gate",
        "Recommendation",
    ),
    "interview_preparation_markdown": (
        "Recruiter / HR Screening",
        "Culture Fit / Behavioral Interview",
        "Technical Interview",
        "CV Deep-Dive Questions",
        "Company-Specific Preparation",
        "Preparation Plan",
        "Questions to Ask",
    ),
}
_FORBIDDEN_APPLICATION_PHRASES = (
    "Zend Certified PHP Developer",
    "Zend PHP Certification",
)
_MAX_APPLICATION_WORD_COUNTS = {
    "cv_markdown": 800,
    "cover_letter_markdown": 450,
    "analysis_markdown": 1000,
    "interview_preparation_markdown": 1100,
}
_MIN_APPLICATION_WORD_COUNTS = {
    "cv_markdown": 500,
    "cover_letter_markdown": 300,
    "analysis_markdown": 700,
    "interview_preparation_markdown": 800,
}
_COMPACT_MIN_WORD_COUNTS = {**_MIN_APPLICATION_WORD_COUNTS, "cv_markdown": 300, "cover_letter_markdown": 150}
_HANDOFF_REQUIREMENTS = {
    "research.md": (100, ("Fact", "Inference", "Unknown")),
    "evidence-map.md": (
        450,
        (
            "Priority requirement",
            "Candidate evidence and source",
            "Match",
            "## Proposed CV",
        ),
    ),
    "requirements-risks.md": (
        250,
        (
            "## Explicit Requirements",
            "## Inferred Requirements",
            "## Gaps and Risks",
            "## ATS Terms",
            "## Interview Probes",
        ),
    ),
}
_HEADLINE_GENERIC_TERMS = {
    "and",
    "architect",
    "consultant",
    "developer",
    "engineer",
    "engineering",
    "expert",
    "for",
    "full",
    "fullstack",
    "lead",
    "manager",
    "mid",
    "of",
    "principal",
    "remote",
    "senior",
    "software",
    "specialist",
    "stack",
    "staff",
    "the",
}


class ApplicationError(RuntimeError):
    pass


class ApplicationClient(Protocol):
    model: str

    def generate(
        self,
        *,
        prompt: str,
        candidate_profile: str,
        vacancy: Mapping[str, Any],
    ) -> Mapping[str, Any]: ...


class DocxConverter(Protocol):
    def convert(self, source: Path, target: Path) -> None: ...


@dataclass(frozen=True, slots=True)
class PreparationResult:
    status: str
    vacancy_id: str
    directory: str


@dataclass(slots=True)
class PreparationSummary:
    selected: int = 0
    prepared: int = 0
    skipped: int = 0
    errors: int = 0


class CodexApplicationDraftClient:
    """Load Markdown drafts produced by the active Codex task."""

    def __init__(self, directory: Path, *, model: str, document: str | None = None) -> None:
        if not model.strip():
            raise ValueError("a Codex model label is required")
        self.directory = directory.resolve()
        self.model = model.strip()
        self.document = _normalize_document(document)

    def generate(
        self,
        *,
        prompt: str,
        candidate_profile: str,
        vacancy: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        del prompt, candidate_profile, vacancy
        result: dict[str, str] = {}
        for field in _selected_fields(self.document):
            filename = APPLICATION_FILES[field]
            path = self.directory / filename
            try:
                result[field] = op.read_text(path)
            except OSError as exc:
                raise ApplicationError(f"cannot read Codex application draft {path}: {exc}") from exc
        return result


def validate_application_draft(
    vacancy_directory: Path,
    draft_directory: Path,
    *,
    document: str | None = None,
    reference_date: date | datetime | None = None,
) -> dict[str, str]:
    """Validate a local Codex draft without publishing or converting it."""
    vacancy_directory = vacancy_directory.resolve()
    meta = _read_yaml_mapping(vacancy_directory / "meta.yaml", "vacancy metadata")
    vacancy, _, _ = _load_vacancy(vacancy_directory, meta)
    draft = CodexApplicationDraftClient(
        draft_directory,
        model="deterministic-draft-validator",
        document=document,
    ).generate(prompt="", candidate_profile="", vacancy=vacancy)
    validated = validate_application_package(
        draft,
        vacancy=vacancy,
        document=document,
        reference_date=reference_date,
        document_format=_draft_format(draft_directory),
    )
    _validate_draft_quality(draft_directory.resolve(), validated, document=document,
                            project_root=op.project_root(vacancy_directory), vacancy_text=str(vacancy["job_description"]))
    return validated


class HostMarkdownDocxConverter:
    """Run the installed md-to-docx Codex skill as a host-side converter."""

    def __init__(
        self,
        project_root: Path,
        *,
        script_path: Path | None = None,
        options_path: Path | None = None,
        powershell: str | None = None,
    ) -> None:
        self.project_root = project_root.resolve()
        self.script_path = (script_path or _find_docx_script()).resolve()
        self.options_path = (
            options_path or self.project_root / "config" / "application-docx-options.json"
        ).resolve()
        self.powershell = powershell or shutil.which("pwsh") or shutil.which("powershell") or ""

    def convert(self, source: Path, target: Path) -> None:
        if not op.exists(self.script_path):
            raise ApplicationError(f"Markdown-to-DOCX converter not found: {self.script_path}")
        if not op.exists(self.options_path):
            raise ApplicationError(f"DOCX options file not found: {self.options_path}")
        if not self.powershell:
            raise ApplicationError("PowerShell is required by the Markdown-to-DOCX converter")
        target.parent.mkdir(parents=True, exist_ok=True)
        command = [
            self.powershell,
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            str(self.script_path),
            "-InputPath",
            str(source.resolve()),
            "-OutputPath",
            str(target.resolve()),
            "-OptionsPath",
            str(self.options_path),
        ]
        completed = subprocess.run(
            command,
            cwd=self.project_root,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        if completed.returncode:
            detail = (completed.stderr or completed.stdout).strip()
            raise ApplicationError(f"Markdown-to-DOCX conversion failed: {detail[:1000]}")
        if not op.exists(target) or target.stat().st_size == 0:
            raise ApplicationError(f"Markdown-to-DOCX converter did not create {target}")


class ApplicationGenerator:
    def __init__(
        self,
        registry_root: Path,
        profile_paths: Sequence[Path],
        prompt_path: Path,
        client: ApplicationClient,
        converter: DocxConverter,
        *,
        document: str | None = None,
        clock: Callable[[], datetime] | None = None,
        allow_legacy_drafts: bool = False,
    ) -> None:
        self.registry_root = registry_root.resolve()
        self.profile_paths = tuple(path.resolve() for path in profile_paths)
        self.prompt_path = prompt_path.resolve()
        self.client = client
        self.converter = converter
        self.model = str(getattr(client, "model", client.__class__.__name__))
        self.document = _normalize_document(document)
        self.allow_legacy_drafts = allow_legacy_drafts
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    @op.exclusive
    def generate_directory(self, directory: Path, *, force: bool = False) -> PreparationResult:
        directory = directory.resolve()
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
        vacancy_id = str(meta.get("id", ""))
        if not vacancy_id:
            raise ApplicationError(f"vacancy metadata has no id: {directory / 'meta.yaml'}")

        candidate_profile, profile_version = self._load_candidate_profile()
        prompt, prompt_version = self._load_prompt()
        vacancy, vacancy_version, company_version = _load_vacancy(directory, meta)
        generated_at = self._clock()
        expected_versions = {
            "profile_version": profile_version,
            "vacancy_version": vacancy_version,
            "company_version": company_version,
            "prompt_version": prompt_version,
            "model": self.model,
            "quality_contract_version": QUALITY_CONTRACT_VERSION,
            "cv_export_stem": _cv_export_stem(
                company=str(meta.get("company") or ""),
                title=str(meta.get("title") or ""),
            ),
        }
        application_dir = _application_directory(directory, meta)
        manifest_path = application_dir / "manifest.yaml"
        if not force and _package_is_current(
            application_dir,
            manifest_path,
            expected_versions,
            document=self.document,
        ):
            return PreparationResult("skipped", vacancy_id, directory.name)

        generated = validate_application_package(
            self.client.generate(
                prompt=prompt,
                candidate_profile=candidate_profile,
                vacancy=vacancy,
            ),
            vacancy=vacancy,
            document=self.document,
            reference_date=generated_at,
            document_format=_draft_format(self.client.directory) if isinstance(self.client, CodexApplicationDraftClient) else "standard",
        )
        quality = _document_quality_report(generated)
        if isinstance(self.client, CodexApplicationDraftClient):
            quality.update(
                _validate_draft_quality(
                    self.client.directory,
                    generated,
                    document=self.document,
                    project_root=self.registry_root.parent,
                    vacancy_text=str(vacancy["job_description"]),
                )
            )
        expected_versions["quality_contract_version"] = quality["contract_version"]
        if isinstance(self.client, CodexApplicationDraftClient) and quality["contract_version"] != 2 and not self.allow_legacy_drafts:
            raise ApplicationError("new application publication requires quality schema_version 2; legacy schema 1 is read-only")
        cv_export_files = _cv_export_files(meta)

        staging = Path(tempfile.mkdtemp(prefix=".application-", dir=directory))
        try:
            previous_manifest = _read_existing_manifest(manifest_path)
            if self.document is not None:
                _copy_existing_application_files(application_dir, staging)
                _remove_selected_outputs(staging, self.document)
            for field in _selected_fields(self.document):
                filename = APPLICATION_FILES[field]
                _write_text(staging / filename, generated[field])
            if self.document in {None, "cv"}:
                self.converter.convert(staging / "cv.md", staging / "cv.docx")
                shutil.copyfile(staging / "cv.md", staging / cv_export_files["markdown"])
                shutil.copyfile(staging / "cv.docx", staging / cv_export_files["docx"])
            if self.document in {None, "cover-letter"}:
                self.converter.convert(
                    staging / "cover-letter.md", staging / "cover-letter.docx"
                )
            if isinstance(self.client, CodexApplicationDraftClient) and quality["contract_version"] == 2:
                from .document_quality import DocumentQualityError, validate_export

                declaration = _read_yaml_mapping(self.client.directory / "quality.yaml", "application quality declaration")
                reviews = declaration.get("export_reviews", {})
                exports = {}
                try:
                    for name in _selected_documents(self.document):
                        if name in {"cv", "cover-letter"}:
                            exports[name] = validate_export(
                                staging / f"{name}.md", staging / f"{name}.docx",
                                visual_review=reviews.get(name) if isinstance(reviews, Mapping) else None,
                            )
                except DocumentQualityError as exc:
                    raise ApplicationError(f"export quality validation failed: {exc}") from exc
                quality["exports"] = exports
            document_versions = _document_versions_from_manifest(
                previous_manifest,
                application_dir,
            ) if self.document is not None else {}
            for selected_document in _selected_documents(self.document):
                document_versions[selected_document] = {
                    **expected_versions,
                    "generated_at": _utc_iso(generated_at),
                }
            published_files = _staged_application_files(staging)
            manifest = {
                **expected_versions,
                "generated_at": _utc_iso(generated_at),
                "documents": document_versions,
                "quality": _merge_quality_reports(
                    previous_manifest.get("quality"),
                    quality,
                    document=self.document,
                ),
                "files": published_files,
            }
            _write_text(
                staging / "manifest.yaml",
                yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
            )
            def record_published(target: Path) -> None:
                with op.mutation(directory, "publish-application-manifest"):
                    if target.name != application_dir.name:
                        _record_application_directory(directory / "meta.yaml", meta, target.name)
                    op.record_package(directory, target)

            try:
                _publish_staged_package(staging, application_dir, published_files, on_published=record_published)
            except PermissionError:
                if application_dir.name != _DEFAULT_APPLICATION_DIRECTORY:
                    raise
                fallback = directory / _FALLBACK_APPLICATION_DIRECTORY
                _publish_staged_package(staging, fallback, published_files, on_published=record_published)
                application_dir = fallback
        finally:
            shutil.rmtree(staging, ignore_errors=True)

        return PreparationResult("prepared", vacancy_id, directory.name)

    def is_current(self, directory: Path) -> bool:
        directory = directory.resolve()
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
        _, profile_version = self._load_candidate_profile()
        _, prompt_version = self._load_prompt()
        _, vacancy_version, company_version = _load_vacancy(directory, meta)
        expected_versions = {
            "profile_version": profile_version,
            "vacancy_version": vacancy_version,
            "company_version": company_version,
            "prompt_version": prompt_version,
            "model": self.model,
            "quality_contract_version": QUALITY_CONTRACT_VERSION,
            "cv_export_stem": _cv_export_stem(
                company=str(meta.get("company") or ""),
                title=str(meta.get("title") or ""),
            ),
        }
        application_dir = _application_directory(directory, meta)
        return _package_is_current(
            application_dir,
            application_dir / "manifest.yaml",
            expected_versions,
            document=self.document,
        )

    def _load_candidate_profile(self) -> tuple[str, str]:
        if not self.profile_paths:
            raise ApplicationError("at least one candidate source-of-truth path is required")
        sections = []
        for path in self.profile_paths:
            if not op.exists(path):
                raise ApplicationError(f"candidate source-of-truth file not found: {path}")
            content = op.read_text(path).strip()
            if not content:
                raise ApplicationError(f"candidate source-of-truth file is empty: {path}")
            sections.append(f"## Source: {path.name}\n\n{content}")
        combined = "\n\n".join(sections)
        return combined, _content_version(combined)

    def _load_prompt(self) -> tuple[str, str]:
        if not op.exists(self.prompt_path):
            raise ApplicationError(f"application prompt not found: {self.prompt_path}")
        prompt = op.read_text(self.prompt_path).strip()
        if not prompt:
            raise ApplicationError(f"application prompt is empty: {self.prompt_path}")
        return prompt, _content_version(prompt)


def resolve_job_directories(registry_root: Path, selector: str) -> list[Path]:
    jobs_dir = registry_root.resolve() / "jobs"
    if selector.casefold() == "all":
        return sorted(path.parent for path in op.metadata_paths(jobs_dir))

    direct = jobs_dir / selector
    if op.exists(direct / "meta.yaml"):
        return [direct.resolve()]

    matches = []
    for meta_path in op.metadata_paths(jobs_dir):
        meta = _read_yaml_mapping(meta_path, "vacancy metadata")
        if str(meta.get("id", "")) == selector:
            matches.append(meta_path.parent.resolve())
    if len(matches) > 1:
        raise ApplicationError(f"vacancy id appears in multiple directories: {selector}")
    if not matches:
        raise ApplicationError(f"vacancy not found: {selector}")
    return matches


def validate_application_package(
    value: Mapping[str, Any],
    *,
    vacancy: Mapping[str, Any] | None = None,
    document: str | None = None,
    reference_date: date | datetime | None = None,
    document_format: str = "standard",
) -> dict[str, str]:
    if document_format not in {"standard", "compact"}:
        raise ApplicationError("document_format must be standard or compact")
    document = _normalize_document(document)
    expected = set(_selected_fields(document))
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise ApplicationError("invalid application fields: " + "; ".join(details))

    result = {}
    for field in _selected_fields(document):
        content = value[field]
        if not isinstance(content, str) or not content.strip():
            raise ApplicationError(f"{field} must be non-empty Markdown")
        clean = content.strip() + "\n"
        if "```" in clean[:20]:
            raise ApplicationError(f"{field} must not be wrapped in a code fence")
        result[field] = clean

    for field, headings in _REQUIRED_HEADINGS.items():
        if field not in result:
            continue
        missing = [heading for heading in headings if f"## {heading}" not in result[field]]
        if missing:
            raise ApplicationError(
                f"{field} is missing required headings: {', '.join(missing)}"
            )
    for field, content in result.items():
        folded = content.casefold()
        for phrase in _FORBIDDEN_APPLICATION_PHRASES:
            if phrase.casefold() in folded:
                raise ApplicationError(f"{field} contains forbidden phrase: {phrase}")
        word_count = _word_count(content)
        word_minimum = (_COMPACT_MIN_WORD_COUNTS if document_format == "compact" else _MIN_APPLICATION_WORD_COUNTS)[field]
        if word_count < word_minimum:
            raise ApplicationError(
                f"{field} is below {word_minimum}-word minimum ({word_count} words)"
            )
        word_limit = _MAX_APPLICATION_WORD_COUNTS[field]
        if word_count > word_limit:
            raise ApplicationError(
                f"{field} exceeds {word_limit}-word limit ({word_count} words)"
            )
    if "cv_markdown" in result:
        _validate_cv_links(result["cv_markdown"])
        _validate_cv_skills(result["cv_markdown"])
        _validate_cv_experience_bullets(result["cv_markdown"], minimum=6 if document_format == "compact" else 10)
        _validate_cv_experience_age(result["cv_markdown"], reference_date=reference_date)
        _validate_cv_role_technologies(result["cv_markdown"])
        if vacancy is not None:
            _validate_cv_headline(result["cv_markdown"], vacancy)
    if "cover_letter_markdown" in result:
        _validate_cover_letter_paragraphs(result["cover_letter_markdown"], minimum=3 if document_format == "compact" else 4)
    return result


def _word_count(markdown: str) -> int:
    return len(re.findall(r"\b[\w'-]+\b", markdown, flags=re.UNICODE))


def _markdown_section(markdown: str, heading: str) -> str:
    lines = markdown.splitlines()
    selected: list[str] = []
    in_section = False
    for line in lines:
        match = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if match and len(match.group(1)) == 2:
            if in_section:
                break
            in_section = match.group(2).strip().casefold() == heading.casefold()
            continue
        if in_section:
            selected.append(line)
    return "\n".join(selected)


def _validate_cv_links(markdown: str) -> None:
    folded = markdown.casefold()
    missing = []
    if not re.search(r"https?://(?:www\.)?linkedin\.com/", folded):
        missing.append("LinkedIn")
    if not re.search(r"https?://(?:www\.)?github\.com/", folded):
        missing.append("GitHub")
    if missing:
        raise ApplicationError(
            "cv_markdown must include working profile URLs for: " + ", ".join(missing)
        )


def _validate_cv_skills(markdown: str) -> None:
    section = _markdown_section(markdown, "Skills")
    items = [
        match.group(1).strip()
        for line in section.splitlines()
        if (match := re.match(r"^\s*[-*]\s+(.+?)\s*$", line))
    ]
    if not items:
        items = [item.strip() for item in re.split(r"[,;|]", section) if item.strip()]
    if not 12 <= len(items) <= 18:
        raise ApplicationError(
            "cv_markdown Skills must contain 12 to 18 vacancy-relevant items "
            f"({len(items)} found)"
        )


def _validate_cv_experience_bullets(markdown: str, *, minimum: int = 10) -> None:
    section = _markdown_section(markdown, "Experience")
    bullets = [
        line
        for line in section.splitlines()
        if re.match(r"^\s*[-*]\s+\S", line)
        and not re.match(r"^\s*[-*]\s+(?:\*\*)?Technologies", line, re.IGNORECASE)
    ]
    if len(bullets) < minimum:
        raise ApplicationError(
            f"cv_markdown Experience must contain at least {minimum} evidence-backed bullets "
            f"({len(bullets)} found)"
        )


def _validate_cover_letter_paragraphs(markdown: str, *, minimum: int = 4) -> None:
    body: list[str] = []
    for block in re.split(r"\n\s*\n", markdown.strip()):
        text = " ".join(
            line.strip() for line in block.splitlines() if not line.lstrip().startswith("#")
        ).strip()
        folded = text.casefold()
        if not text or folded.startswith(("dear ", "hello ", "hi ")):
            continue
        if folded.startswith(("sincerely", "best regards", "kind regards", "cordiali")):
            continue
        if _word_count(text) >= 20:
            body.append(text)
    if not minimum <= len(body) <= 6:
        raise ApplicationError(
            f"cover_letter_markdown must contain {minimum} to 6 substantive body paragraphs "
            f"({len(body)} found)"
        )


def _document_quality_report(package: Mapping[str, str]) -> dict[str, Any]:
    documents = {}
    for field, content in package.items():
        document = next(
            name for name, mapped_field in APPLICATION_DOCUMENTS.items() if mapped_field == field
        )
        documents[document] = {
            "word_count": _word_count(content),
            "sha256": _content_version(content),
        }
    return {
        "contract_version": QUALITY_CONTRACT_VERSION,
        "documents": documents,
    }


def _validate_draft_quality(
    draft_directory: Path,
    package: Mapping[str, str],
    *,
    document: str | None,
    project_root: Path | None = None,
    vacancy_text: str | None = None,
) -> dict[str, Any]:
    quality_path = draft_directory / "quality.yaml"
    quality = _read_yaml_mapping(quality_path, "application quality declaration")
    version = quality.get("schema_version")
    if type(version) is not int or version not in {1, QUALITY_CONTRACT_VERSION}:
        raise ApplicationError(
            "application quality declaration schema_version must be "
            f"1 (legacy) or {QUALITY_CONTRACT_VERSION}: {quality_path}"
        )
    if quality.get("workflow") != "two-wave":
        raise ApplicationError("application quality declaration workflow must be two-wave")

    final_review = quality.get("final_review")
    if not isinstance(final_review, Mapping) or any(
        final_review.get(key) is not True
        for key in ("claim_grounding", "cross_file_consistency")
    ):
        raise ApplicationError(
            "application quality declaration final_review must confirm "
            "claim_grounding and cross_file_consistency"
        )

    selected = set(_selected_documents(_normalize_document(document)))
    method: dict[str, Any] = {
        "workflow": "two-wave",
        "final_review": {
            "claim_grounding": True,
            "cross_file_consistency": True,
        },
    }
    if "cover-letter" in selected:
        cover_letter = quality.get("cover_letter")
        if not isinstance(cover_letter, Mapping):
            raise ApplicationError("application quality declaration is missing cover_letter")
        skill = str(cover_letter.get("skill") or "").strip()
        skill_version = str(cover_letter.get("version") or "").strip()
        if skill != "write-cover-letter" or not skill_version:
            raise ApplicationError(
                "cover_letter must record write-cover-letter and its installed version"
            )
        if cover_letter.get("workbench_complete") is not True:
            raise ApplicationError("cover_letter workbench_complete must be true")
        stories = cover_letter.get("evidence_stories")
        if not isinstance(stories, list) or len(stories) != 2:
            raise ApplicationError("cover_letter must record exactly two evidence_stories")
        for index, story in enumerate(stories, start=1):
            if not isinstance(story, Mapping):
                raise ApplicationError(f"cover_letter evidence story {index} must be a mapping")
            requirement = str(story.get("requirement") or "").strip()
            source = str(story.get("candidate_source") or "").strip().replace("\\", "/")
            if not requirement or not source.startswith("registry/candidate/"):
                raise ApplicationError(
                    f"cover_letter evidence story {index} must include a requirement and "
                    "a registry/candidate source"
                )
        motivation = cover_letter.get("company_motivation")
        if not isinstance(motivation, Mapping):
            raise ApplicationError("cover_letter must record company_motivation")
        fact = str(motivation.get("fact") or "").strip()
        source_url = str(motivation.get("source_url") or "").strip()
        if not fact or not re.match(r"^https?://", source_url, re.IGNORECASE):
            raise ApplicationError(
                "cover_letter company_motivation must include a fact and HTTP(S) source_url"
            )
        method["cover_letter"] = {
            "skill": skill,
            "version": skill_version,
            "workbench_complete": True,
            "evidence_story_count": len(stories),
            "company_source_url": source_url,
        }

    required_handoffs = _required_handoffs(selected)
    handoff_report: dict[str, Any] = {}
    for filename in required_handoffs:
        path = draft_directory / "parts" / filename
        try:
            content = op.read_text(path).strip()
        except OSError as exc:
            raise ApplicationError(f"cannot read required application handoff {path}: {exc}") from exc
        minimum, markers = _HANDOFF_REQUIREMENTS[filename]
        count = _word_count(content)
        if count < minimum:
            raise ApplicationError(
                f"application handoff {filename} is below {minimum}-word minimum "
                f"({count} words)"
            )
        missing = [marker for marker in markers if marker.casefold() not in content.casefold()]
        if missing:
            raise ApplicationError(
                f"application handoff {filename} is missing required content: "
                + ", ".join(missing)
            )
        if filename == "research.md" and not re.search(r"https?://", content):
            raise ApplicationError("application handoff research.md must cite an HTTP(S) URL")
        handoff_report[filename] = {
            "word_count": count,
            "sha256": _content_version(content),
        }

    report = _document_quality_report(package)
    report["contract_version"] = version
    report["document_format"] = _draft_format(draft_directory)
    if version == 1:
        report["migration_note"] = "Legacy contract 1: source-linked claims and export checks are not verified; prepare a new contract 2 draft."
    else:
        report["grounding"] = _validate_v2_grounding(quality, package, draft_directory, project_root, vacancy_text)
        for receipt in report["documents"].values():
            receipt["evidence_bank_path"] = report["grounding"]["evidence_bank_path"]
            receipt["evidence_bank_sha256"] = report["grounding"]["evidence_bank"]["sha256"]
    report.update(
        {
            "declaration_sha256": _content_version(
                op.read_text(quality_path)
            ),
            "method": method,
            "handoffs": handoff_report,
        }
    )
    return report


def _draft_format(directory: Path) -> str:
    quality = _read_yaml_mapping(directory / "quality.yaml", "application quality declaration")
    value = quality.get("document_format", "standard")
    if not isinstance(value, str) or value not in {"standard", "compact"}:
        raise ApplicationError("document_format must be standard or compact")
    if value == "compact" and quality.get("schema_version") != 2:
        raise ApplicationError("compact documents require quality schema_version 2")
    return value


def _contained_file(root: Path, relative: Any, label: str) -> Path:
    if not isinstance(relative, str) or not relative.strip() or Path(relative).is_absolute():
        raise ApplicationError(f"{label} must be a relative file path")
    path = (root / relative).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ApplicationError(f"{label} escapes its root")
    return path


def _validate_v2_grounding(
    quality: Mapping[str, Any], package: Mapping[str, str], draft: Path, root: Path | None,
    vacancy_text: str | None = None,
) -> dict[str, Any]:
    if root is None:
        raise ApplicationError("quality v2 requires a project root containing registry/candidate")
    bank_path = _contained_file(root, quality.get("evidence_bank"), "evidence_bank")
    ledger_path = _contained_file(draft, quality.get("claims_ledger"), "claims_ledger")
    bank = _read_yaml_mapping(bank_path, "candidate evidence bank")
    ledger = _read_yaml_mapping(ledger_path, "application claims ledger")
    try:
        report = validate_claims_ledger(ledger, bank, package, root)
    except EvidenceError as exc:
        raise ApplicationError(f"application grounding failed: {exc}") from exc
    review = quality["final_review"]
    if not isinstance(review.get("reviewer"), str) or not review["reviewer"].strip():
        raise ApplicationError("quality v2 final_review requires reviewer identity")
    hashes = review.get("document_sha256")
    if not isinstance(hashes, Mapping):
        raise ApplicationError("quality v2 final_review requires document_sha256")
    for name, field in APPLICATION_DOCUMENTS.items():
        if field in package and hashes.get(name) != _content_version(package[field]):
            raise ApplicationError(f"final review is stale or missing for {name}")
    if review.get("quality_gate") is not True:
        raise ApplicationError("quality v2 final_review quality_gate must be true")
    if "cv_markdown" in package:
        audit = quality.get("cv_audit")
        if not isinstance(audit, Mapping) or not str(audit.get("target_role") or "").strip():
            raise ApplicationError("quality v2 requires cv_audit target_role")
        proofs = audit.get("top_third_evidence_ids")
        if not isinstance(proofs, list) or not all(isinstance(item, str) for item in proofs) or len(set(proofs)) < 2 or not set(proofs).issubset(set(report["evidence_ids"])):
            raise ApplicationError("cv_audit requires at least two used top_third_evidence_ids")
        top = package["cv_markdown"][:len(package["cv_markdown"]) // 3]
        for identifier in proofs:
            if not any(claim.get("document") in {"cv", "cv_markdown"} and identifier in claim.get("evidence_ids", []) and claim.get("text", "") in top for claim in ledger["claims"]):
                raise ApplicationError("cv_audit evidence must anchor text in the final CV top third")
        decisions = audit.get("bullet_decisions")
        if not isinstance(decisions, list) or not decisions or any(
            not isinstance(item, Mapping) or item.get("decision") not in {"keep", "remove", "rewrite"}
            or not str(item.get("reason") or "").strip() or not str(item.get("text") or "").strip()
            for item in decisions
        ):
            raise ApplicationError("cv_audit requires reasoned bullet_decisions")
        report["cv_audit"] = dict(audit)
    from .requirements import validate_requirements

    try:
        requirements = validate_requirements(
            quality.get("requirements"), vacancy_text=vacancy_text,
            candidate_text="\n".join(entry["source"]["quote"] for entry in bank["entries"]),
        )
    except ValueError as exc:
        raise ApplicationError(f"quality v2 requirements: {exc}") from exc
    if not requirements:
        raise ApplicationError("quality v2 requires a structured requirements matrix")
    for requirement in requirements:
        ids = requirement.get("evidence_ids", [])
        if not isinstance(ids, list) or not all(isinstance(item, str) for item in ids) or not set(ids).issubset(set(report["evidence_ids"])):
            raise ApplicationError("requirement references unused evidence")
        if requirement["match"] in {"strong", "partial"} and not ids:
            raise ApplicationError("strong/partial requirements need evidence_ids")
        if requirement["candidate_quote"] and not any(
            entry["id"] in ids and requirement["candidate_quote"] in entry["source"]["quote"]
            for entry in bank["entries"]
        ):
            raise ApplicationError("requirement candidate_quote must occur in its referenced evidence")
    if "cover_letter_markdown" in package:
        for story in quality["cover_letter"]["evidence_stories"]:
            ids = story.get("evidence_ids")
            if not isinstance(ids, list) or not ids or not all(isinstance(item, str) for item in ids) or not set(ids).issubset(set(report["evidence_ids"])):
                raise ApplicationError("cover letter stories require used evidence_ids")
            source = str(story.get("candidate_source", "")).replace("\\", "/")
            if not all(any(entry["id"] == identifier and entry["source"]["path"].replace("\\", "/") == source for entry in bank["entries"]) for identifier in ids):
                raise ApplicationError("cover letter story source must match its referenced evidence")
            if not all(any(claim.get("document") in {"cover-letter", "cover_letter_markdown"} and identifier in claim.get("evidence_ids", []) for claim in ledger["claims"]) for identifier in ids):
                raise ApplicationError("cover letter stories must ground actual letter claims")
    report.update({"reviewer": review["reviewer"], "document_sha256": dict(hashes), "requirements": requirements,
                   "evidence_bank_path": str(quality["evidence_bank"]), "claims_ledger_path": str(quality["claims_ledger"]),
                   "claims": ledger["claims"]})
    return report


def _required_handoffs(selected_documents: set[str]) -> tuple[str, ...]:
    required: set[str] = set()
    if "cv" in selected_documents:
        required.add("evidence-map.md")
    if "cover-letter" in selected_documents:
        required.update(("research.md", "evidence-map.md"))
    if selected_documents & {"analysis", "interview-preparation"}:
        required.update(_HANDOFF_REQUIREMENTS)
    return tuple(filename for filename in _HANDOFF_REQUIREMENTS if filename in required)


def _merge_quality_reports(
    previous: Any,
    current: Mapping[str, Any],
    *,
    document: str | None,
) -> dict[str, Any]:
    if document is None or not isinstance(previous, Mapping):
        return dict(current)
    merged = dict(previous)
    previous_documents = previous.get("documents")
    current_documents = current.get("documents")
    documents = dict(previous_documents) if isinstance(previous_documents, Mapping) else {}
    if isinstance(current_documents, Mapping):
        documents.update(current_documents)
    merged.update(current)
    merged["documents"] = documents
    previous_exports = previous.get("exports")
    current_exports = current.get("exports")
    if isinstance(previous_exports, Mapping) or isinstance(current_exports, Mapping):
        merged["exports"] = {
            **(dict(previous_exports) if isinstance(previous_exports, Mapping) else {}),
            **(dict(current_exports) if isinstance(current_exports, Mapping) else {}),
        }
    return merged


def _normalize_document(document: str | None) -> str | None:
    if document is None:
        return None
    normalized = document.strip().casefold()
    if normalized not in APPLICATION_DOCUMENTS:
        choices = ", ".join(APPLICATION_DOCUMENTS)
        raise ValueError(f"unknown application document {document!r}; expected: {choices}")
    return normalized


def _selected_documents(document: str | None) -> tuple[str, ...]:
    if document is None:
        return tuple(APPLICATION_DOCUMENTS)
    return (document,)


def _selected_fields(document: str | None) -> tuple[str, ...]:
    return tuple(APPLICATION_DOCUMENTS[name] for name in _selected_documents(document))


def _validate_cv_role_technologies(markdown: str) -> None:
    roles: list[tuple[str, list[str]]] = []
    current_title: str | None = None
    current_lines: list[str] = []
    in_experience = False
    for line in markdown.splitlines():
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip()
            if level == 2:
                if in_experience and current_title is not None:
                    roles.append((current_title, current_lines))
                if in_experience:
                    break
                in_experience = title.casefold() == "experience"
                current_title = None
                current_lines = []
                continue
            if in_experience and level == 3:
                if current_title is not None:
                    roles.append((current_title, current_lines))
                current_title = title
                current_lines = []
                continue
        if in_experience and current_title is not None:
            current_lines.append(line)
    else:
        if in_experience and current_title is not None:
            roles.append((current_title, current_lines))

    missing = [
        title
        for title, lines in roles
        if not any(
            re.match(r"^\s*(?:\*\*)?Technologies(?:\*\*)?\s*:\s*\S", line, re.IGNORECASE)
            for line in lines
        )
    ]
    if missing:
        raise ApplicationError(
            "cv_markdown Experience roles are missing evidence-backed Technologies lines: "
            + ", ".join(missing)
        )


def _validate_cv_experience_age(
    markdown: str, *, reference_date: date | datetime | None
) -> None:
    if isinstance(reference_date, datetime):
        today = reference_date.date()
    elif isinstance(reference_date, date):
        today = reference_date
    else:
        today = datetime.now(timezone.utc).date()
    cutoff = (today.year - 10, today.month)

    lines = markdown.splitlines()
    experience_lines: list[str] = []
    in_experience = False
    for line in lines:
        heading = re.match(r"^(#{1,6})\s+(.+?)\s*$", line.strip())
        if heading:
            level = len(heading.group(1))
            title = heading.group(2).strip().casefold()
            if level == 2:
                if in_experience:
                    break
                in_experience = title == "experience"
                continue
        if in_experience:
            experience_lines.append(line)

    for match in _EXPERIENCE_DATE_RANGE_RE.finditer("\n".join(experience_lines)):
        end = match.group("end")
        if end.casefold() in {"present", "current"}:
            continue
        end_parts = end.split()
        if len(end_parts) == 1:
            end_month = 12
            end_year = int(end_parts[0])
        else:
            end_month = next(
                index
                for index, month in enumerate(_MONTH_NAMES, start=1)
                if month.casefold() == end_parts[0].casefold()
            )
            end_year = int(end_parts[1])
        if (end_year, end_month) < cutoff:
            raise ApplicationError(
                "cv_markdown Experience includes employment that ended more than "
                f"10 years ago: {match.group(0)}"
            )


def _validate_cv_headline(markdown: str, vacancy: Mapping[str, Any]) -> None:
    title = _vacancy_title(vacancy)
    if not title:
        return
    lines = markdown.splitlines()
    if not lines:
        raise ApplicationError("cv_markdown must start with the candidate name")
    name_match = re.match(r"^#\s+(.+?)\s*$", lines[0])
    if not name_match:
        raise ApplicationError("cv_markdown must start with an H1 candidate name")
    if len(lines) < 2 or not lines[1].strip():
        raise ApplicationError(
            "cv_markdown must place a vacancy-aligned professional headline "
            "immediately after the candidate name"
        )
    headline = lines[1].strip()
    if headline.startswith("#"):
        raise ApplicationError(
            "cv_markdown headline must be plain text immediately after the candidate name"
        )

    title_terms = _headline_terms(title)
    headline_terms = _headline_terms(headline)
    if not title_terms:
        return
    distinctive_terms = [
        term for term in title_terms if term not in _HEADLINE_GENERIC_TERMS
    ]
    required_terms = distinctive_terms or title_terms
    matches = sorted(set(required_terms) & set(headline_terms))
    minimum_matches = 1 if distinctive_terms else min(2, len(required_terms))
    if len(matches) < minimum_matches:
        expected = ", ".join(required_terms[:5])
        raise ApplicationError(
            "cv_markdown headline is not aligned with vacancy.metadata.title "
            f"'{title}'; expected headline terms such as: {expected}"
        )


def _vacancy_title(vacancy: Mapping[str, Any]) -> str:
    metadata = vacancy.get("metadata")
    if not isinstance(metadata, Mapping):
        return ""
    return str(metadata.get("title") or "").strip()


def _headline_terms(value: str) -> list[str]:
    terms: list[str] = []
    seen: set[str] = set()
    for token in re.findall(r"[A-Za-z0-9]+", value.casefold()):
        if len(token) < 3 or token in _ROLE_LOCATION_TERMS or token in _ROLE_NOISE_TERMS:
            continue
        if token not in seen:
            terms.append(token)
            seen.add(token)
    return terms


def _load_vacancy(
    directory: Path, meta: Mapping[str, Any]
) -> tuple[dict[str, Any], str, str]:
    job_path = directory / "job.md"
    if not op.exists(job_path):
        raise ApplicationError(f"vacancy job description is missing: {job_path}")
    job_text = op.read_text(job_path).strip()
    if not job_text:
        raise ApplicationError(f"vacancy job description is empty: {job_path}")
    company_path = directory / "company.md"
    company_text = op.read_text(company_path).strip() if op.exists(company_path) else ""
    vacancy = {
        "metadata": dict(meta),
        "job_description": job_text,
        "provided_company_information": company_text or None,
    }
    versioned_metadata = {
        key: value for key, value in meta.items() if key != "application_directory"
    }
    vacancy_version = _content_version(
        json.dumps(
            {"metadata": versioned_metadata, "job_description": job_text},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    company_version = _content_version(company_text)
    return vacancy, vacancy_version, company_version


def _application_directory(directory: Path, meta: Mapping[str, Any]) -> Path:
    name = str(meta.get("application_directory", _DEFAULT_APPLICATION_DIRECTORY)).strip()
    if not name or Path(name).name != name or not name.startswith("application"):
        raise ApplicationError("application_directory must be a single application-prefixed directory name")
    return directory / name


def _record_application_directory(meta_path: Path, meta: Mapping[str, Any], directory_name: str) -> None:
    updated = dict(meta)
    updated["application_directory"] = directory_name
    _write_text(
        meta_path,
        yaml.safe_dump(updated, allow_unicode=True, sort_keys=False),
    )


def _package_is_current(
    application_dir: Path,
    manifest_path: Path,
    expected_versions: Mapping[str, str],
    *,
    document: str | None = None,
) -> bool:
    if not op.exists(manifest_path):
        return False
    try:
        manifest = _read_yaml_mapping(manifest_path, "application manifest")
    except ApplicationError:
        return False
    document = _normalize_document(document)
    quality = manifest.get("quality", {})
    quality_documents = quality.get("documents", {}) if isinstance(quality, Mapping) else {}
    for name in _selected_documents(document):
        receipt = quality_documents.get(name, {}) if isinstance(quality_documents, Mapping) else {}
        if isinstance(receipt, Mapping) and receipt.get("evidence_bank_path"):
            root = op.project_root(application_dir)
            if root is None:
                return False
            try:
                path = _contained_file(root, receipt["evidence_bank_path"], "evidence_bank")
                bank = _read_yaml_mapping(path, "candidate evidence bank")
                if validate_evidence_bank(bank, root)["sha256"] != receipt.get("evidence_bank_sha256"):
                    return False
                markdown = op.read_text(application_dir / APPLICATION_FILES[APPLICATION_DOCUMENTS[name]])
                if _content_version(markdown.strip() + "\n") != receipt.get("sha256"):
                    return False
                if name in {"cv", "cover-letter"}:
                    from .document_quality import file_sha256

                    exports = quality.get("exports", {})
                    export = exports.get(name, {}) if isinstance(exports, Mapping) else {}
                    if not isinstance(export, Mapping) or file_sha256(application_dir / f"{name}.docx") != export.get("artifact_sha256"):
                        return False
                    if file_sha256(application_dir / f"{name}.md") != export.get("source_sha256"):
                        return False
                    if name == "cv":
                        stem = str(expected_versions.get("cv_export_stem", ""))
                        if file_sha256(application_dir / f"{stem}.docx") != export.get("artifact_sha256"):
                            return False
                        if file_sha256(application_dir / f"{stem}.md") != export.get("source_sha256"):
                            return False
            except (ApplicationError, EvidenceError, OSError):
                return False
    document_versions = manifest.get("documents")
    if isinstance(document_versions, dict):
        for selected_document in _selected_documents(document):
            versions = document_versions.get(selected_document)
            if not isinstance(versions, dict) or any(
                versions.get(key) != value for key, value in expected_versions.items()
            ):
                return False
            if not all(
                (application_dir / filename).is_file()
                for filename in _required_document_files(selected_document, expected_versions)
            ):
                return False
        return True

    if any(manifest.get(key) != value for key, value in expected_versions.items()):
        return False
    return all(
        (application_dir / filename).is_file()
        for selected_document in _selected_documents(document)
        for filename in _required_document_files(selected_document, expected_versions)
    )


def _required_document_files(
    document: str,
    versions: Mapping[str, Any],
) -> tuple[str, ...]:
    if document == "cv":
        stem = str(versions.get("cv_export_stem") or "")
        return ("cv.md", "cv.docx", f"{stem}.md", f"{stem}.docx")
    if document == "cover-letter":
        return ("cover-letter.md", "cover-letter.docx")
    return (APPLICATION_FILES[APPLICATION_DOCUMENTS[document]],)


def _read_existing_manifest(path: Path) -> dict[str, Any]:
    if not op.exists(path):
        return {}
    try:
        return _read_yaml_mapping(path, "application manifest")
    except ApplicationError:
        return {}


def _document_versions_from_manifest(
    manifest: Mapping[str, Any],
    application_dir: Path,
) -> dict[str, dict[str, Any]]:
    documents = manifest.get("documents")
    if isinstance(documents, dict):
        return {
            str(name): dict(versions)
            for name, versions in documents.items()
            if name in APPLICATION_DOCUMENTS and isinstance(versions, dict)
        }
    legacy_versions = {
        key: manifest.get(key)
        for key in (
            "profile_version",
            "vacancy_version",
            "company_version",
            "prompt_version",
            "model",
            "cv_export_stem",
        )
    }
    if any(value is None for value in legacy_versions.values()):
        return {}
    generated_at = manifest.get("generated_at")
    if generated_at is not None:
        legacy_versions["generated_at"] = generated_at
    return {
        document: dict(legacy_versions)
        for document in APPLICATION_DOCUMENTS
        if all(
            (application_dir / filename).is_file()
            for filename in _required_document_files(document, legacy_versions)
        )
    }


def _copy_existing_application_files(source: Path, staging: Path) -> None:
    if not source.is_dir():
        return
    allowed = set(APPLICATION_FILES.values()) | {"cv.docx", "cover-letter.docx"}
    for path in source.iterdir():
        if not op.exists(path):
            continue
        if path.name in allowed or (
            path.name.startswith("CV_") and path.suffix.casefold() in {".md", ".docx"}
        ):
            shutil.copy2(path, staging / path.name)


def _remove_selected_outputs(staging: Path, document: str) -> None:
    field = APPLICATION_DOCUMENTS[document]
    filenames = {APPLICATION_FILES[field]}
    if document == "cv":
        filenames.add("cv.docx")
        filenames.update(
            path.name
            for path in staging.iterdir()
            if op.exists(path)
            and path.name.startswith("CV_")
            and path.suffix.casefold() in {".md", ".docx"}
        )
    elif document == "cover-letter":
        filenames.add("cover-letter.docx")
    for filename in filenames:
        path = staging / filename
        if op.exists(path):
            path.unlink()


def _staged_application_files(staging: Path) -> list[str]:
    return sorted(path.name for path in staging.iterdir() if op.exists(path))


def _cv_export_files(meta: Mapping[str, Any]) -> dict[str, str]:
    stem = _cv_export_stem(
        company=str(meta.get("company") or ""),
        title=str(meta.get("title") or ""),
    )
    return {
        "markdown": f"{stem}.md",
        "docx": f"{stem}.docx",
    }


def _cv_export_stem(*, company: str, title: str) -> str:
    company_part = _compact_company_slug(company) or "company"
    role_part = _pascal_role_slug(title) or "Role"
    stem = f"CV_{_CV_OWNER_STEM}_{company_part}_{role_part}"
    if len(stem) <= _MAX_CV_EXPORT_STEM_LENGTH:
        return stem
    digest = hashlib.sha256(stem.encode("utf-8")).hexdigest()[:8]
    prefix_length = _MAX_CV_EXPORT_STEM_LENGTH - len(digest) - 1
    return f"{stem[:prefix_length]}_{digest}"


def _compact_company_slug(value: str) -> str:
    tokens = re.findall(r"[A-Za-z0-9]+", value.casefold())
    filtered = [token for token in tokens if token not in _COMPANY_SUFFIX_TERMS]
    return "".join(filtered or tokens)


def _pascal_role_slug(value: str) -> str:
    segments = re.split(r"\s+\|\s+", value)
    kept: list[str] = []
    for segment in segments:
        if _is_role_noise_segment(segment):
            continue
        kept.append(segment)
    if not kept:
        kept = segments[:1]
    words = re.findall(r"[A-Za-z0-9]+", " ".join(kept))
    filtered = [word for word in words if word.casefold() not in _ROLE_NOISE_TERMS]
    return "".join(word[:1].upper() + word[1:] for word in filtered)


def _is_role_noise_segment(value: str) -> bool:
    words = re.findall(r"[A-Za-z]+", value.casefold())
    if not words:
        return True
    if any(word not in _ROLE_NOISE_TERMS for word in words) and not all(
        word in _ROLE_LOCATION_TERMS or word in _ROLE_NOISE_TERMS for word in words
    ):
        return False
    return True


def _publish_staged_package(staging: Path, target: Path, files: Sequence[str],
                            *, on_published: Callable[[Path], None] | None = None) -> None:
    expected = [*files, "manifest.yaml"]
    missing = [filename for filename in expected if not (staging / filename).is_file()]
    if missing:
        raise ApplicationError("staged application package is incomplete: " + ", ".join(missing))

    target.parent.mkdir(parents=True, exist_ok=True)
    backup = target.with_name(f".{target.name}.{uuid.uuid4().hex}.backup")
    had_previous = target.exists()
    if had_previous:
        os.replace(target, backup)
    try:
        os.replace(staging, target)
        if on_published is not None:
            on_published(target)
    except Exception:
        if target.exists() and not staging.exists():
            os.replace(target, staging)
        if had_previous and backup.exists() and not target.exists():
            os.replace(backup, target)
        raise
    finally:
        if backup.exists() and target.exists():
            shutil.rmtree(backup, ignore_errors=True)


def _find_docx_script() -> Path:
    configured = os.environ.get("MD_TO_DOCX_SCRIPT", "").strip()
    if configured:
        return Path(configured).expanduser()
    codex_home = os.environ.get("CODEX_HOME", "").strip()
    candidates = []
    if codex_home:
        candidates.append(Path(codex_home) / "skills" / "md-to-docx" / "scripts" / "convert_with_md_to_docx.ps1")
    candidates.append(
        Path.home() / ".codex" / "skills" / "md-to-docx" / "scripts" / "convert_with_md_to_docx.ps1"
    )
    for candidate in candidates:
        if op.exists(candidate):
            return candidate
    return candidates[0]


def _read_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(op.read_text(path))
    except OSError as exc:
        raise ApplicationError(f"cannot read {label} {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ApplicationError(f"invalid YAML in {label} {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ApplicationError(f"{label} must be a YAML mapping: {path}")
    return loaded


def _content_version(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _write_text(path: Path, content: str) -> None:
    handled = op.write_operational(path, content)
    if handled is not None:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc).replace(microsecond=0)
    return value.isoformat().replace("+00:00", "Z")
