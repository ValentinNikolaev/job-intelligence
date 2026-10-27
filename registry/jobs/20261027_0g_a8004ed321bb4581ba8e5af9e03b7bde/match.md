# Match Analysis

**Score:** 32/100  
**Recommendation:** Weak Match

The profile has useful Kubernetes, AWS, CI/CD, Helm, ArgoCD, observability, and Go evidence, but the role is an end-to-end platform and blockchain-node owner requiring deep multi-cloud, networking, Terraform or Pulumi, and long-term DevOps/SRE experience not established here.

## Why it matches

- Kubernetes migration and deployment preparation with Helm, GitHub Actions, and ArgoCD.
- AWS, monitoring, production troubleshooting, and reliability experience are evidenced.
- Go is present as a supporting engineering skill.

## Gaps

- The profile does not establish 5+ years in DevOps/SRE/platform roles, production experience on two of Google Cloud, AWS, and Alibaba Cloud, Terraform or Pulumi, blockchain-node operations, or the detailed networking and Kubernetes operations listed.

## Concerns

- The posting expects ownership of more than 200 virtual machines and cloud cost management, which is materially broader than the supplied candidate evidence.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| 5+ years in DevOps, SRE, or platform roles and 3+ years running production Kubernetes | critical / stated | missing | We want 5+ years in DevOps, SRE or platform roles, including 3+ years running production Kubernetes and owning CI/CD pipelines. | Kubernetes | The profile shows Kubernetes work but not the required duration in a DevOps/SRE/platform role. / Verify the actual operational ownership and dates before considering the role further. |
| Production experience on at least two specified cloud providers | critical / stated | missing | Production experience on at least two of Google Cloud, AWS and Alibaba Cloud | AWS | Only AWS is explicitly evidenced in the supplied profile. / Do not claim Google Cloud or Alibaba Cloud experience without new evidence. |
| Terraform or Pulumi in production | critical / stated | missing | Terraform or Pulumi in production, plus scripting in Bash and in Python or Go. |  | Terraform, Pulumi, Bash, and Python are not explicitly established. / Treat this as a major screening risk. |
| Kubernetes, Helm, and CI/CD | high / stated | partial | Kubernetes clusters and managed databases | Migrated managed services from ECS to Kubernetes. | The evidence supports migration and preparation, not the role's full cluster-operations scope. / Present the bounded migration and delivery work precisely. |
| Blockchain node operations | meaningful / stated | missing | operate validator, sentry, seed, RPC and archive nodes | Cryptocurrency. | Cryptocurrency domain exposure does not establish blockchain-node operations. / Do not infer infrastructure experience from domain exposure. |
