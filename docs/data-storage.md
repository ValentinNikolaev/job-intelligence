# Operational storage, Sheets and recovery

`config/data-services.yaml` selects exactly one operational backend. `yaml` is the
temporary migration source; `mongodb` reads and writes only MongoDB. Connection
failure is an error, never a reason to consult old YAML. Once cutover is verified,
the application refuses a YAML override. Reverting Git does not roll back a database.

## Data ownership

MongoDB owns vacancy metadata, descriptions, current matches, triage, application
records, immutable status events, feedback and operational usage/audit logs. A vacancy
keeps its original UUID and directory. An application has a separate deterministic
ID anchored to a confirmed submission event, allowing repeat applications. Event IDs
are deterministic; effective dates and recording dates remain separate. Unknown
submission dates remain unknown. Automatic prefilter rejection is not an employer
decision. Contradictory submission evidence is reported for review, never repaired by
inventing a status or date.

Explicit confirmations without an earlier `applied` event are separate audit evidence.
The initial `registry/application-confirmations.yaml` records the owner's confirmation
for WhiteTech and CoinsPaid. MongoDB retains that evidence and links their existing
interview/rejection events to application records; it creates no synthetic status
transition and leaves unknown submission dates blank.

Source identity documents have unique `(source, source_job_id)` keys. Historical
conflicting owners remain explicit lists; collection refuses an ambiguous identity.
Fingerprint indexes are nonunique. Existing same-source parallel roles remain
separate, as do uncertain company/title matches. Archived identities and application
history are retained after their artifact directory is archived.

MongoDB archival is logical: it hides records from active queues and keeps their
original Git-managed artifacts in place. Only legacy YAML archival creates ZIPs and
removes directories. The initial migration retains historical ZIP data only for
confirmed submissions, as requested by the owner. Other archived vacancies and
prefilter records are excluded from the new database and backups; original ZIPs
remain untouched in Git. Required evidence and documents are extracted individually.
This prevents a failed
Git push from leaving database references to a ZIP that existed only on a runner.

Configs, candidate evidence and source discovery configuration remain YAML/Markdown
files. Application Markdown/DOCX, quality receipts and manifests remain Git-managed
artifacts, owned by their vacancy UUID and directory; MongoDB records their hashes.
Candidate evidence is immutable. Existing operational YAML is a frozen migration
source after cutover, not a second writable database. Catalog/index pages are derived
projections. The original job/profile/prompt hashes and model provenance are preserved.

All MongoDB writers use a common expiring lease and revision checks. Status and its
manual audit are in one transaction. MongoDB transactions require a replica set;
standalone MongoDB is not a supported substitute. Backup and migration use the same
lease. Filesystem and GitHub Actions locks alone cannot coordinate machines.

## Credentials and network

Store local `MONGODB_URI` in the ignored `sources/.env` or process environment. Store
the CI URI separately in the repository Actions secret `MONGODB_URI`. Use the plain
variable `JOBINTEL_DATABASE_NAME=job_intelligence`. GitHub secrets cannot be read back
as a local credential vault. Never place connection strings in arguments, logs, Git,
backup archives or prompts. Grant the runtime database user `readWrite` on this one
database rather than `atlasAdmin`.

For GitHub-hosted runners, the selected design creates a temporary runner IPv4 `/32`
Atlas database access entry and deletes only that run's entry in unconditional cleanup.
An expiry is a second cleanup safeguard. The management service account needs only
`Project Network Access Manager` in this project. Store `ATLAS_CLIENT_ID` and
`ATLAS_CLIENT_SECRET` as Actions secrets and `ATLAS_PROJECT_ID` as a variable.

The management API has its own IP restrictions. A dynamic runner cannot bootstrap
itself if that API rejects its address. The user must explicitly configure that access
or provide a stable network path before CI is enabled; the workflow must not widen
the database allowlist to `0.0.0.0/0`.

