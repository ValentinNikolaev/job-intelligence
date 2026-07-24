from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from scripts.notify_telegram import message_with_initiator, notification_config, preserve_unsent_message, send_message


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
        self.assertIn("text=A title\nScore: 80", command)
        self.assertIn("https://api.telegram.org/botsecret/sendMessage", command)

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

    def test_message_with_initiator_adds_internal_source_once(self) -> None:
        message = message_with_initiator("Title\nScore: 68", "Job Intelligence: normal preparation")

        self.assertEqual(
            "Internal initiator: Job Intelligence: normal preparation\nTitle\nScore: 68",
            message,
        )
        self.assertEqual(message, message_with_initiator(message, "Another initiator"))

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
