# Evidence-backed application quality

New preparation uses quality contract 2. Existing contract-1 packages remain readable
and explicitly legacy; their boolean review declarations are not upgraded to verified
claims. Reprepare an explicitly approved vacancy to create a new v2 package. Match
analysis and preparation still run inside Codex; project code only validates and
publishes local drafts.

An explicit named-vacancy refresh of an existing CV can use
`--document cv --allow-low-score-cv-refresh` when its current approved-profile match is
`possible_match` below the configured preparation threshold. The flag does not apply to
new packages, other documents, hard rejections, or automatic selection. Report the
score and material gaps to the candidate rather than disguising fit.

When the user explicitly chooses to pursue a vacancy that remains a recorded hard
rejection, a CV-only refresh of its existing package may instead use
`--document cv --bypass-hard-rejection-cv-refresh`. This is a narrow, user-approved
exception: it does not alter the match record, make the vacancy generally eligible,
permit a new package or other documents, or apply to scheduled work. Report the
recorded rejection and the bypass in the user-facing result.

## Candidate evidence bank

`registry/candidate/*.md` remains immutable. `registry/evidence/achievements.yaml` is a
source index, not another source of truth. Its entries include source-reviewed
excerpts, candidate-confirmed clarifications, and unresolved imported claims;
use the evidence validation command for current counts. Ambiguous imported dates
and metrics remain unverified. Newly bootstrapped entries
always start unverified.
A reviewer must compare the quoted source, attribution and meaning before using an
entry. Current candidate unknowns can be listed with:

```powershell
python run.py applications profile-questions
python run.py evidence validate --bank registry/evidence/achievements.yaml
python run.py evidence bootstrap --input .codex-work/extracts.yaml --output .codex-work/bank.yaml
python run.py evidence publish --input .codex-work/reviewed-bank.yaml
```

Bootstrap takes a YAML list of entries with `id` and `source.path`/`source.quote`, plus
optional `employer`, `role`, `period`, and `technologies`. It calculates the source's
normalized-text SHA-256 and always creates unverified entries. It never overwrites a bank.
Publish validates all entries and preserves existing IDs and retractions. Optional `source.context_quote` is another exact excerpt from the same source for
employer/role/period context; it never supplies claim numbers. Sources
must be direct candidate Markdown files; paths escaping that directory are rejected.
When the work excerpt and separately confirmed role title live in different
candidate files, an entry may use `attribution_source` with its own candidate
path, exact quote and normalized hash. This second source establishes role
attribution only; claim numbers and technologies still need the primary
`source.quote`. Do not use it to conceal a title or date conflict.

A bank contains:

```yaml
schema_version: 1
entries:
  - id: example-delivery
    status: verified
    employer: Example
    role: Backend Engineer
    period: 2020 - 2024
    technologies: [PHP]
    source:
      path: registry/candidate/backend-engineer-cv.md
      quote: '<exact source excerpt containing the employer, role, period and technology>'
      sha256: '<SHA-256 of UTF-8 source text, BOM removed and CRLF normalized to LF>'
    verification:
      reviewer: '<actual reviewer>'
      reviewed_at: '2026-09-22'
      method: source-quote-and-attribution-review
```

This is a schema example, not candidate evidence. Entry statuses are `verified`,
`unverified`, `cannot-confirm`, and `retracted`. Only verified entries may support
claims. The last two require `reason`; publish preserves them unchanged. New evidence
must have a separate ID and its own source. Never ask a leading question that turns an
unknown metric into a guess. Missing metrics can stay narrative-only.

Bank reuse means selecting primary evidence again. It does not permit reusing another
vacancy's keywords, research, conclusions or application text.

## Claims and requirement provenance

In the selected draft directory, create `claims.yaml`:

```yaml
schema_version: 1
claims:
  - document: cv
    text: '<exact complete bullet appearing in final cv.md>'
    evidence_ids: [example-delivery]
    employer: Example
    role: Backend Engineer
    technologies: [PHP]
```

Use `cv`, `cover-letter`, `analysis`, or `interview-preparation` as document names.
Every selected document needs anchored candidate evidence, and every Experience
bullet needs a complete anchor. Numbers and declared role/technology attribution are
checked against the referenced source excerpts. A mechanical pass does not establish
semantic equivalence: the final reviewer still checks ownership, units, dates, context,
qualification and cross-document consistency. Do not widen an excerpt merely to make
an unrelated number pass.

Requirement rows use the same vocabulary in matching and preparation:

```yaml
requirement: Production PHP development
importance: high
basis: structural
jd_quote: '<exact excerpt from this vacancy>'
match: strong
candidate_quote: '<exact supporting candidate excerpt>'
risk: ''
mitigation: ''
hard_blocker: false
evidence_ids: [example-delivery]
```

