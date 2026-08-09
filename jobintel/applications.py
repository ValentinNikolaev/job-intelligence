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
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol

import yaml


APPLICATION_FILES = {
    "cv_markdown": "cv.md",
    "cover_letter_markdown": "cover-letter.md",
    "analysis_markdown": "analysis.md",
    "interview_preparation_markdown": "interview-preparation.md",
}

_DEFAULT_APPLICATION_DIRECTORY = "application"
_FALLBACK_APPLICATION_DIRECTORY = "application-codex"
_CV_OWNER_STEM = "ValentinNikolaev"
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
_SIMPLE_LIFE_HEADING_RE = re.compile(r"^(?P<marks>#{2,4})\s+Simple(?:\.life| App| Life)\s*$")
_HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+")
_MONTH_YEAR_RANGE_RE = re.compile(
    rf"(?P<start>\b(?:{_MONTH_PATTERN})\s+\d{{4}})\s*[-–—]\s*"
    rf"(?P<end>Present|Current|(?:{_MONTH_PATTERN})\s+\d{{4}})\b"
)
_EXPERIENCE_DATE_RANGE_RE = re.compile(
    rf"(?P<start>\b(?:(?:{_MONTH_PATTERN})\s+)?\d{{4}})\s*[-–—]\s*"
    rf"(?P<end>Present|Current|(?:(?:{_MONTH_PATTERN})\s+)?\d{{4}})\b",
    re.IGNORECASE,
)

