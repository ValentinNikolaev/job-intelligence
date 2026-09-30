# Candidate-confirmed Simple.life telephony privacy details — 2026-09-27

The candidate supplied and confirmed the following details in this task. Preserve the
wording as direct candidate evidence. Internal ticket identifiers are evidence context,
not CV content.

## Attribution

Employer: Simple.life / Simple App  
Role: Software Developer  
Project: Outbound telephony platform on Amazon Connect, August–September 2026

## Context and ownership

Simple operates in the medical and health domain, including clinic callback requests;
every call carries PII and potentially PHI. The candidate owned the architecture and
backend end to end, authored the epic and design document and made the security
decisions. The work passed formal security sign-off (DEV-35381) and a BAA and
call-recording compliance review (DEV-35382), then reached production on 2026-09-25
with a three-person cross-functional team: backend, frontend and SRE.

## Verified privacy, access and audit design

- The customer phone number was resolved server-side, never returned by the API,
  rendered in the agent UI or written to logs; only a mask reached the browser. There
  was no number-reveal UI.
- The number passed to Amazon Connect as a contact attribute and was wiped by the
  contact flow before reaching the queue. It was purged from the Connect contact record
  by TTL (DEV-35427), leaving no long-lived AWS-side copy.
- Developer Tools were disabled on agent machines through MDM policy. Agent identity
  used an opaque Entra `oid`, not email; changing identity providers required one script
  and no PII was used as a key.
- Contact Lens recording and transcription required explicit customer consent in the
  flow: DTMF 1 granted consent, DTMF 2 or silence refused it. QA verified this behaviour
  in scenarios TC-C6, TC-C7 and TC-C8.
- Agents received only `support:call` through Entra L1 group membership. Diagnostics and
  agent-catalog administration used separate permissions. The backend received only the
  agent subject and a boolean, not permission names or group identifiers.
- Federation used AssumeRole and GetFederationToken without per-agent AWS accounts or a
  SAML application. The backend created Connect users lazily, deactivated them with
  DeleteUser and removed stale users by cron.
- Each call attempt linked the request, Connect contact and audit record. Call history
  and duration came from the contact record, not an agent-entered form.

## Lawful calling and delivery controls

- The backend scheduler enforced customer-timezone call windows, Sundays and public
  holidays, the do-not-call list and automatic withdrawal of queued callbacks on
  opt-out, window closure or hang. Amazon Connect retries were set to zero, so built-in
  retries could not bypass these controls.
- The call outcome was written to the existing Intercom ticket, with no duplicate ticket
  or duplicate PII record.
- The designed load was 10–20 calls a day per agent, up to 50. The flow called the agent
  first and played a whisper with the call reason before dialing the customer, avoiding
  customer dead air.
- The candidate authored a 30-scenario telephony QA checklist and run journal, completed
  four documented runs in two days before launch, and converted every finding into a
  ticket.
