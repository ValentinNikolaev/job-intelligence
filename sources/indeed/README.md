# Indeed email Job Alert

This is an email-only source; it does not scrape Indeed or use a private API.
Use the [email intake workflow](../../prompts/job-alert-import.md) to stage actual
Job Alert or matching-job emails, then run `python run.py indeed`.

The input defaults to `.codex-work/job-alerts/indeed.json`, with an `INDEED_INPUT`
override. Accepted sender domains are `indeed.com`, `jobalert.indeed.com` and
`match.indeed.com`. Login, passkey, subscription activation and account emails
contain no importable posting and must be excluded by the intake task.

The collector accepts job links with a stable 16-character `jk`. For supported
`cts.indeed.com/v3` links, it decodes the embedded gzip destination offline and
validates that it is an Indeed vacancy. It never visits tracking, application,
unsubscribe or account links. Only the clean `https://it.indeed.com/viewjob?jk=...`
URL and posting ID enter the registry; personal tracking tokens are not stored.
Unsupported link formats need review, not a guessed URL or synthetic job ID.

Title, company and the vacancy excerpt must be present verbatim in the original
email body. Publication date is unknown when absent. Remote and hybrid labels are
preserved as evidence, with no assumption of full remote work. Registry storage
and deduplication use the existing pipeline. See the Reteinformaticalavoro source
README for the shared staging, privacy and fail-closed behavior.
