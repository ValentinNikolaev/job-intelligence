from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Protocol

import yaml


RECOMMENDATIONS = (
    "strong_match",
    "match",
    "possible_match",
    "weak_match",
    "not_match",
)

MATCH_OUTPUT_SCHEMA: dict[str, Any] = {
    "type": "object",
    "properties": {
        "score": {"type": "integer", "minimum": 0, "maximum": 100},
        "recommendation": {"type": "string", "enum": list(RECOMMENDATIONS)},
        "summary": {"type": "string"},
        "strengths": {"type": "array", "items": {"type": "string"}},
        "gaps": {"type": "array", "items": {"type": "string"}},
        "concerns": {"type": "array", "items": {"type": "string"}},
        "hard_rejection": {"type": "boolean"},
        "hard_rejection_reason": {"type": ["string", "null"]},
    },
    "required": [
        "score",
        "recommendation",
        "summary",
        "strengths",
        "gaps",
        "concerns",
        "hard_rejection",
        "hard_rejection_reason",
    ],
    "additionalProperties": False,
}

DEFAULT_MATCH_PROMPT_PATH = (
    Path(__file__).resolve().parents[1] / "prompts" / "vacancy-match.md"
)


def _prompt_version(path: Path = DEFAULT_MATCH_PROMPT_PATH) -> str:
    prompt = path.read_text(encoding="utf-8").strip()
    payload = prompt + json.dumps(
        MATCH_OUTPUT_SCHEMA, sort_keys=True, separators=(",", ":")
    )
    return "job-match-v1:sha256:" + hashlib.sha256(payload.encode("utf-8")).hexdigest()


PROMPT_VERSION = _prompt_version()

_MATCH_META_FIELDS = (
    "id",
    "title",
    "company",
    "company_url",
    "location",
    "remote",
    "employment_type",
    "published_at",
    "analysis_priority",
    "data_source",
)

_RELEVANT_SOURCE_METADATA = {
    "categories",
    "compensation",
    "department",
    "industry",
    "job_types",
    "level",
    "location_restrictions",
    "parent_categories",
    "salary",
    "secondary_locations",
    "seniority",
    "tags",
    "team",
    "timezone_restrictions",
    "workplace_type",
}

_CLOUDFLARE_EMAIL_PROTECTION_RE = re.compile(
    r"(/cdn-cgi/l/email-protection#)[0-9A-Fa-f]+"
)


class MatchError(RuntimeError):
    pass


class MatchClient(Protocol):
    def analyze(self, *, candidate_profile: str, vacancy: Mapping[str, Any]) -> Mapping[str, Any]: ...


@dataclass(frozen=True, slots=True)
class AnalysisResult:
    status: str
    vacancy_id: str
    directory: str
    score: int | None = None


@dataclass(slots=True)
class AnalysisSummary:
    selected: int = 0
    analyzed: int = 0
    skipped: int = 0
    errors: int = 0


@dataclass(frozen=True, slots=True)
class AnalysisPack:
    schema_version: int
    workflow: str
    prompt_version: str
    profile: str
    profile_version: str
    items: tuple[dict[str, Any], ...]


class CodexMatchDraftClient:
    """Load a match draft produced by the active Codex task."""

    def __init__(self, path: Path, *, model: str) -> None:
        if not model.strip():
            raise ValueError("a Codex model label is required")
        self.path = path.resolve()
        self.model = model.strip()

    def analyze(self, *, candidate_profile: str, vacancy: Mapping[str, Any]) -> Mapping[str, Any]:
        del candidate_profile, vacancy
        return _read_yaml_mapping(self.path, "Codex match draft")


