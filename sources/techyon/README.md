# Techyon

Collects public vacancies from https://www.techyon.it/candidati.html and follows
its pagination. No account or API key is required.

```text
python run.py techyon
```

The collector is discovered automatically by `python run.py all`. It reads the
full JobPosting JSON-LD from each detail page, including requirements, location,
posting date, and employment type when supplied. It excludes application forms
and newsletter text. Vacancy URL slugs provide stable source IDs; repeated links
are fetched once per run. Existing collection filters, cross-source deduplication,
MongoDB persistence, and API request accounting apply normally.

Techyon is a headhunter. The `company` field preserves the published
`hiringOrganization` (often Techyon SRL); it does not guess an anonymous client's
identity. The description retains the hiring-company context. Remote work stays
unknown unless the structured posting explicitly declares `TELECOMMUTE`.

Settings in `config.yaml` control the request timeout and maximum listing pages
(default 10). `TECHYON_CONFIG` can point to another config. Requests retry HTTP
429, server errors, and network timeouts up to three times. An initial listing
failure fails the collector; later page/card failures are logged and reported
as partial collection errors while valid records continue.
