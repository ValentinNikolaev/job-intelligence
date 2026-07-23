from __future__ import annotations

import argparse
import asyncio
import json
import shutil
import sys
from pathlib import Path

from jobintel.config import load_env


TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Send one Telegram notification asynchronously.")
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--message")
    source.add_argument("--message-file", type=Path)
    return parser


def _default_env_path() -> Path:
    return Path(__file__).resolve().parents[1] / "sources" / ".env"


def notification_config() -> tuple[str, str]:
    config = load_env(_default_env_path())
    return (
        config.get("TELEGRAM_BOT_TOKEN", "").strip(),
        config.get("TELEGRAM_CHAT_ID", "").strip(),
    )


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
    token, chat_id = notification_config()
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required", file=sys.stderr)
        return 2
    try:
        message = args.message
        if args.message_file is not None:
            message = args.message_file.read_text(encoding="utf-8")
        await send_message(message or "", token=token, chat_id=chat_id)
    except Exception as exc:
        print(f"Telegram notification error: {exc}", file=sys.stderr)
        return 1
    print("Telegram notification sent.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
