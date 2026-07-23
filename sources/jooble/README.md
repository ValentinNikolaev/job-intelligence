# Jooble collector

The Jooble collector sends JSON `POST` requests to `https://jooble.org/api/{api_key}`,
normalizes the returned vacancies, and stores them through the shared registry.

## Credentials

For local runs, put the API key in the ignored `sources/.env` file:

```dotenv
JOOBLE_API_KEY=your-api-key
```

Scheduled CodexSandboxOnline runs should provide the same name as an environment secret
for the task or host. `JOOBLE_CONFIG` may optionally point to another YAML configuration file.

## Multiple query profiles

Edit `sources/jooble/config.yaml`. Every enabled profile needs a unique `name`,
`keywords`, and `location`:

```yaml
request_budget: 10
results_per_page: 50
max_pages_per_profile: 5

query_profiles:
  - name: backend-italy
    keywords: "python backend developer"
    location: "Italy"
    radius: "80"
    max_pages: 3

  - name: data-rome
    keywords: "data engineer"
    location: "Rome"
    salary: 40000
    search_mode: 0
    company_search: false
    results_per_page: 25
    max_pages: 2

  - name: saved-but-disabled
    enabled: false
    keywords: "platform engineer"
    location: "Milan"
```

Supported profile fields map to Jooble's API as follows:

| YAML field | Jooble field | Notes |
|---|---|---|
| `keywords` | `keywords` | Required |
| `location` | `location` | Required |
| `radius` | `radius` | `0`, `4`, `8`, `16`, `26`, `40`, or `80` km |
| `salary` | `salary` | Non-negative minimum salary |
| `search_mode` | `SearchMode` | Defaults to Jooble's mode `0` when omitted |
| `company_search` | `companysearch` | Search company names when `true` |
| `results_per_page` | `ResultOnPage` | Overrides the global value |
| `max_pages` | — | Local pagination cap for the profile |

Pagination is round-robin: page 1 of each profile is requested before page 2 of
any profile. Duplicate Jooble job IDs returned by overlapping profiles are yielded
only once per run.

## Request quota

The key-issuance message states a default limit of 500 requests and asks users to
contact Jooble to increase it. The public REST API documentation, last modified
26 May 2025, does not define whether that quota resets or over what interval.
`request_budget` is therefore a conservative per-run guard. Retries also consume
this budget. Set it according to the confirmed quota for the account.

## Run

```text
python run.py jooble
```

HTTP 429 and server errors are retried up to two times with exponential backoff.
Authentication failures stop immediately with a message that does not expose the
API key.
