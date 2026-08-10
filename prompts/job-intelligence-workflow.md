# Job Intelligence workflow contract

This file is the shared execution contract for both interactive Codex tasks and
Scheduled Tasks. A launcher may provide a vacancy URL, pasted vacancy text, an
explicit registry directory, or a sealed analysis batch. The launcher is not the
workflow: it must read this contract and then apply the mode that matches its input.

## Modes

### `manual-application`

Use when the user supplies a vacancy URL, raw job post, recruiter message, or company
careers text and asks to prepare it.

1. Read `AGENTS.md`, `config/codex-workflows.yaml`, this file, and the
   `manual-vacancy-application` skill.
2. Extract the vacancy into an ignored draft under `.codex-work/manual-job/` and
   publish it only with `python run.py add-manual --input <draft.yaml>`.
3. Keep the run scoped to the newly published vacancy. Do not select `all` and do not
   compare it with another vacancy.
4. If no current match exists, create a sealed analysis input and evaluate that one
   vacancy independently. Publish with `python run.py analyze-batch` or
   `python run.py analyze`, passing the selected `--model-profile` when needed.
5. Prepare only when the published score meets `prepare_min_score`. Write the four
   vacancy-keyed Markdown drafts under `.codex-work/application/<directory>/` and
   publish them with `python run.py prepare <directory> --input .codex-work/application
   --workflow prepare [--model-profile <profile>]`.
6. Invoke `$write-cover-letter` for `cover-letter.md`; never replace it with inline
   letter logic. Never submit the application or contact the employer.

### `scheduled-analysis`

Use only for the sealed pending-analysis queue. Acquire the workflow lock, build a
fresh pack, evaluate every pack item independently, publish the complete keyed result
mapping, regenerate the catalog, and perform the repository checks and Git handoff.
Do not prepare applications automatically from a schedule.

### `manual-status`

Use only after the user explicitly requests a status change. Run `python run.py status`
with the requested status and preserve the audit history.

## Model selection

Read the `model_profiles` and workflow `allowed_profiles` entries in
`config/codex-workflows.yaml`. Use the workflow default unless the launcher supplies
`--model-profile <name>`. The selected Codex task or Scheduled Task must actually use
the model and reasoning named by that profile. The repository cannot switch the active
Codex model from inside a running task; it only resolves the allowed provenance label
for deterministic publication.

Never pass an arbitrary model label. If the requested profile is not allowed, stop
before model-dependent publication and report the configuration mismatch.

## Evidence and isolation

- Treat `registry/candidate/*.md` as immutable evidence; never invent claims.
- Read only the selected vacancy, configured candidate sources, and the relevant
  specialized prompt (`vacancy-match.md` or `vacancy-application.md`).
- Keep all model-produced drafts in `.codex-work/` until deterministic publication.
- Use the deterministic project commands for validation, hashing, atomic publication,
  DOCX conversion, and index generation.
