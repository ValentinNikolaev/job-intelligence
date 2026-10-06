# Custom company-board collector

The custom collector monitors company-owned career pages where no stable public
API is available. Jobs collected here are treated as direct company-board leads:
they use `source: custom`, receive `analysis_priority: 100`, and have the highest
source precedence because these pages are more authoritative than aggregators.

Linked detail pages retain matching JSON-LD `JobPosting` metadata, including
`datePosted`, instead of losing it in the visible-text fallback. Sources configured
with `ats: bizneo` also parse Italian `Pubblicata <day> di <month> [year]` text.
When the year is absent, `published_at` uses the latest non-future occurrence
(an upper bound on the actual date), with the original text and inference basis
preserved in source metadata. This lets the existing seven-day prefilter reject
old advertisements without claiming a confirmed publication year or closed role.
Missing or invalid dates remain unknown; TLS verification is still required.

Edit [`config.yaml`](config.yaml):

```yaml
sources:
  - name: example
    company: Example S.r.l.
    board_url: https://example.test/careers
    company_url: https://example.test
    remote: true
    location: Remote Italy
    title_terms:
      - backend
      - php
      - software
    # Opt in only for pages whose visible headings are actual job titles.
    extract_headings: true
    heading_title_terms:
      - senior php backend developer
    # Exact external ATS hosts that the board is allowed to link to.
    allowed_job_hosts:
      - jobs.workable.com
    # Role content must make Italy eligibility explicit. This can be an Italy,
    # Europe, European Union, or EMEA signal; explicit US/Canada/UK-only
    # restrictions suppress the role.
    location_terms: [Italy, Europe, European Union, EMEA]
    exclude_location_terms: [US only, Canada only, UK only]
    seed_jobs:
      - title: Senior PHP Backend Developer
        url: https://example.test/careers/senior-php-backend-developer
```

For each source, the collector fetches the board page, reads JSON-LD
`JobPosting` blocks, follows links whose text or URL matches the configured
title terms, and optionally fetches explicit `seed_jobs`. By default links must
remain on the board hostname; `allowed_job_hosts` admits only exact additional
hostnames, such as a public ATS. With `extract_headings: true`, each matching
`h1`–`h6` on the board is treated as a separate inline role.
`heading_title_terms` is mandatory in that mode and should contain specific
current role titles rather than broad words such as `developer`. The role
identity is a hash of the canonical board URL and normalized heading, so
multiple roles on one page remain distinct. It stores the fetched HTML as
Markdown, so downstream validation and publishing remain deterministic.

`seed_jobs` are for persistent or known open company-board pages. Do not add a
generic application form as a seed unless it represents a real current vacancy.
For a named role inside a shared board, set `description_start` and
`description_end` on its seed to exact visible text delimiting that role.
Matching ignores case and markup whitespace. Every configured marker must be present
in order; otherwise that seed emits no vacancy. The end marker requires a start
marker and is excluded from the description. Scoped seeds use the board URL and
title for identity, allowing several named roles on one page without collisions.
Do not use application-select options or placeholder text as role boundaries.
Pages that require JavaScript rendering may produce no vacancies until their
server-rendered HTML exposes matching links or JSON-LD.

The [Rome-office source notes](rome-boards.md) record the 20 added boards,
verified parsing modes, and access/freshness limitations. An office in Rome does
not assign Rome to every vacancy; Laser Romae's Go role is in Milan and FOS's
PHP/Python role is in Genova. Undated advertisements retain an unknown publication
date. The normal shared prefilter still applies, including CMS/front-end exclusions.

`location_terms` is an optional role-level allowlist. When configured, the
title, visible job-page text, and JSON-LD location must contain one of those
terms. `exclude_location_terms` rejects an explicit conflicting restriction
even when an allowlist term is also present. Use these fields for a location
policy; do not label every role on a global company page as remote or Italy
eligible. A worldwide role is emitted only when its page also makes Italy or
an allowed European region explicit.

The board, every seed, and every followed detail page fail independently. A
failed board page does not suppress explicit seeds, while a failed detail page
does not discard roles already collected from the same source.

Up to eight sources are fetched concurrently. Pages within a source are fetched
in their existing order, and the collector emits jobs and resolves duplicates
in config order even when later sources finish first. Each source owns its own
`urllib` opener, and each page uses a fresh request; no HTTP session is shared
between workers. The
per-source and per-page JSON logs include timings and failures, while request
and error totals include every attempted page across workers.

## Yeb

The Yeb board at <https://www.yeb.it/azienda/lavora-con-noi> uses an accordion
whose fragment IDs change between page renders. The configured Senior PHP seed
uses the stable page URL and visible Senior/Junior headings to isolate its
requirements; generic accordion links are deliberately not followed. Remote work
and the publication date remain unknown.

The full Senior section mentions Drupal and WordPress as preferred knowledge.
The existing shared CMS prefilter therefore excludes it from automatic intake.
An explicitly user-selected application can use `add-manual` with the complete
section and its original qualifications; this does not change the collection
policy or remove source wording to evade it.
