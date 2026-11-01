# Match Analysis

**Score:** 63/100  
**Recommendation:** Possible Match

Possible fit for Go infrastructure services with strong evidence in APIs, Kubernetes, asynchronous/event-driven systems, reliability, and GitOps. The role has several central infrastructure requirements—bare-metal provisioning, Kubernetes controllers, Redfish/PXE, and long-running workflow engines—not established in the profile.

## Why it matches

- Go backend, AWS, Kubernetes, API design, event-driven systems, retries, and observability are supported.
- Kubernetes migration and ArgoCD experience are directly documented.
- The remote EU location includes Italy.

## Gaps

- Bare-metal provisioning, BMC/Redfish, PXE/iPXE, Metal3, Cluster API, and GPU hardware are not documented.
- Temporal or equivalent workflow-engine experience is not explicit.

## Concerns

- Several missing items are core to the infrastructure-control-plane domain rather than optional technologies.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Kubernetes controller/reconciler patterns | critical / stated | unknown | Deep understanding of Kubernetes primitives and controller/reconciler patterns. |  | Controller/reconciler implementation is not stated. / Validate with a concrete Kubernetes control-plane example. |
| Bare-metal provisioning | critical / stated | missing | Hands-on experience with bare-metal provisioning flows — BMC/Redfish, PXE/iPXE, image management, and hardware inspection. |  | No candidate evidence for bare-metal or hardware provisioning. / Treat as a major screening risk. |
| Go infrastructure services | critical / stated | strong | Proficiency in Go (preferred for backend/Kubernetes ecosystem) | Go | / |
| Asynchronous long-running workflows | high / stated | partial | Experience building workflow-driven or event-driven systems (e.g., Temporal) where operations are long-running and state must remain consistent across retries and failures. | Build resilient message delivery pipelines with fallback logic, retries, and | Temporal or infrastructure reconciliation is not established. / Map prior retry/idempotency work to durable workflow requirements. |
