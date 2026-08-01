# Scheduled application preparation

If Telegram is unavailable or the send fails, preserve any unsent message in a collision-resistant `.codex-work/telegram-message-<unique-prefix>.txt` file; never overwrite another process's message.

Configure this Scheduled Task with **GPT-5.6 Terra** and **medium reasoning**. Work only inside the configured repository.

Before selecting work, pull the latest committed repository state from the configured
remote branch, for example with `git fetch --prune origin` and `git pull --ff-only`,
then inspect the current repo-derived queue data with
`python run.py api queues prepare --json --limit 10`. Do not rely on stale task context
when deciding which vacancy is pending.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in preparation mode, and process exactly one pending vacancy using workflow `prepare`. The queue already returns only priority-score vacancies while any fresh priority vacancy is pending; only when no priority vacancy is pending may it return normal-score vacancies. Do not prepare vacancies older than `prepare_max_age_days` from their `discovered_at` timestamp. If the configured model is unavailable or does not match, report the mismatch and do not publish. Never call the OpenAI Platform API from project code. The workflow skill owns its final catalog step.

After a successful package publication, send at most one Telegram message for this run. Include exactly one initiator line, `Automation ID: job-intelligence-application-preparation`, plus title, original vacancy URL, `Vacancy ID`, `Directory`, score, a repository link to `application/cv.md` or `application/cover-letter.md` when available, and five concise skills or requirements taken directly from the vacancy. Use the `vacancy_id` and `directory` fields from `python run.py api queues prepare --json` or from the selected vacancy `meta.yaml` so the user can run `python run.py status <vacancy-id-or-directory> ...` without searching the registry manually. Do not include `Internal initiator:` or prose labels such as `Job Intelligence: application preparation` as initiator text. If no repository link is possible, include the system path. Write the initial message to a run-specific path matching `.codex-work\\telegram-message-prepare-<vacancy-or-run-id>.txt` so concurrent processes cannot overwrite it, then call `python scripts/notify_telegram.py --message-file <message-file> --initiator "job-intelligence-application-preparation"` exactly once. Let the notifier load Telegram secrets from task/host environment or `sources/.env`; do not pre-skip based only on the current process environment. If sending fails, report that notification was skipped/failed without exposing secrets; the notifier preserves an unsent copy as `.codex-work\\telegram-message-<prefix>-<timestamp>-<pid>.txt`.
