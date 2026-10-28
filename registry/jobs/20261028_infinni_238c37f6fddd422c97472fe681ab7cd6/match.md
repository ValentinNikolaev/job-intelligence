# Match Analysis

**Score:** 18/100  
**Recommendation:** Not Match

The role is a senior Java backend position with several mandatory Java-specific requirements. The sealed profile supports senior backend architecture, Go, AWS, PostgreSQL, Kubernetes, event-driven systems, and mentoring, but does not support expert Java, Spring/Hibernate, Java concurrency, Kafka, or JVM tuning.

## Why it matches

- The profile states over 15 years of development experience and includes senior backend and technical-lead work.
- The candidate has distributed and event-driven systems experience, including queues and EventBridge.
- The profile supports AWS, PostgreSQL, Kubernetes, performance optimization, production reliability, and mentoring.
- The candidate's Go backend background is relevant only as a listed nice-to-have, not as a substitute for the mandatory Java stack.

## Gaps

- No expert-level Java evidence appears in the candidate profile.
- No Spring Boot/Data, Hibernate/JPA, Java concurrency, JVM internals, garbage-collector, or Kafka production evidence appears in the sealed profile.
- Redis experience is not established by the supplied candidate evidence.

## Concerns

- The vacancy's central technology and concurrency requirements are Java-specific and are not adjacent gaps that can be mitigated by the candidate's PHP/Go experience.
- The role offers EU remote work and a relocation option, but location fit cannot compensate for the mandatory Java stack mismatch.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Expert-level Java | critical / stated | missing | Expert-level Java. | ### Languages - Go - PHP | Java is an explicit core requirement and no Java experience is present in the sealed profile. / No credible mitigation without new candidate evidence establishing expert Java experience. |
| Deep Spring and Hibernate/JPA experience | critical / stated | missing | Deep experience with Spring (Boot, Data, etc.) and Hibernate/JPA, including an understanding of what happens under the hood. | ### Frameworks - Laravel - Symfony | The named Java frameworks and ORM are absent from the profile. / No credible mitigation without new candidate evidence. |
| Java multithreading and concurrency | critical / stated | missing | Strong command of multi-threading and concurrency in Java: CompletableFuture, thread pools and executors, the fork/join framework, synchronization primitives, and common pitfalls. | ### Languages - Go - PHP | The mandatory concurrency requirement is specifically Java-based and unsupported by the profile. / No credible mitigation without new candidate evidence. |
| Kafka in production | critical / stated | missing | Hands-on experience with Kafka in production. | ### Messaging Systems - Email delivery infrastructure - DNS / DKIM / SPF / DMARC | Kafka production experience is not evidenced. / No credible mitigation without new candidate evidence. |
| JVM internals and performance tuning | critical / stated | missing | Practical knowledge of JVM internals, garbage collectors (G1, ZGC, etc.), and performance tuning with tools like profilers, heap dumps, and GC logs. | ### Frameworks - Laravel - Symfony | No JVM or Java runtime evidence is present. / No credible mitigation without new candidate evidence. |
| At least 5 years as a Senior Developer or Architect | critical / stated | strong | At least 5 years of experience working as a Senior Developer or Architect. | I'm a highly experienced developer with over 15 years of expertise. | / |
| Strong PostgreSQL skills | high / stated | partial | Strong PostgreSQL skills, including schema design, query optimization, and indexing. | Normalized database tables and performed extensive query optimization. | Schema normalization and query optimization are evidenced, but indexing is not explicitly quoted. / Use the documented normalization and query-optimization evidence, and verify indexing experience separately. |
| Redis experience | high / stated | unknown | Experience using Redis for caching, rate limiting, or other patterns. |  | Redis is not explicitly evidenced in the sealed profile. / Confirm Redis experience separately if the Java mismatch were resolved. |
| Distributed systems and eventual consistency | high / stated | strong | A solid grasp of distributed systems concepts, including eventual consistency, idempotency, and horizontal scaling. | I architect and lead the development of the platform's internal event analytics | The exact eventual-consistency terminology is not stated in the candidate quote. / |
| AWS service operation | high / stated | strong | Experience building and running services on AWS. | AWS | The profile's technology list names AWS, while the supplied quote does not describe a specific AWS service. / |

## Hard rejection

- Expert-level Java and deep Spring/Hibernate/JPA experience are explicit mandatory requirements, while the sealed candidate profile lists Go and PHP and provides no Java evidence.
