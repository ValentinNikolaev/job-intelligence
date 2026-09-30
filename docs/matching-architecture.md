# Vacancy Match Analysis

## Flow

```text
Codex task (one vacancy)
  + registry/candidate/*.md
  + registry/jobs/<vacancy>/meta.yaml
  + registry/jobs/<vacancy>/job.md
  + prompts/vacancy-match.md
            ↓
local YAML draft under .codex-work/
            ↓
deterministic Python validation and publication
            ↓
match.yaml + match.md + registry/index.md
```

Project code does not call the OpenAI Platform API or another model endpoint. The active
Codex task performs semantic evaluation. `CodexMatchDraftClient` only reads a local YAML
file; `MatchAnalyzer` validates its exact fields, adds hashes and provenance, writes both
outputs atomically, and refreshes the index.

## Schema and scoring

The draft contains `score`, `recommendation`, `summary`, `strengths`, `gaps`, `concerns`,
`hard_rejection`, and `hard_rejection_reason`. Recommendations are `strong_match`,
`match`, `possible_match`, `weak_match`, and `not_match`. The complete rubric and draft
example are versioned in `prompts/vacancy-match.md`.

## Cache

`profile_version`, `job_version`, `prompt_version`, and the actual Codex `model` label
must all match before an analysis is current. `python run.py pending analyze all
--workflow analyze` derives the allowed model label from policy and lists work without invoking a model. Publication accepts exactly
one vacancy and one draft so context isolation remains a Codex-task responsibility.

## Model routing

The analysis task uses GPT-5.6 Luna with low reasoning by project policy. The model is
selected when creating the Codex task; repository configuration cannot switch the active
model. The publisher label records provenance only.
