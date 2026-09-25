# Interview Preparation — Recare Deutschland GmbH: Senior Backend Engineer (Go)

Recare is explicit that this is a senior individual-contributor role centered on
owning a domain inside their Go codebase, not a management track, in a small,
remote-first, written-communication-heavy team. Prepare to demonstrate real
architecture judgment and self-directed ownership, not just Go syntax fluency.

## Recruiter / HR Screening

Expect confirmation of the remote-first setup (Germany, Spain, Portugal, Italy,
Poland, France, Austria) and a check that a fully async, written-communication-heavy
workflow is genuinely appealing rather than a compromise. Be ready to state plainly
that recent work has been Go-first and production-facing (Simple.life), with earlier
architecture-ownership experience at Hyprr. Ask about team size and how the "step in
when your lead is away" responsibility actually gets exercised in practice.

## Culture Fit / Behavioral Interview

The posting explicitly wants someone "looking for a strong individual contributor
role rather than a path into people management" who still "supports and mentors
other engineers." The strongest story here is owning the Simple.life support
platform end to end: designing it, personally owning its operation under load of up
to three times the ordinary monthly ticket volume, and building the API
orchestration layer myself. Pair that with the Hyprr story: working directly with
the CTO to define the technology roadmap and owning microservice/serverless
architecture decisions as Technical Lead, which is direct evidence of contributing
to architecture decisions without being handed them.

## Technical Interview

Expect a deep system-design conversation, since the posting frames "own a domain
inside our core Go codebase" as central. Be ready to walk through the Simple.life
platform's design: why Go, how the Zendesk/Intercom/internal-service integration is
structured, and how the API orchestration layer routes and classifies tickets.
Expect questions on database performance, referencing the airSlate story: reducing
peak load on the main database by removing bottlenecks and redistributing workload.
Be candid that Postgres/GORM and CircleCI specifically are not separately confirmed
in the record, even though general SQL/database and CI/CD experience is well
evidenced — do not claim tool-specific familiarity beyond what is true. Expect a
question about AI-tool usage in daily engineering work, since the posting states the
company is "an AI company now" and expects genuine curiosity about it.

## CV Deep-Dive Questions

Expect a question about the shift from PHP-heavy roles toward a recent Go-focused
role — be ready to explain that PHP and Go have run in parallel across the career,
with Go increasingly central in the most recent, most senior-scoped work. Expect a
question about the CRURATED engagement's part-time, concurrent nature relative to
Simple.life — be ready to explain that clearly rather than let it look like an
unexplained overlap. Expect a question on what "mentoring" has actually looked like
day to day: the honest answer is that direct evidence in this package centers on
architecture leadership and team task-distribution (airSlate) rather than a named
mentoring program, so frame it as leadership-adjacent knowledge sharing rather than
overclaiming a formal mentoring track record.

## Company-Specific Preparation

Recare describes itself as "one of Germany's leading HealthTech companies,"
transforming hospital discharge management, and states it currently connects over
two thirds of all German hospitals with more than 650 rehabilitation clinics and
over 25,000 care and homecare providers. That scale is worth referencing directly
when discussing why the domain-ownership model appeals: a small team supporting
that much real-world infrastructure means individual ownership decisions matter a
great deal.

## Preparation Plan

1. Rehearse the Simple.life system-design walkthrough with specific technical
   detail: the Go backend's structure, the API orchestration layer, and operational
   ownership under peak load.
2. Rehearse the Hyprr architecture-ownership story with concrete detail on specific
   decisions made with the CTO, not just "helped define the roadmap."
3. Prepare a clear, honest answer on the PHP-to-Go balance and on the scope of past
   mentoring/knowledge-sharing work.
4. Prepare two or three specific questions about the Go codebase domain this hire
   would own, to ask during the recruiter screen.

## Additional Notes

Because Recare frames written communication as genuinely important for a fully
remote, async-first team, be ready to demonstrate that in the interview itself:
answer questions with the same structure and precision you would use in a written
design doc, rather than a purely verbal, free-associating style. The posting's
emphasis on "real time communication" alongside written skill suggests interviewers
will also watch for comfort thinking out loud under mild pressure, so practice
narrating a technical decision live rather than only preparing a polished written
answer.

## Questions to Ask

- "Which part of the Go codebase would I be taking ownership of first, and how is
  that decided?"
- "What does 'stepping in when your lead is away' look like in practice — how often,
  and for how long?"
- "How does the team use AI tooling day to day, beyond code generation?"
- "What does the current CI/testing setup catch versus what still needs a human
  reviewer?"
