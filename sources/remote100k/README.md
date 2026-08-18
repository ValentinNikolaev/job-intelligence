# Remote 100K source status

Remote 100K was evaluated for automated collection on 2026-08-18. Its public
site exposes vacancy pages, but no supported public RSS or jobs API was found.
The site's robots policy disallows its internal `/api/` routes, and its current
terms prohibit data mining, robots, and similar extraction. This repository
therefore does not install a scraper or call the internal API.

A future collector requires written permission or a documented, licensed feed
from Remote 100K. The stable source name will be `remote100k`.

- Terms: https://remote100k.com/legal/terms
- Robots policy: https://remote100k.com/robots.txt
