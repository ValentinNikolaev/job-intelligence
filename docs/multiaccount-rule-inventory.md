# Selection-rule inventory and behavioral baseline

Recorded 2026-10-20 for [migration phases 0-3](multiaccount-migration-plan.md).
The baseline sections describe behavior captured before extraction in commit
`188d3c4c34253b8fd91a373e678f160910aed7ad`; the phase-2 section below records the
configuration cutover. This inventory does not authorize collection,
reclassification, preparation, historical rewrites or a second account. Candidate
source records and secrets were not used to construct the synthetic baseline.

## Common deterministic selection

The operational implementation is [prefilter.py](../jobintel/prefilter.py).
[selection-policy.yaml](../config/selection-policy.yaml) now supplies its personal
decisions, preserving the baseline values below. Normalization, timestamp parsing, word boundaries, language
requirement recognition and technology aliases remain shared Python mechanics.
Table order is rejection precedence; the first applicable rule supplies the category
and exact explanation. Configuration lists preserve the existing within-rule order.

| Order | Existing location and value | Consumer and precedence | Configuration owner |
| --- | --- | --- | --- |
| 1 | `load_company_retry_rules`, `_company_retry_rejection`: configured companies, aliases and retry dates; first match before every other rejection; allow on the date itself | Collection in `cli.py`; normalized company names and UTC reference date | Existing `config/application-profile.yaml:company_retry_after`; no duplicate in selection policy |
| 2 | `MAX_JOB_AGE_DAYS = 7`; strictly older than the cutoff; absent/unparseable dates do not reject | `prefilter_job`; UTC conversion and comparison are mechanics | `selection-policy.yaml:max_age_days` |
| 3 | `_is_obvious_role_mismatch`: QA/quality assurance/test automation/automation tester and Android/iOS/mobile engineer/mobile developer, title only | Prefilter, before remote checks | `excluded_roles: [qa, mobile]`; grouped recognizers remain code |
| 4 | `job.remote is False` rejects; `None` remains unknown | Prefilter; explicit nonremote wins over location text | `reject_explicit_non_remote: true` |
| 5 | `_american_work_time_rejection`: US remote; US residence; American continent work time; American continent residence, in that order | Prefilter scans normalized title, description, location and employment type. Explicit European/EU/EMEA/CET/CEST/UTC/GMT availability bypasses this entire group, but no other group | `location` booleans and `allow_european_exception`; region recognition remains code |
| 6 | `_hard_blocking_language_requirement`: Albanian, Bulgarian, Croatian, Czech, Danish, Dutch, Estonian, Finnish, French, German, Greek, Hungarian, Latvian, Lithuanian, Norwegian, Polish, Portuguese, Romanian, Serbian, Slovak, Slovenian, Spanish, Swedish, Turkish; separate Italian branch last | Prefilter scans description and location, not title; language list order wins over text order. Optional/negated clauses do not block; English does not cancel a different mandatory language. Russian/Ukrainian are not blockers | Ordered `blocking_languages`, with `italian` last; multilingual aliases/requirement recognition stay code |
| 7 | `_cms_stack`: TYPO3, WordPress/Word Press, Drupal, in that order | Prefilter; first CMS before other stack exclusions | `excluded_cms: [typo3, wordpress, drupal]` |
| 8 | `_blacklisted_stack`: Spring Boot; Python + R; Python + Julia | Prefilter; individual excluded technology before ordered combinations, even when Go/PHP also occurs | `excluded_technologies: [spring_boot]`; `excluded_combinations: [[python, r], [python, julia]]` |
| 9 | `_has_target_stack`: Go/Golang or PHP, any one sufficient | Prefilter; final rejection if neither recognized. Existing contextual Go and PHP version aliases remain code | `target_technologies: [go, php]` |

Current rejection explanation strings remain in Python. Selection-policy identifiers
choose recognized concepts, never regular expressions, code or replacement messages.
`_has_english_requirement` is currently unused by `prefilter_job`; do not revive it as
a bypass while extracting language policy.

