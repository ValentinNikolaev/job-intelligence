# Lytvynov Production interview preparation

## Recruiter / HR Screening

Prepare to explain why a high-load social product and an agency-run client team interest you. State the confirmed five aggregate years in production Go without assigning them to a single employer. Explain Rome location, remote CET collaboration, the concurrent CRURATED consulting arrangement, English upper-intermediate and B2B entity status accurately. Confirm notice period and any requested contract details before giving a precise response. The posted salary range is an employer range; use the vacancy-specific compensation workflow before stating an expectation. Be ready to discuss the roughly six-hour test task and the client's technical interview.

## Culture Fit / Behavioral Interview

Likely prompts include how you handled an unclear service boundary, a deteriorating vendor API, a production deadline, a privacy decision, incident communication, a difference of opinion with a technical lead, balancing tests with delivery, mentoring a teammate and coordinating a remote cross-functional release. Choose grounded STAR stories from the Go gateway, shared Snowflake delivery engine, Amazon Connect release, CRURATED versioned event flow and airSlate database reliability. Explain which decisions were yours and which were team decisions. Avoid inventing traffic or customer numbers for these stories.

## Technical Interview

High Priority. Go concurrency, contexts, race avoidance, channel closure, testing and error propagation. High Priority. Design a photo ingestion and metadata system with separate media storage, durable events, idempotent workers, retry policy and backpressure. High Priority. Explain microservice contracts and consistency when a social feed consumes event streams. Medium Priority. Compare SQS and the named Pub/Sub product conceptually, including delivery guarantees. Medium Priority. Spanner transactions and schema choices at a conceptual level; distinguish learning from past use. Medium Priority. Discuss the CI/CD pipelines implemented at airSlate and the Kubernetes, Helm, GitHub Actions and ArgoCD tools listed in the verified skills profile. Prepare to discuss rollout observability and rollback. Medium Priority. gRPC contracts, versioning and deadline propagation as design topics. Lower Priority. DDD and Clean Architecture vocabulary unless the client makes it central in the interview.

Rehearse a concrete upload failure. The client retries after an object reaches storage but before metadata commits. Describe the upload token, object key, ownership check and what happens if the same callback is delivered twice. Then add a queue consumer for image variants. Explain how idempotency, visibility timeouts and dead-letter handling affect recovery, and which metric would tell you a single slow customer is delaying everyone else. Set a proposed retention period only after asking about the actual business constraints.

## CV Deep-Dive Questions

For the Go support platform, explain the ticket-system integration boundary and production ownership without using the retracted volume claim. For the gateway, explain tenant stores, queues and vendor-neutral event contracts. For the Snowflake engine, describe why daily history reads were removed and how the shared job separated ingestion from delivery. For callbacks, explain security review and scheduling controls. For CRURATED, state plainly that it was PHP consulting and walk through the versioned event publication and modular stream setup. For airSlate, describe how database load was redistributed and how production stability changed.

## Company-Specific Preparation

The client application is described as serving millions of people and handling substantial photo volume, but its exact scale and topology are unknown. Research a reference architecture as preparation, then distinguish that proposed design from personal experience. Lytvynov Production's agency model means the client technical leads will likely test independent reasoning and calm production decisions. Prepare concise English explanations of one incident and one architecture tradeoff.

## Preparation Plan

Must prepare: a Go coding exercise under a time limit, one microservice data-flow sketch and a grounded account of recent production ownership. Before technical interview, rehearse event semantics, database and object-store boundaries, Kubernetes rollout and GCP vocabulary. Before final or culture interview, rehearse remote collaboration and clarify contractual answers.

For the test task, reserve time to restate assumptions, run the required commands from a clean checkout and document anything the reviewer needs to reproduce the result. Prioritize a small working path with tests for cancellation and duplicate delivery. Bring one architecture decision to the technical interview and explain how your answer would change if the service needed a stronger consistency guarantee or a different latency budget.

Explain how you would roll out a new consumer schema with producers on staggered versions. Identify the signals that would permit widening the rollout, such as error rate and queue age, and the state a rollback would need to preserve.

Prepare two clarifying questions about media privacy and account deletion before proposing data retention or an image processing pipeline.

## Questions to Ask

1. What part of the social platform would this engineer own?
2. Where are photos stored and how are metadata updates propagated?
3. What are the latency and availability targets?
4. Which services use gRPC and which use Pub/Sub?
5. How does the team handle retries and duplicate events?
6. What are the current migration or scaling pressures?
7. How are production incidents shared between client and agency?
8. Which decisions can the contractor make independently?
