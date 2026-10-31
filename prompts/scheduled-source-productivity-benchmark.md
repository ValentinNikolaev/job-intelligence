# Scheduled source productivity benchmark

This reporting task has no selected project workflow profile. Configure it with
the global GPT-6 Sol/medium default. Work only inside the configured repository.

This is a reporting-only benchmark task. Do not collect vacancies, run
model-dependent vacancy analysis, prepare applications, change vacancy statuses, or
call the OpenAI Platform API from project code.

Before benchmarking, use a clean isolated managed worktree and inspect its local
checkout and remote revision with `gh`. Use `gh repo sync` without `--force` only
in that clean worktree; stop on refusal or divergence and preserve all local
files. Read the updated instructions afterward.

Read `AGENTS.md`, `config/codex-workflows.yaml` and the configured storage
environment from the primary checkout without copying or printing secrets.
Pass its absolute path as `--env <primary-sources-.env>` to the current
deterministic reports:

```powershell
python run.py api source-usage --json --env <primary-sources-.env>
python run.py api catalog-vacancies --json --env <primary-sources-.env>
python run.py api workflow-summary --json --env <primary-sources-.env>
python run.py api workflow-limits --json --env <primary-sources-.env>
```

Analyze which vacancy source is most productive. Treat productivity as a balanced
benchmark, not just raw volume. Include these metrics per source when data is
available:

- Recent yield from `source-usage`: `last_created`, `last_updated`,
  `last_rejected`, `last_fetched`, `last_requests`, errors, and request efficiency.
- Cumulative API cost proxy: `total_requests` and `runs`.
- Catalog impact from `catalog-vacancies`: active vacancies by source, analyzed
  vacancies by source, average and median score by source, count and share scoring
  at or above the current `prepare_min_score` in `config/codex-workflows.yaml`,
  and rejected/closed/withdrawn share by source.
- Reliability signals: `last_status`, `last_errors`, `limit_reached`, and stale or
  missing data.

Compare sources using the same observation window and show denominators beside
rates. Distinguish small samples and missing match scores from genuine low yield;
selection filters, source age, and overlap can confound source comparisons. Do
not rank a source as an underperformer merely because it had one empty run or
fewer requests. Rank sources and name a winner or runner-up only when the
observed samples support that distinction. Explain the weighting in plain
language, flag limitations, and recommend one concrete collection/configuration
action for the next day. If the data is insufficient, say so and state exactly
what should be measured next.

Do not write project files for this reporting task. If any project file changes
unexpectedly, stop and report the complete diff; do not stage, commit or push it.
For separately authorized repository changes, use the reviewed finalizer from
an isolated managed worktree under `AGENTS.md`. If nothing changed, make no
empty commit.
