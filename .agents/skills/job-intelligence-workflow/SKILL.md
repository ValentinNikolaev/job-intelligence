---
name: job-intelligence-workflow
description: Run the repository's vacancy collection, match analysis, vacancy-status management, and vacancy-specific application preparation without project code calling the OpenAI Platform API. Use for Job Intelligence scheduled runs, processing pending vacancies, publishing Codex-produced drafts, manually changing vacancy status, and orchestrating the mandatory final independent vacancy-catalog generation.
---

# Job Intelligence Workflow

Obey `AGENTS.md` first. Never call the OpenAI Platform API from repository code. Use the model already selected for the active Codex task and never claim to have switched models from inside the task.

## Choose one mode

- For collection, run `python run.py all`, regenerate the registry index, and report source failures separately.
- For analysis, follow `references/analyze.md` and process a sealed batch of up to 15
  pending vacancies.
- For application packages, follow `references/prepare.md` with workflow `prepare` and
  process one to 10 fresh vacancies explicitly selected by the user through vacancy IDs
  or registry directories. Use `$write-cover-letter` for every letter and never expand
  the selection to `all`.
- For a user-requested status change, run `python run.py status <vacancy-id-or-directory> <status>`. Never change status without an explicit user request. Preserve the complete history through the command.

Read `config/codex-workflows.yaml` before model-dependent work. The selected Scheduled Task or chat must use the corresponding model and reasoning level. Pass the workflow name to the deterministic publisher; it derives the only allowed model label from policy. If the requested model is unavailable in the current Codex surface, tell the user and do not publish under that workflow.

## Common rules

1. For preparation, read only the explicitly selected batch, the configured candidate
   source files, and the relevant prompt. Handle one selected vacancy at a time and do
   not compare vacancies or reuse vacancy-specific research, keywords, or draft content.
   For analysis, read only the sealed input pack and the batch prompt; do not compare
   vacancies or read another vacancy's artifacts.
2. Write model-produced drafts only under `.codex-work/`; the directory is ignored by Git.
3. Require `$write-cover-letter` from the highest installed version of
   `agent-plugins@valentin-agent-plugins` available in the active task during
   preparation. Stop if the active task cannot load it; do not recreate the retired
   inline drafting flow.
4. Publish through `run.py` so schema validation, hashes, atomic writes, DOCX conversion, and cache metadata remain deterministic.
5. If publication fails validation, fix the draft and retry. Do not edit generated cache metadata by hand.
6. Never submit applications or contact employers.

## Mandatory final catalog step

After every successful collection, analysis, preparation, or manual status change, use `$generate-vacancy-catalog` and run its deterministic command as a separate operating-system process. Include its result in the final report. Do not import or call the catalog generator in-process.

## Mandatory Git finalization

After the catalog process, run the relevant tests and API-prohibition scan. Inspect the full diff, stage all added, changed, and deleted project files with `git add -A`, commit once, and push the current branch to `origin`. Never stage ignored secrets or local work files. If the tree is unchanged, skip the commit and push. End the report with a changelog derived from the commit plus the commit hash and push result. Do not open a pull request unless explicitly requested.
