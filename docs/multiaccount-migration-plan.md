# Phased migration to account-specific configuration

Created: 2026-10-20. Last updated: 2026-10-20.

## Goal and current scope

Make personal selection rules and candidate-specific behavior configurable while
keeping the current system operational after every phase. Connect a second account
only in the final phase.

An account represents one candidate, their preferences, evidence, application
history and integration destinations. Multiple search profiles for the same
candidate do not require separate accounts.

Phases **0-3** were implemented in reviewed increments and merged in PR 2. Phase **4**,
candidate-independent document preparation, is complete in
[PR 3](https://github.com/ValentinNikolaev/job-intelligence/pull/3) on a new branch
from the updated main. Phase **5** was implemented on a new branch from merged
main and is now complete in [PR 4](https://github.com/ValentinNikolaev/job-intelligence/pull/4);
phase 6 and operating a second account remain deferred.
Existing named-vacancy approval requirements still apply to actual application
preparation; this implementation iteration uses synthetic fixtures only.

## Progress and maintenance

Phases 0-3 are complete in [PR 2](https://github.com/ValentinNikolaev/job-intelligence/pull/2):
implementation, independent semantic gates, final council, cumulative published-code
review and the clean-checkout correction review passed. The exact corrected commit
[`e30d2dc`](https://github.com/ValentinNikolaev/job-intelligence/commit/e30d2dc2941ed79ee87239e2ee7260498151e611)
passed [PR CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39428852968/attempts/1).
PR 2 was merged as `83d812e29fdfbbc1aa942def52011fe5a6bab2d3`. Phase 4 is complete on
`ValentinNikolaev/multiaccount-p4`, created from that updated main, and published
in PR 3. Independent cumulative review R3 approved the clean published code at
`d8495d0d64f1d49566a2cdc8cdf11ac547d1e2f6`; both exact-head CI runs passed.
The iteration extracts preparation configuration while preserving analysis
identities, candidate sources and published artifacts. PR 3 was merged as
`e87e8dd9dd973a963b058abe0a2827c66b6385cb`. Phase 5 is complete on
`ValentinNikolaev/multiaccount-p5` from that updated main. Clean cumulative R6
approved published runtime `d66943b60107a196dc7a04f94429a6932aca058e`; exact-head
push and PR CI passed. PR 4 remains open and unmerged; phase 6 remains deferred.

| Phase | Deliverable | Depends on | Status |
| --- | --- | --- | --- |
| 0 | Inventory and behavioral baseline | None | Done |
| 1 | Validated configuration for existing selection rules | 0 | Done |
| 2 | Configuration-driven prefilter and triage | 1 | Done |
| 3 | Configurable match-analysis preferences | 2 | Done |
| 4 | Candidate-independent document preparation | 3 | Done |
| 5 | Explicit account description with one live account | 4 | Done |
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

Implementation evidence: [matching policy and sealed analysis](matching-policy.md),
strict qualitative policy loader, shared runtime effective-input identity and actual
payload-bound schema-2 drafts. Targeted unit and real-MongoDB checks exercise current
and stale inputs without rewriting original judgments. R5 core review approved the
corrected publication boundaries. Actual blind matching evaluation passed and its
exact effective identity is pinned for legacy compatibility. Fresh independent
editorial evaluation passed 10/10 after bounded fixture clarification. Final full
MongoDB verification passed 782 tests without skips; core post-pin and architecture
R5a reviews approved. Final council and peer review approved; cumulative R6 approved
the published runtime, and clean R7 closed its sole finding CR-007 after the focused
LF-preservation correction. CI passed on that exact corrected commit. Phase 3 is done.

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
retain the exact packs, decisions and receipts with their recorded hashes for audit
and repeat binding validation. Ignored artifacts are not durable tracked evidence.

Published cumulative review R6 approved the 45-path runtime change at `2877883` and
identified only CR-007, checkout conversion of the frozen baseline prompt to CRLF.
Commit `e30d2dc` pins that fixture alone to LF. Independent R7 approved a fresh Windows
checkout with `core.autocrlf=true`: index/worktree LF, 66 LF bytes, zero CR bytes and
the exact original hash; all 23 executions passed in 2.563 seconds, including the
formerly failing test and the full 22-test evaluator module. The checkout was clean.
The council peer retained its approval after inspecting the minimal attributes delta.

[Corrected-commit PR CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39428852968/attempts/1)
passed 782 tests in 24.858 seconds with two missing-Poppler PDF skips. The local full
suite passed all 782 with no skips. Earlier `2877883`
[push CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39427800350)
passed 782 with the same two skips; its
[first PR attempt](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39427805497/attempts/1)
stopped before tests when the MongoDB container exited, with cause unknown. The
[second attempt](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39427805497/attempts/2)
passed 782 with those two skips. No code defect is inferred from that startup failure.

The next action is reviewed finalizer publication of this documentation-only acceptance
increment and final PR handoff. Changed bindings or integrated code, finalizer refusal,
new review defects or CI failures require reassessment. Phases 4-6 remain deferred.

## Phase 4: candidate-independent document preparation

Tasks:

- [x] Configure the CV filename owner currently fixed in `jobintel/applications.py`.
- [x] Resolve candidate evidence and voice-source paths explicitly while preserving
  the current paths for the existing candidate and immutable source contents.
- [x] Separate personal career boundaries from general editorial requirements.
  Replace employer-specific branches in `jobintel/career_coverage.py` with reviewed,
  source-bound clarification handling; do not invent candidate chronology.
- [x] Update evidence validators, manifests and quality checks together. Keep
  candidate sources, artifacts and drafts bound to the correct context.
- [x] Update `AGENTS.md`, local skills, prompts and documentation consistently so
  candidate-specific instructions do not override another candidate's configuration.
  Run the required blind evaluation before editorial-policy changes.
- [x] Verify the current candidate retains approved career coverage and quality gates.
  Preparing real documents still requires explicit named-vacancy authorization,
  `prepare-preflight` and the required cover-letter skill.

Acceptance gate: preparation mechanics no longer depend on one person's name or
employer, with existing grounding and application-quality protections preserved.

Local implementation and review evidence: [preparation configuration](preparation-configuration.md).
The final full suite passed 815 tests in 81.647 seconds on Python 3.14.6 with a
disposable MongoDB 8 replica set and no skips. R1 and corrected R2 approved;
P4-001 through P4-006 are closed. Three final council views and anonymized peer
review accepted bounded draft publication after those local gates passed. The
final bound editorial assessment passed 10/10; its reused reviewer terminal had
prior conversation context, so this is not a memory-clean independent replication.
Published code
[`d8495d0`](https://github.com/ValentinNikolaev/job-intelligence/commit/d8495d0d64f1d49566a2cdc8cdf11ac547d1e2f6)
received independent cumulative R3 approval from a clean Windows checkout after
inspection of all 47 changed paths and 88 passing targeted executions without skips.
Two isolated negative controls reproduced the old alternate-policy and invented-month
defects; restored controls passed. Current chronology matches the baseline across
nine employers, with six permitted by the configured window. The copied editorial
pack and receipt exactly match fresh export/recomputation; this verifies bindings
without adding independent semantic corroboration.

[Push CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39442642289)
passed 815 tests in 29.397 seconds and
[PR CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39442699794)
passed 815 in 32.250 seconds, both on attempt 1. Each CI run skipped two real-PDF
checks because Poppler/pdfinfo was unavailable; the local full suite had no skips.
Phase 4 is done. No real application was generated in that iteration. PR 3 was
subsequently merged as `e87e8dd9dd973a963b058abe0a2827c66b6385cb`. Account selection
is implemented in phase 5 below; a second account remains phase 6 work.

## Phase 5: explicit account description, one live account

Implementation scope: introduce an enforced single-account contract while keeping
the supported existing layout. Descriptor references that consumers cannot honor
must fail closed, rather than silently fall back to their previous defaults.
Candidate/evidence settings remain owned by the preparation profile; integration
destinations remain owned by data-services configuration and environment. Do not
add a mutable process-wide active account or change match/preparation identities
merely because an account label is introduced. Unknown or conflicting selections
must fail before operational environment loading, timing, dispatch, locks or writes.
The [account contract and entrypoint inventory](account-context.md) records the
ownership boundaries, supported layout and explicit source/editorial limitations.

Tasks:

- [x] Add a small versioned account descriptor referencing the existing policy,
  profile, source configurations, data paths and integration destinations. Reuse
  configuration already extracted; avoid moving files merely to create a directory.
- [x] Introduce one resolver/context for these references and an explicit `--account`
  selector. Keep the existing account as the documented default.
- [x] Resolve account selection before dispatch, including separate handlers for
  `storage`, `sheets`, `applications`, `documents`, `evidence` and related commands.
- [x] Specify CLI/environment/config precedence and reject conflicting or unknown
  account selection before data access. Test store caches and credential scoping.
- [x] Check current scheduled prompts, GitHub Actions, catalog generation, exports,
  notifications, backups and repository finalization with the single live account.
- [x] Use isolated fixtures to exercise distinct contexts without onboarding a second
  live candidate. Retain current MongoDB connection, schema and current file paths.
- [x] Review the retained shared Zend-credential exclusion before onboarding another
  candidate; explicitly decide its ownership without weakening current candidate rules.
- [x] Resolve the deferred source-side Go/PHP/Italy relevance preferences listed in
  the rule inventory, or explicitly scope the supported source set, before claiming
  candidate-independent onboarding. Phases 0-3 leave those source decisions intact.

Acceptance gate: implicit default and explicit current-account runs are equivalent;
unknown accounts fail early. Only one live account is enabled.

Phase 5 is complete in [PR 4](https://github.com/ValentinNikolaev/job-intelligence/pull/4).
The final local full suite passed 900 tests in 284.203 seconds without skips on
Python 3.14.6/disposable MongoDB 8. R1, corrected R3, R4 and R5 approved their
increments; clean cumulative R6 approved all 53 published paths at
[`d66943b`](https://github.com/ValentinNikolaev/job-intelligence/commit/d66943b60107a196dc7a04f94429a6932aca058e).
P5-001 and P5-002 are closed on that clean Windows checkout with explicit negative
controls. R6 independently passed 117 tests in 32.709 seconds and 69 in 14.980
seconds, no skips; actual junction and root-alias checks also passed.

[Runtime push CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39467930438)
passed 900 tests in 47.868 seconds on attempt 1.
[Runtime PR CI](https://github.com/ValentinNikolaev/job-intelligence/actions/runs/39467937515/attempts/2)
passed 900 in 54.188 seconds on attempt 2; attempt 1 stopped before tests when the
test MongoDB container exited, with cause unknown. Each successful CI run skipped
two real-PDF checks because Poppler/pdfinfo was unavailable; the local suite had no
skips. All required MongoDB, test and cleanup steps actually ran. The PR job checked
a synthetic merge of the reviewed head into main `629e9597`.

Final council specialists and anonymized peer review accepted bounded publication
subject to the integrated checks, complete staged inspection, clean published review
and exact-head CI; these gates passed. Their convergence is not independent proof,
and sampled boundary coverage does not establish concurrent tenancy or deployed
Scheduled Task behavior. Agent review records are posted by the author account,
not separate GitHub-user approvals. The existing source bundle and Zend exclusion
remain explicitly scoped to the sole current account. No second candidate, production
operation, application generation, canonical record/artifact rewrite or MongoDB
migration occurred. The PR stays open and unmerged for handoff.

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
| 2026-10-20 | Published-checkout review R6 identified CR-007: `core.autocrlf=true` converts the frozen baseline prompt fixture to CRLF, breaking its exact original-byte/hash regression. Added one root `.gitattributes` rule setting only `/tests/fixtures/match-policy-baseline-prompt.md` to `text eol=lf`; fixture content and the byte assertion remain unchanged. | `python -m unittest tests.test_match_policy_eval -v` passed all 22 tests in 2.360 seconds. Git's checkout filter with `core.autocrlf=true` now preserves LF and original SHA-256 `98f9d0657557afc0a256b0a2a9140300738d2e38d1cec59ca40bc167acc5cb47`. Diff checks passed. No runtime, configuration, prompt, schema or evaluation-input changes. Phase 3 remains in progress pending publication of this correction, independent corrected R6 review and exact-published-SHA CI. |
| 2026-10-20 | Accepted phase 3 and marked phases 0-3 complete. Published runtime `2877883f74eaec8583135c11cab1dee4002cbc95` received cumulative R6 approval apart from CR-007. Published LF correction `e30d2dc2941ed79ee87239e2ee7260498151e611` received independent clean R7 approval and closed CR-007: fresh Windows `core.autocrlf=true` checkout, index/worktree LF, 66 LF/zero CR, exact original hash, 23 passing executions in 2.563 seconds and clean state. Council peer retained approval. | Exact corrected-commit PR CI run 39428852968 attempt 1 passed 782 tests in 24.858 seconds, two missing-Poppler PDF skips; prior runtime push CI passed likewise. Prior runtime PR attempt 1 stopped before tests on MongoDB container exit of unknown cause; attempt 2 passed. Local full suite remains 782 passing/no skips in 127.566 seconds. Durable PR/CI links and history are recorded in the final synthesis. This acceptance increment changes documentation only; runtime tests were not rerun. Phases 4-6 remain deferred; reviewed finalizer publication of acceptance docs and final PR handoff are next. |
| 2026-10-20 | Started phase 4 on new managed branch `ValentinNikolaev/multiaccount-p4` from merged main `83d812e29fdfbbc1aa942def52011fe5a6bab2d3`. Architecture and risk review selected one preparation context in existing application-profile configuration, separate from unchanged analysis identity; no account selector or database migration. | Pre-change Python 3.14.6 full suite passed 782 tests in 137.795 seconds with disposable MongoDB 8 and no skips. No candidate sources, packages, vacancy statuses, notifications or catalog inputs changed. Phase 4 is in progress; phases 5-6 remain deferred. |
| 2026-10-20 | Pre-change blind editorial assessment returned 9/10: `team-result` mixed Senior CV selection with attribution grounding. The reviewer retained a defensible omission on adjudication. Independent technical review approved only its kind/requirement clarification to statement-level grounding, preserving source, claim and expected disposition. | Original decisions SHA-256 `6bb65feae472f9ee38c07e836268349d5e72fad17de7c93182005582c6cc81bb`, original corpus `569ee2c6f5b55b9c8fa3e06030e239e11a26d52b0bff4627fc3bcd87a15e1ecc`; the original failed receipt remains failed evidence. Clarified corpus `94f7fff8a3735f82dd5f343a2e7014273228c998968589cbd16e83e33e287457` received a fresh blind pass. Its initial 9/10 reassigned a metric to an unrelated achievement; source/requirement adjudication corrected that reviewer error without changing the corpus. Final clarified baseline passed 10/10, decisions `c0abe93bab6dcef70047a1e9a42912ccfcc1fcb58fb79a6d426cf7c84c28a84d`, unchanged pre-extraction policy `222e61ce3544f70f9ef2b463c9b4c911ed5ac19cee11e39878e27d109e8665cd`. This bounded check preceded generic editorial-policy edits; it does not prove general ranking or hiring effectiveness. |
| 2026-10-20 | Implemented preparation configuration/context, configured filenames/sources/banks/voice, generic evidence-bound career corrections, quality/manifest/per-document identities and CLI/preflight/lifecycle integration. Updated generic prompts and source/distributed manual instructions. Early subset review R1 closed P4-001 after independently checking preservation of source-backed rendering limits; evaluator/finalizer dependencies now bind the effective preparation contract without exporting contact answers. | Core focused suite passed 126 tests; integration passed 85 focused tests plus 54 real-MongoDB matching/storage/snapshot tests, no skips. R1 independently passed 14 evaluator/finalizer tests and verified exact clarification quotes/hashes. Full working-tree run had 806 tests and 12 failures; diagnosis traced shared deleted-temp paths to an unrestored test-fixture patch, under correction. Independent core R2 also identified stale/foreign supplied contexts (P4-002), raw-client receipt stamping (P4-003), and invented-month acceptance after year-only clarification (P4-004); fixes and independent re-review remain required. Phase 4 is not accepted yet. |
| 2026-10-20 | Independent final blind editorial assessment in an Orca Codex session passed all ten cases without evaluator/answer-key access. Coordinator reviewed every reason and exact source anchoring. Initial baseline disagreements and adjudications above remain separate evidence. | Actual model/effort `gpt-6.1-sol` / `high` confirmed by runtime launch receipt and terminal. Corpus SHA-256 `94f7fff8a3735f82dd5f343a2e7014273228c998968589cbd16e83e33e287457`, final policy `c918b61a9734193faf845e0b8e2163c4674bf011d2f032f24ccdf8da6fc99992`, decisions `85661386d1ad26161004b33897504bd7cd5b5a5cbd913a49a5db04ccdeebe88c`. This is one bounded synthetic reviewer, not independent evidence of hiring results. Full runtime acceptance remains pending R2 corrections and release verification. |
| 2026-10-20 | Diagnosed the 12 full-suite CLI failures as test isolation: three manually composed application fixtures skipped `doCleanups()`, leaving `cli.__file__` at a deleted temporary project. Registered their cleanups and added a module-root restoration regression; production configuration remains strict. | All 52 tests in the affected ordered group passed, including all 12 earlier failures. Suppressing cleanup reproduced one expected regression failure; restored control passed. API-prohibition test/search passed. R2 P4-002/003/004/005 remain open until corrected core tests and independent re-review pass; phase 4 remains in progress. |
| 2026-10-20 | Corrected core review R2 approved and closed P4-002 through P4-005 after independent positive/negative reproductions: authoritative fresh project contexts, foreign registry rejection, raw-client rejection/default and honest legacy-only compatibility, source date precision, mandatory cache receipts and tamper detection. Direct lint now rejects foreign/stale contexts before reads. A database-only raw-client fixture explicitly tests legacy behavior instead of expecting current schema-3 provenance. | R2 independently ran ten focused regressions plus original counterexamples; integration owner ran 57 focused tests with actual disposable MongoDB, no skips. A preceding 812-test run had one error in that legacy fixture before its adaptation; this was not treated as a pass. Final post-correction `python -m unittest discover -v` passed 814 tests in 81.118 seconds with no skips. API-prohibition unit/search, all 66 local links and diff checks passed. No source, vacancy, artifact, status or catalog-input changes. |
| 2026-10-20 | Final council (three separate architecture/risk/execution views and anonymized peer review) accepted bounded draft publication after the full suite and independent R2 closure. The remaining two-fixed-voice-file documentation paragraph was corrected to the configured nonempty list; a complete current-pack semantic reassessment passed 10/10 and coordinator inspected every reason. | Final policy SHA-256 `b912be8bca0b344eb9b283a8262af03766ea494dae5396ff8006c980bbfce3e0`, corpus `94f7fff8a3735f82dd5f343a2e7014273228c998968589cbd16e83e33e287457`, decisions `f63e65fb54a4050628f5b1c0c355412709070fe090728eac4e1eaf514a893217`. The same independent reviewer retained prior conversation context but read only the new pack during reassessment, so this is not a memory-clean replication. Council test counts overlap and are not additive confidence; source semantics remain a reviewed trust boundary. Phase 4 remains in progress pending finalizer publication, clean published-commit review and exact-SHA CI; phases 5-6 stay deferred. |
| 2026-10-20 | Complete staged-diff inspection found P4-006: CV grounding hashed the bound project policy but still read editorial rules from the module checkout. Passed the explicit context policy path to validation and added an alternate-project anti-pattern regression with complete synthetic policy fixtures. Independent R2 reproduced the original bypass and verified rejection under the bound policy, default/restored passing controls and the expected old-fallback mutation failure. | Owner's 100 focused tests passed; each of the three final council advisors separately inspected the minimal three-file correction and passed its regression. Exact post-correction full suite passed 815 tests in 81.647 seconds, no skips, with disposable MongoDB 8/Python 3.14.6. Current 10/10 semantic receipt revalidated unchanged policy/input hashes; API-prohibition and diff checks passed. All P4-001 through P4-006 findings are closed. Only reviewed publication, clean published review and exact-SHA CI remain before phase-4 completion. |
| 2026-10-20 | Accepted phase 4 after publication of `d8495d0d64f1d49566a2cdc8cdf11ac547d1e2f6` in PR 3. Fresh independent cumulative review R3 approved all 47 changed paths in a clean Windows checkout, supported closure of P4-001 through P4-006 and found no new confirmed P1/P2. Marked phase 4 done; phases 5-6 remain unstarted. | R3 observed 88 passing targeted executions without skips and two expected in-memory negative-control failures with restored passing controls. All nine employer chronologies equal the baseline; six remain within the configured scope. Fresh export/receipt recomputation preserves the recorded 10/10 bindings without independent semantic corroboration. Exact-head push CI 39442642289 and PR CI 39442699794 passed on attempt 1: 815 tests in 29.397/32.250 seconds, each with two missing-Poppler PDF skips. The final local full suite passed 815 in 81.647 seconds without skips. This acceptance increment changes documentation only and requires its own diff/link review and publication; no runtime suite repeat is claimed. Main, candidate sources, applications, statuses, catalog inputs and MongoDB contracts remain unchanged by this iteration. |
| 2026-10-20 | Started phase 5 from merged phase-4 main `e87e8dd9dd973a963b058abe0a2827c66b6385cb` in new managed branch `ValentinNikolaev/multiaccount-p5`. Three independent architecture/risk/execution advisors inspected actual entrypoints; anonymized peer review is underway before implementation. The bounded design pins unsupported layout references and preserves the existing one-account resources. | Pre-change `python -m unittest discover -v` on Python 3.14.6 with a disposable MongoDB 8 replica set passed 815 tests in 227.222 seconds, no skips. Identified boundaries include pre-dispatch timing, subsidiary CLIs, direct archive/notification/restore scripts, current-directory Sheets routing, environment leakage and destination-scoped store caches. Implementation and acceptance remain pending; no production operations, candidate/artifact/status/catalog changes or phase-6 onboarding. |
| 2026-10-20 | Preimplementation Quick council completed three independent first-principles/contrarian/execution passes and anonymized Orca-session peer review. Coordinator accepted bounded implementation with concerns converted to explicit gates: one `current` account, pinned unsupported references, operation-local credentials, coherent roots, pre-effect selection and a reviewed entrypoint inventory. | Convergence is not independent proof. The weakest point is distributed resource/root reconstruction, so acceptance requires actual early-rejection, cross-root/destination/credential tests and default/freshness parity. Descriptor/path-metadata reads and runtime dependency bootstrap may precede validation; operational reads/writes may not. CLI/process-environment disagreement rejects, dotenv cannot select an account. Existing source relevance and Zend exclusion remain scoped to the sole current account; broader onboarding stays deferred. No new runtime verification is claimed at this decision checkpoint. |
| 2026-10-20 | Completed the dormant phase-5 contract increment: strict `config/accounts.yaml`, immutable `jobintel/accounts.py` context/resolver, safe selector extraction, freshness checks and read-only module gate; explicit descriptor-only fixtures and 33 focused tests. Added the account ownership/entrypoint guide. R1 independently approved the complete six-file delta; existing runtime consumers are still unchanged. | Owner's 33 tests passed in 1.602 seconds; independent R1 passed 33 in 1.574 seconds, no skips. R1 additionally verified real Windows internal/external config and registry junction rejection and root-alias parity; removing containment produced nine expected assertions across two tests, restored controls passed. Coordinator's final contract full suite passed 848 tests in 164.792 seconds on Python 3.14.6/disposable MongoDB 8, no skips. Runtime account wiring, operation-local credentials/cache isolation, scripts/Actions and final phase acceptance remain pending. No production, candidate/artifact/status/catalog or storage-contract changes. |
| 2026-10-20 | Published the contract as `33b004064961c7d02fa40bc9a601c892c5d2d87d` in [PR 4](https://github.com/ValentinNikolaev/job-intelligence/pull/4). The reviewed finalizer safely integrated concurrent main `629e95970333e4cc107d7f56727aa06c391eae4d`; its unrelated Qonto match record retained blob `a61e612058c3b35f8dc2d6a92df1e1e8ee42148c`. Clean Windows R2 requested P5-001: an LF-only duplicate-key test mutation became a no-op with checkout CRLF. | R2 observed 33 focused tests with one failure in 1.689 seconds, no skips; correctly duplicated CRLF YAML was rejected, and normalizing only the synthetic input restored the failing test. The owner replaced the brittle construction and added explicit LF/CRLF mutation assertions: 34 focused tests pass in 1.142 seconds, no skips; independent closure remains pending. Push CI 39463783940 attempt 1 passed 848 in 25.667 seconds with two missing-Poppler skips. PR CI 39463820636 attempt 1 stopped before tests on MongoDB container startup exit of unknown cause; same-commit attempt 2 passed. Runtime integration and final acceptance remain in progress. |
| 2026-10-20 | Completed the phase-5 operational wiring across the main CLI, subsidiary CLIs, storage/workflow boundaries, archive/notification/isolated-restore scripts and seven operational Actions. Selection is resolved before effects; operation-local credentials preserve default dotenv → explicit dotenv → process precedence without mutating process environment. Canonical roots, delivery paths and destination-scoped store caches are enforced. The guide classifies shared repository/infrastructure utilities, pure explicit-input helpers and current-account source/Zend restrictions; no second account or alternate layout is enabled. | Independent R3 approved the script subset after 95 passing focused tests in 18.034 seconds and closed P5-001 locally, including LF/CRLF negative controls. Independent R4 approved central wiring after 62 tests in 23.081 seconds and 29 in 16.393 seconds, including real disposable MongoDB checks; old behavior reproduced P5-002 (partial explicit dotenv lost default URI/database), restored precedence passed. R5 approved leaf entrypoints after 132 tests in 15.505 seconds, 12 conflict probes, actual foreign-cwd module runs and junction rejection. These counts overlap and are not additive confidence. Published-checkout closure and exact-head runtime CI remain pending. |
| 2026-10-20 | The first integrated runtime suite ran 900 tests in 170.881 seconds and failed five collection-safety cases: their mocked CLI invocation still supplied noncanonical source/registry roots and was correctly rejected before the tested collector. Updated only the fixture invocation to the selected root's sources/registry, preserving all original status, storage, usage and call-order assertions. | The owner then passed 45 focused tests in 5.984 seconds; independent R4 re-review passed all 10 collection-safety tests in 0.432 seconds and confirmed the collectors actually execute. The corrected complete suite is in progress; the failed run is not a passing gate. Three final council specialists found no runtime must-fix and conditionally accepted the bounded architecture pending integrated checks, anonymized peer review, complete staged inspection, publication, clean cumulative review and exact-head CI. The backup prompt received only a mechanical correction describing its explicit isolated-store seam; application/editorial policies and match identities are unchanged. |
| 2026-10-20 | Corrected integrated verification completed: `python -m unittest discover -v` passed 900 tests in 284.203 seconds on Python 3.14.6 with a disposable MongoDB 8 replica set, no skips. The final project code/configuration API-prohibition search found no prohibited integrations; local links and diff checks passed. | Runtime implementation checklist items are complete, including explicit current-account source/Zend ownership limits. Phase 5 stays in progress until final council synthesis, complete staged inspection, reviewed publication, clean cumulative published-code review and exact-head CI. Canonical catalog inputs did not change, so catalog regeneration is not required. |
| 2026-10-20 | Final Quick council and anonymized Orca-session peer review conditionally accepted reviewed publication of the frozen single-current-account runtime. Three specialists converged on bounded authority/configuration ownership without a new concrete must-fix; the peer independently observed 17 distinct focused tests, reproduced the five old-fixture failures in memory, restored all 10 collection-safety passes and confirmed the corrected full-suite log. Complete 52-path staged runtime diff inspection followed; no unrelated records, credentials or artifacts are staged. | The strongest argument examines the caller-trusted explicit-store seam and the actual guarded restore caller. The weakest accepted point is future operational callers bypassing account guards when using account-independent primitives; ContextVar scoping does not establish concurrent tenancy. The receipt field `source_files_mutated: false` is an assertion supported by inspected control flow/tests, not independent before/after forensic measurement. Convergence and overlapping counts are not additional proof. Reproduced pre-gate effects, destination drift or substantive published-tree differences require reassessment. Clean published cumulative review and exact-head CI remain mandatory before phase acceptance; deployed Scheduled Task settings have not been inspected or changed. |
| 2026-10-20 | Accepted phase 5 after independent clean cumulative R6 approved the complete 53-path published delta at `d66943b60107a196dc7a04f94429a6932aca058e`. P5-001 and P5-002 are closed on the actual CRLF Windows checkout; no new confirmed P1/P2 or material missing test. Marked phase 5 Done; phase 6 remains Not started. | R6 passed 117 tests in 32.709 seconds and 69 in 14.980 seconds, no skips; four real configuration/registry junction redirections rejected and root-alias parity passed in 0.586 seconds. In-memory old-behavior negatives reproduced both reviewed defects and restored controls passed in 1.431 seconds. Unrelated Qonto match blob and empty registry diff verified. Exact-head push CI 39467930438 attempt 1 and PR CI 39467937515 attempt 2 passed 900 tests in 47.868/54.188 seconds, each with two missing-Poppler PDF skips; the local complete suite passed all 900 without skips. PR attempt 1 stopped before tests on Mongo container exit of unknown cause; it is retained as failed evidence. Final council release conditions are satisfied for the bounded runtime; this acceptance increment changes documentation only and requires its own review/publication and final-head CI before PR handoff. No runtime full-suite repeat is claimed. |
