from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
from collections.abc import Callable, Collection, Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PureWindowsPath
from typing import Any, Protocol

import yaml

from . import storage_bridge as op
from .rejection_cooldown import load_retry_rules, retry_reason, require_retry_eligible, rejection_day
from .requirements import validate_requirements, render_requirements
from .matching_policy import DEFAULT_PROJECT_ROOT, MatchingContext, canonical, digest, load_matching_context


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
        "requirements": {"type": "array", "maxItems": 100, "items": {"type": "object"}},
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

LEGACY_PROMPT_VERSION = "job-match-v1:sha256:813df4c8583b3d5ac10bf119ee81af822f104b467466a37c820cb6a3ca2629f0"
# Exact extraction identity approved by the independent synthetic migration evaluation.
APPROVED_EXTRACTION_VERSION = "job-match-v2:sha256:936069737a4caa24ba6a39627dc3ef204e5bee92bf658d074f62be57028137c5"


def current_matching_context(project_root: Path = DEFAULT_PROJECT_ROOT) -> MatchingContext:
    return load_matching_context(project_root, output_schema=MATCH_OUTPUT_SCHEMA)


def match_is_current(match: Mapping[str, Any], *, profile_version: str, job_version: str,
                     models: Collection[str], context: MatchingContext) -> bool:
    version = match.get("prompt_version")
    compatible = version == context.prompt_version or (
        version == LEGACY_PROMPT_VERSION and context.prompt_version == APPROVED_EXTRACTION_VERSION
    )
    return (compatible and isinstance(match.get("model"), str) and match.get("profile_version") == profile_version
            and match.get("job_version") == job_version and match.get("model") in models)

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

MAX_ANALYSIS_BATCH_SIZE = 15
_ANALYSIS_SKIP_STATUSES = frozenset(
    {
        "prepared",
        "applied",
        "interview",
        "technical_interview",
        "final_interview",
        "offer",
        "rejected",
        "withdrawn",
        "closed",
    }
)

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
    context: MatchingContext

    def to_dict(self) -> dict[str, Any]:
        payload = {"schema_version": self.schema_version, "workflow": self.workflow,
                   "prompt_version": self.prompt_version, "prompt": self.context.prompt,
                   "policy": self.context.policy.canonical_analysis_snapshot(),
                   "policy_version": self.context.policy.fingerprint(),
                   "output_schema": json.loads(self.context.schema_json),
                   "profile": {"text": self.profile, "version": self.profile_version}, "items": list(self.items)}
        return {**payload, "pack_sha256": digest(payload)}


class CodexMatchDraftClient:
    """Load a match draft produced by the active Codex task."""

    def __init__(self, path: Path, *, model: str, context: MatchingContext | None = None) -> None:
        if not model.strip():
            raise ValueError("a Codex model label is required")
        self.path = path.resolve()
        self.model = model.strip()
        self.context = context

    def analyze(self, *, candidate_profile: str, vacancy: Mapping[str, Any]) -> Mapping[str, Any]:
        context = self.context if self.context is not None else current_matching_context()
        pack = load_analysis_pack(self.path, context=context)
        if len(pack["items"]) != 1:
            raise MatchError("single Codex draft requires exactly one sealed item")
        item = pack["items"][0]
        if pack["profile"]["text"] != candidate_profile or item["vacancy"] != vacancy:
            raise MatchError("single Codex draft is not bound to the supplied profile and vacancy")
        results = pack.get("results")
        if not isinstance(results, dict) or set(results) != {item["directory"]}:
            raise MatchError("single Codex draft requires exactly its sealed directory result")
        return results[item["directory"]]


