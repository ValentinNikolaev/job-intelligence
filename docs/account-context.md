# Single-account execution contract

Phase 5 introduces explicit account selection while retaining one live account and
the existing data layout. Follow the [migration plan](multiaccount-migration-plan.md)
for implementation and release status. The descriptor, resolver and operational
entrypoint integration are implemented in
[PR 4](https://github.com/ValentinNikolaev/job-intelligence/pull/4). Independent
reviews, full-suite verification and published-checkout/CI evidence are recorded
in the plan before phase acceptance.

## Ownership and supported layout

`config/accounts.yaml` describes the `current` account. It references existing
configuration owners rather than copying their contents:

| Descriptor reference | Existing owner |
| --- | --- |
| Selection policy | `config/selection-policy.yaml` |
| Match preferences | `config/matching-policy.yaml` |
| Candidate, preparation sources, evidence and career settings | `config/application-profile.yaml` |
| Voice source paths | `config/application-review.yaml` |
| Shared editorial guidance | `config/cv-editorial-knowledge.yaml` |
| Model routing and workflow limits | `config/codex-workflows.yaml` |
| Storage and Google destinations, schedules | `config/data-services.yaml` |

Schema 1 supports exactly `current` as both registered account and default. Its
reference names and canonical relative locations are pinned. Unsupported references
must be rejected; they are not customization options. The supported paths remain
`sources`, `registry`, `catalog`, `archives`, `notifications/telegram`, `.codex-work`
and the default credential file `sources/.env`. No data is moved and no MongoDB
field, index, database, adapter, transaction or lease migration is introduced.

The existing preparation-profile flexibility remains supported, including its
configured candidate/evidence paths and voice-source contract. These settings are
not duplicated in the account descriptor. Secrets and destination values remain in
their existing owners; the account context does not contain credential values.

## Selection and validation contract

The command contract accepts `--account current` and `--account=current`
before or after the command. Resolution uses an explicit selector, then process
`JOBINTEL_ACCOUNT`, then the descriptor default. If CLI and process environment
explicitly disagree, the command fails rather than choosing between them. Conflicting
repeated flags, blank or unknown values also fail. Account-specific dotenv files
cannot select an account.

Resolve a coherent project root before loading its descriptor. A supplied context
must belong to that root and still match its authoritative descriptor. Unsupported
registry/source layouts, traversal and pinned-path symlink/junction redirection
must fail, including redirection elsewhere inside the same root. Canonicalizing a
symlink to the project root itself does not change its account identity.
Missing or invalid descriptors must never redirect an operation to the executable
checkout or a parent project's defaults.

Validation may read the descriptor and inspect path metadata. Runtime dependency
bootstrap may precede the account gate. The gate must precede operational dotenv,
candidate/payload reads, storage access, timing writes, locks, dispatch and output.
Offline commands retain lazy credential loading. For storage resources, an explicit
external `--env` overlays the selected account's default dotenv; process values win
over both. A partial explicit file therefore preserves default MongoDB URI/database
values it does not override. Source collectors retain their existing explicit-file
configuration semantics. A credential-file override cannot change the account or
data root. File-loaded credentials do not persist in `os.environ` after an operation.

An account label is a routing contract, not a semantic freshness input. Unchanged
effective policy/profile inputs must retain their matching and preparation identities.
Storage caches must remain scoped to resolved root, URI digest and database. Repository
publication and provider quotas continue to protect their actual shared resources.
The standalone control-plane gate `python -m jobintel.accounts --account current`
validates the descriptor before operational automation starts; an explicit
`--project-root` may identify a complete isolated project root.

```text
python -m jobintel.accounts --account current
python run.py --account current list
python run.py list --account=current
python run.py --project-root <complete-project-root> list --account current
```

Existing commands without a selector use `current`. A legacy `--registry` or
`--sources` override must match that selected root's canonical path. To operate
on a complete isolated project, select its root explicitly; combining external
records with executable-checkout policies is no longer supported. Leaf CLIs and
operational scripts use the same argument resolver. Normal dependency bootstrap
uses the executable checkout; direct scripts also load their code from their own
checkout rather than an unrelated editable installation.

## Entrypoint inventory and required checks

The following inventory defines the implemented boundaries and their acceptance
checks. Each operational boundary consumes a validated context or independently
resolves its explicit root before effects. Exact observed verification remains
recorded separately in the migration execution log.

| Boundary | Required account/resource ownership | Verification |
| --- | --- | --- |
| `run.py`, console CLI and timing wrapper | Resolve before timing and subsidiary dispatch; coherent root and registry/source overrides | Default/CLI/environment parity; rejected selection reaches no handler or timing writer |
| Storage CLI and bridge | Same root for data-services, environment and cached store; no post-cutover file fallback | Distinct roots/destinations, sequential credentials, poisoned-YAML and transaction/lease checks |
| Sheets CLI | Explicit context root for destination and `.codex-work` files, replacing independent cwd lookup | Foreign cwd cannot change destination; foreign paths rejected; unchanged export/plan/request output |
| Applications, documents, evidence, timing and editorial CLIs | Validate standalone calls and supplied context before resource access | Invalid/missing/foreign context sentinels; existing grounding and quality checks |
| Workflow API snapshot operations | Validate operational root before storage or account configuration reads | Current-account parity and invalid-context rejection |
| Archive script | Validate explicit project root before policy load, lock or archive access | Unknown selection before effects; original archive rules and MongoDB preservation |
| Notification and outbox delivery scripts | Bind payload, delivery state and destination credentials to the same context before reads/sends | Early rejection; containment; existing duplicate/receipt behavior |
| Restored-backup verification | Separate source credential authority from restored-project/test-database authority | Legacy backup compatibility, isolated restore and no source writes |
| Operational GitHub Actions | Explicit current-account environment and validation before operational probes/grants | Checked-in workflow contract checks; existing schedules and cleanup retained |
| Scheduled analysis, selected preparation, mail, Sheets, backup and source benchmark | Existing default resolves current; explicit current-account environment may be supplied | Inspect checked-in commands and retain explicit external-env requirements |
| Reviewed repository finalizer | Shared repository publication, not an account-selected destination | Existing isolation, complete-tree, concurrency and non-force publication checks |

Outbox delivery retains its existing path flags, confined to the selected account's
`notifications/telegram/outbox`, `sent` and `receipts` locations. It rejects a foreign
payload or delivery-state destination before reading or sending. Explicit document
conversion/validation inputs keep their previous behavior; this account contract
does not prohibit every external input to a pure document tool. Existing evidence,
preview and publication containment/grounding gates remain effective.

Restored backups are explicit comparison inputs. Their catalog reader receives the
already verified isolated test store; it does not discover source-account credentials,
repoint ambient process environment, or add account descriptors to legacy archives.

Pure path-explicit policy loaders, validators, hashing, normalization, document
conversion and Sheets builders do not select accounts. Bare unconfigured filesystem
primitives remain usable for isolated fixtures. Neither exception authorizes an
account-selecting operational entrypoint to bypass a missing descriptor. Atlas
grant/revoke is shared infrastructure operating on explicit infrastructure credentials;
its always-run revoke cleanup must remain available. Account-aware Actions validate
before granting access. Project-bound match evaluators remain read-only consumers of
the fixed current project's policy; fully explicit evaluator inputs select artifacts,
not an operational account. Their existing semantic/binding checks remain required.

Checked-in prompt/workflow inspection does not prove deployed Scheduled Task settings.
No deployed automation settings are changed as part of repository implementation.

## Remaining source and editorial limits

The current source bundle retains its Go/PHP/Italy-oriented discovery filters,
including source-module relevance rules listed in the
[rule inventory](multiaccount-rule-inventory.md). Schema 1 does not promise a
candidate-independent source bundle. Configure those preferences or explicitly
review the supported source set before broader onboarding.

The Zend-credential exclusion belongs to the current candidate's editorial contract.
Existing enforcement in the generic prompt and validator stays effective for the
sole supported account. This decision does not make it a universal rule for future
candidates. Another candidate requires extraction or an explicit reviewed ownership
decision and the required editorial evaluation before onboarding.

Phase 6 remains responsible for a second live account, isolated operational
destinations and end-to-end cross-account verification.

The [second-account rollout and recovery checklist](second-account-rollout.md)
records future provisioning, activation and recovery gates. Schema 1 cannot onboard
a second account; a reviewed phase-6 contract extension must precede registration.
The checklist does not authorize deployment or changes to live automation.
