# European remote source expansion

Verified on 2026-10-10 for remote work from Rome with PHP/Go backend and hands-on technical leadership. A remote label does not establish Italy eligibility, work authorization or acceptable contract terms.

## Enabled collection

| Source | Interface | Per-run bound |
|---|---|---|
| WhiteTech | Public Greenhouse API | One board request; opted-in description geography |
| Hostaway | Public company careers HTML | One board and ten unique matching details |
| Remotive | Documented public JSON API | One request; at most 100 input records |
| Remote OK | Public JSON API | One request; at most 100 records including legal metadata |
| LaraJobs | Published RSS | One feed and at most five detail requests |

API/RSS pilots expire after **2026-10-24 inclusive, UTC**, then make no requests until explicitly extended. Responses are capped at 3 MB; timeouts at 30 seconds. JSON feeds do not fetch details. The existing six-hour schedule adds at most four feed requests per source/day; manual runs are additional requests.

Remotive advises at most four requests/day and delays API jobs by 24 hours. Remotive and Remote OK require attribution/linkback, retained in records and source URLs. Do not syndicate Remotive jobs to third-party aggregators or hide listings behind signup gates.

- [Remotive interface and terms](https://github.com/remotive-com/remote-jobs-api)
- [Remote OK feed and legal metadata](https://remoteok.com/api)
- [LaraJobs RSS](https://larajobs.com/feed)
- [WhiteTech careers](https://whitetech.com/careers)
- [Hostaway careers](https://careers.hostaway.com/)

## Filtering and identity

Pilot intake requires an original publication date within seven days, a relevant engineering title and compatible declared geography. Unknown dates/locations are excluded from pilot intake. Worldwide/Europe remains a regional signal; full prefilter and match analysis still check country, schedule and stack. Tags alone do not establish role relevance.

Short or missing descriptions are excluded. Eligible LaraJobs items can receive bounded detail requests because its RSS often omits the description. JavaScript-only employer pages with insufficient text remain excluded. Detail enrichment preserves the original RSS date. Errors and filter reasons are logged.

English does not cancel a mandatory unsupported language. Optional languages remain allowed. Text checks are screening heuristics, not proof of candidate fluency or hiring eligibility.

WhiteTech explicitly opts into description-based location filtering; other Greenhouse boards retain location/office-only filtering. Hostaway requires role-level Italy/Europe/EMEA evidence and keeps original JSON-LD dates. Its detail-page cap is configurable; repeated links are fetched once.

Cross-source deduplication also checks company and official role URLs, including stored application URLs. Recruitee /c/new suffixes and Greenhouse EU hostname aliases are normalized. Shared board URLs require matching titles; ambiguous URL matches remain separate. MongoDB batches prefetch URL owners with fingerprints and source identities. Upsert preserves existing status and history.

## Search channels awaiting a collection interface

- [JustJoin IT PHP](https://justjoin.it/job-offers/remote/php) and [Go](https://justjoin.it/job-offers/remote/go): country and mandatory Polish screening. Robots disallows /api/; no documented public read API/RSS verified.
- [No Fluff Jobs](https://nofluffjobs.com/remote/php): country, language and B2B/freelance screening. Robots disallows /api/; no documented public read API/RSS verified.
- [Welcome to the Jungle international](https://app.welcometothejungle.com/): check active employer postings and working hours; no stable collection interface verified.

These channels have **no enabled collector**. Do not use undocumented browser APIs or activate accounts/alerts for this expansion. Individual findings can follow manual intake; preparing/submitting applications remains separate.

[EU Remote Jobs terms](https://euremotejobs.com/tos/) prohibit scraping, systematic extraction and republication: no collector without provider permission. RemoteinEurope redirects to existing WeWorkRemotely coverage. EuropeanRemote and ReadyToTouch are employer discovery lists, not active vacancy feeds.

## Pilot evaluation

Compare canonical source-usage and vacancy reports: unique fresh Italy-compatible leads, current match quality, overlaps, requests, errors and missing-location/description exclusions. API size, tag hits and one empty run are not proof of useful yield or no market demand. Extend only useful sources or a defensible niche.
