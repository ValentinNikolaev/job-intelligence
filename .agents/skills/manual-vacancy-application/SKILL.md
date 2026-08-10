---
name: manual-vacancy-application
description: Intake and analyze one manually sourced vacancy, and prepare its Job Intelligence application package only after explicit user approval. Use when the user provides a raw vacancy, link, pasted job post, recruiter message, or company careers text; do not infer preparation consent from intake alone.
---

# Manual Vacancy Application

Obey `AGENTS.md` first. Never add or restore OpenAI Platform API calls, SDK usage, API keys, OpenAI-compatible model endpoints, or model-proxy code. This skill is a Codex-only orchestration wrapper over deterministic manual intake commands and `$job-intelligence-workflow`.

## Goal

Read `prompts/job-intelligence-workflow.md` before starting. That file is the shared
repository contract used by this interactive URL flow and by Scheduled Tasks; this
skill owns the manual intake orchestration and vacancy isolation.

Turn one raw/manual vacancy into an analyzed registry entry, and into a prepared
application package only after an explicit user gateway decision:

- Publish the extracted vacancy with the deterministic `add-manual` command.
- Analyze only the newly published vacancy when no acceptable match already exists.
- If and only if the user explicitly asks to prepare the vacancy, prepare the
  application artifacts through `$job-intelligence-workflow`, using
  `$write-cover-letter` for `cover-letter.md`, then publish the deterministic
  DOCX-backed package.

Do not bypass deterministic project commands. Do not hand-edit published registry artifacts or cache metadata.

## Workflow

1. Run the one-time Git preflight in `prompts/job-intelligence-workflow.md` before
   reading vacancy or candidate evidence. Resolve a behind or diverged branch and
   unexpected tracked changes in workflow output paths first; preserve unrelated user
   changes. Then read `config/codex-workflows.yaml` and identify the configured model profiles,
   reasoning levels, and `prepare_min_score`. Use the workflow default or an explicitly
   selected `--model-profile`. You cannot switch the current task model from inside
   the repo; if the active task is not using the selected profile, tell the user before
   publishing model-dependent results.
2. Extract fields from the supplied vacancy text or link, ask only for missing or
   ambiguous required evidence, write one manual draft under `.codex-work/manual-job/`,
   and publish it with `python run.py add-manual --input <draft.yaml>`.
3. Capture the newly published vacancy directory from the `add-manual` command output.
   Do not rediscover it through a queue or broad registry scan. From this point, keep
   the workflow scoped to that single vacancy.
4. If the vacancy has no current `match.yaml`, analyze only this directory. Read its
   vacancy files, the configured candidate evidence, and `prompts/vacancy-match.md`;
   write one result draft under `.codex-work/manual-analysis/`, then publish it with
   `python run.py analyze <vacancy-directory> --input <draft.yaml> --workflow analyze --model-profile <selected-profile>`.
   Do not run triage, `pending analyze all`, `analyze-batch`, or any queue command for
   this manual flow, and do not read unrelated vacancy directories.
5. Treat the published match score only as an eligibility signal, never as consent:
   - If score is below `prepare_min_score`, do not prepare and report the reason.
   - If score is at least `prepare_min_score` but the user has not explicitly requested
     preparation, stop after intake/analysis and report that user approval is required.
   - If score is at least `prepare_min_score` and the user explicitly requests
     preparation for this vacancy, use workflow `prepare`.
6. Prepare exactly this vacancy with `$job-intelligence-workflow` preparation rules and
   its two-wave orchestration. In Wave 1, run research, CV/evidence, and
   requirements/risks roles in parallel when subagent slots are available. Research
   receives meta/job/company plus minimal candidate motivation hooks, not the full CV;
   CV/evidence receives the vacancy and configured candidate sources, performs no web
   research, and includes a complete proposed CV draft in `evidence-map.md`;
   requirements/risks receives the vacancy and candidate evidence. Each writes only its
   exclusive handoff under `.codex-work/application/<vacancy-directory>/parts/`:
   `research.md`, `evidence-map.md`, or `requirements-risks.md`. No Wave 1 role may
   publish, run a deterministic project command, or write a final artifact. The main
   agent reconciles the handoffs, rejects unsupported claims, and writes the final
   `cv.md`. Limit the overall preparation scope to this vacancy's `meta.yaml`, `job.md`,
   optional `company.md`, configured candidate source files, and
   `prompts/vacancy-application.md`; route only the subset assigned to each role.
   Research in one pass using the posting plus at most two primary company sources
   unless a critical eligibility or company-identity fact remains unresolved.
7. Start Wave 2 only after the final CV is fixed. Run cover-letter,
   interview-preparation, and application-analysis roles in parallel when slots are
   available, with exclusive ownership of `cover-letter.md`,
   `interview-preparation.md`, and `analysis.md`. Cover letter receives the vacancy,
   final CV, verified research, and only required candidate evidence; interview receives
   the vacancy, final CV, requirements/risks, and verified research without browsing
   again; analysis receives the vacancy, final CV, and all Wave 1 handoffs. The
   cover-letter role must invoke
   `$write-cover-letter`; stop if that skill is unavailable and never substitute the
   retired inline drafting logic. If subagents or enough slots are unavailable, run the
   same roles sequentially with the same handoffs, wave boundary, and file ownership.
   No role may read the full registry, another vacancy, or inputs it does not need. Do
   not claim a model switch inside the active task.
8. The main agent performs one cross-file consistency and claim-grounding pass after
   Wave 2. Then run the single combined deterministic draft check:
   `python run.py validate-application <vacancy-directory> --input .codex-work/application/<vacancy-directory>`.
   After it succeeds, publish once with `python run.py prepare <vacancy-directory> --input .codex-work/application/<vacancy-directory> --workflow prepare --model-profile <selected-profile>`.
   If validation fails, fix only its cause and rerun the validator. If DOCX conversion
   fails after validation, fix only that deterministic issue and retry publication.
9. Confirm the application directory contains the published Markdown artifacts, DOCX artifacts, and `manifest.yaml`.
10. Regenerate the vacancy catalog through `$generate-vacancy-catalog`, then run the
   required tests and prohibited-API scan exactly once. Inspect the full diff, stage,
   commit, and push when repository files changed. Repeat only a specific failed check
   after correcting its cause.

## Output Rules

Report the vacancy directory, match score, chosen workflow, generated CV and cover-letter artifact paths, catalog result, commit hash, and push result. Never submit the application or contact the employer.