References: [Atlas service accounts](https://www.mongodb.com/docs/atlas/configure-api-access/),
[database IP access](https://www.mongodb.com/docs/atlas/security/ip-access-list/),
[temporary access entries](https://www.mongodb.com/docs/api/doc/atlas-admin-api-v2/operation/operation-creategroupaccesslistentry).

## Migration and rollback

1. Pause local scheduled writers and GitHub collection/archive workflows. Confirm
   no writer is running and the checkout matches the source Git revision.
2. Inventory live registries, historical submission evidence, manual history and
   verbatim feedback. Keep all current registry data and only confirmed submissions
   from archives. Build a deterministic plan with object hashes and exact evidence
   paths (`archive.zip!member` for archived evidence). Review ambiguity coverage.
3. Back up the source files and a separately timed Sheets snapshot. Upload and download
   through the Codex Google Drive connector and perform an isolated restore drill.
4. Import under the global lease with checkpoints. A rerun must be idempotent and
   reject different data for the same imported identity. Reconcile values, IDs,
   relationships, dates and hashes, not only counts.
5. Set MongoDB as the source only after reconciliation and the restore drill pass.
   Keep writers paused until runtime checks and network configuration are verified.

If import fails before cutover, leave YAML authoritative and resume the same checked
plan. After new MongoDB writes, reverting to old YAML is prohibited: first stop writers,
take a verified current backup and explicitly export/reconcile all intervening changes.
Never restore into production as part of a drill.

## Sheets and backup

The fixed spreadsheet and backup folder IDs live in `config/data-services.yaml`.
`prompts/google-sheets-sync.md` and `prompts/database-backup.md` are the canonical
scheduled instructions. Only Codex uses the connected Google Drive plugin. Project
code prepares plans/checksums/receipts and never calls Google APIs; GitHub Actions has
no Google credentials.

Each confirmed application with a complete four-document package is one row keyed by hidden `application_id`; the visible vacancy ID connects it to internal resources. User notes,
contacts, next actions and due dates belong to the user. Sorting rows is safe because
each run reads IDs again. System status changes use `python run.py status`, not sheet
edits. Duplicate IDs, newer/conflicting revisions and changed immutable events stop
sync. External content is written as literal strings. A no-op changes no cells or
timestamps. Actual writes require exact readback verification.

Backups preserve all required collections/indexes, status/feedback, vacancy artifacts,
selected historical submission evidence and independently timestamped Sheets manual
fields. Old ZIPs are never copied wholesale. Manifests include
schema, source Git revision, UTC time, object counts, sizes and SHA-256. Files and DB
data are captured within the global writer exclusion window; Sheets is a separate
snapshot. Every delivered backup is downloaded, verified and restored into an isolated
database. No retention deletion is enabled. Upload retry uses the same backup ID and
verified manifest instead of creating duplicate copies.

Atlas Free counts uncompressed BSON and indexes against its 0.5 GB quota. Free/Flex do
not support `mongodump --oplog` / `mongorestore --oplogReplay`, so this design uses the
shared write exclusion window. Measure actual data and indexes before choosing a tier;
no paid plan is enabled automatically. [Atlas limits](https://www.mongodb.com/docs/atlas/reference/free-shared-limitations/).

Schedules use `gpt-5.6-terra`, reasoning `medium`: Sheets daily 09:00/19:00 Europe/Rome;
backup every three calendar days at 09:30 anchored after the first verified delivery.
They stay disabled until the required first-run checks pass. Local schedules require
the computer to be on and the application running. They notify only for errors,
conflicts, overdue backups or required user action.

## Cutover evidence (2026-09-21 UTC)

The production import into `job_intelligence` was reconciled at
`2026-09-21T23:14:10Z`: 79 vacancies (76 current and three archive-only), 305 current
prefilter records, 376 source identities, 104 status events, 21 application records,
20 artifact manifests, one feedback record and four operational logs. A second
import inserted nothing; the ID, value and hash reconciliation had no differences.
Measured BSON data was 4,122,274 bytes, with 110,592 bytes of indexes.

The [application sheet](https://docs.google.com/spreadsheets/d/1E82sr4Lt-3yEB0Kb_Amso9NCMThcsF0Sy9x7ma5S848/edit)
contains 20 confirmed applications and 24 linked history events. Blackbird remains
`needs_review` in storage because its evidence explicitly says the external form
was not submitted. It is excluded from confirmed applications. Coverage is limited
to the repository's historical evidence and explicit owner confirmations; unknown
submission dates remain blank.

The verified pre-cutover backup is
`20260921T230713Z-c7b5c819622c4316b7b103e5f6d858d5`.
Its [restore receipt](https://drive.google.com/file/d/1Va7SBMK-T-_aGWC3v-Sm2K7kqd8rOvQg/view)
records exact reconciliation, 1,340 restored files, 76 catalog entries and the same
20-application/24-event export. The first MongoDB backup successfully restored from
Drive is `20260921T232730Z-e7b733a5407542d0bab850abbe7fe013`
([downloaded-copy restore receipt](https://drive.google.com/file/d/12rc5sg8_B84CEsAd-QpFxvOUhIl97UkN/view)):
911 operational documents,
seven non-primary indexes and 1,340 restored files. Both deliveries verified all
1,341 payload objects. Exact restored document/index hashes matched, all references
resolved, and catalog/export checks reproduced 76 vacancies and 20 applications.
Subsequent delivery and scheduled-run receipts are kept in
the [backup folder](https://drive.google.com/drive/folders/1wsfd-IzS9viLGaU7y3dpQWrGryGyKPTP).
Files prefixed `FAILED-restore-check-` are diagnostic attempts and must never be used
as successful recovery points.

GitHub Actions remains the collection scheduler. The redundant local Codex
collection task is disabled; scheduled Codex analysis uses the same MongoDB source.
Sheets and backup schedules are separate from analysis and preparation policy.

## Application history artifacts

Application lifecycle events use MongoDB operational_logs records keyed
`application-lifecycle:<vacancy-id>`. These contain confirmed submission metadata and
observed events, separate from vacancy status. Exact submitted file snapshots and
validated follow-through drafts live under `registry/application-history/<vacancy-id>/`
as Git-managed artifacts. Keep this directory in full-repository backups and restores;
never derive a sent version from a subsequently regenerated package. Evidence banks
under `registry/evidence/` are derived indexes of immutable candidate sources, not
canonical operational vacancy records.

Backup verification checks lifecycle submission receipts and exact snapshot bytes
against their MongoDB records and requires them in the backup payload. Missing or
tampered sent files fail backup validation.
