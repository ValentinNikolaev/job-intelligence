# Scheduled vacancy analysis

Configure this Scheduled Task with **GPT-5.6 Luna** and **low reasoning**. Work only inside the configured repository.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in analysis mode, and use a
batch of up to 15 sealed pending vacancies when the batch contract is available.
Acquire the shared collection/analysis lock before fetching, pulling, inspecting the
queue, running triage, or creating the pack. Keep it through publication, catalog
generation, verification, commit, and push, and release it after success or failure:
`python run.py workflow-lock acquire analysis --lock-token-file .codex-work/workflow-lock-token.txt --lock-timeout-seconds 3600`.
Set `JOBINTEL_WORKFLOW_LOCK_TOKEN` from that token file for every guarded command in
the run. Only after acquiring the lock, refresh the configured remote branch with
`git fetch --prune origin` and `git pull --ff-only`. Record the authoritative backlog
before analysis with `python run.py api workflow-summary --json`, then inspect queue
details with `python run.py api queues analyze --json --limit 30`. Do not rely on stale
task context when deciding which vacancies are pending. Release the lock with
`python run.py workflow-lock release --lock-token-file .codex-work/workflow-lock-token.txt`.
While holding that token, create the pack with:
`python run.py pending analyze all --limit 15 --pack .codex-work/analyze-pack.yaml`.
Treat that newly written pack as the only batch source for the current run. Evaluate
every record independently and write the same metadata and items with a strict
`results` mapping. Before publication, verify that the batch item directories and
result keys exactly match the current pack; never reuse items or results from an
earlier run. Publish with `python run.py analyze-batch --input
.codex-work/analyze-batch.yaml --workflow analyze`. If the configured model is
unavailable or does not match, report the mismatch and do not publish. Never call the
OpenAI Platform API from project code. The workflow skill owns its final catalog step.
Before starting triage or analysis, inspect `.codex-work/telegram-message-*.txt` for
preserved unsent messages from earlier runs. Retry each pending message with
`python scripts/notify_telegram.py --message-file <path>`. Treat a message as sent
only when the command exits with code 0 and prints `Telegram notification sent.`;
after confirmed success, remove that consumed pending file so it cannot be sent twice.
After the Codex run, record exact usage only when the current Codex surface exposes it:
`python run.py usage record --workflow analyze --model <configured-label>
--input-tokens <n> --output-tokens <n> --total-tokens <n> --credits <n>`. If exact
usage is unavailable, report that it is unavailable; do not record a fabricated
zero-token or zero-credit estimate.
If Telegram is unavailable or the send fails, preserve any unsent message in a collision-resistant `.codex-work/telegram-message-<unique-prefix>.txt` file; never overwrite another process's message. Always invoke `python scripts/notify_telegram.py` and let it load `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` from the task/host environment or the ignored `sources/.env`; do not pre-skip based only on the current process environment. If this task sends a Telegram message for new vacancy analysis, include the original vacancy URL, `Vacancy ID`, and `Directory` for each reported vacancy, include exactly one initiator line, `Automation ID: job-intelligence-batch-vacancy-analysis`, and do not include `Internal initiator:` or prose labels as initiator text. Use the `vacancy_id` and `directory` fields from `python run.py api queues analyze --json` or the sealed analysis pack so the user can run `python run.py status <vacancy-id-or-directory> ...` without searching the registry manually.

After publication and catalog generation, run `python run.py api workflow-summary
--json` again. Report `pending_analyze` before, after, and as a delta. Keep the catalog
total separate and never report "catalog vacancies not processed this run": that
subtraction measures only the current run, not the pending-analysis backlog.
