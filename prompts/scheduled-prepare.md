# Scheduled application preparation

Automatic scheduled application preparation is disabled.

Do not select vacancies automatically, do not run `python run.py api queues prepare`,
and do not publish application packages from a schedule. Application preparation now
starts only from an explicit user chat request naming a vacancy ID or registry
directory from the analyzed vacancy matches.

If this Scheduled Task still exists, it should stop after reporting that manual
selection is required. The manual chat workflow is:

1. Use analyzed vacancy matches from Telegram or the catalog.
2. The user explicitly provides one vacancy ID or registry directory.
3. A Codex task reads `AGENTS.md`, invokes `$job-intelligence-workflow` in preparation
   mode, writes drafts under `.codex-work/`, and publishes with
   `python run.py prepare <vacancy-id-or-directory> --input <draft-directory> --workflow prepare`.
