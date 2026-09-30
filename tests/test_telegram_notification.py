from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from scripts.notify_telegram import (
    enrich_vacancy_urls,
    format_message_html,
    message_with_initiator,
    notification_config,
    preserve_unsent_message,
    send_message,
    send_message_once,
    validate_vacancy_urls,
)


class TelegramNotificationTests(unittest.TestCase):
    def test_sends_one_url_encoded_message_with_curl(self) -> None:
        process = AsyncMock()
        process.communicate.return_value = (b'{"ok":true}', b"")
        process.returncode = 0
        with patch("scripts.notify_telegram.shutil.which", return_value="curl.exe"), patch(
            "scripts.notify_telegram.asyncio.create_subprocess_exec", return_value=process
        ) as create_process:
            asyncio.run(send_message("A title\nScore: 80", token="secret", chat_id="123"))
        command = create_process.call_args.args
        self.assertIn("chat_id=123", command)
        self.assertIn("text=<b>A title</b>\n<b>Score:</b> <i>80</i>", command)
        self.assertIn("parse_mode=HTML", command)
        self.assertIn("disable_web_page_preview=true", command)
        self.assertIn("https://api.telegram.org/botsecret/sendMessage", command)

    def test_formats_vacancies_with_safe_labels_and_blank_separator(self) -> None:
        message = "\n".join(
            (
                "Automation ID: batch-analysis",
                "SumUp — Backend Engineer (score 88)",
                "Vacancy ID: one",
                "Directory: sumup",
                "URL: https://example.test/job?a=1&b=2",
                "Acme — Senior PHP Engineer (score 84)",
                "Vacancy ID: two",
                "Directory: acme",
                "URL: https://example.test/other",
            )
        )

        formatted = format_message_html(message)

        self.assertIn("<b>Automation ID:</b> <i>batch-analysis</i>", formatted)
        self.assertIn("<b>SumUp — Backend Engineer</b> <i>(score 88)</i>", formatted)
        self.assertIn("<b>Vacancy ID:</b> one", formatted)
        self.assertIn("https://example.test/job?a=1&amp;b=2", formatted)
        self.assertIn("</b> https://example.test/job?a=1&amp;b=2\n\n<b>Acme", formatted)

    def test_enriches_unavailable_url_from_registry(self) -> None:
        with TemporaryDirectory() as temporary:
            registry_root = Path(temporary) / "registry"
            vacancy = registry_root / "jobs" / "sumup"
            vacancy.mkdir(parents=True)
            (vacancy / "meta.yaml").write_text(
                "\n".join(
                    (
                        "id: vacancy-one",
                        "sources:",
                        "- source: arbeitnow",
                        "  url: https://example.test/sumup",
                    )
                ),
                encoding="utf-8",
            )

            enriched = enrich_vacancy_urls(
                "SumUp — Backend Engineer\nVacancy ID: vacancy-one\nURL: unavailable",
                registry_root,
            )

        self.assertIn("URL: https://example.test/sumup", enriched)
        self.assertNotIn("URL: unavailable", enriched)

    def test_enriches_blank_urls_when_url_precedes_vacancy_id(self) -> None:
        with TemporaryDirectory() as temporary:
            registry_root = Path(temporary) / "registry"
            for name, vacancy_id, url in (
                ("sumup", "vacancy-one", "https://example.test/sumup"),
                ("acme", "vacancy-two", "https://example.test/acme"),
            ):
                vacancy = registry_root / "jobs" / name
                vacancy.mkdir(parents=True)
                (vacancy / "meta.yaml").write_text(
                    f"id: {vacancy_id}\nsources:\n- source: direct\n  url: {url}\n",
                    encoding="utf-8",
                )
            message = "\n".join(
                (
                    "SumUp — Backend Engineer — score 88",
                    "URL: ",
                    "Vacancy ID: vacancy-one",
                    "Directory: sumup",
                    "",
                    "Acme — Senior PHP Engineer — score 84",
                    "URL: unavailable",
                    "Vacancy ID: vacancy-two",
                    "Directory: acme",
                )
            )

            enriched = enrich_vacancy_urls(message, registry_root)

        self.assertIn("URL: https://example.test/sumup", enriched)
        self.assertIn("URL: https://example.test/acme", enriched)
        validate_vacancy_urls(enriched)

    def test_rejects_vacancy_notification_with_missing_url(self) -> None:
        with self.assertRaisesRegex(ValueError, "vacancy-one"):
            validate_vacancy_urls("Title\nURL: \nVacancy ID: vacancy-one\nDirectory: sumup")

    def test_sends_identical_notification_only_once(self) -> None:
        response = {"ok": True, "result": {"message_id": 42}}
        with TemporaryDirectory() as temporary, patch(
            "scripts.notify_telegram.send_message", new=AsyncMock(return_value=response)
        ) as sender:
            first = asyncio.run(
                send_message_once(
                    "Title\nScore: 80",
                    token="secret",
                    chat_id="123",
                    receipt_dir=Path(temporary),
                )
            )
            second = asyncio.run(
                send_message_once(
                    "Title\nScore: 80",
                    token="secret",
                    chat_id="123",
                    receipt_dir=Path(temporary),
                )
            )

        self.assertEqual((response, True), first)
        self.assertEqual((None, False), second)
        sender.assert_awaited_once()

    def test_failed_delivery_can_be_retried(self) -> None:
        response = {"ok": True, "result": {"message_id": 43}}
        with TemporaryDirectory() as temporary, patch(
            "scripts.notify_telegram.send_message",
            new=AsyncMock(side_effect=(RuntimeError("network failed"), response)),
        ) as sender:
            with self.assertRaisesRegex(RuntimeError, "network failed"):
                asyncio.run(
                    send_message_once(
                        "Title\nScore: 81",
                        token="secret",
                        chat_id="123",
                        receipt_dir=Path(temporary),
                    )
                )
            retried = asyncio.run(
                send_message_once(
                    "Title\nScore: 81",
                    token="secret",
                    chat_id="123",
                    receipt_dir=Path(temporary),
                )
            )

        self.assertEqual((response, True), retried)
        self.assertEqual(2, sender.await_count)

    def test_loads_credentials_from_sources_env_with_environment_override(self) -> None:
        with TemporaryDirectory() as temporary:
            env_path = Path(temporary) / ".env"
            env_path.write_text(
                "TELEGRAM_BOT_TOKEN=file-token\nTELEGRAM_CHAT_ID=file-chat\n",
                encoding="utf-8",
            )
            with patch("scripts.notify_telegram._default_env_path", return_value=env_path), patch.dict(
                "os.environ", {"TELEGRAM_CHAT_ID": "env-chat"}, clear=False
            ):
                token, chat_id = notification_config()

        self.assertEqual("file-token", token)
        self.assertEqual("env-chat", chat_id)

    def test_message_with_initiator_adds_automation_id_once(self) -> None:
        message = message_with_initiator("Title\nScore: 68", "job-intelligence-normal-application-preparation")

        self.assertEqual(
            "Automation ID: job-intelligence-normal-application-preparation\nTitle\nScore: 68",
            message,
        )
        self.assertEqual(
            "Automation ID: another-automation\nTitle\nScore: 68",
            message_with_initiator(message, "another-automation"),
        )
        self.assertEqual(
            "Automation ID: another-automation\nTitle\nScore: 68",
            message_with_initiator(
                "Internal initiator: Job Intelligence: normal preparation\nTitle\nScore: 68",
                "another-automation",
            ),
        )

    def test_preserves_unsent_message_with_unique_prefixed_name(self) -> None:
        with TemporaryDirectory() as temporary:
            source = Path(temporary) / "telegram-message.txt"
            first = preserve_unsent_message("first", source_file=source, prefix="normal preparation")
            second = preserve_unsent_message("second", source_file=source, prefix="normal preparation")

            self.assertEqual(Path(temporary), first.parent)
            self.assertEqual(Path(temporary), second.parent)
            self.assertNotEqual(first, second)
            self.assertTrue(first.name.startswith("telegram-message-normal-preparation-"))
            self.assertEqual("first", first.read_text(encoding="utf-8"))
            self.assertEqual("second", second.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
