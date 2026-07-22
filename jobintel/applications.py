from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import yaml


APPLICATION_FILES = {
    "cv_markdown": "cv.md",
    "cover_letter_markdown": "cover-letter.md",
    "analysis_markdown": "analysis.md",
    "interview_preparation_markdown": "interview-preparation.md",
}

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
        expected_versions = {
            "profile_version": profile_version,
            "vacancy_version": vacancy_version,
            "company_version": company_version,
            "prompt_version": prompt_version,
            "model": self.model,
        }
        application_dir = directory / "application"
        manifest_path = application_dir / "manifest.yaml"
        if not force and _package_is_current(application_dir, manifest_path, expected_versions):
            return PreparationResult("skipped", vacancy_id, directory.name)

        generated = validate_application_package(
            self.client.generate(
                prompt=prompt,
                candidate_profile=candidate_profile,
                vacancy=vacancy,
            )
        )

        staging = Path(tempfile.mkdtemp(prefix=".application-", dir=directory))
        try:
            for field, filename in APPLICATION_FILES.items():
                _write_text(staging / filename, generated[field])
            self.converter.convert(staging / "cv.md", staging / "cv.docx")
            self.converter.convert(
                staging / "cover-letter.md", staging / "cover-letter.docx"
            )
            manifest = {
                **expected_versions,
                "generated_at": _utc_iso(self._clock()),
                "files": [
                    "cv.md",
                    "cv.docx",
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
            _publish_staged_package(staging, application_dir, manifest["files"])
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
        }
        application_dir = directory / "application"
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


def validate_application_package(value: Mapping[str, Any]) -> dict[str, str]:
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
    return result


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
    vacancy_version = _content_version(
        json.dumps(
            {"metadata": dict(meta), "job_description": job_text},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )
    )
    company_version = _content_version(company_text)
    return vacancy, vacancy_version, company_version


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
    return all((application_dir / filename).is_file() for filename in required)


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
