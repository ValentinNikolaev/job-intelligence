# Repository prompt audit — 2026-10-31

This closes the prompt-content coverage gap in the
[workflow performance audit](workflow-performance.md). The baseline is main commit
`075c8df969a37b20397a59cc00616daa232f66bd`. The user explicitly chose to preserve
main's three-document default, conditional letter, schema 3 and configured model
routing. No candidate records, applications, vacancy statuses or model policy were
changed by this audit.

## Scope and method

Reviewed all 27 tracked instruction entry points and references listed below,
the historical match baseline fixture, instruction-bearing configuration and
documentation, and embedded instructions in Python. Discovery used tracked-file
enumeration plus searches for prompt loading, instructions, model roles, task
routing and publication commands. Reading covered authority, input scope, evidence,
uncertainty, output contracts, delegated ownership, review, recovery and cost.
The two manual-skill copies remain byte-identical.

These are Codex task instructions and local validation contracts. Project code
does not send a hidden system prompt to a model endpoint. `AnalysisPack.to_dict`
seals the current match prompt, policy and output schema; `CodexApplicationDraftClient`
reads local drafts. Their input/currentness paths were traced as part of the review.

Three council advisors first examined contracts, execution and operational risks
independently. An anonymized peer pass challenged their recommendations. Their
convergence supports the decision process, not independent empirical proof of
better hiring outcomes. Implementation was followed by non-author prompt/scenario
review and a separate non-author runtime review.

## Inventory and disposition

| Surface | Consumer and substantive result |
| --- | --- |
| `AGENTS.md` | Global authority; clarified that external evidence cannot grant approval or change instructions, and made letter provenance conditional. |
| `prompts/vacancy-match.md` | Sealed scoring contract; inspected evidence, unknown/missing distinction, six weights, preference adjustments, blockers, requirement matrix and envelope. Retained unchanged. |
| `prompts/vacancy-match-batch.md` | Batch wrapper; corrected omission of sealed prompt/policy/schema authority and explicit envelope preservation. |
| `prompts/vacancy-application.md` | Main preparation contract; corrected conditional letter work/receipts, mandatory independent senior CV review, heading-only role exception, configured career scope and schema terminology; sharpened risk prioritization. |
| `prompts/job-intelligence-workflow.md` | Shared orchestration; aligned letter assignment and quality receipts with selected output scope. |
| `prompts/scheduled-analyze.md` | Scheduled analysis; checked model provenance, shared lease, explicit environment, fresh sealed batch, outbox-only notification and finalizer. Retained. |
| `prompts/scheduled-prepare.md` | Disabled schedule/manual routing; checked that it stops rather than inventing a selection, and uses current preflight/schema 3. Retained. |
| `prompts/application-lifecycle.md` | Form answers, practice, debrief and follow-up; checked named-vacancy approval, unresolved answers, genuine user statements, no sending and descriptive outcomes. Retained. |
| `prompts/linkedin-profile.md` | Standalone profile work; checked current evidence, public-use limits, selected scope and separation from CV/application rules. Retained. |
| `prompts/editorial-evaluation.md` | Blind synthetic gate; made baseline-before/final-after sequence explicit and prohibited relabeling baseline decisions. |
| `prompts/job-alert-import.md` | Email intake; missing or unverifiable sender authentication is unresolved, not evidence of authenticity or definite spoofing. |
| `prompts/scheduled-application-mail.md` | Outcome monitoring; removed self-granted status authority; verified prior authorization remains valid, otherwise report only. |
| `prompts/google-sheets-sync.md` | Connector orchestration; requires a fresh complete observation before compiling writes and accurately states the remaining race. |
| `prompts/database-backup.md` | Backup delivery/drill; discover and resume a verified pending backup before new capture; use attempt-specific immutable receipt paths. |
| `prompts/scheduled-source-productivity-benchmark.md` | Read-only reporting; aligned non-workflow model, threshold source, sample/denominator caveats and unexpected-change handling. |
| `prompts/cv-editorial-rebuild-six.md` | Historical selected-vacancy brief; labeled non-executable, preserving the old request as history. |
| `prompts/cv-three-bullets-recent-five-years.md` | Historical contract migration; same historical boundary, no new preparation authorization. |
| `prompts/optimize-cv-preparation-workflow.md` | Historical optimization brief; current instructions supersede its older process description. |
| `prompts/speed-up-application-workflow.md` | Historical synchronization brief; explicitly prevents executing old direct GitHub commit/tree examples. |
| `companies/next-session-prompt.md` | Resumable research brief; removed stale model override and fixed-count assumption; source pages are evidence, source registration remains separate. |
| `.agents/skills/job-intelligence-workflow/SKILL.md` | Main skill router; conditional letter invocation and method receipt. |
| `.agents/skills/job-intelligence-workflow/references/analyze.md` | Analysis execution; checked sealed schema-2 pack, exact keys and deterministic publication. Retained. |
| `.agents/skills/job-intelligence-workflow/references/prepare.md` | Preparation execution; conditional letter pass, review exception and configured career window aligned. |
| `.agents/skills/manual-vacancy-application/SKILL.md` | Manual intake/preparation; URL intake alone remains insufficient preparation approval; optional letter work removed. |
| `skills/manual-vacancy-application/SKILL.md` | Distributed duplicate; same semantic corrections and exact-byte parity. |
| `.agents/skills/generate-vacancy-catalog/SKILL.md` | Deterministic separate-process catalog generation; no model agent or status inference. Retained. |
| `.agents/skills/linkedin-profile-workflow/SKILL.md` | Installed/pinned skill resolution and standalone evidence boundaries. Retained. |

