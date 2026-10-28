# LinkedIn email Job Alerts

The [email intake workflow](../../prompts/job-alert-import.md) stages verified
Go/PHP cards from `jobalerts-noreply@linkedin.com` under the ignored
`.codex-work/job-alerts/linkedin.json`. Run `python run.py linkedin` after staging.
`LINKEDIN_INPUT` can override the input path. Missing input means no staged mail.

The collector accepts only numeric job-card routes under `/comm/jobs/view/` or
`/jobs/view/`. It canonicalizes the numeric ID locally, strips personal tracking
parameters, and does not follow mail links. The agent opens the canonical posting
in the in-app browser and stages its rendered `posting_text`. Both the email and
posting must contain the same title and company. Fields must be exact excerpts
of that posting. Its SHA-256 and `posting_text` scope are recorded. Without page
evidence the scope remains `email_excerpt`; absent publication dates stay unknown.

`Hybrid` is preserved in `source_metadata.remote_working`, with `remote=None`
rather than `True`. The shared selection policy's `location.hybrid_italy_only`
gate requires an explicit Italian country in the job location. Unknown country
does not qualify, and company text or EMEA hours cannot override the gate.
An explicit standalone Hybrid card label is retained even if the staging agent
omits `remote_working`. Unverified work arrangements stay unresolved in intake.
Deduplication uses the stable posting ID through the normal pipeline.
