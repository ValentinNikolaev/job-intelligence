# Matching preferences and sealed analysis

[matching-policy.yaml](../config/matching-policy.yaml) contains qualitative analysis
preferences. [selection-policy.yaml](../config/selection-policy.yaml) separately
controls deterministic prefilter and triage decisions. Model judgment runs inside
Codex; the project loads data, seals inputs, checks drafts and publishes validated
results without invoking a model endpoint.

## Policy schema

[matching_policy.py](../jobintel/matching_policy.py) loads a required schema-1 file
into frozen dataclasses with tuple lists. All fields are explicit; there are no
inherited layers, implicit additions, personal defaults in Python, regex rules or
numeric adjustment weights. Unknown/duplicate fields, missing settings, invalid
types/identifiers, duplicate list values, recursive YAML and contradictory settings
fail with file/field diagnostics. Lists replace and preserve order.

| Field | Meaning | Extracted baseline value |
| --- | --- | --- |
| `prefer_remote` | Decrease fit when remote work is absent or unclear | `true` |
| `preferred_technologies` | Increase fit when a listed technology is meaningful to the role | PHP, Go |
| `discouraged_core_technologies` | Decrease fit for central requirements, without inventing a hard blocker | Spring Boot, ASP.NET/.NET web backend |
| `discouraged_roles` | Decrease fit for the selected role categories | SRE |
| `prefer_relocation_package` | Increase fit when a package is offered | `true` |
| `preferred_cities` | Increase fit for roles based in a named city | Roma, Rome |
| `preferred_domains` | Increase fit for selected domains | Support automation, email, support |
| `block_us_work_requirements` | Preserve the existing decisive US-hours conflict rule | `true` |
| `allow_european_or_candidate_local_hours` | Preserve its explicit European/candidate-local hours exception | `true` |

Technology identifiers currently cover `go`, `php`, `python`, `r`, `julia`,
`spring_boot`, `aspnet`; role identifiers cover `sre`; domain identifiers cover
`support_automation`, `email`, `support`. City entries are nonempty text. Preferred
and discouraged technology lists cannot overlap. The hours exception requires the
corresponding conflict rule. Empty preference lists add no hidden choices.

The [generic match prompt](../prompts/vacancy-match.md) retains the original scoring
weights, recommendation bands, evidence/unknown-information rules and hard-rejection
boundaries. It explains how the policy's switches and identifiers apply. Preferences
do not establish unsupported mandatory conflicts. No numeric adjustment magnitude
was introduced by extraction.

## Runtime identity and freshness

`current_matching_context(project_root)` reads that project's current policy and
generic prompt, together with `MATCH_OUTPUT_SCHEMA`. It has no import-time prompt
read. Commands load one immutable context before locks, metadata migration, source
snapshots, preparation materialization, draft clients or notifications, and pass it
to nested consumers. Compatibility library calls without an explicit context load
the package's known project configuration; they do not guess a project from a vacancy
path or fall back after a missing/invalid configuration.

The effective `prompt_version` is `job-match-v2:sha256:<digest>` over canonical JSON
containing the stripped generic prompt, output schema and typed policy snapshot.
Mapping keys are sorted; list order is preserved. Candidate evidence remains bound
solely by its existing separate `profile_version`; the vacancy retains its existing
`job_version`. Model provenance and score remain independent fields. Notification
destinations and other unrelated settings do not enter the analysis identity.

One shared `match_is_current` predicate serves the analyzer, file queues, MongoDB
snapshot queues and preparation preflight. Changed relevant inputs are stale. The
change does not execute reanalysis, update statuses or rewrite historical matches.

The legacy bridge accepts only the exact reviewed pre-extraction
version `job-match-v1:sha256:813df4c8583b3d5ac10bf119ee81af822f104b467466a37c820cb6a3ca2629f0`
when the current effective identity equals the independently approved extraction
identity `job-match-v2:sha256:936069737a4caa24ba6a39627dc3ef204e5bee92bf658d074f62be57028137c5`.
A later generic prompt, schema or scoring-policy change
must break that bridge. Original stored versions, model labels, scores, receipts and
bytes remain unchanged when an old match is reused. Historically approved model
labels retain their existing read-only compatibility.

