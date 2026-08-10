# Scheduled application preparation

Automatic scheduled application preparation is disabled.

Read `prompts/job-intelligence-workflow.md` for the shared manual-application
contract. A user-provided vacancy URL must enter through the interactive
`manual-application` mode and `$manual-vacancy-application`; this Scheduled Task must
not invent a selection or silently prepare a queue.

When that manual URL flow has no current match, it uses direct `python run.py analyze
<vacancy-directory> --input <draft.yaml> --workflow analyze`; it must not borrow this
or the scheduled analysis queue to process unrelated vacancies.

Do not select vacancies automatically, do not run `python run.py api queues prepare`,
and do not publish application packages from a schedule. Application preparation now
starts only from an explicit user chat request naming a vacancy ID or registry
directory from the analyzed vacancy matches.

If this Scheduled Task still exists, it should stop after reporting that manual
selection is required. The manual chat workflow is:

1. Use analyzed vacancy matches from Telegram or the catalog.
2. The user explicitly provides one to 10 vacancy IDs or registry directories.
3. A Codex task reads `AGENTS.md`, invokes `$job-intelligence-workflow` in preparation
   mode, writes one isolated draft set per vacancy under
   `.codex-work/application/<vacancy-directory>/`, validates each completed draft set
   once with `python run.py validate-application <vacancy-directory> --input
   .codex-work/application/<vacancy-directory>`, and publishes the verified batch with
   `python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare --model-profile <selected-profile>`.
