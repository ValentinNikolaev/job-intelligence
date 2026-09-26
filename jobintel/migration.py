"""Deterministic migration of the legacy file registry into document storage.

The planner is intentionally independent from MongoDB.  It reads the legacy files,
produces stable documents and a coverage report, and only then hands the plan to a
store.  Historical text is data: nothing in an archive or feedback file is executed.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import uuid
import zipfile
from collections import Counter, defaultdict
from contextlib import nullcontext
from dataclasses import dataclass, field
from pathlib import Path, PurePosixPath
from typing import Any, Iterable, Mapping, Protocol, Sequence
from urllib.parse import quote, unquote, urlsplit

import yaml


MIGRATION_SCHEMA_VERSION = 1
PROJECT_NAMESPACE = uuid.NAMESPACE_URL
OPERATIONAL_LOGS = (
    "manual-status-log.yaml",
    "application-confirmations.yaml",
    "codex-usage.yaml",
    "source-api-usage.yaml",
)
REPOSITORY_URL = "https://github.com/ValentinNikolaev/job-intelligence"
_COMPLETE_PACKAGE_FILES = frozenset({
    "cv.md", "cv.docx", "cover-letter.md", "cover-letter.docx",
    "analysis.md", "interview-preparation.md", "manifest.yaml",
})
_ACTUAL_DATE = re.compile(r"actual application date[^0-9]*(\d{4}-\d{2}-\d{2})", re.I)
_NOT_SUBMITTED = re.compile(r"(?:not|wasn['’]t|was not)\s+(?:externally\s+)?submitted|form not submitted", re.I)


class DocumentStore(Protocol):
    def get(self, collection: str, key: str) -> Mapping[str, Any] | None: ...
    def put(
        self,
        collection: str,
        key: str,
        document: Mapping[str, Any],
        *,
        expected_revision: int,
    ) -> Mapping[str, Any] | bool: ...
    def list(self, collection: str, *args: Any, **kwargs: Any) -> Sequence[Mapping[str, Any]]: ...
    def insert_batch(self, collection: str, documents: Sequence[Mapping[str, Any]]) -> int: ...
    def lease(self, owner: str, *args: Any, **kwargs: Any): ...
    def transaction(self): ...


@dataclass(frozen=True, slots=True)
class Evidence:
    locator: str
    sha256: str
    size: int

    def as_dict(self) -> dict[str, Any]:
        return {"locator": self.locator, "sha256": self.sha256, "size": self.size}


@dataclass(slots=True)
class Observation:
    directory: str
    scope: str
    archived: bool
    archive_category: str | None
    meta: dict[str, Any]
    meta_evidence: Evidence
    job_text: str = ""
    company_text: str | None = None
    match: dict[str, Any] | None = None
    triage: dict[str, Any] | None = None
    artifacts: list[dict[str, Any]] = field(default_factory=list)


def stable_id(prefix: str, *parts: object) -> str:
    name = "\0".join((prefix, *(str(part) for part in parts)))
    return str(uuid.uuid5(PROJECT_NAMESPACE, name))


def status_event_id(
    vacancy_id: str,
    recorded_at: str,
    from_status: str | None,
    to_status: str,
) -> str:
    return stable_id(
        "jobintel:status-event:v1",
        vacancy_id,
        recorded_at,
        from_status or "",
        to_status,
    )


def application_id(vacancy_id: str, applied_event_id: str) -> str:
    return stable_id("jobintel:application:v1", vacancy_id, applied_event_id)


def submission_confirmation_id(vacancy_id: str, recorded_at: str) -> str:
    return stable_id("jobintel:submission-confirmation:v1", vacancy_id, recorded_at)


def prefilter_id(source: str, source_job_id: str) -> str:
    return stable_id("jobintel:prefilter:v1", source, source_job_id)


def source_identity_id(source: str, source_job_id: str) -> str:
    return stable_id("jobintel:source-identity:v1", source, source_job_id)


def project_vacancy_history(
    vacancy_record: Mapping[str, Any],
    manual_events: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Project one vacancy's immutable events and application attempts.

    A matching manual audit event enriches its status-history event.  An applied
    transition creates a distinct application, so a later repeated application to
    the same vacancy receives a different stable ID.  ``recorded_at`` is retained
    even when the actual submission time is unknown.
    """
    meta = vacancy_record.get("meta")
    if not isinstance(meta, Mapping):
        raise ValueError("vacancy record requires a metadata mapping")
    vacancy_id = str(vacancy_record.get("_id") or meta.get("id") or "")
    if not vacancy_id:
        raise ValueError("vacancy record requires an existing vacancy UUID")
    relevant = [dict(item) for item in manual_events if str(item.get("vacancy_id") or "") == vacancy_id]
    manual_by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    manual_order_by_key: dict[tuple[str, str, str], int] = {}
    for manual_order, item in enumerate(relevant):
        key = (
            str(item.get("changed_at") or ""),
            str(item.get("from_status") or ""),
            str(item.get("to_status") or ""),
        )
        manual_by_key[key] = item
        manual_order_by_key[key] = manual_order

    events: list[dict[str, Any]] = []
    consumed: set[tuple[str, str, str]] = set()
    previous = ""
    history = meta.get("status_history") or []
    if not isinstance(history, list):
        raise ValueError(f"invalid status_history for {vacancy_id}")
    for ordinal, raw in enumerate(history):
        if not isinstance(raw, Mapping):
            raise ValueError(f"invalid status_history item for {vacancy_id}")
        status = str(raw.get("status") or "")
        recorded_at = str(raw.get("changed_at") or "")
        if not status or not recorded_at:
            raise ValueError(f"incomplete status_history item for {vacancy_id}")
        key = (recorded_at, previous, status)
        audit = manual_by_key.get(key)
        if audit is not None:
            consumed.add(key)
        event_id = status_event_id(vacancy_id, recorded_at, previous, status)
        event = {
            "_id": event_id,
            "schema_version": 1,
            "event_id": event_id,
            "vacancy_id": vacancy_id,
            "application_id": application_id(vacancy_id, event_id) if status == "applied" else None,
            "from_status": previous or None,
            "status": status,
            "effective_at": _effective_at(status, recorded_at, audit),
            "recorded_at": recorded_at,
            "reason": audit.get("reason") if audit else None,
            "note": audit.get("note") if audit else None,
            "actor": audit.get("actor") if audit else "system",
            "interaction": audit.get("interaction") if audit else None,
            "application_channel": (
                audit.get("application_channel") or audit.get("submission_channel")
                if audit
                else None
            ),
            "source": "status_history+manual_status_log" if audit else "status_history",
            "ordinal": ordinal,
            "manual_order": manual_order_by_key.get(key),
        }
        events.append(event)
        previous = status

    # A manual log is authoritative audit evidence even if an old archived metadata
    # snapshot does not contain the corresponding transition.
    for manual_order, audit in enumerate(relevant):
        key = (
            str(audit.get("changed_at") or ""),
            str(audit.get("from_status") or ""),
            str(audit.get("to_status") or ""),
        )
        if key in consumed:
            continue
        recorded_at, from_status, status = key
        if not recorded_at or not status:
            continue
        event_id = status_event_id(vacancy_id, recorded_at, from_status, status)
        events.append(
            {
                "_id": event_id,
                "schema_version": 1,
                "event_id": event_id,
                "vacancy_id": vacancy_id,
                "application_id": application_id(vacancy_id, event_id) if status == "applied" else None,
                "from_status": from_status or None,
                "status": status,
                "effective_at": _effective_at(status, recorded_at, audit),
                "recorded_at": recorded_at,
                "reason": audit.get("reason"),
                "note": audit.get("note"),
                "actor": audit.get("actor"),
                "interaction": audit.get("interaction"),
                "application_channel": audit.get("application_channel") or audit.get("submission_channel"),
                "source": "manual_status_log",
                "ordinal": None,
                "manual_order": manual_order,
            }
        )
    # Timestamps currently have second precision. Preserve the source sequence for
    # transitions recorded in the same second; event_id lexical order is unrelated
    # to lifecycle order.
    events.sort(
        key=lambda item: (
            str(item["recorded_at"]),
            0 if item.get("ordinal") is not None else 1,
            int(item.get("ordinal") if item.get("ordinal") is not None else item.get("manual_order") or 0),
        )
    )

    issues: list[dict[str, Any]] = []
    applications: list[dict[str, Any]] = []
    # A historical status value or prepared package is not evidence of an actual
    # submission. Only an append-only manual audit opens an application attempt.
    starts = [
        index
        for index, event in enumerate(events)
        if event["status"] == "applied" and "manual_status_log" in str(event.get("source"))
    ]
    confirmation = vacancy_record.get("submission_confirmation")
    if isinstance(confirmation, Mapping):
        recorded_at = str(confirmation.get("recorded_at") or "")
        # A confirmation fills a missing historical submission. It is redundant
        # when an audited applied transition already existed at confirmation time,
        # but remains a distinct earlier attempt when a later reapplication occurs.
        has_prior_applied = any(
            str(events[start].get("recorded_at") or "") < recorded_at
            for start in starts
        )
        if recorded_at and not has_prior_applied:
            confirmation_id = str(
                confirmation.get("confirmation_id")
                or submission_confirmation_id(vacancy_id, recorded_at)
            )
            app_id = application_id(vacancy_id, confirmation_id)
            first_later_start = starts[0] if starts else len(events)
            prior_events = events[:first_later_start]
            for related in prior_events:
                if related.get("status") != "found":
                    related["application_id"] = app_id
            current_event = prior_events[-1] if prior_events else None
            applications.append(
                {
                    "_id": app_id,
                    "schema_version": 1,
                    "application_id": app_id,
                    "vacancy_id": vacancy_id,
                    "applied_event_id": None,
                    "submission_confirmation_id": confirmation_id,
                    "directory": vacancy_record.get("directory"),
                    "company": meta.get("company"),
                    "title": meta.get("title"),
                    "applied_at_effective": confirmation.get("submitted_at"),
                    "applied_at_recorded": recorded_at,
                    "current_status": current_event.get("status") if current_event else meta.get("status"),
                    "status_changed_at": current_event.get("effective_at") if current_event else None,
                    "status_recorded_at": current_event.get("recorded_at") if current_event else None,
                    "source_url": _first_source_url(meta),
                    "channel": _application_channel(meta, confirmation),
                    "location": meta.get("location"),
                    "remote": meta.get("remote"),
                    "salary": _salary(meta),
                    "package_locator": _portable_package_locator(vacancy_record),
                    "confirmation": {
                        "state": "confirmed",
                        "reason": "explicit_user_confirmation",
                        "evidence": confirmation.get("note"),
                    },
                    "source_revision": int(vacancy_record.get("revision") or 1),
                }
            )
    for attempt_index, start in enumerate(starts):
        end = starts[attempt_index + 1] if attempt_index + 1 < len(starts) else len(events)
        event = events[start]
        app_id = str(event["application_id"])
        # Later status transitions belong to this attempt until another confirmed
        # application starts. Adding a future attempt never changes this boundary.
        for related in events[start:end]:
            related["application_id"] = app_id
        current_event = events[end - 1]
        evidence = " ".join(str(event.get(field) or "") for field in ("reason", "note"))
        confirmation_state = "needs_review" if _NOT_SUBMITTED.search(evidence) else "confirmed"
        if confirmation_state == "needs_review":
            issues.append(
                {
                    "code": "contradictory_applied_event",
                    "severity": "needs_review",
                    "vacancy_id": vacancy_id,
                    "event_id": event["event_id"],
                    "message": "Applied status conflicts with evidence that submission did not occur.",
                }
            )
        applications.append(
            {
                "_id": app_id,
                "schema_version": 1,
                "application_id": app_id,
                "vacancy_id": vacancy_id,
                "applied_event_id": event["event_id"],
                "directory": vacancy_record.get("directory"),
                "company": meta.get("company"),
                "title": meta.get("title"),
                "applied_at_effective": event.get("effective_at"),
                "applied_at_recorded": event.get("recorded_at"),
                "current_status": current_event["status"],
                "status_changed_at": current_event.get("effective_at") if current_event else None,
                "status_recorded_at": current_event.get("recorded_at") if current_event else None,
                "source_url": _first_source_url(meta),
                "channel": _application_channel(meta, event),
                "location": meta.get("location"),
                "remote": meta.get("remote"),
                "salary": _salary(meta),
                "package_locator": _portable_package_locator(vacancy_record),
                "confirmation": {
                    "state": confirmation_state,
                    "reason": event.get("reason"),
                    "evidence": event.get("note"),
                },
                "source_revision": int(vacancy_record.get("revision") or 1),
            }
        )
    return applications, events, issues


