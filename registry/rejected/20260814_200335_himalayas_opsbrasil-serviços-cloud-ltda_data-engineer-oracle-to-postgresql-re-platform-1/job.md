# Data Engineer - Oracle to PostgreSQL Re-Platform ( 102-08SENG-02 )

Posted: 2026-08-08T13:29:22Z

## Rejection

- Category: tech_stack
- Reason: role does not mention Go/Golang or PHP

This is not a ticket execution role. You get the problem and the context, you propose the solution, you build it, you ship it, and you defend the technical decisions directly in front of the client. The mandate is to take a production-grade LLM agent from read-only insight toward supervised action — hardening it for scale and staging it up a capability ladder (Explains → Recommends → Orchestrates → Acts). AI-assisted engineering (Claude Code, Cursor, Copilot, or equivalent) is the baseline here, not a differentiator — but you sign the code, and "the AI wrote it" is never an answer when something breaks in production.

### What you will do

-

Own end-to-end delivery: take a production LLM agent from requirement to production deploy, and defend the architecture and trade-offs directly with the client.

-

Build and harden agent orchestration (LangGraph / LangChain or equivalent) — routing, tool-calling, planning, synthesis, and state management.

-

Integrate tools over MCP and keep a growing tool surface fast and correct, including BM25, hybrid, or vector retrieval as scale demands.

-

Run models on AWS Bedrock and Bedrock AgentCore — model selection/routing, guardrails, memory, and regional residency profiles.

-

Build the evaluation harness (golden sets, LLM-as-judge, quality gates wired into CI) and instrument the system with OpenTelemetry for per-session token, cost, and latency attribution.

-

Drive down cost and latency with real levers (model routing, prompt caching, payload pruning, parallelizing independent calls) behind a regression gate; build in circuit breakers, fallbacks, and dead-letter handling.

-

Design and stage safe write-actions with least-privilege permissions, human-in-the-loop approval, plan versioning, audit trail, and rollback — released behind feature flags to a small cohort first.

### Requirements

### Required

-

5+ years in software engineering, with at least 2 genuinely at a senior level; strong Python in production, and comfort picking up TypeScript or Go when a project calls for it.

-

Hands-on LLM application engineering: prompt design, tool/function calling, structured output, context management, and token budgeting, in a system real users hit.

-

Agent orchestration experience: built or operated orchestration with a framework like LangGraph or LangChain, or hand-rolled, beyond single-prompt calls.

-

Managed LLM/agent platform in production: AWS Bedrock, Google Vertex AI, or Azure AI Foundry — model invocation, streaming, guardrails, and agent tooling. (We use Bedrock and Bedrock AgentCore; equivalent depth on Vertex AI or Azure transfers directly.)

-

Evaluation, retrieval & observability: eval harnesses and golden/reference sets, vector or hybrid search in production, and OpenTelemetry-based distributed tracing with token/cost/latency attribution.

-

Production AWS, CI/CD & IaC: real IAM, networking, storage, and observability experience; CI/CD pipelines versioned as code; Terraform in production.

-

Working English: comfortable defending system design and technical decisions directly on client calls.

### Highlights

### Tech stack

AWS Bedrock, Bedrock AgentCore, LangGraph/LangChain, MCP, Terraform, GitHub Actions/GitLab CI, OpenTelemetry

Originally posted on [Himalayas](https://himalayas.app)
