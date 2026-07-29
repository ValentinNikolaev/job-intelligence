## Recruiter / HR Screening

- Motivation: connect the role to Go backend ownership, global-scale systems, self-custody Web3 products, and remote engineering.
- Location and authorization: clarify that the candidate is based in Rome/Fiumicino, Italy. Ask whether the role is truly global remote or has U.S. work-authorization constraints, since the registry record says United States.
- Working model: prepare examples of remote and cross-functional collaboration with Support Ops, Product, AI teams, and engineering leadership.
- Language: English appears as upper-intermediate/professional working proficiency across sources; be ready to describe written async communication and technical discussions.
- Notice period/current status: reconcile Simple.life and CRURATED dates before speaking with recruiters.
- Salary: prepare a senior remote Go/backend range and decide whether crypto/Web3 compensation mix matters, including token or equity components if offered.
- Job-change story: focus on deeper Go backend work, product-scale reliability, and Web3 systems.

## Culture Fit / Behavioral Interview

Likely behavioral questions:

1. Tell us about a backend system you owned from design to production.
2. Describe a time you built a system from scratch under ambiguous requirements.
3. How do you balance product speed with reliability and maintainability?
4. Tell us about a production incident involving retries, fallback logic, or monitoring.
5. How do you collaborate with product and support teams when priorities change?
6. Describe your experience with remote or async engineering communication.
7. Tell us about a time you improved system performance.
8. How would you ramp up on a new Web3 or wallet-specific domain?
9. Describe a time you helped raise engineering standards through review or mentoring.

STAR stories to prepare:

- Simple.life Go support automation: system ownership, API orchestration, Zendesk/Intercom integrations, retries, monitoring, and 30% ticket deflection.
- CRURATED event analytics infrastructure: versioned event schema, S3/Webhook downstreams, backpressure, observability, and 99.9% delivery reliability.
- airSlate migration and performance work: ECS to Kubernetes, Helm/GitHub Actions/ArgoCD, API bottlenecks, database load reduction, and release consistency.
- Hyprr Web3/NFT platform: prototype to closed beta, backend leadership, Ethereum-based digital asset components, and product planning.
- PDFfiller messaging service: team leadership, 50 million emails/month, and BFCM load.

## Technical Interview

**High Priority - Go backend engineering.** Review goroutines, contexts, cancellation, worker pools, HTTP services, API design, error handling, testing, profiling, and race detection. Prepare concrete Simple.life examples.

**High Priority - Microservices and cloud architecture.** Prepare designs for service boundaries, data ownership, deployment, observability, retries, idempotency, rate limiting, and graceful failure. Use airSlate and CRURATED examples.

**High Priority - Reliability and scale.** Expect questions on delivery guarantees, backpressure, queues, monitoring, incident response, database bottlenecks, and high-traffic behavior.

**High Priority - Web3 and wallet domain ramp-up.** Study self-custody, seed phrases, private keys, transaction signing, address derivation, chain RPCs, nonce handling, gas fees, wallet security, and common user-risk scenarios. Be honest about direct gaps.

**Medium Priority - SQL and databases.** Review MySQL/PostgreSQL schema design, query optimization, indexes, transactions, and operational load reduction.

**Medium Priority - Kubernetes and CI/CD.** Prepare the airSlate migration story: ECS to Kubernetes, Helm, GitHub Actions, ArgoCD, operational impact, and deployment risks.

**Medium Priority - System design.** Practice designing a backend for wallet notifications, token metadata, transaction history ingestion, price feeds, or swap routing. Cover caching, chain data freshness, retries, rate limits, and security.

**Low Priority - Mobile/extension surfaces.** Understand backend implications for mobile, browser extension, and desktop clients, but do not claim frontend or mobile expertise.

## CV Deep-Dive Questions

- What did the Go support automation platform do, and which services did it integrate?
- How did you design API orchestration for routing and lifecycle tracking?
- What failure modes did fallback logic and retries address?
- How did you measure 30% ticket deflection?
- What did CRURATED's event analytics system do, and why did it need backpressure?
- How did you maintain 99.9% event delivery reliability?
- What was your role in the ECS to Kubernetes migration?
- How did you reduce API response times and database load at airSlate?
- What Web3/NFT work did you do at Hyprr?
- Have you built self-custody wallet, private-key, or transaction-signing systems directly?

## Company-Specific Preparation

- Use Trust Wallet's official website to understand its self-custody positioning, 200M-user claim, supported Web3 experiences, audits, and ISO certification.
- Read the Trust Wallet careers page values: user-obsessed, humble, integrity, open, owners. Prepare examples for each without repeating marketing language.
- Review the public Ashby job posting before applying because the local registry text is truncated.
- Study Trust Wallet's relationship with Binance and prepare a neutral answer about working in a broad blockchain ecosystem.
- Review basic wallet architecture: local key storage, seed phrases, signing, RPC providers, chain indexing, transaction history, token metadata, swaps, and security warnings.

## Preparation Plan

**Must prepare before recruiter screen:** location/work authorization, current employment dates, salary expectations, remote availability, motivation for Trust Wallet, and a short explanation of Web3 experience.

**Before technical interview:** prepare two system designs: wallet transaction-history backend and reliable event/notification pipeline for wallet activity. Practice Go concurrency and failure-mode questions.

**Before final/culture interview:** prepare stories about ownership, remote collaboration, user-impact decisions, reliability trade-offs, and learning a domain with security consequences.

## Questions to Ask

1. Which backend services would this role own in the first three to six months?
2. How does the team split work between wallet product features, infrastructure, and platform reliability?
3. What scale or latency constraints matter most for the backend systems?
4. How do backend services interact with chain RPC providers or indexers?
5. Which security reviews or release gates apply to backend changes?
6. How does the team handle incidents that affect wallet users?
7. What timezone overlap does the global remote team expect?
8. How do mobile, extension, and backend teams coordinate feature launches?
9. What would make a new senior backend engineer successful after 90 days?