def _effective_at(status: str, recorded_at: str, audit: Mapping[str, Any] | None) -> str | None:
    if audit:
        text = " ".join(str(audit.get(field) or "") for field in ("reason", "note"))
        if status == "applied":
            match = _ACTUAL_DATE.search(text)
            if match:
                return match.group(1)
        # Manual audit timestamps record when the project learned or recorded the
        # status. They are not silently promoted to the employer event time.
        return None
    return recorded_at


def _first_source(meta: Mapping[str, Any]) -> Mapping[str, Any]:
    sources = meta.get("sources")
    if isinstance(sources, list) and sources and isinstance(sources[0], Mapping):
        return sources[0]
    return meta


def _first_source_url(meta: Mapping[str, Any]) -> str | None:
    value = _first_source(meta).get("url") or meta.get("source_url")
    return str(value) if value else None


def _application_channel(meta: Mapping[str, Any], event: Mapping[str, Any]) -> str | None:
    # A vacancy source (Adzuna, manual intake, and so on) does not identify how
    # an application was submitted. Only application-specific evidence does.
    for record in (event, meta):
        for field in ("application_channel", "submission_channel"):
            value = record.get(field)
            if value:
                return str(value)
    return None


def _salary(meta: Mapping[str, Any]) -> dict[str, Any]:
    raw = meta.get("salary")
    if isinstance(raw, Mapping):
        return dict(raw)
    return {
        "min": meta.get("salary_min"),
        "max": meta.get("salary_max"),
        "currency": meta.get("salary_currency"),
        "period": meta.get("salary_period"),
        "gross_net": meta.get("salary_gross_net"),
    }


