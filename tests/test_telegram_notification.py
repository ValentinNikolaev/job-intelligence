from __future__ import annotations

import asyncio
import unittest
from unittest.mock import AsyncMock, patch

from scripts.notify_telegram import send_message


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


if __name__ == "__main__":
    unittest.main()
