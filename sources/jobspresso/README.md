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
