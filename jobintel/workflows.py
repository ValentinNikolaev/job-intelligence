from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class WorkflowError(RuntimeError):
    pass


MAX_PREPARATION_BATCH_SIZE = 10


@dataclass(frozen=True, slots=True)
class ModelProfile:
    name: str
    model: str
    reasoning: str
    model_label: str


@dataclass(frozen=True, slots=True)
class Workflow:
    name: str
    model: str
    reasoning: str
    model_label: str
    default_profile: str
    allowed_profiles: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class WorkflowPolicy:
    prepare_min_score: int
    prepare_max_age_days: int
    workflows: dict[str, Workflow]
    prepare_batch_size: int = 1
    model_profiles: dict[str, ModelProfile] | None = None

    def workflow(self, name: str) -> Workflow:
        canonical = name.strip().casefold().replace("-", "_")
        try:
            return self.workflows[canonical]
        except KeyError as exc:
            choices = ", ".join(sorted(key.replace("_", "-") for key in self.workflows))
            raise WorkflowError(f"unknown workflow {name!r}; expected one of: {choices}") from exc

    def prepare_score_is_eligible(self, workflow: str, score: int) -> bool:
        canonical = workflow.strip().casefold().replace("-", "_")
        if canonical == "prepare":
            return self.prepare_min_score <= score <= 100
        raise WorkflowError(f"workflow {workflow!r} is not a preparation workflow")

    def resolve_model_profile(self, workflow: str, profile: str | None = None) -> ModelProfile:
        selected_workflow = self.workflow(workflow)
        profiles = self.model_profiles or {}
        requested = (profile or selected_workflow.default_profile).strip().casefold().replace("-", "_")
        allowed = set(selected_workflow.allowed_profiles)
        if requested not in allowed:
            choices = ", ".join(sorted(allowed))
            raise WorkflowError(
                f"model profile {profile!r} is not allowed for workflow {selected_workflow.name!r}; "
                f"expected one of: {choices}"
            )
        try:
            return profiles[requested]
        except KeyError as exc:
            raise WorkflowError(f"unknown model profile {requested!r}") from exc


def load_workflow_policy(path: Path) -> WorkflowPolicy:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise WorkflowError(f"cannot read workflow policy {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise WorkflowError(f"invalid workflow policy YAML {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise WorkflowError(f"workflow policy must be a YAML mapping: {path}")
    if loaded.get("schema_version") != 1:
        raise WorkflowError(f"unsupported workflow policy schema: {loaded.get('schema_version')!r}")

    prepare_min = _score(loaded.get("prepare_min_score"), "prepare_min_score")
    prepare_max_age_days = _positive_int(loaded.get("prepare_max_age_days", 7), "prepare_max_age_days")
    prepare_batch_size = _positive_int(
        loaded.get("prepare_batch_size", 1), "prepare_batch_size"
    )
    if prepare_batch_size > MAX_PREPARATION_BATCH_SIZE:
        raise WorkflowError(
            "prepare_batch_size must not exceed "
            f"{MAX_PREPARATION_BATCH_SIZE} vacancies per Codex task"
        )

    model_profiles = _load_model_profiles(loaded.get("model_profiles"))
    raw_workflows = loaded.get("workflows")
    if not isinstance(raw_workflows, dict):
        raise WorkflowError("workflows must be a YAML mapping")
    workflows: dict[str, Workflow] = {}
    for name in ("analyze", "prepare"):
        raw = raw_workflows.get(name)
        if not isinstance(raw, dict):
            raise WorkflowError(f"workflow {name!r} must be a YAML mapping")
        default_profile = _optional_name(raw.get("default_profile"))
        if default_profile is None:
            values: dict[str, str] = {}
            for field in ("model", "reasoning", "model_label"):
                value = raw.get(field)
                if not isinstance(value, str) or not value.strip():
                    raise WorkflowError(f"workflow {name!r} has invalid {field}")
                values[field] = value.strip()
            default_profile = name
            model_profiles.setdefault(
                default_profile,
                ModelProfile(default_profile, values["model"], values["reasoning"], values["model_label"]),
            )
        if default_profile not in model_profiles:
            raise WorkflowError(f"workflow {name!r} references unknown default_profile {default_profile!r}")
        raw_allowed = raw.get("allowed_profiles", [default_profile])
        if not isinstance(raw_allowed, list) or not raw_allowed:
            raise WorkflowError(f"workflow {name!r} has invalid allowed_profiles")
        allowed_profiles = tuple(_required_name(value, f"workflow {name!r} allowed profile") for value in raw_allowed)
        for profile in allowed_profiles:
            if profile not in model_profiles:
                raise WorkflowError(f"workflow {name!r} references unknown model profile {profile!r}")
        selected_profile = model_profiles[default_profile]
        workflows[name] = Workflow(
            name,
            selected_profile.model,
            selected_profile.reasoning,
            selected_profile.model_label,
            default_profile,
            allowed_profiles,
        )
    return WorkflowPolicy(
        prepare_min,
        prepare_max_age_days,
        workflows,
        prepare_batch_size,
        model_profiles,
    )


def _load_model_profiles(raw_profiles: Any) -> dict[str, ModelProfile]:
    if raw_profiles is None:
        return {}
    if not isinstance(raw_profiles, dict):
        raise WorkflowError("model_profiles must be a YAML mapping")
    profiles: dict[str, ModelProfile] = {}
    for raw_name, raw in raw_profiles.items():
        name = _required_name(raw_name, "model profile")
        if not isinstance(raw, dict):
            raise WorkflowError(f"model profile {name!r} must be a YAML mapping")
        values: dict[str, str] = {}
        for field in ("model", "reasoning", "model_label"):
            value = raw.get(field)
            if not isinstance(value, str) or not value.strip():
                raise WorkflowError(f"model profile {name!r} has invalid {field}")
            values[field] = value.strip()
        profiles[name] = ModelProfile(name, values["model"], values["reasoning"], values["model_label"])
    return profiles


def _optional_name(value: Any) -> str | None:
    if value is None:
        return None
    return _required_name(value, "name")


def _required_name(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise WorkflowError(f"{field} must be a non-empty string")
    return value.strip().casefold().replace("-", "_")


def _score(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise WorkflowError(f"{field} must be an integer from 0 to 100")
    return value


def _positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise WorkflowError(f"{field} must be a positive integer")
    return value
