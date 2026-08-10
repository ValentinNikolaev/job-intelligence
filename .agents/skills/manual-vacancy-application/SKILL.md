---
name: manual-vacancy-application
description: Orchestrate one manually sourced vacancy into a complete Job Intelligence application package. Use when the user provides a raw vacancy, link, pasted job post, recruiter message, or company careers text and wants Codex to add it, analyze only that vacancy if needed, and prepare the existing CV and cover-letter artifacts without adding OpenAI Platform API calls to project code.
---

# Manual Vacancy Application

Obey `AGENTS.md` first. Never add or restore OpenAI Platform API calls, SDK usage, API keys, OpenAI-compatible model endpoints, or model-proxy code. This skill is a Codex-only orchestration wrapper over deterministic manual intake commands and `$job-intelligence-workflow`.

## Goal

Read `prompts/job-intelligence-workflow.md` before starting. That file is the shared
repository contract used by this interactive URL flow and by Scheduled Tasks; this
skill owns the manual intake orchestration and vacancy isolation.

Turn one raw/manual vacancy into a prepared application package:

- Publish the extracted vacancy with the deterministic `add-manual` command.
- Analyze only the newly published vacancy when no acceptable match already exists.
- Prepare the application artifacts through `$job-intelligence-workflow`, using
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
5. Decide preparation from the published match score:
   - If score is below `prepare_min_score`, stop after catalog/check/finalization and report that no CV or cover letter should be prepared under repository policy.
   - If score is at least `prepare_min_score`, use workflow `prepare`. Preparation starts only from the vacancy ID or registry directory explicitly provided by the user.
6. Prepare exactly this vacancy with `$job-intelligence-workflow` preparation rules.
   Read only its `meta.yaml`, `job.md`, optional `company.md`, configured candidate
   source files, and `prompts/vacancy-application.md`. Research in one pass using the
   posting plus at most two primary company sources unless a critical eligibility or
   company-identity fact remains unresolved. Invoke `$write-cover-letter` for the final
   letter and stop if that skill is unavailable; do not substitute the retired inline
   drafting logic. Write drafts under `.codex-work/application/<vacancy-directory>/`.
7. Complete all four drafts, then run the single combined deterministic draft check:
   `python run.py validate-application <vacancy-directory> --input .codex-work/application/<vacancy-directory>`.
   After it succeeds, publish once with `python run.py prepare <vacancy-directory> --input .codex-work/application/<vacancy-directory> --workflow prepare --model-profile <selected-profile>`.
   If validation fails, fix only its cause and rerun the validator. If DOCX conversion
   fails after validation, fix only that deterministic issue and retry publication.
8. Confirm the application directory contains the published Markdown artifacts, DOCX artifacts, and `manifest.yaml`.
9. Regenerate the vacancy catalog through `$generate-vacancy-catalog`, then run the
   required tests and prohibited-API scan exactly once. Inspect the full diff, stage,
   commit, and push when repository files changed. Repeat only a specific failed check
   after correcting its cause.

## Output Rules

Report the vacancy directory, match score, chosen workflow, generated CV and cover-letter artifact paths, catalog result, commit hash, and push result. Never submit the application or contact the employer.
