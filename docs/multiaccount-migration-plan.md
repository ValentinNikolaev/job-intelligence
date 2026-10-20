# Phased migration to account-specific configuration

Created: 2026-10-20. Last updated: 2026-10-20.

## Goal and current scope

Make personal selection rules and candidate-specific behavior configurable while
keeping the current system operational after every phase. Connect a second account
only in the final phase.

An account represents one candidate, their preferences, evidence, application
history and integration destinations. Multiple search profiles for the same
candidate do not require separate accounts.

The authorized implementation covers **phases 0-3**, in reviewed increments: baseline
and dormant configuration (0-1), deterministic cutover (2), then analysis preferences
(3). Phases 0-2 retain a standalone release gate. Later phases and operating a second
account remain outside this authorization.

## Progress and maintenance

Phases 0-2 are complete, published and independently reviewed. Phase 3 is in progress:
analysis preferences, shared freshness and sealed Codex drafts passed core review and
both independent semantic gates. Full MongoDB verification and architecture review
passed. The final three-view council and anonymized peer review approved the bounded
implementation for publication in draft PR 2. Phase 3 remains in progress until clean
published-worktree review R6 and CI on the exact published commit pass.

| Phase | Deliverable | Depends on | Status |
| --- | --- | --- | --- |
| 0 | Inventory and behavioral baseline | None | Done |
| 1 | Validated configuration for existing selection rules | 0 | Done |
| 2 | Configuration-driven prefilter and triage | 1 | Done |
| 3 | Configurable match-analysis preferences | 2 | In progress |
| 4 | Candidate-independent document preparation | 3 | Not started |
| 5 | Explicit account description with one live account | 4 | Not started |
| 6 | Second account in an isolated environment | 5 | Not started |

Maintain this file in the same change as implementation progress:

- Use `Not started`, `In progress`, `Blocked`, or `Done` in the phase table.
- Check a task only when its deliverable exists and its required verification passes.
  Starting a task does not complete it; leave unfinished substeps unchecked.
- Append a dated execution-log entry with completed checklist items, affected paths,
  verification commands and outcomes, remaining work and any blocker. Link to durable
  evidence where available; an ignored local file alone is not durable evidence.
- Mark a phase `Done` only after its acceptance gate passes. Record justified skips
  and limitations explicitly, rather than presenting them as passed checks.
- Record changed scope or decisions here before marking the affected work complete.
- Keep pending work in this file across interruptions. Resume from the last verified
  step instead of repeating completed work or restarting the migration.
- Do not insert a commit hash before it exists. The publishing commit already binds
  each progress update to its code and checks; a later entry may reference that hash.

## Boundaries for the first iteration

- Keep the current MongoDB database, schema, indexes, storage adapter, transactions
  and leases. Do not add an account field or migrate operational records.
- Preserve existing CLI commands, scheduled entrypoints, paths, environment-variable
  behavior and integration destinations.
- Keep candidate evidence and published application artifacts unchanged.
- Keep analysis prompts, scores, preparation rules and model routing unchanged.
- Do not introduce new country, language, role or technology restrictions while
  extracting the existing ones. Preserve precedence and rejection explanations.
- Do not bulk reanalyze, reclassify, archive or change vacancy statuses. Historical
  employer decisions and immutable feedback remain intact.
- Keep model-dependent work in Codex; project code must not call the OpenAI Platform
  API or an OpenAI-compatible model endpoint.

## Phase 0: inventory and behavioral baseline

Tasks:

- [x] Inventory personal rules in `jobintel/`, `sources/`, `config/`, `prompts/`,
  `.agents/skills/`, scripts and GitHub Actions. Record location, current value,
  consumer, precedence and intended configuration owner in this document or a linked
  inventory. Identify duplicated or contradictory rules without changing them.
- [x] Separate personal decisions from shared mechanics: recognizing a mandatory
  language requirement is shared; deciding whether that language blocks a candidate
  belongs to the candidate's policy.