## One envelope for individual and batch drafts

An exported schema-2 pack contains these bound inputs:

| Field | Binding |
| --- | --- |
| `prompt`, `policy`, `output_schema` | Exact runtime effective inputs |
| `prompt_version`, `policy_version` | Canonical effective-input and policy digests |
| `profile.text`, `profile.version` | Actual assembled source evidence and its content hash |
| `items` | One to 15 selected directory/ID/source references and actual vacancy payloads with profile/job hashes |
| `pack_sha256` | Canonical envelope digest, excluding itself and the later `results` mapping |
| `results` | Codex adds one output mapping for every exact selected directory |

Copy the envelope unchanged and add `results`. Both file loading and direct
`publish_analysis_batch(mapping, results, analyzer)` validate the same schema and
payload bindings. Publication independently compares the actual assembled candidate
text, vacancy text/metadata, IDs, versions and notification source URLs to current canonical inputs. Recomputing
an outer hash cannot make fabricated input agree with the current source. All batch
items/results are validated before the first match write. `--force` does not bypass
integrity or permit a different selected vacancy. Directory selectors and publication
paths must remain directly inside `registry/jobs`; traversal, absolute/drive/UNC paths
and links escaping that boundary are rejected.

The public `MatchAnalyzer.publish_analysis` method also requires the complete sealed
one-item draft. Optional version labels cannot authorize a raw result. Only the private
write primitive used by already validated batches and synchronous analysis receives
an individual result with mandatory current input bindings.

For a named individual vacancy:

1. Export with `python run.py analyze <directory-or-id> --pack .codex-work/manual-analysis/pack.yaml --workflow analyze [--model-profile <profile>]`.
2. Evaluate only that one item in Codex, copy the complete pack and add its one
   directory-keyed result under `.codex-work/manual-analysis/`.
3. Publish using the existing invocation `python run.py analyze <directory-or-id> --input <draft.yaml> --workflow analyze [--model-profile <profile>]`.

Result-only legacy draft files fail closed with export guidance. Do not attach new
metadata to an old judgment to make it appear current: export and reevaluate changed
inputs. Manual intake retains its single-vacancy boundary and preparation approval
gateway; it does not enter triage or the scheduled queue.

Scheduled analysis keeps `pending analyze ... --pack` and `analyze-batch --input`.
Both use the same envelope and effective context. No existing CLI argument, MongoDB
schema, database, index or adapter was replaced. The emitted match record continues
to use its existing provenance fields.

## Independent evaluation and publication

Two separate gates apply before accepting this migration:

- The required [blind editorial evaluation](../prompts/editorial-evaluation.md)
  checks ten curated editorial dispositions and their grounding. It is not evidence
  of scoring equivalence.
- [evaluate_match_policy.py](../scripts/evaluate_match_policy.py) compares 14 synthetic
  vacancy pairs under two masked prompt variants: 56 individual judgments and 28 pair
  comparisons. It checks preference direction, blocker boundaries and uncertainty,
  without requiring exact cross-variant numeric scores.

The semantic helper's preserved baseline prompt/schema are actual pre-extraction
fixtures. No candidate source records or live vacancies are used by the corpus.
Export current inputs with
`python scripts/evaluate_match_policy.py export --output .codex-work/match-policy-pack.json`.
Give only that exported pack to an independent Codex reviewer, without corpus answer
keys. Save completed decisions at `.codex-work/match-policy-decisions.json` and run
`python scripts/evaluate_match_policy.py evaluate --input .codex-work/match-policy-decisions.json --output .codex-work/match-policy-receipt.json`.

The project wrapper and finalizer derive prompt, schema and policy from the actual
runtime loader, not a supplied policy sidecar or previously exported receipt. Inputs,
pack and decisions are hash-bound. Ties block acceptance and return
`review_required: true`; inspect every disagreement and every tie. Exact source excerpts
establish anchoring, not semantic sufficiency; the coordinator must review reasoning.
Masked labels/order do not promise
that a reviewer cannot infer variant identity from the supplied policy/text.

