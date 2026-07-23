from __future__ import annotations

import asyncio
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import AsyncMock, patch

from scripts.notify_telegram import notification_config, send_message


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


if __name__ == "__main__":
    unittest.main()
