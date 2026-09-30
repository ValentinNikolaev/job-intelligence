# Ashby collector

Ashby exposes public company job boards at
`https://jobs.ashbyhq.com/{board}` and a public, unauthenticated postings API at
`https://api.ashbyhq.com/posting-api/job-board/{board}`. This collector uses only
that public API; it does not use recruiter/employer APIs and needs no Ashby
account or API key.

## Board registry

Known boards are stored in [`config.yaml`](config.yaml):

```yaml
version: 1
timeout_seconds: 30
filters:
  remote_only: true
  location_terms: [Italy, Germany, Netherlands, Europe]
  title_terms: [backend, software engineer, platform engineer]
boards:
  - name: satispay
    company: Satispay
```

`name` is the first path segment after `jobs.ashbyhq.com`. `company` is optional,
but adding the display name is recommended because the public API does not
consistently return one. If omitted, the stable board identifier is used as the
company value required by the common job model.

Ashby boards return every listed vacancy for a company. Optional global `filters`
keep the registry focused without changing the upstream request:

- `remote_only: true` accepts jobs marked by Ashby as remote through `isRemote`
  or `workplaceType`;
- `location_terms` performs a case-insensitive match against primary and secondary
  Ashby locations;
- `title_terms` performs a case-insensitive match against the job title.

An empty or omitted term list disables that filter. Discovery preserves the
configured filters when it adds another board.

To add a board manually, append it to `boards`. To validate and add one or more
board names or job URLs automatically, run:

```text
python run.py ashby discover satispay
python run.py ashby discover https://jobs.ashbyhq.com/docker/some-job-id kong
```

Discovery extracts and normalizes the first URL path segment, deduplicates it,
and calls the public board endpoint. Only a response containing an Ashby `jobs`
list is accepted. Discovery stores boards only; it never stores individual jobs
and it does not use a search engine.

Set `ASHBY_CONFIG` in `sources/.env` only if the board registry is kept at a
different path.

## Collect

Run every registered board with:

```text
python run.py ashby
```

Every request includes `includeCompensation=true`. Listed jobs are normalized
into the common registry, while `isListed: false` jobs are ignored. The original
job URL is the source URL. Application URL, board, department, team, workplace
type, secondary locations, and compensation are retained under that source's
`metadata` mapping in `meta.yaml`. `descriptionPlain` is preferred for `job.md`;
HTML is converted to Markdown only when plain text is unavailable.

A failed, removed, timed-out, or malformed board is logged and counted as an
error without preventing later boards from being collected. The command exits
non-zero when any board failed, following the common collector convention.

The collector performs a full public-board fetch on each run. Discovery sources
beyond manually supplied board names and URLs (for example, search results or
URLs observed in other collectors) can be added later without changing the
collector.
