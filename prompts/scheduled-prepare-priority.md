# Scheduled priority application preparation

Configure this Scheduled Task with **GPT-5.6 Terra** and **medium reasoning**. Work only inside the configured repository.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in priority preparation mode, and process exactly one pending vacancy at or above the priority score, using workflow `prepare-priority`. If the configured model is unavailable or does not match, report the mismatch and do not publish. Never call the OpenAI Platform API from project code. The workflow skill owns its final catalog step.

After a successful package publication, send at most one Telegram message for this run. Include the title, original vacancy URL, score, a repository link to `application/cv.md` or `application/cover-letter.md` when available, and five concise skills or requirements taken directly from the vacancy. If no repository link is possible, include the system path. Write `.codex-work\\telegram-message.txt` and call `python scripts/notify_telegram.py --message-file .codex-work\\telegram-message.txt` exactly once when task secrets are available; otherwise report that notification was skipped without exposing secrets.
