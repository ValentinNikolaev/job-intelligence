# Hacker News hiring collector

Uses the [documented HN Algolia search API](https://hn.algolia.com/api) to discover
the official `whoishiring` account's monthly **Who is hiring?** threads. It reads
only top-level employer comments, never the candidate-oriented **Who wants to be
hired?** thread or discussion replies. No account or credentials are needed.

The enabled pilot runs through 2026-10-29 inclusive, UTC, on the existing six-hour
collection schedule. It makes one discovery request and at most three comment
requests per thread, covering at most two months when the seven-day window crosses
a month boundary (seven requests maximum). Newest comments come first; pagination
truncation is logged. Each response is capped at 3 MB and 30 seconds. There are no
external job-page requests, retries, messages or application submissions.

Intake requires a relevant engineering title and explicit remote signal in the
employer's pipe-separated header, an original comment date within seven days,
regional geography compatible with Italy, and a substantial description. The
shared prefilter subsequently checks stack, language and working hours. Europe,
EMEA and worldwide are regional signals, not verified employment eligibility.
The source preserves the complete employer text, original header (including any
salary and contract wording), HN comment identity, thread URL and attribution.
One multi-role employer post stays one record; its hiring status is unverified.

Override the configuration path with `HACKERNEWS_CONFIG`. Run with
`python run.py hackernews --env <absolute-primary-env-path>`.
