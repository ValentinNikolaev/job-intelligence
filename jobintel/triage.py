from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Mapping
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from . import storage_bridge as op
from .selection_policy import DEFAULT_SELECTION_POLICY_PATH, SelectionPolicy, load_selection_policy


TRIAGE_VERSION = "deterministic-triage-v2"
BODY_WINDOW = 12000
_HIGH_CONFIDENCE_RULES: tuple[tuple[str, str], ...] = (
    ("sales", r"\b(sales|account executive|business development|pre[- ]sales|sales engineer)\b"),
    ("qa", r"\b(qa|quality assurance|test automation|manual tester|software tester)\b"),
    ("mobile", r"\b(ios|android|mobile developer|react native|flutter)\b"),
    ("junior", r"\b(junior|jr\.?|intern|internship|graduate|entry[- ]level|trainee)\b"),
    ("sre", r"\b(site reliability engineer|sre)\b"),
    ("consulting", r"\b(consultant|consulting)\b"),
    ("non_backend", r"\b(frontend|front[- ]end|ux|ui designer|data scientist|machine learning engineer)\b"),
)


def evaluate_triage(meta: Mapping[str, Any], job_text: str, *, policy: SelectionPolicy) -> dict[str, Any]:
    """Pure decision and input binding shared by file and operational snapshots."""
    title = str(meta.get("title", ""))
    body = job_text[:BODY_WINDOW].casefold()
    haystack = f"{title.casefold()}\n{body}"
    patterns = dict(_HIGH_CONFIDENCE_RULES)
    selected = [(reason, patterns[reason]) for reason in policy.triage_exclusions]
    matched = [(reason, pattern) for reason, pattern in selected if re.search(pattern, haystack)]
    # Only title matches are high-confidence; body-only matches can be incidental.
    title_matches = [reason for reason, pattern in selected if re.search(pattern, title.casefold())]
    skip_model = bool(title_matches)
    reason = title_matches[0] if title_matches else (matched[0][0] if matched else None)
    confidence = "high" if title_matches else ("medium" if matched else "low")
    return {
        "schema_version": 1,
        "triage_version": _triage_version(title.casefold(), body, policy),
        "vacancy_id": str(meta.get("id", "")),
        "skip_model": skip_model,
        "reason": reason,
        "confidence": confidence,
        "matched_title_rules": title_matches,
    }


def _triage_version(title: str, body: str, policy: SelectionPolicy) -> str:
    inputs = {"policy": policy.triage_fingerprint(), "title": title, "body": body,
              "recognition": {"algorithm": "title-first-v1", "patterns": _HIGH_CONFIDENCE_RULES, "body_window": BODY_WINDOW}}
    canonical = json.dumps(inputs, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return f"{TRIAGE_VERSION}:sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def triage_directory(directory: Path, *, policy: SelectionPolicy | None = None) -> dict[str, Any]:
    policy = policy if policy is not None else load_selection_policy(DEFAULT_SELECTION_POLICY_PATH)
    meta = _read_mapping(directory / "meta.yaml")
    job_text = op.read_text(directory / "job.md") if op.exists(directory / "job.md") else ""
    result = evaluate_triage(meta, job_text, policy=policy)
    result["triaged_at"] = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    return result


def write_triage(directory: Path, *, policy: SelectionPolicy | None = None) -> dict[str, Any]:
    result = triage_directory(directory, policy=policy)
    path = directory / "triage.yaml"
    if op.exists(path):
        try:
            existing = yaml.safe_load(op.read_text(path))
        except (OSError, yaml.YAMLError):
            existing = None
        if isinstance(existing, dict) and all(
            existing.get(key) == result.get(key)
            for key in result
            if key != "triaged_at"
        ):
            result["triaged_at"] = existing.get("triaged_at", result["triaged_at"])
    content = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    if op.write_operational(path, content) is not None:
        return result
    if not op.exists(path) or op.read_text(path) != content:
        path.write_text(content, encoding="utf-8", newline="\n")
    return result


def snapshot_should_skip(document: Mapping[str, Any], *, policy: SelectionPolicy | None = None) -> bool:
    """Recompute existing receipts against current inputs; never rewrite their history."""
    policy = policy if policy is not None else load_selection_policy(DEFAULT_SELECTION_POLICY_PATH)
    receipt = document.get("triage")
    meta = document.get("meta")
    body = document.get("job_text", "")
    if not isinstance(receipt, dict) or not isinstance(meta, dict) or not isinstance(body, str):
        return False
    if (type(receipt.get("schema_version")) is not int or receipt["schema_version"] != 1
            or type(receipt.get("skip_model")) is not bool
            or not isinstance(receipt.get("confidence"), str)
            or receipt.get("confidence") not in {"high", "medium", "low"}
            or not isinstance(receipt.get("triage_version"), str)
            or not receipt["triage_version"]
            or str(receipt.get("vacancy_id", "")) != str(meta.get("id", ""))):
        return False
    decision = evaluate_triage(meta, body, policy=policy)
    return decision["skip_model"] is True and decision["confidence"] == "high"


def should_skip_model(directory: Path, *, policy: SelectionPolicy | None = None) -> bool:
    policy = policy if policy is not None else load_selection_policy(DEFAULT_SELECTION_POLICY_PATH)
    path = directory / "triage.yaml"
    if not op.exists(path):
        return False
    try:
        loaded = yaml.safe_load(op.read_text(path))
        meta = _read_mapping(directory / "meta.yaml")
        job_text = op.read_text(directory / "job.md") if op.exists(directory / "job.md") else ""
    except (OSError, ValueError, yaml.YAMLError):
        return False
    return snapshot_should_skip({"meta": meta, "job_text": job_text, "triage": loaded}, policy=policy)


def _read_mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(op.read_text(path))
    if not isinstance(loaded, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return loaded