Importance is `critical|high|meaningful|preferred|low_signal`; basis is
`stated|structural|inferred`; match is
`strong|partial|missing|unknown|not_applicable`. Inferred rows cannot be critical,
high, or hard blockers and leave `jd_quote` empty. Stated and structural rows require
a source quote. High/critical gaps require risk and mitigation. Missing candidate
information is unknown, not proof of an incompatibility. Hard blockers require a
stated rule and candidate evidence establishing the conflict. `evidence_ids` are
optional in match analysis, required for strong/partial preparation rows, and must
refer to evidence used by the package. No additional numeric weight is computed.

## Quality receipt

A new draft's `quality.yaml` extends the existing two-wave receipt:

```yaml
schema_version: 2
workflow: two-wave
document_format: standard
evidence_bank: registry/evidence/achievements.yaml
claims_ledger: claims.yaml
final_review:
  claim_grounding: true
  cross_file_consistency: true
  quality_gate: true
  reviewer: '<actual reviewer identity; distinguish self-review from independent review>'
  document_sha256:
    cv: 'sha256:<normalized Markdown digest>'
    cover-letter: 'sha256:<normalized Markdown digest>'
    analysis: 'sha256:<normalized Markdown digest>'
    interview-preparation: 'sha256:<normalized Markdown digest>'
cv_audit:
  target_role: '<supported target positioning>'
  top_third_evidence_ids: [example-delivery, example-reliability]
  editorial_review:
    knowledge_base_version: 1
    verdict: approve
    reviewer: '<actual editor identity>'
    mode: independent
  bullet_decisions:
    - text: '<bullet reviewed>'
      decision: keep
      reason: '<why it answers an important requirement>'
      weight: critical
      signal_type: impact
      ordering_rationale: '<why this bullet precedes the next one in its role>'
      contribution: '<candidate-owned decision or delivery>'
      affected_scope: '<system, users, team, or organisation affected>'
      consequence: '<source-backed consequence; not merely the completed implementation>'
      verdict: approve
requirements: []
cover_letter:
  skill: write-cover-letter
  version: '<actually invoked installed version>'
  workbench_complete: true
  evidence_stories:
    - requirement: '<first priority>'
      candidate_source: registry/candidate/backend-engineer-cv.md
      evidence_ids: [example-delivery]
    - requirement: '<complementary priority>'
      candidate_source: registry/candidate/backend-engineer-cv.md
      evidence_ids: [example-reliability]
  company_motivation:
    fact: '<verified company-specific fact>'
    source_url: 'https://example.test/primary-source'
```

Fill the requirements list with actual rows; an empty list is invalid in preparation.
Replace every example value. The two top-third IDs must anchor actual CV text. Record
keep/remove/rewrite decisions for the reviewed bullets, with reasons, against the final
CV. A normalized Markdown digest is SHA-256 of `(text.strip() + "\n")` encoded as
UTF-8, prefixed with `sha256:`. Evidence source hashes normalize UTF-8 text, BOM and line endings and have no prefix;
submission snapshots and lifecycle source receipts retain raw-byte hashes. Single
document mode includes only selected document hashes and applicable CV/letter fields.
The existing substantive handoffs remain required.

When one document is republished, its manifest quality receipt replaces only that
document's claims, hashes, export, and applicable handoffs. Receipts for unchanged
documents remain in the manifest. `grounding.document_receipts` records each
document's review and claims-ledger source after such a merge. The top-level
claims-ledger hash and path refer to the newly published document.

Standard limits remain CV 400–800 words, letter 300–450. A CV Summary is one
employer-facing paragraph of 50–110 words and cannot contain internal evidence IDs,
source/verification commentary, gap notes, placeholders, or drafting language.
`document_format: compact`
allows CV 300–800 and letter 150–450, with at least six Experience bullets and three
body paragraphs. Recommended compact targets are CV 300–500 and letter 150–250.
The analysis/interview minima and ceilings remain unchanged. Preserve two meaningful
letter stories, credible claims and required sections in either format. Compact is
selected for the application channel or user preference, never an excuse for generic
or skeletal content. Current Experience still excludes roles older than ten years.

