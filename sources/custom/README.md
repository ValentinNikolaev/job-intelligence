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

The board, every seed, and every followed detail page fail independently. A
failed board page does not suppress explicit seeds, while a failed detail page
does not discard roles already collected from the same source.
