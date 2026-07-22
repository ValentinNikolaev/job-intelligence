# Scheduled priority application preparation

Configure this Scheduled Task with **GPT-5.6 Terra** and **medium reasoning**. Work only inside the configured repository.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in priority preparation mode, and process exactly one pending vacancy at or above the priority score, using workflow `prepare-priority`. If the configured model is unavailable or does not match, report the mismatch and do not publish. Never call the OpenAI Platform API from project code. The workflow skill owns its final catalog step.
