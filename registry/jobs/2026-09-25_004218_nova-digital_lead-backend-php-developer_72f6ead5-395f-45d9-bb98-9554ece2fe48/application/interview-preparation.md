# Interview Preparation — Nova Digital: Lead Backend PHP Developer

Nova Digital describes itself as the technological heart of the NOVA ecosystem, with
50+ million requests daily and 10+ million active users. The role sits in the R&D
department, whose mission is fast PoC-to-MVP validation followed by production
hardening, and it explicitly wants both PHP depth and demonstrated technical
leadership. Treat the "PoC speed vs. production rigor" balance as the central theme.

## Recruiter / HR Screening

Expect confirmation of language requirements (confident Ukrainian, English at B1) and
remote/location logistics ("full remote з будь-якого куточка України" or office work
in company hubs). Be ready to describe your current Ukrainian and English proficiency
plainly rather than assume it is obvious from your background. Since the team explicitly
values PoC/MVP speed, expect an early question about how quickly you can stand up a
working prototype from an idea.

## Culture Fit / Behavioral Interview

The posting explicitly asks for "успішний досвід управління командою або технічного
лідерства" (successful team management or technical leadership experience). Your
strongest story is Hyprr: as Technical Lead, you defined the technology roadmap
directly with the CTO, established the core PHP/Go/AWS/Kubernetes stack, and brought
the product from prototype to closed beta in under 6 months. Pair that with the
CRURATED story: you took full technical ownership of the DataLake/event-analytics
platform and the Crutrade integration in production, showing you can both lead and
personally execute.

## Technical Interview

Expect deep questions on PHP 7/8, Laravel/Symfony, PostgreSQL, RabbitMQ, and
event-driven or DDD-style architecture. Walk through the CRURATED architecture
decision: why queues and EventBridge, why a versioned event schema, and how that
increased data-lake throughput by more than 10x. Be ready to connect this to the
posting's own architecture-committee framing: describe how you would defend a similar
decision before a review body, not just execute it solo. For the AI-orientation
requirement, be candid: your strongest verified evidence is cross-functional
collaboration with Support Ops, Product, and AI teams on a production automation
platform, not hands-on LLM-API development itself — frame it as "designed the
API/architecture around an AI team's needs" rather than claiming direct LLM
integration work you have not had independently confirmed. GCP and on-premise
infrastructure are gaps against your AWS/Kubernetes background; acknowledge this
directly rather than implying GCP depth you do not have.

## CV Deep-Dive Questions

Expect a question about the CRURATED engagement's concurrent, part-time structure
alongside Simple.life — be ready to explain the time split honestly. Expect a
follow-up on the Hyprr roadmap story: name one specific technology or architecture
decision you and the CTO made, not just that a roadmap existed. Expect a question
about why your most recent full-time role (Simple.life) is Go-based rather than PHP:
be honest that your PHP depth in this window comes from the concurrent CRURATED
engagement plus your earlier airSlate and Hyprr history.

## Company-Specific Preparation

Nova Digital's stated scale (50+ million daily requests, 10+ million users) and its
R&D mission of PoC-to-production hardening connects directly to your CRURATED and
Hyprr stories: both involve taking something from an early, fast-moving stage to a
reliable production state. The posting does not name specific current PoC/MVP
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
3. Prepare an honest, specific answer distinguishing "cross-team AI collaboration" from
   "hands-on LLM API development," since the posting's AI-orientation ask is broader
   than your most direct evidence.
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
