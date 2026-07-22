# Adzuna collector

The collector uses Adzuna's `GET /jobs/{country}/search/{page}` endpoint and
normalizes every returned advertisement into the common registry model.
Descriptions are snippets because that is all the search API returns.

## Configuration

Keep credentials in the ignored `sources/.env` file:

```dotenv
ADZUNA_APP_ID=your-app-id
ADZUNA_APP_KEY=your-app-key
```

Edit [`config.yaml`](config.yaml) to add searches. Each list item becomes one
independent Adzuna search; pagination is round-robin so every query gets a
first page before a broad query can consume the run budget.

```yaml
queries:
  - country: it
    what: "python developer"
    where: "Roma"
    max_days_old: 7
    sort_by: date
    full_time: true
    max_pages: 3
```

`country` must be one of the countries supported by Adzuna. A query needs at
least one of `what`, `what_and`, `what_phrase`, `what_or`, or `title_only`.
The collector accepts the search parameters from the official OpenAPI contract:

- text: `what`, `what_and`, `what_phrase`, `what_or`, `what_exclude`, `title_only`;
- location: `where`, `distance`, and `location0` through `location7`;
- filters: `max_days_old`, `category`, `salary_min`, `salary_max`, `company`;
- flags: `salary_include_unknown`, `full_time`, `part_time`, `contract`, `permanent`;
- ordering: `sort_by` and `sort_dir`.

Use YAML `true` for enabled flags and omit disabled flags. `ADZUNA_CONFIG` can
point to a different YAML file if separate search profiles are needed.

Run only this source with:

```powershell
python run.py adzuna
```

## Request budget

As of 2026-07-22, Adzuna's published default limits are:

- 25 requests per minute;
- 250 requests per day;
- 1000 requests per week;
- 2500 requests per month.

Adzuna does not publish a separate hourly cap. The minute limit would allow a
short burst of 1500 requests/hour, but the daily limit would be exhausted after
250 requests, so that number is not a usable hourly budget.

For nine runs per workday (09:00 through 17:00), five workdays per week, and 22
workdays per month:

| Limit | Runs in period | Maximum requests/run |
|---|---:|---:|
| Daily: 250 | 9 | 27 |
| Weekly: 1000 | 45 | 22 |
| Monthly: 2500 | 198 | 12 |

The monthly quota is the binding constraint. The checked-in
`request_budget: 11` caps **all HTTP attempts, including retries**, at 99/day,
495/week, and 2178 in a 22-workday month. This leaves 322 monthly requests
(about 13%) for manual runs, longer months, and other Adzuna endpoints. The
budget is per process; do not run several collector processes concurrently
unless they coordinate a shared quota.

Official references:

- [Search endpoint and response example](https://developer.adzuna.com/docs/search)
- [Interactive OpenAPI documentation](https://developer.adzuna.com/activedocs/)
- [Terms and default API limits](https://developer.adzuna.com/docs/terms_of_service)

The terms also restrict ongoing commercial, government, and academic use after
the stated 14-day trial unless Adzuna grants consent or a licence. Check the
terms for the intended use before scheduling long-running collection.
