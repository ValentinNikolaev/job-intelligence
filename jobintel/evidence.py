"""Check source provenance and claim mechanics; Codex reviews meaning separately."""
from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from .preparation_context import PreparationContext, PreparationContextError, load_preparation_context, resolve_preparation_context


class EvidenceError(ValueError):
    pass


STATUSES = frozenset({"verified", "unverified", "cannot-confirm", "retracted"})
CONTEXT_FIELDS = ('problem', 'contribution', 'scope', 'decision', 'consequence', 'delivery_status', 'responsibility')
_NUMBER = re.compile(r'(?<!\w)\d+(?:[.,]\d+)*(?:%|[xX])?')


def _validate_context(entry: Mapping[str, Any], quote: str) -> None:
    context = entry.get('achievement_context', {})
    if not isinstance(context, Mapping) or set(context) - set(CONTEXT_FIELDS):
        raise EvidenceError('achievement_context has unknown fields or is not a mapping')
    for name, field in context.items():
        if not isinstance(field, Mapping) or field.get('status') not in {'supported', 'unknown'}:
            raise EvidenceError(f'achievement_context.{name} requires supported or unknown status')
        if field['status'] == 'supported':
            if _text(field.get('quote'), f'achievement_context.{name}.quote') not in quote:
                raise EvidenceError('achievement context must quote its primary evidence')
        elif field.get('quote'):
            raise EvidenceError('unknown achievement context cannot contain a supported quote')
    measurements = entry.get('measurements', [])
    if not isinstance(measurements, list):
        raise EvidenceError('measurements must be a list')
    seen = set()
    for measurement in measurements:
        if not isinstance(measurement, Mapping):
            raise EvidenceError('measurement must be a mapping')
        identifier = _text(measurement.get('id'), 'measurement.id')
        if identifier in seen:
            raise EvidenceError('duplicate measurement id')
        seen.add(identifier)
        excerpt = _text(measurement.get('quote'), 'measurement.quote')
        if excerpt not in quote:
            raise EvidenceError('measurement quote must occur in its primary evidence')
        for name in ('value', 'measure', 'unit', 'scope'):
            value = _text(measurement.get(name), f'measurement.{name}')
            if value.casefold() not in excerpt.casefold():
                raise EvidenceError(f'measurement {name} is absent from its source quote')
        if measurement['value'] not in _NUMBER.findall(excerpt):
            raise EvidenceError('measurement value must be an exact numeric token')
        for name in ('baseline', 'period', 'method'):
            if name not in measurement:
                raise EvidenceError(f'measurement.{name} must record source text or explicit null')
            if measurement[name] is not None and _text(measurement[name], f'measurement.{name}').casefold() not in excerpt.casefold():
                raise EvidenceError(f'measurement {name} is absent from its source quote')


def evidence_questions(bank: Mapping[str, Any], root: Path, identifiers: Sequence[str] = (), *, context: PreparationContext | None = None) -> dict[str, Any]:
    """List unanswered factual questions without ranking claims or updating sources."""
    validate_evidence_bank(bank, root, context=context)
    known = {entry['id'] for entry in bank['entries']}
    if set(identifiers) - known:
        raise EvidenceError('unknown selected evidence ids')
    prompts = dict(problem='What problem or constraint did this work address?',
        contribution='What was your personal contribution, if any, and what belonged to others?', scope='Which system, users or team were affected?',
        decision='Who chose the approach, what was your part, and which constraints are confirmed?',
        consequence='What change, if any, is confirmed after the work? Unknown or unmeasured results may stay unknown.',
        delivery_status='Was this proposed, implemented or deployed? What confirms that stage?',
        responsibility='Which decisions were yours, which did you influence, and which belonged to others?')
    questions = []
    for entry in bank['entries']:
        if identifiers and entry['id'] not in identifiers:
            continue
        context = entry.get('achievement_context', {})
        for field in CONTEXT_FIELDS:
            if context.get(field, {}).get('status') != 'supported':
                questions.append(dict(evidence_id=entry['id'], field=field, question=prompts[field],
                                      source_quote=entry['source']['quote'], status=entry['status']))
        for measurement in entry.get('measurements', []):
            for field in ('baseline', 'period', 'method'):
                if measurement[field] is None:
                    questions.append(dict(evidence_id=entry['id'], measurement_id=measurement['id'], field=field,
                        question=f'What is the {field} for this measurement, if it is known?', source_quote=measurement['quote']))
        if _NUMBER.search(entry['source']['quote']) and not entry.get('measurements'):
            questions.append(dict(evidence_id=entry['id'], field='measurement_context',
                question='Which numbers describe measured outcomes, dates or versions? What do they measure and how?',
                source_quote=entry['source']['quote']))
    return dict(schema_version=1, questions=questions, candidate_sources_changed=False)


