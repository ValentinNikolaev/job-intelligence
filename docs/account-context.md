# Single-account execution contract

Phase 5 introduces explicit account selection while retaining one live account and
the existing data layout. Follow the [migration plan](multiaccount-migration-plan.md)
for implementation status. The first increment adds the descriptor and resolver;
runtime enforcement and the entrypoint checks below remain pending until recorded
as completed in that plan.

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

The planned command contract accepts `--account current` and `--account=current`
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
Offline commands must retain lazy credential loading. An explicit external `--env`
remains a credential-file override, with existing process-environment precedence;
it cannot change the account or data root. File-loaded credentials must not persist
in `os.environ` after an operation.

An account label is a routing contract, not a semantic freshness input. Unchanged
effective policy/profile inputs must retain their matching and preparation identities.
Storage caches must remain scoped to resolved root, URI digest and database. Repository
publication and provider quotas continue to protect their actual shared resources.
The standalone control-plane gate `python -m jobintel.accounts --account current`
validates the descriptor before operational automation starts; an explicit
`--project-root` may identify a complete isolated project root.

## Entrypoint inventory and required checks

The following is the implementation/review inventory, not a claim that wiring is
already complete. Each operational boundary must consume a validated context or
independently resolve its explicit root before effects.

| Boundary | Required account/resource ownership | Verification |
| --- | --- | --- |
| `run.py`, console CLI and timing wrapper | Resolve before timing and subsidiary dispatch; coherent root and registry/source overrides | Default/CLI/environment parity; rejected selection reaches no handler or timing writer |
| Storage CLI and bridge | Same root for data-services, environment and cached store; no post-cutover file fallback | Distinct roots/destinations, sequential credentials, poisoned-YAML and transaction/lease checks |
| Sheets CLI | Explicit context root for destination and `.codex-work` files, replacing independent cwd lookup | Foreign cwd/path rejection; unchanged export/plan/request output |
| Applications, documents, evidence, timing and editorial CLIs | Validate standalone calls and supplied context before resource access | Invalid/missing/foreign context sentinels; existing grounding and quality checks |
| Workflow API snapshot operations | Validate operational root before storage or account configuration reads | Current-account parity and invalid-context rejection |
| Archive script | Validate explicit project root before policy load, lock or archive access | Unknown selection before effects; original archive rules and MongoDB preservation |
| Notification and outbox delivery scripts | Bind payload, delivery state and destination credentials to the same context before reads/sends | Early rejection; containment; existing duplicate/receipt behavior |
| Restored-backup verification | Separate source credential authority from restored-project/test-database authority | Legacy backup compatibility, isolated restore and no source writes |
| Operational GitHub Actions | Explicit current-account environment and validation before operational probes/grants | Checked-in workflow contract checks; existing schedules and cleanup retained |
| Scheduled analysis, selected preparation, mail, Sheets, backup and source benchmark | Existing default resolves current; explicit current-account environment may be supplied | Inspect checked-in commands and retain explicit external-env requirements |
| Reviewed repository finalizer | Shared repository publication, not an account-selected destination | Existing isolation, complete-tree, concurrency and non-force publication checks |

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