class MatchAnalyzer:
    def __init__(
        self,
        registry_root: Path,
        profile_paths: Sequence[Path],
        client: MatchClient,
        *,
        clock: Callable[[], datetime] | None = None,
        allowed_models: Collection[str] | None = None,
        context: MatchingContext | None = None,
    ) -> None:
        self.registry_root = registry_root
        self.jobs_dir = registry_root / "jobs"
        self.profile_paths = tuple(profile_paths)
        self.client = client
        self.model = str(getattr(client, "model", client.__class__.__name__))
        self.allowed_models = (
            frozenset(allowed_models)
            if allowed_models is not None
            else frozenset((self.model,))
        )
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.context = context

    def matching_context(self) -> MatchingContext:
        return self.context if self.context is not None else current_matching_context()

    def checked_directory(self, directory: Path) -> Path:
        directory = Path(directory)
        jobs = self.jobs_dir.resolve()
        resolved = directory.resolve()
        if resolved.parent != jobs or resolved == jobs:
            raise MatchError("analysis directory must be directly inside registry/jobs")
        return directory

    def resolve(self, selector: str) -> list[Path]:
        if selector.casefold() == "all":
            return sorted(self.checked_directory(path.parent) for path in op.metadata_paths(self.jobs_dir))

        _directory_name(selector)
        direct = self.checked_directory(self.jobs_dir / selector)
        if op.exists(direct / "meta.yaml"):
            return [direct]

        matches = []
        for meta_path in op.metadata_paths(self.jobs_dir):
            meta = _read_yaml_mapping(meta_path, "vacancy metadata")
            if str(meta.get("id", "")) == selector:
                matches.append(self.checked_directory(meta_path.parent))
        if len(matches) > 1:
            raise MatchError(f"vacancy id appears in multiple directories: {selector}")
        if not matches:
            raise MatchError(f"vacancy not found: {selector}")
        return matches

    def analyze_directory(self, directory: Path, *, force: bool = False) -> AnalysisResult:
        context = self.matching_context()
        profile_text, profile_version, meta, vacancy, job_version = self._inputs(directory)
        require_retry_eligible(self.registry_root, str(meta.get("company") or ""), today=rejection_day(self._clock().isoformat()))

        if analysis_should_skip_status(meta) and not force:
            return AnalysisResult("skipped", str(meta.get("id", "")), directory.name)

        match_path = directory / "match.yaml"
        if not force and op.exists(match_path):
            existing = _read_yaml_mapping(match_path, "match analysis")
            if match_is_current(existing, profile_version=profile_version, job_version=job_version,
                                models=self.allowed_models, context=context):
                score = existing.get("score")
                return AnalysisResult(
                    "skipped",
                    str(meta.get("id", "")),
                    directory.name,
                    score if isinstance(score, int) and not isinstance(score, bool) else None,
                )

        analysis = self.client.analyze(candidate_profile=profile_text, vacancy=vacancy)
        return self._publish_analysis(
            directory,
            analysis,
            force=force,
            expected_profile_version=profile_version,
            expected_job_version=job_version,
            expected_prompt_version=context.prompt_version,
            context=context,
        )

    def publish_analysis(
        self,
        directory: Path,
        analysis: Mapping[str, Any],
        *,
        force: bool = False,
        expected_profile_version: str | None = None,
        expected_job_version: str | None = None,
        expected_prompt_version: str | None = None,
    ) -> AnalysisResult:
        """Publish one complete sealed Codex draft; copied labels cannot bind a raw result."""
        self.checked_directory(directory)
        context = self.matching_context()
        validate_analysis_pack(analysis, context=context)
        items = analysis["items"]
        if len(items) != 1 or items[0]["directory"] != directory.name:
            raise MatchError("public single publication requires the complete sealed draft for exactly this directory")
        results = analysis.get("results")
        summary = publish_analysis_batch(analysis, results, self, force=force)
        score = results[directory.name]["score"] if summary.analyzed else None
        return AnalysisResult("analyzed" if summary.analyzed else "skipped", items[0]["vacancy_id"], directory.name, score)

    @op.transactional
    def _publish_analysis(self, directory: Path, analysis: Mapping[str, Any], *, force: bool,
                          expected_profile_version: str, expected_job_version: str,
                          expected_prompt_version: str, context: MatchingContext) -> AnalysisResult:
        if expected_prompt_version != context.prompt_version:
            raise MatchError("analysis prompt or matching policy changed after the draft was created")
        profile_text, profile_version, meta, vacancy, job_version = self._inputs(directory)
        require_retry_eligible(self.registry_root, str(meta.get("company") or ""), today=rejection_day(self._clock().isoformat()))
        if analysis_should_skip_status(meta) and not force:
            return AnalysisResult("skipped", str(meta.get("id", "")), directory.name)
        if expected_profile_version != profile_version:
            raise MatchError(f"candidate profile changed after the analysis pack was created: {directory}")
        if expected_job_version != job_version:
            raise MatchError(f"vacancy changed after the analysis pack was created: {directory}")
        match_path = directory / "match.yaml"
        if not force and op.exists(match_path):
            existing = _read_yaml_mapping(match_path, "match analysis")
            if match_is_current(existing, profile_version=profile_version, job_version=job_version,
                                models=self.allowed_models, context=context):
                score = existing.get("score")
                return AnalysisResult(
                    "skipped",
                    str(meta.get("id", "")),
                    directory.name,
                    score if isinstance(score, int) and not isinstance(score, bool) else None,
                )

        validated = validate_match(analysis, vacancy_text=str(vacancy["job_description"]), candidate_text=profile_text)
        stored = {
            **validated,
            "analyzed_at": _utc_iso(self._clock()),
            "profile_version": profile_version,
            "job_version": job_version,
            "prompt_version": context.prompt_version,
            "model": self.model,
        }
        _write_atomic(directory / "match.md", render_match_markdown(stored))
        _write_atomic(match_path, yaml.safe_dump(stored, allow_unicode=True, sort_keys=False))
        return AnalysisResult(
            "analyzed", str(meta.get("id", "")), directory.name, int(stored["score"])
        )

    def is_current(
        self, directory: Path, *, allowed_models: Collection[str] | None = None
    ) -> bool:
        _, profile_version, _, _, job_version = self._inputs(directory)
        match_path = directory / "match.yaml"
        if not op.exists(match_path):
            return False
        try:
            existing = _read_yaml_mapping(match_path, "match analysis")
        except MatchError:
            return False
        return match_is_current(existing, profile_version=profile_version, job_version=job_version,
                                models=allowed_models if allowed_models is not None else self.allowed_models,
                                context=self.matching_context())

    def _inputs(
        self, directory: Path
    ) -> tuple[str, str, dict[str, Any], dict[str, Any], str]:
        self.checked_directory(directory)
        profile_text, profile_version = self._load_profile()
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
        job_path = directory / "job.md"
        if not op.exists(job_path):
            raise MatchError(f"vacancy job description is missing: {job_path}")
        job_text = op.read_text(job_path)
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
            if not op.exists(path):
                raise MatchError(f"Candidate Profile file not found: {path}")
            content = op.read_text(path).strip()
            if not content:
                raise MatchError(f"Candidate Profile file is empty: {path}")
            sections.append(f"## Source: {path.name}\n\n{content}")
        profile_text = "\n\n".join(sections)
        return profile_text, _content_version(profile_text)