def _portable_package_locator(vacancy_record: Mapping[str, Any]) -> str | None:
    value = vacancy_record.get("package_url")
    if isinstance(value, str) and value.startswith(("https://", "http://")):
        return value
    return None


def _package_locator(observation: Observation, git_revision: str) -> str | None:
    """Link to associated package evidence without claiming it was submitted."""
    if not observation.artifacts:
        return None
    locator = observation.meta_evidence.locator
    if "!" in locator:
        archive_path = locator.split("!", 1)[0]
        return f"{REPOSITORY_URL}/blob/{quote(git_revision, safe='')}/{quote(archive_path, safe='/')}"

    roots: set[str] = set()
    for artifact in observation.artifacts:
        path = PurePosixPath(str(artifact.get("path") or ""))
        parts = path.parts
        for index, part in enumerate(parts):
            if part == "application" or part.startswith("application-"):
                roots.add(PurePosixPath(*parts[: index + 1]).as_posix())
                break
    if not roots:
        return None
    package_root = min(roots, key=lambda value: (PurePosixPath(value).name != "application", value))
    return f"{REPOSITORY_URL}/tree/{quote(git_revision, safe='')}/{quote(package_root, safe='/')}"


def _source_keys(meta: Mapping[str, Any]) -> list[tuple[str, str]]:
    keys: set[tuple[str, str]] = set()
    sources = meta.get("sources")
    if isinstance(sources, list):
        for item in sources:
            if isinstance(item, Mapping) and item.get("source") and item.get("source_job_id"):
                keys.add((str(item["source"]), str(item["source_job_id"])))
    if meta.get("source") and meta.get("source_job_id"):
        keys.add((str(meta["source"]), str(meta["source_job_id"])))
    return sorted(keys)


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _evidence(locator: str, raw: bytes) -> Evidence:
    return Evidence(locator, hashlib.sha256(raw).hexdigest(), len(raw))


def _load_yaml(raw: bytes, locator: str) -> dict[str, Any]:
    try:
        value = yaml.safe_load(raw.decode("utf-8"))
    except (UnicodeDecodeError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot parse {locator}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"expected YAML mapping: {locator}")
    return value


