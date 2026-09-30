# Interview Preparation — Nova Digital: Lead Backend PHP Developer

Nova Digital describes itself as the technological heart of the NOVA ecosystem, with
50+ million requests daily and 10+ million active users. The role sits in the R&D
department, whose mission is fast PoC-to-MVP validation followed by production
hardening, and it explicitly wants both PHP depth and demonstrated technical
leadership. Treat the "PoC speed vs. production rigor" balance as the central theme.

## Recruiter / HR Screening

Expect confirmation of language requirements (confident Ukrainian, English at B1) and
remote/location logistics (the registry says worldwide remote, while the posting says
remote from Ukraine or office work in company hubs). Clarify whether Rome is eligible.
Be ready to describe your current Ukrainian and English proficiency
plainly rather than assume it is obvious from your background. Since the team explicitly
values PoC/MVP speed, expect an early question about how quickly you can stand up a
working prototype from an idea. Have a factual notice-period and salary expectation
ready; neither is documented in the candidate sources.

## Culture Fit / Behavioral Interview

The posting explicitly asks for "успішний досвід управління командою або технічного
лідерства" (successful team management or technical leadership experience). Your
strongest story is Hyprr: as Technical Lead, you defined the technology roadmap
directly with the CTO, established the core PHP/Go/AWS/Kubernetes stack, and brought
the product from prototype to closed beta in under 6 months. Pair that with the
CRURATED story: you took full technical ownership of the DataLake/event-analytics
platform and the Crutrade integration in production, showing you can both lead and
personally execute. Prepare five distinct behavioral examples: a contested architecture
decision, a prototype you changed after feedback, a production failure you diagnosed,
a cross-team dependency you resolved, and a decision to simplify existing code. Use
the CRURATED schema/versioning work, Simple.life pipeline consolidation, and Hyprr
roadmap where the details fit; do not invent conflict or stakeholder reactions.

## Technical Interview

High priority: PHP 7/8, Laravel/Symfony, PostgreSQL, event-driven architecture and
the route from PoC to production. Walk through the CRURATED architecture
decision: why queues and EventBridge, why a versioned event schema, and how that
increased data-lake throughput by more than 10x. Be ready to connect this to the
posting's own architecture-committee framing: describe how you would defend a similar
decision before a review body, not just execute it solo. High priority for AI:
explain the Simple.life LLM support agent's action tools and evaluation pipeline,
including how conversation text, action events and subscription-state snapshots fed
evaluation JSON. This is hands-on backend work, not merely AI-team proximity.
Medium priority: Kubernetes/Docker, API contracts, service integration and queues;
distinguish the evidenced EventBridge work from the posting's RabbitMQ example.
Lower-evidence probes: gRPC, WebSockets, GCP and on-premise infrastructure. State
the boundary of experience clearly rather than substituting a neighboring tool.

## CV Deep-Dive Questions

Expect a question about the CRURATED engagement's concurrent, part-time structure
alongside Simple.life — be ready to explain the time split honestly. Expect a
follow-up on the Hyprr roadmap story: name one specific technology or architecture
decision you and the CTO made, not just that a roadmap existed. Expect a question
about why your most recent full-time role (Simple.life) is principally Go-based:
PHP was also in that role's technology mix, but no specific PHP achievement is
documented; current PHP delivery is evidenced by the concurrent CRURATED engagement.
Clarify the exact Simple.life end month and title if asked rather than silently
promoting the later block's conflicting Senior Backend Engineer title.

## Company-Specific Preparation

Nova Digital's stated scale (50+ million daily requests, 10+ million users) and its
R&D mission of PoC-to-production hardening connects to CRURATED's production
analytics pipeline, Hyprr's prototype-to-closed-beta product development, and the
Simple.life gateway that enabled a first B2B demo. These are different maturity
stages; do not call the Hyprr beta a proven production system. The posting does not name specific current PoC/MVP
projects, so use the recruiter screen to learn what the R&D team is actively building
before the technical rounds.

## Company-Specific Preparation (continued)

Since the posting is written entirely in Ukrainian and states Ukrainian fluency as a
requirement, expect at least part of the process to run in Ukrainian; rehearsing your
key technical stories in Ukrainian, not only English, will reduce the risk of
stumbling over vocabulary mid-interview. The posting's tone throughout is direct and
technical rather than marketing-heavy, which suggests the interviewers themselves are
likely to be engineers or an engineering-adjacent tech lead rather than a generalist
recruiter for the technical rounds.

## Preparation Plan

1. Rehearse the Hyprr technical-leadership story with one specific, concrete
   architecture or technology decision you and the CTO made together.
2. Rehearse the CRURATED event-driven architecture story, including the "why" behind
   queues/EventBridge and the versioned event schema.
3. Prepare a hands-on Simple.life LLM-agent example: one action tool, its evaluation
   data, and a production defect you fixed, while keeping unmeasured resolution-rate
   estimates out of the story.
4. Confirm your current Ukrainian and English proficiency levels in plain terms before
   the call.

## Questions to Ask

- "Які конкретні PoC чи MVP зараз у розробці у вашій R&D команді?" (What specific PoC
  or MVP projects is the R&D team currently building?)
- "Як виглядає взаємодія з командою AI-розробки на практиці — спільні спринти, окремі
  API-контракти?" (What does collaboration with the AI-development team look like in
  practice — shared sprints, separate API contracts?)
- "Наскільки часто рішення проходять через Архітектурний комітет, і як виглядає цей
  процес?" (How often do decisions go through the Architecture Committee, and what
  does that process look like?)
- "What does the split between GCP and on-premise infrastructure actually look like
  for this team's services?"
- "What evidence must a PoC show before the team funds and operates an MVP?"
- "Which production measures decide whether an R&D service is ready for handover?"
