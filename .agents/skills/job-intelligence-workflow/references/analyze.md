# Analyze a sealed batch

1. Read `config/codex-workflows.yaml` and confirm the task uses the `analyze` model and reasoning level.
2. Run `python run.py triage` and then `python run.py pending analyze all --limit 15 --pack .codex-work/analyze-pack.yaml`.
3. If the pack has no items, report that analysis is current and stop.
4. Read only the sealed pack and the selected batch prompt. Evaluate every item independently; do not compare vacancies or reuse conclusions.
5. Add a `results` mapping keyed by every exact input `directory` to a copy of the
   newly created pack. Each value must be the exact YAML match mapping required by
   `prompts/vacancy-match.md`. Verify that the batch item directories and result keys
   exactly match the current pack; never reuse an earlier batch file. Do not add prose.
6. Publish with `python run.py analyze-batch --input .codex-work/analyze-batch.yaml --workflow analyze`.
7. If validation fails, correct only the batch draft and retry. Confirm all published `match.yaml`, `match.md`, and `registry/index.md` files exist and are valid.
