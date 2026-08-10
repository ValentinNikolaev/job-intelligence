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
careers text. Intake and analysis may proceed for that vacancy, but preparation is a
separate user-gated action.

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
5. Do not prepare merely because the score meets `prepare_min_score`. Prepare only
   when the user has explicitly asked to prepare this vacancy or has clearly approved
   preparation after intake/analysis. The approval must identify the vacancy by ID,
   registry directory, or an unambiguous reference to the manually supplied vacancy.
   Follow the two-wave preparation contract below and keep every handoff and final
   draft keyed to this vacancy under `.codex-work/application/<directory>/`.
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

### Two-wave preparation

Apply this protocol independently to every explicitly selected vacancy:

1. In Wave 1, run independent research, CV/evidence, and requirements/risks roles in
   parallel when subagent slots are available. Research receives only this vacancy's
   meta/job/company files plus minimal candidate motivation hooks, not the full CV, and
   writes `parts/research.md`. CV/evidence receives this vacancy and configured
   candidate sources, performs no web research, and writes `parts/evidence-map.md` with
   both the evidence mapping and a complete proposed CV draft. Requirements/risks
   receives this vacancy and candidate evidence and writes
   `parts/requirements-risks.md`. A Wave 1 role must not publish or write a final
   artifact.
2. The main agent reconciles the three handoffs, checks every proposed claim against the
   candidate evidence, and writes the final `cv.md`. Wave 2 cannot start before this CV
   is fixed.
3. In Wave 2, run cover-letter, interview-preparation, and application-analysis roles in
   parallel when slots are available. They exclusively own `cover-letter.md`,
   `interview-preparation.md`, and `analysis.md`, respectively. Cover letter receives
   the vacancy, final CV, verified research, and only required candidate evidence and
   must invoke `$write-cover-letter`; interview receives the vacancy, final CV,
   requirements/risks handoff, and verified research without browsing again; analysis
   receives the vacancy, final CV, and all Wave 1 handoffs.
4. The main agent performs one cross-file consistency and claim check, then runs
   `validate-application` once and `prepare` once. Subagents never run those commands or
   edit another role's file.
5. If subagents or enough slots are unavailable, execute the same roles sequentially,
   preserving the two waves, handoff files, and exclusive ownership. Do not claim a
   model switch that the current Codex task did not perform.

For batches, parallel work may be distributed across vacancies, but each agent and
artifact must remain scoped to exactly one vacancy. Never combine or reuse candidate
evidence, company research, requirements, wording, or handoffs across vacancy
directories. No role may reread unneeded sources, the full registry, or another
vacancy's files.

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
