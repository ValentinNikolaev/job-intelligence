# Job Intelligence

A minimal local-first collector that turns source-specific vacancies into one human-readable filesystem registry.

```text
Source API → collector → normalized job → deduplication → registry/jobs → registry/index.md
```

The current MVP implements Adzuna, Arbeitnow, CleanJobData, DOU, Himalayas,
Jobicy, Jobspresso, Jooble, We Work Remotely, public Ashby and Greenhouse
job-board collectors, and custom company-board monitoring.

## Requirements

- Python 3.11 or newer
- Internet access while collecting

PyYAML is the only runtime package outside Python's standard library. Match
analysis and application writing run inside Codex. Project code never calls the
OpenAI Platform API; it only validates and publishes local drafts produced by the
active Codex task.

## Setup

Create and activate a virtual environment, then install the project:

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e .
Copy-Item sources/.env.example sources/.env
```

On macOS or Linux, activation is `source .venv/bin/activate` and the copy command is `cp sources/.env.example sources/.env`.

Edit `sources/.env` for local interactive runs:

```dotenv
ADZUNA_APP_ID=your-app-id
ADZUNA_APP_KEY=your-app-key
JOOBLE_API_KEY=your-api-key
CLEANJOBDATA_API_KEY=your-api-key
TELEGRAM_BOT_TOKEN=your-telegram-bot-token
TELEGRAM_CHAT_ID=your-telegram-chat-id
```

`sources/.env` is ignored by Git. Real credentials must never be added to `.env.example` or source files. Scheduled tasks that use CodexSandboxOnline for sandboxed command execution should provide the same names as task or host environment secrets instead:

```text
ADZUNA_APP_ID
ADZUNA_APP_KEY
JOOBLE_API_KEY
CLEANJOBDATA_API_KEY
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

The process environment wins over `sources/.env`, so the same code works in both
local and CodexSandboxOnline execution. If an Online secret is missing, only the affected
source should fail; `python run.py all` continues collecting from the remaining
configured sources and reports the failure separately.

Adzuna search terms and filters live in
[`sources/adzuna/config.yaml`](sources/adzuna/config.yaml), not in `.env`:

```yaml
queries:
  - country: it
    what: "python developer"
    where: "Roma"
    max_days_old: 7
    sort_by: date
```

See the [Adzuna collector guide](sources/adzuna/README.md) for every supported
filter, pagination behavior, rate limits, and the per-run request-budget
calculation.

Jooble searches live in [`sources/jooble/config.yaml`](sources/jooble/config.yaml)
and support multiple named query profiles. See the
[Jooble collector guide](sources/jooble/README.md) for all fields, fair
round-robin pagination, and the caveat around Jooble's unspecified 500-request
quota period.

CleanJobData searches live in
[`sources/cleanjobdata/config.yaml`](sources/cleanjobdata/config.yaml). The
collector uses the `/jobs` list endpoint with `extra_fields=description`, cursor
pagination, bearer authentication via `CLEANJOBDATA_API_KEY`, and an internal
1 req/sec throttle for the free trial rate limit. See the
[CleanJobData collector guide](sources/cleanjobdata/README.md) for supported
filters, quotas, and local caching notes.

Ashby boards live in [`sources/ashby/config.yaml`](sources/ashby/config.yaml).
They use Ashby's public postings endpoint and require no account or API key. See
the [Ashby collector guide](sources/ashby/README.md) for registry and discovery
details.

Greenhouse boards live in
[`sources/greenhouse/config.yaml`](sources/greenhouse/config.yaml), starting with
Grafana Labs. They use Greenhouse's public Job Board API with `content=true` and
require no account or API key. See the
[Greenhouse collector guide](sources/greenhouse/README.md) for board-token,
filtering, and preserved metadata details.

Arbeitnow is a public European job feed and requires no API key. Its optional
page limit, request timeout, and documented `visa_sponsorship` filter live in
[`sources/arbeitnow/config.yaml`](sources/arbeitnow/config.yaml). The collector
follows the API's `links.next` pagination URL and leaves keyword/location
filtering to downstream processing. See the
[Arbeitnow collector guide](sources/arbeitnow/README.md) for details.

