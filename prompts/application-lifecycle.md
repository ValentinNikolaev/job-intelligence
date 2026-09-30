# Approved application follow-through

Use with `$job-intelligence-workflow` only after the user explicitly requests the
activity for one named vacancy. A URL or analyzed match alone does not authorize these
artifacts. This prompt does not send messages, submit applications, infer vacancy
status, or authorize scheduled reminders. Read `docs/application-lifecycle.md` for
commands and the JSON publication contract. Read the configured current MongoDB vacancy
context; never use frozen registry YAML as live vacancy input.

## Form answers

Read the selected vacancy, actual form questions/limits, final selected CV, verified
candidate evidence and application profile. Answer the question asked within its
character/word limit; prefer plain text suitable for pasting. Keep right-to-work,
sponsorship, location, availability and compensation consistent with known profile
fields. Run `applications profile-questions` to identify unresolved facts. A value of
TODO_CONFIRM is not an answer. Collect material missing facts from the user; publish
unresolved entries only as needs_confirmation, visibly excluded from paste-ready text.
Do not manufacture metrics, production experience, salary flexibility or relocation
preferences. Reference candidate sources, not earlier generated answers.

## Interview practice

Use the approved vacancy, selected round, final CV, verified story bank and role-specific
preparation. Ask one question at a time; wait for the user's answer, then ask a relevant
follow-up before giving focused feedback. Evaluate specificity, ownership, technical
tradeoffs, evidence and relevance to the role. Track reused stories and weak answers.
Suggest a clearer version only within confirmed facts; do not script invented personal
experience. Preserve the actual user's answer as a user_statement input before saving
a session item. Ask the user to supply missing facts neutrally, including the option
that a metric cannot be confirmed. Do not automatically promote a practice answer into
verified candidate evidence.

## Interview debrief

Use the user's supplied transcript or recollection. Record which it is. Capture the
questions, actual answers, known feedback and concrete follow-up preparation. Separate
observations from interpretations of interviewer reactions. Preserve contradictions
and previously retracted claims; repeated generated text is not confirmation. Update
neither the immutable source CV nor vacancy status from a debrief. Save only the
requested selected-vacancy artifact with source provenance.

## Follow-up draft

Read the confirmed submission and subsequent events. Respect employer timelines,
terminal outcomes and requests not to contact them. A read-only `applications followups`
report suggests timing; it is not approval to draft or send. When explicitly asked,
write a short contextual message using the exact role and factual submission date,
with one grounded reason for continued interest. Do not claim a relationship, prior
conversation, completed interview or new achievement without evidence. No sending.

## Publication and outcome recording

Write a JSON draft under `.codex-work/` using the documented schema. Each confirmed
claim needs exact source text/hash or an exact known profile scalar. User statements
must be text genuinely supplied by the user; never create a source file containing a
model invention and label it user_statement. Complete grounding review before setting
`grounding_review: true`. Publish through `applications publish-draft <vacancy>` with
`--approved-vacancy` matching the actual selection. This explicit argument records the
selection; it cannot substitute for approval in the task.

Record submissions only after the user confirms the exact sent files and date; archive
the actual files, not regenerated substitutes. Record human replies and interview
invitations separately from auto-acknowledgments. Rejection handling preserves the full
message through the existing feedback/status flow first. Outcome reporting never
changes strategy, scores or statuses automatically. Suggest experiments only after
reporting sample size, follow-up time and confounding factors.
