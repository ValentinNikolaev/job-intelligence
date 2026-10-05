"""Fast aggregate diagnostics for Codex application drafts before publication."""
from __future__ import annotations

import hashlib
import re
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any

from .applications import (
    APPLICATION_DOCUMENTS, APPLICATION_FILES, _HANDOFF_REQUIREMENTS,
    _EXPERIENCE_DATE_RANGE_RE, _MONTH_NAMES,
    _markdown_section, _read_yaml_mapping, _required_handoffs, _selected_documents,
    _validate_cv_audit_bullet_coverage,
)
from .evidence import validate_evidence_bank


def _diagnostic(items: list[dict[str, str]], code: str, message: str, path: Path) -> None:
    items.append({"code": code, "message": message, "path": str(path)})


def _load(path: Path, label: str, items: list[dict[str, str]]) -> dict[str, Any] | None:
    try:
        return _read_yaml_mapping(path, label)
    except Exception as exc:
        _diagnostic(items, "YAML_INVALID", str(exc), path)
        return None


def _cv_lint(markdown: str, quality: Mapping[str, Any], path: Path, items: list[dict[str, str]], *, reference_date: date | None = None) -> None:
    section = _markdown_section(markdown, "Experience")
    roles: list[tuple[str, list[str]]] = []
    for line in section.splitlines():
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            roles.append((heading.group(1), []))
        elif roles:
            roles[-1][1].append(line)
    today = reference_date or date.today()
    cutoff = (today.year - 5, today.month)
    for title, lines in roles:
        bullets = [re.sub(r"^\s*[-*]\s+", "", line).strip() for line in lines
                   if re.match(r"^\s*[-*]\s+\S", line)
                   and not re.match(r"^\s*[-*]\s+(?:\*\*)?Technologies", line, re.I)]
        if any(re.match(r"^\s*[-*]\s+(?:\*\*)?Technologies", line, re.I) for line in lines) and not bullets:
            _diagnostic(items, "CV_TECHNOLOGIES_NOT_BULLETS", "Technologies lines cannot satisfy Experience bullet depth", path)
        normal = [re.sub(r"\W+", "", bullet).casefold() for bullet in bullets]
        if len(normal) != len(set(normal)):
            _diagnostic(items, "CV_DUPLICATE_BULLET", f"duplicate normalized Experience bullet in {title}", path)
        period = _EXPERIENCE_DATE_RANGE_RE.search("\n".join([title, *lines[:4]]))
        required = 2
        if period:
            end = period.group("end")
            if end.casefold() in {"present", "current"}:
                end_key = (today.year, today.month)
            else:
                parts = end.split()
                year = int(parts[-1])
                month = (
                    next(index for index, name in enumerate(_MONTH_NAMES, 1) if name.casefold() == parts[0].casefold())
                    if len(parts) > 1 else (today.month if year == today.year else 12)
                )
                end_key = (year, month)
            required = 3 if end_key >= cutoff else 2
        if len(bullets) < required:
            _diagnostic(items, "CV_ROLE_DEPTH", f"{title} has {len(bullets)} Experience bullets; requires {required}", path)
    audit = quality.get("cv_audit")
    if isinstance(audit, Mapping) and isinstance(audit.get("bullet_decisions"), list):
        try:
            _validate_cv_audit_bullet_coverage(markdown, audit["bullet_decisions"])
        except Exception as exc:
            _diagnostic(items, "CV_AUDIT_ANCHOR", str(exc), path)
    else:
        _diagnostic(items, "CV_AUDIT_ANCHOR", "cv_audit.bullet_decisions is required for a CV", path)


