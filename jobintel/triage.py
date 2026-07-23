from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


TRIAGE_VERSION = "deterministic-triage-v1"
_HIGH_CONFIDENCE_RULES: tuple[tuple[str, str], ...] = (
    ("sales", r"\b(sales|account executive|business development|pre[- ]sales|sales engineer)\b"),
    ("qa", r"\b(qa|quality assurance|test automation|manual tester|software tester)\b"),
    ("mobile", r"\b(ios|android|mobile developer|react native|flutter)\b"),
    ("junior", r"\b(junior|jr\.?|intern|internship|graduate|entry[- ]level|trainee)\b"),
    ("consulting", r"\b(consultant|consulting)\b"),
    ("non_backend", r"\b(frontend|front[- ]end|ux|ui designer|data scientist|machine learning engineer)\b"),
)


def triage_directory(directory: Path) -> dict[str, Any]:
    meta = _read_mapping(directory / "meta.yaml")
    job_text = (directory / "job.md").read_text(encoding="utf-8") if (directory / "job.md").is_file() else ""
    title = str(meta.get("title", ""))
    haystack = f"{title}\n{job_text[:12000]}".casefold()
    matched = [(reason, pattern) for reason, pattern in _HIGH_CONFIDENCE_RULES if re.search(pattern, haystack)]
    # Only title matches are high-confidence; body-only matches can be incidental.
    title_matches = [reason for reason, pattern in _HIGH_CONFIDENCE_RULES if re.search(pattern, title.casefold())]
    skip_model = bool(title_matches)
    reason = title_matches[0] if title_matches else (matched[0][0] if matched else None)
    confidence = "high" if title_matches else ("medium" if matched else "low")
    return {
        "schema_version": 1,
        "triage_version": TRIAGE_VERSION,
        "vacancy_id": str(meta.get("id", "")),
        "skip_model": skip_model,
        "reason": reason,
        "confidence": confidence,
        "matched_title_rules": title_matches,
        "triaged_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
    }


def write_triage(directory: Path) -> dict[str, Any]:
    result = triage_directory(directory)
    path = directory / "triage.yaml"
    if path.is_file():
        try:
            existing = yaml.safe_load(path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            existing = None
        if isinstance(existing, dict) and all(
            existing.get(key) == result.get(key)
            for key in result
            if key != "triaged_at"
        ):
            result["triaged_at"] = existing.get("triaged_at", result["triaged_at"])
    content = yaml.safe_dump(result, allow_unicode=True, sort_keys=False)
    if not path.is_file() or path.read_text(encoding="utf-8") != content:
        path.write_text(content, encoding="utf-8", newline="\n")
    return result


def should_skip_model(directory: Path) -> bool:
    path = directory / "triage.yaml"
    if not path.is_file():
        return False
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError):
        return False
    return isinstance(loaded, dict) and loaded.get("skip_model") is True and loaded.get("confidence") == "high"


def _read_mapping(path: Path) -> dict[str, Any]:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(loaded, dict):
        raise ValueError(f"expected YAML mapping: {path}")
    return loaded
