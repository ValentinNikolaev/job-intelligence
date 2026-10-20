# Application review contract 3

New publication requires quality schema 3 and claims-ledger schema 2. Versions 1 and
2 remain readable and explicitly legacy; do not upgrade their labels or regenerate
existing applications. A new single-document publication preserves all other files
and their original review records. New preparation still needs explicit named-vacancy
approval and its normal preflight. These controls run inside the existing evidence,
independent CV edit and final letter passes, without another compulsory agent wave.

Resolve preparation settings from `config/application-profile.yaml` and voice sources
from `config/application-review.yaml`. New schema-3 `quality.yaml` drafts must copy
the exact `preparation_context_version` returned by the selected batch's preflight.
Validation and publication reject missing or changed context before publication;
never attach a current identity to an old draft to make it eligible. The manifest
records this identity for each newly published document. A single-document refresh
preserves the other documents' original identities and review records. Existing
records without the binding stay readable and require explicit regeneration to meet
the current preparation contract.

Candidate source contents, evidence entries and cover-letter voice bytes retain
their own source/hash checks. Configuration identity does not prove source meaning
or replace those checks. CV-only and evidence commands resolve voice configuration
without requiring unrelated host-local letter files to be available.

## Achievement context and missing facts

An evidence-bank entry may add `achievement_context`. The supported keys are
`problem`, `contribution`, `scope`, `decision`, `consequence`, `delivery_status` and
`responsibility`. Each is `{status: supported, quote: <exact primary-source excerpt>}`
or `{status: unknown}`. A contextual excerpt must occur in that entry's primary
`source.quote`; another employer's context or the attribution-only source cannot
supply an achievement. Verification of the entry remains mandatory before claims.
Do not infer decision ownership, production rollout or causal results from a title.

`python run.py evidence questions --id <evidence-id>` lists missing contextual fields,
measurement records and measurement baseline/period/method. Repeat `--id` for a bounded
selection and use `--bank` for a reviewed draft bank. It validates source quotes and
hashes and writes nothing. Candidate answers must become separately sourced candidate
clarifications through the existing authorized source workflow, not generated prose.
Reuse current verified facts; a missing metric is not a reason to invent one.

Every CV claim in ledger schema 2 includes `support`, with `contribution`, `scope` and
`consequence` each containing `evidence_id` and an exact `quote` from a referenced
verified entry. The same source excerpt may support several dimensions. The reviewer
must still check its meaning; an implementation-only sentence cannot establish a
consequence merely by being copied into that field.

## Measurements with attributed context

An evidence entry can contain:

```yaml
measurements:
  - id: onboarding-time
    value: '35%'
    measure: onboarding time
    unit: '%'
    scope: team
    baseline: null
    period: null
    method: null
    quote: 'Reduced team onboarding time by 35%.'
```

This is synthetic schema data, not candidate evidence. `quote` must be an exact
primary-source substring. Value, measure, unit and scope must occur in it. Baseline,
period and method must be exact sourced text or explicit null for unknown. Null is
permitted; do not turn an absent measurement method into an invented explanation.
For dates, versions or counts, use the actual measure/unit/scope wording in the source
and claim; numeric context is not a demand that every number be a performance metric.

A numeric claim includes `measurements: [{evidence_id: <id>, measurement_id:
onboarding-time, claim_quote: <exact final-claim excerpt>}]`. The claim excerpt must
preserve the source value, measure, unit and scope. Every numeric token in a schema-2
claim needs a binding; a number somewhere in a long source quote is insufficient.
The validator catches missing context and obvious measure/unit/scope reassignment.
For a translated claim, a measurement binding may add `translation: {language,
reviewer, reason, source_quote, measure, scope}`. Its source quote must equal the
original measurement context; translated labels must occur in the final claim and
the value/unit remain unchanged. The target language must differ from the source
measurement's optional `language` (default English). An English-to-English relabeling
cannot bypass the measure check. The named editor reviews equivalence; code cannot
establish that an arbitrary translation preserves meaning.
It does not establish causation or semantic equivalence of an arbitrary paraphrase.
Review qualifiers, estimates, periods, personal versus team contribution and actual
delivery stage against the source. Preserve a qualitative result when confirmation
is unavailable. No measurement data is added automatically to the existing bank.

## Complete role inventory

`cv_audit.role_coverage` contains every employer returned by the canonical corrected
career inventory, including policy-excluded employers internally. Each row records:

- `employer`, exact canonical name;
- `source_period: {start: [year, month_or_null], end: [year, month_or_null] | null}`;
- `decision: include|exclude`, according to the current career policy;
- `reason`, explaining the scope decision and vacancy relevance;
- `heading`, the exact final H3 title without its Markdown marker for an included
  employer, or null for an excluded one;
