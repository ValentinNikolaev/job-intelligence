# Interview Preparation

## Recruiter / HR Screening

Prepare concise responses for:

- Availability for roughly 20 hours per week and a start within 24–48 hours after onboarding.
- Comfort with output-based compensation and the conditions needed to evaluate it: task size, acceptance criteria, rework, and minimum submissions.
- Why production backend experience transfers to AI evaluation: realistic environments need credible architecture, failure, and recovery behavior.
- Direct AI experience: describe support automation accurately and state that RL-environment authoring is new.
- Remote contractor eligibility from Italy, invoicing arrangement, time-zone expectations, and contract duration.
- Salary/rate expectations, notice period, and current commitments, which require candidate-provided answers.
- Overlapping Simple.life and CRURATED dates and the correct latest-role end date.

## Culture Fit / Behavioral Interview

1. Describe a distributed-system failure you designed around — use retries/backpressure from CRURATED or Simple.life.
2. Tell us about an ambiguous operational problem — use support-automation orchestration.
3. Give an example of improving system throughput — use the 10x data-lake increase.
4. Describe a difficult production incident — use airSlate monitoring and SRE diagnosis.
5. How do you make a system reproducible for other engineers — use versioned event schemas and CI/CD.
6. Tell us about designing for peak load — use the BFCM messaging platform.
7. How do you document edge cases and acceptance criteria — prepare a real example without inventing details.
8. Describe collaboration with technical leads and stakeholders — use Hyprr roadmap or airSlate planning.

## Technical Interview

- **High priority — distributed systems:** consistency, idempotency, queues, retries, poison messages, backpressure, ordering, deduplication, and partial failure.
- **High priority — cloud failure scenarios:** unhealthy rollouts, dependency failure, storage exhaustion, throttling, regional/service degradation, and safe recovery.
- **High priority — deterministic validation:** explicit state, reproducible inputs, invariant checks, time control, fixture isolation, and separating expected from incidental behavior.
- **High priority — Kubernetes and CI/CD:** deployments, readiness/liveness, rollback, Helm, GitHub Actions, ArgoCD, and failure injection concepts.
- **High priority — observability:** logs, metrics, traces, alert signals, and distinguishing symptoms from root causes.
- **Medium priority — AWS:** EventBridge, S3, ECS, access boundaries, networking concepts, and service failure modes. State exact hands-on depth.
- **Medium priority — security/recovery:** least privilege, secret handling, backups, RPO/RTO, and disaster-recovery testing; do not overstate formal ownership.
- **Medium priority — Go:** concurrency, context cancellation, error handling, interfaces, testing, and building reproducible CLI/service components.

## CV Deep-Dive Questions

- How was the 10x event-pipeline throughput measured?
- What guaranteed the claimed 99.9% event-delivery reliability?
- How were retries and backpressure implemented across destinations?
- What did you personally own in the ECS-to-Kubernetes migration?
- Describe a production issue found through monitoring and the resulting fix.
- What aspects of AI-assisted triage did you design versus integrate?
- Explain the overlapping recent roles and confirm dates.

## Company-Specific Preparation

Review the [official platform overview](https://www.micro1.ai/) and understand the distinction between real-world RL environments and contextual agent evaluations. Read the vacancy again for the exact artifact list: environments, validation tests, golden solutions, defective variants, architecture documentation, and acceptance criteria.

Prepare a sample scenario verbally: a queue-backed service with a bad IAM policy or rollout defect, observable symptoms, deterministic checks, expected recovery, and one intentionally broken variant. Present it as an interview exercise, not as prior work.

## Preparation Plan

**Must prepare:** availability and contract answers; one detailed distributed-system failure story; one cloud deployment story; one reproducibility/testing story; precise AI-experience boundaries.

**Before the technical interview:** design two reproducible cloud-failure scenarios, refresh IAM/networking and disaster-recovery fundamentals, and practice explaining deterministic validation without hidden dependencies.

**Before final/culture rounds:** clarify project duration, review and rejection policies, expected weekly throughput, communication cadence, and ownership of submitted artifacts.

## Questions to Ask

1. What does one accepted task contain, and how is its scope estimated?
2. How are submissions reviewed, rejected, or returned for rework?
3. What minimum weekly output is expected in practice?
4. Which cloud providers and infrastructure tools are used in the environments?
5. Are experts given templates for validators, golden solutions, and defective variants?
6. How is effective compensation affected by review and rework time?
7. What customer or benchmark confidentiality constraints apply?
8. How long is the project expected to run, and can weekly availability change?
