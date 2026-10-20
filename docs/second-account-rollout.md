# Second-account rollout and recovery checklist

Second-account onboarding is unsupported by schema 1. The current resolver accepts
exactly `current`, its pinned references and its canonical paths. Registering another
account or redirecting those paths requires a reviewed phase-6 schema and execution
contract extension first. This checklist prepares that future decision; it does not
enable another account or authorize deployment, collection, analysis, delivery or
changes to deployed automation.

The [single-account contract](account-context.md) is authoritative for supported
commands today. The [migration plan](multiaccount-migration-plan.md) owns phase
status and execution evidence. All future checklist items below remain gates, not
claims that onboarding or isolation has already passed.

## 1. Establish the supported baseline

- [ ] Record the reviewed code revision and current-account descriptor/configuration
  versions without copying credential values. Confirm the first account remains
  operational and identify its owner and recovery contact.
- [ ] Inventory actual deployed Scheduled Tasks and GitHub Actions: code revision,
  working directory, project root, selector, environment-secret references,
  destinations, schedule/timezone, concurrency and responsible operator. Checked-in
  prompts and workflows do not establish deployed settings. Deployed Scheduled Task
  settings are unverified by this stabilization increment and require separate review.
- [ ] Record a proposed activation scope, resource limits, stop conditions and an
  owner for recovery. Obtain separate explicit authorization before changing deployed
  settings or enabling second-account operations.

The following existing command validates the selected root's descriptor and path
metadata without accessing operational storage, credentials or candidate evidence:

```text
python -m jobintel.accounts --account current
```

Run it from the intended reviewed checkout with an absent or matching
`JOBINTEL_ACCOUNT`. For an already complete isolated root, the supported form is
`python -m jobintel.accounts --project-root <complete-project-root> --account current`.
A CLI/environment conflict must fail; do not weaken that guard to make a probe pass.
This gate validates schema-1 selection and paths, not credential permissions,
resource isolation or a complete deployment. No second-account command is supported
or prescribed here.

## 2. Review the phase-6 contract before provisioning

- [ ] Specify and review the schema, account selection and configuration ownership
  extension before adding an account entry. Retain early rejection of unknown,
  conflicting, stale or redirected contexts. Do not treat current pinned paths as
  configurable alternate layouts.
- [ ] Choose separate executions/environments of the same reviewed codebase and a
  separate operational destination under the existing storage contract. Define the
  deployment mechanism explicitly. This checklist does not require MongoDB account
  fields, new indexes or a migration of the current database.
- [ ] Define the boundary between account routing and access control. An account
  label selects resources; it is not a login identity or permission grant. Provision
  deployment credentials and destination permissions independently, with only the
  access required by the chosen operation.
- [ ] Review source ownership against the [rule inventory](multiaccount-rule-inventory.md).
  Current Go/PHP/Italy discovery filters and source-module relevance rules must be
  configured or explicitly approved for the second candidate's supported source set.
- [ ] Review the current candidate's Zend-credential exclusion and other editorial
  ownership constraints before reuse. Extract candidate-specific rules or record a
  reviewed ownership decision. Before changing application prompts or editorial
  policy, run the blind corpus workflow in
  [the editorial evaluation contract](../prompts/editorial-evaluation.md).

## 3. Prepare isolated resources and verified evidence

- [ ] Obtain explicit authorization to add the second candidate's verified source
  material. Treat those sources as immutable evidence; derive candidate-specific
  evidence banks, career settings and voice settings from them. Do not copy claims
  from the first candidate or use unverified, retracted or cannot-confirm entries.
- [ ] Record the owner and concrete isolated destination for each resource below.
  Provision only after the reviewed contract supports it; keep secrets outside
  tracked configuration and evidence receipts.

| Resource | Required ownership decision |
| --- | --- |
| Runtime and deployment | Separate process environment, reviewed code revision, project root, task/Actions configuration and schedule |
| Storage | Separate operational destination and its credential authority, backups and recovery scope |
| Candidate and policy inputs | Verified sources, evidence banks, matching/selection preferences, preparation and voice configuration |
| Local outputs | Isolated records, artifacts, drafts, catalogs, archives and export paths |
| External outputs | Separate Sheets/Drive destinations and reviewed access permissions |
| Notification delivery | Intended recipient/destination plus isolated outbox, sent state and delivery receipts |
| Coordination | Locks and leases scoped to the actual protected resource, including any shared repository |
| Capacity | Per-execution budgets and aggregate provider quotas when credentials are shared |

