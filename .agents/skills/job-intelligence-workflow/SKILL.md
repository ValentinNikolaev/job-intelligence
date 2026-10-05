---
name: job-intelligence-workflow
description: Run the repository's vacancy collection, match analysis, vacancy-status management, and vacancy-specific application preparation without project code calling the OpenAI Platform API. Use for Job Intelligence scheduled runs, processing pending vacancies, publishing Codex-produced drafts, manually changing vacancy status, and orchestrating the mandatory final independent vacancy-catalog generation.
---

# Job Intelligence Workflow

Obey `AGENTS.md` first. Never call the OpenAI Platform API from repository code. Use the model already selected for the active Codex task and never claim to have switched models from inside the task.

Read `config/data-services.yaml` before operational work and run `python run.py storage
doctor`. When MongoDB is selected, old registry YAML and description Markdown are frozen
migration evidence, not current inputs. For each explicitly selected manual analysis or
preparation vacancy, obtain current content with `python run.py storage vacancy-context
--selector <vacancy-id-or-directory> --output .codex-work/vacancy-context.json` and read
that export. Scheduled analysis continues to use its deterministic sealed input pack.
Read candidate evidence and application artifacts from their existing file paths.
If storage is unavailable, stop the affected operation; never switch to old files.

Before a preparation editor receives any selected vacancy, run `python run.py
prepare-preflight <selector-1> [<selector-2> ...] --workflow prepare [--model-profile
<profile>] [--document <document>]`. The command is read-only apart from an ignored
`.codex-work/vacancy-snapshots/` view. It resolves selectors against canonical storage,
checks the adapter, required metadata, current match from an approved analysis
profile, score eligibility, and hard rejection. A failed preflight means no drafts,
preview, conversion, or publication.

## Choose one mode

Before choosing a mode, read `prompts/job-intelligence-workflow.md`. It is the shared
execution contract for interactive and scheduled launchers; this skill supplies the
tool sequencing and safety boundaries around that contract.

Before reading vacancy or candidate evidence, researching, or drafting, perform the
one-time repository preflight from the shared contract in an isolated managed worktree. Resolve a behind or diverged branch
and any unexpected tracked changes in workflow output paths before model-dependent
work. Preserve unrelated user changes. Do not repeat the initial synchronization during the same run.

- For collection, run `python run.py all`, regenerate the registry index, and report source failures separately.
- For analysis, follow `references/analyze.md` and process a sealed batch of up to 15
  pending vacancies.
- For a manually supplied vacancy, use `$manual-vacancy-application`. Analyze its newly
  published registry directory directly; do not route that one-vacancy run through
  triage, `pending analyze all`, or the scheduled sealed queue.
- For application packages, follow `references/prepare.md` with workflow `prepare` and
  process one to 10 fresh vacancies explicitly selected by the user through vacancy IDs
  or registry directories. Generate the full package by default; when the user
  explicitly names exactly one document, use the matching `--document` mode. Use
  `$write-cover-letter` for every selected letter and never expand the selection to
  `all`.
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
2. Write model-produced drafts only under `.codex-work/`; the directory is ignored by Git.
3. When a cover letter is selected, require `$write-cover-letter` from the highest installed version of
   `agent-plugins@valentin-agent-plugins` available in the active task during
   preparation. Stop if the active task cannot load it; do not recreate the retired
   inline drafting flow.
4. Publish through `run.py` so schema validation, hashes, atomic writes, DOCX conversion, and cache metadata remain deterministic.
5. For default full-package preparation, use the two-wave orchestration and exclusive
   file ownership in `references/prepare.md`. For an explicit single-document request,
   run only the roles and handoffs required by that document. The main agent alone
   finalizes selected drafts, performs the applicable claim check, validates, and
   publishes.
