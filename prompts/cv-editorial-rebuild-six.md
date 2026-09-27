# Senior+/Architect CV editorial rebuild — six selected vacancies

Rebuild **only the CV** for each explicitly selected vacancy below. Do not change a
vacancy status, submit an application, regenerate a cover letter, or edit interview
preparation or application analysis. Use `$job-intelligence-workflow`, `AGENTS.md`,
`config/codex-workflows.yaml`, `docs/application-quality.md`, and the immutable
candidate evidence bank. Process every vacancy independently; do not reuse employer
requirements, company claims, keyword choices, or wording between packages.

## Selected packages

1. `registry/jobs/2026-09-14_180905_talmatic_senior-go-golang-software-engineer/application/`
2. `registry/jobs/2026-09-25_004218_slotcatalog_senior-php-developer_05157206-8864-4b3a-bb38-cb8d42304ac8/application/`
3. `registry/jobs/2026-09-25_004218_nova-digital_lead-backend-php-developer_72f6ead5-395f-45d9-bb98-9554ece2fe48/application/`
4. `registry/jobs/2026-09-23_070623_webeetle_developer/application/`
5. `registry/jobs/2026-09-25_111732_infobus_php-developer-support_1917faa8-9aeb-4bb4-96ec-7b29df67d582/application/`
6. `registry/jobs/2026-09-25_181923_recare-deutschland-gmbh_senior-backend-engineer-go-m-w-d_f2ba10d6-6781-4168-bbcd-7c7becdfb7e5/application/`

## Editorial standard

Treat the final CV as a Senior Backend Engineer / Backend Architect document, not an
engineering design note. A confirmed fact may support a bullet, but is not automatically
a resume achievement.

For every Experience bullet, apply this test:

`candidate contribution → consequential decision or change → supported consequence`

Reject or rewrite a bullet that fails any part. Do not compensate for missing evidence
with a number, a plausible impact statement, or a rephrased duty.

### Priority order inside each role

Rank bullets before writing and publish them from strongest to weakest:

1. Confirmed impact on customers, product delivery, safety, security, compliance,
   reliability, cost, or operational risk.
2. Architecture ownership and consequential technical judgment.
3. Scale, a difficult integration, or a material process change.
4. Operational resilience, observability, performance, or compliance improvement.
5. Team-level standardization or influence.
6. A secondary technical detail only when it strengthens an earlier result.

Record for every retained bullet: `weight` (`critical`, `high`, `medium`, `low`),
signal type (`impact`, `architecture`, `security`, `reliability`, `scale`, or
`team_influence`), the ordering rationale, and verdict (`approve`, `rewrite`, or
`reject`). A CV cannot be published unless every displayed bullet has `approve` and
the completed ordering is descending by weight within each role.

### Exclusions

Keep source-code line counts, test counts, coverage, internal ticket IDs, permission
names, API field names, UI controls, TTL mechanics, queue/contact-flow mechanics,
specific QA scenarios, and similar implementation details in the evidence bank or
interview preparation. Do not put them in a CV.

For Simple.life telephony, lead with the employer-relevant result: privacy-first
health-domain calling architecture protecting PII/PHI, formal security and
call-recording compliance review, and a production release. Describe lawful calling,
least-privilege access, and auditability only at outcome level. Do not list how phone
numbers were resolved, masked, transported, retained, or purged.

## Reusable editorial knowledge base

Maintain a deterministic, versioned editorial knowledge base for future CV work. It
must contain approved Senior+/Architect outcome patterns, rejected anti-patterns,
and mappings from internal implementation facts to employer-facing consequences. It
may suggest a shape, but never supply a candidate claim. Each candidate claim must
remain grounded in immutable candidate evidence.

Add deterministic checks that reject known anti-pattern categories and require a
positive final editorial receipt. The check must not force filler bullets, invent a
consequence, or convert an unsupported metric into an achievement.

## Evidence and rendering rules

- Use only `verified` evidence-bank entries backed by `registry/candidate/*.md`.
- Preserve the confirmed Simple.life date/title treatment and PHP attribution rules.
- Retain at least two distinct substantive bullets for every displayed role and at
  least three for each role ending in the last three years. Omit a role if evidence
  cannot satisfy this without filler.
- Keep reverse chronology, role dates, vacancy-specific skills, and a maximum of two
  visually readable pages.
- Use PHP for Simple.life only in Technologies unless a direct source confirms a
  Simple.life PHP result. Attribute CRURATED PHP delivery to CRURATED.

## Required workflow and acceptance criteria

1. Create CV-only drafts under `.codex-work/application/<vacancy-directory>/`.
2. Update claims, evidence map, `quality.yaml`, and manifest-bound metadata so every
   final bullet has an evidence anchor and an editorial verdict.
3. Run `validate-application ... --document cv` for each selected vacancy.
4. Publish with `prepare ... --document cv` only after all selected drafts pass.
5. Before canonical publication, preview each final draft with `python run.py documents
   preview-cv .codex-work/application/<vacancy-directory>/cv.md` and visually inspect
   every rendered page: maximum two pages, no clipping, orphaned headings, overlap,
   or unreadable density. The publisher reuses a matching checked preview DOCX.
6. Regenerate the catalog, run the relevant tests and the prohibited-API scan, inspect
   the complete staged diff, and publish the reviewed commit to `main` through
   `scripts/finalize_repository.py` without force.

Report, for every vacancy: the reordered final bullets with weights, removed/rejected
bullets and their reasons, evidence sources, page count, validation result, and the
published commit hash.
