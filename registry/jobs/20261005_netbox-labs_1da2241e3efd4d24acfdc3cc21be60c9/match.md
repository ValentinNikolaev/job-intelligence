# Match Analysis

**Score:** 20/100
**Recommendation:** Not Match

Go backend and event-driven experience are relevant, but the role makes substantial React/TypeScript, Python, gRPC, observability-dashboard, and frontend-testing requirements central and they are unsupported by the profile.

## Why it matches

- Go backend, APIs, event-driven systems, queues, and operational reliability are supported.

## Gaps

- The profile does not establish production React/TypeScript dashboards, Python, gRPC/Protobuf, data visualization, or frontend testing.

## Concerns

- Network telemetry, SNMP/gNMI, and NetBox experience are not present in the candidate profile.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Backend Go and Python | critical / stated | partial | Production experience with Go and Python: strong in at least one and working proficiency in the other. | - Go | Go is supported, but Python is not evidenced. / Confirm any Python production work. |
| gRPC and Protocol Buffers | critical / stated | missing | Hands-on experience designing and operating gRPC services with Protocol Buffers, including schema evolution and backward compatibility, streaming RPCs, deadlines, interceptors/middleware, and error handling. | - Go | No gRPC or Protocol Buffers experience is present in the profile. / This is a central technical requirement and requires direct evidence. |
| React and TypeScript dashboards | critical / stated | missing | Strong React and TypeScript skills, including component composition, state management, and typing best practices. | - PHP | No React or TypeScript experience is present in the profile. / This is a decisive role-scope conflict. |
| Observability dashboards | critical / stated | missing | Proven experience building monitoring, observability, or analytics dashboards: time-series charts, heatmaps, status and health views, and drill-down navigation. | - PHP | The profile includes monitoring/observability but not frontend dashboard construction. / Require a portfolio or concrete production example. |
| Event-driven systems and queues | high / stated | strong | Experience building distributed, event-driven systems, including message queues (e.g., RabbitMQ or Kafka), asynchronous job processing, and idempotent data ingestion. | - Go | / |

## Hard rejection

- The mandatory full-stack role requires strong production React/TypeScript observability dashboards and frontend testing, which are clearly unsupported by the candidate profile.
