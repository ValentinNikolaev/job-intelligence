# Require three substantial CV bullets for roles ending within five years

Update the Job Intelligence CV quality contract and regenerate **all six CVs**
prepared in the preceding six-CV editorial rebuild, including CVs that already
meet the new per-role minimum. Read `AGENTS.md`,
`config/codex-workflows.yaml`, `docs/application-quality.md`,
`config/cv-editorial-knowledge.yaml`, the `$job-intelligence-workflow` skill,
`prompts/cv-editorial-rebuild-six.md`, and the immutable candidate sources first.
Use each vacancy's current `application_directory` rather than assuming the
original path. In particular, Talmatic currently uses `application-codex/`.

## Six CVs to regenerate

Regenerate the CV Markdown, DOCX, upload-friendly CV copies, and CV-related
manifest receipts for every vacancy below. Keep each draft and evidence review
independent. Do not treat an already compliant bullet count as a reason to skip
that vacancy.

1. `registry/jobs/2026-09-14_180905_talmatic_senior-go-golang-software-engineer/`
2. `registry/jobs/2026-09-25_004218_slotcatalog_senior-php-developer_05157206-8864-4b3a-bb38-cb8d42304ac8/`
3. `registry/jobs/2026-09-25_004218_nova-digital_lead-backend-php-developer_72f6ead5-395f-45d9-bb98-9554ece2fe48/`
4. `registry/jobs/2026-09-23_070623_webeetle_developer/`
5. `registry/jobs/2026-09-25_111732_infobus_php-developer-support_1917faa8-9aeb-4bb4-96ec-7b29df67d582/`
6. `registry/jobs/2026-09-25_181923_recare-deutschland-gmbh_senior-backend-engineer-go-m-w-d_f2ba10d6-6781-4168-bbcd-7c7becdfb7e5/`

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
- Audit and regenerate all six CVs individually under the new editorial rule,
  using verified vacancy-specific evidence, updated claims and
  `cv_audit.bullet_decisions`, and a positive editorial receipt. Preserve cover
  letters, analysis, interview preparation, and status. Reuse a fresh genuine
  same-profile match; if a new one is required, analyze that vacancy rather than
  changing a provenance label.
- Validate all six finalized drafts with `validate-application --document cv`,
  publish the six CV-only packages with `prepare --document cv` after they pass,
  then inspect every rendered DOCX/PDF for a readable maximum of two pages with
  all Experience bullets present. Regenerate the catalog when required; run the
  project checks and inspect the complete diff.

Report per vacancy the before/after bullet counts by role, each added bullet and
its candidate evidence, any fact still requiring confirmation, page count, and
validation result. Publish all real project changes safely in one commit under
the repository's current finalization policy. Do not change vacancy status,
submit applications, edit immutable candidate facts, or add an OpenAI Platform
API integration. Do not open a PR unless requested.
