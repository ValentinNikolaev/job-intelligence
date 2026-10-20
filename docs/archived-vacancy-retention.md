# Historical vacancy ZIP retention

Recorded: 2026-10-20. Source tree: `9214cf28732ec712cba2c8e03520b6d0518c9d5d`.

The owner requested filesystem cleanup while explicitly retaining non-applied
vacancies in MongoDB. This change covers only historical ZIPs under `archives/`.
The generated catalog, active vacancy directories, application-history snapshots,
feedback, candidate evidence, source identities and all MongoDB records remain
outside the cleanup. MongoDB continues to own operational vacancy data.

## Retention decision

Keep complete archived vacancy directories when canonical application records
confirm a submission, including applications subsequently rejected or withdrawn.
Current `status: applied` alone is not a retention rule. Keep legacy records with
an `applied` history entry conservatively when canonical confirmation is absent;
do not turn that historical label into a confirmed submission or modify MongoDB.

Read-only database inspection found 38 confirmed application records for 37 distinct
vacancies, plus one application needing review. Four confirmed vacancies depend on
three historical ZIPs. Another six directories have legacy applied history but no
canonical application confirmation or manual-status audit event. Those six remain
explicitly unverified, rather than being deleted or silently treated as confirmed.

The scan checked 562 ZIPs, 71,617 metadata entries and all current archive locators
in vacancy legacy evidence, artifact manifests and application package links. No
archived feedback file was found; all separate feedback records are preserved.
All files in the ten retained directories keep their exact original member paths
and bytes. The four ZIP filenames also stay unchanged, preserving database and
package locators.

| Retained ZIP | Directories | Evidence | ZIP SHA-256 after compaction |
| --- | --- | --- | --- |
| [2026-08-01.zip](../archives/stale/2026-08-01.zip) | 6 | Legacy applied history, unverified | `e85f5291c8cf6839a50fd581a360f2a7f0a304686015024b4871bd120441a828` |
| [2026-08-09.zip](../archives/stale/2026-08-09.zip) | 1 | Confirmed Nord Security application | `3725161da0e1f3a9814de15f1fe90c7e51cd5d51f29055c64d668b9cc098d4a7` |
| [2026-08-10.zip](../archives/stale/2026-08-10.zip) | 2 | Confirmed Solidgate and Zfort Group applications | `d9064a800650b4b7a7e33fab8e3be39434ce1542d512288dfaa9523a6b5b7087` |
| [2026-08-19.zip](../archives/stale/2026-08-19.zip) | 1 | Confirmed CoinsPaid application | `02290f89adcb19def4682d8f87a12860ee32c0430c2a8960e1c926f952f9329d` |

The six legacy directories belong to Grafanalabs, ShippyPro, Jagaad, SparkFabrik,
Nord Security and Cubbit. Their original metadata and documents remain inside the
August 1 ZIP. Any later confirmation or deletion is a separate decision; this
cleanup does not change statuses or import them into MongoDB.

## Filesystem result and verification

The cleanup removes 558 ZIPs and compacts four: 239,092,512 bytes become
556,123 bytes, with ten vacancy directories and 150 original members retained.
This reduces checked-out archive files by about 99.77%. It does not purge Git
history or promise an equivalent reduction in Git object storage or clone size.
Original complete ZIPs remain recoverable from the source commit above.

Before mutation, every archive source and candidate replacement was hashed and
every resolved target checked to remain inside this worktree's `archives/`.
Independent pre-apply review approved all 562 source ZIP hashes and CRCs, all four
replacement ZIPs and every retained member's original path, size and SHA-256.
Post-apply verification passed all four ZIP CRC/hash checks and all 150 member
hashes. The actual backup compactor produces byte-identical payloads for all three
canonical-reference ZIPs before and after cleanup; all 36 archived application
artifact hashes match MongoDB, and all four archived package links resolve.

Existing migration, backup, lifecycle-backup and restored-backup checks ran 40 tests:
39 passed and one real-MongoDB restore test skipped because the disposable test URI
was not configured. This is not a passing integration check. Published PR CI must
run the full suite with its disposable replica set before handoff. This cleanup
changes data and documentation only; no runtime or test code changes.

No production backup, restore, database mutation, catalog regeneration or status
change was performed. Catalog inputs are unchanged. Independent final diff review,
reviewed publication, clean published verification and exact-head CI remain the
handoff gates; their results belong in the PR review record.
