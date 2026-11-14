# Match Analysis

**Score:** 82/100  
**Recommendation:** Strong Match

Strong fit for a hands-on technical lead role combining Go, production LLM automation, evaluation, event-driven systems, reliability, and healthcare-sensitive privacy; FHIR, German, and some stack items remain gaps.

## Why it matches

- Technical leadership, architecture, roadmap, delivery, mentoring, and backend ownership across multiple production systems.
- Production LLM support-agent work, action tools, evaluation data, and defect remediation directly support agent orchestration and eval requirements.
- Strong audit, privacy, GDPR, observability, asynchronous pipeline, and operational reliability evidence.

## Gaps

- FHIR and medical coding domain experience are not established.
- German, TypeScript/Node.js/React, AWS Bedrock, and Datadog are not clearly evidenced as production technologies.

## Concerns

- The role expects full-stack depth across frontend and data as well as backend, while the strongest evidence is backend-focused.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| At least six years of experience including leading a small team. | critical / stated | strong | 6+ years of experience | Directly managed 10 developers. | No material evidence gap for the leadership requirement. / |
| Hands-on LLM and agent-system experience in production. | critical / stated | strong | Experience running an LLM or agent system in production is a strong plus, and strong personal projects count. | Implemented 10+ agent action tools: subscription cancel, cancellation offer, refund, marketing/Braze unsubscribe, user search (incl. via OpenAI vision), attachments extraction, useful-links generation for new billing, review processing for a second product. | The role's medical coding domain and model stack are new contexts. / Explain the production boundaries, failure modes, and human-review design of the support agent. |
| Evals with ground truth, regression tests, and an error taxonomy. | high / stated | partial | ground truth, regression tests | Built the evaluation pipeline: conversation texts + action events + subscription-state snapshots on ticket open/close → Eval JSON. | The profile evidences an evaluation pipeline but does not explicitly establish ground-truth labels or an error taxonomy. / Clarify the evaluation dataset, regression criteria, and classification of failure modes. |
| Reliability, observability, security, and privacy in a sensitive healthcare context. | high / stated | partial | own reliability, observability and security | PII controls: customer phone number never rendered or logged | Strong privacy and production-reliability evidence exists, but healthcare coding and expert-reviewed CI gates are not established. / Map the demonstrated GDPR and telephony controls to the role's patient-data and audit requirements. |
| Technical direction across backend, frontend, data model, and healthcare standards. | high / stated | partial | set the architecture with the team across backend, frontend and a data model built on healthcare standards such as FHIR. | I architect and lead the development of the platform's internal event analytics | Backend and event/data architecture are strong, but frontend depth and FHIR are not evidenced. / Verify practical frontend and healthcare data-model experience during technical assessment. |
| English communication in a remote team. | high / stated | strong | explain decisions and trade-offs clearly in English | English - Professional Working | No material evidence gap is established by the profile. / |