## Triage, queues and archive consumers

[triage.py](../jobintel/triage.py) applied baseline ordered categories `sales`, `qa`,
`mobile`, `junior`, `sre`, `consulting`, `non_backend`. These are personal exclusions;
category patterns are recognition mechanics. A title match means high confidence and
`skip_model: true`; body-only recognition means medium confidence and no skip; no
recognition means low confidence. Title matches outrank body matches. The returned
reason is the first matching category in rule order, and all matching title categories
retain that order. Only the first 12,000 body characters are inspected. The selected
categories belong to `selection-policy.yaml:triage_exclusions`.

The baseline identified these consumers for the coordinated phase-2 cutover:

| Location | Current behavior | Required cutover boundary |
| --- | --- | --- |
| `jobintel/cli.py` collection handler | Loads retry policy, calls `prefilter_job` for normalized jobs | Validate selection once before source requests or mutations; pass immutable policy |
| `jobintel/cli.py` triage handler | Calls `write_triage` inside file/MongoDB batch handling | Pass policy to the same shared recognition/decision logic |
| `jobintel/cli.py:_run_pending_locked` | Omits high-confidence triage skips and post-analysis statuses; priority orders remaining items; passes skip callback to sealed-pack builder | Shared read-only skip decision and current vacancy inputs, including title changes |
| `jobintel/matching.py:build_analysis_pack` | Optional triage callback filters input before freshness/pack sealing | Bind the command's explicit policy through the callback |
| `jobintel/workflow_api.py:queue_items` and `_snapshot_should_skip` | File and MongoDB-snapshot paths have separate skip readers; both currently trust stored high-confidence skips without version checks | Unify effective policy and current title/body semantics without per-row database fallback |
| `scripts/archive_jobs.py:eligible` and `_eligible_document` | File and MongoDB-snapshot paths archive allowed statuses when stored `skip_model` is true; confidence/version are not checked | Preserve current fresh-baseline results, but stale content/policy must not cause archive writes |
| `.github/workflows/job-intelligence-collection.yml` | Collection, triage, skipped/low-score/stale archive, workflow reporting | Preserve existing command arguments and destinations; fail before operations on invalid policy |
| `.github/workflows/job-intelligence-archive-skipped.yml` | Can archive independently of the collection/triage run | Must receive shared freshness protection; preceding triage cannot be assumed |

At baseline, `triage_version` equaled `deterministic-triage-v1`, and readers did not
validate it or the title/body that produced the receipt. Phase 2 adds current-input
evaluation as described below. No original historical receipt is relabeled by reads.

## Existing source-side and deferred policy owners

Source filters run before the common prefilter. They are intentionally not a second
copy of the new common selection policy: provider queries and source relevance
continue to live under their existing owners in this iteration.
These source-side Go/PHP/Italy relevance decisions remain a constraint on future
onboarding. Before phase 6 claims candidate-independent onboarding, configure or
explicitly scope the affected sources; phases 0-3 do not perform that extraction.