def lint_application_draft(
    vacancy_directory: Path,
    draft_directory: Path,
    *,
    document: str | None = None,
    vacancy_text: str | None = None,
) -> dict[str, Any]:
    """Return every predictable local defect without publishing or converting a package."""
    vacancy_directory, draft = vacancy_directory.resolve(), draft_directory.resolve()
    project_root = vacancy_directory.parents[2]
    diagnostics: list[dict[str, str]] = []
    quality_path = draft / "quality.yaml"
    quality = _load(quality_path, "application quality declaration", diagnostics)
    selected = set(_selected_documents(document))
    package: dict[str, str] = {}
    for name in selected:
        path = draft / APPLICATION_FILES[APPLICATION_DOCUMENTS[name]]
        try:
            package[APPLICATION_DOCUMENTS[name]] = path.read_text(encoding="utf-8-sig")
            if any(line.rstrip(" \t") != line for line in package[APPLICATION_DOCUMENTS[name]].splitlines()):
                _diagnostic(diagnostics, "TRAILING_WHITESPACE", f"{path.name} has trailing spaces or tabs", path)
        except OSError:
            _diagnostic(diagnostics, "DOCUMENT_MISSING", f"required draft document is missing: {path.name}", path)
    if quality is not None:
        for filename in _required_handoffs(selected):
            path = draft / "parts" / filename
            try:
                content = path.read_text(encoding="utf-8-sig")
            except OSError:
                _diagnostic(diagnostics, "HANDOFF_MISSING", f"required handoff is missing: {filename}", path)
                continue
            _, markers = _HANDOFF_REQUIREMENTS[filename]
            for marker in markers:
                if marker.casefold() not in content.casefold():
                    _diagnostic(diagnostics, "HANDOFF_MARKER", f"{filename} is missing marker: {marker}", path)
        if quality.get("schema_version") == 2:
            review = quality.get("final_review")
            hashes = review.get("document_sha256") if isinstance(review, Mapping) else None
            if not isinstance(hashes, Mapping):
                _diagnostic(diagnostics, "ARTIFACT_HASH_MISSING", "final_review.document_sha256 is required", quality_path)
            else:
                for name, field in APPLICATION_DOCUMENTS.items():
                    if field in package and hashes.get(name) != "sha256:" + hashlib.sha256((package[field].strip() + "\n").encode()).hexdigest():
                        _diagnostic(diagnostics, "ARTIFACT_HASH_STALE", f"final review hash is stale or missing for {name}", quality_path)
            if "cv_markdown" in package:
                _cv_lint(package["cv_markdown"], quality, draft / "cv.md", diagnostics)
            bank_path = quality.get("evidence_bank")
            ledger_path = quality.get("claims_ledger")
            bank: dict[str, Any] | None = None
            if isinstance(bank_path, str):
                bank = _load(project_root / bank_path, "candidate evidence bank", diagnostics)
                if bank is not None:
                    try:
                        validate_evidence_bank(bank, project_root)
                    except Exception as exc:
                        _diagnostic(diagnostics, "EVIDENCE_UNAVAILABLE", str(exc), project_root / bank_path)
            ledger = _load(draft / ledger_path, "application claims ledger", diagnostics) if isinstance(ledger_path, str) else None
            if isinstance(bank, Mapping) and isinstance(ledger, Mapping):
                entries = {str(entry.get("id")): entry for entry in bank.get("entries", []) if isinstance(entry, Mapping)}
                for claim in ledger.get("claims", []):
                    if not isinstance(claim, Mapping):
                        continue
                    for identifier in claim.get("evidence_ids", []) if isinstance(claim.get("evidence_ids"), list) else []:
                        entry = entries.get(str(identifier))
                        if not isinstance(entry, Mapping) or entry.get("status") != "verified":
                            _diagnostic(diagnostics, "EVIDENCE_UNAVAILABLE", f"claim references unverified, retracted, or cannot-confirm evidence: {identifier}", draft / ledger_path)
                        elif any(claim.get(key) and str(claim[key]).casefold() != str(entry.get(key, "")).casefold() for key in ("employer", "role")):
                            _diagnostic(diagnostics, "CLAIM_ROLE_INCOMPATIBLE", f"claim employer/role is incompatible with evidence {identifier}", draft / ledger_path)
                for row in quality.get("requirements", []) if isinstance(quality.get("requirements"), list) else []:
                    if not isinstance(row, Mapping):
                        continue
                    ids = row.get("evidence_ids", []) if isinstance(row.get("evidence_ids"), list) else []
                    quote = row.get("candidate_quote")
                    if quote and not any(quote in str(entries.get(str(identifier), {}).get("source", {}).get("quote", "")) for identifier in ids):
                        _diagnostic(diagnostics, "CANDIDATE_QUOTE_NOT_EXACT", "candidate_quote is not an exact referenced evidence substring", quality_path)
                    jd_quote = row.get("jd_quote")
                    if jd_quote:
                        if vacancy_text is None:
                            try:
                                job_text = (vacancy_directory / "job.md").read_text(encoding="utf-8-sig")
                            except OSError:
                                job_text = ""
                        else:
                            job_text = vacancy_text
                        if jd_quote not in job_text:
                            _diagnostic(diagnostics, "JOB_QUOTE_NOT_EXACT", "jd_quote is not an exact selected-vacancy substring", quality_path)
    diagnostics.sort(key=lambda item: (item["code"], item["path"], item["message"]))
    return {"ok": not diagnostics, "draft": str(draft), "diagnostics": diagnostics}