- [x] Build on `tests/test_prefilter.py`, `tests/test_triage.py` and collection/queue
  tests to capture representative accepted, rejected and ambiguous vacancies.
  Freeze the reference time for age-dependent cases.
- [x] Capture current decisions, rejection categories, explanations, rule precedence
  and relevant queue behavior. Include optional versus mandatory languages, mixed
  stacks, European exceptions to American-hours restrictions and title/body triage.
- [x] Record baseline checks and any pre-existing failures separately from migration
  failures. Use fixtures or read-only snapshots; do not probe production with writes.

Acceptance gate: the inventory identifies the consumers that must change together,
and durable tests can expose behavior drift during extraction.

Implementation evidence: [rule inventory and baseline](multiaccount-rule-inventory.md),
39 fixed-time prefilter cases, 13 triage cases and four queue cases. The phase-0/1
increment retained the original runtime. Its MongoDB checks passed 710 tests with no
skips. Independent review R1 approved the corrected increment, including a mutation
that confirms receipt-timestamp preservation is exercised; the phase is `Done`.

## Phase 1: validated configuration, without runtime cutover

Tasks:

- [x] Introduce `config/selection-policy.yaml` with a versioned schema reproducing
  the baseline rules. Phase 1 shipped it as a dormant interface; phase 2 activates it.
- [x] Cover maximum vacancy age, excluded roles, target technologies, excluded
  technologies and combinations, remote requirements, blocking mandatory languages,
  existing location/timezone decisions and triage exclusions.
- [x] Keep company retry rules in `config/application-profile.yaml` for this iteration.
  Do not create another authoritative copy. Keep already configurable source queries
  in `sources/*/config.yaml` and workflow settings in `config/codex-workflows.yaml`.
- [x] Add a typed loader with strict field/type/version validation. Reject unknown
  fields and contradictory settings; document defaults, path resolution and ordering.
- [x] Define explicit list semantics. Avoid implicit concatenation or layered
  inheritance in this iteration. Configuration must not contain executable code.
- [x] Test valid configuration and failures for missing required settings, malformed
  YAML, unsupported versions and unsupported rule values. Diagnostics identify the
  file and field without exposing secrets.
- [x] Leave the operational flow on the existing implementation until phase 2.
  Do not expose unsupported allowlist or other future capabilities as working fields.

Acceptance gate: the file describes the existing behavior completely, validates
deterministically, and does not yet alter production decisions.

Implementation evidence: phase 1 added dormant `jobintel/selection_policy.py`, explicit
version-1 configuration and strict loader tests. Immutable relevant-subset digests
support phase 2; phase 1 changed no operational imports or CLI arguments. Its MongoDB
checks passed 710 tests with no skips. Independent verification of the final test
correction passed and review R1 approved the increment; the phase is `Done`.

## Phase 2: configuration-driven deterministic selection

Tasks:

- [x] Load and validate the policy once at each relevant command boundary, before
  collection requests or mutations. Pass it explicitly to consumers; avoid hidden
  mutable process-wide settings. A required invalid policy fails closed.
- [x] Switch `jobintel/prefilter.py` and collection callers in `jobintel/cli.py` to the
  typed policy. Retain normalization, text recognition, precedence and explanations.
- [x] Switch `jobintel/triage.py` and its CLI, pending-queue, `workflow_api.py` and
  skipped-archive
  consumers together. Test both path-based and MongoDB snapshot-based queue paths.
- [x] Define triage freshness using the existing `triage_version` field, without a
  MongoDB schema change. An unchanged legacy-equivalent policy may reuse legacy
  decisions; changed relevant rules must trigger recomputation or an explicit
  refresh requirement, never silently reuse an incompatible skip decision.
- [x] Compare old and new results on the phase-0 corpus without writing production
  records. Compare decisions, categories, reasons and queue behavior, not just totals.
- [x] Add meaningful tests showing that changing one supported configuration value
  changes its intended decision, while unrelated settings preserve other decisions.
- [x] Verify existing commands and automation entrypoints still work with their
  existing arguments. Remove obsolete personal decision constants only after all
  consumers have switched; shared recognition dictionaries may remain code.
