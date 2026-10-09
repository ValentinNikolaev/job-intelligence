# Jobspresso collector

Jobspresso publishes a public RSS feed at `https://jobspresso.co/jobs/feed/`.
The collector requires no account or API key. Run it with:

```text
python run.py jobspresso
```

`config.yaml` supports a positive `timeout_seconds`; `JOBSPRESSO_CONFIG` may
point to an alternate local config. The adapter makes exactly one request to
the latest-jobs feed: it does not add query-string pagination or scrape detail
pages. The feed therefore defines the collector's latest-vacancy scope.

The stable post ID identifies a listing, the full encoded body is converted to
Markdown, and `dc:creator` supplies company and location. Each registry source
reference retains the original Jobspresso link for attribution. GUID or a
canonical URL hash is used only when an older item omits its post ID.

Transient connection, rate-limit, and server failures are retried up to three
times. Invalid XML or incomplete items fail with feed/item context.

Cheap mode retains only target-stack engineering jobs published in the last
`max_age_days` (seven by default). This is our selection policy, not a Jobspresso
restriction. A nonempty feed whose newest publication is older than the window
now reports an explicit stale-source error. Missing publication dates also fail
clearly; an empty feed is still valid.

On 2026-10-09 the RSS, alternate official job feed, public listing endpoint, and
latest job's JSON-LD all still pointed to August 28/29 publications. Cache
revalidation did not reveal fresh jobs. Do not relabel old postings as new or
widen the window to conceal the upstream lack of updates. Collection will resume
automatically when the source publishes current entries.
