## Recruiter / HR Screening

Prepare a clear account of why this role is interesting: production backend ownership combined with careful review of AI-assisted work in a financial-data setting. The candidate can explain current Go and PHP evidence without implying that both are equally recent in one job. Describe CRURATED as concurrent part-time PHP consulting alongside Simple.life, then state the corrected Simple.life end date at the precision supported by the career record. Ask which country will employ or contract with a worldwide remote hire and confirm work authorization before an application or offer. Salary expectations, notice period and earliest start date are still unconfirmed in the profile. Do not fill them from the advertised range or an assumed employment arrangement. For English, the source states upper-intermediate; practise a spoken technical walkthrough and a short explanation of how a disagreement with a vendor would be handled.

The recruiter may ask, “Do you use Claude Code every day?” Prepare the truthful answer from the candidate's actual use, with a real example and a distinction between coding-agent workflow and the production LLM system he helped build. Do not substitute the latter for the former. The practical case requires a task, an agent log or recording, working solution and a note about automated versus manual verification. Check in advance which tools and logs the candidate can actually show without exposing employer confidential data.

## Culture Fit / Behavioral Interview

Use true examples and prepare situation, task, action and result notes for these likely questions:

1. Describe a vague business request you made concrete. Who chose the scope and acceptance criteria?
2. When did you reject a generated or suggested implementation because the risk was too high?
3. How did you choose between shipping quickly and adding a security check?
4. Describe a production incident you owned after the feature had shipped.
5. How did you handle a disagreement about architecture with product, SRE or frontend colleagues?
6. Which repetitive process did you automate, and how did you know it helped?
7. Tell us about a feature where the result differed from the first expectation.
8. How did you review another engineer's work without taking over their decision?

Potential source-backed story pools are the Simple.life telephony security review, the LLM support evaluation pipeline, the helpdesk vendor boundary, and the CRURATED production integration. The candidate must supply his own precise account of meetings, trade-offs and outcomes. Source files confirm technical contributions, not every behavioural detail above.

## Technical Interview

**High priority — coding-agent verification.** Be ready to turn a vague request into requirements, acceptance criteria and edge cases. Show a reproducible agent session if the candidate has one. Explain which claims can be checked with tests and which need manual review, especially payment amounts, authorization, personal data and merchant isolation. The posting expects live adaptation with the CTO, so practise explaining a changed requirement before making a code change.

**High priority — backend fundamentals.** Review Go concurrency and cancellation, PHP request handling, SQL transactions, indexes, idempotency, REST contracts, authentication boundaries, queue retries and failure visibility. Use actual production examples without claiming an unsupported payment-acquiring stack. Be able to explain why a multi-tenant ingestion service needs tenant isolation and how to verify it.

**High priority — operations.** Walk through CI/CD, monitoring, rollback, incident triage and ownership after release. The telephony production release and support-platform operation are suitable evidence. Discuss security sign-off and privacy review at the level disclosed in candidate sources. The posting names Docker and Linux, but the record does not establish hands-on scope for each. Confirm and prepare those details from direct experience rather than adding them to the CV on assumption.

**Medium priority — financial and security domain.** Review payment gateway API failure modes, duplicate callbacks, reconciliation concepts, PCI scope, secret handling and audit logs as interview topics. Distinguish conceptual understanding from personal implementation. The candidate has older gateway integration and recent privacy-sensitive support work, but no verified card-scheme or acquiring ownership.

**Low priority — employer's particular toolchain.** ClickUp task format, nightly red-team runs and Claude Code-specific commands can be learned from the company process, yet must not be presented as prior practice until confirmed.

## CV Deep-Dive Questions

Expect to explain what “owned” means for each system. For the LLM support agent, which action tools did the candidate personally build, what was evaluated, and where did human review enter? For the telephony backend, what architectural decision was his, who approved security, and what did he operate after launch? For the helpdesk gateway, what boundary did the vendor-neutral model create and what was actually demonstrated? For CRURATED, how was technical ownership of the production DataLake, parallel event versions and Crutrade integration established, and which outcomes are qualitative rather than measured? For airSlate, identify the backend team role and avoid taking sole credit for Prometheus-tracked team improvements. The withdrawn ECS-to-Kubernetes migration must not reappear in answers.

## Company-Specific Preparation

The live [Djinni posting](https://djinni.co/jobs/855076-ai-native-product-engineer-php-go/) describes a still-anonymous product FinTech employer. Read its practical-case instructions again immediately before the exercise. Ask whether sample data, payment stubs and a repository will be supplied. Clarify what may be recorded or shared in an agent log and how sensitive data should be excluded. Do not infer a named product, location of incorporation or payment volume. If the employer discloses these later, verify them from primary material before adjusting the application story.

## Preparation Plan

**Must prepare before first call:** truthful coding-agent usage account, one recent end-to-end backend story, the concurrent CRURATED timeline, English introduction, authorization and start-date facts. **Before technical stage:** work through one realistic task from vague request to tests and manual high-risk review, then check the output and share only a sanitized log if appropriate. Practise the Go/PHP, SQL, API, queue and security questions above. **Before final CTO session:** prepare a concise architecture walkthrough, identify what changes when requirements move, and decide how to challenge an agent-generated plan while staying responsible for the result.

## Questions to Ask

1. Which product and payment flows would this engineer own first?
2. Who makes the final call on product scope and acceptance criteria?
3. What does a good agent-session log show in your practical case?
4. Which changes always require manual review before release?
5. How do you test merchant isolation and money movement paths?
6. How are production incidents shared between feature owners and platform engineers?
7. What measures show that an AI-assisted feature helped the requester?
8. Which country and contract type apply to a candidate working from Italy?
