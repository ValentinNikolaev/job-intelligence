# Scheduled vacancy analysis

Configure this Scheduled Task with **GPT-5.6 Luna** and **low reasoning**. Work only inside the configured repository.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in analysis mode, and use a
batch of up to 10 sealed pending vacancies when the batch contract is available:
`python run.py pending analyze all --limit 10 --pack .codex-work/analyze-pack.yaml`.
Evaluate every record independently and write the same pack with a strict `results`
mapping, then publish it with `python run.py analyze-batch --input
.codex-work/analyze-batch.yaml --workflow analyze`. If the configured model is
unavailable or does not match, report the mismatch and do not publish. Never call the
OpenAI Platform API from project code. The workflow skill owns its final catalog step.
After the Codex run, record exact usage when the current Codex surface exposes it:
`python run.py usage record --workflow analyze --model <configured-label>
--input-tokens <n> --output-tokens <n> --total-tokens <n> --credits <n>`. If exact
credits are unavailable, record an estimate explicitly with `--measurement estimated`.
If Telegram is unavailable or the send fails, preserve any unsent message in a collision-resistant `.codex-work/telegram-message-<unique-prefix>.txt` file; never overwrite another process's message.
