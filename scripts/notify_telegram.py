from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import hashlib
from html import escape
import json
import os
import shutil
import sys
from pathlib import Path
import re

import yaml

from jobintel.config import load_env


TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
_LABEL_RE = re.compile(r"^(Automation ID|Score|Vacancy ID|Directory|URL):\s*(.*)$", re.IGNORECASE)
_MISSING_URLS = {"", "-", "—", "n/a", "none", "unknown", "unavailable"}
_VACANCY_ID_RE = re.compile(r"^\s*Vacancy ID:\s*(\S+)\s*$", re.IGNORECASE)
_URL_RE = re.compile(r"^\s*URL:\s*(.*)$", re.IGNORECASE)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send one Telegram notification asynchronously.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--message")
    source.add_argument("--message-file", type=Path)
    parser.add_argument(
        "--initiator",
        help="Automation ID to include in the Telegram message.",
    )
    return parser


def _default_env_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sources" / ".env"


def notification_config() -> tuple[str, str]:
    config = load_env(_default_env_path())
    return (
        config.get("TELEGRAM_BOT_TOKEN", "").strip(),
        config.get("TELEGRAM_CHAT_ID", "").strip(),
    )


def message_with_initiator(message: str, initiator: str | None) -> str:
    lines = message.strip().splitlines()
    while lines and (
        lines[0].startswith("Internal initiator:")
        or lines[0].startswith("Automation ID:")
    ):
        lines.pop(0)
    clean_message = "\n".join(lines).strip()
    clean_initiator = (initiator or "").strip()
    if not clean_initiator:
        return clean_message
    line = f"Automation ID: {clean_initiator}"
    return f"{line}\n{clean_message}" if clean_message else line


def enrich_vacancy_urls(message: str, registry_root: Path) -> str:
    if not re.search(r"^URL:\s*(?:unavailable|unknown|n/a|none|-|—)?\s*$", message, re.IGNORECASE | re.MULTILINE):
        return message
    urls = _registry_urls(registry_root)
    lines = message.splitlines()
    vacancy_ids = [match.group(1) for line in lines if (match := _VACANCY_ID_RE.match(line))]
    url_indexes = [index for index, line in enumerate(lines) if _URL_RE.match(line)]
    for ordinal, line_index in enumerate(url_indexes):
        url_match = _URL_RE.match(lines[line_index])
        assert url_match is not None
        if url_match and url_match.group(1).strip().casefold() in _MISSING_URLS:
            vacancy_id = vacancy_ids[ordinal] if ordinal < len(vacancy_ids) else ""
            source_url = urls.get(vacancy_id, "")
            if source_url:
                lines[line_index] = f"URL: {source_url}"
    return "\n".join(lines)


def validate_vacancy_urls(message: str) -> None:
    vacancy_ids = [match.group(1) for line in message.splitlines() if (match := _VACANCY_ID_RE.match(line))]
    if not vacancy_ids:
        return
    url_values = [match.group(1).strip() for line in message.splitlines() if (match := _URL_RE.match(line))]
    if len(url_values) != len(vacancy_ids):
        raise ValueError(
            "Vacancy notification requires exactly one URL for every Vacancy ID "
            f"({len(vacancy_ids)} IDs, {len(url_values)} URL fields)"
        )
    missing = [vacancy_ids[index] for index, value in enumerate(url_values) if value.casefold() in _MISSING_URLS]
    if missing:
        raise ValueError(f"Vacancy notification contains missing URLs for: {', '.join(missing)}")


def format_message_html(message: str) -> str:
    lines = message.strip().splitlines()
    separated: list[str] = []
    for line in lines:
        clean = line.strip()
        if clean and separated and separated[-1].strip().casefold().startswith("url:"):
            separated.append("")
        separated.append(clean)

    rendered: list[str] = []
    for index, line in enumerate(separated):
        if not line:
            if rendered and rendered[-1] != "":
                rendered.append("")
            continue
        label_match = _LABEL_RE.match(line)
        if label_match:
            label = label_match.group(1)
            value = escape(label_match.group(2), quote=False)
            if label.casefold() in {"automation id", "score"}:
                rendered.append(f"<b>{escape(label)}:</b> <i>{value}</i>")
            else:
                rendered.append(f"<b>{escape(label)}:</b> {value}")
            continue
        next_line = next((candidate for candidate in separated[index + 1 :] if candidate), "")
        if re.match(r"^(?:Score|Vacancy ID):", next_line, re.IGNORECASE):
            headline = re.match(r"^(.*?)(?:\s+)(\(score\s+\d+\))$", line, re.IGNORECASE)
            if headline:
                rendered.append(
                    f"<b>{escape(headline.group(1), quote=False)}</b> "
                    f"<i>{escape(headline.group(2), quote=False)}</i>"
                )
            else:
                rendered.append(f"<b>{escape(line, quote=False)}</b>")
            continue
        rendered.append(escape(line, quote=False))
    return "\n".join(rendered).strip()


def _registry_urls(registry_root: Path) -> dict[str, str]:
    result: dict[str, str] = {}
    for meta_path in sorted((registry_root / "jobs").glob("*/meta.yaml")):
        try:
            meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        except (OSError, yaml.YAMLError):
            continue
        if not isinstance(meta, dict):
            continue
        vacancy_id = str(meta.get("id") or "").strip()
        sources = meta.get("sources")
        if not vacancy_id or not isinstance(sources, list):
            continue
        for source in sources:
            if not isinstance(source, dict):
                continue
            url = str(source.get("url") or "").strip()
            if url:
                result[vacancy_id] = url
                break
    return result


