# Match Analysis

**Score:** 55/100
**Recommendation:** Possible Match

Good Go, Kubernetes, ArgoCD, GitHub Actions, AWS, observability, and architecture foundations, but many mandatory platform technologies and frontend requirements are unverified or absent.

## Why it matches

- Go development, Kubernetes, GitHub Actions, ArgoCD, AWS, Prometheus/Jaeger, and architecture are supported.
- Distributed systems, event-driven pipelines, reliability, and production troubleshooting are relevant.

## Gaps

- OpenTelemetry, controller-runtime, CRDs, admission webhooks, React/TypeScript, Istio, Kafka, MCP, and Cloud Broker APIs are not explicitly evidenced.

## Concerns

- The breadth of mandatory platform and frontend requirements creates substantial delivery risk.
- On-call expectations and the role's Ukraine location compatibility are not fully established.

## Requirement evidence

| Requirement | Priority / basis | Match | Posting evidence | Candidate evidence | Risk / action |
| --- | --- | --- | --- | --- | --- |
| Kubernetes operators, CRDs, and admission webhooks | critical / stated | unknown | Develop Kubernetes operators using controller-runtime / Operator SDK (kubebuilder) |  | Core operator-specific experience is not evidenced. / Confirm operator and CRD projects before applying. |
| OpenTelemetry | critical / stated | unknown | OpenTelemetry (OTEL) observability |  | OTEL experience is not evidenced. / Confirm collector/exporter experience. |
| Go development | critical / stated | strong | Go language development | Go-based backends | / |
| Frontend React and TypeScript | high / stated | unknown | React / Frontend Stack (TS, Tailwind, Vite, TanStack) |  | Frontend experience is not established. / Confirm hands-on React/TypeScript scope. |
