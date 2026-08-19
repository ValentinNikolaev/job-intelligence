from __future__ import annotations

import argparse
import asyncio
import json
import os
from datetime import datetime, timezone
from pathlib import Path

from jobintel.telegram_outbox import load_notification, render_notification_message
from notify_telegram import notification_config, send_message_once


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deliver one tracked Telegram outbox file.")
    parser.add_argument("--outbox-file", type=Path, required=True)
    parser.add_argument("--sent-dir", type=Path, required=True)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    return parser


async def _main() -> int:
    args = _parser().parse_args()
    notification = load_notification(args.outbox_file)
    token, chat_id = notification_config()
    if not token or not chat_id:
        raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
    message = render_notification_message(notification)
    response, sent = await send_message_once(
        message,
        token=token,
        chat_id=chat_id,
        receipt_dir=args.receipt_dir,
    )
    args.sent_dir.mkdir(parents=True, exist_ok=True)
    sent_path = args.sent_dir / args.outbox_file.name
    delivered = {
        **notification,
        "delivered_at": datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z"),
        "telegram_message_id": (
            response.get("result", {}).get("message_id")
            if isinstance(response, dict) and isinstance(response.get("result"), dict)
            else None
        ),
        "delivery_status": "sent" if sent else "duplicate_skipped",
    }
    temporary = sent_path.with_name(f".{sent_path.name}.{os.getpid()}.tmp")
    temporary.write_text(
        json.dumps(delivered, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    os.replace(temporary, sent_path)
    args.outbox_file.unlink()
    print(f"Delivered Telegram outbox notification {notification['notification_id']}.")
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(_main()))
