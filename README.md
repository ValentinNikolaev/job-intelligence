# Job Intelligence

Job Intelligence is my local-first workflow for finding, reviewing, and preparing
job applications. It collects vacancies from public sources, stores them in a
readable registry, checks each role against my candidate evidence, and prepares
vacancy-specific application packages through Codex tasks.

This README is a review of how my flow works. It is not a generic project README
written to market a product. I use it to show the process in the open: what code
does, where Codex helps, where I keep human judgment, and how reviewers can audit
the result.

The full technical README has been preserved in
[`TECHNICAL_README.md`](TECHNICAL_README.md).

```text
Source API -> collector -> normalized vacancy -> deduplication -> registry
             -> match analysis -> application package -> catalog
```

## Who This Is For

HR readers can use this repository to understand how I search, filter, compare,
and prepare applications without hiding behind generic career language.

Senior developers can review the architecture, data boundaries, tests, model-use
policy, and failure handling. The goal is transparency: every important step leaves
files, hashes, commands, or reviewable Markdown behind.

## What The Workflow Does

- Collects vacancies from public job APIs and company career pages.
- Normalizes each vacancy into a shared local format.
- Deduplicates roles across sources without merging ambiguous records.
- Stores every canonical vacancy as Markdown plus YAML metadata.
- Rejects obvious non-profile roles through deterministic filters.
- Uses committed candidate records as the source of truth.
- Runs Codex tasks for judgment-heavy match analysis and application writing.
- Validates Codex-produced drafts before publishing them.
- Generates CV, cover letter, application analysis, and interview preparation files.
- Builds a human-readable vacancy catalog from registry metadata.

## What The Workflow Does Not Do

- It does not call the OpenAI Platform API from project code.
- It does not use a hidden model proxy, OpenAI SDK, or OpenAI-compatible endpoint.
- It does not invent candidate claims.
- It does not auto-submit applications.
- It does not infer application status from artifacts or external events.
- It does not require a database, service process, Docker setup, or UI.

This boundary matters. Deterministic code handles repeatable work. Codex handles
tasks that need language judgment. The repository keeps the handoff visible.

## Repository Map

| Path | Purpose |
| --- | --- |
| `sources/` | Collectors, source configs, and source-specific guides. |
| `registry/jobs/` | Canonical vacancy records, match results, and application packages. |
| `registry/candidate/` | Candidate source records used as evidence. |
| `catalog/` | Generated vacancy catalog for human review. |
| `docs/` | Architecture notes for collection, matching, and preparation. |
| `prompts/` | Versioned Codex prompts for model-dependent work. |
| `tests/` | Unit tests for deterministic behavior. |
| `run.py` | Main command entrypoint. |
| `TECHNICAL_README.md` | Full technical operating manual. |

## Main Flow

1. **Collect vacancies**

   Source collectors fetch vacancies from Adzuna, Arbeitnow, CleanJobData, DOU,
   Himalayas, Jobicy, Jooble, public Ashby boards, public Greenhouse boards, and
   selected company career pages.

2. **Normalize and deduplicate**

   Each source record becomes a shared `NormalizedJob`. The registry matches exact
   source IDs first, then uses conservative fingerprints for possible cross-source
   matches.

3. **Filter unsuitable roles**

   Deterministic filters keep old vacancies and obvious non-profile roles out of
   the main registry. Rejected records remain available under `registry/rejected/`
   with structured reasons.

4. **Analyze the match**

   A Codex task compares one vacancy, or a sealed batch of up to fifteen vacancies,
   against the candidate evidence. Project code validates the produced draft before
   publishing `match.yaml` and `match.md`.

5. **Prepare the application**

   A separate Codex task handles an explicitly selected batch of one to ten vacancies.
   For each vacancy, the task can use two coordination waves: company research,
   CV/evidence mapping, and requirement/risk review run in parallel first; after the
   coordinating agent fixes the shared `cv.md`, cover-letter, interview, and analysis
   work can run in parallel. Subagents exchange intermediate work only through that
   vacancy's `.codex-work/application/<vacancy>/parts/` directory and have exclusive
   ownership of their output files. Inputs stay minimal: research does not receive the
   full candidate CV, CV drafting does not browse the web, and second-wave workers see
   only the finalized CV and handoffs they need. The letter still goes through the
   dedicated `$write-cover-letter` plugin skill. The coordinator performs one
   cross-file check, validates the complete package once, and publishes it once. The
   same ownership and vacancy-isolation rules apply when concurrency is unavailable
   and the waves run sequentially.