- [ ] Verify credential precedence with synthetic values first: process values must
  agree with the intended account routing; dotenv files cannot select an account.
  An explicit credential file must not redirect data roots. Do not print credentials.
- [ ] Record backups and revision/high-water evidence for each destination before
  first activation, together with an independently verified isolated-restore method.
  Keep restore targets separate from source-account storage.
- [ ] Review publication ownership. Git is a shared resource even when runtime data
  is isolated. Use the reviewed repository finalizer from an isolated managed
  worktree, inspect its complete diff, retain unrelated changes, and publish without
  force. Do not run it in the shared checkout or bypass it with direct tree/ref APIs.

## 4. Prove isolation before bounded activation

- [ ] Start with read-only configuration resolution and a synthetic stand using
  matching CLI/process selectors, explicit isolated roots and fixture-only
  credentials/destinations. Exercise real entrypoints and inspect resulting fixture
  artifacts. A second sentinel fixture must remain untouched.
- [ ] Block provider/model calls, message sends and production storage access in the
  stand. Verify rejected selectors reach no operational readers/writers. Separately
  test matching selection through successful operational handlers; rejection tests
  and help output do not prove those paths.
- [ ] Record evidence in the categories below. Do not turn static inspection or
  mocked transport success into a claim of live deployment verification.

| Evidence category | What it establishes | What it leaves unverified |
| --- | --- | --- |
| Real entrypoint on synthetic fixtures | Parsing, selection, routing and observed fixture behavior for the named command | Production configuration, live providers and deployed tasks |
| Fixture-only writes | Actual outputs and untouched sentinel resources within the stand | Cross-account production isolation |
| Mocked or blocked external boundary | Call contract or prevention of external effects | Successful delivery, provider availability and destination permissions |
| Static checked-in command audit | Declared arguments, selector/environment wiring and ordering | Actual deployed settings and successful execution |
| Deployed automation review | Only the settings and revision actually inspected in a separately authorized review | Uninspected tasks or unexecuted operational behavior |

- [ ] After the contract and synthetic gates pass, obtain explicit authorization for
  a bounded activation: chosen sources, destination, execution count, budgets and
  stop conditions. Validate deployment configuration read-only first; then perform
  bounded collection and analysis while keeping the first account operational.
  Model-dependent work runs inside Codex, never project model-API calls.
- [ ] Verify independent matches, statuses, history, artifacts and delivery state
  for the same source vacancy. Check exports, archives and isolated restoration.
  Application preparation still requires explicit named-vacancy approval; sending,
  submission, source changes and status changes retain their own authorization gates.
- [ ] Enable recurring execution or external delivery only after separate explicit
  activation authorization and evidence review. Observe a bounded first run and
  compare intended versus actual destinations, revisions and receipts. Record
  remaining unknowns rather than declaring all automation verified.

## 5. Stop, roll back or recover according to observed effects

Before any operational effects, stop the proposed activation and restore the reviewed
previous deployment/configuration through its normal controlled mechanism. Verify
that current-account routing remains intact. Revoke only newly provisioned access
that is confirmed unused and whose removal is authorized. Keep the decision record;
do not delete data or shared resources to make the environment appear unchanged.

After any write or possible delivery, treat the task as recovery, not merely code
rollback:

1. Stop further affected runs and delivery under the authorized operational stop
   procedure. Leave unrelated current-account operations intact where isolation is
   established; if the destination is uncertain, contain the affected writers first.
2. Preserve MongoDB records, history, revisions, application artifacts, outbox/sent
   state and delivery receipts. Record the code/configuration revision, execution IDs,
   affected destinations and last known successful operations without secrets.
3. Reconcile committed writes and external acknowledgements before resuming. Missing
   local receipt evidence does not prove a message was unsent. Do not reset duplicate
   guards or resend automatically when delivery is uncertain.
4. Verify backup/restore evidence in an isolated destination and assess compatibility
   before reverting executable code. A code rollback must not discard data written
   under the newer contract. Any corrective write or destructive recovery requires
   a separately reviewed, explicitly authorized plan.
5. Re-run read-only routing and consistency checks, then an explicitly authorized
   bounded recovery run. Record reconciled results and unresolved effects before
   restoring schedules or delivery.

Never restore frozen registry YAML over canonical MongoDB state, delete databases
or history as rollback, or blindly rerun collection to repair uncertain outcomes.
Do not infer employer rejection or change vacancy status from operational incidents.
