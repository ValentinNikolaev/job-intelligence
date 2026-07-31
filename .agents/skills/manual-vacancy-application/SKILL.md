------
name: manual-vacancy-application
description: Orchestrate a manually sourced vacancy into a complete Job Intelligence application package. Use when the user provides a raw vacancy, link, pasted job post, recruiter message, or company careers text and wants Codex to add it before manual-job-intake, analyze it if needed, and prepare the existing CV and cover-letter application artifacts without adding OpenAI Platform API calls to project code.
---

# Manual Vacancy Application

Obey `AGENTS.md` first. Never add or restore OpenAI Platform API calls, SDK usage, API keys, OpenAI-compatible model endpoints, or model-proxy code. This skill is a Codex-only orchestration wrapper over the existing `$manual-job-intake` and `$job-intelligence-workflow` skills.

## Goal

Turn one raw/manual vacancy into a prepared application package:

- Publish the vacancy through `$manual-job-intake`.
- Analyze only the newly published vacancy when no acceptable match already exists.
- Prepare the existing application artifacts through `$job-intelligence-workflow`: `cv.md`, `cover-letter.md`, `analysis.md`, and `interview-preparation.md`, then publish the deterministic DOCX-backed application package.

Do not bypass deterministic project commands. Do not hand-edit published registry artifacts or cache metadata.

## Workflow

1. Read `config/codex-workflows.yaml` and identify the configured models, reasoning levels, `prepare_min_score`, and `priority_score`. You cannot switch the current task model from inside the repo; if the active task is not using the needed workflow model, tell the user before publishing model-dependent results.
2. Use `$manual-job-intake` on the supplied vacancy text or link. Extract fields, ask only for missing or ambiguous required evidence, write the manual draft under `.codex-work/manual-job/`, and publish it with `python run.py add-manual --input <draft.yaml>`.
3. Capture the newly published vacancy directory from the command output or `git diff`. From this point, keep the workflow scoped to that single vacancy except for sealed queue commands.
4. If the vacancy has no `match.yaml`, analyze it with `$job-intelligence-workflow` in analysis mode:
   - Prefer marking the manual draft with `analysis_priority: 100` only when the user explicitly requested priority.
   - Run the normal triage and sealed analyze-pack commands.
   - If the sealed pack includes other vacancies, publish results only when the pack contract can be honored for every included directory. Otherwise stop and tell the user to create a dedicated analysis task or rerun when the queue can be safely processed.
   - Do not read unrelated vacancy directories while producing the match result.
5. Decide preparation from the published match score:
   - If score is below `prepare_min_score`, stop after catalog/check/finalization and report that no CV or cover letter should be prepared under repository policy.
   - If score is at least `prepare_min_score`, use workflow `prepare`. Priority-score vacancies are handled first by the queue, but the publisher uses the same workflow for all prepared applications.
6. Prepare exactly this vacancy with `$job-intelligence-workflow` preparation rules. Read only its `meta.yaml`, `job.md`, optional `company.md`, configured candidate source files, and `prompts/vacancy-application.md`. Write drafts under `.codex-work/application/<vacancy-directory>/`.
7. Publish with `python run.py prepare <vacancy-directory> --input .codex-work/application/<vacancy-directory> --workflow prepare`. If validation or DOCX conversion fails, fix the draft or deterministic converter issue and retry.
8. Confirm the application directory contains the published Markdown artifacts, DOCX artifacts, and `manifest.yaml`.
9. Regenerate the vacancy catalog through `$generate-vacancy-catalog`, run required tests and the prohibited-API scan, inspect the full diff, stage, commit, and push when repository files changed.

## Output Rules

Report the vacancy directory, match score, chosen workflow, generated CV and cover-letter artifact paths, catalog result, commit hash, and push result. Never submit the application or contact the employer.