def build_analysis_pack(
    registry_root: Path,
    profile_paths: Sequence[Path],
    *,
    directories: Sequence[Path] | None = None,
    limit: int | None = None,
    triage_skip: Callable[[Path], bool] | None = None,
    model: str = "pack-builder",
    allowed_models: Collection[str] | None = None,
    context: MatchingContext | None = None,
    force: bool = False,
) -> AnalysisPack:
    """Create a sealed, deterministic input pack for one batched Codex run."""
    if limit is None:
        limit = MAX_ANALYSIS_BATCH_SIZE
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= MAX_ANALYSIS_BATCH_SIZE:
        raise MatchError(f"analysis pack limit must be between 1 and {MAX_ANALYSIS_BATCH_SIZE}")
    analyzer = MatchAnalyzer(
        registry_root,
        profile_paths,
        CodexMatchDraftClient(Path("unused-match.yaml"), model=model),
        allowed_models=allowed_models,
        context=context,
    )
    context = analyzer.matching_context()
    analyzer.context = context
    profile, profile_version = analyzer._load_profile()
    items: list[dict[str, Any]] = []
    retry_rules = load_retry_rules(registry_root)
    selected_directories = analyzer.resolve("all") if directories is None else [analyzer.checked_directory(path) for path in directories]
    for directory in _priority_sorted_directories(selected_directories):
        analyzer.checked_directory(directory)
        if triage_skip and triage_skip(directory):
            continue
        meta = _read_yaml_mapping(directory / "meta.yaml", "vacancy metadata")
        if retry_reason(str(meta.get("company") or ""), retry_rules):
            continue
        if analysis_should_skip_status(meta) and not force:
            continue
        if analyzer.is_current(directory) and not force:
            continue
        _, _, meta, vacancy, job_version = analyzer._inputs(directory)
        items.append(
            {
                "vacancy_id": str(meta.get("id", "")),
                "directory": directory.name,
                "source_url": _primary_source_url(meta),
                "profile_version": profile_version,
                "job_version": job_version,
                "vacancy": vacancy,
            }
        )
        if len(items) >= limit:
            break
    return AnalysisPack(2, "analyze", context.prompt_version, profile, profile_version, tuple(items), context)


def dump_analysis_pack(pack: AnalysisPack, path: Path) -> None:
    _write_atomic(path, yaml.safe_dump(pack.to_dict(), allow_unicode=True, sort_keys=False))


def load_analysis_pack(path: Path, *, context: MatchingContext | None = None) -> dict[str, Any]:
    loaded = _read_yaml_mapping(path, "analysis pack")
    validate_analysis_pack(loaded, context=context if context is not None else current_matching_context())
    return loaded