DOU remote category pages live in
[`sources/dou/config.yaml`](sources/dou/config.yaml). The collector monitors the
PHP and Golang remote vacancy pages, follows each vacancy link for full
description text when available, and assigns `analysis_priority: 100` to those
configured high-priority leads. See the
[DOU collector guide](sources/dou/README.md) for configuration details.

Himalayas provides a free public remote-job search API with no API key. Search
profiles and per-query page limits live in
[`sources/himalayas/config.yaml`](sources/himalayas/config.yaml). The collector
supports `q`, `country`, `worldwide`, `exclude_worldwide`, `seniority`,
`employment_type`, `company`, `timezone`, and `sort`; it manages the 1-based
`page` parameter itself. See the
[Himalayas collector guide](sources/himalayas/README.md) for configuration,
pagination, attribution, and stored metadata details.

Jobicy is primarily a remote-job source and exposes the public, keyless
`GET https://jobicy.com/api/v2/remote-jobs` endpoint. Multiple `count`, `geo`,
`industry`, and `tag` query profiles live in
[`sources/jobicy/config.yaml`](sources/jobicy/config.yaml); taxonomy slugs are
kept configurable and passed through unchanged. Jobicy asks clients not to poll
more than once per hour, and a few checks per day are recommended for personal
search. See the [Jobicy collector guide](sources/jobicy/README.md) for details.

Jobspresso exposes a first-party jobs RSS feed with full descriptions and stable
WordPress post IDs. The collector polls only the advertised clean feed URL (no
query-string pagination) and keeps Jobspresso links as source attribution. See
the [Jobspresso collector guide](sources/jobspresso/README.md) for details.

We Work Remotely explicitly permits use of its public RSS feeds with attribution.
Configured category feeds live in
[`sources/weworkremotely/config.yaml`](sources/weworkremotely/config.yaml) and
are deduplicated by stable job identity. See the
[We Work Remotely collector guide](sources/weworkremotely/README.md) for details.

Wellfound, Built In, and Remote 100K were evaluated as requested but are not
automated collectors. Their current public terms do not authorize the required
automated extraction, and no supported public job feed was found. Their source
guides under `sources/` record the verification and the authorization needed to
enable a future adapter without pretending that an unsupported scraper works.

Custom company-board monitoring lives in
[`sources/custom/config.yaml`](sources/custom/config.yaml). It tracks selected
remote-first or full-remote company career pages, including ShippyPro, Madisoft /
Nuvola, Jagaad, SparkFabrik, BitBull, Spreaker, Userbot / Neuraltech, Switcho,
and Refactory. These vacancies are assigned `analysis_priority: 100` because
they come directly from company job boards, and their canonical content outranks
aggregator sources. See the
[custom collector guide](sources/custom/README.md) for configuration details and
the caveat that JavaScript-only pages may not expose vacancies to the
deterministic HTML parser.

## Run

```text
python run.py list
python run.py adzuna
python run.py arbeitnow
python run.py cleanjobdata
python run.py dou
python run.py himalayas
python run.py jobicy
python run.py jobspresso
python run.py jooble
python run.py weworkremotely
python run.py ashby
python run.py greenhouse
python run.py custom
python run.py ashby discover https://jobs.ashbyhq.com/satispay/some-job-id
python run.py add-manual --input .codex-work/manual-job/example.yaml
python run.py all
python run.py reindex
python run.py status <job-directory-or-vacancy-id> <status>
python run.py catalog
python run.py doctor
python run.py api workflow-summary --json
python run.py api workflow-limits --json
python run.py api source-usage --json
python run.py usage record --workflow analyze --model codex:gpt-5.6-luna:low --input-tokens 1234 --output-tokens 456 --credits 0.12
python run.py usage summary
python run.py api catalog-vacancies --json
python run.py api queues analyze --json --limit 30
python run.py pending analyze all --workflow analyze --model-profile <selected-profile>
python run.py pending analyze <job-directory-or-vacancy-id> --workflow analyze --pack <pack.yaml>
python run.py analyze <job-directory-or-vacancy-id> --input <draft.yaml> --workflow analyze --model-profile <selected-profile>
python run.py pending prepare <selector-1> [<selector-2> ...] --workflow prepare --model-profile <selected-profile>
python run.py validate-application <job-directory-or-vacancy-id> --input <draft-directory>
python run.py prepare <selector-1> [<selector-2> ...] --input .codex-work/application --workflow prepare --model-profile <selected-profile>
```

