# Local-first Vacancy Collection Architecture

## 1. Recommended Language

Use Python 3.11 or newer. Python runs consistently on Windows, macOS, and Linux; its standard library covers HTTP, JSON, filesystem work, HTML parsing, hashing, and the CLI. PyYAML is the only runtime dependency because YAML is the registry's structured format. A small local `.env` reader avoids adding a second dependency.

## 2. Minimal Architecture

```text
Source API
→ Source Collector
→ Normalized Job
→ Source Identity Check
→ Cross-source Deduplication
→ Canonical Vacancy
→ Filesystem Registry
→ index.md
```

- A source collector owns authentication, pagination, filters, and mapping one API schema to `NormalizedJob`.
- The registry owns both identity checks, canonical field selection, safe filesystem writes, and index generation.
- `meta.yaml` is authoritative. Markdown is a human-readable projection.
- The CLI discovers collectors from `sources/*/collector.py`, so source implementations remain isolated.

## 3. Repository Structure

```text
job-intelligence/
├── jobintel/
│   ├── cli.py
│   ├── ashby_boards.py
│   ├── collector.py
│   ├── config.py
│   ├── html_to_markdown.py
│   ├── models.py
│   ├── normalization.py
│   └── registry.py
├── sources/
│   ├── .env                  # ignored
│   ├── .env.example
│   ├── adzuna/
│   │   ├── collector.py
│   │   ├── config.yaml
│   │   └── README.md
│   ├── jooble/
│   │   ├── collector.py
│   │   ├── config.yaml
│   │   └── README.md
│   └── ashby/
│       ├── collector.py
│       ├── config.yaml
│       └── README.md
├── discovery/ashby/discovery.py
├── registry/
│   ├── jobs/.gitkeep
│   └── index.md
├── tests/
├── docs/collection-architecture.md
├── pyproject.toml
├── run.py
├── README.md
└── .gitignore
```

There is one small common package, not a layered framework. Unimplemented source folders document their future configuration without pretending to work.

## 4. Normalized Source Job

```python
@dataclass(frozen=True)
class NormalizedJob:
    source: str
    source_job_id: str
    source_url: str
    title: str
    company: str
    description: str
    company_url: str | None = None
    location: str | None = None
    remote: bool | None = None
    employment_type: str | None = None
    published_at: str | None = None
    company_description: str | None = None
    source_metadata: Mapping[str, Any] = field(default_factory=dict)
```

The required fields are the minimum needed for identity, presentation, and a useful stored vacancy. Timestamps are normalized to UTC ISO 8601 strings where a source supplies them.

## 5. Canonical Vacancy Model

```yaml
schema_version: 2
id: "31d603fe-5bcb-4ea0-9d39-8fb214f17750"
title: "Senior Backend Engineer"
company: "Acme"
company_url: "https://acme.example"
location: "Remote EU"
remote: true
employment_type: "full-time"
sources:
  - source: "adzuna"
    source_job_id: "12345"
    url: "https://www.adzuna.example/jobs/12345"
published_at: "2026-07-20T10:00:00Z"
discovered_at: "2026-07-22T18:30:15Z"
updated_at: "2026-07-22T18:30:15Z"
status: "found"
status_history:
  - status: "found"
    changed_at: "2026-07-22T18:30:15Z"
fingerprint: "sha256:..."
data_source: "adzuna"
content_source: "adzuna"
company_content_source: null
```

`content_source` records which source supplied `job.md`; its rank makes updates deterministic. `company_content_source` does the same for optional `company.md`. The directory name is deliberately absent from the identity model.
Optional source-specific values are stored under a source reference's `metadata`
mapping rather than adding ATS-specific canonical fields.

## 6. Registry Format

```text
registry/jobs/2026-07-22_203015_acme_senior-backend-engineer/
├── meta.yaml
├── job.md
└── company.md
```

`meta.yaml`:

```yaml
schema_version: 2
id: "31d603fe-5bcb-4ea0-9d39-8fb214f17750"
title: "Senior Backend Engineer"
company: "Acme"
company_url: "https://acme.example"
location: "Remote EU"
remote: true
employment_type: "full-time"
sources:
  - source: "adzuna"
    source_job_id: "12345"
    url: "https://www.adzuna.example/jobs/12345"
published_at: "2026-07-20T10:00:00Z"
discovered_at: "2026-07-22T18:30:15Z"
updated_at: "2026-07-22T18:30:15Z"
status: "found"
status_history:
  - status: "found"
    changed_at: "2026-07-22T18:30:15Z"
fingerprint: "sha256:79b7..."
data_source: "adzuna"
content_source: "adzuna"
company_content_source: "adzuna"
```

`job.md`:

```markdown
# Senior Backend Engineer

Build and operate Acme's backend services.

## Requirements

- Python
- PostgreSQL
```

Optional `company.md`:

```markdown
# Acme

Acme builds tools for distributed engineering teams.
```

## 7. Deduplication Strategy

### Same-source deduplication

Scan metadata into an in-memory lookup keyed by `(source, source_job_id)`. This exact key is authoritative. A repeated record always updates or leaves unchanged its existing canonical directory.

### Cross-source deduplication

1. Normalize Unicode with NFKC, lowercase, replace punctuation with spaces, trim, and collapse whitespace.
2. For companies, also remove a trailing `ltd`, `limited`, `inc`, `incorporated`, `llc`, `corp`, or `corporation`.
3. For locations, normalize safe variants such as `work from home` to `remote` and remove punctuation differences. Do not erase geographic qualifiers.
4. Hash `normalized_company|normalized_title|normalized_location` with SHA-256 and store it with a `sha256:` prefix.
5. Treat equal fingerprints as candidate duplicates only when the incoming record is from a different source. Merge it into the existing vacancy and add its source reference.

