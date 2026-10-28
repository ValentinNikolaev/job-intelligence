"""Strict, immutable configuration for deterministic vacancy selection."""
from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import yaml
from yaml.nodes import MappingNode, Node, ScalarNode, SequenceNode


# These are recognizer capabilities, not a candidate's selected policy or defaults.
ROLE_IDS = frozenset({"qa", "mobile"})
TECHNOLOGY_IDS = frozenset({"go", "php", "python", "r", "julia", "spring_boot"})
CMS_IDS = frozenset({"typo3", "wordpress", "drupal"})
LANGUAGE_IDS = frozenset({
    "albanian", "bulgarian", "croatian", "czech", "danish", "dutch", "estonian",
    "finnish", "french", "german", "greek", "hungarian", "italian", "latvian",
    "lithuanian", "norwegian", "polish", "portuguese", "romanian", "serbian",
    "slovak", "slovenian", "spanish", "swedish", "turkish",
})
TRIAGE_IDS = frozenset({"sales", "qa", "mobile", "junior", "sre", "consulting", "non_backend"})
DEFAULT_SELECTION_POLICY_PATH = Path(__file__).resolve().parents[1] / "config/selection-policy.yaml"


class SelectionPolicyError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class LocationPolicy:
    hybrid_italy_only: bool
    reject_us_remote: bool
    reject_us_location: bool
    reject_american_timezones: bool
    reject_american_location: bool
    allow_european_exception: bool


@dataclass(frozen=True, slots=True)
class SelectionPolicy:
    schema_version: int
    max_age_days: int
    excluded_roles: tuple[str, ...]
    reject_explicit_non_remote: bool
    target_technologies: tuple[str, ...]
    excluded_cms: tuple[str, ...]
    excluded_technologies: tuple[str, ...]
    excluded_combinations: tuple[tuple[str, ...], ...]
    blocking_languages: tuple[str, ...]
    location: LocationPolicy
    triage_exclusions: tuple[str, ...]

    def fingerprint(self) -> str:
        return _digest(asdict(self))

    def prefilter_fingerprint(self) -> str:
        values = asdict(self)
        del values["triage_exclusions"]
        return _digest(values)

    def triage_fingerprint(self) -> str:
        return _digest({"schema_version": self.schema_version, "triage_exclusions": self.triage_exclusions})


def _digest(value: Any) -> str:
    canonical = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def load_selection_policy(path: Path) -> SelectionPolicy:
    """Load exactly this file; callers own project-root/path resolution. No fallback."""
    path = Path(path)

    def fail(field: str, message: str) -> None:
        raise SelectionPolicyError(f"{path}: {field}: {message}")

    def check_yaml(node: Node, field: str, ancestors: frozenset[int] = frozenset()) -> None:
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
                check_yaml(value, child, ancestors)
        elif isinstance(node, SequenceNode):
            for index, item in enumerate(node.value):
                check_yaml(item, f"{field}[{index}]", ancestors)

    try:
        text = path.read_text(encoding="utf-8-sig")
        node = yaml.compose(text, Loader=yaml.SafeLoader)
        if node is not None:
            check_yaml(node, "$")
        raw = yaml.safe_load(text)
    except OSError as exc:
        fail("$", f"cannot read policy ({exc.__class__.__name__})")
    except UnicodeError:
        fail("$", "policy must be UTF-8 text")
    except yaml.YAMLError as exc:
        mark = getattr(exc, "problem_mark", None)
        location = f" at line {mark.line + 1}, column {mark.column + 1}" if mark is not None else ""
        fail("$", f"malformed or unsupported YAML{location}")

    def mapping(value: Any, fields: set[str], field: str) -> dict[str, Any]:
        if not isinstance(value, dict):
            fail(field, "must be a mapping")
        unknown = set(value) - fields
        if unknown:
            fail(field, "unknown fields: " + ", ".join(sorted(unknown)))
        missing = fields - set(value)
        if missing:
            fail(field, "missing required fields: " + ", ".join(sorted(missing)))
        return value

    def boolean(value: Any, field: str) -> bool:
        if type(value) is not bool:
            fail(field, "must be a boolean")
        return value

    def identifiers(value: Any, allowed: frozenset[str], field: str, *, nonempty: bool = False) -> tuple[str, ...]:
        if not isinstance(value, list) or (nonempty and not value):
            fail(field, "must be a nonempty list" if nonempty else "must be a list")
        result = []
        for index, item in enumerate(value):
            if type(item) is not str or item not in allowed:
                fail(f"{field}[{index}]", "unsupported identifier; supported: " + ", ".join(sorted(allowed)))
            if item in result:
                fail(f"{field}[{index}]", "duplicate identifier")
            result.append(item)
        return tuple(result)

    raw = mapping(raw, set(SelectionPolicy.__dataclass_fields__), "$")
    if type(raw["schema_version"]) is not int or raw["schema_version"] != 1:
        fail("schema_version", "must be supported integer version 1")
    if type(raw["max_age_days"]) is not int or raw["max_age_days"] < 1:
        fail("max_age_days", "must be a positive integer")
    location_raw = mapping(raw["location"], set(LocationPolicy.__dataclass_fields__), "location")
    location = LocationPolicy(**{key: boolean(value, f"location.{key}") for key, value in location_raw.items()})
    if location.allow_european_exception and not any((location.reject_us_remote, location.reject_us_location,
            location.reject_american_timezones, location.reject_american_location)):
        fail("location.allow_european_exception", "requires an enabled American location/time constraint")
    targets = identifiers(raw["target_technologies"], TECHNOLOGY_IDS, "target_technologies", nonempty=True)
    excluded = identifiers(raw["excluded_technologies"], TECHNOLOGY_IDS, "excluded_technologies")
    if set(targets) & set(excluded):
        fail("excluded_technologies", "must not also be target technologies")
    combinations_raw = raw["excluded_combinations"]
    if not isinstance(combinations_raw, list):
        fail("excluded_combinations", "must be a list")
    combinations = []
    seen_combinations = set()
    for index, value in enumerate(combinations_raw):
        field = f"excluded_combinations[{index}]"
        combination = identifiers(value, TECHNOLOGY_IDS, field)
        if len(combination) < 2:
            fail(field, "must contain at least two distinct technologies")
        if frozenset(combination) in seen_combinations:
            fail(field, "duplicate combination")
        if set(combination) & set(excluded):
            fail(field, "redundant combination contains an individually excluded technology")
        seen_combinations.add(frozenset(combination))
        combinations.append(combination)
    return SelectionPolicy(
        schema_version=raw["schema_version"], max_age_days=raw["max_age_days"],
        excluded_roles=identifiers(raw["excluded_roles"], ROLE_IDS, "excluded_roles"),
        reject_explicit_non_remote=boolean(raw["reject_explicit_non_remote"], "reject_explicit_non_remote"),
        target_technologies=targets, excluded_cms=identifiers(raw["excluded_cms"], CMS_IDS, "excluded_cms"),
        excluded_technologies=excluded, excluded_combinations=tuple(combinations),
        blocking_languages=identifiers(raw["blocking_languages"], LANGUAGE_IDS, "blocking_languages"),
        location=location, triage_exclusions=identifiers(raw["triage_exclusions"], TRIAGE_IDS, "triage_exclusions"),
    )