Installed editable environments can also use `job-intel adzuna`.

Each source prints:

```text
Source: adzuna
Fetched: 120
Created: 15
Updated: 3
Duplicates merged: 6
Unchanged: 96
Rejected: 0
Errors: 0
API requests: 11
```

`all` isolates collector failures: it continues with other sources and exits non-zero if any source failed. To avoid one large feed monopolizing a scheduled run, collection targets process at most 100 fetched vacancies per collector by default. Override this with `--collection-limit <n>` or `JOBINTEL_COLLECTION_LIMIT`; use `0` for unlimited. Completed collectors append API request usage to `registry/source-api-usage.yaml`, grouped by source with cumulative totals and per-run entries. The index is regenerated from registry metadata after the run.

Codex task usage is recorded separately in `registry/codex-usage.yaml`. After each
scheduled or interactive Codex run, record the usage shown by Codex:

```text
python run.py usage record --workflow analyze --model codex:gpt-5.6-luna:low \
  --input-tokens <n> --output-tokens <n> --total-tokens <n> --credits <n>
```

Token and credit fields are optional because Codex may expose different usage details
by surface. Use `--measurement estimated` for a local estimate; estimates are not an
account-level credit balance. The append-only log is available through
`python run.py api codex-usage --json`.

## Registry

Each canonical vacancy has exactly one directory:

```text
registry/jobs/2026-07-22_203015_acme_senior-backend-engineer/
├── meta.yaml
├── job.md
└── company.md   # only when useful source content exists
```

`meta.yaml` is the source of truth. Its UUID is canonical; the directory name is only a readable first-discovery label. `sources` can contain several external references for the same vacancy. `job.md` keeps the preferred description, with direct ATS sources ranked above aggregators.

New vacancies start with `status: found` and a matching first `status_history` entry.
Statuses are changed only by an explicit user request:

```text
python run.py status <job-directory-or-vacancy-id> reviewing --reason "needs human review"
```

Allowed values are `found`, `reviewing`, `prepared`, `applied`, `interview`,
`technical_interview`, `final_interview`, `offer`, `rejected`, `withdrawn`, and
`closed`. The command preserves history and records an exact UTC timestamp. It never
changes status based on generated artifacts.

Manual status decisions made through the user/LLM workflow are also appended to
`registry/manual-status-log.yaml`. That file stores the selected vacancy, old and new
status, reason text, normalized reason key, actor, optional interaction id, and
aggregated counts by status and reason. Use `--reason`, `--actor`, `--interaction-id`,
and `--status-note` when Codex records a user decision, for example:

```text
python run.py status <job-directory-or-vacancy-id> rejected --reason "requires hybrid work" --interaction-id "<task-or-thread-id>"
```

The registry uses exact `(source, source_job_id)` identity first. For a new source record, it uses a SHA-256 fingerprint of normalized company, title, and location as a candidate match. Two IDs from the same source never merge by fingerprint, and ambiguous fingerprint matches stay separate. See [the focused architecture proposal](docs/collection-architecture.md) for the complete model and tradeoffs.

Manually sourced vacancies can be published from a Codex- or human-prepared YAML
draft:

```yaml
source_url: "https://example.test/jobs/42"
company: "Priority Co"
title: "Platform Engineer"
description: |
  Full extracted job description.
analysis_priority: 100
remote: true
```

```text
python run.py add-manual --input .codex-work/manual-job/priority-co.yaml
```

For a user-supplied URL or pasted vacancy, capture the directory printed by
`add-manual` and analyze that exact directory with the direct `python run.py analyze
<directory> --input <draft.yaml> --workflow analyze` command. Manual application intake
does not run triage or join the scheduled sealed analysis queue.

`analysis_priority` is optional and ranges from `0` to `100`. It affects only
analysis queue order for `pending analyze`, sealed analysis packs, and queue APIs;
it must not be treated as match evidence or added to the match score.