_REQUIRED_HEADINGS = {
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

    def __init__(self, directory: Path, *, model: str) -> None:
        if not model.strip():
            raise ValueError("a Codex model label is required")
        self.directory = directory.resolve()
        self.model = model.strip()

    def generate(
        self,
        *,
        prompt: str,
        candidate_profile: str,
        vacancy: Mapping[str, Any],
    ) -> Mapping[str, Any]:
        del prompt, candidate_profile, vacancy
        result: dict[str, str] = {}
        for field, filename in APPLICATION_FILES.items():
            path = self.directory / filename
            try:
                result[field] = path.read_text(encoding="utf-8")
            except OSError as exc:
                raise ApplicationError(f"cannot read Codex application draft {path}: {exc}") from exc
        return result


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
        if not self.script_path.is_file():
            raise ApplicationError(f"Markdown-to-DOCX converter not found: {self.script_path}")
        if not self.options_path.is_file():
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
        if not target.is_file() or target.stat().st_size == 0:
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
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.registry_root = registry_root.resolve()
        self.profile_paths = tuple(path.resolve() for path in profile_paths)
        self.prompt_path = prompt_path.resolve()
        self.client = client
        self.converter = converter
        self.model = str(getattr(client, "model", client.__class__.__name__))
        self._clock = clock or (lambda: datetime.now(timezone.utc))

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
        simple_life_end_date = _simple_life_cv_end_date(generated_at)
        expected_versions = {
            "profile_version": profile_version,
            "vacancy_version": vacancy_version,
            "company_version": company_version,
            "prompt_version": prompt_version,
            "model": self.model,
            "simple_life_end_date": simple_life_end_date,
            "cv_export_stem": _cv_export_stem(
                company=str(meta.get("company") or ""),
                title=str(meta.get("title") or ""),
            ),
        }
        application_dir = _application_directory(directory, meta)
        manifest_path = application_dir / "manifest.yaml"
        if not force and _package_is_current(application_dir, manifest_path, expected_versions):
            return PreparationResult("skipped", vacancy_id, directory.name)

        generated = validate_application_package(
            self.client.generate(
                prompt=prompt,
                candidate_profile=candidate_profile,
                vacancy=vacancy,
            ),
            vacancy=vacancy,
            reference_date=generated_at,
        )
        generated["cv_markdown"] = _apply_simple_life_cv_end_date(
            generated["cv_markdown"],
            simple_life_end_date,
        )
        cv_export_files = _cv_export_files(meta)

        staging = Path(tempfile.mkdtemp(prefix=".application-", dir=directory))
        try:
            for field, filename in APPLICATION_FILES.items():
                _write_text(staging / filename, generated[field])
            self.converter.convert(staging / "cv.md", staging / "cv.docx")
            self.converter.convert(
                staging / "cover-letter.md", staging / "cover-letter.docx"
            )
            shutil.copyfile(staging / "cv.md", staging / cv_export_files["markdown"])
            shutil.copyfile(staging / "cv.docx", staging / cv_export_files["docx"])
            manifest = {
                **expected_versions,
                "generated_at": _utc_iso(generated_at),
                "files": [
                    "cv.md",
                    "cv.docx",
                    cv_export_files["markdown"],
                    cv_export_files["docx"],
                    "cover-letter.md",
                    "cover-letter.docx",
                    "analysis.md",
                    "interview-preparation.md",
                ],
            }
            _write_text(
                staging / "manifest.yaml",
                yaml.safe_dump(manifest, allow_unicode=True, sort_keys=False),
            )
            try:
                _publish_staged_package(staging, application_dir, manifest["files"])
            except PermissionError:
                if application_dir.name != _DEFAULT_APPLICATION_DIRECTORY:
                    raise
                application_dir = directory / _FALLBACK_APPLICATION_DIRECTORY
                _publish_staged_package(staging, application_dir, manifest["files"])
                _record_application_directory(directory / "meta.yaml", meta, application_dir.name)
        finally:
            shutil.rmtree(staging, ignore_errors=True)

        return PreparationResult("prepared", vacancy_id, directory.name)

    def is_current(self, directory: Path) -> bool:
        directory = directory.resolve()
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
        _, profile_version = self._load_candidate_profile()
        _, prompt_version = self._load_prompt()
        _, vacancy_version, company_version = _load_vacancy(directory, meta)
        simple_life_end_date = _simple_life_cv_end_date(self._clock())
        expected_versions = {
            "profile_version": profile_version,
            "vacancy_version": vacancy_version,
            "company_version": company_version,
            "prompt_version": prompt_version,
            "model": self.model,
            "simple_life_end_date": simple_life_end_date,
            "cv_export_stem": _cv_export_stem(
                company=str(meta.get("company") or ""),
                title=str(meta.get("title") or ""),
            ),
        }
        application_dir = _application_directory(directory, meta)
        return _package_is_current(
            application_dir, application_dir / "manifest.yaml", expected_versions
        )

    def _load_candidate_profile(self) -> tuple[str, str]:
        if not self.profile_paths:
            raise ApplicationError("at least one candidate source-of-truth path is required")
        sections = []
        for path in self.profile_paths:
            if not path.is_file():
                raise ApplicationError(f"candidate source-of-truth file not found: {path}")
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                raise ApplicationError(f"candidate source-of-truth file is empty: {path}")
            sections.append(f"## Source: {path.name}\n\n{content}")
        combined = "\n\n".join(sections)
        return combined, _content_version(combined)

    def _load_prompt(self) -> tuple[str, str]:
        if not self.prompt_path.is_file():
            raise ApplicationError(f"application prompt not found: {self.prompt_path}")
        prompt = self.prompt_path.read_text(encoding="utf-8").strip()
        if not prompt:
            raise ApplicationError(f"application prompt is empty: {self.prompt_path}")
        return prompt, _content_version(prompt)


def resolve_job_directories(registry_root: Path, selector: str) -> list[Path]:
    jobs_dir = registry_root.resolve() / "jobs"
    if selector.casefold() == "all":
        return sorted(path.parent for path in jobs_dir.glob("*/meta.yaml"))

    direct = jobs_dir / selector
    if direct.is_dir() and (direct / "meta.yaml").is_file():
        return [direct.resolve()]

    matches = []
    for meta_path in jobs_dir.glob("*/meta.yaml"):
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
    reference_date: date | datetime | None = None,
) -> dict[str, str]:
    expected = set(APPLICATION_FILES)
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
    for field in APPLICATION_FILES:
        content = value[field]
        if not isinstance(content, str) or not content.strip():
            raise ApplicationError(f"{field} must be non-empty Markdown")
        clean = content.strip() + "\n"
        if "```" in clean[:20]:
            raise ApplicationError(f"{field} must not be wrapped in a code fence")
        result[field] = clean

    for field, headings in _REQUIRED_HEADINGS.items():
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
    _validate_cv_experience_age(result["cv_markdown"], reference_date=reference_date)
    if vacancy is not None:
        _validate_cv_headline(result["cv_markdown"], vacancy)
    return result


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
    if not job_path.is_file():
        raise ApplicationError(f"vacancy job description is missing: {job_path}")
    job_text = job_path.read_text(encoding="utf-8").strip()
    if not job_text:
        raise ApplicationError(f"vacancy job description is empty: {job_path}")
    company_path = directory / "company.md"
    company_text = company_path.read_text(encoding="utf-8").strip() if company_path.is_file() else ""
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
) -> bool:
    if not manifest_path.is_file():
        return False
    try:
        manifest = _read_yaml_mapping(manifest_path, "application manifest")
    except ApplicationError:
        return False
    if any(manifest.get(key) != value for key, value in expected_versions.items()):
        return False
    required = [
        "cv.md",
        "cv.docx",
        "cover-letter.md",
        "cover-letter.docx",
        "analysis.md",
        "interview-preparation.md",
    ]
    files = manifest.get("files")
    if isinstance(files, list):
        required.extend(
            filename
            for filename in files
            if isinstance(filename, str) and filename.startswith("CV_")
        )
    return all((application_dir / filename).is_file() for filename in required)


def _simple_life_cv_end_date(value: datetime) -> str:
    previous_month = value.replace(day=1) - timedelta(days=1)
    return f"{_MONTH_NAMES[previous_month.month - 1]} {previous_month.year}"


def _apply_simple_life_cv_end_date(markdown: str, end_date: str) -> str:
    lines = markdown.splitlines(keepends=True)
    in_simple_life = False
    simple_life_heading_level = 0
    changed = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        simple_life_heading = _SIMPLE_LIFE_HEADING_RE.match(stripped)
        if simple_life_heading:
            in_simple_life = True
            simple_life_heading_level = len(simple_life_heading.group("marks"))
            continue
        heading = _HEADING_RE.match(stripped)
        if (
            in_simple_life
            and heading
            and len(heading.group("marks")) <= simple_life_heading_level
        ):
            in_simple_life = False
        if not in_simple_life or changed:
            continue

        updated = _MONTH_YEAR_RANGE_RE.sub(
            lambda match: f"{match.group('start')} - {end_date}",
            line,
            count=1,
        )
        if updated != line:
            lines[index] = updated
            changed = True
    return "".join(lines)


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
    return f"CV_{_CV_OWNER_STEM}_{company_part}_{role_part}"


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


def _publish_staged_package(staging: Path, target: Path, files: Sequence[str]) -> None:
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
    except Exception:
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
        if candidate.is_file():
            return candidate
    return candidates[0]


def _read_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
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