def preserve_unsent_message(
    message: str,
    *,
    source_file: Path | None,
    prefix: str | None = None,
) -> Path:
    directory = source_file.parent if source_file is not None else Path(".codex-work")
    directory.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    clean_prefix = re.sub(r"[^A-Za-z0-9_.-]+", "-", (prefix or "unsent").strip()).strip("-")
    if not clean_prefix:
        clean_prefix = "unsent"
    target = directory / f"telegram-message-{clean_prefix}-{timestamp}-{os.getpid()}.txt"
    counter = 1
    while target.exists():
        target = directory / f"telegram-message-{clean_prefix}-{timestamp}-{os.getpid()}-{counter}.txt"
        counter += 1
    target.write_text(message, encoding="utf-8")
    return target


async def send_message(message: str, *, token: str, chat_id: str) -> dict[str, object]:
    curl = shutil.which("curl") or shutil.which("curl.exe")
    if not curl:
        raise RuntimeError("curl is required to send Telegram notifications")
    if not message.strip():
        raise ValueError("Telegram message cannot be empty")
    formatted_message = format_message_html(message)
    command = [
        curl,
        "--silent",
        "--show-error",
        "--fail",
        "-X",
        "POST",
        TELEGRAM_API.format(token=token),
        "--data-urlencode",
        f"chat_id={chat_id}",
        "--data-urlencode",
        f"text={formatted_message}",
        "--data-urlencode",
        "parse_mode=HTML",
        "--data-urlencode",
        "disable_web_page_preview=true",
    ]
    process = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    if process.returncode:
        detail = (stderr or stdout).decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"Telegram request failed: {detail[:500]}")
    try:
        response = json.loads(stdout.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise RuntimeError("Telegram returned invalid JSON") from exc
    if not isinstance(response, dict) or response.get("ok") is not True:
        raise RuntimeError("Telegram rejected the notification")
    return response


def delivery_fingerprint(message: str, chat_id: str) -> str:
    payload = f"{chat_id}\0{format_message_html(message)}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


async def send_message_once(
    message: str,
    *,
    token: str,
    chat_id: str,
    receipt_dir: Path,
) -> tuple[dict[str, object] | None, bool]:
    receipt_dir.mkdir(parents=True, exist_ok=True)
    fingerprint = delivery_fingerprint(message, chat_id)
    receipt_path = receipt_dir / f"{fingerprint}.json"
    if receipt_path.is_file():
        return None, False

    claim_path = receipt_dir / f"{fingerprint}.sending"
    try:
        descriptor = os.open(claim_path, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError as exc:
        if receipt_path.is_file():
            return None, False
        raise RuntimeError(f"Telegram notification delivery is already in progress: {fingerprint}") from exc
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as claim:
            claim.write(datetime.now(timezone.utc).isoformat() + "\n")
        response = await send_message(message, token=token, chat_id=chat_id)
        result = response.get("result")
        message_id = result.get("message_id") if isinstance(result, dict) else None
        receipt = {
            "fingerprint": fingerprint,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "telegram_message_id": message_id,
        }
        temporary = receipt_dir / f".{fingerprint}.{os.getpid()}.tmp"
        temporary.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        os.replace(temporary, receipt_path)
        return response, True
    finally:
        claim_path.unlink(missing_ok=True)


async def _main() -> int:
    args = _parser().parse_args()
    message = args.message
    if args.message_file is not None:
        message = args.message_file.read_text(encoding="utf-8")
    message = message_with_initiator(message or "", args.initiator)
    message = enrich_vacancy_urls(
        message,
        Path(__file__).resolve().parents[1] / "registry",
    )
    try:
        validate_vacancy_urls(message)
    except ValueError as exc:
        print(f"Telegram notification validation error: {exc}", file=sys.stderr)
        preserved = preserve_unsent_message(
            message,
            source_file=args.message_file,
            prefix=args.initiator or "invalid-message",
        )
        print(f"Unsent Telegram message preserved: {preserved}", file=sys.stderr)
        return 1
    token, chat_id = notification_config()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required", file=sys.stderr)
        preserved = preserve_unsent_message(
            message,
            source_file=args.message_file,
            prefix=args.initiator or "missing-secrets",
        )
        print(f"Unsent Telegram message preserved: {preserved}", file=sys.stderr)
        return 2
    try:
        _, sent = await send_message_once(
            message,
            token=token,
            chat_id=chat_id,
            receipt_dir=Path(__file__).resolve().parents[1] / ".codex-work" / "telegram-deliveries",
        )
    except Exception as exc:
        print(f"Telegram notification error: {exc}", file=sys.stderr)
        preserved = preserve_unsent_message(
            message,
            source_file=args.message_file,
            prefix=args.initiator or "send-failed",
        )
        print(f"Unsent Telegram message preserved: {preserved}", file=sys.stderr)
        return 1
    if sent:
        print("Telegram notification sent.")
    else:
        print("Telegram notification already sent; duplicate skipped.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
