# Evidence-backed application quality

New preparation uses quality contract 2. Existing contract-1 packages remain readable
and explicitly legacy; their boolean review declarations are not upgraded to verified
claims. Reprepare an explicitly approved vacancy to create a new v2 package. Match
analysis and preparation still run inside Codex; project code only validates and
publishes local drafts.

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
  bullet_decisions:
    - text: '<bullet reviewed>'
      decision: keep
      reason: '<why it answers an important requirement>'
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
Do not turn an unsupported trade-off or missing metric into a claim. Prefer compact
format to padding a standard CV with duties. Group Skills by domain and review the
rendered export for a two-page PDF limit when PDF conversion is available. The
`cv_audit.bullet_decisions` receipt must cover every final Experience bullet with
its exact text and a reason tied to a vacancy requirement or senior-level signal;
the validator checks coverage, while the reviewer remains responsible for meaning.
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
