from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml


class UsageError(RuntimeError):
    pass


class CodexUsageLog:
    """Append one externally reported or locally estimated Codex run."""

    def __init__(self, path: Path) -> None:
        self.path = path.resolve()

    def record(
        self,
        *,
        workflow: str,
        model: str,
        status: str = "completed",
        run_id: str | None = None,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
        credits: float | None = None,
        measurement: str = "reported",
        selected: int | None = None,
        batch_size: int | None = None,
        note: str | None = None,
    ) -> dict[str, Any]:
        workflow = workflow.replace("-", "_").strip()
        if not workflow:
            raise UsageError("workflow is required")
        if not model.strip():
            raise UsageError("model is required")
        if measurement not in {"reported", "estimated"}:
            raise UsageError("measurement must be reported or estimated")
        values = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "selected": selected,
            "batch_size": batch_size,
        }
        for field, value in values.items():
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise UsageError(f"{field} must be a non-negative integer")
        if credits is not None and (isinstance(credits, bool) or not isinstance(credits, (int, float)) or credits < 0):
            raise UsageError("credits must be a non-negative number")
        if total_tokens is None and input_tokens is not None and output_tokens is not None:
            total_tokens = input_tokens + output_tokens
        run = {
            "run_id": run_id.strip() if run_id and run_id.strip() else uuid.uuid4().hex,
            "recorded_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
            "workflow": workflow,
            "model": model.strip(),
            "status": status.strip() or "completed",
            "measurement": measurement,
        }
        for field, value in (
            ("input_tokens", input_tokens),
            ("output_tokens", output_tokens),
            ("total_tokens", total_tokens),
            ("credits", credits),
            ("selected", selected),
            ("batch_size", batch_size),
        ):
            if value is not None:
                run[field] = value
        if note and note.strip():
            run["note"] = note.strip()
        payload = self._load()
        payload["runs"].append(run)
        self._write(payload)
        return run

    def _load(self) -> dict[str, Any]:
        if not self.path.is_file():
            return {"schema_version": 1, "runs": []}
        try:
            loaded = yaml.safe_load(self.path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError) as exc:
            raise UsageError(f"cannot read Codex usage log {self.path}: {exc}") from exc
        if not isinstance(loaded, dict) or not isinstance(loaded.get("runs"), list):
            raise UsageError(f"Codex usage log must contain a runs list: {self.path}")
        loaded.setdefault("schema_version", 1)
        return loaded

    def _write(self, payload: dict[str, Any]) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp = self.path.with_name(f".{self.path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temp.write_text(yaml.safe_dump(payload, allow_unicode=True, sort_keys=False), encoding="utf-8", newline="\n")
            os.replace(temp, self.path)
        finally:
            if temp.exists():
                temp.unlink()
