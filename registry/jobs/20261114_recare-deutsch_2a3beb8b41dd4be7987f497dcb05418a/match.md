# Match Analysis

**Score:** 76/100  
**Recommendation:** Match

Strong backend and integration fit for a remote Italy-eligible healthtech role, with production Go, automation, observability, and LLM evidence; desktop automation and German healthcare standards remain gaps.

## Why it matches

- Production Go ownership across support automation, vendor integrations, APIs, queues, and resilient delivery pipelines.
- Direct production LLM and evaluation-pipeline experience with human-facing support workflows.
- Strong reliability, monitoring, debugging, and operational edge-case experience.

## Gaps

- No explicit Electron or TypeScript desktop experience.
- German language and HIS/KIS/PVS/EMR, HL7 v2, or FHIR experience are not established.

## Concerns

- The role involves Windows desktop automation in RDP or Citrix environments, which is not directly evidenced in the profile.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Professional backend experience in Go, Python, or TypeScript with production software owned and shipped. | critical / stated | strong | You have professional backend experience in Go, Python, or TypeScript, and you can point to production software you shipped and owned. | support automation platform | No material evidence gap for the core backend requirement. / |
| Integration-heavy systems involving APIs, workflows, data models, auth, and real-world edge cases. | critical / stated | strong | You're comfortable working on integration-heavy systems: APIs, workflows, data models, auth, and real-world edge cases. | Engineer a unified API orchestration layer | Hospital-system integration experience is not established, although comparable vendor integrations are. / Translate the support-platform integration experience into the hospital workflow context during assessment. |
| Experience building and evaluating AI or computer-use automation with human control. | high / stated | partial | Human-in-the-loop by default | Built the evaluation pipeline: conversation texts + action events + subscription-state snapshots on ticket open/close → Eval JSON. | Production LLM and evaluation work is evidenced, but computer-use automation and healthcare approval workflows are not. / Verify the candidate's approach to safety rails, human review, and UI automation failure recovery. |
| Reliability, monitoring, debugging, and test coverage for operable production systems. | high / stated | strong | You're pragmatic about reliability: you care about monitoring, debugging, test coverage, and making systems operable. | Build resilient message delivery pipelines | No material evidence gap for operational reliability. / |
| German, Electron or TypeScript desktop, healthcare IT standards, or HIS/KIS/PVS/EMR experience. | preferred / stated | unknown | German language skills. |  | These preferred qualifications are not established in the candidate profile. / Treat them as interview questions rather than hard eligibility gates. |
