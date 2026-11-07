# Vacancy compensation benchmark

Required for every salary expectation, compensation recommendation and salary form
field. The candidate asks for the market's central value, researched by Codex, rather
than repeated salary questions. Explicit later candidate instructions take precedence;
preserve named-vacancy exceptions in `config/application-profile.yaml`.

## 1. Define the comparison

Read the selected current vacancy and its application field. Record actual scope,
seniority, relevant discipline, eligible work locations, currency and requested period.
Distinguish a hands-on Staff IC from a manager or a generic senior developer. Record
whether the route specifies employment or contracting; leave an unspecified contract
unknown. Keep the owning workflow's selection, research and submission gates.

## 2. Map where people physically work

Research the company even when the vacancy is fully remote. Prefer current employer
team/office pages, engineering articles and public professional profiles. For each
country/city record function, evidence date, source and one evidence class:

- Employer-attested working hub or existing team: an explicit statement of people
  working there, with the function if supplied.
- Individually corroborated: a current professional role and self-reported working
  location; record that a profile is self-reported, not independently audited.
- Hiring location only: where a vacancy permits a future hire or hybrid attendance.
- Legal/contact address only: never evidence of a working team.

Separate current observation from old statements or search snippets that could not
be opened. An advertised position is not an employee count. A genuine distributed
team counts even without an office. Do not search for private employee contact data.
Record the gaps if physical locations cannot be established; never substitute the
registered address. Stop after a bounded search when further work adds no evidence.

## 3. Identify the relevant team and pay policy

Prioritize this role's engineers, manager and adjacent technical teams over company
sales/support headcount. Keep relevant and unrelated hubs separate. Look for explicit
global pay, location bands, local-market pay or a designated hiring-hub budget.
Office locations indicate possible markets; they do not prove the salary policy.
Candidate residence affects the calculation only when applicability is evidenced,
or is clearly labelled as a provisional scenario rather than company policy.

## 4. Collect comparable pay evidence

Use this order, recording unsuccessful higher-priority searches as gaps:

1. Employer-published band for this exact role and applicable location/contract.
2. Comparable roles at the same company with known level and geography.
3. Comparable employers and recruiter salary studies in the relevant working hubs.
4. Broader regional datasets as a labelled fallback.

Prefer sources from the last 12 months. Record publication/data period, retrieval
date, sample size when available, scope, currency, base/total compensation and why
the comparison fits. Explain any older data. Deduplicate reposts and shared upstream
datasets. Mark recruiter reproductions of an employer's band as such unless its
original is verified. Aggregator-generated estimates are not employer disclosures.
Funding, revenue, prestige or a Staff title alone cannot establish a budget.

## 5. Normalize like for like

Compare annual gross base pay for employment. Keep bonus, commission, pension,
equity and total compensation separate. Use actual guaranteed payments when a source
specifies 12/13/14 instalments; do not invent extra payments. Keep contractor rates
in a separate scenario, including evidenced billable time and benefits differences;
never apply a universal B2B multiplier. Convert currencies only with a cited official
rate and date; otherwise leave each scenario in its native currency. Do not convert
gross to net without the necessary personal tax facts and a suitable method.

## 6. Calculate a central value without invented weights

For comparable individual observations, prefer the median; show the arithmetic
mean too when it is useful and data permit. For a published band use
`(lower + upper) / 2`, explicitly called a band midpoint, not a measured average.
Do not average overlapping publications as independent observations.

Combine markets with weights only when actual relevant-team proportions and a
reason to apply those proportions to pay are known. Hiring counts, office counts
and guesses are not weights. Otherwise show separate scenarios, select one with
an explicit rationale, and retain the others as sensitivity checks. If policy is
unknown, a clearly named provisional scenario is permissible for a required numeric
field. Its interval midpoint may be a negotiation estimate; it cannot be called
the employer's average salary. A midpoint of a cross-market envelope is a scenario
heuristic, not an employee-weighted or statistically estimated market mean.

Round a form figure sensibly, normally to EUR/USD/GBP 5,000 annually, preserving the
requested currency and period. Do not automatically subtract 10%, target the upper
band or add a negotiation premium. Any adjustment needs explicit candidate direction
or evidenced role/contract differences. Keep the exact calculation in the record.

## 7. Save the calculation and use it

Save `research/compensation/YYYY-MM-DD-<company>-<role>.md`, keyed by vacancy ID.
Include:

- Vacancy URL/ID, as-of date, scope, contract and requested field basis.
- Physical-team evidence table with functions, evidence classes, dates and links.
- Pay-policy finding, including unknowns; selected market and rejected alternatives.
- Comparable-source table with periods, sample sizes or explicit unknowns, normalized
  values and limitations; distinguish direct disclosure from third-party reporting.
- Reproducible arithmetic, scenario intervals, central estimate and rounded form value.
- Confidence and what would change the answer. High requires applicable company pay
  evidence; medium requires well-matched market and geography evidence; low applies
  when relevant-team distribution or applicable pay policy remains unresolved.
- Exact proposed form text and whether it was entered; submission requires its own
  authorization. Do not change vacancy status or record a submission from filling.

For low confidence, retain a researched numeric proposal if the field requires it;
use negotiable wording when supported by the field. Do not present the estimate as
a confirmed company budget, candidate minimum or verified personal preference.
Refresh before reuse if the role, pay policy or sources changed, or after 90 days.
Preserve approved application artifacts and their receipts; a new calculation does
not retroactively alter their provenance. Never write research estimates into
immutable candidate evidence.
