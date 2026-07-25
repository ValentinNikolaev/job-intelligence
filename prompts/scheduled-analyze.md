# Scheduled vacancy analysis

Configure this Scheduled Task with **GPT-5.6 Luna** and **low reasoning**. Work only inside the configured repository.

Before selecting work, pull the latest committed repository state from the configured
remote branch, for example with `git fetch --prune origin` and `git pull --ff-only`,
then inspect the current repo-derived queue data with
`python run.py api queues analyze --json --limit 10`. Do not rely on stale task context
when deciding which vacancies are pending.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in analysis mode, and use a
batch of up to 10 sealed pending vacancies when the batch contract is available:
`python run.py pending analyze all --limit 10 --pack .codex-work/analyze-pack.yaml`.
Evaluate every record independently and write the same pack with a strict `results`
mapping, then publish it with `python run.py analyze-batch --input
.codex-work/analyze-batch.yaml --workflow analyze`. If the configured model is
unavailable or does not match, report the mismatch and do not publish. Never call the
OpenAI Platform API from project code. The workflow skill owns its final catalog step.
Before starting triage or analysis, inspect `.codex-work/telegram-message-*.txt` for
preserved unsent messages from earlier runs. Retry each pending message with
`python scripts/notify_telegram.py --message-file <path>`. Treat a message as sent
only when the command exits with code 0 and prints `Telegram notification sent.`;
after confirmed success, remove that consumed pending file so it cannot be sent twice.
After the Codex run, record exact usage when the current Codex surface exposes it:
`python run.py usage record --workflow analyze --model <configured-label>
--input-tokens <n> --output-tokens <n> --total-tokens <n> --credits <n>`. If exact
credits are unavailable, record an estimate explicitly with `--measurement estimated`.
If Telegram is unavailable or the send fails, preserve any unsent message in a collision-resistant `.codex-work/telegram-message-<unique-prefix>.txt` file; never overwrite another process's message. Always invoke `python scripts/notify_telegram.py` and let it load `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from the task/host environment or the ignored `sources/.env`; do not pre-skip based only on the current process environment. If this task sends a Telegram message, include exactly one initiator line, `Automation ID: job-intelligence-batch-vacancy-analysis`, and do not include `Internal initiator:` or prose labels as initiator text.