class MatchAnalyzer:
    def __init__(
        self,
        registry_root: Path,
        profile_paths: Sequence[Path],
        client: MatchClient,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self.registry_root = registry_root
        self.jobs_dir = registry_root / "jobs"
        self.profile_paths = tuple(profile_paths)
        self.client = client
        self.model = str(getattr(client, "model", client.__class__.__name__))
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def resolve(self, selector: str) -> list[Path]:
        if selector.casefold() == "all":
            return sorted(path.parent for path in self.jobs_dir.glob("*/meta.yaml"))

        direct = self.jobs_dir / selector
        if direct.is_dir() and (direct / "meta.yaml").is_file():
            return [direct]

        matches = []
        for meta_path in self.jobs_dir.glob("*/meta.yaml"):
            meta = _read_yaml_mapping(meta_path, "vacancy metadata")
            if str(meta.get("id", "")) == selector:
                matches.append(meta_path.parent)
        if len(matches) > 1:
            raise MatchError(f"vacancy id appears in multiple directories: {selector}")
        if not matches:
            raise MatchError(f"vacancy not found: {selector}")
        return matches

    def analyze_directory(self, directory: Path, *, force: bool = False) -> AnalysisResult:
        profile_text, profile_version, meta, vacancy, job_version = self._inputs(directory)

        match_path = directory / "match.yaml"
        if not force and match_path.exists():
            existing = _read_yaml_mapping(match_path, "match analysis")
            if (
                existing.get("profile_version") == profile_version
                and existing.get("job_version") == job_version
                and existing.get("prompt_version") == PROMPT_VERSION
                and existing.get("model") == self.model
            ):
                score = existing.get("score")
                return AnalysisResult(
                    "skipped",
                    str(meta.get("id", "")),
                    directory.name,
                    score if isinstance(score, int) and not isinstance(score, bool) else None,
                )

        analysis = self.client.analyze(candidate_profile=profile_text, vacancy=vacancy)
        return self.publish_analysis(
            directory,
            analysis,
            force=force,
            expected_profile_version=profile_version,
            expected_job_version=job_version,
        )

    def publish_analysis(
        self,
        directory: Path,
        analysis: Mapping[str, Any],
        *,
        force: bool = False,
        expected_profile_version: str | None = None,
        expected_job_version: str | None = None,
    ) -> AnalysisResult:
        profile_text, profile_version, meta, vacancy, job_version = self._inputs(directory)
        del profile_text, vacancy
        if expected_profile_version and expected_profile_version != profile_version:
            raise MatchError(f"candidate profile changed after the analysis pack was created: {directory}")
        if expected_job_version and expected_job_version != job_version:
            raise MatchError(f"vacancy changed after the analysis pack was created: {directory}")
        match_path = directory / "match.yaml"
        if not force and match_path.exists():
            existing = _read_yaml_mapping(match_path, "match analysis")
            if (
                existing.get("profile_version") == profile_version
                and existing.get("job_version") == job_version
                and existing.get("prompt_version") == PROMPT_VERSION
                and existing.get("model") == self.model
            ):
                score = existing.get("score")
                return AnalysisResult(
                    "skipped",
                    str(meta.get("id", "")),
                    directory.name,
                    score if isinstance(score, int) and not isinstance(score, bool) else None,
                )

        validated = validate_match(analysis)
        stored = {
            **validated,
            "analyzed_at": _utc_iso(self._clock()),
            "profile_version": profile_version,
            "job_version": job_version,
            "prompt_version": PROMPT_VERSION,
            "model": self.model,
        }
        _write_atomic(directory / "match.md", render_match_markdown(stored))
        _write_atomic(match_path, yaml.safe_dump(stored, allow_unicode=True, sort_keys=False))
        return AnalysisResult(
            "analyzed", str(meta.get("id", "")), directory.name, int(stored["score"])
        )

    def is_current(self, directory: Path) -> bool:
        _, profile_version, _, _, job_version = self._inputs(directory)
        match_path = directory / "match.yaml"
        if not match_path.is_file():
            return False
        try:
            existing = _read_yaml_mapping(match_path, "match analysis")
        except MatchError:
            return False
        return (
            existing.get("profile_version") == profile_version
            and existing.get("job_version") == job_version
            and existing.get("prompt_version") == PROMPT_VERSION
            and existing.get("model") == self.model
        )

    def _inputs(
        self, directory: Path
    ) -> tuple[str, str, dict[str, Any], dict[str, Any], str]:
        profile_text, profile_version = self._load_profile()
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
        job_path = directory / "job.md"
        if not job_path.is_file():
            raise MatchError(f"vacancy job description is missing: {job_path}")
        job_text = job_path.read_text(encoding="utf-8")
        vacancy = _compact_vacancy(meta, job_text)
        job_version = _content_version(
            json.dumps(vacancy, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        )
        return profile_text, profile_version, meta, vacancy, job_version

    def _load_profile(self) -> tuple[str, str]:
        if not self.profile_paths:
            raise MatchError("at least one Candidate Profile path is required")
        sections = []
        for path in self.profile_paths:
            if not path.is_file():
                raise MatchError(f"Candidate Profile file not found: {path}")
            content = path.read_text(encoding="utf-8").strip()
            if not content:
                raise MatchError(f"Candidate Profile file is empty: {path}")
            sections.append(f"## Source: {path.name}\n\n{content}")
        profile_text = "\n\n".join(sections)
        return profile_text, _content_version(profile_text)


def build_analysis_pack(
    registry_root: Path,
    profile_paths: Sequence[Path],
    *,
    limit: int | None = None,
    triage_skip: Callable[[Path], bool] | None = None,
) -> AnalysisPack:
    """Create a sealed, deterministic input pack for one batched Codex run."""
    analyzer = MatchAnalyzer(
        registry_root,
        profile_paths,
        CodexMatchDraftClient(Path("unused-match.yaml"), model="pack-builder"),
    )
    profile, profile_version = analyzer._load_profile()
    items: list[dict[str, Any]] = []
    for directory in _priority_sorted_directories(analyzer.resolve("all")):
        if triage_skip and triage_skip(directory):
            continue
        if analyzer.is_current(directory):
            continue
        _, _, meta, vacancy, job_version = analyzer._inputs(directory)
        items.append(
            {
                "vacancy_id": str(meta.get("id", "")),
                "directory": directory.name,
                "profile_version": profile_version,
                "job_version": job_version,
                "vacancy": vacancy,
            }
        )
        if limit is not None and len(items) >= limit:
            break
    return AnalysisPack(1, "analyze", PROMPT_VERSION, profile, profile_version, tuple(items))


def dump_analysis_pack(pack: AnalysisPack, path: Path) -> None:
    payload = {
        "schema_version": pack.schema_version,
        "workflow": pack.workflow,
        "prompt_version": pack.prompt_version,
        "profile": {"text": pack.profile, "version": pack.profile_version},
        "items": list(pack.items),
    }
    _write_atomic(path, yaml.safe_dump(payload, allow_unicode=True, sort_keys=False))


def load_analysis_pack(path: Path) -> dict[str, Any]:
    loaded = _read_yaml_mapping(path, "analysis pack")
    if loaded.get("schema_version") != 1 or loaded.get("workflow") != "analyze":
        raise MatchError("analysis pack must use schema_version 1 and workflow analyze")
    if not isinstance(loaded.get("profile"), dict) or not isinstance(loaded.get("items"), list):
        raise MatchError("analysis pack requires profile and items")
    if not isinstance(loaded["profile"].get("text"), str) or not isinstance(loaded["profile"].get("version"), str):
        raise MatchError("analysis pack profile requires text and version")
    if loaded.get("prompt_version") != PROMPT_VERSION:
        raise MatchError("analysis pack prompt_version is stale")
    return loaded


def publish_analysis_batch(
    pack: Mapping[str, Any],
    results: Mapping[str, Any],
    analyzer: MatchAnalyzer,
) -> AnalysisSummary:
    """Validate and publish a complete batch; a missing/duplicate key fails closed."""
    items = pack.get("items")
    if not isinstance(items, list) or not items:
        raise MatchError("analysis pack has no items")
    if set(results) != {str(item.get("directory", "")) for item in items if isinstance(item, dict)}:
        raise MatchError("batch results must contain exactly one result for every pack directory")
    validated: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise MatchError("analysis pack item must be a mapping")
        directory_name = str(item.get("directory", ""))
        directory = analyzer.registry_root / "jobs" / directory_name
        _, profile_version, _, _, job_version = analyzer._inputs(directory)
        if str(item.get("profile_version", "")) != profile_version:
            raise MatchError(f"candidate profile changed after the analysis pack was created: {directory}")
        if str(item.get("job_version", "")) != job_version:
            raise MatchError(f"vacancy changed after the analysis pack was created: {directory}")
        result = results[directory_name]
        if not isinstance(result, Mapping):
            raise MatchError(f"batch result must be a mapping: {directory_name}")
        validated[directory_name] = validate_match(result)
    summary = AnalysisSummary(selected=len(items))
    for item in items:
        directory = analyzer.registry_root / "jobs" / str(item.get("directory", ""))
        result = analyzer.publish_analysis(
            directory,
            validated[directory.name],
            expected_profile_version=str(item.get("profile_version", "")),
            expected_job_version=str(item.get("job_version", "")),
        )
        if result.status == "skipped":
            summary.skipped += 1
        else:
            summary.analyzed += 1
    return summary


def validate_match(value: Mapping[str, Any]) -> dict[str, Any]:
    expected = {
        "score",
        "recommendation",
        "summary",
        "strengths",
        "gaps",
        "concerns",
        "hard_rejection",
        "hard_rejection_reason",
    }
    if set(value) != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected)
        details = []
        if missing:
            details.append("missing " + ", ".join(missing))
        if extra:
            details.append("unexpected " + ", ".join(extra))
        raise MatchError("invalid match fields: " + "; ".join(details))

    score = value["score"]
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise MatchError("match score must be an integer from 0 to 100")
    recommendation = value["recommendation"]
    if recommendation not in RECOMMENDATIONS:
        raise MatchError(f"invalid recommendation: {recommendation}")
    summary = _required_text(value["summary"], "summary")
    strengths = _text_list(value["strengths"], "strengths")
    gaps = _text_list(value["gaps"], "gaps")
    concerns = _text_list(value["concerns"], "concerns")
    hard_rejection = value["hard_rejection"]
    if not isinstance(hard_rejection, bool):
        raise MatchError("hard_rejection must be a boolean")
    reason_value = value["hard_rejection_reason"]
    if reason_value is not None and not isinstance(reason_value, str):
        raise MatchError("hard_rejection_reason must be text or null")
    reason = reason_value.strip() if isinstance(reason_value, str) else None
    if hard_rejection and not reason:
        raise MatchError("a hard rejection requires a reason")
    if hard_rejection and (recommendation != "not_match" or score > 24):
        raise MatchError("a hard rejection must be not_match with a score from 0 to 24")

    return {
        "score": score,
        "recommendation": recommendation,
        "summary": summary,
        "strengths": strengths,
        "gaps": gaps,
        "concerns": concerns,
        "hard_rejection": hard_rejection,
        "hard_rejection_reason": reason,
    }


def render_match_markdown(match: Mapping[str, Any]) -> str:
    recommendation = str(match["recommendation"]).replace("_", " ").title()
    lines = [
        "# Match Analysis",
        "",
        f"**Score:** {match['score']}/100  ",
        f"**Recommendation:** {recommendation}",
        "",
        str(match["summary"]).strip(),
    ]
    _append_section(lines, "Why it matches", match["strengths"])
    _append_section(lines, "Gaps", match["gaps"])
    _append_section(lines, "Concerns", match["concerns"])
    if match.get("hard_rejection"):
        _append_section(lines, "Hard rejection", [match.get("hard_rejection_reason")])
    return "\n".join(lines).rstrip() + "\n"


def _compact_vacancy(meta: Mapping[str, Any], job_text: str) -> dict[str, Any]:
    metadata = {field: meta.get(field) for field in _MATCH_META_FIELDS if meta.get(field) is not None}
    sources = []
    for source in meta.get("sources", []):
        if not isinstance(source, dict):
            continue
        compact = {"source": source.get("source")}
        source_metadata = source.get("metadata")
        if isinstance(source_metadata, dict):
            relevant = {
                key: value
                for key, value in source_metadata.items()
                if key in _RELEVANT_SOURCE_METADATA and value not in (None, {}, [], "")
            }
            if relevant:
                compact["metadata"] = relevant
        sources.append(compact)
    if sources:
        metadata["sources"] = sources
    return {"metadata": metadata, "job_description": _stable_job_text(job_text)}


def _stable_job_text(job_text: str) -> str:
    text = _CLOUDFLARE_EMAIL_PROTECTION_RE.sub(r"\1<protected>", job_text)
    return text.strip()


def _priority_sorted_directories(directories: Sequence[Path]) -> list[Path]:
    return sorted(directories, key=_analysis_queue_key, reverse=True)


def _analysis_queue_key(directory: Path) -> tuple[int, str, str]:
    try:
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
    except MatchError:
        return (0, "", directory.name)
    return (
        _analysis_priority(meta.get("analysis_priority")),
        str(meta.get("discovered_at") or ""),
        directory.name,
    )


def _analysis_priority(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value if 0 <= value <= 100 else 0


def _read_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise MatchError(f"cannot read {label} {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise MatchError(f"invalid YAML in {label} {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise MatchError(f"{label} must be a YAML mapping: {path}")
    return loaded


def _content_version(content: str) -> str:
    return "sha256:" + hashlib.sha256(content.encode("utf-8")).hexdigest()


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise MatchError(f"{field} must be non-empty text")
    return value.strip()


def _text_list(value: Any, field: str) -> list[str]:
    if not isinstance(value, list):
        raise MatchError(f"{field} must be a list")
    result = []
    for item in value:
        if not isinstance(item, str) or not item.strip():
            raise MatchError(f"{field} entries must be non-empty text")
        result.append(item.strip())
    return result


def _append_section(lines: list[str], heading: str, items: Any) -> None:
    clean_items = [str(item).strip() for item in items if str(item or "").strip()]
    if not clean_items:
        return
    lines.extend(("", f"## {heading}", ""))
    lines.extend(f"- {item}" for item in clean_items)


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc).replace(microsecond=0)
    return value.isoformat().replace("+00:00", "Z")


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
