# Arbeitnow collector

Arbeitnow exposes a free public European job feed at
`https://www.arbeitnow.com/api/job-board-api`. It requires no account, API key,
or authentication.

## Run

From the repository root:

```text
python run.py arbeitnow
```

Jobs are normalized and upserted through the shared registry into
`registry/jobs/<vacancy>/`; the generated overview is `registry/index.md`.
Repeated runs use Arbeitnow's stable `slug` (or a deterministic hash of the job
URL when no slug is present), so they update the same vacancy rather than create
a duplicate.

## Configuration

Edit `sources/arbeitnow/config.yaml`:

```yaml
version: 1
max_pages: 5
timeout_seconds: 30
visa_sponsorship: null
```

- `max_pages`: positive integer page limit, or `null` to continue until the API
  returns an empty page or no next link.
- `timeout_seconds`: positive HTTP timeout in seconds.
- `visa_sponsorship`: `true`, `false`, or `null`. A non-null value is sent as
  the API's documented `visa_sponsorship` query parameter.

Set `ARBEITNOW_CONFIG` in `sources/.env` only if you need to use a different
configuration file.

## Pagination and data

The collector starts at the public endpoint and follows the URL in
`links.next`, matching the API's actual response envelope. It stops at the
configured page limit, an empty `data` list, or a null next link. Repeated or
off-domain pagination URLs fail the collection clearly instead of looping or
fetching an unexpected host.

The full available description is converted from HTML to the registry's
Markdown format. The original Arbeitnow job URL is retained. Useful feed-only
fields (`tags` and `job_types`) are kept in source metadata. Arbeitnow is a feed,
so keyword and location criteria are not sent as invented API parameters; any
common downstream filtering remains outside this collector.

Transient HTTP failures, rate limiting (`429`), connection failures, and
timeouts are retried up to three times with the repository's exponential
backoff convention. Invalid JSON and invalid response/pagination shapes fail
immediately with source and page context.
