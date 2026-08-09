# Vacancy-specific application workflow

## Goal and boundary

Generate an evidence-backed CV, cover letter, application analysis, and interview plan
for an explicitly selected batch of one to 10 registry vacancies without modifying
candidate source documents or calling the OpenAI Platform API from project code.

```text
Codex task seals 1-10 explicit vacancy selectors
        ↓
for each vacancy: read only that vacancy + candidate sources + versioned prompt
        ↓
final CV + verified research → $write-cover-letter
        ↓
.codex-work/application/<vacancy>/ four isolated Markdown drafts
        ↓
Python resolves the selection and validates each package
        ↓
per-vacancy DOCX conversion + atomic application/ publication + manifest
```

The active interactive Codex task performs company research and writing. Scheduled
preparation remains disabled because the vacancy selection must come from the user.
The application prompt delegates the letter to `$write-cover-letter` from
`agent-plugins@valentin-agent-plugins` version `9.0.0+codex.20260809175723`; the task
must stop instead of using a generic fallback when the skill is unavailable.
`CodexApplicationDraftClient` only reads local Markdown. The deterministic publisher
validates all drafts, converts `cv.md` and `cover-letter.md`, and swaps the complete
`application/` directory with rollback so a failure preserves the previous package.

## Inputs and isolation

The Codex task reads the configured candidate source-of-truth files and, one selected
vacancy at a time, its `meta.yaml`, `job.md`, optional `company.md`, and
`prompts/vacancy-application.md`. Each task processes no more than 10 explicitly selected
vacancies. Once the CV and company research are final, `$write-cover-letter` receives
only that vacancy's evidence and produces the final letter. Its research notes and
unresolved confirmation items go to `analysis.md`, not `cover-letter.md`. Every draft set
is keyed by vacancy directory. Research, requirements, keywords, and wording must not
leak between packages, and non-selected vacancy artifacts remain out of scope. `all` is
never a valid preparation selector.

## Cache

`manifest.yaml` records candidate, vacancy, company, prompt, and actual Codex model-label
versions. All six output artifacts must exist. Manual
`pending prepare <selector-1> [<selector-2> ...]` checks compare those values locally
without invoking a model. The prompt pins the cover-letter plugin version, so changing
that pin changes `prompt_version` and makes existing packages stale for regeneration.

## Model routing

The `prepare` route uses the model configured in `config/codex-workflows.yaml` and the
hard-capped `prepare_batch_size` policy.
Scores below `prepare_min_score` are not prepared. Vacancies older than
`prepare_max_age_days` from `discovered_at` are excluded from preparation. There is no
automatic preparation queue: the user chooses one to 10 vacancies from analyzed matches
and requests preparation by vacancy IDs or registry directories.
