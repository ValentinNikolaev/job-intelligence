# Require three substantial CV bullets for roles ending within five years

Update the Job Intelligence CV quality contract and repair the recent six CV-only
packages where the new rule finds a short role. Read `AGENTS.md`,
`config/codex-workflows.yaml`, `docs/application-quality.md`,
`config/cv-editorial-knowledge.yaml`, the `$job-intelligence-workflow` skill,
`prompts/cv-editorial-rebuild-six.md`, and the immutable candidate sources first.
The six selected vacancy directories in that prompt define the package scope;
use each vacancy's current `application_directory` rather than assuming the
original path. In particular, Talmatic currently uses `application-codex/`.

## Editorial rule

Every role displayed in `Experience` whose end date falls within the last five
years must have **at least three distinct, source-backed bullets** in both standard
and compact CVs. Keep the existing two-bullet minimum for older displayed roles,
the preference for four or more substantial bullets in recent roles when evidence
supports them, and the overall CV minima. Rank bullets by value to the target
vacancy, but do not require every bullet to be exceptionally vacancy-specific:
when the top two are narrow, use a broader, still substantial example of backend
delivery, architecture, operational
ownership, technical leadership, or team impact for the third. A documented
responsibility may establish real scope or ownership without a numeric result;
state only the consequence the source actually supports. Do not split one result,
repeat a claim, invent an outcome or metric, or use generic duty filler.

Review all candidate evidence for an in-scope short role before deciding it lacks
material. For Talmatic, inspect the two current airSlate bullets and the separate
documented airSlate work on database load, shared logging, feature delivery, production
support, and team leadership. Check the verification status and later candidate
clarifications for each possible third story. The ECS-to-Kubernetes claim is
explicitly disallowed; do not revive it. Do not convert unconfirmed performance
numbers or generic troubleshooting into confirmed achievements. The candidate has
said that the airSlate period included substantial additional work; if the existing
record still cannot support three distinct strong bullets, ask focused questions
about a concrete system, personal contribution, and observed result. Leave that
vacancy's CV unpublished until the necessary facts are confirmed, and report the
specific gap instead of satisfying the count with filler. Do not omit a substantive
role solely to bypass the three-bullet rule.

## Implementation and package repair

- Change the deterministic per-role validator from its current two-for-older/
  three-for-roles-ending-within-three-years rule to a three-bullet minimum for
  roles ending within five years, with two still allowed for older displayed
  roles. Count only Experience bullets, not Technologies or another section.
  Use the validator's reference date and an explicit five-year cutoff. Apply the
  gate to new CV drafts; identify old receipts as legacy instead of relabeling them.
- Update `AGENTS.md`, the preparation skill/reference, application-quality docs,
  prompts, and tests so they state the same rule and the same evidence boundary.
  Add tests on both sides of the five-year cutoff, compact CVs, excluded
  Technologies lines, and a rejected duplicate/unsupported third bullet where
  the deterministic contract can detect it. Keep human factual-distinctness
  review explicit.
- Audit the six current CVs individually. Rebuild and publish only the CV for each
  package with an in-scope role below three, using verified vacancy-specific
  evidence, updated claims and `cv_audit.bullet_decisions`, and a positive
  editorial receipt.
  Preserve cover letters, analysis, interview preparation, and status. Reuse a
  fresh genuine same-profile match; if a new one is required, analyze that vacancy
  rather than changing a provenance label.
- Validate every changed draft with `validate-application --document cv`, publish
  with `prepare --document cv`, then inspect the rendered DOCX/PDF for a readable
  maximum of two pages with all Experience bullets present. Regenerate the catalog
  when required; run the project checks and inspect the complete diff.

Report per vacancy the before/after bullet counts by role, each added bullet and
its candidate evidence, any fact still requiring confirmation, page count, and
validation result. Publish all real project changes safely in one commit under
the repository's current finalization policy. Do not change vacancy status,
submit applications, edit immutable candidate facts, or add an OpenAI Platform
API integration. Do not open a PR unless requested.
