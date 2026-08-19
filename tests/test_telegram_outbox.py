from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from jobintel.telegram_outbox import (
    TelegramOutboxError,
    build_analysis_notification,
    enqueue_notification,
    load_notification,
    render_notification_message,
)


class TelegramOutboxTests(unittest.TestCase):
    def test_builds_notification_only_for_eligible_non_rejected_results(self) -> None:
        notification = build_analysis_notification(
            _pack(),
            {
                "eligible": _result(82),
                "low": _result(64),
                "rejected": _result(91, hard_rejection=True),
            },
            minimum_score=65,
            clock=lambda: datetime(2026, 8, 19, 8, 0, tzinfo=timezone.utc),
        )

        assert notification is not None
        self.assertEqual("2026-08-19T08:00:00Z", notification["created_at"])
        self.assertEqual(["eligible"], [item["directory"] for item in notification["items"]])
        self.assertEqual(64, len(notification["notification_id"]))

    def test_returns_none_when_no_result_is_eligible(self) -> None:
        notification = build_analysis_notification(
            {"items": [_item("low", "low-id", "Low Co", "Low role")]},
            {"low": _result(64)},
            minimum_score=65,
        )

        self.assertIsNone(notification)

    def test_requires_source_url_for_an_eligible_vacancy(self) -> None:
        item = _item("eligible", "eligible-id", "Example", "Backend")
        item["source_url"] = ""

        with self.assertRaisesRegex(TelegramOutboxError, "source URL"):
            build_analysis_notification(
                {"items": [item]},
                {"eligible": _result(80)},
                minimum_score=65,
            )

    def test_enqueue_is_deterministic_and_sent_manifest_suppresses_requeue(self) -> None:
        notification = build_analysis_notification(
            {"items": [_item("eligible", "eligible-id", "Example", "Backend")]},
            {"eligible": _result(80)},
            minimum_score=65,
            clock=lambda: datetime(2026, 8, 19, 8, 0, tzinfo=timezone.utc),
        )
        assert notification is not None
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            first = enqueue_notification(root, notification)
            second = enqueue_notification(root, notification)
            loaded = load_notification(first)
            sent = root / "notifications" / "telegram" / "sent" / first.name
            sent.parent.mkdir(parents=True)
            sent.write_text(first.read_text(encoding="utf-8"), encoding="utf-8")
            first.unlink()
            third = enqueue_notification(root, notification)

        self.assertEqual(first, second)
        self.assertEqual(notification, loaded)
        self.assertEqual(sent, third)

    def test_rendered_message_has_the_sender_contract(self) -> None:
        notification = build_analysis_notification(
            {"items": [_item("eligible", "eligible-id", "Example", "Backend")]},
            {"eligible": _result(80)},
            minimum_score=65,
        )
        assert notification is not None

        message = render_notification_message(notification)

        self.assertIn("Automation ID: job-intelligence-batch-vacancy-analysis", message)
        self.assertIn("Example — Backend", message)
        self.assertIn("Score: 80", message)
        self.assertIn("Vacancy ID: eligible-id", message)
        self.assertIn("Directory: eligible", message)
        self.assertIn("URL: https://example.test/eligible", message)

    def test_tampered_manifest_is_rejected(self) -> None:
        notification = build_analysis_notification(
            {"items": [_item("eligible", "eligible-id", "Example", "Backend")]},
            {"eligible": _result(80)},
            minimum_score=65,
        )
        assert notification is not None
        notification["items"][0]["score"] = 81
        with TemporaryDirectory() as temporary:
            path = Path(temporary) / "tampered.json"
            path.write_text(json.dumps(notification), encoding="utf-8")

            with self.assertRaisesRegex(TelegramOutboxError, "does not match"):
                load_notification(path)


def _pack() -> dict[str, object]:
    return {
        "items": [
            _item("eligible", "eligible-id", "Example", "Backend"),
            _item("low", "low-id", "Low Co", "Low role"),
            _item("rejected", "rejected-id", "Rejected Co", "Rejected role"),
        ]
    }


def _item(directory: str, vacancy_id: str, company: str, title: str) -> dict[str, object]:
    return {
        "directory": directory,
        "vacancy_id": vacancy_id,
        "source_url": f"https://example.test/{directory}",
        "vacancy": {"company": company, "title": title},
    }


def _result(score: int, *, hard_rejection: bool = False) -> dict[str, object]:
    return {"score": score, "hard_rejection": hard_rejection}


if __name__ == "__main__":
    unittest.main()
