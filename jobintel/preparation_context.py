"""Resolve the source boundaries and provenance for one preparation context."""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path, PureWindowsPath
from typing import Any

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


class PreparationContextError(ValueError):
    pass


def resolve_preparation_context(project_root: Path, context: PreparationContext | None = None) -> PreparationContext:
    """Check an optional operation snapshot against the current authoritative root."""
    current = load_preparation_context(project_root)
    if context is not None:
        if context.project_root != current.project_root:
            raise PreparationContextError("preparation context belongs to another project")
        if context.version != current.version:
            raise PreparationContextError("preparation context is stale for the current project configuration")
    return current


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def _mapping(value: Any, fields: set[str], label: str) -> dict:
    if not isinstance(value, dict) or set(value) != fields:
        raise PreparationContextError(f"{label} requires exactly: {', '.join(sorted(fields))}")
    return value


def _text(value: Any, label: str) -> str:
    if type(value) is not str or not value.strip() or value != value.strip():
        raise PreparationContextError(f"{label} requires nonempty trimmed text")
    return value


def _load(path: Path) -> dict:
    def check(node, ancestors=frozenset()):
        if id(node) in ancestors:
            raise PreparationContextError(f"{path}: recursive YAML aliases are unsupported")
        ancestors = ancestors | {id(node)}
        if isinstance(node, MappingNode):
            seen = set()
            for key, value in node.value:
                if not isinstance(key, ScalarNode) or key.tag != "tag:yaml.org,2002:str" or key.value in seen:
                    raise PreparationContextError(f"{path}: duplicate or non-text YAML key")
                seen.add(key.value)
                check(value, ancestors)
        elif isinstance(node, SequenceNode):
            for value in node.value:
                check(value, ancestors)
    try:
        text = path.read_text(encoding="utf-8-sig")
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            check(node)
        value = yaml.safe_load(text)
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        raise PreparationContextError(f"cannot read preparation configuration {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise PreparationContextError(f"{path}: configuration must be a mapping")
    return value


@dataclass(frozen=True, slots=True)
class PreparationContext:
    project_root: Path
    preparation_json: str
    voice_sources: tuple[str, ...]
    editorial_sha256: str

    @property
    def preparation(self) -> dict:
        return json.loads(self.preparation_json)

    @property
    def cv_owner_stem(self) -> str:
        return self.preparation["cv_owner_stem"]

    @property
    def candidate_directory(self) -> Path:
        return self.contained_path(self.preparation["candidate_directory"])

    @property
    def evidence_bank(self) -> Path:
        return self.contained_path(self.preparation["evidence_bank"])

    @property
    def career_source_path(self) -> Path:
        return self.source_path(self.preparation["career_sources"][0]["path"])

    @property
    def profile_paths(self) -> tuple[Path, ...]:
        paths = []
        configured = self.preparation["profile_sources"]
        preferred = configured["preferred"]
        selected = preferred if all(self.source_path(value).is_file() for value in preferred) else configured["fallback"]
        for value in [*selected, *configured["supplements"]]:
            pattern = Path(value)
            matches = sorted(self.candidate_directory.glob(pattern.name)) if "*" in pattern.name else [self.source_path(value)]
            for path in matches:
                path = self.source_path(self.relative(path))
                if path in paths:
                    raise PreparationContextError("duplicate resolved profile source")
                paths.append(path)
        return tuple(paths)

    @property
    def employer_aliases(self) -> dict[str, tuple[str, ...]]:
        return {name.casefold(): tuple(values) for name, values in self.preparation["employer_aliases"].items()}

    @property
    def version(self) -> str:
        snapshot = dict(preparation=self.preparation, voice_sources=self.voice_sources, editorial_sha256=self.editorial_sha256)
        return "preparation-v1:sha256:" + hashlib.sha256(_canonical(snapshot).encode("utf-8")).hexdigest()

    def contained_path(self, value: str) -> Path:
        if type(value) is not str or not value or "\\" in value or Path(value).is_absolute() or re.match(r"^[A-Za-z]:", value):
            raise PreparationContextError("preparation paths must be project-relative POSIX paths")
        parts = value.split("/")
        if any(part in {"", ".", ".."} for part in parts):
            raise PreparationContextError("preparation paths cannot contain empty or traversal segments")
        path = (self.project_root / value).resolve()
        if not path.is_relative_to(self.project_root):
            raise PreparationContextError("preparation path escapes the project")
        return path

    def relative(self, path: Path) -> str:
        try:
            return path.resolve().relative_to(self.project_root).as_posix()
        except ValueError as exc:
            raise PreparationContextError("preparation path escapes the project") from exc

    def source_path(self, value: str) -> Path:
        path = self.contained_path(value)
        if path.parent != self.candidate_directory or path.suffix.lower() != ".md":
            raise PreparationContextError("evidence sources must be direct Markdown files in the configured candidate directory")
        return path


def load_preparation_context(project_root: Path) -> PreparationContext:
    root = Path(project_root).resolve()
    profile = _load(root / "config/application-profile.yaml")
    if type(profile.get("schema_version")) is not int or profile["schema_version"] != 1:
        raise PreparationContextError("application profile requires schema_version 1")
    fields = {"cv_owner_stem", "candidate_directory", "evidence_bank", "profile_sources", "career_sources", "employer_aliases", "career_scope", "career_clarifications"}
    preparation = _mapping(profile.get("preparation"), fields, "application profile preparation")
    owner = _text(preparation["cv_owner_stem"], "cv_owner_stem")
    if not re.fullmatch(r"[A-Za-z0-9]{1,60}", owner):
        raise PreparationContextError("cv_owner_stem must contain 1-60 ASCII letters or digits")
    voice_policy = _mapping(_load(root / "config/application-review.yaml"), {"schema_version", "voice_sources"}, "voice policy")
    if type(voice_policy["schema_version"]) is not int or voice_policy["schema_version"] != 1:
        raise PreparationContextError("voice policy requires schema_version 1")
    voices = voice_policy["voice_sources"]
    if not isinstance(voices, list) or not voices:
        raise PreparationContextError("voice_sources requires a nonempty list")
    for value in voices:
        _text(value, "voice source")
    if len({value.casefold() for value in voices}) != len(voices):
        raise PreparationContextError("voice_sources cannot contain duplicate paths")
    editorial_path = root / "config/cv-editorial-knowledge.yaml"
    try:
        editorial_hash = hashlib.sha256(editorial_path.read_text(encoding="utf-8-sig").encode("utf-8")).hexdigest()
    except OSError as exc:
        raise PreparationContextError(f"cannot read CV editorial policy: {editorial_path}") from exc
    context = PreparationContext(root, _canonical(preparation), tuple(voices), editorial_hash)
    candidate = context.candidate_directory
    generated_roots = (".codex-work", "registry/jobs", "registry/application-history", "catalog")
    if any(candidate.is_relative_to((root / value).resolve()) for value in generated_roots):
        raise PreparationContextError("candidate_directory cannot designate generated artifacts or application history")
    bank = context.evidence_bank
    if bank.suffix.lower() not in {".yaml", ".yml"} or bank.is_relative_to(candidate):
        raise PreparationContextError("evidence_bank must be YAML outside the immutable candidate directory")
    profiles = _mapping(preparation["profile_sources"], {"preferred", "fallback", "supplements"}, "profile_sources")
    for name, values in profiles.items():
        if not isinstance(values, list) or (name != "supplements" and not values):
            raise PreparationContextError("profile source alternatives require nonempty lists; supplements require a list")
        seen_profiles = set()
        for value in values:
            path = context.contained_path(value)
            if path.parent != candidate or path.suffix.lower() != ".md" or any(char in value for char in "?[]") or (name != "supplements" and "*" in value):
                raise PreparationContextError("profile sources must be direct candidate Markdown paths; supplements allow basename stars")
            if value.casefold() in seen_profiles:
                raise PreparationContextError("duplicate profile source")
            seen_profiles.add(value.casefold())
    sources = preparation["career_sources"]
    if not isinstance(sources, list) or not sources:
        raise PreparationContextError("career_sources requires a nonempty list")
    source_paths = set()
    for source in sources:
        _mapping(source, {"path", "section"}, "career source")
        path = context.source_path(source["path"])
        _text(source["section"], "career source section")
        if path in source_paths:
            raise PreparationContextError("duplicate career source")
        source_paths.add(path)
    aliases = preparation["employer_aliases"]
    if not isinstance(aliases, dict):
        raise PreparationContextError("employer_aliases must be a mapping")
    seen_aliases = {}
    for employer, values in aliases.items():
        _text(employer, "alias employer")
        if not isinstance(values, list) or not values:
            raise PreparationContextError("employer aliases require a nonempty list")
        for value in [employer, *values]:
            folded = _text(value, "employer alias").casefold()
            if folded in seen_aliases and seen_aliases[folded] != employer:
                raise PreparationContextError("employer aliases must resolve uniquely")
            seen_aliases[folded] = employer
        if len({value.casefold() for value in values}) != len(values):
            raise PreparationContextError("duplicate employer alias")
    scope = _mapping(preparation["career_scope"], {"first_employer", "maximum_years_since_end"}, "career_scope")
    if scope["first_employer"] is not None:
        _text(scope["first_employer"], "first_employer")
    years = scope["maximum_years_since_end"]
    if type(years) is not int or not 1 <= years <= 100:
        raise PreparationContextError("maximum_years_since_end requires an integer from 1 to 100")
    clarifications = preparation["career_clarifications"]
    if not isinstance(clarifications, list):
        raise PreparationContextError("career_clarifications must be a list")
    seen = set()
    for clarification in clarifications:
        _mapping(clarification, {"employer", "reviewed", "sources", "corrections"}, "career clarification")
        employer = _text(clarification["employer"], "clarification employer")
        if employer.casefold() in seen:
            raise PreparationContextError("duplicate career clarification employer")
        seen.add(employer.casefold())
        reviewed = _mapping(clarification["reviewed"], {"reviewer", "reason"}, "clarification reviewed")
        for name, value in reviewed.items():
            _text(value, f"clarification {name}")
        records = clarification["sources"]
        if not isinstance(records, list) or not records:
            raise PreparationContextError("career clarification requires source records")
        for source in records:
            if not isinstance(source, dict) or set(source) - {"path", "sha256", "quote", "context_quote"} or {"path", "sha256", "quote"} - set(source):
                raise PreparationContextError("invalid career clarification source")
            context.source_path(source["path"])
            if not re.fullmatch(r"[0-9a-f]{64}", _text(source["sha256"], "clarification source hash")):
                raise PreparationContextError("clarification source requires a SHA-256 hash")
            _text(source["quote"], "clarification source quote")
            if "context_quote" in source:
                _text(source["context_quote"], "clarification source context")
        corrections = clarification["corrections"]
        if not isinstance(corrections, dict) or not corrections or set(corrections) - {"start", "end"}:
            raise PreparationContextError("clarification corrections require start and/or end")
        for correction in corrections.values():
            if not isinstance(correction, dict) or set(correction) - {"value", "precision", "source", "uncertainty_source"} or {"value", "precision", "source"} - set(correction):
                raise PreparationContextError("invalid career date correction")
            _text(correction["value"], "corrected date")
            if correction["precision"] not in {"year", "month"}:
                raise PreparationContextError("corrected date precision must be year or month")
            for name in ("source", "uncertainty_source"):
                if name in correction and (type(correction[name]) is not int or not 0 <= correction[name] < len(records)):
                    raise PreparationContextError("correction source must identify a source record")
    for voice in voices:
        if not Path(voice).is_absolute() and not PureWindowsPath(voice).is_absolute():
            context.contained_path(voice)
    return context
