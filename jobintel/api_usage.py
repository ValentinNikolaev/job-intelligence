from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from .models import CollectorSummary


SCHEMA_VERSION = 1


class ApiUsageLog:
    def __init__(self, path: Path) -> None:
        self.path = path

    def record(self, summary: CollectorSummary, *, run_started_at: str | None = None) -> None:
        if summary.api_requests <= 0:
            return
        data = self._load()
        sources = data.setdefault("sources", {})
        if not isinstance(sources, dict):
            sources = {}
            data["sources"] = sources
        source = sources.setdefault(summary.source, {})
        if not isinstance(source, dict):
            source = {}
            sources[summary.source] = source

        previous_total = _non_negative_int(source.get("total_requests"))
        source["total_requests"] = previous_total + summary.api_requests
        source["last_run_at"] = _utc_now()
        source["last_status"] = "failed" if summary.errors else "completed"
        runs = source.setdefault("runs", [])
        if not isinstance(runs, list):
            runs = []
            source["runs"] = runs
        runs.append(
            {
                "run_started_at": run_started_at or source["last_run_at"],
                "recorded_at": source["last_run_at"],
                "requests": summary.api_requests,
                "fetched": summary.fetched,
                "created": summary.created,
                "updated": summary.updated,
                "duplicates_merged": summary.merged,
                "unchanged": summary.unchanged,
                "rejected": summary.rejected,
                "errors": summary.errors,
                "limit_reached": summary.limit_reached,
            }
        )
        _write_atomic(self.path, _dump(data))

    def _load(self) -> dict[str, Any]:
        if not self.path.exists():
            return {"schema_version": SCHEMA_VERSION, "sources": {}}
        try:
            loaded = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise ValueError(f"cannot read API usage log {self.path}: {exc}") from exc
        if loaded is None:
            return {"schema_version": SCHEMA_VERSION, "sources": {}}
        if not isinstance(loaded, dict):
            raise ValueError(f"API usage log must be a YAML mapping: {self.path}")
        loaded.setdefault("schema_version", SCHEMA_VERSION)
        loaded.setdefault("sources", {})
        return loaded


def _non_negative_int(value: Any) -> int:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else 0


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _dump(value: dict[str, Any]) -> str:
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
