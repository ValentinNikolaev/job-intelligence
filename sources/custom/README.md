# Custom company-board collector

The custom collector monitors company-owned career pages where no stable public
API is available. Jobs collected here are treated as direct company-board leads:
they use `source: custom`, receive `analysis_priority: 100`, and have the highest
source precedence because these pages are more authoritative than aggregators.

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
Pages that require JavaScript rendering may produce no vacancies until their
server-rendered HTML exposes matching links or JSON-LD.

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