| Locations | Existing decisions and consumers | Owner / disposition |
| --- | --- | --- |
| `sources/adzuna/config.yaml` | Italy; backend/technical lead/engineering manager; PHP/Golang/Laravel/Symfony; provider exclusions include WordPress/Drupal/Magento/Python/Java/.NET; age seven days | Existing source queries, interpreted by source collector; preserve |
| `sources/jooble/config.yaml`, `sources/himalayas/config.yaml`, `sources/jobicy/config.yaml` | Italy/Europe searches; senior backend, Go, PHP and lead/manager profiles; Himalayas admits worldwide results | Existing per-source query schemas; preserve |
| `sources/djinni/config.yaml`, `sources/dou/config.yaml` | Remote PHP and Golang category searches | Existing per-source queries; preserve |
| `sources/ashby/config.yaml`, `sources/greenhouse/config.yaml` and collectors | Remote-only, engineering title terms and Italy/Europe/EMEA/worldwide coverage; Ashby also names Germany/Netherlands | Existing source filters; preserve source-specific recognition and settings |
| `sources/custom/config.yaml` and collector | Board-specific title/location/exclusion lists; inherited source-level defaults; selected Italy/EU/EMEA eligibility; some UK/US/country exclusions | Existing source config, not new selection inheritance; preserve |
| `jobintel/remote_feeds.py` and its source collectors | Engineering/Go/PHP/Laravel/Symfony role recognition, remote signal, Italy/EU/EMEA/worldwide eligibility and country-only/excluding-Italy exclusions | Existing shared source relevance; preserve; a broader source-policy extraction is deferred |
| `sources/weworkremotely/collector.py`, `sources/jobspresso/collector.py` and configs | Seven-day source cutoff; Go/PHP/Laravel/Symfony relevance; Jobspresso rejects title noise; WWR checks engineering titles | Existing source config/mechanics; preserve even where common policy overlaps |
| Other `sources/*/config.yaml` (Arbeitnow, Cleanjobdata, Hacker News, Larajobs, RemoteOK, Remotive, Techyon) | Existing feeds, enabled/pilot settings, result/page/request limits and source-specific discovery | Preserve under source owners; no new restrictions or provider calls in this extraction |
| `jobintel/arc_alerts.py`, `scripts/resolve_arc_alert_links.py`, `scripts/import_readytotouch_companies.py` | Arc alert Go/PHP selection; remote Go-company directory import is a separate research utility | Preserve existing discovery/research scope, not common vacancy selection |
| `config/codex-workflows.yaml`, `jobintel/workflows.py` | Analysis/preparation models; preparation score 65, age 14 days, batch up to 10; analysis pack up to 15 | Existing workflow policy; immutable model provenance, no selection-policy duplication |
| `scripts/archive_jobs.py`, archive GitHub Actions | Low-score default 65, stale archive age seven days; archivable lifecycle statuses | Existing archive command semantics; do not infer outcome/status or change thresholds |
| `prompts/vacancy-match.md`, `jobintel/matching.py`, `workflow_api.py`, CLI preparation preflight | Weighted fit and personal qualitative preferences: remote, selected technologies/roles, relocation, Rome, support/email domains, European-hours exception | Phase 3: separate versioned analysis-policy snapshot; semantic judgment only in Codex |
| `AGENTS.md`, `prompts/job-intelligence-workflow.md`, `prompts/vacancy-application.md`, `.agents/skills/job-intelligence-workflow/` | Named-vacancy approval, profile/evidence paths, immutable candidate facts, career scope, document structure and review gates | Existing preparation contract; no phase-0/1 edits; phase 4+ owns candidate-specific preparation extraction |
| `config/application-profile.yaml`, `config/application-review.yaml`, `config/cv-editorial-knowledge.yaml`, `jobintel/career_coverage.py`, `jobintel/applications.py`, `jobintel/application_review.py` | Candidate profile/voice references, career boundaries and source-bound clarification branches, fixed CV filename owner | Existing evidence/editorial owners; defer to phase 4; no personal record copy or source changes |
| `config/linkedin-profile.yaml`, LinkedIn prompt/local skill | Standalone profile/evidence paths and draft destination | Separate authorized profile workflow; preserve |
| `config/data-services.yaml`, `jobintel/sheets_sync.py`, notification/backup scripts and Actions | Current MongoDB destination, Google destinations, schedules, Europe/Rome timezone, notification delivery state | Existing integration owners; phase 5 context references, phase 6 isolation; no migration or destination changes |

Known overlaps are preserved: source searches may exclude Python/Java/.NET more
strictly than the common mixed-stack filter; triage excludes SRE/junior/consulting
where prefilter may accept them; semantic analysis treats some technology/location
preferences separately from deterministic rejection. These are not silently unified.
The current Go contextual recognizer also accepts an incidental “Go” near “Engineer”
in the title/body window; the synthetic corpus freezes that ambiguous behavior rather
than fixing it during extraction.

