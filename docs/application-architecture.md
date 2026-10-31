# Vacancy-specific application workflow

## Goal and boundary

Generate an evidence-backed CV, application analysis, and interview plan
for an explicitly selected batch of one to 10 registry vacancies without modifying
candidate source documents or calling the OpenAI Platform API from project code.
Inspect the application route: add a letter only for a required form field or an
email-only application, through a separate selected-document pass.

```text
Codex task seals 1-10 explicit vacancy selectors
        ↓
for each vacancy: read only that vacancy + candidate sources + versioned prompt
        ↓
final CV + verified research → conditional separate $write-cover-letter pass
        ↓
.codex-work/application/<vacancy>/ isolated Markdown drafts
        ↓
quality.yaml + substantive two-wave handoffs
        ↓
Python resolves the selection and validates content, structure, provenance, and hashes
        ↓
per-vacancy DOCX conversion + atomic application/ publication + manifest
```

The active interactive Codex task performs company research and writing. Scheduled
preparation remains disabled because the vacancy selection must come from the user.
The application prompt delegates a selected letter to `$write-cover-letter` from the
highest installed version of `agent-plugins@valentin-agent-plugins`; the task must stop
instead of using a generic fallback when the skill is unavailable.
`CodexApplicationDraftClient` only reads local Markdown. The deterministic publisher
validates the selected drafts, converts selected `cv.md` and `cover-letter.md` files,
and swaps the `application/` directory with rollback so a failure preserves the
previous package. The default selection is CV, analysis and interview preparation.
An explicit
`--document` selection updates only `cv`, `cover-letter`, `analysis`, or
`interview-preparation` while carrying forward other recognized artifacts unchanged.

The [quality contract](application-quality.md) rejects skeletal drafts before
conversion and defines the current standard, compact and email limits. Required
CV sections, real profile URLs, bounded skills, grounded Experience bullets and
substantive handoffs apply to selected documents. Schema-3 `quality.yaml` records
the applicable two-wave work, claim grounding and cross-file review. A selected
letter additionally records its actual skill/workbench, source-backed evidence and
company context, voice checks and independent council receipts under the
[review contract](application-review-contract.md). Minima never authorize filler
or invented evidence; an unmet substantive gate blocks the affected document.

## Inputs and isolation

The Codex task reads the configured candidate source-of-truth files and, one selected
vacancy at a time, its canonical preflight snapshot and optional company context, and
`prompts/vacancy-application.md`. Each task processes no more than 10 explicitly selected
vacancies. For a selected letter, once the CV and company research are final, `$write-cover-letter` receives
only that vacancy's evidence and produces the final letter. Its research notes and
unresolved confirmation items go to `analysis.md`, not `cover-letter.md`. Every draft set
is keyed by vacancy directory. Research, requirements, keywords, and wording must not
leak between packages, and non-selected vacancy artifacts remain out of scope. `all` is
never a valid preparation selector.

## Cache

`manifest.yaml` records candidate, vacancy, company, prompt, actual Codex model label,
and quality-contract versions per document. Its `quality` section stores document word
counts and hashes, validated handoff word counts and hashes, declaration hash, and
method provenance. A cache hit requires the selected documents' canonical and
derived artifacts and current per-document bindings; a single-document cache hit requires only that document's canonical and
derived outputs. Manual
`pending prepare <selector-1> [<selector-2> ...]` checks compare those values locally
without invoking a model. Changing the application prompt changes `prompt_version` and
makes affected documents stale for regeneration.

## Model routing

The `prepare` route uses the model configured in `config/codex-workflows.yaml` and the
hard-capped `prepare_batch_size` policy.
Its eligibility check accepts a current match analysis from any approved `analyze`
profile. It still checks candidate, vacancy, and match-prompt versions, score, and hard
rejection. The manifest keeps the original analysis model, score, timestamp, and
version separately from the preparation model. Reanalysis is needed only when the
match is missing or stale; changing only the stored model label is prohibited.
The active `luna_medium` route also treats current historical `luna_low` matches as
already analyzed, so the model change does not put them back in the analysis queue.
Scores below `prepare_min_score` are not prepared. Vacancies older than
`prepare_max_age_days` from `discovered_at` are excluded from preparation. There is no
automatic preparation queue: the user chooses one to 10 vacancies from analyzed matches
and requests preparation by vacancy IDs or registry directories.

## Application quality and follow-through

The [quality v3 contract](application-quality.md) adds source-backed
evidence, grounded claim ledgers, compact document formats, a final CV review, and
real DOCX export checks. Old receipts stay explicitly legacy. The
[application lifecycle](application-lifecycle.md) preserves exact sent files,
records confirmed outcomes, reports descriptive conversion rates and follow-up timing,
and publishes approved form-answer/interview/follow-up drafts. No application is sent
and no status changes automatically.