On 2026-10-20 the actual matching evaluation passed: 56 judgments, 28 comparison
rows, no ties or inversions, and four correctly identified hard rejections (two
conflict types under both variants). The coordinator reviewed all 14 pairs' reasoning
under each variant and found no source-excerpt or recommendation-band issues.
The decisions SHA-256 is `91aeb564fcc6a843ad11167ddc239d3530aa4ab490ec940a216ec85a4135f3d9`;
the blind-pack SHA-256 is `d2b16de239aa5c34fdd12ca82237c5b4fbae35de2d5717b5554e96c29154d71f`.
The local receipt is `.codex-work/match-policy-receipt.json`; ignored evaluation
artifacts are not tracked project evidence. These counts, identities and limitations
are preserved here and in the [migration plan](multiaccount-migration-plan.md).

Both equivalent-policy variants received identical judgments from one masked reviewer.
This is a bounded synthetic extraction check, not independent numeric replications or
a guarantee of variant-identity blindness. It does not establish hiring effectiveness.
Fixture/evaluator unit tests remain mechanical checks and cannot replace actual
independent passes. Editorial acceptance and final release checks remain separate.

The initial phase-3 editorial pass scored 9/10. For the proposal-versus-delivery case,
the reviewer consistently chose omission because the evidence supported a proposal
while the requirement demanded production experience. Technical review found the
synthetic fixture ambiguous about whether it evaluated CV selection or delivery-stage
accuracy. The authorized clarification changes only the case kind/requirement to
claim grounding and explicit delivery-stage accuracy, preserving source text, claim
text and curated disposition. This clarification did not change production editorial
policy and did not itself count as acceptance.

The fresh independent editorial assessment passed all ten cases; the coordinator
inspected every reason. Its corpus SHA-256 is
`569ee2c6f5b55b9c8fa3e06030e239e11a26d52b0bff4627fc3bcd87a15e1ecc`, policy SHA-256
`222e61ce3544f70f9ef2b463c9b4c911ed5ac19cee11e39878e27d109e8665cd` and decisions SHA-256
`6c109f3db119d58f7b2626da7a6ab5dc01fc4309b9a82f08017d282943596555`.
This editorial result establishes the curated dispositions, separately from scoring.

The final Python 3.14.6 full suite with a disposable MongoDB 8 replica set passed
782 tests in 127.566 seconds with no skips. API-prohibition checks and diff checks
passed. Core review, including the production pin, approved the corrected code.
Architecture review R5a closed CR-003/004 after 47 independent tests and five expected
mutation failures followed by restored passing controls; it also revalidated the
actual matching receipt. Final council and anonymized peer review accepted bounded
publication. Cumulative published-code review R6 approved the runtime; its sole finding
CR-007 concerned checkout line endings in the frozen baseline fixture. The focused
LF rule in [`e30d2dc`](https://github.com/ValentinNikolaev/job-intelligence/commit/e30d2dc2941ed79ee87239e2ee7260498151e611)
preserves its original bytes. Fresh Windows R7 review with `core.autocrlf=true`
approved and closed CR-007 after 23 passing executions in 2.563 seconds, with
index/worktree LF, 66 LF/zero CR and the original hash. The council peer retained approval.
[CI on that exact commit](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39428852968/attempts/1)
passed 782 tests in 24.858 seconds, with two missing-Poppler PDF skips. Phase 3 is
complete in [PR 2](https://github.com/ValentinNikolaev/job-intelligence/pull/2); phases 4-6
remain deferred. Earlier CI startup failure/retry evidence remains in the
[migration plan](multiaccount-migration-plan.md). Retain exact ignored packs, decisions
and receipts for repeat validation: recomputation checks bindings separately from
the original semantic judgments. This final acceptance increment changes docs only;
runtime tests were not rerun.
