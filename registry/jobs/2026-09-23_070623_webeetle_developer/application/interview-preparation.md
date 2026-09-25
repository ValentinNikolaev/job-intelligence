# Interview Preparation — weBeetle: Developer (Back-End)

weBeetle is hiring a Developer for an enterprise, microservices-focused development
team, on-site in Angri (SA), Italy or Split, Croatia, with smart working limited to 2-4
days per month. Two things will dominate this conversation beyond the technical
screen: your seniority relative to a posting that is explicitly open to junior
candidates, and your Italian language level given the mostly-on-site setup.

## Recruiter / HR Screening

Expect confirmation of the practical basics: which site (Angri or Split), the CCNL
COMMERCIO contract terms (14 monthly payments, meal vouchers, training budget, company
bonus), and the onboarding tutor process. Be upfront early about two things: you are
still learning Italian, though your English is strong, and you have prior experience
working as a developer at an Italian company. Raising this yourself, rather than
waiting to be asked, signals honesty and lets the recruiter address it directly instead
of discovering it later. Also be ready to explain, briefly and positively, why a
15+-year senior engineer is interested in a role also open to junior profiles — frame
it around the team, the microservices focus, and genuine interest in the company's
stated culture of continuous learning.

## Culture Fit / Behavioral Interview

weBeetle describes wanting people who "danno valore alle relazioni, all'apprendimento
continuo" (value relationships and continuous learning) and who are willing to set
aside their own certainties. Your strongest story here is the CRURATED event-analytics
work: you architected and led the event schema and routing design, reaching event
delivery reliability above 99.9%, while working as part of a concurrent, part-time
subcontract engagement alongside your Simple.life role — a good example of disciplined,
self-managed ownership across two active engagements at once. Pair that with the
airSlate story: as Programming Team Lead you owned on-call operations, technical
onboarding, and interviewing new team members, showing you can operate in a mentoring
and team-building capacity, not just as an individual contributor.

## Technical Interview

Expect deep questions on microservices and event-driven architecture, since the posting
calls this out as the company's core technical focus. Walk through the CRURATED event
schema versioning work: why a versioned schema matters for consistency across teams,
and how the routing logic supports multiple downstream destinations (webhook, S3-style
targets) with delivery guarantees. Be ready to connect this to the posting's specific
mention of Kubernetes, Ambassador, Envoy, and Istio — your direct evidence is
Kubernetes/microservices architecture at Hyprr, so be honest that your service-mesh
tooling exposure (Ambassador/Envoy/Istio specifically) is not independently verified
and frame it as transferable systems-design knowledge rather than hands-on tool
experience. For the database side, use the airSlate story: reducing peak load on the
main database by removing bottlenecks and redistributing workload. Be candid that
MongoDB is not in your verified background, and that your event-driven experience is
PHP-based rather than Node.js-specific — both are honest, minor gaps against an
otherwise strong match.

## CV Deep-Dive Questions

Expect a question about the CRURATED and Simple.life overlap: be precise that CRURATED
was a concurrent, part-time subcontract/consulting engagement running alongside your
full Simple.life role, not two competing full-time jobs. Expect a question probing the
airSlate "Programming Team Lead" title: be ready to describe the shift from
individual contribution to leading epic decomposition, task delegation, and on-call
ownership. Expect a direct question about your Italian level — answer with the same
honesty as in the cover letter: currently learning, strong English, prior experience at
an Italian company as a developer.

## Company-Specific Preparation

weBeetle frames itself around relationships, continuous learning, and questioning one's
own certainties, and runs an initial company-tutor onboarding phase for new hires. The
role sits inside an enterprise-focused, microservices-oriented development team, hiring
either a Front-End (React) or Back-End (PHP/Symfony/Node.js) Developer; your fit is
clearly the Back-End track. Use the tutor-onboarding detail as a genuine point of
interest — it suggests a company that invests in ramping people up properly, which is
directly relevant given your Italian is still developing.

## Preparation Plan

1. Rehearse the CRURATED event-schema and routing story end to end, including the
   99.9%+ delivery reliability result and the concurrent-engagement framing.
2. Rehearse the airSlate database-bottleneck and team-lead/on-call story.
3. Prepare a short, confident answer on why a senior engineer wants a role open to
   junior candidates, and a short, honest answer on your current Italian level.
4. Confirm before the call which site (Angri or Split) applies and how commute or
   relocation logistics from Rome would work in practice.

## Questions to Ask

- "Com'è strutturato il periodo iniziale di affiancamento con il tutor aziendale?"
  (How is the initial tutor-supported onboarding period structured?)
- "Quanto è vincolante la presenza in sede rispetto allo smart working di 2-4 giorni al
  mese?" (How strict is the on-site requirement compared to the 2-4 monthly remote
  days?)
- "In che lingua avvengono le comunicazioni quotidiane del team di sviluppo?" (What
  language does the development team use for day-to-day communication?)
- "Quali strumenti di orchestrazione dei microservizi usate concretamente — Kubernetes,
  Ambassador, Envoy, Istio?" (Which microservices orchestration tools do you actually
  use in practice?)
