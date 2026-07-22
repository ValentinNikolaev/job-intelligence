# Scheduled vacancy analysis

Configure this Scheduled Task with **GPT-5.6 Luna** and **low reasoning**. Work only inside the configured repository.

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in analysis mode, and process exactly one pending vacancy with workflow `analyze`. If the configured model is unavailable or does not match, report the mismatch and do not publish. Never call the OpenAI Platform API from project code. The workflow skill owns its final catalog step.
