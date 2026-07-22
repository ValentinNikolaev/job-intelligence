# Analyze one vacancy

1. Read `config/codex-workflows.yaml` and confirm the task uses the `analyze` model and reasoning level.
2. Run `python run.py pending analyze all --workflow analyze`.
3. If the command prints no path, report that analysis is current and stop.
4. Select only the first printed vacancy directory. Read its `meta.yaml` and `job.md`, plus the configured files under `registry/candidate/` and `prompts/vacancy-match.md`. Do not read another vacancy.
5. Evaluate the vacancy and write the exact YAML draft required by `prompts/vacancy-match.md` to `.codex-work/analyze/<vacancy-directory>.yaml`.
6. Publish it with `python run.py analyze <vacancy-directory> --input <draft-path> --workflow analyze`.
7. If validation fails, correct only the draft and retry. Confirm `match.yaml`, `match.md`, and `registry/index.md` exist and are valid.
