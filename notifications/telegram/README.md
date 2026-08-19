# Telegram notification queue

Scheduled Codex analysis never sends Telegram messages directly. Successful batch
publication writes one validated JSON manifest to `outbox/` when at least one newly
analyzed vacancy has a score at or above `prepare_min_score` and is not a hard
rejection.

The `Job Intelligence Telegram Delivery` GitHub Actions workflow sends each manifest
with repository secrets `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`. After confirmed
delivery it moves the manifest to `sent/`, stores a message fingerprint receipt in
`receipts/`, commits those acknowledgement files, and pushes `main`.

Delivery is at-least-once. The tracked receipt suppresses normal retries, but Telegram
does not provide an idempotency key, so a runner crash after Telegram accepts a message
and before the acknowledgement commit reaches GitHub can still produce a duplicate.
