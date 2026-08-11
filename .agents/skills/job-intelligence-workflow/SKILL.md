---
name: job-intelligence-workflow
description: Run the repository's vacancy collection, match analysis, vacancy-status management, and vacancy-specific application preparation without project code calling the OpenAI Platform API. Use for Job Intelligence scheduled runs, processing pending vacancies, publishing Codex-produced drafts, manually changing vacancy status, and orchestrating the mandatory final independent vacancy-catalog generation.
---

# Job Intelligence Workflow

Obey `AGENTS.md` first. Never call the OpenAI Platform API from repository code. Use the model already selected for the active Codex task and never claim to have switched models from inside the task.

## Choose one mode

Before choosing a mode, read `prompts/job-intelligence-workflow.md`. It is the shared
execution contract for interactive and scheduled launchers; this skill supplies the
tool sequencing and safety boundaries around that contract.

Before reading vacancy or candidate evidence, researching, or drafting, perform the
one-time Git preflight from the shared contract. Unless the launcher already supplied
a clean short `codex/*` worktree, create one with `python run.py worktree <task-name>`
and continue there. Preserve unrelated user changes in the original checkout. GitHub
Actions is the only writer to `main`; do not repeat the fetch or push Codex output to
`main` during the same run.

- For collection, run `python run.py all`, regenerate the registry index, and report source failures separately.
- For analysis, follow `references/analyze.md` and process a sealed batch of up to 15
  pending vacancies.
- For a manually supplied vacancy, use `$manual-vacancy-application`. Analyze its newly
  published registry directory directly; do not route that one-vacancy run through
  triage, `pending analyze all`, or the scheduled sealed queue.
- For application packages, follow `references/prepare.md` with workflow `prepare` and
  process one to 10 fresh vacancies explicitly selected by the user through vacancy IDs
  or registry directories. Use `$write-cover-letter` for every letter and never expand
  the selection to `all`.
- For a user-requested status change, run `python run.py status <vacancy-id-or-directory> <status>`. Never change status without an explicit user request. Preserve the complete history through the command.

Read `config/codex-workflows.yaml` before model-dependent work. Select the workflow's
default model profile unless the launcher explicitly supplies `--model-profile`; the
selected Scheduled Task or chat must use the corresponding model and reasoning level.
Pass the workflow and optional model profile to the deterministic publisher; it derives
the only allowed model label from policy. If the requested model is unavailable in the
current Codex surface, tell the user and do not publish under that profile.

## Common rules

1. For preparation, read only the explicitly selected batch, the configured candidate
   source files, and the relevant prompt. Handle one selected vacancy at a time and do
   not compare vacancies or reuse vacancy-specific research, keywords, or draft content.
   For scheduled analysis, read only the sealed input pack and the batch prompt. For a
   manual vacancy, read only that selected directory, its configured candidate evidence,
   and `prompts/vacancy-match.md`. In either mode, do not compare vacancies or read
   another vacancy's artifacts.
   Use `registry/candidate/evidence-index.md` to route evidence reads, then open only
   the cited primary sections needed to verify selected claims. Do not substitute the
   index for the configured files used by deterministic hashes.
2. Write model-produced drafts only under `.codex-work/`; the directory is ignored by Git.
3. Require `$write-cover-letter` from the highest installed version of
   `agent-plugins@valentin-agent-plugins` available in the active task during
   preparation. Stop if the active task cannot load it; do not recreate the retired
   inline drafting flow.
4. Publish through `run.py` so schema validation, hashes, atomic writes, DOCX conversion, and cache metadata remain deterministic.
5. For preparation, use the two-wave orchestration and exclusive file ownership in
   `references/prepare.md`. Parallelize independent roles only when subagent slots are
   available; otherwise preserve the same handoffs and run them sequentially. The main
   agent alone finalizes the CV, performs the cross-file claim check, validates, and
   publishes.
6. After all four application drafts for a vacancy are complete, run
   `python run.py validate-application <job-directory-or-vacancy-id> --input
   <draft-directory>` once as the combined prepublication check. Publish only after it
   succeeds. If validation fails, fix only its cause and rerun the validator. Do not
   edit generated cache metadata by hand.
7. Never submit applications or contact employers.

## Mandatory final catalog step

After every successful collection, analysis, preparation, or manual status change, use `$generate-vacancy-catalog` and run its deterministic command as a separate operating-system process. Include its result in the final report. Do not import or call the catalog generator in-process.

## Mandatory Git finalization

After the catalog process, run the relevant tests and API-prohibition scan exactly once,
then inspect the full diff, stage all added, changed, and deleted project files with
`git add -A`, commit once, and push the current branch to `origin`. Repeat only the
specific failed check after correcting its cause; do not rerun the entire workflow or
full check suite without a failure. For a Codex-authored commit, inspect the staged diff
and write a natural, human-written subject that names the run's actual result, using a
useful count or vacancy context when relevant. Do not reuse or randomly select from the
GitHub Actions templates, and do not use a generic `update data`, `update files`, `workflow
changes`, or `automated update` subject. Never stage ignored secrets or local work
files. If the tree is unchanged, skip the commit and push. End the report with a
changelog derived from the commit plus the commit hash and push result. Do not open a
pull request unless explicitly requested.
