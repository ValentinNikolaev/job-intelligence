# Interview Preparation — SlotCatalog: Senior PHP Developer

SlotCatalog positions itself as "a leading intelligence and data platform in the
online casino industry," serving both players and industry stakeholders with
performance insights and large-scale structured data, and is now expanding into
regulated markets, direct media sales, and AI-powered tools. The posting's tone is
blunt about fit: they explicitly rule out candidates who need detailed tickets or have
never owned features after release, so treat ownership and outcome-thinking as the
central theme of every answer.

## Recruiter / HR Screening

Expect confirmation of the practical basics: remote setup, English communication level
(the posting states "English C1-C2 is a must"), and whether you're comfortable being
"fully accountable for what goes to production." Be ready to describe your current
availability honestly, and to speak plainly about your English level rather than
assume it's assumed. Since the company frames itself around real production impact,
expect an early question about a time you owned something after release, not just
built it.

## Culture Fit / Behavioral Interview

The posting's "Not a Fit If" section is unusually explicit: no fit for developers who
need step-by-step tickets, avoid legacy or complex code, or have never owned features
after release. Your strongest answer here is the CRURATED event-analytics pipeline:
you took full technical ownership of the DataLake and event-analytics platform in
production, architected the event-driven system yourself using queues and EventBridge,
and kept it operating reliably (event delivery reliability above 99.9%) rather than
handing it off after the initial build. Pair that with the airSlate story: you
personally reduced peak load on the main database by removing bottlenecks and
redistributing workload, and troubleshot production issues directly from logs,
monitoring, and SRE dashboards rather than waiting for an escalation from someone else.

## Technical Interview

Expect deep questions on PHP 8, Laravel/Symfony, PostgreSQL/MySQL, and REST APIs under
real traffic. Walk through the CRURATED event schema decision: why a versioned event
schema was necessary to keep new event types consistent across teams, and how the
modular design let you cut new analytics-stream setup time from several days to under
4 hours. Be ready to go deep on the Laravel/Symfony-based product-wide logger package
you built at airSlate, since that is your most direct, concrete Laravel/Symfony
artifact. For the database bottleneck story, be specific about the diagnostic process:
what you looked at first, how you identified the bottleneck, and how you redistributed
workload without downtime. You do not have verified experience with the specific
Filament (v5) admin-panel builder the posting names — be honest about that rather than
implying familiarity, while noting your broader PHP admin/backend tooling experience.

## CV Deep-Dive Questions

Expect a question about the CRURATED engagement's structure: it runs concurrently with
your Simple.life role as a part-time PHP subcontract/consulting engagement, not a
second full-time job — be ready to explain how you balance both and how much of your
time CRURATED actually represents. Expect a question on the Crutrade integration
specifically: you took full technical ownership of it in production, including
authentication/OTP, account linking, and collection import/export — be ready to name
one concrete technical decision in that integration, not just the list of features.
Expect a question about why your recent Simple.life work is Go-based while this role
is PHP-only: be honest that Simple.life is a Go platform, and that your PHP depth
comes from CRURATED, airSlate, and Hyprr running in parallel or in sequence with it.

## Company-Specific Preparation

SlotCatalog's stated direction — regulated markets, direct media sales, and
"AI-powered tools" — connects naturally to your CRURATED and Simple.life work turning
raw operational data into reliable, observable pipelines. Since the posting emphasizes
SEO and "large-scale structured data," be ready to talk about data reliability and
throughput (the 10x DataLake throughput increase) rather than only feature delivery.
The posting does not name the exact regulated markets or AI initiatives, so use the
recruiter screen to learn specifics before the technical rounds.

## Preparation Plan

1. Rehearse the CRURATED event-analytics ownership story end to end: problem,
   architecture decision (EventBridge/queues), the versioned event schema, and the
   99.9% reliability outcome.
2. Rehearse the airSlate database-bottleneck and SRE-troubleshooting stories with
   specific technical detail, since production ownership under pressure is the
   posting's clearest theme.
3. Prepare an honest, short answer on the Filament (v5) gap and on the CRURATED/
   Simple.life concurrent-engagement structure, since both are likely probe points.
4. Confirm your current English proficiency level in plain terms before the call,
   since the posting states it as a hard C1-C2 requirement.

## Questions to Ask

- "What does 'expanding into regulated markets' look like technically — new
  compliance requirements on the backend, or mostly business/legal work?"
- "How is the PHP backend team structured today, and who owns architecture decisions
  day to day?"
- "What does 'AI-powered tools' mean concretely for this team's roadmap?"
- "What does production on-call or incident response look like in practice here?"
