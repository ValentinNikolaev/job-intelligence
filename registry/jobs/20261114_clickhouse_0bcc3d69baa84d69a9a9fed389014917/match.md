# Match Analysis

**Score:** 61/100  
**Recommendation:** Possible Match

Strong Go, distributed-systems, Kubernetes, AWS, reliability, and observability evidence aligns with the product-metrics platform, but the vacancy lists Canada and does not clearly establish eligibility for an Italy-based candidate.

## Why it matches

- 2+ years of Go experience is supported by: "I design and own a support automation platform that connects Zendesk, Intercom, and internal services through a robust, scalable backend in Go."
- Distributed event pipelines, delivery guarantees, backpressure, retries, and 99.9% reliability are supported by the CRURATED evidence.
- Kubernetes, Helm, ArgoCD, Terraform, AWS, and production troubleshooting are supported by the candidate profile.

## Gaps

- ClickHouse or comparable petabyte-scale metrics storage is not explicitly established in the profile.
- Kafka, Temporal, and Kubernetes operator/controller experience are not explicitly established.

## Concerns

- The vacancy metadata states "Canada" while the candidate is based in Italy; the remote country arrangement is not explicit enough to treat this as a hard rejection.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| 5+ years of relevant software development industry experience building and operating scalable, fault-tolerant, distributed systems | critical / stated | strong | 5+ years of relevant software development industry experience building and operating scalable, fault-tolerant, distributed systems | I'm a highly experienced developer with over 15 years of expertise. | The exact scale of petabyte-level operation is not shown. / Lead with production event pipelines, support automation, reliability, and throughput outcomes. |
| 2+ years of software application development experience using Golang | critical / stated | strong | 2+ years of software application development experience using Golang | I design and own a support automation platform | The profile does not give a separately calculated Go duration. / Use the dated recent Go backend work and avoid an unsupported exact duration. |
| Experience with storing, shipping, and retrieving large volumes of data efficiently using technologies such as ClickHouse | high / stated | unknown | Experience with storing, shipping, and retrieving large volumes of data efficiently using technologies such as ClickHouse |  | ClickHouse and petabyte-scale storage are not explicit in the candidate evidence. / Verify relevant data-platform experience before preparation. |
| Experience with technologies such as Kubernetes, Helm, ArgoCD, Temporal as well as infrastructure-as-code tools such as Terraform | high / stated | partial | Experience with technologies such as Kubernetes, Helm, ArgoCD, Temporal as well as infrastructure-as-code tools such as Terraform | Migrated managed services from ECS to Kubernetes. | Terraform is listed in the profile but Temporal is not explicitly evidenced. / Separate verified Kubernetes/Helm/ArgoCD evidence from unknown Temporal experience. |
| fully remote environment | high / stated | unknown | ClickHouse is a globally distributed company and remote-friendly. We currently operate in over 25 countries. |  | The sealed metadata says Canada and does not confirm Italy eligibility. / Confirm country-of-employment eligibility before applying. |
