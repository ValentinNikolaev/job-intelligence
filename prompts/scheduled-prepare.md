# Scheduled normal application preparation

Configure this Scheduled Task with **GPT-5.5** and **medium reasoning**. Work only inside the configured repository.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in normal preparation mode, and process exactly one pending vacancy whose score is from `prepare_min_score` through `priority_score - 1`, using workflow `prepare`. If GPT-5.5 is unavailable in the selected Codex surface, report that limitation and do not publish. Never call the OpenAI Platform API from project code. The workflow skill owns its final catalog step.
