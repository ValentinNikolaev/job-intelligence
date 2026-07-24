from __future__ import annotations

import argparse
import asyncio
from datetime import datetime, timezone
import json
import os
import shutil
import sys
from pathlib import Path
import re

from jobintel.config import load_env


TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


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
        f"text={message}",
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


async def _main() -> int:
    args = _parser().parse_args()
    message = args.message
    if args.message_file is not None:
        message = args.message_file.read_text(encoding="utf-8")
    message = message_with_initiator(message or "", args.initiator)
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
        await send_message(message, token=token, chat_id=chat_id)
    except Exception as exc:
        print(f"Telegram notification error: {exc}", file=sys.stderr)
        preserved = preserve_unsent_message(
            message,
            source_file=args.message_file,
            prefix=args.initiator or "send-failed",
        )
        print(f"Unsent Telegram message preserved: {preserved}", file=sys.stderr)
        return 1
    print("Telegram notification sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
