from __future__ import annotations

import os
import uuid
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

from .normalization import slug


SCHEMA_VERSION = 1
DEFAULT_ACTOR = "codex"
DEFAULT_INTERACTION_SOURCE = "llm_assisted_manual"


class ManualStatusLogError(RuntimeError):
    pass


@dataclass(frozen=True, slots=True)
class ManualStatusEvent:
    changed_at: str
    vacancy_id: str
    directory: str
    company: str
    title: str
    from_status: str
    to_status: str
    reason: str
    actor: str = DEFAULT_ACTOR
    interaction_source: str = DEFAULT_INTERACTION_SOURCE
    interaction_id: str | None = None
    note: str | None = None

    def as_dict(self) -> dict[str, Any]:
        event: dict[str, Any] = {
            "changed_at": self.changed_at,
            "vacancy_id": self.vacancy_id,
            "directory": self.directory,
            "company": self.company,
            "title": self.title,
            "from_status": self.from_status,
            "to_status": self.to_status,
            "reason": self.reason,
            "reason_key": reason_key(self.reason),
            "actor": self.actor,
            "interaction": {"source": self.interaction_source},
        }
        if self.interaction_id:
            event["interaction"]["id"] = self.interaction_id
        if self.note:
            event["note"] = self.note
        return event


def append_manual_status_event(path: Path, event: ManualStatusEvent) -> dict[str, Any]:
    payload = _read_log(path)
    events = payload.get("events")
    if not isinstance(events, list):
        raise ManualStatusLogError(f"manual status log events must be a list: {path}")
    events.append(event.as_dict())
    payload = _with_summary(events)
    _write_atomic(path, _dump_yaml(payload))
    return payload


def reason_key(reason: str) -> str:
    key = slug(reason)
    return key or "unspecified"


def _read_log(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return _with_summary([])
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ManualStatusLogError(f"cannot read manual status log {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ManualStatusLogError(f"manual status log must be a YAML mapping: {path}")
    if loaded.get("schema_version") != SCHEMA_VERSION:
        raise ManualStatusLogError(
            f"unsupported manual status log schema {loaded.get('schema_version')!r}: {path}"
        )
    events = loaded.get("events")
    if not isinstance(events, list):
        raise ManualStatusLogError(f"manual status log events must be a list: {path}")
    return _with_summary(events)


def _with_summary(events: list[Any]) -> dict[str, Any]:
    normalized_events = [_event_mapping(event) for event in events]
    by_status: dict[str, dict[str, Any]] = {}
    by_reason: dict[str, dict[str, Any]] = {}
    status_counter = Counter(str(event.get("to_status") or "") for event in normalized_events)
    reason_rows: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for event in normalized_events:
        reason_rows[str(event.get("reason_key") or "unspecified")].append(event)
    for status, count in sorted(status_counter.items()):
        if not status:
            continue
        rows = [event for event in normalized_events if event.get("to_status") == status]
        by_status[status] = {
            "count": count,
            "last_changed_at": rows[-1].get("changed_at") if rows else None,
        }
    for key, rows in sorted(reason_rows.items()):
        by_reason[key] = {
            "count": len(rows),
            "reason": rows[-1].get("reason") or key,
            "last_changed_at": rows[-1].get("changed_at"),
        }
    return {
        "schema_version": SCHEMA_VERSION,
        "description": (
            "Append-only audit log for manual vacancy status decisions made through "
            "user/LLM interaction. Automated collection and prefilter rejections are "
            "tracked elsewhere."
        ),
        "summary": {
            "total_events": len(normalized_events),
            "by_status": by_status,
            "by_reason": by_reason,
        },
        "events": normalized_events,
    }


def _event_mapping(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ManualStatusLogError("manual status log event must be a YAML mapping")
    event = dict(value)
    event["reason"] = str(event.get("reason") or "unspecified").strip() or "unspecified"
    event["reason_key"] = str(event.get("reason_key") or reason_key(event["reason"]))
    return event


def _dump_yaml(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _write_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