Collected vacancy directories are not ignored, so the registry can be inspected, diffed, and committed if desired. Review source terms and the sensitivity of your search data before publishing it.

Collection applies a deterministic prefilter before writing to the main registry.
Vacancies older than seven days and obvious non-profile roles such as QA Automation,
Android, or iOS are kept out of `registry/jobs/`. Hard requirements for European
languages other than English, Russian, or Ukrainian are rejected; hard Italian is
also rejected unless the vacancy explicitly requires English. English language
requirements are always a green light for the language filter, and optional European
languages are allowed because the candidate can proceed in English. The prefilter
also rejects Spring Boot, Python + R, and Python + Julia roles, and only allows
vacancies that mention Go/Golang or PHP. Remote roles limited to the United States
are rejected unless the vacancy explicitly allows EU, EMEA, CET/CEST, or comparable
European working availability. Rejected records are written under
`registry/rejected/` with a structured `rejection_reason` in `meta.yaml` and the
same reason at the top of `job.md`.

### Match analysis and ranking

The `$job-intelligence-workflow` Codex skill compares one vacancy at a time with
the authoritative Candidate Profile. The `analyze` route never invokes a model;
it validates a Codex-produced YAML draft and writes:

```text
registry/jobs/<job-directory>/
├── meta.yaml
├── job.md
├── match.yaml
└── match.md
```

By default analysis uses the reviewed compact `registry/candidate/match-profile.md`
when present; otherwise it combines the two full candidate source files. Override
them by repeating `--profile`, or set `CANDIDATE_PROFILE_PATHS` to an OS path list.
The compact profile is for analysis only; preparation still uses the full sources.
For example:

```text
python run.py analyze <vacancy> --profile profile/profile.md --input draft.yaml --workflow analyze --model-profile terra_medium
```

`profile_version`, `job_version`, `prompt_version`, and the policy-derived model
label prevent unchanged work from being selected again. `--force` bypasses that cache. The index shows
unanalyzed jobs, orders analyzed jobs by score descending, and never uses another
vacancy as model context.

For high-throughput scheduled analysis, create and publish a sealed batch:

```text
python run.py triage
python run.py triage <job-directory-or-vacancy-id>
python run.py pending analyze all --limit 10 --pack .codex-work/analyze-pack.yaml
# Codex adds a strict `results` mapping to the pack.
python run.py analyze-batch --input .codex-work/analyze-batch.yaml --workflow analyze --model-profile <selected-profile>
```

`triage.yaml` is deterministic and high-confidence skips never enter the model queue.
When a vacancy selector is supplied, triage and `pending analyze --pack` remain scoped
to that exact vacancy instead of expanding to the scheduled queue.
Batch publication fails if any result is missing, extra, invalid, based on stale
candidate/vacancy hashes, or already current because another run published it after
the pack was built. Rebuild a stale pack from the latest repository state instead of
publishing or reporting it as skipped. Preparation has its own independently validated
batch contract for one to 10 explicitly selected vacancies; automatic preparation
selection remains disabled.

See [the matching design](docs/matching-architecture.md) for the schema, rubric,
hard-rejection rules, and cache behavior.

### Vacancy-specific application packages

By default, the Codex skill writes four Markdown drafts for each vacancy in an explicitly selected
batch of one to 10. An explicit `--document` request writes and publishes only `cv`,
`cover-letter`, `analysis`, or `interview-preparation`. `prepare` resolves the entire selection, reads each draft set from
`.codex-work/application/<vacancy-directory>/`, validates it independently, converts the
final CV and cover letter, and publishes:

```text
registry/jobs/<job-directory>/application/
├── cv.md
├── cv.docx
├── CV_ValentinNikolaev_<company>_<RoleAndFocus>.md
├── CV_ValentinNikolaev_<company>_<RoleAndFocus>.docx
├── cover-letter.md
├── cover-letter.docx
├── analysis.md
├── interview-preparation.md
└── manifest.yaml
```

The interactive Codex task reads only the selected vacancies, handles one vacancy at a
time with the configured candidate source documents, and applies the versioned
[single-package prompt](prompts/vacancy-application.md) independently. Codex may use its
own web-search capability for current company research. Project code does not call a
model or search API.

