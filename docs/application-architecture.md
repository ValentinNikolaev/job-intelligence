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
previous package. The default selection is all four documents. An explicit
`--document` selection updates only `cv`, `cover-letter`, `analysis`, or
`interview-preparation` while carrying forward other recognized artifacts unchanged.

The quality contract rejects skeletal drafts before conversion. Full packages require
at least 500 CV words, 300 cover-letter words, 700 analysis words, and 800 interview
preparation words while retaining the existing hard ceilings. It also checks required
CV sections, real profile URLs, a bounded skills inventory, evidence-backed Experience
bullets, cover-letter paragraph structure, and minimum handoff depth. `quality.yaml`
records the two-wave workflow, the installed `$write-cover-letter` version and completed
workbench, two sourced evidence stories, a sourced company motivation fact, and the
coordinator's claim-grounding and cross-file review.

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

`manifest.yaml` records candidate, vacancy, company, prompt, actual Codex model label,
and quality-contract versions per document. Its `quality` section stores document word
counts and hashes, validated handoff word counts and hashes, declaration hash, and
method provenance. A full-package cache hit requires all six standard output
artifacts; a single-document cache hit requires only that document's canonical and
derived outputs. Manual
`pending prepare <selector-1> [<selector-2> ...]` checks compare those values locally
without invoking a model. Changing the application prompt changes `prompt_version` and
makes affected documents stale for regeneration.

## Model routing

The `prepare` route uses the model configured in `config/codex-workflows.yaml` and the
hard-capped `prepare_batch_size` policy.
Its eligibility check requires the current match analysis to use the same selected
model profile. If an explicitly selected vacancy was last analyzed under another
profile, the active preparation-profile Codex task must evaluate it again and publish a
new isolated match draft with `analyze --model-profile <profile> --force`; changing only
the stored model label is prohibited.
Scores below `prepare_min_score` are not prepared. Vacancies older than
`prepare_max_age_days` from `discovered_at` are excluded from preparation. There is no
automatic preparation queue: the user chooses one to 10 vacancies from analyzed matches
and requests preparation by vacancy IDs or registry directories.
