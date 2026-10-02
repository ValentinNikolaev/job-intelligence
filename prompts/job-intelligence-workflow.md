# Job Intelligence workflow contract

Read `config/data-services.yaml` and run `python run.py storage doctor` before
operational work. MongoDB is the sole source after cutover; frozen registry YAML and
description files must not be used as live evidence. Use the sealed pack for scheduled
analysis, and `python run.py storage vacancy-context --selector <selected-id-or-directory>
--output .codex-work/vacancy-context.json` for an explicitly selected manual analysis or
preparation vacancy. Candidate evidence and generated application documents stay files.

For any explicitly selected preparation batch, run `python run.py prepare-preflight
<selector-1> [<selector-2> ...] --workflow prepare [--model-profile <profile>]
[--document <document>]` before reading vacancy evidence or drafting. It is a
fail-closed, storage-backed gate; MongoDB canonical metadata is materialized only under
`.codex-work/vacancy-snapshots/`. Do not copy frozen registry files from another checkout.

This file is the shared execution contract for both interactive Codex tasks and
Scheduled Tasks. A launcher may provide a vacancy URL, pasted vacancy text, an
explicit registry directory, or a sealed analysis batch. The launcher is not the
workflow: it must read this contract and then apply the mode that matches its input.

## One-time repository preflight

Before reading candidate or vacancy evidence, browsing, or producing model-dependent
drafts, create or reuse an isolated managed worktree. Inspect the remote with `gh`.

1. Run `python scripts/finalize_repository.py preflight` in the isolated worktree.
   It uses `gh` for remote inspection, refuses any local changes, fetches, and only
   fast-forwards a clean checkout. Leave shared checkout changes untouched.
2. Re-read updated instructions and record the baseline revision. Treat unreadable
   paths as an access problem, never as confirmed deletions.

Before final publication, run `python scripts/finalize_repository.py review`, inspect
its complete `.codex-work/finalization/review.patch`, then run `publish --subject
<specific-subject>`. The finalizer rechecks the remote head and non-force pushes one
reviewed commit. It stops if integration changes reviewed files, has a conflict, or
the local/remote tree lacks the repository spine required by the workflow. Do not call
`gh api` to create Git trees, commits, or branch refs directly: `publish` and the
reviewed `publish-api` fallback are the only publication paths.

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
   A current match produced by any approved `analyze` profile can support preparation.
   Preserve its actual model label and score alongside the preparation model. If the
   match is missing or stale, run a real analysis in an allowed analysis task; never
   change only the stored model label or reuse a stale judgment as if it were new.
5. Do not prepare merely because the score meets `prepare_min_score`. Prepare only
   when the user has explicitly asked to prepare this vacancy or has clearly approved
   preparation after intake/analysis. The approval must identify the vacancy by ID,
   registry directory, or an unambiguous reference to the manually supplied vacancy.
   Follow the two-wave preparation contract below and keep every handoff and final
   draft keyed to this vacancy under `.codex-work/application/<directory>/`.
   The default is the full four-document package. If the user explicitly requests
   exactly one document, generate only it and use the matching `--document` value for
   pending, validation, and publication.
6. When a cover letter is selected, invoke `$write-cover-letter` for `cover-letter.md`; never replace it with inline
   letter logic. Never submit the application or contact the employer.
7. Use the posting plus at most two primary company sources in one research pass. Stop
   when company identity, role context, and one defensible motivation point are
   verified. Exceed the budget only for a critical unresolved eligibility or company-
   identity fact, and record the reason.
8. Complete all four drafts by default, or only the explicitly selected draft, then run
   `python run.py lint-application <directory> --input .codex-work/application/<directory>
   [--document <document>]`, preview any selected CV, and run the combined deterministic
   draft check: `python run.py validate-application <directory> --input
   .codex-work/application/<directory> [--document <document>]`. After both checks succeed, publish once with
   `python run.py prepare <directory> --input .codex-work/application/<directory>
   --workflow prepare [--model-profile <profile>] [--document <document>]`. After a validation failure,
   correct only its cause, rerun the validator, and do not publish until it passes.

### Two-wave preparation

Apply this protocol independently to every explicitly selected vacancy:

Use the full two-wave protocol by default. For an explicit single-document request,
run only the roles and handoffs necessary for that document; preserve any existing
unselected artifacts. The cover-letter skill is required only when the selected scope
includes `cover-letter`.

Before Wave 1, confirm each selected vacancy has a current match produced by an
approved analysis profile. Reuse that match across preparation profiles when the
vacancy, candidate, and match prompt versions still agree. If no current match exists,
create and publish a new isolated match draft in an allowed analysis task before
drafting application artifacts. Preserve both model labels as content provenance.

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
4. Before validation, write `.codex-work/application/<directory>/quality.yaml`, schema
   version 2, with `workflow: two-wave`; cover-letter skill name/version;
   `workbench_complete: true`; two evidence stories with `candidate_source`; a
   company-motivation fact and `source_url`; and final `claim_grounding: true` and
   `cross_file_consistency: true`.
5. The main agent performs one cross-file consistency and claim check, runs
   `lint-application` once per finalized vacancy, previews selected CV drafts with
   `python run.py documents preview-cv .codex-work/application/<directory>/cv.md`,
   inspects every rendered page, then runs `validate-application` once per finalized
   vacancy and one batch `prepare` call after all drafts pass. Subagents never run those commands or
   edit another role's file. The validator checks the quality contract, required
   handoffs, provenance, word counts, and hashes; the manifest retains them.
6. If subagents or enough slots are unavailable, execute the same roles sequentially,
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
catalog state, then inspect the complete staged diff and perform the isolated-worktree
finalization. Repeat only a
specific failed check after correcting its cause; do not duplicate the full suite or
rerun the model workflow. For the Codex-authored commit, derive a natural, human-written
subject from the staged diff and name the concrete outcome, including a useful count or
vacancy context when relevant. Do not choose from the GitHub Actions templates or use a
generic `update data`, `update files`, `workflow changes`, or `automated update` subject.
Keep run identifiers and mechanical file counts in the commit body.

## Application quality and lifecycle extensions

New preparation uses quality schema 2; see `docs/application-quality.md` for evidence
bank/claim ledger, compact format, final CV audit, export validation and receipt
contracts. Existing schema 1 artifacts remain explicitly legacy and require real
regeneration to meet v2. Ancillary form answers, interview practice/debriefs and
follow-up drafts follow `prompts/application-lifecycle.md` only after explicit
approval for the named vacancy. Recording a confirmed submission preserves exact
sent files; it never changes vacancy status automatically.

`AGENTS.md` permits only the reviewed finalizer's narrow local Git operations in an
isolated worktree. Use `gh` for remote inspection and never force a remote update or
overwrite unrelated local changes.