At baseline, the editorial export/finalizer policy bindings did not include the match
prompt. Phase 3 adds that binding and a separate scoring-policy gate; actual independent
passes remain required. Editorial fixture unit tests are not those passes and do not
prove scoring behavior. Match freshness must agree between individual analysis, sealed
packs, snapshots and preparation preflight.

## Selection schema and versioning contract

[selection_policy.py](../jobintel/selection_policy.py) exposes
`load_selection_policy(path) -> SelectionPolicy` with frozen dataclasses and tuple
collections. All fields are required. There are no code defaults, environment
overrides, inherited layers or implicit list additions. The caller supplies the exact
path; command boundaries resolve it as `project_root/config/selection-policy.yaml`.
Missing files fail rather than searching another checkout. Schema version 1 rejects
unknown fields, duplicate YAML keys, recursive aliases, invalid field types/IDs,
duplicate IDs/combinations, conflicting target/excluded technologies, redundant
combinations and an exception with no corresponding constraint. Diagnostics name the
file and field without echoing YAML values or parser source excerpts.

Empty exclusion lists disable that category; target technologies must be nonempty
and support Go, PHP, Python, R, Julia and Spring Boot through existing recognizer
capabilities; the selected policy chooses Go/PHP. Location booleans name the
current recognition groups; they do not add arbitrary countries/timezones or allowlists.
All list values replace the entire list and preserve their order. Maps are canonically
serialized with sorted keys; ordered lists remain ordered. The returned object exposes:

- `fingerprint()`: every effective selection field and schema version.
- `prefilter_fingerprint()`: every field except triage exclusions.
- `triage_fingerprint()`: schema version and triage exclusions only.

These are canonical SHA-256 subset digests, not receipt versions or evidence that a
stored decision is current. The phase-2 receipt additionally binds recognizer version
and current vacancy content. Changing age/language/stack policy cannot change the triage
subset; changing triage exclusions cannot change the prefilter subset. Analysis policy
will have its own narrower inputs rather than depending on notification settings.

## Durable characterization and verification

[selection-baseline.yaml](../tests/fixtures/selection-baseline.yaml) contains only
synthetic vacancies with a fixed `2026-07-23T12:00:00Z` reference time. It captures
39 prefilter cases with exact categories/reasons, 13 triage cases and four queue
cases. [test_selection_baseline.py](../tests/test_selection_baseline.py) executes the
corpus against unchanged runtime code, verifies repeated triage receipt stability,
and compares file queue, MongoDB-shaped snapshot queue, CLI pending order and skipped
archive eligibility. Snapshot tests are unit coverage, not a real-Mongo claim.
[test_selection_policy.py](../tests/test_selection_policy.py) exercises immutable
loading, strict failures, replacement semantics and subset digest independence.

Before implementation, the coordinator ran Python 3.14.6 against a disposable local
MongoDB 8.0 replica set: **697 tests passed, no skips** on 2026-10-20. Command:
`JOBINTEL_TEST_MONGODB_URI=mongodb://127.0.0.1:27019/?replicaSet=rs0&directConnection=true python -m unittest discover -v`
(environment assignment syntax depends on shell). This supersedes the earlier
unit-only result (678 tests, 17 skipped). No production URI or production writes were
used. The ignored baseline log is supplementary, not the durable evidence itself.

The existing [.github/workflows/mongodb-tests.yml](../.github/workflows/mongodb-tests.yml)
reproduces integration coverage with a disposable MongoDB 8 replica set and Python
3.11. It runs unconditionally for pull requests; its push path filter omits config-only
and prompt-only changes. Do not treat absent push CI as a passing check.