For Senior or Tech Lead positioning, the final CV audit is editorial as well as
mechanical. Each Experience bullet should identify a supported contribution, the
system or people affected, and a consequence. Quantified scale is useful only when
the candidate evidence supports it. Review architecture judgment, reliability and
operations, simplification, and influence beyond code where the source records them.
The audit must also distinguish material senior-level evidence from routine baseline
work. Restoring a third-party integration, cron, scan, retry flow, or long-running job
is ordinary operational ownership unless evidence establishes a consequence beyond
returning to expected behaviour. Similarly, creating a shared logger, library, package,
or implementation aligned with an existing standard is not a Senior+ outcome without
a documented architectural decision, adoption, migration, or organisation-level
consequence. Senior-sounding verbs do not change this test. Omit a baseline item when
the stronger result cannot be grounded; never invent scale, influence, or a trade-off.
For Senior, Tech Lead, Staff, Principal, or Architect positioning, the editorial review
must be independent of the CV author and record `mode: independent`. Every retained
bullet's receipt must state the candidate's contribution, affected scope, and actual
consequence. These fields make the reviewer confront a duty-only or routine-baseline
line before it can be approved; they are not a licence to infer a missing outcome.
Do not turn an unsupported trade-off or missing metric into a claim. Prefer compact
format over padding. Count distinct outcome bullets under every displayed role and
explain any one- or two-bullet role before publication. Recent roles should carry the
most substantive evidence; order bullets within each role by vacancy-relevant impact
and scope before implementation details. Record these role-by-role choices in
`cv_audit.bullet_decisions`, including why the first bullet is the strongest and why
the remaining bullets are distinct. Group Skills by domain and review the
rendered export for a two-page PDF limit when PDF conversion is available. The
`cv_audit.bullet_decisions` receipt must cover every final Experience bullet with
its exact text and a reason tied to a vacancy requirement or senior-level signal;
the validator checks coverage, while the reviewer remains responsible for meaning.
The versioned, deterministic CV guidance lives in `config/cv-editorial-knowledge.yaml`.
For every final Experience bullet, record `weight` (`critical`, `high`, `medium`,
`low`), `signal_type` (`impact`, `architecture`, `security`, `reliability`,
`scale`, `team_influence`), an ordering rationale, and `verdict: approve`.
List bullets from strongest to weakest within each role. The validator checks the
positive versioned editorial receipt, exact final-bullet coverage, descending
weights, and known internal-detail anti-patterns. These checks cannot establish
that a claimed consequence is true or that two bullets represent distinct work;
the editor must confirm both against verified candidate evidence. A rejected
bullet stays out of the CV rather than being padded or split to reach a count.
The validator also requires reverse chronology and at least two bullets for
each displayed role, rising to three for roles ending within five years of
preparation (including the explicit five-year cutoff month). It counts only
Experience bullets, never a Technologies line, and rejects a mechanically
detectable repeated bullet within the same role. These are rejection thresholds,
not prompts to invent or split
achievements. Revisit sources and omit an inessential older role or pause the
package when distinct facts cannot support the threshold.
When an imported candidate source offers useful but unconfirmed figures, present
them with their context for candidate selection and ask how each was measured.
If the candidate requests clarification, ask a focused follow-up about the
metric's scope, personal contribution, and measurement source; a question is
not a rejection. Use only the figures the candidate confirms; retain a
qualitative outcome when confirmation is unavailable.

## Export validation and visual review

Contract-2 publication validates selected DOCX exports against canonical Markdown
before the atomic package swap and stores machine-readable receipts in the manifest.
Legacy documents do not silently acquire this receipt. The validator extracts actual
DOCX text, checks preservation/order, hyperlink targets, hidden text, and small fonts.

```powershell
python run.py documents validate cv.md cv.docx --receipt .codex-work/docx-check.json
python run.py documents export-pdf cv.docx .codex-work/cv.pdf
python run.py documents validate cv.md .codex-work/cv.pdf --max-pages 2
python run.py documents render .codex-work/cv.pdf .codex-work/cv-pages
```

Paths are examples; use the selected vacancy's real files. PDF export uses LibreOffice
when installed; PDF checks/rendering use Poppler tools. Missing dependencies produce
an explicit diagnostic, not a successful empty check. DOCX text validation uses the
standard library. A page budget is a delivery-format constraint, not an ATS score.
After rendering, inspect every page for clipped text, awkward breaks, blank pages and
legibility. Supply a visual-review receipt only after actual inspection; it must bind
to the same artifact hash. Editing or regenerating the file invalidates that review.
Uninspected exports retain `not_reviewed`; text preservation alone cannot certify a
specific employer's ATS. Use `documents validate --help` for visual receipt options.

For a selected CV-only batch, run `python run.py prepare-preflight <directory-or-id>
[...] --workflow prepare` before drafting. For each finalized draft, run
`python run.py lint-application <directory-or-id> --input <draft-directory>
--document cv`, preview it, and then run the combined validator. Lint aggregates
predictable handoff, grounding quote, evidence status, hash, CV-audit, and
Experience-depth defects; it never replaces publication validation. `python run.py
documents preview-cv` returns `status: unavailable` without writing a
canonical package when a renderer prerequisite is missing. A successful preview is
bound to the Markdown, converter code, DOCX options and artifact hashes, so changing
any of them invalidates preview reuse and requires another visual review.

## Measurement and later application stages

See `application-lifecycle.md` and `../prompts/application-lifecycle.md` for confirmed
submissions, descriptive outcome analysis, form answers, practice and follow-ups.
No new command sends mail, submits a form, or changes vacancy status. Company-specific
historical salary context lives in `config/application-company-context.yaml` and must
be reverified for that company; it is never a global candidate salary preference.

The mechanisms were independently implemented after reviewing career-ops at
[de4d285](https://github.com/career-ops-hq/career-ops/tree/de4d28535f15cec37f315552fab1292f1da636e2).
Their usefulness should be evaluated from confirmed submissions and invitations, not
from a generated quality score or a claimed universal improvement percentage.
