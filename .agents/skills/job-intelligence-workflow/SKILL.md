---
name: job-intelligence-workflow
description: Run the repository's vacancy collection, match analysis, vacancy-status management, and vacancy-specific application preparation without project code calling the OpenAI Platform API. Use for Job Intelligence scheduled runs, processing pending vacancies, publishing Codex-produced drafts, manually changing vacancy status, and orchestrating the mandatory final independent vacancy-catalog generation.
---

# Job Intelligence Workflow

Obey `AGENTS.md` first. Never call the OpenAI Platform API from repository code. Use the model already selected for the active Codex task and never claim to have switched models from inside the task.

## Choose one mode

- For collection, run `python run.py all`, regenerate the registry index, and report source failures separately.
- For analysis, follow `references/analyze.md` and process exactly one pending vacancy.
- For a normal application package, follow `references/prepare.md` with workflow `prepare` and process exactly one vacancy whose match score is at least `prepare_min_score` and below `priority_score`.
- For a priority application package, follow `references/prepare.md` with workflow `prepare_priority` and process exactly one vacancy whose match score is at least `priority_score`.
- For a user-requested status change, run `python run.py status <vacancy-id-or-directory> <status>`. Never change status without an explicit user request. Preserve the complete history through the command.

Read `config/codex-workflows.yaml` before model-dependent work. The selected Scheduled Task or chat must use the corresponding model and reasoning level. Pass the workflow name to the deterministic publisher; it derives the only allowed model label from policy. If the requested model is unavailable in the current Codex surface, tell the user and do not publish under that workflow.

## Common rules

1. Read only the selected vacancy, the configured candidate source files, and the relevant prompt. Do not read another vacancy's match or application package.
2. Write model-produced drafts only under `.codex-work/`; the directory is ignored by Git.
3. Publish through `run.py` so schema validation, hashes, atomic writes, DOCX conversion, and cache metadata remain deterministic.
4. If publication fails validation, fix the draft and retry. Do not edit generated cache metadata by hand.
5. Never submit applications or contact employers.

## Mandatory final catalog step

After every successful collection, analysis, preparation, or manual status change, use `$generate-vacancy-catalog` and run its deterministic command as a separate operating-system process. Include its result in the final report. Do not import or call the catalog generator in-process.

## Mandatory Git finalization

After the catalog process, run the relevant tests and API-prohibition scan. Inspect the full diff, stage all added, changed, and deleted project files with `git add -A`, commit once, and push the current branch to `origin`. Never stage ignored secrets or local work files. If the tree is unchanged, skip the commit and push. End the report with a changelog derived from the commit plus the commit hash and push result. Do not open a pull request unless explicitly requested.
