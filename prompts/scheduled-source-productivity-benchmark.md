# Scheduled source productivity benchmark

Configure this Scheduled Task with the model and reasoning from the selected workflow
profile in `config/codex-workflows.yaml`. Work only inside the configured repository.

This is a reporting-only benchmark task. Do not collect vacancies, run
model-dependent vacancy analysis, prepare applications, change vacancy statuses, or
call the OpenAI Platform API from project code.

Before benchmarking, pull the latest committed repository state from the configured
remote branch:

```powershell
git fetch --prune origin
git pull --ff-only
```

Read `AGENTS.md` and `config/codex-workflows.yaml`, then gather current deterministic
data:

```powershell
python run.py api source-usage --json
python run.py api catalog-vacancies --json
python run.py api workflow-summary --json
python run.py api workflow-limits --json
```

Analyze which vacancy source is most productive. Treat productivity as a balanced
benchmark, not just raw volume. Include these metrics per source when data is
available:

- Recent yield from `source-usage`: `last_created`, `last_updated`,
  `last_rejected`, `last_fetched`, `last_requests`, errors, and request efficiency.
- Cumulative API cost proxy: `total_requests` and `runs`.
- Catalog impact from `catalog-vacancies`: active vacancies by source, analyzed
  vacancies by source, average and median score by source, count and share scoring
  `>=65` by source, and rejected/closed/withdrawn share by source.
- Reliability signals: `last_status`, `last_errors`, `limit_reached`, and stale or
  missing data.

Rank sources overall and name the current winner, runner-up, and underperformers.
Explain the weighting in plain language, flag data limitations, and recommend one
concrete collection/configuration action for the next day. If the data is
insufficient to make a confident recommendation, say so and state exactly what should
be measured next.

Do not write project files unless explicitly necessary. If no project files change,
do not commit or push. If any real project file changes unexpectedly, inspect the full
diff, stage only real project changes, commit once, push to `origin`, and report the
commit hash and push result. Derive a natural, human-written commit subject from the
staged diff and name its concrete outcome. Do not select from the GitHub Actions
templates or use a generic `update data`, `update files`, `workflow changes`, or
`automated update` subject; keep execution metadata in the commit body.
