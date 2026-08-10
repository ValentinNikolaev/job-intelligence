# Job Intelligence workflow contract

This file is the shared execution contract for both interactive Codex tasks and
Scheduled Tasks. A launcher may provide a vacancy URL, pasted vacancy text, an
explicit registry directory, or a sealed analysis batch. The launcher is not the
workflow: it must read this contract and then apply the mode that matches its input.

## One-time Git preflight

Before reading candidate or vacancy evidence, browsing, or producing model-dependent
drafts, inspect the repository once:

1. Run `git status --short` and identify any existing tracked changes.
2. Run `git fetch origin`, identify the current branch and its upstream, and compare
   `HEAD` with that upstream using `git rev-list --left-right --count`.
3. If the branch is behind or diverged, integrate the upstream safely before generating
   artifacts. If tracked changes overlap workflow output paths, resolve ownership first.
   Preserve unrelated user work.

If sandbox or ACL restrictions make readable tracked directories appear deleted, rerun
the read-only Git checks with repository access before treating those paths as changes.
Do not repeat the fetch later in the same run; the final handoff needs a diff/status
check, not a second preflight.

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
4. If no current match exists, evaluate this vacancy independently, write one result
   draft under `.codex-work/manual-analysis/`, and publish it directly with
   `python run.py analyze <directory> --input <draft.yaml> --workflow analyze
   [--model-profile <profile>]`. Do not run triage, `pending analyze all`,
   `analyze-batch`, or another queue command in this mode.
5. Prepare only when the published score meets `prepare_min_score`. Write the four
   vacancy-keyed Markdown drafts under `.codex-work/application/<directory>/`.
6. Invoke `$write-cover-letter` for `cover-letter.md`; never replace it with inline
   letter logic. Never submit the application or contact the employer.
7. Use the posting plus at most two primary company sources in one research pass. Stop
   when company identity, role context, and one defensible motivation point are
   verified. Exceed the budget only for a critical unresolved eligibility or company-
   identity fact, and record the reason.
8. Complete all four drafts, then run the single combined deterministic draft check:
   `python run.py validate-application <directory> --input
   .codex-work/application/<directory>`. After it succeeds, publish once with
   `python run.py prepare <directory> --input .codex-work/application/<directory>
   --workflow prepare [--model-profile <profile>]`. After a validation failure,
   correct only its cause, rerun the validator, and do not publish until it passes.

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

## Finalization

After deterministic publication, regenerate the catalog in its required separate
process. Run the required tests and prohibited-API scan exactly once after the final
catalog state, then inspect the complete diff and perform the Git handoff. Repeat only a
specific failed check after correcting its cause; do not duplicate the full suite or
rerun the model workflow.