def _directory_name(value: Any) -> str:
    if (not isinstance(value, str) or not value or value in {".", ".."}
            or "/" in value or "\\" in value or PureWindowsPath(value).drive or ":" in value):
        raise MatchError("analysis directory must be a simple registry/jobs directory name")
    return value


def validate_analysis_pack(loaded: Mapping[str, Any], *, context: MatchingContext) -> None:
    required = {"schema_version", "workflow", "prompt_version", "prompt", "policy", "policy_version", "output_schema", "profile", "items", "pack_sha256"}
    if set(loaded) - {"results"} != required or type(loaded.get("schema_version")) is not int or loaded["schema_version"] != 2 or loaded.get("workflow") != "analyze":
        raise MatchError("analysis draft requires a schema-2 sealed pack; export with analyze --pack or pending analyze --pack")
    if not isinstance(loaded.get("profile"), dict) or not isinstance(loaded.get("items"), list):
        raise MatchError("analysis pack requires profile and items")
    if len(loaded["items"]) > MAX_ANALYSIS_BATCH_SIZE:
        raise MatchError(f"analysis pack exceeds the maximum of {MAX_ANALYSIS_BATCH_SIZE} items")
    if (set(loaded["profile"]) != {"text", "version"} or not isinstance(loaded["profile"].get("text"), str)
            or not loaded["profile"]["text"].strip() or not isinstance(loaded["profile"].get("version"), str)):
        raise MatchError("analysis pack profile requires text and version")
    profile = loaded["profile"]
    if profile["version"] != _content_version(profile["text"]):
        raise MatchError("analysis pack profile text does not match its version")
    if (loaded["prompt_version"] != context.prompt_version or loaded["prompt"] != context.prompt
            or loaded["policy"] != context.policy.canonical_analysis_snapshot()
            or loaded["policy_version"] != context.policy.fingerprint()
            or loaded["output_schema"] != json.loads(context.schema_json)):
        raise MatchError("analysis pack prompt, schema or matching policy is stale or altered")
    sealed = {key: value for key, value in loaded.items() if key not in {"pack_sha256", "results"}}
    if loaded["pack_sha256"] != digest(sealed):
        raise MatchError("analysis pack content does not match its sealed hash")
    seen = set()
    seen_ids = set()
    for item in loaded["items"]:
        if not isinstance(item, dict) or set(item) != {"vacancy_id", "directory", "source_url", "profile_version", "job_version", "vacancy"}:
            raise MatchError("analysis pack item requires its exact sealed fields")
        name = _directory_name(item["directory"])
        if name in seen:
            raise MatchError("analysis pack contains duplicate directories")
        seen.add(name)
        if not isinstance(item["vacancy_id"], str) or not item["vacancy_id"] or item["vacancy_id"] in seen_ids or not isinstance(item["source_url"], str):
            raise MatchError("analysis pack vacancy IDs must be nonempty and unique; source URLs must be text")
        seen_ids.add(item["vacancy_id"])
        vacancy = item["vacancy"]
        if not isinstance(vacancy, dict) or set(vacancy) != {"metadata", "job_description"} or not isinstance(vacancy["metadata"], dict) or not isinstance(vacancy["job_description"], str):
            raise MatchError("analysis pack vacancy must contain metadata and job description")
        if (item["profile_version"] != profile["version"] or item["job_version"] != _content_version(canonical(vacancy))
                or item["vacancy_id"] != vacancy["metadata"].get("id")):
            raise MatchError("analysis pack vacancy/profile payload does not match its bound identity or version")


