from __future__ import annotations

from datetime import datetime, timezone
import hashlib
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
    undelivered_items,
    validate_notification,
)
from scripts.notify_telegram import format_message_html


class TelegramOutboxTests(unittest.TestCase):
    def test_country_flags_survive_queue_roundtrip_and_html_formatting(self) -> None:
        item = _item("eligible", "eligible-id", "Example & Co", "Backend")
        item["vacancy"] = {"metadata": {
            **item["vacancy"],
            "location": "Italy, Germany, France, Spain, Poland, Portugal, Italy",
        }}
        notification = build_analysis_notification(
            {"items": [item]}, {"eligible": _result(80)}, minimum_score=65,
        )
        assert notification is not None
        self.assertEqual(["IT", "DE", "FR", "ES", "PL", "PT"], notification["items"][0]["country_codes"])
        with TemporaryDirectory() as temporary:
            loaded = load_notification(enqueue_notification(Path(temporary), notification))
        message = format_message_html(render_notification_message(loaded))
        self.assertIn("<b>🇮🇹 🇩🇪 🇫🇷 🇪🇸 🇵🇱 Example &amp; Co — Backend</b>", message)
        self.assertNotIn("🇵🇹", message)
        self.assertIn("<b>URL:</b> https://example.test/eligible", message)

    def test_unknown_location_has_no_flags_or_leading_space(self) -> None:
        item = _item("eligible", "eligible-id", "Example", "Backend")
        item["vacancy"]["location"] = "Worldwide"
        notification = build_analysis_notification(
            {"items": [item]}, {"eligible": _result(80)}, minimum_score=65,
        )
        assert notification is not None
        self.assertEqual([], notification["items"][0]["country_codes"])
        self.assertIn("\n\nExample — Backend\n", render_notification_message(notification))

    def test_dou_and_djinni_default_to_ukraine_when_country_is_not_explicit(self) -> None:
        for source in ("dou", "djinni"):
            with self.subTest(source=source):
                item = _item("eligible", "eligible-id", "Example", "Backend")
                item["vacancy"]["location"] = "Київ, за кордоном, віддалено"
                item["vacancy"]["data_source"] = source
                notification = build_analysis_notification(
                    {"items": [item]}, {"eligible": _result(80)}, minimum_score=65,
                )
                assert notification is not None
                self.assertEqual(["UA"], notification["items"][0]["country_codes"])

    def test_ukraine_default_does_not_apply_to_other_sources(self) -> None:
        item = _item("eligible", "eligible-id", "Example", "Backend")
        item["vacancy"]["location"] = "Remote"
        item["vacancy"]["data_source"] = "adzuna"
        notification = build_analysis_notification(
            {"items": [item]}, {"eligible": _result(80)}, minimum_score=65,
        )
        assert notification is not None
        self.assertEqual([], notification["items"][0]["country_codes"])

    def test_dou_and_djinni_explicit_country_is_not_overridden(self) -> None:
        item = _item("eligible", "eligible-id", "Example", "Backend")
        item["vacancy"]["location"] = "Remote Germany"
        item["vacancy"]["data_source"] = "dou"
        notification = build_analysis_notification(
            {"items": [item]}, {"eligible": _result(80)}, minimum_score=65,
        )
        assert notification is not None
        self.assertEqual(["DE"], notification["items"][0]["country_codes"])

    def test_legacy_v1_manifest_keeps_its_original_hash_and_message(self) -> None:
        payload = {
            "schema_version": 1,
            "channel": "telegram",
            "initiator": "job-intelligence-batch-vacancy-analysis",
            "minimum_score": 65,
            "items": [{"company": "Example", "title": "Backend", "score": 80,
                       "vacancy_id": "eligible-id", "directory": "eligible",
                       "url": "https://example.test/eligible"}],
        }
        notification = {
            **payload,
            "notification_id": hashlib.sha256(json.dumps(
                payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"),
            ).encode("utf-8")).hexdigest(),
            "created_at": "2026-08-19T08:00:00Z",
        }
        self.assertEqual(notification, validate_notification(notification))
        self.assertIn("\n\nExample — Backend\n", render_notification_message(notification))

    def test_country_codes_are_validated_and_protected_by_payload_hash(self) -> None:
        notification = build_analysis_notification(
            {"items": [_item("eligible", "eligible-id", "Example", "Backend")]},
            {"eligible": _result(80)}, minimum_score=65,
        )
        assert notification is not None
        for codes in (None, "IT", ["ZZ"], ["it"], ["IT", "IT"], [{}], [True]):
            with self.subTest(codes=codes):
                notification["items"][0]["country_codes"] = codes
                with self.assertRaisesRegex(TelegramOutboxError, "invalid country codes"):
                    validate_notification(notification)
        notification["items"][0]["country_codes"] = ["IT"]
        with self.assertRaisesRegex(TelegramOutboxError, "does not match"):
            validate_notification(notification)

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

    def test_delivery_filters_sent_urls_and_duplicates_within_batch(self) -> None:
        previous = build_analysis_notification(
            {"items": [_item("old", "old-id", "Neting", "Laravel")]},
            {"old": _result(84)}, minimum_score=65,
        )
        assert previous is not None
        repeated = _item("repeat", "new-id", "Neting", "Laravel Remote")
        repeated["source_url"] = "https://EXAMPLE.test/old/#details"
        fresh = _item("fresh", "fresh-id", "Fresh", "Backend")
        duplicate_fresh = _item("fresh-again", "another-id", "Fresh", "Backend role")
        duplicate_fresh["source_url"] = "https://example.test/fresh/"
        current = build_analysis_notification(
            {"items": [repeated, fresh, duplicate_fresh]},
            {name: _result(80) for name in ("repeat", "fresh", "fresh-again")},
            minimum_score=65,
        )
        assert current is not None
        with TemporaryDirectory() as temporary:
            sent_dir = Path(temporary)
            receipt = {**previous, "delivery_status": "sent"}
            (sent_dir / "previous.json").write_text(json.dumps(receipt), encoding="utf-8")
            selected = undelivered_items(current, sent_dir)
            self.assertEqual(["fresh-id"], [item["vacancy_id"] for item in selected])
            self.assertIn("Fresh — Backend", render_notification_message(current, items=selected))
            receipt = {**current, "delivery_status": "sent", "delivered_vacancy_ids": ["fresh-id"]}
            (sent_dir / "current.json").write_text(json.dumps(receipt), encoding="utf-8")
            self.assertEqual([], undelivered_items(current, sent_dir))

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
