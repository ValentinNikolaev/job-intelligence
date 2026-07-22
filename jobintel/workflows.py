from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


class WorkflowError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class Workflow:
    name: str
    model: str
    reasoning: str
    model_label: str


@dataclass(frozen=True, slots=True)
class WorkflowPolicy:
    prepare_min_score: int
    priority_score: int
    workflows: dict[str, Workflow]

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
            return self.prepare_min_score <= score < self.priority_score
        if canonical == "prepare_priority":
            return self.priority_score <= score <= 100
        raise WorkflowError(f"workflow {workflow!r} is not a preparation workflow")


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
    priority = _score(loaded.get("priority_score"), "priority_score")
    if prepare_min >= priority:
        raise WorkflowError("prepare_min_score must be lower than priority_score")

    raw_workflows = loaded.get("workflows")
    if not isinstance(raw_workflows, dict):
        raise WorkflowError("workflows must be a YAML mapping")
    workflows: dict[str, Workflow] = {}
    for name in ("analyze", "prepare", "prepare_priority"):
        raw = raw_workflows.get(name)
        if not isinstance(raw, dict):
            raise WorkflowError(f"workflow {name!r} must be a YAML mapping")
        values: dict[str, str] = {}
        for field in ("model", "reasoning", "model_label"):
            value = raw.get(field)
            if not isinstance(value, str) or not value.strip():
                raise WorkflowError(f"workflow {name!r} has invalid {field}")
            values[field] = value.strip()
        workflows[name] = Workflow(name, values["model"], values["reasoning"], values["model_label"])
    return WorkflowPolicy(prepare_min, priority, workflows)


def _score(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise WorkflowError(f"{field} must be an integer from 0 to 100")
    return value