- [x] Run the release checks below and record the resulting evidence and limitations.

Acceptance gate: baseline decisions are equivalent, configuration changes are
effective, stale triage cannot bypass updated rules, and no storage migration or
historical record rewrite is needed. Phases 0-2 form a standalone release.

Implementation evidence: [phase-2 runtime contract](multiaccount-rule-inventory.md#phase-2-cutover-and-verification)
and targeted disposable-MongoDB checks (106 tests passed, no skips). Current baseline
decisions and explanations remain equal; stale/legacy triage reads reevaluate current
inputs without rewriting receipts. Final post-correction full checks passed 725 tests
with no skips. Review R3 approved the corrected increment, closed CR-002 and verified
that restoring cutoff subtraction triggers the regression tests. The coordinator
accepted phase 2; it is `Done`.

Recovery: revert the extraction/configuration change if its release gate fails.
No database rollback should be necessary for extraction alone. Any records written
by normal operation remain real history and must not be discarded.

## Phase 3: configurable analysis preferences

Tasks:

- [x] Extract candidate-specific scoring preferences from `prompts/vacancy-match.md`:
  technology and role preferences, Rome, relocation, support/email domains and
  timezone compatibility. Preserve the distinction between preferences and blockers.
- [x] Supply a deterministic, versioned policy snapshot to individual and sealed-batch
  analysis. Keep semantic evaluation inside Codex and source text as data.
- [x] Run the required [blind editorial evaluation](../prompts/editorial-evaluation.md)
  before changing application prompts or editorial policy; record its evidence.
- [x] Bind match freshness to the relevant effective inputs using the existing
  versioning contract where possible. Changing notification settings must not stale
  a match; changing scoring preferences must be detected.
- [x] Define compatibility for existing matches explicitly. Preserve original model,
  score, prompt/profile provenance and legacy receipts; never relabel old judgments.
- [x] Test analysis and preparation-preflight freshness consistently. Avoid automatic
  mass reanalysis and distinguish input-version changes from semantic policy changes.

Acceptance gate: personal analysis preferences come from configuration, changed
inputs invalidate the right results, and evaluation supports the intended behavior.

Working-tree evidence: [matching policy and sealed analysis](matching-policy.md),
strict qualitative policy loader, shared runtime effective-input identity and actual
payload-bound schema-2 drafts. Targeted unit and real-MongoDB checks exercise current
and stale inputs without rewriting original judgments. R5 core review approved the
corrected publication boundaries. Actual blind matching evaluation passed and its
exact effective identity is pinned for legacy compatibility. Fresh independent
editorial evaluation passed 10/10 after bounded fixture clarification. Final full
MongoDB verification passed 782 tests without skips; core post-pin and architecture
R5a reviews approved. Final council and peer review accepted the local implementation
and gates for publication; phase 3 is `In progress`. Publication, clean R6 review and
exact-commit CI are future steps.

### Final council synthesis

All three independent views (first principles, contrarian and a fresh executor) and
the anonymized peer review approved bounded publication, with no confirmed must-fix
or material code disagreement. Explicit configuration, shared freshness, sealed
inputs and the exact legacy-version pairing fit phases 0-3; account infrastructure
and phases 4-6 remain deferred. The fresh executor independently passed 67 focused
tests in 79.035 seconds, separately from the coordinator's 782-test full suite.

The weakest accepted evidence is one masked matching reviewer and a small synthetic
corpus. Identical variant judgments do not prove broad numeric stability or hiring
effects. Recomputing a receipt checks bindings; it is not independent semantic
corroboration. The editorial fixture clarification does not establish that the
original omission judgment was wrong. Underlying semantic artifacts remain ignored;
the coordinator will preserve the exact current packs, decisions and receipts, copy
them into the clean R6 checkout and revalidate them through R6 and CI.

The next action is reviewed finalizer publication into draft PR 2, followed by clean
R6 and CI on the exact published commit. Finalizer refusal, changed bindings or
integrated code, R6 defects or CI failures require reassessment. Phase 3 will be
marked done only after those gates actually pass, in a final documentation increment.

## Phase 4: candidate-independent document preparation

Tasks:

- [ ] Configure the CV filename owner currently fixed in `jobintel/applications.py`.
- [ ] Resolve candidate evidence and voice-source paths explicitly while preserving
  the current paths for the existing candidate and immutable source contents.
- [ ] Separate personal career boundaries from general editorial requirements.
  Replace employer-specific branches in `jobintel/career_coverage.py` with reviewed,
  source-bound clarification handling; do not invent candidate chronology.
- [ ] Update evidence validators, manifests and quality checks together. Keep
  candidate sources, artifacts and drafts bound to the correct context.
- [ ] Update `AGENTS.md`, local skills, prompts and documentation consistently so
  candidate-specific instructions do not override another candidate's configuration.
  Run the required blind evaluation before editorial-policy changes.
- [ ] Verify the current candidate retains approved career coverage and quality gates.
  Preparing real documents still requires explicit named-vacancy authorization,
  `prepare-preflight` and the required cover-letter skill.

Acceptance gate: preparation mechanics no longer depend on one person's name or
employer, with existing grounding and application-quality protections preserved.

## Phase 5: explicit account description, one live account

Tasks:

- [ ] Add a small versioned account descriptor referencing the existing policy,
  profile, source configurations, data paths and integration destinations. Reuse
  configuration already extracted; avoid moving files merely to create a directory.
- [ ] Introduce one resolver/context for these references and an explicit `--account`
  selector. Keep the existing account as the documented default.
- [ ] Resolve account selection before dispatch, including separate handlers for
  `storage`, `sheets`, `applications`, `documents`, `evidence` and related commands.
- [ ] Specify CLI/environment/config precedence and reject conflicting or unknown
  account selection before data access. Test store caches and credential scoping.
- [ ] Check current scheduled prompts, GitHub Actions, catalog generation, exports,
  notifications, backups and repository finalization with the single live account.
- [ ] Use isolated fixtures to exercise distinct contexts without onboarding a second
  live candidate. Retain current MongoDB connection, schema and current file paths.
- [ ] Resolve the deferred source-side Go/PHP/Italy relevance preferences listed in
  the rule inventory, or explicitly scope the supported source set, before claiming
  candidate-independent onboarding. Phases 0-3 leave those source decisions intact.

Acceptance gate: implicit default and explicit current-account runs are equivalent;
unknown accounts fail early. Only one live account is enabled.

## Phase 6: connect the second account last

Tasks:

- [ ] Add the second candidate's verified sources and configurations after phases
  0-5 pass. Supply secrets through the environment, never tracked configuration.
- [ ] Start with separate executions/environments of the same codebase. Keep records,
  evidence banks, application artifacts, drafts, catalogs, exports and notification
  delivery state isolated. A shared operational vacancy pool is outside this plan.
- [ ] Provision a separate operational destination using the existing storage
  contract. Choose and review its deployment configuration here; do not retrofit
  account fields into the current MongoDB database as an earlier prerequisite.
- [ ] Scope locks and budgets to the resources they protect. Shared source credentials
  still share provider quotas; repository publication still coordinates shared Git.
- [ ] Validate read-only configuration resolution first, then bounded collection and
  analysis. Prepare real applications only with explicit named-vacancy approval.
- [ ] Verify the same source vacancy can have independent match results, statuses,
  history and delivery state. Test export, archive and isolated restore boundaries.
- [ ] Verify onboarding required configuration and evidence, not personal Python
  branches or edits to generic prompts. Keep the first account operational.

Acceptance gate: both candidates operate independently and no evidence, document,
decision, status or notification crosses account boundaries.

## Release checks and deferred work

Each implementation release must run relevant targeted tests, then
`python -m unittest discover -v` under Python 3.11+, and search project
code/configuration for prohibited API integrations. Report unavailable integration
checks honestly; absence of a MongoDB test service is not a passing integration test.
Inspect the complete diff and publish through the reviewed repository finalizer
from an isolated managed worktree. Regenerate the vacancy catalog only when the
workflow changes its inputs; documentation-only planning does not require it.

Documentation-only updates require link, checklist consistency and diff checks;
they do not establish runtime verification of the planned implementation.

The first release must not expand into generic rule scripting, a web account/login
system, a shared multi-tenant database, shared vacancy ingestion, simultaneous
multi-account execution, moving existing artifacts or reorganizing the CLI.
Such work requires a separate decision after the phased migration is useful.

## Execution log

| Date | Work completed | Verification and remaining work |
| --- | --- | --- |
| 2026-10-20 | Inspected current personal-rule/configuration boundaries; recorded the phased plan, gates and progress-update protocol; linked it from `TECHNICAL_README.md`. | Local Markdown links, seven pending phases and 45 unchecked tasks verified; `git diff --check` passed. Runtime tests not run: documentation only. No implementation, runtime cutover, database migration or second-account onboarding performed. All phase checklists remain open. |
| 2026-10-20 | Authorized implementation scope expanded to phases 0-3 with separate reviewed increments. Implemented phase-0 inventory and synthetic corpus in `docs/multiaccount-rule-inventory.md`, `tests/fixtures/selection-baseline.yaml` and `tests/test_selection_baseline.py`; added phase-1 dormant configuration, immutable strict loader and loader tests. Added archive skip readers to the phase-2 consumer inventory. | Before implementation, coordinator verified 697 tests with no skips on Python 3.14.6 and a disposable MongoDB 8 replica set using `JOBINTEL_TEST_MONGODB_URI` and `python -m unittest discover -v`. New targeted command `python -m unittest tests.test_selection_policy tests.test_selection_baseline tests.test_prefilter tests.test_triage -v`: 42 tests passed, including 13 new test methods. `git diff --check` passed. Both phases remain in progress pending independent increment review and full post-change verification. No runtime cutover, candidate/artifact/status changes or catalog input changes; phases 2-3 remain unstarted. |
| 2026-10-20 | Iteration-1 review fixes: target identifiers now use all existing technology recognizer capabilities rather than the selected Go/PHP defaults; invalid UTF-8 receives a safe file/field validation error; the triage repeat test advances its clock by one day and asserts the original receipt timestamp and bytes survive. | Coordinator's full post-change `python -m unittest discover -v` against the disposable MongoDB replica set passed 710 tests in 53.325 seconds with no skips. That run preceded the final test-only clock correction; `python -m unittest tests.test_selection_baseline tests.test_selection_policy -v` passed all 13 tests after the correction. Phase-0/1 statuses remain in progress pending the reviewer's verification of the corrected diff; no phase-2 runtime work has started. |
| 2026-10-20 | Independent review R1 approved iteration 1; finding CR-001 closed and coordinator accepted phases 0-1. Marked both phases done. | Reviewer independently passed all 13 targeted selection tests and verified that removing timestamp preservation produces 13 expected triage subtest failures. Full MongoDB evidence remains 710 passing tests, no skips. Phase 2 remains unstarted; runtime behavior and operational records are unchanged. |
| 2026-10-20 | Published phases 0-1 as commit `188d3c4c34253b8fd91a373e678f160910aed7ad` on the feature branch in [PR 2](https://github.com/ValentinNikolaev/job-intelligence/pull/2). Independent post-integration review R2 approved the clean published increment. Started phase 2 configuration cutover for prefilter, triage, pending queues, workflow API and skipped archive readers. | R2 independently passed 13 targeted tests and diff checks. Published-commit CI passed 710 tests with two PDF-tool skips on Ubuntu; local MongoDB suite had no skips. The PR CI's initial MongoDB container startup failure occurred before tests and passed on rerun. Phase 2 remains in progress; targeted runtime checks are underway before full checks and independent review. No phase-3 work or production data writes. |
| 2026-10-20 | Completed the phase-2 working-tree cutover: explicit immutable policy at collection/triage/pending/API/skipped-archive boundaries; shared pure triage with policy/recognition/current-input version binding; read-only stale/legacy refresh; policy-efficacy and side-effect regression tests, including real-MongoDB receipt/revision preservation. Updated integration fixtures and preserved source/CLI/storage contracts. | `JOBINTEL_TEST_MONGODB_URI` set only to the disposable local replica set; targeted selection/prefilter/triage/API/archive/CLI/storage-bridge suite passed 106 tests in 21.365 seconds with no skips. Independent review and full release checks remain pending, so phase 2 is in progress. Source-side relevance extraction is explicitly deferred before second-account onboarding; phase 3 remains unstarted. |
| 2026-10-20 | Review R3 identified CR-002: a positive million-day age setting passed schema validation but constructing the datetime cutoff overflowed after collection fetched rows. Replaced cutoff subtraction with exact integer elapsed-microsecond comparison; positive configuration integers remain supported, including values beyond floating-point range. Added million-day/1,001-digit policy and explicit-override regressions, one-microsecond cutoff cases and a dated-row collection regression. | Coordinator's pre-correction full MongoDB suite passed 723 tests in 121.885 seconds with no skips. After correction, selection-runtime/baseline/prefilter/CLI targeted checks passed 57 tests in 3.204 seconds; `git diff --check` passed. Final full checks and independent re-review of CR-002 remain pending. Phase 2 remains in progress; no phase-3 changes or production operations. |
| 2026-10-20 | Review R3 approved the corrected phase-2 increment and closed CR-002. Coordinator accepted phase 2 and marked it done. | Reviewer independently passed 43 focused tests and confirmed that restoring old cutoff subtraction in memory causes two expected `OverflowError` regression failures. Final post-correction `python -m unittest discover -v` with the disposable MongoDB replica set passed 725 tests in 136.660 seconds with no skips. API-prohibition unit check, explicit runtime/configuration API search, local Markdown-link checks and `git diff --check` passed. Catalog inputs remain unchanged. Publication remains the coordinator's next step; phase 3 is unstarted. |
| 2026-10-20 | Published phase 2 as commit `d5711331d032c38d27d995ee6a820f7cdfef8c0c` in PR 2. Cumulative review R4 approved the clean published worktree. Started phase 3 with separate matching policy, runtime effective-input identity, shared freshness, sealed individual/batch Codex drafts and the bounded semantic-evaluation gate. | R4 independently passed 90 tests and verified a negative control caused four expected failures before restoring the passing control. Phase 3 is in progress; semantic evaluation and acceptance remain pending. No later-phase account work, model endpoint calls or production operations. |
| 2026-10-20 | Implemented phase-3 runtime policy/context, shared freshness and schema-2 payload sealing for direct/CLI single and batch publication. Added strict policy and negative integrity tests, real unpatched preparation freshness, file/MongoDB snapshot parity and fail-before-side-effect checks. Updated source/distributed manual workflow and scheduled contracts; integrated the independently developed synthetic scoring evaluator/finalizer gate through its separate file owner. | Combined targeted disposable-MongoDB suite passed 113 tests in 17.001 seconds with no skips; one additional real-MongoDB preflight/snapshot policy-change regression passed in 0.825 seconds. Seal/policy/matching/workflow-contract checks passed 55 tests in 5.076 seconds with no skips after adding a Windows junction fallback for actual link-escape coverage. Runtime/prompt review R5 is underway. The legacy bridge remains disabled until the exact reviewed effective identity passes actual independent semantic evaluation; no approval is inferred from fixture tests. |
| 2026-10-20 | R5 requested CR-005/006 corrections after 57 independent focused tests: public raw-result publication could assign current provenance to old analysis; a resealed source URL could enter notifications. Required complete sealed input at the public single-publication boundary and canonical source-URL comparison for every batch item before writes. Added valid public-single and forced/raw/copied-label/last-item URL regressions. Separately owned finalizer retry/rebase findings CR-003/004 are undergoing architecture verification. | Corrected matching/seal/batch/storage-bridge checks passed 52 tests in 14.658 seconds against actual disposable MongoDB, no skips. In-memory negative controls produced four expected raw-publication subtest failures and one expected URL-binding failure; restored two-test control passed. Core fixes await independent R5 re-review. Frozen prompt/schema/policy inputs are undergoing actual independent blind semantic/editorial evaluation; no legacy pin or phase-3 acceptance yet. |
| 2026-10-20 | R5 core re-review approved CR-005/006 and closed both findings. Actual blind matching evaluation passed and coordinator reviewed all pair reasoning: 56 judgments, 28 comparison rows, zero ties/inversions and four hard rejections across two conflict types and two variants; no source-quote/band issues. Authorized exact production legacy pin `job-match-v2:sha256:936069737a4caa24ba6a39627dc3ef204e5bee92bf658d074f62be57028137c5`. | Decisions SHA-256 `91aeb564fcc6a843ad11167ddc239d3530aa4ab490ec940a216ec85a4135f3d9`; blind-pack SHA-256 `d2b16de239aa5c34fdd12ca82237c5b4fbae35de2d5717b5554e96c29154d71f`. One masked reviewer gave identical judgments for equivalent-policy variants; this does not establish independent numeric replication, variant-identity blindness or hiring effectiveness. Real-constant tests exercise current/legacy reuse and prompt/schema/policy/profile/job/model invalidation without rewriting receipts/history; targeted actual-MongoDB checks passed 58 tests in 14.738 seconds, no skips. Editorial, final full-suite and cumulative acceptance gates remain pending; phase 3 stays in progress. |
| 2026-10-20 | Initial phase-3 editorial evaluation scored 9/10. The reviewer retained omission on adjudication because proposal-only evidence did not satisfy a production-experience requirement. Technical review identified ambiguity between CV selection and the intended delivery-stage grounding contract. Coordinator authorized the separate evaluator owner to clarify only that synthetic case's kind/requirement, leaving source, claim, curated disposition and production editorial policy unchanged. | A fresh independently evaluated ten-case export remains required; 10/10 is not claimed. Matching-evaluation inputs and its 56-judgment receipt remain unchanged. Finalizer retry/rebase/tie-gate review CR-003/004 remains independently pending at this checkpoint; phase 3 remains in progress. |
| 2026-10-20 | Fresh independent editorial assessment passed 10/10; coordinator inspected every reason. The earlier 9/10 and defensible omission/adjudication remain recorded above. Core post-pin review approved without new findings. Architecture R5a re-review approved and closed CR-003/004 after 47 independent tests, five expected mutation failures and restored controls; actual matching receipt revalidated. | Editorial corpus SHA-256 `569ee2c6f5b55b9c8fa3e06030e239e11a26d52b0bff4627fc3bcd87a15e1ecc`, policy `222e61ce3544f70f9ef2b463c9b4c911ed5ac19cee11e39878e27d109e8665cd`, decisions `6c109f3db119d58f7b2626da7a6ab5dc01fc4309b9a82f08017d282943596555`. Final `python -m unittest discover -v` on Python 3.14.6 with disposable MongoDB 8 passed 782 tests in 127.566 seconds, no skips; API unit/search and diff checks passed. Two final council views approved bounded draft publication; the third view and anonymized peer review remain pending. Phase 3 stays in progress. Publication, clean R6 and exact-published-commit CI remain future steps. |
| 2026-10-20 | Final council and anonymized peer review approved bounded publication with no confirmed must-fix; synthesis and accepted evidence limits recorded above. All three views agreed on phases 0-3 boundaries; phases 4-6 remain deferred. Fresh executor verification passed 67 focused tests in 79.035 seconds, independently of the coordinator's full suite. | Local implementation and gates are accepted for publication into draft PR 2. Exact ignored semantic packs/decisions/receipts will be preserved and revalidated in the clean review checkout. Receipt recomputation establishes bindings, not independent semantic corroboration; the one-reviewer synthetic evaluation remains limited. Phase 3 stays in progress pending actual finalizer publication, clean R6 and exact-published-SHA CI. |