6. **Regenerate the catalog**

   The catalog gives a readable overview of vacancies, scores, statuses, links, and
   available application artifacts.

## Candidate Evidence

The workflow relies on two candidate records:

- `registry/candidate/linkedin-profile.md`
- `registry/candidate/backend-engineer-cv.md`

Those files are the evidence base. Application drafts and match analysis must not
add experience, metrics, tools, companies, or responsibilities unless the candidate
records support them. If two records conflict, the workflow preserves the conflict
for review instead of guessing.

## Model Boundary

Project code must stay deterministic. It can collect, normalize, deduplicate,
validate, index, convert, and publish local files. It must not call the OpenAI
Platform API or an OpenAI-compatible model endpoint.

Codex runs model-dependent work in separate interactive or scheduled tasks. The
repository then validates and publishes Codex-produced local drafts. This keeps the
model boundary explicit and auditable.

## Common Commands

Set up the project:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item sources/.env.example sources/.env
```

Run collection and maintenance:

```text
python run.py all
python scripts/archive_jobs.py rejected --keep-items 50
python run.py reindex
python run.py catalog
python run.py doctor
python run.py top 10
```

Run one source:

```text
python run.py adzuna
python run.py arbeitnow
python run.py cleanjobdata
python run.py dou
python run.py himalayas
python run.py jobicy
python run.py jooble
python run.py ashby
python run.py greenhouse
python run.py custom
```

Change a vacancy status after an explicit decision:

```text
python run.py status <job-directory-or-vacancy-id> reviewing --reason "needs human review"
```

Manual status changes made through the user/Codex loop are audited in
`registry/manual-status-log.yaml`, including counts by target status and reason.

Publish Codex-produced work:

```text
python run.py analyze <job-directory-or-vacancy-id> --input <draft.yaml> --workflow analyze
python run.py triage <job-directory-or-vacancy-id>
python run.py pending analyze <job-directory-or-vacancy-id> --workflow analyze --pack <pack.yaml>
python run.py validate-application <job-directory-or-vacancy-id> --input <draft-directory>
python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare
# Select an allowed model profile when the active Codex task uses a non-default model.
python run.py analyze <job-directory-or-vacancy-id> --input <draft.yaml> --workflow analyze --model-profile terra_medium
python run.py prepare <selector-1> --input .codex-work/application --workflow prepare --model-profile luna_low
```

An explicit selector limits both deterministic triage and an analysis pack to that
single vacancy; use `all` only when intentionally processing the scheduled queue.

The shared interactive and scheduled workflow contract lives in
[`prompts/job-intelligence-workflow.md`](prompts/job-intelligence-workflow.md).
Model profiles are configured in `config/codex-workflows.yaml`; the Codex task must
actually use the selected profile's model and reasoning because repository code cannot
switch the active model of a running task.

Run tests:

```text
python -m unittest discover -v
```

See [`TECHNICAL_README.md`](TECHNICAL_README.md) for the full command list, source
configuration, queue APIs, workflow routing, and collector authoring guide.

## Review Notes

This repository is meant to be inspected. A reviewer can open a vacancy directory
and see the original job text, metadata, match analysis, generated application
files, and publication manifest. A developer can run the tests and trace the
deterministic path from source record to registry entry.

That is the point of the project. I want the workflow to be useful, but I also want
it to show how I work: transparent about tools, careful with evidence, willing to
automate repetitive steps, and honest about where human judgment still matters.

## Scope

Job Intelligence collects, normalizes, deduplicates, stores, ranks, indexes, and
prepares vacancy-specific application materials.

It stays small by design. No database. No automatic submission. No hidden
status tracking. No product-style UI. The repository is a working system and a
reviewable record of the decisions behind that system.
