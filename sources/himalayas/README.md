# Himalayas collector

The Himalayas collector searches the public remote-jobs API and stores matching
vacancies in the local registry. It uses
`https://himalayas.app/jobs/api/search`, requires no API key or account, and is
intended for private job discovery.

## Configuration

Edit `sources/himalayas/config.yaml`:

```yaml
version: 1
timeout_seconds: 30
max_pages_per_query: 5

queries:
  - q: "backend engineer"
    country: "IT"
    seniority: "Senior"
    sort: "recent"

  - q: "golang"
    country: "IT"
    seniority: "Senior"
    sort: "recent"

  - q: "backend engineer"
    worldwide: true
    seniority: "Senior"
    sort: "recent"
    max_pages: 3
```

`HIMALAYAS_CONFIG` in `sources/.env` can point to a different YAML file. It is
only a path override; there are no credentials.

The API search parameters supported in each query are:

| Parameter | Value |
|---|---|
| `q` | Free-text search |
| `country` | ISO alpha-2 code, country name, slug, or common abbreviation |
| `worldwide` | Boolean; only worldwide-friendly jobs |
| `exclude_worldwide` | Boolean; omit worldwide jobs from a country search |
| `seniority` | One value, comma-separated values, or a YAML list |
| `employment_type` | One value, comma-separated values, or a YAML list |
| `company` | One company slug, comma-separated slugs, or a YAML list |
| `timezone` | Offset such as `UTC-5` or `UTC+05:30` |
| `sort` | `relevant`, `recent`, `salaryAsc`, `salaryDesc`, `nameAToZ`, `nameZToA`, or `jobs` |

The API also supports `page`, but the collector manages it. Use
`max_pages_per_query` for the default ceiling and optional `max_pages` inside a
query to override that ceiling. Every query must include at least one actual
filter; `sort` alone is not enough.

## Pagination and rate limiting

Search pages are 1-based. Requests are sequential and queries are paginated
round-robin. A query stops when the API returns no jobs, its `totalCount` has
been reached, a page is shorter than the response's `limit`, or its configured
maximum page count is reached. Search page size is controlled by Himalayas; the
collector does not send the browse endpoint's `limit` parameter.

HTTP `429` and server errors are retried up to three total attempts with the
same 1-second then 2-second backoff used by the other public-feed collectors.
Himalayas currently refreshes the API cache daily, so frequent polling provides
little benefit.

## Run

From the repository root:

```text
python run.py himalayas
```

In an editable installation, `job-intel himalayas` is equivalent. `python
run.py all` includes Himalayas automatically.

## Normalization and deduplication

`guid` is the source identifier when present; otherwise a stable hash of
`applicationLink` is used. The application URL is retained as the source URL,
the full HTML description is converted with the shared HTML-to-Markdown
converter, and Himalayas is recorded as the source. Country restrictions become
the common location value; an empty list becomes `Worldwide`. All Himalayas
jobs are marked remote.

Salary, expiry, categories, timezones, company identifiers, and the configured
queries that found a vacancy remain in the Himalayas source metadata. Duplicate
GUIDs returned by several queries are yielded once with every matching query in
`discovered_by`. The registry's exact source identity check makes repeated runs
idempotent.

An abbreviated stored `meta.yaml` source reference looks like:

```yaml
sources:
  - source: himalayas
    source_job_id: acme-senior-backend-engineer-123
    url: https://himalayas.app/jobs/acme/senior-backend-engineer
    metadata:
      company_slug: acme
      location_restrictions:
        - alpha2: IT
          name: Italy
          slug: italy
      salary:
        period: annual
        min: 70000
        max: 95000
        currency: EUR
      discovered_by:
        - query_index: 1
          parameters:
            q: backend engineer
            country: IT
            seniority: Senior
            sort: recent
```

The complete converted description is stored in that vacancy's `job.md`.

## Attribution and limitations

Keep the source URL and identify Himalayas as the original source when showing
these records. Himalayas asks API users not to submit its jobs to third-party job
boards; this collector only writes the user's private local registry and does
not redistribute listings.

The search endpoint controls page size and may rate-limit requests. Salary and
expiry data are optional, API data may be up to a day behind, and location
restrictions describe candidate eligibility rather than an office location.