6. A full-package draft must include `.codex-work/application/<vacancy-directory>/quality.yaml`
   with `schema_version: 2`: `workflow: two-wave`; invoked cover-letter skill name and
   version; `workbench_complete: true`; two evidence stories with `candidate_source`;
   company-motivation fact with `source_url`; and final-review values
   `claim_grounding: true` and `cross_file_consistency: true`.
   Apply the recent-experience and impact/judgment editorial gates in
   `references/prepare.md` before recording that final review. A total bullet
   count never substitutes for a role-by-role hiring-manager review.
   Preserve every documented employer and engagement in the final CV. Compare the
   complete candidate career inventory with `Experience`, `Additional Experience`,
   and `Earlier Experience`; retain short dated chronology entries when detailed
   bullets are unnecessary. Never omit a company for relevance, page count, age,
   or insufficient achievement bullets. Review overlap and uncertain dates without
   inventing continuity. Record every company's representation in `cv_audit.role_coverage`.
   Every displayed Experience role ending within the five years through the
   validator's reference month needs at least three distinct, source-backed
   Experience bullets; older displayed roles need at least two. Technologies
   lines never count, and no factual-distinctness rule permits filler or a
   rephrased duplicate.
7. After the selected drafts for a vacancy are complete, run
   `python run.py lint-application <job-directory-or-vacancy-id> --input
   <draft-directory> [--document <document>]`, then preview any selected CV, and then
   run `python run.py validate-application <job-directory-or-vacancy-id> --input
   <draft-directory> [--document <document>]` once as the combined prepublication
   check. Omit `--document` for the default full package. Publish only after both
   checks succeed. If either check fails, fix only its cause and rerun the applicable
   check. Do not edit generated cache metadata by hand.
   `validate-application` must check that quality contract, required handoffs, document
   minima, provenance, word counts, and hashes before publication. The final manifest
   must retain the quality contract, provenance, word counts, and hashes.
   Between those checks, preview a selected CV draft with `python run.py documents preview-cv
   .codex-work/application/<vacancy-directory>/cv.md` and inspect its rendered pages.
   Reuse the preview only while its draft and converter options remain unchanged.
8. Never submit applications or contact employers.
9. After preparation, the final report must list the application-package directory for
   every successfully prepared vacancy and the direct source URL for that vacancy. Give
   its absolute local path to
   `registry/jobs/<vacancy-directory>/application/` and, after repository publication,
   a stable repository URL pinned to the published commit. If the source posting is no
   longer reachable, still return its recorded direct URL and mark it unavailable.
   Explicitly identify each selected vacancy that has no package and why; never make the
   user infer package paths or vacancy URLs from IDs, catalog entries, chat history, or
   the changelog.

## Mandatory final catalog step

After every successful collection, analysis, preparation, or manual status change, use `$generate-vacancy-catalog` and run its deterministic command as a separate operating-system process. Include its result in the final report. Do not import or call the catalog generator in-process.

## Mandatory repository finalization

After the catalog process, run the relevant tests and API-prohibition scan exactly once, then
run `python scripts/finalize_repository.py review` in the isolated worktree and inspect
the complete staged patch. Publish with `python scripts/finalize_repository.py publish
--subject <specific-subject>`. The finalizer creates one local commit, integrates a
concurrent remote advance when reviewed files stay identical, and pushes without force.
Do not synchronize a dirty shared checkout or include ignored secrets, caches, or local work files.
For a Codex-authored commit, write a natural, human-written imperative subject from the complete diff naming
the actual result, with useful counts or vacancy context. Do not use a generic `update data`, `update files`,
`workflow changes`, or `automated update` subject, or GitHub Actions templates. If nothing changed, skip publication. End the report
with a changelog, commit hash, and publication result. Do not open a pull request
unless explicitly requested.

## Application quality and lifecycle extensions

New preparation uses quality schema 2; see `docs/application-quality.md` for evidence
bank/claim ledger, compact format, final CV audit, export validation and receipt
contracts. Existing schema 1 artifacts remain explicitly legacy and require real
regeneration to meet v2. Ancillary form answers, interview practice/debriefs and
follow-up drafts follow `prompts/application-lifecycle.md` only after explicit
approval for the named vacancy. Recording a confirmed submission preserves exact
sent files; it never changes vacancy status automatically.

