from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlparse


OUTBOX_SCHEMA_VERSION = 1
TELEGRAM_ANALYSIS_INITIATOR = "job-intelligence-batch-vacancy-analysis"


class TelegramOutboxError(RuntimeError):
    pass


def build_analysis_notification(
    pack: Mapping[str, Any],
    results: Mapping[str, Any],
    *,
    minimum_score: int,
    clock: Callable[[], datetime] | None = None,
) -> dict[str, Any] | None:
    items = pack.get("items")
    if not isinstance(items, list):
        raise TelegramOutboxError("analysis pack requires an items list")
    if set(results) != {
        str(item.get("directory", "")) for item in items if isinstance(item, Mapping)
    }:
        raise TelegramOutboxError(
            "analysis notification results must match the analysis pack directories"
        )
    if isinstance(minimum_score, bool) or not isinstance(minimum_score, int):
        raise TelegramOutboxError("minimum score must be an integer")

    eligible: list[dict[str, Any]] = []
    for item in items:
        if not isinstance(item, Mapping):
            raise TelegramOutboxError("analysis pack item must be a mapping")
        directory = _required_text(item.get("directory"), "directory")
        result = results.get(directory)
        if not isinstance(result, Mapping):
            raise TelegramOutboxError(f"analysis result must be a mapping: {directory}")
        score = result.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
            raise TelegramOutboxError(f"analysis result has an invalid score: {directory}")
        hard_rejection = result.get("hard_rejection")
        if not isinstance(hard_rejection, bool):
            raise TelegramOutboxError(
                f"analysis result has an invalid hard_rejection flag: {directory}"
            )
        if score < minimum_score or hard_rejection:
            continue

        vacancy = item.get("vacancy")
        if not isinstance(vacancy, Mapping):
            raise TelegramOutboxError(f"analysis pack vacancy must be a mapping: {directory}")
        metadata = vacancy.get("metadata", vacancy)
        if not isinstance(metadata, Mapping):
            raise TelegramOutboxError(f"analysis pack vacancy metadata must be a mapping: {directory}")
        source_url = _required_http_url(item.get("source_url"), f"source URL for {directory}")
        eligible.append(
            {
                "company": _required_text(metadata.get("company"), f"company for {directory}"),
                "title": _required_text(metadata.get("title"), f"title for {directory}"),
                "score": score,
                "vacancy_id": _required_text(
                    item.get("vacancy_id"), f"vacancy ID for {directory}"
                ),
                "directory": directory,
                "url": source_url,
            }
        )

    if not eligible:
        return None

    payload = {
        "schema_version": OUTBOX_SCHEMA_VERSION,
        "channel": "telegram",
        "initiator": TELEGRAM_ANALYSIS_INITIATOR,
        "minimum_score": minimum_score,
        "items": eligible,
    }
    notification_id = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    now = (clock or (lambda: datetime.now(timezone.utc)))()
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    return {
        **payload,
        "notification_id": notification_id,
        "created_at": now.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        ),
    }


def enqueue_notification(project_root: Path, notification: Mapping[str, Any]) -> Path:
    validated = validate_notification(notification)
    notification_id = str(validated["notification_id"])
    root = project_root / "notifications" / "telegram"
    outbox_path = root / "outbox" / f"{notification_id}.json"
    sent_path = root / "sent" / f"{notification_id}.json"
    if sent_path.is_file():
        return sent_path
    outbox_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(validated, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if outbox_path.is_file():
        if outbox_path.read_text(encoding="utf-8") != content:
            raise TelegramOutboxError(f"notification ID collision: {notification_id}")
        return outbox_path
    temporary = outbox_path.with_name(f".{outbox_path.name}.{os.getpid()}.tmp")
    temporary.write_text(content, encoding="utf-8")
    os.replace(temporary, outbox_path)
    return outbox_path


def load_notification(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise TelegramOutboxError(f"cannot read Telegram outbox file {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise TelegramOutboxError(f"invalid Telegram outbox JSON {path}: {exc}") from exc
    return validate_notification(value)


def validate_notification(value: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(value, Mapping):
        raise TelegramOutboxError("Telegram notification must be a mapping")
    expected = {
        "schema_version",
        "channel",
        "initiator",
        "minimum_score",
        "notification_id",
        "created_at",
        "items",
    }
    if set(value) != expected:
        raise TelegramOutboxError("Telegram notification has invalid fields")
    if value.get("schema_version") != OUTBOX_SCHEMA_VERSION:
        raise TelegramOutboxError("unsupported Telegram outbox schema")
    if value.get("channel") != "telegram":
        raise TelegramOutboxError("Telegram outbox channel must be telegram")
    initiator = _required_text(value.get("initiator"), "initiator")
    minimum_score = value.get("minimum_score")
    if isinstance(minimum_score, bool) or not isinstance(minimum_score, int):
        raise TelegramOutboxError("minimum score must be an integer")
    created_at = _required_text(value.get("created_at"), "created_at")
    notification_id = _required_text(value.get("notification_id"), "notification_id")
    if len(notification_id) != 64 or any(character not in "0123456789abcdef" for character in notification_id):
        raise TelegramOutboxError("notification ID must be a lowercase SHA-256 digest")
    raw_items = value.get("items")
    if not isinstance(raw_items, list) or not raw_items:
        raise TelegramOutboxError("Telegram notification requires at least one item")
    items = []
    for index, raw in enumerate(raw_items):
        if not isinstance(raw, Mapping) or set(raw) != {
            "company",
            "title",
            "score",
            "vacancy_id",
            "directory",
            "url",
        }:
            raise TelegramOutboxError(f"Telegram notification item {index} has invalid fields")
        score = raw.get("score")
        if isinstance(score, bool) or not isinstance(score, int) or not minimum_score <= score <= 100:
            raise TelegramOutboxError(f"Telegram notification item {index} has an invalid score")
        items.append(
            {
                "company": _required_text(raw.get("company"), f"item {index} company"),
                "title": _required_text(raw.get("title"), f"item {index} title"),
                "score": score,
                "vacancy_id": _required_text(raw.get("vacancy_id"), f"item {index} vacancy ID"),
                "directory": _required_text(raw.get("directory"), f"item {index} directory"),
                "url": _required_http_url(raw.get("url"), f"item {index} URL"),
            }
        )
    payload = {
        "schema_version": OUTBOX_SCHEMA_VERSION,
        "channel": "telegram",
        "initiator": initiator,
        "minimum_score": minimum_score,
        "items": items,
    }
    expected_id = hashlib.sha256(
        json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode(
            "utf-8"
        )
    ).hexdigest()
    if notification_id != expected_id:
        raise TelegramOutboxError("Telegram notification ID does not match its payload")
    return {
        **payload,
        "notification_id": notification_id,
        "created_at": created_at,
    }


def render_notification_message(notification: Mapping[str, Any]) -> str:
    validated = validate_notification(notification)
    lines = [f"Automation ID: {validated['initiator']}"]
    for item in validated["items"]:
        lines.extend(
            (
                "",
                f"{item['company']} — {item['title']}",
                f"Score: {item['score']}",
                f"Vacancy ID: {item['vacancy_id']}",
                f"Directory: {item['directory']}",
                f"URL: {item['url']}",
            )
        )
    return "\n".join(lines).strip()


def _required_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise TelegramOutboxError(f"{field} must be non-empty text")
    return value.strip()


def _required_http_url(value: Any, field: str) -> str:
    url = _required_text(value, field)
    parsed = urlparse(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise TelegramOutboxError(f"{field} must be an HTTP(S) URL")
    return url
