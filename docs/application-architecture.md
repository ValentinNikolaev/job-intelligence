# Vacancy-specific application workflow

## Goal and boundary

Generate an evidence-backed CV, cover letter, application analysis, and interview plan
for exactly one registry vacancy without modifying candidate source documents or calling
the OpenAI Platform API from project code.

```text
Codex task reads one vacancy + candidate sources + versioned prompt
        ↓
.codex-work/application/<vacancy>/ four Markdown drafts
        ↓
Python validates headings and content
        ↓
DOCX conversion + atomic application/ publication + manifest
```

The active interactive or Scheduled Codex task performs company research and writing.
`CodexApplicationDraftClient` only reads local Markdown. The deterministic publisher
validates all drafts, converts `cv.md` and `cover-letter.md`, and swaps the complete
`application/` directory with rollback so a failure preserves the previous package.

## Inputs and isolation

The Codex task reads the configured candidate source-of-truth files, one `meta.yaml`, one
`job.md`, optional `company.md`, and `prompts/vacancy-application.md`. Each task processes
exactly one vacancy. It must not read another vacancy's match or application files after
selection.

## Cache

`manifest.yaml` records candidate, vacancy, company, prompt, and actual Codex model-label
versions. All six output artifacts must exist. The `pending prepare` route compares those
values locally without invoking a model.

## Model routing

The single `prepare` route uses the model configured in `config/codex-workflows.yaml`.
Scores below `prepare_min_score` are not prepared. Fresh vacancies scoring at least
`priority_score` are prepared first; normal-score vacancies are prepared only when no
priority-score vacancy is pending. Vacancies older than `prepare_max_age_days` from
`discovered_at` are excluded from preparation.
