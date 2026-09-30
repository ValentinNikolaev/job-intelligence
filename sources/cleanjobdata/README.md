# CleanJobData collector

The CleanJobData collector calls `GET https://api.cleanjobdata.com/jobs` and
normalizes each returned listing into the shared registry model. It requests
`extra_fields=description` on list calls, so it stores full descriptions without
spending extra requests on `/jobs/:id`.

## Credentials

For local runs, keep the bearer token in the ignored `sources/.env` file:

```dotenv
CLEANJOBDATA_API_KEY=your-api-key
```

Scheduled tasks should provide `CLEANJOBDATA_API_KEY` as an environment secret.
`CLEANJOBDATA_CONFIG` can point to a different YAML configuration file.

## Search profiles

Edit `sources/cleanjobdata/config.yaml`. Every enabled profile needs a unique
`name` and at least one of `search`, `title`, `company_name`, or `employer_id`.

```yaml
request_budget: 4
limit: 20
extra_fields:
  - description

search_profiles:
  - name: backend-italy
    search: "senior backend engineer"
    location: "IT"
    max_age: "7d"
    sort_by: relevance
    max_pages: 1

  - name: saved-but-disabled
    enabled: false
    search: "staff engineer"
    remote: true
```

Supported profile fields map directly to CleanJobData query parameters:

| YAML field | Notes |
|---|---|
| `search`, `title`, `sort_by` | Text search and ordering. Use `relevance` only with a search/title. |
| `city_id`, `state_id`, `country_id`, `location` | Geographic filters. `location` uses comma-separated ISO2 country codes. |
| `remote`, `remote_type` | Remote-only and remote-type filters. |
| `company_name`, `employer_id`, `company_website_url`, `domain` | Company and application-domain filters. |
| `salary`, `min_salary`, `require_salary` | Compensation filters. |
| `experience_level`, `employment_type` | Comma-separated taxonomy values from CleanJobData. |
| `published_after`, `max_age`, `created_max_age`, `include_expired` | Freshness and active/expired filters. |
| `limit`, `max_pages`, `extra_fields` | Local pagination and field-selection controls. |

The collector uses cursor pagination and fetches profiles round-robin so broad
searches do not consume the whole per-run budget before narrower searches run.
Duplicate CleanJobData IDs returned by overlapping profiles are yielded once per
run.

## Request budget

The free trial tier communicated for this benchmark allows 250 `/jobs` requests
per month and a rate limit of 1 request per second. The checked-in
`request_budget: 4` is a conservative per-run guard, and retries also consume
that budget. The collector enforces `min_request_interval_seconds: 1` between
HTTP attempts.

Run only this source with:

```powershell
python run.py cleanjobdata
```
