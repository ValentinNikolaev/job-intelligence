# Wellfound source status

Wellfound was evaluated for automated collection on 2026-08-18. It has public
job and role pages, but no supported public jobs API or RSS feed was found.
Wellfound's current terms restrict automated scraping and harvesting, so this
repository intentionally does not install a `collector.py` that would bypass
that boundary.

A future collector requires written permission or a documented, licensed feed
from Wellfound. Once available, it should use the numeric vacancy ID as
`source_job_id`, retain remote-eligibility geography, and be covered by offline
fixtures before it is enabled.

- Terms: https://wellfound.com/terms
- Robots policy: https://wellfound.com/robots.txt
