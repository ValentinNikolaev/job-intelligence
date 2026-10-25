# Match Analysis

**Score:** 49/100  
**Recommendation:** Possible Match

The candidate has relevant Go, distributed-systems, observability, reliability, and PostgreSQL evidence, but the role is specifically networking-focused and the profile does not establish OS-level networking or application-layer proxy and routing experience.

## Why it matches

- Professional Go experience includes scalable backend services, message delivery, retries, monitoring, and production ownership.
- Distributed-system design, event routing, backpressure handling, concurrency-adjacent reliability work, and observability are supported.
- PostgreSQL, MySQL, incident troubleshooting, performance optimisation, and cross-functional delivery are present in the profile.
- The role is remote, which is directionally compatible with the candidate profile.

## Gaps

- No sealed-profile evidence of socket programming, routing tables, packet filtering, overlay routing, proxies, or connectors.
- The posting is Canada-based, while the candidate is in Italy and the description does not clearly establish eligibility outside Canada.

## Concerns

- Networking internals are central to the role rather than a peripheral technology gap.
- The profile shows backend and platform reliability work, but not networking-product ownership.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Application-layer networking components | critical / stated | missing | Proven experience implementing application-layer networking concepts and distributed components, such as proxies, connectors, and overlay routing |  | This is a central role requirement and no matching evidence appears in the sealed profile. / Verify whether any unlisted networking-product work exists before treating the vacancy as viable. |
| OS-level networking internals | critical / stated | missing | Deep knowledge of operating system-level networking internals, including socket programming, routing tables, and packet filtering primitives. |  | The profile does not support the required socket, routing, or packet-filtering knowledge. / Do not prepare without additional verified candidate evidence. |
| Distributed systems and concurrency | high / stated | partial | Experience designing and maintaining distributed systems, with a solid understanding of concurrency | Build resilient message delivery pipelines with fallback logic, retries, and | Distributed reliability is evidenced, but the profile does not explicitly establish the listed concurrency primitives or networking concurrency. / Use a concrete concurrency example only if verified from candidate evidence. |
| Professional Go | high / stated | strong | Professional experience with Go (Golang) | I design and own a support automation platform that connects Zendesk, Intercom, and internal services through a robust, scalable backend in Go. | / |
| Relational databases and SQL | meaningful / stated | partial | Proficiency with relational databases (e.g., PostgreSQL, MySQL) and writing efficient SQL queries. | Additional skills: PostgreSQL, Restfull API. | Relational database experience is present, but efficient SQL-query evidence is limited in the profile. / Confirm the depth of SQL performance work before preparation. |
| Remote work | meaningful / stated | strong | Remote first company: most of our teams work fully remotely. | Fiumicino, Latium, Italy | The metadata lists Canada and the role's geographic eligibility is unclear. / Confirm whether Italy-based applicants are accepted for this Canada-listed role. |
