# Phased migration to account-specific configuration

Created: 2026-10-20. Last updated: 2026-10-20.

## Goal and current scope

Make personal selection rules and candidate-specific behavior configurable while
keeping the current system operational after every phase. Connect a second account
only in the final phase.

An account represents one candidate, their preferences, evidence, application
history and integration destinations. Multiple search profiles for the same
candidate do not require separate accounts.

The next implementation iteration covers **phases 0-2 only**. It extracts existing
deterministic rules into configuration without changing their meaning. This document
records the agreed sequence; it does not authorize starting every later phase or
operating a second account.

## Progress and maintenance

Planning is complete; implementation has not started. Repository inspection used to
prepare this plan is not completion of the baseline or verification gates below.

| Phase | Deliverable | Depends on | Status |
| --- | --- | --- | --- |
| 0 | Inventory and behavioral baseline | None | Not started; next |
| 1 | Validated configuration for existing selection rules | 0 | Not started |
| 2 | Configuration-driven prefilter and triage | 1 | Not started |
| 3 | Configurable match-analysis preferences | 2 | Not started |
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

- [ ] Inventory personal rules in `jobintel/`, `sources/`, `config/`, `prompts/`,
  `.agents/skills/`, scripts and GitHub Actions. Record location, current value,
  consumer, precedence and intended configuration owner in this document or a linked
  inventory. Identify duplicated or contradictory rules without changing them.
- [ ] Separate personal decisions from shared mechanics: recognizing a mandatory
  language requirement is shared; deciding whether that language blocks a candidate
  belongs to the candidate's policy.
- [ ] Build on `tests/test_prefilter.py`, `tests/test_triage.py` and collection/queue
  tests to capture representative accepted, rejected and ambiguous vacancies.
  Freeze the reference time for age-dependent cases.
- [ ] Capture current decisions, rejection categories, explanations, rule precedence
  and relevant queue behavior. Include optional versus mandatory languages, mixed
  stacks, European exceptions to American-hours restrictions and title/body triage.
- [ ] Record baseline checks and any pre-existing failures separately from migration
  failures. Use fixtures or read-only snapshots; do not probe production with writes.

Acceptance gate: the inventory identifies the consumers that must change together,
and durable tests can expose behavior drift during extraction.

## Phase 1: validated configuration, without runtime cutover

Tasks:

- [ ] Add the proposed `config/selection-policy.yaml` with a versioned schema that
  reproduces the current rules. This path is proposed, not an existing interface.
- [ ] Cover maximum vacancy age, excluded roles, target technologies, excluded
  technologies and combinations, remote requirements, blocking mandatory languages,
  existing location/timezone decisions and triage exclusions.
- [ ] Keep company retry rules in `config/application-profile.yaml` for this iteration.
  Do not create another authoritative copy. Keep already configurable source queries
  in `sources/*/config.yaml` and workflow settings in `config/codex-workflows.yaml`.
- [ ] Add a typed loader with strict field/type/version validation. Reject unknown
  fields and contradictory settings; document defaults, path resolution and ordering.
- [ ] Define explicit list semantics. Avoid implicit concatenation or layered
  inheritance in this iteration. Configuration must not contain executable code.
- [ ] Test valid configuration and failures for missing required settings, malformed
  YAML, unsupported versions and unsupported rule values. Diagnostics identify the
  file and field without exposing secrets.
- [ ] Leave the operational flow on the existing implementation until phase 2.
  Do not expose unsupported allowlist or other future capabilities as working fields.

Acceptance gate: the file describes the existing behavior completely, validates
deterministically, and does not yet alter production decisions.

## Phase 2: configuration-driven deterministic selection

Tasks:

- [ ] Load and validate the policy once at each relevant command boundary, before
  collection requests or mutations. Pass it explicitly to consumers; avoid hidden
  mutable process-wide settings. A required invalid policy fails closed.
- [ ] Switch `jobintel/prefilter.py` and collection callers in `jobintel/cli.py` to the
  typed policy. Retain normalization, text recognition, precedence and explanations.
- [ ] Switch `jobintel/triage.py` and its CLI, pending-queue and `workflow_api.py`
  consumers together. Test both path-based and MongoDB snapshot-based queue paths.
- [ ] Define triage freshness using the existing `triage_version` field, without a
  MongoDB schema change. An unchanged legacy-equivalent policy may reuse legacy
  decisions; changed relevant rules must trigger recomputation or an explicit
  refresh requirement, never silently reuse an incompatible skip decision.
- [ ] Compare old and new results on the phase-0 corpus without writing production
  records. Compare decisions, categories, reasons and queue behavior, not just totals.
- [ ] Add meaningful tests showing that changing one supported configuration value
  changes its intended decision, while unrelated settings preserve other decisions.
- [ ] Verify existing commands and automation entrypoints still work with their
  existing arguments. Remove obsolete personal decision constants only after all
  consumers have switched; shared recognition dictionaries may remain code.
- [ ] Run the release checks below and record the resulting evidence and limitations.

Acceptance gate: baseline decisions are equivalent, configuration changes are
effective, stale triage cannot bypass updated rules, and no storage migration or
historical record rewrite is needed. Phases 0-2 form a standalone release.

Recovery: revert the extraction/configuration change if its release gate fails.
No database rollback should be necessary for extraction alone. Any records written
by normal operation remain real history and must not be discarded.

## Phase 3: configurable analysis preferences

Tasks:

- [ ] Extract candidate-specific scoring preferences from `prompts/vacancy-match.md`:
  technology and role preferences, Rome, relocation, support/email domains and
  timezone compatibility. Preserve the distinction between preferences and blockers.
- [ ] Supply a deterministic, versioned policy snapshot to individual and sealed-batch
  analysis. Keep semantic evaluation inside Codex and source text as data.
- [ ] Run the required [blind editorial evaluation](../prompts/editorial-evaluation.md)
  before changing application prompts or editorial policy; record its evidence.
- [ ] Bind match freshness to the relevant effective inputs using the existing
  versioning contract where possible. Changing notification settings must not stale
  a match; changing scoring preferences must be detected.
- [ ] Define compatibility for existing matches explicitly. Preserve original model,
  score, prompt/profile provenance and legacy receipts; never relabel old judgments.
- [ ] Test analysis and preparation-preflight freshness consistently. Avoid automatic
  mass reanalysis and distinguish input-version changes from semantic policy changes.

Acceptance gate: personal analysis preferences come from configuration, changed
inputs invalidate the right results, and evaluation supports the intended behavior.

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
