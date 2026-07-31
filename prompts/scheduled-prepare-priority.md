# Scheduled priority application preparation

Configure this Scheduled Task with **GPT-5.6 Terra** and **medium reasoning**. Before selecting work, fetch and fast-forward the configured remote branch, then inspect only the priority preparation queue:

`python run.py api queues prepare-priority --json --limit 10`

Read `AGENTS.md`, invoke `$job-intelligence-workflow` in preparation mode, and prepare exactly one pending vacancy only when its score is at least the configured `priority_score`. The priority queue excludes lower-scored preparation work. If the queue is empty, stop without publishing. If the selected model or reasoning does not match the workflow policy, report the limitation and do not publish.

Publish the selected application through `python run.py prepare <vacancy> --input <draft-directory> --workflow prepare`. Do not change vacancy status, submit an application, or contact an employer. The workflow skill owns deterministic validation, the independent catalog step, checks, Git finalization, and any required reporting.
