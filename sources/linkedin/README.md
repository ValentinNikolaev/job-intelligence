# LinkedIn email Job Alerts

The [email intake workflow](../../prompts/job-alert-import.md) stages verified
Go/PHP cards from `jobalerts-noreply@linkedin.com` under the ignored
`.codex-work/job-alerts/linkedin.json`. Run `python run.py linkedin` after staging.
`LINKEDIN_INPUT` can override the input path. Missing input means no staged mail.

The collector accepts only numeric job-card routes under `/comm/jobs/view/` or
`/jobs/view/`. It canonicalizes the numeric ID locally, strips personal tracking
parameters, and does not follow mail links. Only exact title, company and card
text from the authenticated email enter the vacancy record. The description
scope is `email_excerpt`; absent publication date or work arrangement stays
unknown. Deduplication uses the stable posting ID through the normal pipeline.
