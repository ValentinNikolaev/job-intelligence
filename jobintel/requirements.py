"""Validate auditable requirement priorities without manufacturing hard blockers."""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

IMPORTANCE = ("critical", "high", "meaningful", "preferred", "low_signal")
BASES = ("stated", "structural", "inferred")
MATCHES = ("strong", "partial", "missing", "unknown", "not_applicable")
FIELDS = {"requirement", "importance", "basis", "jd_quote", "match", "candidate_quote", "risk", "mitigation", "hard_blocker"}


def validate_requirements(value: Any, *, vacancy_text: str | None = None,
                          candidate_text: str | None = None) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) > 100:
        raise ValueError("requirements must be a list of at most 100 rows")
    rows = []
    seen = set()
    for index, row in enumerate(value, 1):
        if not isinstance(row, Mapping) or set(row) - {"evidence_ids"} != FIELDS:
            raise ValueError(f"requirement {index} must contain exactly {', '.join(sorted(FIELDS))}")
        clean = dict(row)
        if "evidence_ids" in clean and (not isinstance(clean["evidence_ids"], list) or
                not all(isinstance(item, str) and item.strip() for item in clean["evidence_ids"])):
            raise ValueError("evidence_ids must be a list of nonempty identifiers")
        for field in FIELDS - {"hard_blocker"}:
            if not isinstance(clean[field], str):
                raise ValueError(f"requirement {index} {field} must be text")
            clean[field] = clean[field].strip()
        key = clean["requirement"].casefold()
        if not key or key in seen:
            raise ValueError("requirements must have unique nonempty descriptions")
        seen.add(key)
        if clean["importance"] not in IMPORTANCE or clean["basis"] not in BASES or clean["match"] not in MATCHES:
            raise ValueError(f"requirement {index} has invalid importance, basis, or match")
        if not isinstance(clean["hard_blocker"], bool):
            raise ValueError("hard_blocker must be a boolean")
        if clean["basis"] == "inferred":
            if clean["importance"] in {"critical", "high"} or clean["hard_blocker"]:
                raise ValueError("inferred requirements cannot be critical, high, or hard blockers")
            if clean["jd_quote"]:
                raise ValueError("inferred requirements must leave jd_quote empty")
        else:
            if not clean["jd_quote"]:
                raise ValueError("stated/structural requirements need a verbatim jd_quote")
            if vacancy_text is not None and clean["jd_quote"] not in vacancy_text:
                raise ValueError("requirement jd_quote is absent from the selected vacancy")
        if clean["match"] in {"strong", "partial"} and not clean["candidate_quote"]:
            raise ValueError("strong/partial requirement matches need candidate_quote")
        if clean["candidate_quote"] and candidate_text is not None and clean["candidate_quote"] not in candidate_text:
            raise ValueError("requirement candidate_quote is absent from candidate evidence")
        if clean["importance"] in {"critical", "high"} and clean["match"] in {"missing", "partial", "unknown"}:
            if not clean["risk"] or not clean["mitigation"]:
                raise ValueError("material gaps need a specific risk and mitigation")
        if clean["hard_blocker"] and (clean["basis"] != "stated" or clean["match"] != "missing"):
            raise ValueError("hard blockers require a stated requirement and established missing capability")
        if clean["hard_blocker"] and not clean["candidate_quote"]:
            raise ValueError("hard blockers need candidate evidence establishing the conflict")
        rows.append(clean)
    return sorted(rows, key=lambda row: (IMPORTANCE.index(row["importance"]), row["match"] == "strong"))


def render_requirements(rows: list[dict[str, Any]]) -> list[str]:
    lines = ["", "## Requirement evidence", "", "| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |", "| --- | --- | --- | --- | --- | --- |"]
    def cell(text: str) -> str:
        return " ".join(text.split()).replace("|", "\\|")
    for row in rows:
        values = [row["requirement"], f"{row['importance']} / {row['basis']}", row["match"], row["jd_quote"], row["candidate_quote"], f"{row['risk']} / {row['mitigation']}"]
        lines.append("| " + " | ".join(cell(value) for value in values) + " |")
    return lines
