# Interview Preparation — INFOBUS: PHP Developer (Support)

INFOBUS's own posting is very explicit that this role is about keeping existing
systems and partner integrations stable rather than building new features from
scratch, with a weekend duty rotation built in. Prepare to demonstrate calm,
methodical troubleshooting instincts and comfort with reactive support work, not
just PHP syntax knowledge.

## Recruiter / HR Screening

Expect confirmation of the practical basics: remote-work terms (not detailed in the
public posting), the weekend duty rotation ("one day of work on either Saturday or
Sunday, with one weekday off in return"), and PHP 7.4+/MySQL baseline knowledge. Be
ready to state plainly that recent work has combined production PHP ownership
(CRURATED) with Go-based backend ownership (Simple.life), so the PHP depth is
current, not years-stale. Ask directly about team size and how the on-call rotation
escalates when a partner integration breaks outside business hours.

## Culture Fit / Behavioral Interview

The posting values people who enjoy "troubleshooting, analyzing complex issues,
working with APIs and integrations, and improving existing systems" over people who
want to build new products. The strongest story here is taking full technical
ownership of the CRURATED Crutrade integration in production, covering authentication
and OTP, account linking, collection import/export, purchase-ownership verification,
and request/response logging end to end. Pair that with the airSlate story: reducing
peak load on the main database by removing bottlenecks and redistributing workload,
which is exactly the "stabilize rather than rebuild" mindset the posting describes.

## Technical Interview

Expect deep questions on diagnosing broken partner integrations: walk through how the
Crutrade authentication/OTP and account-linking flow was built and how issues would
be diagnosed using request/response logs. Be ready to explain the database work at
airSlate in technical terms: what made the peak load a problem, how bottlenecks were
identified, and what redistributing the workload actually meant in practice. Expect
questions on log analysis and monitoring tooling (the posting mentions Postman and
cURL specifically) — be candid that hands-on ownership of production troubleshooting
is well evidenced, but naming those exact tools is not separately confirmed in the
record, so don't overclaim familiarity with a specific tool beyond what is true.
Expect questions on SQL query optimization, JSON/XML handling in API payloads, and
how to communicate a technical root cause to a non-technical partner.

## CV Deep-Dive Questions

Expect a question on the CRURATED engagement's actual scope, since it was a
concurrent part-time subcontract alongside Simple.life, not a single full-time
role — be ready to explain that clearly rather than let it look like an
unexplained overlap. Expect a question on why the DataLake/event-analytics
ownership at CRURATED (30+ event types, 99.9%+ delivery reliability, sub-4-hour
stream onboarding) is relevant to a PHP-support role even though it centers on
analytics infrastructure: the honest answer is that it demonstrates the same
production-ownership and reliability instincts the INFOBUS role needs, applied to a
different domain. Expect a question on the shift from full-time PHP roles toward a
recent Go-focused role (Simple.life) — be ready to explain that PHP expertise has
stayed current throughout via the CRURATED subcontract rather than lapsing.

## Company-Specific Preparation

INFOBUS Holding was founded in 2002 and built its own online ticket-sales system,
BUSSYSTEM, now connecting more than 40 countries, 37,000 cities, 47,000 routes, 6,500
carriers, and over 10,000 points of sale. That scale means the partner-integration
surface is genuinely large and varied — a useful detail to bring up when discussing
why integration-support work at this scale is appealing rather than repetitive.

## Preparation Plan

1. Rehearse the Crutrade integration-ownership story with specific technical detail:
   the exact flows owned (auth/OTP, account linking, purchase verification) and how
   issues in each would surface in logs.
2. Rehearse the airSlate database-bottleneck story with concrete detail on diagnosis
   and the fix, since "database performance" is a stated core requirement.
3. Prepare a clear, honest one-line explanation of the CRURATED/Simple.life
   concurrent-engagement timeline before it comes up as a question.
4. Prepare two or three specific questions about the on-call escalation process and
   team structure to ask during the recruiter screen.

## Additional Notes

The posting frames this as a support-and-stabilization role for a company running a
high-volume, multi-country ticketing platform, so interviewers will likely probe for
patience and precision under pressure rather than raw feature-delivery speed. Lean
into examples where a fix required careful diagnosis before acting, not just a quick
patch, since that maps directly to the posting's emphasis on root-cause analysis
across logs, database queries, and partner API traffic.

## Questions to Ask

- "What does the weekend duty rotation look like in practice — how often, and what
  kind of issues typically come up during it?"
- "How many partner integrations does the team currently support, and how often do
  new partners get onboarded?"
- "What does the escalation path look like when a partner-reported issue can't be
  resolved during the on-call window?"
- "Is this role fully remote, and if so, are there any timezone-overlap
  expectations with the rest of the team?"