This can false-merge two same-title openings at the same company and location. The implementation isolates candidate selection in one method so a later deterministic discriminator can be added. A canonicalized employer job URL is the best next signal when aggregators expose it; a description hash is not used as a hard key because aggregators often truncate or rewrite descriptions. Fingerprints do not merge two distinct IDs from the same source, reducing the most obvious collision.

## 8. Canonical Source Precedence

Source quality ranks are:

```text
ashby
→ direct
→ adzuna = arbeitnow = himalayas = jooble
→ unknown sources
```

An incoming higher-ranked source may replace canonical title, company, company URL, location, remote flag, employment type, published date, and Markdown content. An equal-ranked source fills missing values but does not cause values to oscillate. A lower-ranked source only fills missing values. All source references are retained and sorted by `(source, source_job_id)`.

For `job.md`, a higher-ranked description wins; at equal rank, the longer non-empty description wins. The same rule independently governs `company.md`. This is deterministic and intentionally not a merge engine.

## 9. Registry Upsert Algorithm

1. Validate the normalized job and compute its fingerprint.
2. Look up `(source, source_job_id)`.
3. If found, use that directory. Compare its reference, canonical fields, and preferred Markdown. Write only if meaningful data changed.
4. Otherwise, look up the fingerprint among other sources. If found, use that candidate and append the new source reference.
5. If neither lookup matches, generate a UUID, create one human-readable directory from the UTC discovery time, and write the initial canonical files.
6. Preserve `discovered_at` forever. Set `updated_at` only when metadata or preferred content changed.
7. Write each file via a temporary sibling and atomic replace. On initial creation, build a temporary directory and rename it only after all content is valid.
8. Classify the result as `created`, `updated`, `merged`, or `unchanged`.
9. After a collector finishes, fully regenerate `index.md` from all valid `meta.yaml` files.

Known source records can be updated or unchanged. A new source with a known fingerprint is merged. A new fingerprint is created. Unchanged input produces no file changes, including no timestamp churn.

## 10. Source Interface

```python
class Collector(Protocol):
    name: str

    def fetch(self) -> Iterable[NormalizedJob]:
        """Fetch every configured page and yield normalized jobs."""
```

Each `sources/<name>/collector.py` exposes `create_collector(config)`. The CLI discovers these modules, validates that their declared names are unique, and passes the shared `.env` mapping. Adding a source means adding that one module; existing collectors and registry code remain unchanged.

## 11. Index Generation

The registry scans `registry/jobs/*/meta.yaml`, validates required fields, sorts by `discovered_at` descending and then canonical ID, and rewrites the whole index atomically. Markdown table cells escape pipes and line breaks. Each row contains discovery date, company, title, location, source links where available, and a relative link to `job.md`. An empty registry still has a valid header. The index is always disposable and rebuildable.

## 12. CLI Execution

From the repository root:

```text
python run.py adzuna
python run.py ashby
python run.py ashby discover https://jobs.ashbyhq.com/satispay/example-job
python run.py all
python run.py list
python run.py reindex
```

`all` catches errors around each collector, prints a per-source summary, continues with the remaining collectors, regenerates the index, and exits non-zero if any collector failed. A single source failure occurs before or between atomic registry upserts, so existing files remain valid.

## 13. MVP Implementation Plan

1. Project skeleton: CLI starts and `registry/index.md` can be regenerated.
2. Normalized source job model: validation tests cover required fields.
3. Canonical vacancy model: YAML round-trip test fixes the schema.
4. Filesystem registry: atomic creation/read tests.
5. Source identity lookup: repeated source records find one directory.
6. Deterministic fingerprint: normalization fixture tests.
7. Registry upsert and deduplication: create, update, merge, and unchanged tests.
8. Index generator: ordering, escaping, and link tests.
9. First collector: Adzuna fixture and pagination/normalization tests.
10. Additional collectors: Jooble uses named query profiles; Ashby uses a public board registry and separate validated discovery command.
11. `run all`: failure-isolation and aggregate-exit-code tests.

Every milestone leaves a runnable or directly testable increment.

## 14. Key Decisions

| Decision                          | Recommendation                                                 | Reason                                                            |
|-----------------------------------|----------------------------------------------------------------|-------------------------------------------------------------------|
| Language                          | Python 3.11+                                                   | Portable, strong standard library, low CLI overhead               |
| Runtime dependencies              | PyYAML only                                                    | YAML correctness is worth one mature dependency                   |
| Persistence                       | One directory per canonical vacancy                            | Human-readable source of truth and required domain invariant      |
| Internal ID                       | UUID4 in metadata                                              | Stable and independent of directory/source naming                 |
| Writes                            | Temporary sibling plus atomic replace                          | Avoids partially written files without transactions               |
| Collector loading                 | Filesystem discovery with one factory                          | New sources do not change core code                               |
| Deduplication                     | Exact source identity, then conservative fingerprint candidate | Deterministic and easy to improve                                 |
| Same-source fingerprint collision | Keep separate                                                  | Prevents collapsing parallel openings from one authoritative feed |
| Content selection                 | Rank first, completeness second                                | Stable and explainable                                            |
| Index                             | Full regeneration                                              | Simple, reliable, and not authoritative                           |
| First source                      | Adzuna API                                                     | Search-focused API with explicit filters and pagination           |

## 15. Open Questions

None block the MVP. Adzuna queries, Jooble query profiles, and Ashby boards live in
their source-specific YAML configurations, while credentials for authenticated
sources belong in `sources/.env`.

The reviewed design maintains the invariants: multiple source records merge into one canonical directory, unchanged reruns do not rewrite files, and a new collector requires only a new source module. It contains no database, web UI, application workflow, LLM, queue, or speculative service abstraction.