def _validate_claim_context(claim: Mapping, referenced: list[Mapping], *, strict: bool) -> None:
    text = claim['text']
    bindings = claim.get('measurements', [])
    if not isinstance(bindings, list):
        raise EvidenceError('claim measurements must be a list')
    covered = set()
    for binding in bindings:
        if not isinstance(binding, Mapping):
            raise EvidenceError('claim measurement binding must be a mapping')
        entry = next((entry for entry in referenced if entry['id'] == binding.get('evidence_id')), None)
        measurement = next((item for item in entry.get('measurements', []) if item['id'] == binding.get('measurement_id')), None) if entry else None
        if measurement is None:
            raise EvidenceError('claim measurement references unavailable attributed context')
        excerpt = _text(binding.get('claim_quote'), 'claim measurement quote')
        if excerpt not in text:
            raise EvidenceError('claim measurement quote must occur in final claim')
        translation = binding.get('translation')
        if translation is not None:
            if not isinstance(translation, Mapping):
                raise EvidenceError('measurement translation must be a mapping')
            language = _text(translation.get('language'), 'measurement translation language')
            if language.casefold() == str(measurement.get('language', 'English')).casefold():
                raise EvidenceError('measurement translation cannot relabel a measure in the source language')
            _text(translation.get('reviewer'), 'measurement translation reviewer')
            _text(translation.get('reason'), 'measurement translation semantic review')
            if translation.get('source_quote') != measurement['quote']:
                raise EvidenceError('measurement translation must bind the exact original context')
        for name in ('value', 'measure', 'unit', 'scope'):
            label = _text(translation.get(name), f'measurement translated {name}') if translation is not None and name in {'measure', 'scope'} else measurement[name]
            if label.casefold() not in excerpt.casefold():
                raise EvidenceError(f'claim measurement changes the source {name}')
        covered.add(measurement['value'])
    if strict and set(_NUMBER.findall(text)) - covered:
        raise EvidenceError('every claim numeric token requires attributed measurement context')
    if strict and claim['document'] in {'cv', 'cv_markdown'}:
        support = claim.get('support')
        if not isinstance(support, Mapping):
            raise EvidenceError('CV claim requires source excerpts for contribution, scope and consequence')
        for name in ('contribution', 'scope', 'consequence'):
            field = support.get(name)
            entry = next((entry for entry in referenced if isinstance(field, Mapping) and entry['id'] == field.get('evidence_id')), None)
            if entry is None or _text(field.get('quote'), f'claim support.{name}') not in entry['source']['quote']:
                raise EvidenceError(f'CV claim support.{name} must quote referenced primary evidence')


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=False).encode()).hexdigest()


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise EvidenceError(f"{label} must be non-empty text")
    return value.strip()


def _source_path(root: Path, source: Mapping[str, Any], *, context: PreparationContext | None = None) -> Path:
    relative = _text(source.get("path"), "source.path").replace("\\", "/")
    try:
        context = context or load_preparation_context(root)
        if context.project_root != root.resolve():
            raise PreparationContextError("evidence context belongs to another project")
        return context.source_path(relative)
    except PreparationContextError as exc:
        raise EvidenceError(str(exc)) from exc


def _source(root: Path, source: Mapping[str, Any], *, context: PreparationContext | None = None) -> str:
    path = _source_path(root, source, context=context)
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


def bootstrap_evidence_bank(project_root: Path, extracts: Sequence[Mapping[str, Any]], *, context: PreparationContext | None = None) -> dict[str, Any]:
    """Seal caller-selected verbatim extracts as unverified, without inventing claims."""
    try:
        context = resolve_preparation_context(project_root, context)
    except PreparationContextError as exc:
        raise EvidenceError(str(exc)) from exc
    entries = []
    for extract in extracts:
        if not isinstance(extract, Mapping) or not isinstance(extract.get("source"), Mapping):
            raise EvidenceError("each extract requires a source mapping")
        source = dict(extract["source"])
        path = _source_path(project_root, source, context=context)
        try:
            source["sha256"] = hashlib.sha256(path.read_text(encoding="utf-8-sig").encode("utf-8")).hexdigest()
        except OSError as exc:
            raise EvidenceError(f"cannot read candidate source {path}: {exc}") from exc
        entries.append({**extract, "status": "unverified", "source": source})
    bank = {"schema_version": 1, "entries": entries}
    validate_evidence_bank(bank, project_root, context=context)
    return bank


def validate_evidence_bank(bank: Mapping[str, Any], project_root: Path, *, context: PreparationContext | None = None) -> dict[str, Any]:
    try:
        context = resolve_preparation_context(project_root, context)
        if context.project_root != project_root.resolve():
            raise PreparationContextError("evidence context belongs to another project")
    except PreparationContextError as exc:
        raise EvidenceError(str(exc)) from exc
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
        quote = _source(project_root, source, context=context)
        _validate_context(entry, quote)
        attribution_source = entry.get("attribution_source")
        if attribution_source is not None:
            if not isinstance(attribution_source, Mapping):
                raise EvidenceError(f"{identifier} attribution_source must be a source mapping")
            attribution_quote = _source(project_root, attribution_source, context=context)
        else:
            attribution_quote = ""
        quote_key = (str(_source_path(project_root, source, context=context)).casefold(), quote)
        if status in {"cannot-confirm", "retracted"}:
            blocked_quotes.add(quote_key)
        elif status == "verified":
            verified_quotes.add(quote_key)
        for key in ("employer", "role", "period"):
            value = entry.get(key)
            available_attribution = quote + "\n" + str(source.get("context_quote", "")) + "\n" + attribution_quote + "\n" + str(attribution_source.get("context_quote", "") if attribution_source else "")
            if value and _text(value, key).casefold() not in available_attribution.casefold():
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
    *, context: PreparationContext | None = None,
) -> dict[str, Any]:
    """Check anchors, metrics and declared role attribution, not semantic equivalence."""
    receipt = validate_evidence_bank(bank, project_root, context=context)
    if type(ledger.get("schema_version")) is not int or ledger['schema_version'] not in {1, 2} or not isinstance(ledger.get("claims"), list):
        raise EvidenceError("claims ledger requires schema_version 1 or 2 and claims list")
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
        _validate_claim_context(claim, referenced, strict=ledger['schema_version'] == 2)
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
    return {"schema_version": ledger['schema_version'], "sha256": _digest(ledger), "evidence_bank": receipt,
            "claim_count": len(seen), "evidence_ids": sorted(used),
            "evidence_entries": [entries[identifier] for identifier in sorted(used)],
            "checks": ["source_quotes", "source_hashes", "verified_status", "numeric_tokens", "declared_attribution", "cv_bullet_coverage"],
            "semantic_review_required": True}
