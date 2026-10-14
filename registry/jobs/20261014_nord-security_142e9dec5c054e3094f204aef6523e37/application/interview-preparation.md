# Interview Preparation — NordPass Backend Engineer

## Recruiter / HR Screening

Resolve location first. The application asks whether you are based in Vilnius or Kaunas and can work there, and whether you can attend the office three days weekly. Your CV says Rome. Establish truthful answers about relocation, attendance and work authorization; ask whether another arrangement is eligible. The general work-from-anywhere benefit does not answer these questions.

Connect the role's secure PHP backend work to NordPass Business's organizational access product without claiming experience on its systems. Expect questions about concurrent CRURATED consulting, Simple.life's year-only end date and your reason for changing jobs. Prepare your actual notice period, gross monthly salary expectation against the posted EUR 3,200–7,200 range, English working comfort and any other required languages.

## Culture Fit / Behavioral Interview

Build STAR notes with your exact responsibility and verified consequence.

1. **Tell us about a security decision under delivery pressure.** Use Simple.life telephony privacy, formal review and production release; distinguish backend from frontend/SRE work.
2. **How did you turn a product need into a service design?** Use the multi-tenant gateway and first B2B demo; avoid estimated vendor-onboarding savings.
3. **When did you improve a process with another team?** Use airSlate planning with Product Management; identify your own decisions.
4. **When did reliability shape an architecture choice?** Use CRURATED event delivery; define the system boundary, not an enterprise SLA.
5. **When did you remove unnecessary work?** Use the Snowflake-to-Intercom consolidation and its eliminated repeated reads.
6. **How did you handle a sensitive user workflow?** Use Simple.life GDPR export and deletion; avoid estimated turnaround savings.
7. **What did you achieve through leadership?** Use an airSlate performance or release result, attributing team work accurately.

## Technical Interview

| Priority | Topics to prepare | Why NordPass may probe them |
|---|---|---|
| High | PHP/Symfony architecture, OOP, async processing, patterns and API design | Explicit requirements. Map examples to codebases and dates; three Symfony-specific years and Slim remain unverified. |
| High | Authentication, access control, privacy and auditability | Discuss Simple.life telephony controls and CRURATED authentication/OTP; do not claim OAuth, OIDC or JWT without evidence. |
| High | Onboarding system design: lifecycle, tenant isolation, idempotency, retries, observability | A hypothetical exercise, not NordPass's confirmed architecture. State assumptions and trade-offs. |
| High | Unit/integration testing, CI/CD and PHP/Go coding | Describe real test and release practices; a QA checklist does not prove the requested test types. |
| Medium | MySQL performance; RabbitMQ/SQS/EventBridge delivery; AWS/Kubernetes operations | Prepare one real data-flow diagram covering duplicates, backpressure and recovery. |
| Medium | Live coding, API errors and readable tests | Practice explaining edge cases and confirming interview tooling. |
| Low | Redis, DynamoDB, Sentry, PHP 8, cryptography, AI-assisted engineering | Vacancy topics absent from the final CV. Distinguish hands-on use from study; LLM integration does not prove AI-assisted coding. |

## CV Deep-Dive Questions

Expect questions on your telephony decisions versus security/team approval; architectural access and consent controls; gateway components behind the B2B demo; and GDPR workflow boundaries. For CRURATED, define the DataLake baseline/window behind more-than-10x throughput, setup-time observation and above-99.9% delivery scope. Explain technical ownership without claiming every line of code.

At airSlate, explain Prometheus measures behind API response, release time and database load; 65% is a maximum, not a reduction. Clarify CRURATED's concurrent part-time status, Simple.life's year-only end and exact Symfony chronology. Keep older dated roles concise.

## Company-Specific Preparation

Review NordPass Business's public features: shared folders, centralized settings, activity logs, breach monitoring, MFA and enterprise integrations. These do not reveal this team's architecture. Revisit the [official vacancy](https://jobs.ashbyhq.com/nord-security/a8f7480a-ce42-4e20-8132-a29030963f6c) and [product page](https://nordpass.com/business-password-manager/). Prepare one diagram of a real CV system and a separately labeled hypothetical onboarding design.

## Preparation Plan

**Before recruiter screening:** settle the two Lithuania answers, relocation/work authorization, salary expectation, notice period and overlapping consulting explanation. Raise an unmet office requirement early.

**Before technical rounds:** reconstruct Symfony/Slim periods, identify actual unit/integration test examples, rehearse PHP/Go coding and onboarding design, and verify named AWS/identity technologies. Defend measured CRURATED and airSlate outcomes.

**Before final/culture rounds:** refine STAR stories on security, product delivery and collaboration. Keep answers proportional to your contribution; omit estimated benefits.

## Questions to Ask

1. Is residence in Vilnius or Kaunas and three office days a firm requirement for this position, and how is eligibility assessed before technical rounds?
2. What does the Business Onboarding & Setup team own directly, and where are its boundaries with identity and security teams?
3. Which onboarding or access-lifecycle problems are most important in the next six months?
4. What PHP frameworks and versions are used in the team's main services, and what is the expected direction of those codebases?
5. How are security design and privacy reviews performed for new backend flows?
6. What testing and release practices give the team confidence when changing account or credential workflows?
7. How does the team measure onboarding success and operational reliability?
8. What would strong performance in the first three months look like for this engineer?