Iteration-1 targeted verification:
`python -m unittest tests.test_selection_policy tests.test_selection_baseline -v`:
**13 tests passed**. The coordinator subsequently ran the full post-change suite
against the same disposable MongoDB replica set: **710 tests passed in 53.325 seconds,
no skips**. Independent review then strengthened the repeat-receipt test by advancing
its clock one day between writes. Reviewer R1 independently passed all 13 targeted
selection tests and confirmed that removing timestamp preservation produces 13 expected
triage subtest failures. R1 approved the increment, closed CR-001 and the coordinator
accepted phases 0-1. Catalog inputs did not change; publication remains the
coordinator's responsibility. The increment was published as commit
`188d3c4c34253b8fd91a373e678f160910aed7ad` in
[PR 2](https://github.com/ValentinNikolaev/job-intelligence/pull/2). Independent review
R2 approved the clean published increment. Ubuntu CI passed 710 tests with two PDF-tool
skips; the local disposable-MongoDB run had no skips. A PR CI MongoDB-container startup
failure happened before tests and passed on rerun.

## Phase-2 cutover and verification

The working-tree implementation now passes an immutable policy from collection,
triage and pending command boundaries, before source requests, leases or metadata
migration. Collection's existing `max_age_days` library override remains available;
when absent, the selected file supplies age. All supported technology identifiers
(Go, PHP, Python, R, Julia, Spring Boot) have recognition implementations for target,
exclusion and combination decisions. Current category/reason/precedence values remain
covered by the frozen baseline corpus.

Direct workflow API report/summary/analysis-queue functions load their known project's
selection file once before obtaining operational snapshots. Nested readers receive the
same object. Skipped-archive commands and direct `archive`/`candidates_for` entrypoints
validate their project's policy before lease or filesystem mutation. Other archive
categories keep their existing thresholds and selection rules. Compatibility library
helpers may omit the policy argument: they load the package's explicit
`DEFAULT_SELECTION_POLICY_PATH`, never walk a temporary registry to guess a project or
fall back after an invalid/missing file. Command paths always pass the already loaded
object. `doctor` includes deterministic selection-policy validation.

`evaluate_triage(meta, job_text, policy=...)` is a pure evaluator. New receipt versions
have prefix `deterministic-triage-v2:sha256:` and bind the canonical triage-policy subset,
recognition algorithm/patterns/body-window contract, casefolded current title and first
12,000 body characters. Unrelated age/language/stack settings do not alter this binding.
The writer retains timestamps and bytes when an unchanged current receipt is repeated.

File, snapshot, pending and skipped-archive readers share the same evaluation. An
existing structurally valid schema-1 receipt, including a legacy v1 receipt or an old
no-skip result, is reevaluated against current policy/title/body. They neither trust
its stored skip bit nor rewrite its timestamp/version. Thus removing an exclusion or
retitling a vacancy can clear an old skip, and newly enabling an exclusion can take
effect. Missing receipts retain the previous non-skipping queue behavior. Malformed
receipts (wrong schema/boolean/confidence/version/identity) do not establish a skip.
Legacy archive-test fixtures now contain actual SRE titles and real receipts rather
than orphan `skip_model` flags with no corresponding source evidence.

[test_selection_runtime.py](../tests/test_selection_runtime.py) covers each policy
group, relevant/irrelevant edits, every supported technology, ordered explanations,
legacy/new/missing/malformed receipts, title/body changes, file/snapshot/pending/archive
parity, command loading once, and invalid policy rejection before fetch, migration,
archive access, leases or writes. The real-MongoDB storage-bridge regression verifies
that policy and title refresh reads preserve stored receipt contents and revisions.

Targeted command on 2026-10-20, with the disposable test URI set:
`python -m unittest tests.test_selection_runtime tests.test_selection_baseline tests.test_selection_policy tests.test_prefilter tests.test_triage tests.test_workflow_api tests.test_archive_jobs tests.test_cli tests.test_storage_bridge -v`:
**106 tests passed in 21.365 seconds, no skips**. This includes unchanged baseline
results; full checks and independent review were pending at this checkpoint. No
production operations, candidate/artifact/status changes, source-query changes,
MongoDB schema/index/database/adapter changes or catalog input changes were performed.

Independent review R3 identified CR-002: a large valid age setting could overflow
datetime cutoff subtraction after collection had fetched rows. The correction compares
elapsed microseconds against an integer day threshold, preserving strict cutoff
semantics without float conversion or an arbitrary configuration upper bound. Regression
coverage includes 1,000,000 days, a 1,001-digit integer, explicit overrides, a dated
collection row and the exact cutoff plus/minus one microsecond. The coordinator's
pre-correction full MongoDB suite passed 723 tests in 121.885 seconds with no skips;
after correction, 57 selection-runtime/baseline/prefilter/CLI targeted tests passed in
3.204 seconds. These checks preceded the final verification recorded below.

Final acceptance on 2026-10-20: review R3 approved the corrected increment and closed
CR-002 after 43 focused tests passed. Restoring cutoff subtraction in memory caused
two expected `OverflowError` regression failures, confirming the new tests exercise
the defect. The coordinator's final post-correction full suite against the disposable
MongoDB replica set passed **725 tests in 136.660 seconds, no skips**. API-prohibition
unit and explicit runtime/configuration search checks, local Markdown links and
`git diff --check` passed. Phase 2 is accepted and done; publication is the coordinator's
next action. Phase 3 remains unstarted.

## Phase-3 accepted implementation

Phase 2 was published as `d5711331d032c38d27d995ee6a820f7cdfef8c0c` in PR 2.
Independent cumulative review R4 approved the clean published worktree after 90 tests
and a four-failure negative control. Phase 3 is complete; its runtime contract
is documented in [matching-policy.md](matching-policy.md).

`config/matching-policy.yaml` now owns the former personal preferences from the match
prompt: remote work, meaningful preferred technologies, discouraged central technology
requirements/SRE roles, relocation packages, cities, support/email domains and the
US-hours exception. Scoring weights and general evidence/blocker rules remain in the
generic prompt. No model or numeric adjustment logic moved into project code.

A runtime context binds generic prompt, output schema and typed policy in the existing
`prompt_version` field. Candidate evidence/profile hashes, stored scores and model
provenance remain separate. A shared freshness predicate reaches file/snapshot queues
and actual preparation preflight. New schema-2 single/batch drafts seal and validate
actual profile/vacancy/policy/prompt payloads as well as hashes, selectors and current
canonical source comparisons. Source/distributed manual and scheduled instructions
use that same envelope while retaining single-vacancy manual isolation.

Before the final additional real-MongoDB regression, 113 targeted runtime, seal,
policy, workflow, preparation, storage-bridge and API-prohibition tests passed in
17.001 seconds with no skips. An additional real-MongoDB regression passed in 0.825
seconds: an unpatched preparation preflight and actual snapshot queue accept a current
match, a policy change makes it stale in both paths, and stored match/document/revision
remain unchanged. The directory-link escape test runs through a real temporary Windows
junction when symlink privilege is unavailable. At that checkpoint, full acceptance
and the exact production legacy bridge pin awaited review and actual blind passes.

Review R5 requested CR-005 and CR-006 corrections: raw public publication could assign
current provenance to an unbound result, and a resealed source URL could reach
notifications. Public publication now requires a complete sealed one-item draft;
batch validation compares every notification source URL with current metadata before
any write. The corrected focused suite passed 52 tests in 14.658 seconds with actual
disposable MongoDB and no skips. In-memory negative controls caused four expected
raw-publication subtest failures and one expected URL-binding failure; the restored
two-test control passed. At that checkpoint, these fixes awaited independent R5
re-review and finalizer retry/rebase findings CR-003/004 awaited architecture
verification. Mechanical results alone did not establish semantic acceptance.

R5 core re-review subsequently approved and closed CR-005/006. The actual independent
matching evaluation passed: 56 judgments and 28 pair rows, zero ties/inversions, four
hard rejections, with all pair reasoning reviewed by the coordinator. The exact
approved effective identity is now pinned for the narrow old-813df legacy bridge;
its digest and evaluation hashes are recorded in [matching-policy.md](matching-policy.md).
Production-constant tests verify unchanged current/legacy reuse and invalidation on
prompt/schema/policy/profile/job/model changes, preserving historical bytes. The
post-pin targeted actual-MongoDB suite passed 58 tests in 14.738 seconds, no skips.
Identical judgments from one masked reviewer do not establish independent numeric
replication or complete variant-identity blindness.

The initial editorial pass scored 9/10; its proposal-only evidence defensibly led the
reviewer to omit a claim under a production-experience requirement. Technical review
found ambiguity between CV selection and delivery-stage grounding. Only the synthetic
case kind/requirement was clarified; source text, claim, curated disposition and
production editorial policy stayed unchanged. A fresh independent pass scored 10/10,
and the coordinator inspected every reason. Exact corpus/policy/decision hashes are
recorded in [matching-policy.md](matching-policy.md).

Final full verification used Python 3.14.6 and a disposable MongoDB 8 replica set:
`python -m unittest discover -v` passed 782 tests in 127.566 seconds, no skips.
API-prohibition unit/search and diff checks passed. Core post-pin review approved;
architecture R5a approved and closed CR-003/004 after 47 independent tests, five
mutation failures and restored controls, also revalidating the actual matching receipt.
The completed final council (first principles, contrarian and fresh executor) and
anonymized peer review approved bounded publication, with no confirmed must-fix or
material code disagreement. They agreed that explicit configuration, shared
freshness, seals and the exact legacy pairing fit phases 0-3 without adding account
infrastructure. The fresh executor separately passed 67 focused tests in 79.035
seconds; this is independent focused evidence, not the coordinator's 782-test suite.

Accepted limits remain one masked matching reviewer and a small synthetic corpus:
identical judgments do not demonstrate broad numeric stability or hiring effects.
Receipt recomputation verifies bindings rather than independently corroborating
semantic judgments. The editorial clarification does not establish that the original
omission was wrong. Retain the exact ignored evaluation packs, decisions and receipts
with the recorded hashes for repeat binding validation; these artifacts remain
outside the tracked evidence.

Phase 3 is complete in [PR 2](https://github.com/ValentinNikolaev/job-intelligence/pull/2).
Cumulative R6 approved the published runtime and found only CR-007: Windows checkout
conversion changed frozen baseline bytes. The minimal `.gitattributes` correction
in [`e30d2dc`](https://github.com/ValentinNikolaev/job-intelligence/commit/e30d2dc2941ed79ee87239e2ee7260498151e611)
pins only that fixture to LF. Fresh clean Windows R7 review with `core.autocrlf=true`
approved and closed CR-007: index/worktree LF, 66 LF/zero CR, original hash preserved,
23 passing executions in 2.563 seconds. The council peer retained approval.
[Exact-commit PR CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39428852968/attempts/1)
passed 782 tests in 24.858 seconds with two missing-Poppler PDF skips. The local full
suite had no skips. Earlier CI's before-test MongoDB startup failure and successful
retry are retained in the [plan's final synthesis](multiaccount-migration-plan.md).
The next action is reviewed finalizer publication of the documentation-only acceptance
increment and final PR handoff. Changed bindings/integrated code, refused publication,
new review defects or CI failures require reassessment. Phases 4-6 remain deferred.

## Phase-4 preparation configuration

Phase 4 is in progress. The [preparation guide](preparation-configuration.md) records
configuration ownership, source boundaries, profile precedence and legacy behavior.
Personal filename, path, employer-alias and career-window decisions move to the
required `preparation` section of `config/application-profile.yaml`; voice paths stay
in `config/application-review.yaml`. Shared grounding and editorial guidance stay in
`config/cv-editorial-knowledge.yaml`. The reviewed default clarification records retain
the existing date precision, title/technology attribution and source-backed rendering
limits. Candidate records themselves remain unchanged.

The pre-existing Zend-credential exclusion remains a shared current editorial
restriction in the generic application prompt and validator. This iteration does not
claim that every personal editorial exception is configurable. Review that restriction
before candidate-independent onboarding in phase 5, alongside the deferred source-side
relevance preferences. A second live account remains phase 6 work.

See the [migration execution log](multiaccount-migration-plan.md#execution-log) for
actual baseline disagreements, review findings, corrective work and release gates.