def publish_analysis_batch(
    pack: Mapping[str, Any],
    results: Mapping[str, Any],
    analyzer: MatchAnalyzer,
    *,
    force: bool = False,
) -> AnalysisSummary:
    """Validate and publish a complete batch; a missing/duplicate key fails closed."""
    context = analyzer.matching_context()
    validate_analysis_pack(pack, context=context)
    items = pack.get("items")
    if not isinstance(items, list) or not items:
        raise MatchError("analysis pack has no items")
    if len(items) > MAX_ANALYSIS_BATCH_SIZE:
        raise MatchError(f"analysis pack exceeds the maximum of {MAX_ANALYSIS_BATCH_SIZE} items")
    if not isinstance(results, Mapping) or set(results) != {str(item.get("directory", "")) for item in items if isinstance(item, dict)}:
        raise MatchError("batch results must contain exactly one result for every pack directory")
    validated: dict[str, dict[str, Any]] = {}
    for item in items:
        if not isinstance(item, dict):
            raise MatchError("analysis pack item must be a mapping")
        directory_name = str(item.get("directory", ""))
        directory = analyzer.checked_directory(analyzer.jobs_dir / directory_name)
        profile_text, profile_version, meta, vacancy, job_version = analyzer._inputs(directory)
        if item["source_url"] != _primary_source_url(meta):
            raise MatchError(f"analysis pack source URL differs from current canonical metadata: {directory}")
        if (pack["profile"]["text"] != profile_text or item["vacancy"] != vacancy
                or item["vacancy_id"] != str(meta.get("id", ""))):
            raise MatchError(f"analysis pack payload differs from current candidate/vacancy inputs: {directory}")
        if str(item.get("profile_version", "")) != profile_version:
            raise MatchError(f"candidate profile changed after the analysis pack was created: {directory}")
        if str(item.get("job_version", "")) != job_version:
            raise MatchError(f"vacancy changed after the analysis pack was created: {directory}")
        if analyzer.is_current(directory) and not force:
            raise MatchError(
                f"analysis pack is stale because analysis is already current: {directory}; "
                "refresh the repository and rebuild the pack"
            )
        result = results[directory_name]
        if not isinstance(result, Mapping):
            raise MatchError(f"batch result must be a mapping: {directory_name}")
        validated[directory_name] = validate_match(result, vacancy_text=str(vacancy["job_description"]), candidate_text=profile_text)
    summary = AnalysisSummary(selected=len(items))
    for item in items:
        directory = analyzer.registry_root / "jobs" / str(item.get("directory", ""))
        result = analyzer._publish_analysis(
            directory,
            validated[directory.name],
            expected_profile_version=str(item.get("profile_version", "")),
            expected_job_version=str(item.get("job_version", "")),
            expected_prompt_version=context.prompt_version,
            force=force,
            context=context,
        )
        if result.status == "skipped":
            summary.skipped += 1
        else:
            summary.analyzed += 1
    return summary


def validate_match(value: Mapping[str, Any], *, vacancy_text: str | None = None,
                   candidate_text: str | None = None) -> dict[str, Any]:
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
    if set(value) - {"requirements"} != expected:
        missing = sorted(expected - set(value))
        extra = sorted(set(value) - expected - {"requirements"})
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

    result = {
        "score": score,
        "recommendation": recommendation,
        "summary": summary,
        "strengths": strengths,
        "gaps": gaps,
        "concerns": concerns,
        "hard_rejection": hard_rejection,
        "hard_rejection_reason": reason,
    }
    if "requirements" in value:
        try:
            rows = validate_requirements(value["requirements"], vacancy_text=vacancy_text, candidate_text=candidate_text)
        except ValueError as exc:
            raise MatchError(str(exc)) from exc
        if any(row["hard_blocker"] for row in rows) and not hard_rejection:
            raise MatchError("a confirmed requirement hard blocker requires hard_rejection")
        if hard_rejection and rows and not any(row["hard_blocker"] for row in rows):
            raise MatchError("hard_rejection requires a stated confirmed blocker in the requirement matrix")
        result["requirements"] = rows
    return result


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
    if match.get("requirements"):
        lines.extend(render_requirements(match["requirements"]))
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


def _primary_source_url(meta: Mapping[str, Any]) -> str:
    sources = meta.get("sources")
    if not isinstance(sources, list):
        return ""
    for source in sources:
        if not isinstance(source, dict):
            continue
        url = str(source.get("url") or "").strip()
        if url:
            return url
    return ""


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


def analysis_should_skip_status(meta: Mapping[str, Any]) -> bool:
    return str(meta.get("status", "")).strip().casefold() in _ANALYSIS_SKIP_STATUSES


def _read_yaml_mapping(path: Path, label: str) -> dict[str, Any]:
    try:
        text = op.read_text(path)
        node = yaml.compose(text, Loader=yaml.SafeLoader)

        def check(value, ancestors=frozenset()):
            if id(value) in ancestors:
                raise MatchError(f"recursive YAML aliases in {label}: {path}")
            ancestors = ancestors | {id(value)}
            if isinstance(value, yaml.MappingNode):
                seen = set()
                for key, child in value.value:
                    if not isinstance(key, yaml.ScalarNode) or key.tag != "tag:yaml.org,2002:str":
                        raise MatchError(f"mapping keys must be text in {label}: {path}")
                    if key.value in seen:
                        raise MatchError(f"duplicate YAML key in {label}: {path}")
                    seen.add(key.value)
                    check(child, ancestors)
            elif isinstance(value, yaml.SequenceNode):
                for child in value.value:
                    check(child, ancestors)

        if node is not None:
            check(node)
        loaded = yaml.safe_load(text)
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
    handled = op.write_operational(path, content)
    if handled is not None:
        return None
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