- `sources`, a nonempty list of candidate `path`, exact `quote`, normalized source
  `sha256` records;
- `reviewer`, the actual CV editor from `cv_audit.editorial_review`.

The editor's receipt also records `author`, separately from `reviewer`. Independent
mode rejects an identical author/editor. Source dates and scope are recomputed on
validation; adding a source employer cannot silently bypass coverage. Every final
heading must be accounted for. The existing career-window and date rules remain in
force, including dated empty bodies for permitted older roles. Exclusion within the
approved employer window is not an editorial shortcut. Code checks completeness and
source records; the independent editor reviews wording, attribution and relevance.

## Two evidence strands and the final letter

Keep the existing `cover_letter.evidence_stories` key with exactly two internal
complementary evidence strands. Its name does not set the number of visible stories.
Normally use one brief narrated example; an email allows zero or one, an attachment
zero, one or two. A second must add a distinct substantive point. Each ability still
needs an anchored candidate claim in the final letter. All channel word/paragraph
limits and the mandatory installed write-cover-letter skill remain in force.

`cover_letter.editorial_review` records:

- actual `reviewer` and `document_sha256` of final normalized Markdown;
- `basis_sha256`, returned by `review_digest(letter_basis(quality))` from
  `jobintel.application_review`;
- `priority_mapping`, exactly two ordered rows matching the evidence strands, each
  with `requirement`, matching `evidence_ids`, a distinct `point`, `why_priority`, and
  an exact `letter_quote` anchored in the claims ledger;
- `distinctness` and `channel_fit`, concrete review notes;
- `narrated_examples`, a list of `{letter_quote, adds_value}`, with the channel limit;
- `company_claim`, the final-text excerpt containing the verified company fact;
- `company_grounding`, the concrete source-to-final-text rationale, including
  semantic equivalence when the source and final letter use different languages;
- `voice: {language, notes, rules: [{path, sha256}, ...]}`.

Priority mappings must name actual supported requirements and use their evidence.
Where supported critical/high requirements exist, select from them. Inspect semantic
distinctness; changing a label does not turn the same point into another ability.

The company-motivation record adds `snapshot: {path, url, quote, sha256, checked_on}`.
Capture primary-source text directly into the ignored draft, for example
`parts/company-source.txt`, not from generated company research. Its path must stay
within the draft. Hash raw bytes, record the actual ISO checking date and original URL.
The source quote must occur in the captured text and contain the fact used in the final
letter. The validator verifies file/quote consistency, not the remote site's truth or
whether a forged local capture came from it; the reviewer must inspect the primary
source. The manifest retains the quote, URL and source hash in its review basis.

Read every current voice source configured in `config/application-review.yaml` and
inspect the exact final language after all edits or translation. Record practical
voice notes and raw-byte hashes for all sources in configured order. The nonempty
source list may use different filenames. A changed final letter, evidence
mapping, company snapshot or current voice source invalidates its review. Source paths
are configurable for another host; missing rules fail the new letter check explicitly.
Markdown review hashes use SHA-256 of `(text.strip() + "\n")`, prefixed with `sha256:`.
Mapping digests use the supplied helper; do not approximate its serialization.

## Executable gates and evaluation

`lint-application` reports role coverage, contextual claims and final-letter defects.
`validate-application` applies the same controls before conversion; publication
revalidates them and exports. These records are preserved in the manifest and merged
per document. Cached v3 letters also recheck current voice hashes. Old receipts are
not retroactively verified and may be stale for a future explicitly selected refresh.

Use [the blind evaluation prompt](../prompts/editorial-evaluation.md) after changing
editorial decisions or the application prompt. The corpus has ten synthetic cases:
routine repair, material reliability, unproven package influence, verified adoption,
metric reassignment, team ownership, proposal versus delivery, omitted employer,
CV-replay letter and a one-example email. Export hides expected answers; evaluation
rejects incomplete/stale/fabricated responses and fails wrong decisions or reason codes.
Existing unit tests verify the evaluator with positive and negative controls; a real
independent Codex pass tests editorial behavior. Neither predicts employer outcomes.
The repository finalizer refuses review/publication of changed editorial-policy
paths without `.codex-work/editorial-decisions.json` and a successful evaluation
against the current corpus and policy hashes. It reevaluates the decisions before
publication and the API fallback, so an old successful receipt is insufficient.
Continue using confirmed submissions and descriptive lifecycle statistics to assess
usefulness, without automatic strategy changes from small observational segments.
