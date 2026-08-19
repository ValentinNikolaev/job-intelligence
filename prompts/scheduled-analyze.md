# Scheduled vacancy analysis — canonical Codex task prompt

This file is the source of truth for the scheduled Codex task. The automation
definition must instruct Codex to read and execute this file in full; it must not
duplicate or silently override these steps. The repository workflow policy and
installed skills may be composed together: use the selected `analyze` profile from
`config/codex-workflows.yaml`, invoke `$job-intelligence-workflow` in analysis mode,
and use any specialized skills it explicitly routes to. The automation's configured
model must match the selected profile; the repository cannot change the active model
during a run.

Configure this Scheduled Task with the model and reasoning from the selected `analyze`
profile in `config/codex-workflows.yaml` (default: `luna_low`). Work only inside the
configured repository.

Read `AGENTS.md` and `prompts/job-intelligence-workflow.md`, invoke
`$job-intelligence-workflow` in analysis mode, and use a
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
`python run.py --workflow analyze pending analyze all --limit 15 --pack .codex-work/analyze-pack.yaml`.
Treat that newly written pack as the only batch source for the current run. Evaluate
every record independently and write the same metadata and items with a strict
`results` mapping. Before publication, verify that the batch item directories and
result keys exactly match the current pack; never reuse items or results from an
earlier run. Publish with `python run.py analyze-batch --input
.codex-work/analyze-batch.yaml --workflow analyze --model-profile <selected-profile>`.
If the configured model is
unavailable or does not match, report the mismatch and do not publish. Never call the
OpenAI Platform API from project code. The workflow skill owns its final catalog step.
After the Codex run, record exact usage only when the current Codex surface exposes it:
`python run.py usage record --workflow analyze --model <configured-label>
--input-tokens <n> --output-tokens <n> --total-tokens <n> --credits <n>`. If exact
usage is unavailable, report that it is unavailable; do not record a fabricated
zero-token or zero-credit estimate.

`analyze-batch` deterministically writes one tracked JSON manifest under
`notifications/telegram/outbox/` when the fresh batch contains at least one newly
analyzed vacancy with a score at or above `prepare_min_score` and without a hard
rejection. It fails closed before publication if an eligible vacancy is missing its
company, title, vacancy ID, directory, or source URL. Include the outbox manifest in
the same analysis commit and push. Do not invoke `scripts/notify_telegram.py`, `curl`,
or any other external sender from this Codex task, and do not create an ignored local
Telegram draft. The separate `Job Intelligence Telegram Delivery` GitHub Actions
workflow owns delivery, tracked receipts, and moving confirmed manifests to
`notifications/telegram/sent/`.

After publication and catalog generation, run `python run.py api workflow-summary
--json` again. Report `pending_analyze` before, after, and as a delta. Keep the catalog
total separate and never report "catalog vacancies not processed this run": that
subtraction measures only the current run, not the pending-analysis backlog.

When repository files changed, inspect the staged diff before committing and write a
natural, human-written subject that states what this run actually accomplished. Use the
number of analyzed vacancies or another concrete result when it makes the subject more
informative. Do not select from the GitHub Actions templates and do not fall back to a
generic `update data`, `update files`, `workflow changes`, or `automated update`
subject. Put the workflow/run identifier and mechanical file counts in the commit body.
