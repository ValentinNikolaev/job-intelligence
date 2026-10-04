"""Local wall-clock timing for Codex preparation, kept outside the repository."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, TypeVar

T = TypeVar("T")
MODEL_STAGES = {"analysis", "editorial_drafting", "visual_review", "finalization"}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _stamp(value: datetime) -> str:
    return value.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _base(root: Path) -> Path:
    return Path(root).resolve() / ".codex-work" / "preparation-timing"


def record_event(root: Path, stage: str, started_at: datetime, elapsed_seconds: float,
                 *, vacancy: str | None = None, status: str = "ok") -> dict[str, object]:
    if not stage or elapsed_seconds < 0:
        raise ValueError("timing stage and nonnegative elapsed seconds are required")
    event: dict[str, object] = {
        "stage": stage, "vacancy": vacancy, "started_at": _stamp(started_at),
        "finished_at": _stamp(_now()), "elapsed_seconds": round(elapsed_seconds, 3),
        "status": status,
    }
    directory = _base(root) / "events"
    directory.mkdir(parents=True, exist_ok=True)
    target = directory / f"{uuid.uuid4().hex}.json"
    temporary = directory / f".{target.name}.tmp"
    temporary.write_text(json.dumps(event, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    return event


def timed_call(root: Path, stage: str, vacancy: str | None, call: Callable[[], T]) -> T:
    started_at, tick = _now(), time.perf_counter()
    status = "error"
    try:
        result = call()
        status = "ok" if not isinstance(result, int) or result == 0 else "error"
        return result
    finally:
        record_event(root, stage, started_at, time.perf_counter() - tick,
                     vacancy=vacancy, status=status)


def report(root: Path) -> dict[str, object]:
    events = [json.loads(path.read_text(encoding="utf-8"))
              for path in sorted((_base(root) / "events").glob("*.json"))]
    events.sort(key=lambda event: (event["started_at"], event["stage"]))
    totals: dict[str, float] = {}
    for event in events:
        key = f"{event['vacancy'] or 'shared'}:{event['stage']}"
        totals[key] = round(totals.get(key, 0.0) + event["elapsed_seconds"], 3)
    result: dict[str, object] = {"schema_version": 1, "events": events, "totals_seconds": totals}
    target = Path(root).resolve() / ".codex-work" / "preparation-timing.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)
    return result


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run.py timing")
    parser.add_argument("action", choices=("start", "stop", "report"))
    parser.add_argument("stage", nargs="?", choices=sorted(MODEL_STAGES))
    parser.add_argument("--vacancy", help="selected vacancy ID or directory; omit for shared work")
    args = parser.parse_args(argv)
    project_root = Path(root or Path.cwd())
    if args.action == "report":
        if args.stage or args.vacancy:
            parser.error("report does not accept a stage or vacancy")
        summary = report(project_root)
        print(json.dumps({"path": str(project_root.resolve() / ".codex-work" / "preparation-timing.json"),
                          "event_count": len(summary["events"]),
                          "totals_seconds": summary["totals_seconds"]},
                         ensure_ascii=False, sort_keys=True))
        return 0
    if not args.stage:
        parser.error("start and stop require a stage")
    marker_name = hashlib.sha256(f"{args.stage}:{args.vacancy or ''}".encode()).hexdigest()[:20]
    marker = _base(project_root) / "active" / f"{marker_name}.json"
    marker.parent.mkdir(parents=True, exist_ok=True)
    if args.action == "start":
        try:
            with marker.open("x", encoding="utf-8") as handle:
                json.dump({"stage": args.stage, "vacancy": args.vacancy,
                           "started_at": _stamp(_now())}, handle)
        except FileExistsError:
            print("Timing stage is already active", file=sys.stderr)
            return 1
        print(str(marker))
        return 0
    if not marker.is_file():
        print("Timing stage was not started", file=sys.stderr)
        return 1
    started = json.loads(marker.read_text(encoding="utf-8"))
    started_at = datetime.fromisoformat(started["started_at"].replace("Z", "+00:00"))
    elapsed = (_now() - started_at).total_seconds()
    event = record_event(project_root, args.stage, started_at, elapsed, vacancy=args.vacancy)
    marker.unlink()
    print(json.dumps(event, ensure_ascii=False, sort_keys=True))
    return 0