def _optional_yaml(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    return _load_yaml(path.read_bytes(), path.as_posix())


def _scan_direct(root: Path) -> list[Observation]:
    found: list[Observation] = []
    for scope in ("jobs", "rejected"):
        base = root / "registry" / scope
        if not base.is_dir():
            continue
        for directory in sorted(path for path in base.iterdir() if path.is_dir()):
            meta_path = directory / "meta.yaml"
            if not meta_path.is_file():
                continue
            raw = meta_path.read_bytes()
            meta = _load_yaml(raw, meta_path.as_posix())
            job_path = directory / "job.md"
            company_path = directory / "company.md"
            found.append(
                Observation(
                    directory=directory.name,
                    scope=scope,
                    archived=False,
                    archive_category=None,
                    meta=meta,
                    meta_evidence=_evidence(meta_path.relative_to(root).as_posix(), raw),
                    job_text=job_path.read_text(encoding="utf-8") if job_path.is_file() else "",
                    company_text=company_path.read_text(encoding="utf-8") if company_path.is_file() else None,
                    match=_optional_yaml(directory / "match.yaml"),
                    triage=_optional_yaml(directory / "triage.yaml"),
                    artifacts=_direct_artifacts(root, directory) if meta.get("id") else [],
                )
            )
    return found


def _direct_artifacts(root: Path, directory: Path) -> list[dict[str, Any]]:
    prefix = directory.relative_to(root).as_posix() + "/"
    result = subprocess.run(
        ["git", "ls-tree", "-rz", "--name-only", "HEAD", "--", prefix],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    if result.returncode:
        return []
    files: list[dict[str, Any]] = []
    for relative in sorted(line for line in result.stdout.split("\0") if "/application" in line):
        raw = _repo_bytes(root, relative)
        files.append({"path": relative, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
    return files


def _repo_bytes(root: Path, relative: str) -> bytes:
    return (root / relative).read_bytes()


def _scan_archives(
    root: Path,
    retained_vacancy_ids: set[str] | None = None,
) -> tuple[list[Observation], list[dict[str, Any]], dict[str, Any]]:
    observations: list[Observation] = []
    errors: list[dict[str, Any]] = []
    stats: dict[str, Counter[str]] = defaultdict(Counter)
    for archive_path in sorted((root / "archives").glob("*/*.zip")):
        category = archive_path.parent.name
        stats[category]["zip_count"] += 1
        stats[category]["zip_bytes"] += archive_path.stat().st_size
        try:
            with zipfile.ZipFile(archive_path) as archive:
                names = set(archive.namelist())
                for name in sorted(item for item in names if item.endswith("/meta.yaml")):
                    prefix = name[: -len("meta.yaml")]
                    raw = archive.read(name)
                    try:
                        meta = _load_yaml(raw, f"{archive_path}!{name}")
                    except ValueError as exc:
                        errors.append(
                            {
                                "code": "invalid_archive_metadata",
                                "severity": "warning" if retained_vacancy_ids is not None else "blocked",
                                "locator": str(exc),
                            }
                        )
                        continue
                    stats[category]["metadata_scanned"] += 1
                    vacancy_id = str(meta.get("id") or "")
                    if retained_vacancy_ids is not None and vacancy_id not in retained_vacancy_ids:
                        stats[category]["metadata_excluded"] += 1
                        continue
                    stats[category]["metadata_retained"] += 1
                    directory = prefix.rstrip("/").split("/")[-1]
                    locator = f"{archive_path.relative_to(root).as_posix()}!{name}"
                    observations.append(
                        Observation(
                            directory=directory,
                            scope="jobs" if meta.get("id") else "rejected",
                            archived=True,
                            archive_category=category,
                            meta=meta,
                            meta_evidence=_evidence(locator, raw),
                            job_text=_zip_text(archive, names, prefix + "job.md"),
                            company_text=_zip_text(archive, names, prefix + "company.md") or None,
                            match=_zip_yaml(archive, names, prefix + "match.yaml"),
                            triage=_zip_yaml(archive, names, prefix + "triage.yaml"),
                            artifacts=(
                                _zip_artifacts(root, archive_path, archive, prefix)
                                if meta.get("id")
                                else []
                            ),
                        )
                    )
                    stats[category]["metadata_count"] += 1
        except (OSError, zipfile.BadZipFile) as exc:
            errors.append(
                {
                    "code": "invalid_archive",
                    "severity": "warning" if retained_vacancy_ids is not None else "blocked",
                    "locator": archive_path.relative_to(root).as_posix(),
                    "message": str(exc),
                }
            )
    return observations, errors, {key: dict(value) for key, value in sorted(stats.items())}


def _zip_text(archive: zipfile.ZipFile, names: set[str], name: str) -> str:
    return archive.read(name).decode("utf-8") if name in names else ""


def _zip_yaml(archive: zipfile.ZipFile, names: set[str], name: str) -> dict[str, Any] | None:
    return _load_yaml(archive.read(name), name) if name in names else None


def _zip_artifacts(
    root: Path,
    archive_path: Path,
    archive: zipfile.ZipFile,
    prefix: str,
) -> list[dict[str, Any]]:
    files: list[dict[str, Any]] = []
    for name in sorted(item for item in archive.namelist() if item.startswith(prefix) and "/application" in item):
        info = archive.getinfo(name)
        if info.is_dir():
            continue
        raw = archive.read(info)
        files.append(
            {
                "path": f"{archive_path.relative_to(root).as_posix()}!{name}",
                "size": len(raw),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
        )
    return files


def inventory(root: Path) -> dict[str, Any]:
    """Return a bounded, deterministic report of all legacy inputs."""
    plan = build_plan(root)
    return plan["manifest"]


def build_plan(root: Path) -> dict[str, Any]:
    """Build an idempotent import plan without changing any external state."""
    root = root.resolve()
    git_revision = _git_revision(root)
    logs, manual_events, raw_confirmations = _operational_logs(root)
    confirmations, confirmation_issues = _normalize_submission_confirmations(raw_confirmations)
    confirmed_archive_ids = _confirmed_application_vacancy_ids(manual_events) | set(confirmations)
    direct = _scan_direct(root)
    archived, archive_errors, archive_stats = _scan_archives(root, confirmed_archive_ids)
    observations = direct + archived
    issues: list[dict[str, Any]] = [*archive_errors, *confirmation_issues]
    by_uuid: dict[str, list[Observation]] = defaultdict(list)
    prefilter: dict[tuple[str, str], list[Observation]] = defaultdict(list)
    source_owners: dict[tuple[str, str], set[str]] = defaultdict(set)
    for observation in observations:
        vacancy_id = str(observation.meta.get("id") or "")
        if vacancy_id:
            by_uuid[vacancy_id].append(observation)
            for key in _source_keys(observation.meta):
                source_owners[key].add(vacancy_id)
        else:
            keys = _source_keys(observation.meta)
            if not keys:
                issues.append(
                    {
                        "code": "idless_without_source_identity",
                        "severity": "blocked",
                        "locator": observation.meta_evidence.locator,
                    }
                )
            else:
                prefilter[keys[0]].append(observation)

    missing_confirmed = sorted(confirmed_archive_ids - set(by_uuid))
    for vacancy_id in missing_confirmed:
        issues.append(
            {
                "code": "confirmed_application_without_vacancy",
                "severity": "blocked",
                "vacancy_id": vacancy_id,
            }
        )

    vacancies: list[dict[str, Any]] = []
    artifact_manifests: list[dict[str, Any]] = []
    package_locators: dict[str, str] = {}
    for vacancy_id, rows in sorted(by_uuid.items()):
        projections = {
            _canonical_json(
                {
                    "company": row.meta.get("company"),
                    "title": row.meta.get("title"),
                    "sources": _source_keys(row.meta),
                }
            )
            for row in rows
        }
        if len(projections) > 1:
            issues.append(
                {
                    "code": "vacancy_uuid_identity_conflict",
                    "severity": "blocked",
                    "vacancy_id": vacancy_id,
                    "locators": sorted(row.meta_evidence.locator for row in rows),
                }
            )
        chosen = max(rows, key=_observation_order)
        evidence = [row.meta_evidence.as_dict() for row in sorted(rows, key=lambda item: item.meta_evidence.locator)]
        vacancy = {
            "_id": vacancy_id,
            "schema_version": 1,
            "directory": chosen.directory,
            "scope": chosen.scope,
            "archived": chosen.archived,
            "archive_category": chosen.archive_category,
            "meta": chosen.meta,
            "job_text": chosen.job_text,
            "company_text": chosen.company_text,
            "match": chosen.match,
            "triage": chosen.triage,
            "legacy_evidence": evidence,
        }
        vacancies.append(vacancy)
        package_observation = chosen if chosen.artifacts else max(
            (row for row in rows if row.artifacts),
            key=_observation_order,
            default=None,
        )
        package_locator = _package_locator(package_observation, git_revision) if package_observation else None
        if package_locator:
            package_locators[vacancy_id] = package_locator
        for row in rows:
            if not row.artifacts:
                continue
            package_key = stable_id(
                "jobintel:package:v1",
                vacancy_id,
                row.meta_evidence.locator.rsplit("/meta.yaml", 1)[0],
            )
            artifact_manifests.append(
                {
                    "_id": package_key,
                    "schema_version": 1,
                    "vacancy_id": vacancy_id,
                    "directory": row.directory,
                    "evidence_locator": row.meta_evidence.locator,
                    "files": row.artifacts,
                }
            )

    prefilter_docs: list[dict[str, Any]] = []
    for (source, source_job_id), rows in sorted(prefilter.items()):
        chosen = max(rows, key=_observation_order)
        key = prefilter_id(source, source_job_id)
        prefilter_docs.append(
            {
                "_id": key,
                "schema_version": 1,
                "directory": chosen.directory,
                "scope": "rejected",
                "archived": chosen.archived,
                "archive_category": chosen.archive_category,
                "meta": chosen.meta,
                "job_text": chosen.job_text,
                "company_text": chosen.company_text,
                "match": chosen.match,
                "triage": chosen.triage,
                "source": source,
                "source_job_id": source_job_id,
                "observation_count": len(rows),
                "evidence": [row.meta_evidence.as_dict() for row in sorted(rows, key=lambda item: item.meta_evidence.locator)],
            }
        )

    source_identity_docs: list[dict[str, Any]] = []
    all_source_keys = set(source_owners) | set(prefilter)
    for source, source_job_id in sorted(all_source_keys):
        vacancy_ids = sorted(source_owners.get((source, source_job_id), set()))
        prefilter_ids = [prefilter_id(source, source_job_id)] if (source, source_job_id) in prefilter else []
        ambiguous = len(vacancy_ids) > 1
        document = {
            "_id": source_identity_id(source, source_job_id),
            "schema_version": 1,
            "source": source,
            "source_job_id": source_job_id,
            "vacancy_ids": vacancy_ids,
            "prefilter_ids": prefilter_ids,
            "ambiguous": ambiguous,
        }
        source_identity_docs.append(document)
        if ambiguous:
            issues.append(
                {
                    "code": "ambiguous_source_identity",
                    "severity": "conflict",
                    "source": source,
                    "source_job_id": source_job_id,
                    "vacancy_ids": vacancy_ids,
                }
            )

    applications: list[dict[str, Any]] = []
    events: list[dict[str, Any]] = []
    for vacancy in vacancies:
        confirmation = confirmations.get(str(vacancy["_id"]))
        if confirmation:
            vacancy["submission_confirmation"] = confirmation
        projected_apps, projected_events, projected_issues = project_vacancy_history(vacancy, manual_events)
        for application in projected_apps:
            application["package_locator"] = package_locators.get(str(vacancy["_id"]))
        applications.extend(projected_apps)
        events.extend(projected_events)
        issues.extend(projected_issues)
    applications = _unique_documents(applications, "application")
    events = _unique_documents(events, "status event")
    feedback_docs = _feedback_documents(root, vacancies, issues)
    artifact_manifests = _unique_documents(artifact_manifests, "artifact manifest")

    collections = {
        "vacancies": sorted(vacancies, key=lambda item: item["_id"]),
        "prefilter_rejections": sorted(prefilter_docs, key=lambda item: item["_id"]),
        "source_identities": sorted(source_identity_docs, key=lambda item: item["_id"]),
        "status_events": sorted(events, key=lambda item: item["_id"]),
        "applications": sorted(applications, key=lambda item: item["_id"]),
        "feedback": sorted(feedback_docs, key=lambda item: item["_id"]),
        "artifact_manifests": sorted(artifact_manifests, key=lambda item: item["_id"]),
        "operational_logs": sorted(logs, key=lambda item: item["_id"]),
    }
    counts = {name: len(documents) for name, documents in collections.items()}
    byte_estimates = {
        name: sum(len(_canonical_json(document)) for document in documents)
        for name, documents in collections.items()
    }
    plan_digest = hashlib.sha256(
        _canonical_json({name: documents for name, documents in sorted(collections.items())})
    ).hexdigest()
    plan_id = stable_id("jobintel:migration-plan:v1", git_revision, plan_digest)
    manifest = {
        "schema_version": MIGRATION_SCHEMA_VERSION,
        "plan_id": plan_id,
        "git_revision": git_revision,
        "plan_sha256": plan_digest,
        "direct_metadata": len(direct),
        "archive_metadata": len(archived),
        "archive_stats": archive_stats,
        "counts": counts,
        "json_byte_estimates": byte_estimates,
        "issue_counts": dict(Counter(str(issue.get("code")) for issue in issues)),
        "blocked": any(issue.get("severity") == "blocked" for issue in issues),
        "issues": sorted(issues, key=_issue_order),
    }
    return {"schema_version": MIGRATION_SCHEMA_VERSION, "manifest": manifest, "collections": collections}


def _observation_order(item: Observation) -> tuple[str, int, str]:
    timestamp = str(item.meta.get("updated_at") or item.meta.get("rejected_at") or item.meta.get("discovered_at") or "")
    return timestamp, 1 if not item.archived else 0, item.meta_evidence.locator


def _issue_order(item: Mapping[str, Any]) -> tuple[str, str, str]:
    return str(item.get("code")), str(item.get("vacancy_id") or item.get("source") or ""), _canonical_json(item).decode("utf-8")


def _unique_documents(documents: Sequence[dict[str, Any]], label: str) -> list[dict[str, Any]]:
    by_id: dict[str, dict[str, Any]] = {}
    for document in documents:
        key = str(document["_id"])
        previous = by_id.get(key)
        if previous is not None and _canonical_json(previous) != _canonical_json(document):
            raise ValueError(f"conflicting {label} ID: {key}")
        by_id[key] = document
    return list(by_id.values())


def _operational_logs(
    root: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    logs: list[dict[str, Any]] = []
    manual_events: list[dict[str, Any]] = []
    confirmations: list[dict[str, Any]] = []
    for filename in OPERATIONAL_LOGS:
        path = root / "registry" / filename
        if not path.is_file():
            continue
        raw = path.read_bytes()
        payload = _load_yaml(raw, path.as_posix())
        logs.append(
            {
                "_id": filename,
                "schema_version": 1,
                "payload": payload,
                "legacy_evidence": _evidence(path.relative_to(root).as_posix(), raw).as_dict(),
            }
        )
        if filename == "manual-status-log.yaml":
            events = payload.get("events")
            if isinstance(events, list):
                manual_events = [dict(event) for event in events if isinstance(event, Mapping)]
        elif filename == "application-confirmations.yaml":
            events = payload.get("events")
            if isinstance(events, list):
                confirmations = [dict(event) for event in events if isinstance(event, Mapping)]
    return logs, manual_events, confirmations


def _normalize_submission_confirmations(
    events: Sequence[Mapping[str, Any]],
) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]]]:
    confirmations: dict[str, dict[str, Any]] = {}
    issues: list[dict[str, Any]] = []
    for raw in events:
        vacancy_id = str(raw.get("vacancy_id") or "")
        recorded_at = str(raw.get("recorded_at") or "")
        if not vacancy_id or not recorded_at:
            issues.append(
                {
                    "code": "invalid_submission_confirmation",
                    "severity": "blocked",
                    "vacancy_id": vacancy_id or None,
                    "message": "confirmation requires vacancy_id and recorded_at",
                }
            )
            continue
        confirmation = dict(raw)
        confirmation["vacancy_id"] = vacancy_id
        confirmation["recorded_at"] = recorded_at
        confirmation["confirmation_id"] = submission_confirmation_id(vacancy_id, recorded_at)
        if vacancy_id in confirmations:
            issues.append(
                {
                    "code": "duplicate_submission_confirmation",
                    "severity": "blocked",
                    "vacancy_id": vacancy_id,
                }
            )
            continue
        confirmations[vacancy_id] = confirmation
    return confirmations, issues


def _confirmed_application_vacancy_ids(
    manual_events: Sequence[Mapping[str, Any]],
) -> set[str]:
    confirmed: set[str] = set()
    for event in manual_events:
        if str(event.get("to_status") or "") != "applied":
            continue
        evidence = " ".join(str(event.get(field) or "") for field in ("reason", "note"))
        vacancy_id = str(event.get("vacancy_id") or "")
        if vacancy_id and not _NOT_SUBMITTED.search(evidence):
            confirmed.add(vacancy_id)
    return confirmed


def _feedback_documents(
    root: Path,
    vacancies: Sequence[Mapping[str, Any]],
    issues: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    vacancy_by_directory = {str(item.get("directory")): str(item.get("_id")) for item in vacancies}
    documents: list[dict[str, Any]] = []
    for path in sorted((root / "registry" / "feedback").glob("*/*.md")):
        relative = path.relative_to(root).as_posix()
        directory = path.parent.name
        vacancy_id = vacancy_by_directory.get(directory)
        raw = path.read_bytes()
        if vacancy_id is None:
            issues.append(
                {
                    "code": "feedback_without_vacancy",
                    "severity": "blocked",
                    "locator": relative,
                }
            )
            continue
        key = stable_id("jobintel:feedback:v1", vacancy_id, relative)
        documents.append(
            {
                "_id": key,
                "schema_version": 1,
                "feedback_id": key,
                "vacancy_id": vacancy_id,
                "directory": directory,
                "path": relative,
                "content": raw.decode("utf-8"),
                "sha256": hashlib.sha256(raw).hexdigest(),
                "size": len(raw),
            }
        )
    return documents


def _git_revision(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.strip()


def import_plan(
    store: DocumentStore,
    plan: Mapping[str, Any],
    *,
    dry_run: bool = True,
    batch_size: int = 250,
) -> dict[str, Any]:
    """Import a plan idempotently, retaining progress between batches."""
    if batch_size < 1:
        raise ValueError("batch_size must be positive")
    manifest = plan.get("manifest")
    collections = plan.get("collections")
    if not isinstance(manifest, Mapping) or not isinstance(collections, Mapping):
        raise ValueError("invalid migration plan")
    if manifest.get("blocked"):
        raise ValueError("migration plan contains blocked integrity issues")
    counts = {str(name): len(docs) for name, docs in collections.items() if isinstance(docs, list)}
    result: dict[str, Any] = {
        "plan_id": manifest.get("plan_id"),
        "dry_run": dry_run,
        "planned": counts,
        "inserted": Counter(),
        "unchanged": Counter(),
        "conflicts": [],
    }
    if dry_run:
        result["inserted"] = {}
        result["unchanged"] = {}
        return result

    owner = f"migration:{manifest['plan_id']}"
    lease = store.lease(owner)
    with lease:
        for collection in sorted(collections):
            documents = collections[collection]
            if not isinstance(documents, list):
                raise ValueError(f"migration collection must be a list: {collection}")
            existing = {str(item["_id"]): item for item in store.list(collection)}
            for offset in range(0, len(documents), batch_size):
                batch = documents[offset : offset + batch_size]
                missing: list[dict[str, Any]] = []
                for raw in batch:
                    document = dict(raw)
                    key = str(document["_id"])
                    previous = existing.get(key)
                    if previous is None:
                        missing.append(document)
                        continue
                    expected = dict(document)
                    expected.pop("_id")
                    previous_payload = _storage_payload(previous)
                    if _canonical_json(previous_payload) == _canonical_json(expected):
                        result["unchanged"][collection] += 1
                    else:
                        result["conflicts"].append({"collection": collection, "_id": key})
                if missing:
                    bulk_insert = getattr(store, "insert_batch", None)
                    if callable(bulk_insert):
                        inserted = int(bulk_insert(collection, missing))
                        if inserted != len(missing):
                            raise ValueError(
                                f"bulk insert count mismatch for {collection}: {inserted} != {len(missing)}"
                            )
                    else:
                        with store.transaction():
                            for document in missing:
                                payload = dict(document)
                                key = str(payload.pop("_id"))
                                store.put(collection, key, payload, expected_revision=0)
                    result["inserted"][collection] += len(missing)
                _record_progress(store, manifest, collection, min(offset + batch_size, len(documents)), len(documents))
    result["inserted"] = dict(result["inserted"])
    result["unchanged"] = dict(result["unchanged"])
    if result["conflicts"]:
        raise ValueError(f"migration conflicts with {len(result['conflicts'])} existing documents")
    return result


def _record_progress(
    store: DocumentStore,
    manifest: Mapping[str, Any],
    collection: str,
    completed: int,
    total: int,
) -> None:
    key = str(manifest["plan_id"])
    previous = store.get("migration_runs", key)
    payload = {
        "schema_version": 1,
        "plan_sha256": manifest.get("plan_sha256"),
        "git_revision": manifest.get("git_revision"),
        "collection": collection,
        "completed": completed,
        "total": total,
        "status": "complete" if completed == total else "running",
    }
    store.put(
        "migration_runs",
        key,
        payload,
        expected_revision=int(previous.get("revision", 0)) if previous else 0,
    )


def reconcile(store: DocumentStore, plan: Mapping[str, Any]) -> dict[str, Any]:
    """Compare all planned IDs and values with a target store."""
    collections = plan.get("collections")
    if not isinstance(collections, Mapping):
        raise ValueError("invalid migration plan")
    report: dict[str, Any] = {"collections": {}, "ok": True}
    for collection, documents in sorted(collections.items()):
        actual_by_id = {str(item["_id"]): item for item in store.list(collection)}
        expected_ids = {str(item["_id"]) for item in documents}
        missing: list[str] = []
        mismatched: list[str] = []
        for raw in documents:
            expected = dict(raw)
            key = str(expected.pop("_id"))
            actual = actual_by_id.get(key)
            if actual is None:
                missing.append(key)
                continue
            actual_payload = _storage_payload(actual)
            if _canonical_json(actual_payload) != _canonical_json(expected):
                mismatched.append(key)
        unexpected = sorted(set(actual_by_id) - expected_ids)
        report["collections"][collection] = {
            "expected": len(documents),
            "missing": missing,
            "mismatched": mismatched,
            "unexpected": unexpected,
        }
        if missing or mismatched or unexpected:
            report["ok"] = False
    return report


def _complete_package_locator(application: Mapping[str, Any], root: Path) -> str | None:
    """Return a package link only when all four generated documents exist."""
    directory = str(application.get("directory") or "")
    if not directory or Path(directory).name != directory or "/" in directory or "\\" in directory:
        return None
    package = root / "registry" / "jobs" / directory / "application"
    if all((package / filename).is_file() for filename in _COMPLETE_PACKAGE_FILES):
        manifest = yaml.safe_load((package / "manifest.yaml").read_text(encoding="utf-8"))
        current_documents = {"cv", "cover-letter", "analysis", "interview-preparation"}
        if isinstance(manifest, Mapping) and (
            current_documents.issubset(manifest.get("documents") or {})
            or (_COMPLETE_PACKAGE_FILES - {"manifest.yaml"}).issubset(manifest.get("files") or [])
        ):
            return str(application.get("package_locator") or (
                f"{REPOSITORY_URL}/tree/main/registry/jobs/{quote(directory)}/application"
            ))
    locator = str(application.get("package_locator") or "")
    url = urlsplit(locator)
    if url.netloc != "github.com" or "/archives/" not in url.path:
        return None
    archive_name = unquote(url.path.split("/archives/", 1)[1])
    archive_rel = Path(archive_name)
    if archive_rel.is_absolute() or ".." in archive_rel.parts or archive_rel.suffix != ".zip":
        return None
    archive = root / "archives" / archive_rel
    if not archive.is_file():
        return None
    with zipfile.ZipFile(archive) as bundle:
        names = {
            PurePosixPath(name).name
            for name in bundle.namelist()
            if f"/{directory}/application/" in f"/{name}"
        }
    return locator if _COMPLETE_PACKAGE_FILES.issubset(names) else None


def export_applications(
    source: Mapping[str, Any] | DocumentStore, *, package_root: Path | None = None
) -> dict[str, Any]:
    """Return the stable Sheets input and explicit coverage exceptions."""
    if isinstance(source, Mapping):
        documents = source.get("collections", {}).get("applications", [])
        events = source.get("collections", {}).get("status_events", [])
    else:
        documents = source.list("applications")
        events = source.list("status_events")
    confirmed: list[dict[str, Any]] = []
    needs_review: list[dict[str, Any]] = []
    without_package: list[dict[str, str]] = []
    for raw in documents:
        item = dict(raw)
        confirmation = item.get("confirmation")
        state = confirmation.get("state") if isinstance(confirmation, Mapping) else None
        if state != "confirmed":
            needs_review.append(_storage_payload(item))
            continue
        package_locator = _complete_package_locator(item, package_root) if package_root is not None else item.get("package_locator")
        if package_root is not None and package_locator is None:
            without_package.append({
                "application_id": str(item.get("application_id") or item.get("_id") or ""),
                "vacancy_id": str(item.get("vacancy_id") or ""),
                "directory": str(item.get("directory") or ""),
            })
            continue
        salary = item.get("salary") if isinstance(item.get("salary"), Mapping) else {}
        confirmed.append(
            {
                "application_id": item.get("application_id") or item.get("_id"),
                "vacancy_id": item.get("vacancy_id"),
                "directory": item.get("directory"),
                "company": item.get("company"),
                "title": item.get("title"),
                "effective_at": item.get("applied_at_effective"),
                "recorded_at": item.get("applied_at_recorded"),
                "status": item.get("current_status"),
                "status_effective_at": item.get("status_changed_at"),
                "status_recorded_at": item.get("status_recorded_at"),
                "vacancy_url": item.get("source_url"),
                "package_url": package_locator,
                "application_channel": item.get("channel"),
                "location": item.get("location"),
                "work_format": item.get("remote"),
                "salary_from": salary.get("min"),
                "salary_to": salary.get("max"),
                "salary_currency": salary.get("currency"),
                "salary_period": salary.get("period"),
                "salary_tax_basis": salary.get("gross_net"),
                "completion_reason": _completion_reason(item, events),
                "source_revision": int(item.get("revision") or item.get("source_revision") or 1),
            }
        )
    confirmed.sort(key=lambda item: str(item["application_id"]))
    needs_review.sort(key=lambda item: str(item.get("application_id") or item.get("_id")))
    without_package.sort(key=lambda item: item["application_id"])
    confirmed_ids = {str(item["application_id"]) for item in confirmed}
    exported_events = [
        {
            "event_id": item.get("event_id") or item.get("_id"),
            "application_id": item.get("application_id"),
            "vacancy_id": item.get("vacancy_id"),
            "status": item.get("status"),
            "effective_at": item.get("effective_at"),
            "recorded_at": item.get("recorded_at"),
            "reason": item.get("reason"),
            "note": item.get("note"),
        }
        for item in sorted(events, key=lambda value: str(value.get("event_id") or value.get("_id")))
        if str(item.get("application_id") or "") in confirmed_ids
    ]
    return {
        "schema_version": 1,
        "source_revision": max(
            (int(item.get("revision") or item.get("source_revision") or 1) for item in documents),
            default=0,
        ),
        "applications": confirmed,
        "events": exported_events,
        "coverage": {
            "confirmed": len(confirmed),
            "needs_review": len(needs_review),
            "confirmed_without_package": len(without_package),
            "confirmed_without_package_records": without_package,
            "status_events_total": len(events),
            "status_events_exported": len(exported_events),
            "needs_review_records": needs_review,
        },
    }


def _storage_payload(document: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in document.items()
        if key not in {"_id", "revision", "writer_fence", "updated_at"}
    }


def _completion_reason(application: Mapping[str, Any], events: Sequence[Mapping[str, Any]]) -> str | None:
    vacancy_id = application.get("vacancy_id")
    current_status = application.get("current_status")
    if current_status not in {"rejected", "closed"}:
        return None
    candidates = [
        event
        for event in events
        if event.get("vacancy_id") == vacancy_id
        and event.get("application_id") == (application.get("application_id") or application.get("_id"))
        and event.get("status") == current_status
    ]
    if not candidates:
        return None
    latest = max(candidates, key=lambda event: str(event.get("recorded_at") or ""))
    return str(latest.get("reason") or latest.get("note") or "") or None
