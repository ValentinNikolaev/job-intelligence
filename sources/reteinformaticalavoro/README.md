# Reteinformaticalavoro Job Alert

This source imports vacancy excerpts from the user's Gmail Job Alert emails. It
does not fetch website pages, follow email links, or need site credentials.

Run the [email intake workflow](../../prompts/job-alert-import.md) in Codex to stage
an evidence-backed batch, then run `python run.py reteinformaticalavoro`.
The collector reads `.codex-work/job-alerts/reteinformaticalavoro.json` by default;
`RETEINFORMATICALAVORO_INPUT` overrides that path. Missing input means no staged
mail, not a network failure. An invalid supplied batch fails before any job is emitted.

The shared importer preserves the numeric `/lavoro/<id>/<slug>` posting identity,
strips tracking query strings, checks sender domains and exact email excerpts,
and retains Gmail message ID, receipt time and a body hash as provenance. Raw mail,
personalized links and account messages are never published to Git or copied into
vacancy metadata. Description scope is explicitly `email_excerpt`, not a full posting.
Unknown publication date and remote status stay unknown; receipt time is not the
vacancy publication date. `Parziale` remains recorded separately from `Totale`.

The ordinary collection pipeline handles MongoDB storage, cross-source deduplication,
prefilters and usage logging. No applications are submitted and no status is changed.
Public-feed collection in GitHub Actions cannot read Gmail: email staging belongs
to the separate authorized Codex daily task. First live email validation is pending
until an actual Job Alert arrives; account confirmation mail is not a fixture.
