# We Work Remotely collector

We Work Remotely publishes official RSS category feeds and requires no API key.
Run the collector with `python run.py weworkremotely`.

Configure unique names and official HTTPS `.rss` URLs in `config.yaml`;
`WEWORKREMOTELY_CONFIG` may point to another local config. The collector reads
only those feeds and does not scrape job detail pages.

It splits `Company: Role`, preserves region/country/state restrictions, converts
the full feed description to Markdown, and records skills, categories, and feed
provenance. RSS GUIDs provide stable identity and duplicates across categories
are yielded once. Registry source references retain the original WWR posting
link for attribution.

Transient failures are retried up to three times. Invalid XML, unofficial feed
URLs, and incomplete items fail with feed/item context.
