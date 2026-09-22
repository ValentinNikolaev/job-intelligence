"""Check source provenance and claim mechanics; Codex reviews meaning separately."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any


class EvidenceError(ValueError):
    pass


STATUSES = frozenset({"verified", "unverified", "cannot-confirm", "retracted"})


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{label} must be non-empty text")
    return value.strip()


def _source_path(root: Path, source: Mapping[str, Any]) -> Path:
    relative = _text(source.get("path"), "source.path").replace("\\", "/")
    path = (root / relative).resolve()
    if not relative.startswith("registry/candidate/") or len(relative.split("/")) != 3 or path.parent != (root / "registry" / "candidate").resolve() or path.suffix.lower() != ".md":
        raise EvidenceError("evidence sources must be direct registry/candidate/*.md files")
    return path


def _source(root: Path, source: Mapping[str, Any]) -> str:
    path = _source_path(root, source)
    try:
        raw = path.read_bytes()
        content = raw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    except (OSError, UnicodeError) as exc:
        raise EvidenceError(f"cannot read candidate source {path}: {exc}") from exc
    quote = _text(source.get("quote"), "source.quote")
    if quote not in content:
        raise EvidenceError(f"source quote is absent from {path.name}")
    context = source.get("context_quote")
    if context is not None and _text(context, "source.context_quote") not in content:
        raise EvidenceError(f"source context quote is absent from {path.name}")
    if source.get("sha256") != hashlib.sha256(content.encode("utf-8")).hexdigest():
        raise EvidenceError(f"stale source hash for {path.name}")
    return quote


def bootstrap_evidence_bank(project_root: Path, extracts: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """Seal caller-selected verbatim extracts as unverified, without inventing claims."""
    entries = []
    for extract in extracts:
        if not isinstance(extract, Mapping) or not isinstance(extract.get("source"), Mapping):
            raise EvidenceError("each extract requires a source mapping")
        source = dict(extract["source"])
        path = _source_path(project_root, source)
        try:
            source["sha256"] = hashlib.sha256(path.read_text(encoding="utf-8-sig").encode("utf-8")).hexdigest()
        except OSError as exc:
            raise EvidenceError(f"cannot read candidate source {path}: {exc}") from exc
        entries.append({**extract, "status": "unverified", "source": source})
    bank = {"schema_version": 1, "entries": entries}
    validate_evidence_bank(bank, project_root)
    return bank


def validate_evidence_bank(bank: Mapping[str, Any], project_root: Path) -> dict[str, Any]:
    if bank.get("schema_version") != 1 or not isinstance(bank.get("entries"), list):
        raise EvidenceError("evidence bank requires schema_version 1 and entries list")
    identifiers: set[str] = set()
    blocked_quotes: set[tuple[str, str]] = set()
    verified_quotes: set[tuple[str, str]] = set()
    counts = dict.fromkeys(sorted(STATUSES), 0)
    for entry in bank["entries"]:
        if not isinstance(entry, Mapping):
            raise EvidenceError("evidence entry must be a mapping")
        identifier = _text(entry.get("id"), "evidence.id")
        if identifier in identifiers:
            raise EvidenceError(f"duplicate evidence id: {identifier}")
        identifiers.add(identifier)
        status = entry.get("status")
        if not isinstance(status, str) or status not in STATUSES:
            raise EvidenceError(f"invalid evidence status: {status}")
        counts[status] += 1
        source = entry.get("source")
        if not isinstance(source, Mapping):
            raise EvidenceError(f"{identifier} requires source provenance")
        quote = _source(project_root, source)
        quote_key = (str(_source_path(project_root, source)).casefold(), quote)
        if status in {"cannot-confirm", "retracted"}:
            blocked_quotes.add(quote_key)
        elif status == "verified":
            verified_quotes.add(quote_key)
        for key in ("employer", "role", "period"):
            value = entry.get(key)
            attribution_quote = quote + "\n" + str(source.get("context_quote", ""))
            if value and _text(value, key).casefold() not in attribution_quote.casefold():
                raise EvidenceError(f"{identifier} {key} is absent from its source quote")
        technologies = entry.get("technologies", [])
        if not isinstance(technologies, list):
            raise EvidenceError(f"{identifier} technologies must be a list")
        for technology in technologies:
            if _text(technology, "technology").casefold() not in quote.casefold():
                raise EvidenceError(f"{identifier} technology is absent from its source quote")
        if status in {"cannot-confirm", "retracted"}:
            _text(entry.get("reason"), f"{identifier} reason")
        if status == "verified":
            verification = entry.get("verification")
            if not isinstance(verification, Mapping):
                raise EvidenceError(f"{identifier} verified evidence needs verification provenance")
            for key in ("reviewer", "reviewed_at", "method"):
                _text(verification.get(key), f"verification.{key}")
    if blocked_quotes & verified_quotes:
        raise EvidenceError("the same source quote cannot be both verified and cannot-confirm/retracted")
    return {"schema_version": 1, "sha256": _digest(bank), "entry_count": len(identifiers), "statuses": counts}


def validate_claims_ledger(
    ledger: Mapping[str, Any], bank: Mapping[str, Any], package: Mapping[str, str], project_root: Path,
) -> dict[str, Any]:
    """Check anchors, metrics and declared role attribution, not semantic equivalence."""
    receipt = validate_evidence_bank(bank, project_root)
    if ledger.get("schema_version") != 1 or not isinstance(ledger.get("claims"), list):
        raise EvidenceError("claims ledger requires schema_version 1 and claims list")
    entries = {entry["id"]: entry for entry in bank["entries"]}
    fields = {"cv": "cv_markdown", "cover-letter": "cover_letter_markdown",
              "analysis": "analysis_markdown", "interview-preparation": "interview_preparation_markdown"}
    anchors: dict[str, list[str]] = {field: [] for field in package}
    evidence_by_anchor: dict[str, list[Mapping[str, Any]]] = {}
    used: set[str] = set()
    seen: set[tuple[str, str]] = set()
    for claim in ledger["claims"]:
        if not isinstance(claim, Mapping):
            raise EvidenceError("claim must be a mapping")
        name = _text(claim.get("document"), "claim.document")
        field = fields.get(name, name)
        text = _text(claim.get("text"), "claim.text")
        if field not in package or text not in package[field]:
            raise EvidenceError("claim must quote text present in its selected document")
        if (field, text) in seen:
            raise EvidenceError("duplicate claim anchor")
        seen.add((field, text))
        ids = claim.get("evidence_ids")
        if not isinstance(ids, list) or not ids or not all(isinstance(item, str) for item in ids):
            raise EvidenceError("claim requires evidence_ids")
        referenced = []
        for identifier in ids:
            entry = entries.get(identifier)
            if entry is None or entry["status"] != "verified":
                raise EvidenceError(f"claim references unavailable verified evidence: {identifier}")
            referenced.append(entry)
            used.add(identifier)
        for key in ("employer", "role"):
            attribution = claim.get(key)
            if attribution and not all(str(entry.get(key, "")).casefold() == _text(attribution, key).casefold() for entry in referenced):
                raise EvidenceError(f"claim {key} does not match all referenced evidence")
        technologies = claim.get("technologies", [])
        if not isinstance(technologies, list):
            raise EvidenceError("claim technologies must be a list")
        for technology in technologies:
            if not any(_text(technology, "technology").casefold() in [t.casefold() for t in e.get("technologies", [])] for e in referenced):
                raise EvidenceError(f"claim technology lacks attributed evidence: {technology}")
        numbers = set(re.findall(r"(?<!\w)\d+(?:[.,]\d+)*(?:%|[xX])?", text))
        source_numbers = set(re.findall(r"(?<!\w)\d+(?:[.,]\d+)*(?:%|[xX])?", "\n".join(e["source"]["quote"] for e in referenced)))
        if numbers - source_numbers:
            raise EvidenceError(f"claim contains unsupported numeric tokens: {sorted(numbers - source_numbers)}")
        anchors[field].append(text)
        if field == "cv_markdown":
            evidence_by_anchor[text] = referenced
    for field, content in package.items():
        if not anchors[field]:
            raise EvidenceError(f"claims ledger has no grounded claims for {field}")
        if field == "cv_markdown":
            section = re.split(r"(?m)^## Experience\s*$", content)
            if len(section) > 1:
                experience = re.split(r"(?m)^## ", section[1])[0]
                role_heading = ""
                for line in experience.splitlines():
                    if line.startswith("### "):
                        role_heading = line[4:].casefold()
                    match = re.match(r"^\s*[-*]\s+(.+)", line)
                    if match and not match[1].startswith("Technologies") and not any(match[1] in anchor for anchor in anchors[field]):
                        raise EvidenceError("every CV experience bullet must have a complete claim anchor")
                    if match and not match[1].startswith("Technologies"):
                        supporting = [entry for anchor in anchors[field] if match[1] in anchor for entry in evidence_by_anchor[anchor]]
                        for entry in supporting:
                            for key in ("employer", "role"):
                                if not entry.get(key) or entry[key].casefold() not in role_heading:
                                    raise EvidenceError(f"CV bullet evidence {key} must match its actual role heading")
    return {"schema_version": 1, "sha256": _digest(ledger), "evidence_bank": receipt,
            "claim_count": len(seen), "evidence_ids": sorted(used),
            "evidence_entries": [entries[identifier] for identifier in sorted(used)],
            "checks": ["source_quotes", "source_hashes", "verified_status", "numeric_tokens", "declared_attribution", "cv_bullet_coverage"],
            "semantic_review_required": True}
