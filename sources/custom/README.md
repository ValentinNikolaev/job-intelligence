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
    seed_jobs:
      - title: Senior PHP Backend Developer
        url: https://example.test/careers/senior-php-backend-developer
```

For each source, the collector fetches the board page, reads JSON-LD
`JobPosting` blocks, follows same-site links whose text or URL matches the
configured title terms, and optionally fetches explicit `seed_jobs`. It stores
the fetched HTML as Markdown, so downstream validation and publishing remain
deterministic.

`seed_jobs` are for persistent or known open company-board pages. Do not add a
generic application form as a seed unless it represents a real current vacancy.
Pages that require JavaScript rendering may produce no vacancies until their
server-rendered HTML exposes matching links or JSON-LD.