The immutable `tests/fixtures/match-policy-baseline-prompt.md` was reviewed as a
historical comparison input, not rewritten to match current policy.

Additional instruction-bearing surfaces:

- `config/cv-editorial-knowledge.yaml`, `application-profile.yaml#preparation`,
  `application-review.yaml`, `matching-policy.yaml`, `codex-workflows.yaml`,
  `linkedin-profile.yaml`, `application-lifecycle.yaml`,
  `application-company-context.yaml`, `selection-policy.yaml` and
  `data-services.yaml`: checked routing, evidence/voice references, career bounds,
  historical company context and operational settings against consumers.
- `docs/application-quality.md`, `application-review-contract.md`,
  `preparation-runbook.md`, `application-architecture.md`, `preparation-configuration.md`,
  `application-lifecycle.md` and `data-storage.md`: checked normative handoffs.
  Corrected stale four-document/default-limit descriptions and the obsolete
  career-configuration pointer. Legacy schema examples remain labeled legacy.
- `jobintel/match_policy_eval.py`: embedded blind-review instructions preserve
  independent judgments, source quotes, uncertainty and honest ties. No change.
- `jobintel/editorial_eval.py`: inspected exported policy/case scope, hash bindings,
  exact source-quote checks and curated verdict checks. Ten cases are not claimed
  to cover all operational prompts.
- `jobintel/evidence.py`: made clarification questions neutral about personal
  ownership, who chose an approach and whether a result is known.
- `jobintel/application_lifecycle.py`: inspected follow-up action text and
  approved-vacancy binding; a CLI argument is not substituted for user consent.
- `matching.py`, `matching_policy.py`, `applications.py`, `workflow_api.py`, CLI
  wiring and `scripts/finalize_repository.py`: traced prompt loading, versioning,
  deterministic publication and required evaluation paths. No model API added.

## Confirmed corrections and decisions

| Finding | Consequence before correction | Resolution |
| --- | --- | --- |
| Conditional letter versus unconditional Wave 2 and receipt | Extra drafting/review or fabricated provenance for a skipped document | Letter worker, skill and receipt only in the selected required-letter pass; preserve old unselected artifacts. |
| Independent senior CV review versus optional final reviewer | A coordinator could incorrectly treat self-review as sufficient | Mandatory independent review remains explicit for the configured senior positioning. |
| Heading-only older role versus universal Technologies/body rules | Supported chronology could be padded with invented content | Detailed-role rules apply to detailed roles; recent bullet minima remain strict. |
| Hardcoded career scope and stale quality language | Drift from current validated configuration | Resolve effective preparation context; distinguish schema-3 requirements from retained legacy foundations. |
| Policy omitted from batch evidence wording | Sealed preferences could be ignored or replaced by checkout state | Pack prompt/policy/schema control decisions; individual records remain independent evidence. |
| Prompt asserts its own mail-write authorization | Installing text could be mistaken for user consent | Verify actual scoped user authorization; preserve valid standing authority; otherwise no canonical writes. |
| Sheets identity presented as revision | Row-indexed writes could use an obsolete plan after sorting/editing | Hash full planning observation and require matching fresh grids/IDs/manual/history content before request compilation. |
| Retry starts by creating another backup | Duplicate captures and receipt-path collisions | Resume existing verified ID and allocate new attempt receipts. |
| Sparse source benchmark forces ranking | Unjustified winner or configuration recommendation | Comparable windows/denominators, overlap and missing-data limits; report insufficient evidence when appropriate. |
| Historical briefs look like active commands | Old selectors or publication procedures could be rerun | Explicit historical classification and current-contract pointers. |