#### Two-wave Codex orchestration

Preparation can reduce elapsed model time without weakening package isolation. For
each selected vacancy, the coordinating agent creates only this vacancy's handoff area:

```text
.codex-work/application/<vacancy-directory>/parts/
```

Wave 1 runs three independent passes in parallel: bounded company research, CV plus
evidence mapping, and requirements plus risk analysis. These workers write only their
assigned intermediate files under `parts/`; they do not publish application artifacts
or write another worker's files. Input routing is deliberately narrow: the research
worker receives vacancy and company material but not the full candidate CV, while the
CV/evidence worker receives the vacancy and candidate evidence but does not browse the
web. Its `evidence-map.md` handoff includes a complete proposed CV draft. The
coordinating agent reviews the handoffs and is the only writer of the canonical
`cv.md`. Every Experience role in that CV has an evidence-backed `Technologies:` line.
That finalized file is the barrier between the waves.

Wave 2 can then run the cover letter, interview preparation, and application analysis
in parallel. Each worker owns exactly one final output, and the cover-letter worker
must invoke `$write-cover-letter`. Each receives only the finalized CV and the specific
handoffs required for its output, rather than every first-wave context. Once all
outputs are present, the coordinator runs one cross-file consistency check, one
`validate-application` command, and one `prepare` command. A failed check is repaired
at its source and only the necessary check is repeated.

If subagent capacity is unavailable, the same passes run sequentially with unchanged
inputs, file ownership, barrier, and validation rules. Every handoff path is keyed to
one vacancy directory; research, evidence mappings, risks, or prose from one vacancy
must never be reused for another.

After the CV and company research are final, the prompt invokes `$write-cover-letter`
from the highest installed version of `agent-plugins@valentin-agent-plugins`. The skill maps priority
requirements to verified evidence, selects two complementary examples, grounds company
motivation in current sources, and runs a final claim ledger. Only the finished letter
goes to `cover-letter.md`; research sources and unresolved confirmation items stay in
`analysis.md`. There is no generic or legacy inline fallback.

Install or refresh the configured personal plugin with
`codex plugin add agent-plugins@valentin-agent-plugins`, then start a new Codex task so
the bundled skill is loaded. Preparation must stop clearly if `$write-cover-letter` is
not available in that task.

The publisher validates all four Markdown outputs by default, or only the explicitly
selected document, before converting a selected CV or cover letter through the
installed host-side `md-to-docx` Codex skill. Set
`MD_TO_DOCX_SCRIPT` only if the skill cannot be found under
`CODEX_HOME/skills/md-to-docx/`. Markdown remains canonical; DOCX is generated only after
the package passes validation. The short `cv.*` files remain stable internal artifacts,
and each package also includes upload-friendly CV copies named like
`CV_ValentinNikolaev_grafana_SeniorBackendEngineerDatabasesLokiIngest.docx`.
Publication preserves the evidence-backed chronology in the validated draft.

`manifest.yaml` records per-document hashes of the candidate sources, vacancy, supplied
company content, prompt, and model. Unchanged selected documents are skipped unless
`--force` is supplied. A prompt change updates `prompt_version` and invalidates affected
documents. The source CV and
LinkedIn registry are never modified.

Preparation is manual and score-gated before any draft is read or published. The user
chooses one to 10 vacancies from analyzed matches and names every vacancy ID or registry
directory in chat. Scores from 65 through 100 are eligible, and scores below 65 are
intentionally excluded.

See [the application workflow design](docs/application-architecture.md) for isolation,
validation, failure handling, and configuration details.

### Codex tasks and model routing

Deterministic collection and maintenance are handled by the GitHub Actions workflow in
`.github/workflows/job-intelligence-collection.yml`. Versioned Codex task prompts for
model-dependent work live under `prompts/`, and the reusable repo skill lives under
`.agents/skills/job-intelligence-workflow/`.

| Task | Model | Reasoning |
|---|---|---|
| Analyze | `luna_low` by default | configured |
| Prepare | `terra_medium` by default | configured |

Application preparation is not queued automatically. After analysis notifications or
catalog review, the user explicitly chooses one to 10 vacancy IDs or registry
directories for each preparation task.

