"""Validated qualitative analysis preferences and runtime effective-input identity."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Mapping

import yaml
from yaml.nodes import MappingNode, ScalarNode, SequenceNode


DEFAULT_PROJECT_ROOT = Path(__file__).resolve().parents[1]
TECHNOLOGIES = frozenset({"go", "php", "python", "r", "julia", "spring_boot", "aspnet"})
ROLES = frozenset({"sre"})
DOMAINS = frozenset({"support_automation", "email", "support"})


def canonical(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


class MatchingPolicyError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class MatchingPolicy:
    schema_version: int
    prefer_remote: bool
    preferred_technologies: tuple[str, ...]
    discouraged_core_technologies: tuple[str, ...]
    discouraged_roles: tuple[str, ...]
    prefer_relocation_package: bool
    preferred_cities: tuple[str, ...]
    preferred_domains: tuple[str, ...]
    block_us_work_requirements: bool
    allow_european_or_candidate_local_hours: bool

    def canonical_analysis_snapshot(self) -> dict[str, Any]:
        return json.loads(canonical(asdict(self)))

    def fingerprint(self) -> str:
        return digest(self.canonical_analysis_snapshot())


@dataclass(frozen=True, slots=True)
class MatchingContext:
    policy: MatchingPolicy
    prompt: str
    schema_json: str

    @property
    def prompt_version(self) -> str:
        inputs = {"prompt": self.prompt, "schema": json.loads(self.schema_json),
                  "policy": self.policy.canonical_analysis_snapshot()}
        return "job-match-v2:sha256:" + digest(inputs)


def load_matching_policy(path: Path) -> MatchingPolicy:
    path = Path(path)

    def fail(field: str, message: str) -> None:
        raise MatchingPolicyError(f"{path}: {field}: {message}")

    def check(node, field="$", ancestors=frozenset()):
        if id(node) in ancestors:
            fail(field, "recursive YAML aliases are unsupported")
        ancestors = ancestors | {id(node)}
        if isinstance(node, MappingNode):
            seen = set()
            for key, value in node.value:
                if not isinstance(key, ScalarNode) or key.tag != "tag:yaml.org,2002:str":
                    fail(field, "mapping keys must be text")
                child = key.value if field == "$" else f"{field}.{key.value}"
                if key.value in seen:
                    fail(child, "duplicate YAML key")
                seen.add(key.value)
                check(value, child, ancestors)
        elif isinstance(node, SequenceNode):
            for index, value in enumerate(node.value):
                check(value, f"{field}[{index}]", ancestors)

    try:
        text = path.read_text(encoding="utf-8-sig")
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            check(node)
        raw = yaml.safe_load(text)
    except (OSError, UnicodeError) as exc:
        fail("$", f"cannot read UTF-8 policy ({type(exc).__name__})")
    except yaml.YAMLError:
        fail("$", "malformed or unsupported YAML")
    if not isinstance(raw, dict):
        fail("$", "must be a mapping")
    fields = set(MatchingPolicy.__dataclass_fields__)
    if set(raw) - fields:
        fail("$", "unknown fields: " + ", ".join(sorted(set(raw) - fields)))
    if fields - set(raw):
        fail("$", "missing required fields: " + ", ".join(sorted(fields - set(raw))))
    if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
        fail("schema_version", "must be supported integer version 1")
    values = {"schema_version": 1}
    for name in ("prefer_remote", "prefer_relocation_package", "block_us_work_requirements", "allow_european_or_candidate_local_hours"):
        if type(raw[name]) is not bool:
            fail(name, "must be a boolean")
        values[name] = raw[name]
    for name, supported in (("preferred_technologies", TECHNOLOGIES), ("discouraged_core_technologies", TECHNOLOGIES),
                            ("discouraged_roles", ROLES), ("preferred_domains", DOMAINS), ("preferred_cities", None)):
        value = raw[name]
        if not isinstance(value, list):
            fail(name, "must be a list")
        seen = set()
        for index, item in enumerate(value):
            if type(item) is not str or not item.strip() or item != item.strip() or (supported is not None and item not in supported):
                fail(f"{name}[{index}]", "must be a supported nonempty identifier or city")
            if item in seen:
                fail(f"{name}[{index}]", "duplicate value")
            seen.add(item)
        values[name] = tuple(value)
    if set(values["preferred_technologies"]) & set(values["discouraged_core_technologies"]):
        fail("discouraged_core_technologies", "cannot also be preferred technologies")
    if values["allow_european_or_candidate_local_hours"] and not values["block_us_work_requirements"]:
        fail("allow_european_or_candidate_local_hours", "requires block_us_work_requirements")
    return MatchingPolicy(**values)


def load_matching_context(project_root: Path = DEFAULT_PROJECT_ROOT, *, output_schema: Mapping[str, Any]) -> MatchingContext:
    policy = load_matching_policy(project_root / "config/matching-policy.yaml")
    path = project_root / "prompts/vacancy-match.md"
    try:
        prompt = path.read_text(encoding="utf-8-sig").strip()
    except (OSError, UnicodeError) as exc:
        raise MatchingPolicyError(f"{path}: $: cannot read UTF-8 prompt ({type(exc).__name__})") from exc
    if not prompt:
        raise MatchingPolicyError(f"{path}: $: prompt must not be empty")
    return MatchingContext(policy, prompt, canonical(output_schema))
