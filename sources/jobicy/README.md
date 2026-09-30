# Jobicy collector

Jobicy is primarily a remote-job source. This collector calls the public,
keyless endpoint:

```text
GET https://jobicy.com/api/v2/remote-jobs
```

## Configuration

Edit `sources/jobicy/config.yaml`:

```yaml
version: 1
timeout_seconds: 30
queries:
  - geo: italy
    industry: dev
    count: 100
  - geo: emea
    tag: golang
    count: 100
```

Each entry is a separate request and supports `count`, `geo`, `industry`, and
`tag`. `count` must be from 1 through 100. The collector deliberately does not
hard-code or validate Jobicy taxonomy values: `geo` and `industry` slugs are
passed through unchanged, so confirm them against Jobicy's current taxonomy.
`tag` is Jobicy's title-and-description keyword search.

To use another config file, set `JOBICY_CONFIG` in `sources/.env`.

## Run

```text
python run.py jobicy
```

No API key is required. A run makes one request per configured query, then
deduplicates overlapping results by Jobicy job ID before storage. The original
Jobicy URL and full description are retained; HTML descriptions are converted
with the repository's common HTML-to-Markdown converter. Salary, industry,
level, excerpt, and company-logo data are stored in source metadata.

Jobicy says frequent polling is unnecessary and asks clients not to check its
feed more than once per hour. For personal search, run this collector only a
few times per day. It has no internal scheduler and does not retry or loop on
API failures.
