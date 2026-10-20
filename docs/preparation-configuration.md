# Preparation configuration

Phase 4 of the [migration plan](multiaccount-migration-plan.md) extracts the current
candidate's document-preparation settings. There is still one live candidate; account
selection and second-account isolation belong to phases 5-6. MongoDB records and
candidate evidence are not migrated.

## Configuration owners

`config/application-profile.yaml` keeps its existing candidate answers and retry
rules. Its required `preparation` section owns these settings:

| Field | Purpose |
| --- | --- |
| `cv_owner_stem` | Safe filename owner used for newly exported CVs |
| `candidate_directory` | Project-relative directory containing immutable direct Markdown sources |
| `evidence_bank` | Derived evidence-bank YAML, outside the immutable source directory |
| `profile_sources` | Ordered preferred sources, fallback sources, then sorted optional supplements |
| `career_sources` | Ordered source paths and their career-section names |
| `employer_aliases` | Candidate-specific employer name equivalence |
| `career_scope` | Source-backed first employer and end-date recency boundary |
| `career_clarifications` | Reviewed, evidence-bound corrections preserving date precision and uncertainty |

Preferred profile sources preserve the existing compact-profile behavior. When the
preferred source is unavailable, use the configured fallback; supplements retain
their configured ordering. Explicit CLI profile arguments take precedence over
`CANDIDATE_PROFILE_PATHS`, then preparation configuration. Resolved preparation
sources must stay inside the configured candidate directory, and canonical match
evidence must be current for those actual sources. The analysis profile resolver and
its hashing remain unchanged.

`config/application-review.yaml` remains the sole voice-path owner. Its ordered,
nonempty unique source list is configurable; personal basenames and a fixed source
count are no longer requirements. Cover-letter review must bind every configured
path and its exact content hash. CV-only and evidence commands do not eagerly read
unrelated external voice files.

`config/cv-editorial-knowledge.yaml` retains shared editorial guidance, structure,
grounding and anti-patterns. It no longer owns the personal career window. Generic
prompts defer candidate-specific title, technology-attribution and uncertainty
decisions to the configured reviewed clarification evidence. Their source-backed
restrictions remain mandatory; a technology list alone never establishes delivery.

Missing or invalid configuration fails closed. There is no production fallback to
the previous hardcoded candidate. Synthetic tests create explicit configuration.

## Clarifications and source boundaries

Career corrections identify an existing employer and endpoint, a reviewed reason,
and exact source paths, hashes and excerpts. The validator rejects missing or stale
evidence, conflicting corrections and unsupported date precision. A year-only end
must retain the explicit source-backed uncertainty rather than acquire a month.
Source hashes and excerpts establish provenance; they do not replace review of what
the evidence means. Corrected sources are read without modifying them.

Evidence, role inventories, ancillary factual answers and preparation validation use
the same configured candidate boundary. Traversal and resolved link escapes fail.
The configured bank remains derived evidence and never authorizes writing candidate
source files. Evidence-command defaults use that bank; explicit draft-bank workflows
keep their existing validation and publication restrictions.

## Draft and publication identity

The immutable preparation context has a `preparation_context_version` beginning
`preparation-v1:sha256:`. Its canonical identity binds preparation configuration,
voice-source paths and shared editorial policy. Policy line endings normalize across
Git checkouts. Candidate profile contents, evidence and voice bytes retain their
separate existing hash checks; a context identity does not prove claim truth.

Before real drafting, run the normal named-vacancy `prepare-preflight`. Copy its exact
context version into new schema-3 `quality.yaml`. Standalone validation and direct or
CLI publication must reject a missing or changed identity before publication. Never
repair an old draft by copying a new identity onto it: recheck the changed inputs
under a fresh preflight. Manifest currentness uses the same context, including the
identity attached to each selected document. A partial refresh preserves all other
documents' files, versions and review records.

Existing records without a preparation binding remain readable and stale under the
new preparation contract. They are not rewritten or automatically regenerated.
Ancillary schema-1 drafts also declare the current preparation identity; their old
published records remain unchanged. No command gains permission to prepare an
application, change status, submit a form or send a message from configuration alone.

## Verification

The release gate combines strict-loader and source-bound negative cases, synthetic
alternate-candidate integration, current-candidate career parity, legacy analysis
identity and file/MongoDB publication regressions. Application-prompt and policy
changes also require the [blind editorial workflow](../prompts/editorial-evaluation.md).
The exported synthetic pack binds the effective preparation context without exposing
contact answers or reading candidate records. A passing curated corpus is bounded
editorial evidence, not a hiring-effectiveness result.

See the [plan's execution log](multiaccount-migration-plan.md#execution-log) for actual
test results, original disagreements, reviews and remaining release gates.
