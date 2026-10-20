from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jobintel.telegram_outbox import load_notification, render_notification_message, undelivered_items
from jobintel.accounts import AccountConfigurationError, resolve_account_arguments

if __package__:
    from .notify_telegram import notification_config, send_message_once
else:
    from notify_telegram import notification_config, send_message_once


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Deliver one tracked Telegram outbox file.", allow_abbrev=False)
    parser.add_argument("--account", help="account identifier (default: current)")
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--outbox-file", type=Path, required=True)
    parser.add_argument("--sent-dir", type=Path, required=True)
    parser.add_argument("--receipt-dir", type=Path, required=True)
    return parser


async def _main(argv: list[str] | None = None) -> int:
    try:
        context, remaining = resolve_account_arguments(
            sys.argv[1:] if argv is None else argv, default_root=Path(__file__).resolve().parents[1],
        )
        args = _parser().parse_args(remaining)
        notifications = context.path("notifications")
        args.outbox_file = args.outbox_file.resolve()
        args.sent_dir = args.sent_dir.resolve()
        args.receipt_dir = args.receipt_dir.resolve()
        if (args.outbox_file.parent != notifications / "outbox"
                or args.sent_dir != notifications / "sent"
                or args.receipt_dir != notifications / "receipts"):
            raise AccountConfigurationError("delivery paths must use the selected account's outbox, sent and receipts directories")
    except AccountConfigurationError as exc:
        print(f"Account configuration error: {exc}", file=sys.stderr)
        return 2
    notification = load_notification(args.outbox_file)
    items = undelivered_items(notification, args.sent_dir)
    response = None
    sent = False
    if items:
        token, chat_id = notification_config(context=context)
        if not token or not chat_id:
            raise RuntimeError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID are required")
        message = render_notification_message(notification, items=items)
        response, sent = await send_message_once(
            message,
            token=token,
            chat_id=chat_id,
            receipt_dir=args.receipt_dir,
            initiator=notification["initiator"],
            repository_root=context.project_root,
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
        "delivered_vacancy_ids": [item["vacancy_id"] for item in items] if sent else [],
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
