# Selection-rule inventory and behavioral baseline

Recorded 2026-10-20 for [migration phases 0-3](multiaccount-migration-plan.md).
This inventory describes existing behavior. It does not authorize collection,
reclassification, preparation, historical rewrites or a second account. Candidate
source records and secrets were not used to construct the synthetic baseline.

## Common deterministic selection

The current operational implementation is [prefilter.py](../jobintel/prefilter.py).
The dormant [selection-policy.yaml](../config/selection-policy.yaml) reproduces its
personal decisions. Normalization, timestamp parsing, word boundaries, language
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

[triage.py](../jobintel/triage.py) currently applies ordered categories `sales`, `qa`,
`mobile`, `junior`, `sre`, `consulting`, `non_backend`. These are personal exclusions;
category patterns are recognition mechanics. A title match means high confidence and
`skip_model: true`; body-only recognition means medium confidence and no skip; no
recognition means low confidence. Title matches outrank body matches. The returned
reason is the first matching category in rule order, and all matching title categories
retain that order. Only the first 12,000 body characters are inspected. The selected
categories belong to `selection-policy.yaml:triage_exclusions`.

All these consumers must be considered together during phase 2:

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

`triage_version` currently equals `deterministic-triage-v1`, but readers do not
validate it or the title/body that produced the receipt. Phase 2 must define the exact
legacy-equivalent bridge and recompute stale decisions read-only, or explicitly
require refresh. No receipt or original historical judgment may be relabeled.

## Existing source-side and deferred policy owners

Source filters run before the common prefilter. They are intentionally not a second
copy of the new common selection policy: provider queries and source relevance
continue to live under their existing owners in this iteration.

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

The existing editorial export/finalizer policy bindings do not include the match
prompt. Phase 3 needs the mandatory independent blind editorial pass plus scoring
evidence bound to the changed match prompt and policy snapshot. Editorial fixture unit
tests are not that pass and do not prove scoring behavior. Match freshness must agree
between individual analysis, sealed packs, snapshots and preparation preflight.

## Dormant schema and versioning contract

[selection_policy.py](../jobintel/selection_policy.py) exposes
`load_selection_policy(path) -> SelectionPolicy` with frozen dataclasses and tuple
collections. All fields are required. There are no code defaults, environment
overrides, inherited layers or implicit list additions. The caller supplies the exact
path; the planned command boundary resolves it as `project_root/config/selection-policy.yaml`.
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
stored decision is current. Phase 2 must additionally handle recognizer version and
current vacancy content. Changing age/language/stack policy cannot change the triage
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
coordinator's next step.
