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

Normal packages use GPT-5.5 with medium reasoning for scores from 65 through 74.
Vacancies scoring at least 75 use GPT-5.6 Terra with medium reasoning; scores below 65
are not prepared. These are separate Codex tasks because a running task
cannot switch its own model. If the configured model is unavailable, report the problem
instead of publishing under an inaccurate label.
