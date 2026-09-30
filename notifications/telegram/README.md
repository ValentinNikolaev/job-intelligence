# Telegram notification queue

Scheduled Codex analysis never sends Telegram messages directly. Successful batch
publication writes one validated JSON manifest to `outbox/` when at least one newly
analyzed vacancy has a score at or above `prepare_min_score` and is not a hard
rejection.

New manifests use schema version 2 and snapshot the explicit countries in each
vacancy's `location` as `country_codes`. Messages show up to five distinct flag
emoji before the company and title, in location order. Additional countries are
stored but not rendered. No icon downloads or external image hosting are needed.

Country names come from the local `pycountry` ISO database, including English,
Russian, Ukrainian, Italian, German, French, Spanish, Polish, and Portuguese names,
plus common aliases such as UK and USA. A location consisting entirely of uppercase
ISO country codes (for example `IT / DE`) is also supported. City-only locations,
unknown locations, and regions such as Remote, Worldwide, Europe, or EMEA do not
produce flags; the notifier does not infer country eligibility from the employer's
address or expand regions into countries. Version 1 manifests still validate with
their original hashes and render without flags.

The `Job Intelligence Telegram Delivery` GitHub Actions workflow sends each manifest
with repository secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. After confirmed
delivery it moves the manifest to `sent/`, stores a message fingerprint receipt in
`receipts/`, commits those acknowledgement files, and pushes `main`.

Delivery is at-least-once. The tracked receipt suppresses normal retries, but Telegram
does not provide an idempotency key, so a runner crash after Telegram accepts a message
and before the acknowledgement commit reaches GitHub can still produce a duplicate.
