# Arc email job alerts

Collect Go/PHP vacancy cards from `talent@arc.dev` using the connected Gmail tools,
including mail in Trash. Follow [the intake runbook](../../prompts/job-alert-import.md),
stage `.codex-work/job-alerts/arc.json`, then run `python run.py arc`.
`ARC_INPUT` may override the staging path. No input is a normal empty collection.

Only the exact sender is accepted. Titles and companies must appear in the original
mail. Descriptions must be continuous excerpts from the mail or the captured posting.
The subject of a recommendation digest
is not evidence of a card's technology, location or remote eligibility. Import only
cards that actually mention Go/Golang/PHP; keep absent facts unknown.

Arc `/t/remote-jobs/<slug>-<id>` and `/dashboard/d/remote-jobs/<id>` links are canonicalized by removing
tracking queries and fragments and retaining the stable posting ID. Account, search, unsubscribe, external and unresolved
SendGrid links are rejected. Never create a posting ID from a Gmail ID or a personal
tracking token. Relative ages such as `4 days ago` stay in the excerpt; do not invent
a publication date. Email previews retain `description_scope: email_excerpt`.

Raw mail remains ignored local staging. MongoDB and the existing registry pipeline
handle filtering and deduplication. This source does not scrape Arc or use a job API.

The user has authorized following job-card links and reading their postings. Run
`scripts/resolve_arc_alert_links.py` with `--allow-job-redirects` to resolve only
the approved SendGrid job links through bounded HEAD requests. Capture the rendered
job description with the connected browser; plain HTTP pages may contain only a
loading shell. Account, profile, application and unsubscribe links remain excluded.
Full captures use `description_scope: posting_text` with a content hash. If a posting
cannot be read, retain the verified email preview and its explicit excerpt scope.