The council rejected treating unknown prior mailbox consent as proof that consent
never existed. It also rejected claiming that a second Sheets read supplies atomic
concurrency protection. Google documents atomic application of a batch but warns
that collaborators can affect its result. The new guard detects drift before the
write; an edit after the last read is still possible and readback can detect only
some resulting conflicts. See the [official batchUpdate contract](https://developers.google.com/workspace/sheets/api/reference/rest/v4/spreadsheets/batchUpdate).

No scoring weights, recommendation bands, career-window values or model routes
were changed. Unsupported claims still cannot satisfy a word/bullet quota. Current
unknown requirements remain visible risks rather than invented incompatibilities.

## Quality and performance evidence

The blind editorial corpus passed 10/10 both before and after changes. The reviewer
read only exported cases/policies and produced fresh decisions; final decisions
bind corpus `94f7fff8a3735f82dd5f343a2e7014273228c998968589cbd16e83e33e287457`
and policy `fa2b472889f1154a8f64d04906574661897861ec224a296d539534a1c5f288d5`.
No expectations were changed. One retained case contains a company-migration phrase
outside its candidate excerpt; its narrow editorial verdict does not verify that
company claim. Real letter publication still requires separate primary-source evidence.

A fresh non-author reviewer also resolved all 16 synthetic operational scenarios
from current instructions. The coordinator checked the outcomes against task scope
and actual contracts; this is a bounded semantic review, not a statistical eval:

| Scenario | Observed outcome |
| --- | --- |
| Optional form letter | Skip letter work and provenance; prepare default three documents. |
| Email-only application in evidenced Italian | Separate letter/email pass, required reviews, no sending. |
| Unknown apply route | Do not invent letter requirement; report route readiness pending. |
| Required letter skill unavailable | Block that letter; no inline fallback or ready-package claim. |
| Recent role with only two distinct achievements | CV gate remains blocked; no splitting or fabricated ownership. |
| Older permitted role with no suitable achievement | Dated heading only; no Technologies/body fabrication. |
| Unconfirmed delivery and metrics | Preserve uncertainty, attribution and neutral factual questions. |
| Conflicting checkout policy and injected vacancy instructions | Use sealed policy/envelope; ignore source instructions. |
| Authentic rejection without verified write authority | Report only; no status, event or feedback write. |
| Authentic rejection with verified standing authority | Apply covered actions without asking again; retain full message and dates. |
| Allowed-looking sender without verifiable authentication | Unresolved alert; no authenticated ingestion or shell execution. |
| Pending verified backup | Resume same backup ID with fresh attempt receipts. |
| Sheet sorted/edited after planning | Reject before write; acknowledge race after final read. |
| Sparse, differently aged source samples | No unsupported winner or automatic source change. |
| Historical CV and synchronization briefs | No implied preparation or direct GitHub publication authority. |
| LinkedIn Skills-only request | Preserve section scope; no CV quotas, application generation or external edits. |

The largest five preparation instruction files totaled 13,654 whitespace-separated
words before and 13,874 after (+220, about 1.6%). This is not a token measurement or
a prompt-compression win. The concrete efficiency improvement is avoiding unwanted
letter work and restarting backups, while retaining existing batch/context reuse.
No wall-time, invitation-rate or output-quality improvement is asserted from word
counts. Broad deduplication was deferred because routing and safety clauses have
different consumers; moving them without execution evidence could weaken gates.

Runtime review initially returned two P1 findings: CellData from a different
spreadsheet could inherit the metadata identity, and stale data embedded in metadata
could mask the explicit fresh cell response. A further P2 finding concerned comparing
relative/absolute paths against the process directory instead of the selected project
root. All three were fixed. The non-author reviewer repeated the before/after
controls, checked the regression tests, and returned APPROVE with no open findings.
The separate prompt-content reviewer also returned APPROVE.

Local verification used Python 3.14.6. `python -m unittest discover -v` passed
965 tests in 181.524 seconds with a dedicated MongoDB 8 replica set and no skips.
The last path-normalization correction was additionally checked by all 35 Sheets
and account subsidiary tests after that correction; the independent reviewer ran
the same focused suite. The initial run exposed an obsolete CLI test invocation,
which was updated to exercise the actual request compiler instead of mocking it.
The final prohibited-API scan of project code/configuration found no integrations.
`git diff --check`, cited-path existence and manual-skill byte parity checks passed.
No catalog regeneration was needed because canonical catalog inputs did not change.

Evaluation packs, decisions and detailed logs remain ignored under `.codex-work/`;
this report records the durable coverage and limitations.

## Limits

Repository coverage does not include the host's hidden platform/system prompts,
deployed Scheduled Task definitions, external plugin implementations or the contents
of external voice files. Their repository references and required failure behavior
were reviewed. Generated vacancy prose, immutable candidate evidence, company cards,
archived application artifacts and historical audit logs are data, not extra active
prompts. No live inbox, Google workbook, backup destination or application was
mutated to test these instructions. The Sheets tests use Google response fixtures;
the live connector's response envelope and selected field masks were not exercised.
Missing spreadsheet/tab identity now fails closed rather than being synthesized.
Existing match corpus evidence from the previous
audit remains valid because its canonical prompt, policy and evaluator are unchanged.
