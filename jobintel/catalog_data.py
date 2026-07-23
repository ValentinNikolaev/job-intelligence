from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .models import VACANCY_STATUSES


class CatalogDataError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ArtifactLinks:
    job_md: str | None
    company_md: str | None
    match_md: str | None
    cv_md: str | None
    cv_docx: str | None
    cover_letter_md: str | None
    cover_letter_docx: str | None
    analysis_md: str | None
    interview_preparation_md: str | None


@dataclass(frozen=True, slots=True)
class CatalogVacancy:
    vacancy_id: str
    directory: Path
    company: str
    title: str
    location: str | None
    status: str
    discovered_at: str
    updated_at: str | None
    status_changed_at: str
    score: int | None
    recommendation: str | None
    sources: tuple[dict[str, Any], ...]
    artifacts: ArtifactLinks

    def to_api_dict(self, *, base: Path | None = None) -> dict[str, Any]:
        return {
            "vacancy_id": self.vacancy_id,
            "directory": _path_value(self.directory, base),
            "company": self.company,
            "title": self.title,
            "location": self.location,
            "status": self.status,
            "discovered_at": self.discovered_at,
            "updated_at": self.updated_at,
            "status_changed_at": self.status_changed_at,
            "score": self.score,
            "recommendation": self.recommendation,
            "sources": list(self.sources),
            "artifacts": {
                "job_md": _optional_path_value(self.artifacts.job_md, base),
                "company_md": _optional_path_value(self.artifacts.company_md, base),
                "match_md": _optional_path_value(self.artifacts.match_md, base),
                "cv_md": _optional_path_value(self.artifacts.cv_md, base),
                "cv_docx": _optional_path_value(self.artifacts.cv_docx, base),
                "cover_letter_md": _optional_path_value(self.artifacts.cover_letter_md, base),
                "cover_letter_docx": _optional_path_value(self.artifacts.cover_letter_docx, base),
                "analysis_md": _optional_path_value(self.artifacts.analysis_md, base),
                "interview_preparation_md": _optional_path_value(
                    self.artifacts.interview_preparation_md, base
                ),
            },
        }


def load_catalog_vacancies(registry_root: Path) -> list[CatalogVacancy]:
    registry_root = registry_root.resolve()
    jobs_dir = registry_root / "jobs"
    rows = []
    for meta_path in sorted(jobs_dir.glob("*/meta.yaml")):
        meta = _read_mapping(meta_path)
        directory = meta_path.parent
        _require_fields(
            meta,
            ("id", "company", "title", "sources", "discovered_at", "status", "status_history"),
            meta_path,
        )
        discovered_at = _timestamp(meta["discovered_at"], "discovered_at", meta_path)
        status = str(meta["status"]).strip()
        if status not in VACANCY_STATUSES:
            raise CatalogDataError(f"invalid vacancy status {status!r}: {meta_path}")
        status_changed_at = _status_changed_at(meta, status, meta_path)
        match = _read_match(directory / "match.yaml")
        rows.append(
            CatalogVacancy(
                vacancy_id=str(meta["id"]),
                directory=directory,
                company=str(meta["company"]),
                title=str(meta["title"]),
                location=_optional_text(meta.get("location")),
                status=status,
                discovered_at=discovered_at,
                updated_at=_optional_timestamp(meta.get("updated_at"), "updated_at", meta_path),
                status_changed_at=status_changed_at,
                score=match["score"] if match else None,
                recommendation=match["recommendation"] if match else None,
                sources=_source_refs(meta["sources"], meta_path),
                artifacts=_artifacts(directory),
            )
        )
    rows.sort(key=lambda row: (row.discovered_at, row.vacancy_id), reverse=True)
    return rows


def _source_refs(value: Any, path: Path) -> tuple[dict[str, Any], ...]:
    if not isinstance(value, list):
        raise CatalogDataError(f"sources must be a list: {path}")
    refs = []
    for item in value:
        if not isinstance(item, dict):
            continue
        refs.append(
            {
                "source": str(item.get("source", "")),
                "source_job_id": str(item.get("source_job_id", "")),
                "url": str(item.get("url", "")),
            }
        )
    return tuple(refs)


def _artifacts(directory: Path) -> ArtifactLinks:
    application = directory / "application"
    return ArtifactLinks(
        job_md=_artifact(directory / "job.md"),
        company_md=_artifact(directory / "company.md"),
        match_md=_artifact(directory / "match.md"),
        cv_md=_artifact(application / "cv.md"),
        cv_docx=_artifact(application / "cv.docx"),
        cover_letter_md=_artifact(application / "cover-letter.md"),
        cover_letter_docx=_artifact(application / "cover-letter.docx"),
        analysis_md=_artifact(application / "analysis.md"),
        interview_preparation_md=_artifact(application / "interview-preparation.md"),
    )


def _artifact(path: Path) -> str | None:
    try:
        return str(path) if path.is_file() else None
    except OSError:
        return None


def _read_match(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    match = _read_mapping(path)
    score = match.get("score")
    recommendation = match.get("recommendation")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise CatalogDataError(f"match analysis has invalid score: {path}")
    if recommendation not in {
        "strong_match",
        "match",
        "possible_match",
        "weak_match",
        "not_match",
    }:
        raise CatalogDataError(f"match analysis has invalid recommendation: {path}")
    return {"score": score, "recommendation": str(recommendation)}


def _status_changed_at(meta: dict[str, Any], status: str, path: Path) -> str:
    history = meta["status_history"]
    if not isinstance(history, list) or not history:
        raise CatalogDataError(f"status_history must be a non-empty list: {path}")
    previous_time = ""
    for entry in history:
        if not isinstance(entry, dict) or entry.get("status") not in VACANCY_STATUSES:
            raise CatalogDataError(f"invalid status_history entry: {path}")
        changed_at = _timestamp(entry.get("changed_at"), "status_history.changed_at", path)
        if previous_time and changed_at < previous_time:
            raise CatalogDataError(f"status_history is not chronological: {path}")
        previous_time = changed_at
    if history[-1].get("status") != status:
        raise CatalogDataError(f"current status does not match status_history: {path}")
    return previous_time


def _read_mapping(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise CatalogDataError(f"cannot read YAML mapping {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise CatalogDataError(f"YAML document must be a mapping: {path}")
    return loaded


def _require_fields(meta: dict[str, Any], fields: tuple[str, ...], path: Path) -> None:
    missing = [field for field in fields if field not in meta]
    if missing:
        raise CatalogDataError(f"metadata missing {', '.join(missing)}: {path}")


def _optional_text(value: Any) -> str | None:
    text = str(value or "").strip()
    return text or None


def _optional_timestamp(value: Any, field: str, path: Path) -> str | None:
    if value in (None, ""):
        return None
    return _timestamp(value, field, path)


def _timestamp(value: Any, field: str, path: Path) -> str:
    text = str(value or "").strip()
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError as exc:
        raise CatalogDataError(f"invalid {field} timestamp {text!r}: {path}") from exc
    if parsed.tzinfo is None:
        raise CatalogDataError(f"{field} timestamp must include a timezone: {path}")
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _path_value(path: Path, base: Path | None) -> str:
    if base is None:
        return str(path)
    return os.path.relpath(path.resolve(), base.resolve()).replace("\\", "/")


def _optional_path_value(path: str | None, base: Path | None) -> str | None:
    if path is None:
        return None
    return _path_value(Path(path), base)
