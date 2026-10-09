# We Work Remotely collector

We Work Remotely publishes official RSS category feeds and requires no API key.
Run the collector with `python run.py weworkremotely`.

Configure unique names and official HTTPS `.rss` URLs in `config.yaml`;
`WEWORKREMOTELY_CONFIG` may point to another local config. The collector reads
only those feeds and does not scrape job detail pages.

The default uses the official all-jobs feed, then filters for engineering titles
and explicit Go/Golang/PHP evidence. On 2026-10-09 the old all-programming feed
stopped at September 28, while the all-jobs feed included October 9 postings.
The seven-day window is a local freshness rule, not a service restriction.
A nonempty feed with no current publication dates raises an upstream freshness
error instead of reporting a successful empty collection. Empty feeds remain valid.

It splits `Company: Role`, preserves region/country/state restrictions, converts
the full feed description to Markdown, and records skills, categories, and feed
provenance. RSS GUIDs provide stable identity and duplicates across categories
are yielded once. Registry source references retain the original WWR posting
link for attribution.

Transient failures are retried up to three times. Invalid XML, unofficial feed
URLs, and incomplete items fail with feed/item context.