The authoritative routing policy and allowed model profiles are in
[`config/codex-workflows.yaml`](config/codex-workflows.yaml). The configured model must be
selected in the Codex or Scheduled Task UI; `--workflow` plus optional `--model-profile`
validates the route and derives the provenance label, but does not switch the active model. If a configured model is
unavailable, the task must report that limitation instead of publishing under another
workflow.

For Scheduled Tasks, run the versioned analysis prompt after the GitHub collection
workflow has had a chance to publish fresh registry changes. Application preparation
starts only from an interactive user request naming one to 10 vacancy IDs or registry
directories. Each model-dependent run must pull the latest committed repository state
before selecting work. Each model-dependent run handles one sealed analysis batch or one
explicit preparation batch of at most 10 vacancies, so its cadence controls token use.
CodexSandboxOnline or worktree execution requires a committed repository baseline plus
explicit secret provisioning through the task or host environment; never commit
`sources/.env`.

The GitHub collection workflow is suitable for a three-hour cadence. It runs collection,
deterministic triage, the four archive actions (`low-score`, `skipped`, `stale`, and
`rejected`), indexing, catalog generation, tests, doctor checks, queue/status JSON
commands, and `python run.py top 20`; each Python command writes its output to the
GitHub step summary. Rejected vacancy archiving keeps the newest 50 directories in
`registry/rejected/` and moves older entries to `archives/rejected/`. If project files
changed, the workflow commits and pushes the full deterministic update. Ignored secrets
and local work files are never staged.

### Vacancy catalog

The `$generate-vacancy-catalog` repo skill runs its deterministic command as a separate
operating-system process at the
end of every successful collection, analysis, preparation, or manual status change. Its
deterministic command writes [`catalog/index.md`](catalog/index.md) from `meta.yaml` and
existing application artifacts without modifying vacancy data.

Catalog and workflow state also have a JSON contract intended for scheduled tasks,
Docker wrappers, and future HTTP endpoints. `python run.py api catalog-vacancies --json`
returns normalized vacancy rows with source links, match scores, status timestamps, and
available application artifact paths. `python run.py api workflow-summary --json`,
`source-usage --json`, and `queues analyze --json` expose backlog, source request usage,
analysis queue selection, and estimated input-token budget status without invoking a
model.

For up to 100 vacancies the catalog stays in one file. Larger registries receive monthly
files plus a summary index. Entries are sorted by `discovered_at`, newest first; all
artifact links are repository-relative and missing files are shown as unavailable.

### Candidate source of truth

The candidate profile is stored in two primary records:

- [LinkedIn profile registry](registry/candidate/linkedin-profile.md) - detailed career timeline and extended experience.
- [Backend Engineer CV registry](registry/candidate/backend-engineer-cv.md) - curated positioning, skills, and selected experience.

Future CV and cover-letter variants must start from these two records. Treat facts and metrics as evidence-backed only when one of the records supports them; do not invent or silently combine claims. When the records conflict, preserve the conflict for review or ask the candidate instead of guessing. A newer source explicitly supplied by the candidate may amend or supersede these records.

## Add a collector

Create `sources/<name>/collector.py` containing:

```python
class ExampleCollector:
    name = "example"

    def __init__(self, config):
        self.config = config

    def fetch(self):
        # Authenticate, paginate, filter, and yield NormalizedJob values.
        yield normalized_job


def create_collector(config):
    return ExampleCollector(config)
```

The CLI discovers the module automatically. Collectors must not read or write the registry; they only yield `jobintel.models.NormalizedJob` values. Put placeholder configuration names in `sources/.env.example`, keep secrets in `sources/.env`, and add fixture-based adapter tests.

## Test

```text
python -m unittest discover -v
```

The tests use temporary registries and fixture responses; they do not call external APIs or modify `registry/`.

## Scope

The project collects, normalizes, deduplicates, stores, ranks, indexes, and prepares
vacancy-specific application materials. It intentionally has no database, UI, automatic
submission, application-status tracking, persistent queue, service process, or Docker
requirement. Scheduled execution remains an opt-in Codex configuration because cadence
and host permissions are user-specific.
