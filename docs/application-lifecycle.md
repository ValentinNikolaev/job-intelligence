# Application lifecycle and outcome measurement

Operational submission/outcome events live in MongoDB `operational_logs`, accessed
through the configured storage backend. There is no frozen-YAML fallback. Exact sent
files and validated ancillary documents are Git-managed under
`registry/application-history/<canonical-vacancy-id>/`; they survive vacancy archival.
Back up both MongoDB and this artifact directory. No lifecycle action changes a
vacancy's status: only the existing explicit `run.py status` command does that.

## Record what actually happened

```powershell
python run.py applications record-submission <vacancy> --submission-id <key> --sent-on YYYY-MM-DD --artifact <sent-cv> --artifact <sent-letter> --channel direct --positioning senior-backend --format compact --role-family backend --confirm-sent
python run.py applications verify-submission <vacancy> --submission-id <key>
python run.py applications record-event <vacancy> --submission-id <key> --event-id <key> --kind interview_invitation --occurred-on YYYY-MM-DD
python run.py applications report --as-of YYYY-MM-DD
python run.py applications followups --as-of YYYY-MM-DD
python run.py applications profile-questions
```

Only run record-submission after the user confirms what was sent and when. Preserve
exact file bytes, SHA-256, size, channel, positioning and format. Unknown labels remain
`not_provided`. Never treat generated documents as submitted applications. Reusing an
ID with conflicting data fails; an identical retry is idempotent. Events store their
recording timestamp separately from the observed event date.

Kinds include `auto_ack`, `human_reply`, `interview_invitation`, `interview`, `offer`,
`rejection`, `withdrawal`, and `followup_sent`. For employer messages use
`--note-file <verbatim-text>` and `--note-origin employer_message`. User descriptions
use `user_description`; do not invent employer wording. Rejections must also satisfy
the existing feedback-file and manual-status audit contract; complete that explicit
status flow first, then record the linked outcome. Silence is never a rejection.

Reports use confirmed submissions as the denominator. Auto-acknowledgments do not
count as human replies or invitations. They show counts, descriptive confidence
intervals, awaiting/censored applications and response timing. Channel, role family,
positioning and format breakdowns are observational: selection, timing, company and
role can confound comparisons. No automatic strategy or score-threshold change follows
from a small segment. A later rejection does not erase an earlier interview.

Follow-up output is a read-only schedule. It uses configurable spacing/maximum counts
and suppresses follow-ups after a response or terminal outcome. The schedule does not
create a scheduled task, send a message, or mark follow-ups sent. Respect an employer's
stated timeline and any instruction not to follow up.

## Named-vacancy ancillary drafts

After explicit approval for the vacancy and requested activity, Codex follows
`prompts/application-lifecycle.md` and writes a JSON draft. Publish it with:

```powershell
python run.py applications publish-draft <vacancy> --kind answers --draft .codex-work/answers.json --approved-vacancy <same-vacancy>
```

Kinds are `answers`, `interview-practice`, `interview-debrief`, and `followup`. Outputs
include JSON, Markdown and plain text. The argument records the explicit selection;
it does not replace the requirement to obtain actual user authorization in the task.
No activity is generated merely because a vacancy URL was supplied.

A draft has `schema_version: 1`, canonical `vacancy_id`, `kind`,
`grounding_review: true`, and an `items` list. Each item contains `prompt`, `text`,
`status: confirmed|needs_confirmation`, and evidence through `sources` or a known
`profile_field`. Sources are required for confirmed items without a profile field.
A source contains `path`, raw
file `sha256`, and exact `quote`; candidate sources must remain under
`registry/candidate/`. User-supplied source text under `.codex-work/` must be explicitly
marked `kind: user_statement`; generated material cannot impersonate user statements.
For profile facts, `profile_field` names the exact dot path in
`config/application-profile.yaml`; a confirmed answer must match the known configured
scalar. TODO_CONFIRM values can only be confirmation items. Do not guess right-to-work,
sponsorship, salary, availability, language proficiency or production experience.
