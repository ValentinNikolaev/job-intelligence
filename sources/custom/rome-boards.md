# Rome-office company boards

Verified on 2026-10-05 (Europe/Rome). All 20 companies are configured once in
`config.yaml`; the custom registry now has 80 sources. Office presence and job
location are separate facts. No Rome-only eligibility filter is configured.

The live check fetched 13 named advertisements across 12 companies: 8 were
created in canonical MongoDB and 5 rejected by the existing shared prefilter.
These counts include a focused TocToc recheck after adding its hyphenated PHP
URL term. The other 19 configurations were unchanged. Five boards failed at
HTTP/TLS access; three accessible boards had no named target-stack vacancy.
Access failures are reported, not bypassed. Undated/evergreen text is preserved
without inventing a publication date or asserting a fresh opening.

On 2026-10-09, Laser Romae, Polis-net and Molecole passed HTTPS verification
with the certifi CA bundle. The TLS failures below describe the original
2026-10-05 check, not their current access state. Immobiliare remains HTTP 403.

| Company | Careers page | Extraction | Live result / limitation |
|---|---|---|---|
| Immobiliare.it | [Careers](https://www.immobiliare.it/info/lavora-con-noi/) | target-stack links / JSON-LD | 0; HTTP 403 |
| Laser Romae | [Careers](https://careers.laserromae.it/jobs) | target-stack links / JSON-LD | 0; expired TLS certificate |
| Proxima Group | [Careers](https://proximagroup.eu/join-pro/) | target-stack links / JSON-LD | 0; placeholder/filter text only |
| TocToc | [Careers](https://www.toctoc.me/lavora-con-noi/) | linked PHP detail | 1 advertisement; publication date unconfirmed |
| Polis-net | [Careers](https://www.polis-net.it/entra-in-polis-net/) | specific role heading | 0; expired TLS certificate |
| ESIS Italia | [Careers](https://www.esis-italia.com/lavora-con-noi/) | linked PHP detail | 1 advertisement; publication date unconfirmed |
| IPTSAT | [Careers](https://www.iptsat.com/lavora-con-noi/) | target-stack links / JSON-LD | 0; general candidature only |
| GEB Software | [Careers](https://www.gebsoftware.com/lavora-con-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed |
| Tecninf | [Careers](https://www.tecninf.it/lavora-con-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed |
| Jarvis Farm | [Careers](https://www.jarvisfarm.it/lavora-con-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed; mixed Java EE and PHP requirements |
| Labica | [Careers](https://www.labica.it/content/ricerca-personale-php-mvc-mvvm-mvp-flutter-cordova-ionic-csharp-visual-studio-analista-programmatore-roma-smartworking) | target-stack links / JSON-LD | 0; HTTP 404 |
| DIYticket | [Careers](https://www.diyticket.it/jobs) | bounded named-role seed | 1 advertisement; publication date unconfirmed; actual title Sviluppatore FrontEnd |
| Aryon Solutions | [Careers](https://www.aryonsolutions.it/lavora-con-noi/) | target-stack links / JSON-LD | 0; PHP appears in a form selector only |
| Tun2U | [Careers](https://www.tun2u.it/contatti/) | bounded named-role seed | 2 advertisements; undated |
| Molecole | [Careers](https://www.molecole.com/lavora/) | specific role heading | 0; expired TLS certificate |
| NOIS3 | [Careers](https://www.nois3.it/lavora-con-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed; freelance, fully remote |
| Next Adv | [Careers](https://www.nextadv.it/lavora-con-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed |
| Mdesigner | [Careers](https://www.mdesigner.it/lavora-con-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed |
| Area SX | [Careers](https://www.areasx.com/index.php?D=1&page=curricula.php) | bounded named-role seed | 1 advertisement; publication date unconfirmed |
| Gruppo FOS | [Careers](https://www.gruppofos.it/lavora-noi/) | bounded named-role seed | 1 advertisement; publication date unconfirmed; PHP/Python role in Genova |

The visible source descriptions remain authoritative. In particular:

- Laser Romae has a Rome office. Its Go Developer posting lists Milan in the
  header but Rome (hybrid) in the body, so the role location is contradictory.
  [Office](https://www.laserromae.it/dove-siamo/) and
  [careers board](https://careers.laserromae.it/jobs) support separate facts.
  A 2026-10-05 diagnostic snapshot of the linked job pages shows `Pubblicata
  28 di Maggio` for Go Developer and `Pubblicata 9 di Febbraio` for Back End
  Developer in Rome, with no publication year. Both exceed the seven-day
  freshness window even under the latest possible non-future year. The Bizneo
  parser now records these dates and their year inference for the shared prefilter.
  HTTPS verification succeeds with certifi as of 2026-10-09; the old vacancy
  dates still fail the freshness filter.
- Gruppo FOS has a [Rome office](https://www.gruppofos.it/contatti/), while
  its PHP/Python Junior Software Developer advertisement specifies Genova.
  Its bounded seed excludes Java and Rome listings elsewhere on the board.
- Proxima's placeholder headings, IPTSAT's general application, and Aryon's
  JAVA/PHP form option do not establish current target-stack vacancies.
- Labica's historic careers URL now returns 404; its redesigned site exposes
  no verified replacement careers page. The original endpoint is retained for
  audit but disabled after rechecking on 2026-10-09; no generic company page is
  substituted for a hiring source.
- GEB, DIYticket, Tun2U and Molecole advertise old PHP/CMS stacks without dates.
  Polis-net mentions 2018-2019 projects. These are undated employer leads; shared
  role/stack filters can exclude them from the candidate's active queue.

## Adzuna Italy verification

The existing Adzuna source now retains only its three Italian backend/lead/
engineering-manager profiles. Six non-Italian expansion profiles were removed;
the request ceiling and other title/stack/freshness settings remain unchanged.
The normal collection made three successful Italian API requests and returned
zero relevant advertisements. A separate one-request diagnostic (`country: it`,
`what: php`, latest seven days, five results) returned five Italian locations,
including Rome; all five supplied redirect URLs used `www.adzuna.it`.
Diagnostic rows were not published as candidate matches or new search profiles.

Requests use the [official search API](https://developer.adzuna.com/docs/search)
on `api.adzuna.com`; vacancy links preserve its `redirect_url` and tracking
parameters. No HTML scraper or duplicate custom Adzuna source was added.
