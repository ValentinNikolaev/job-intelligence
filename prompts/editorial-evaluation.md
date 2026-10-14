# Blind editorial regression evaluation

Run this bounded workflow after changing application prompts, editorial knowledge or
their review contracts. It creates no application and requires no vacancy selection.
Never call a model endpoint from project code. Never read candidate records for these
synthetic cases and never update an existing CV, evidence bank or package.

1. Run `python run.py editorial export --output .codex-work/editorial-pack.json`.
2. Give that pack to one independent Codex reviewer. The reviewer must not read
   `tests/fixtures/editorial-corpus.yaml` or its answer keys. Read only the exported
   cases and policies. Reuse an available reviewer; do not create an assessment team.
3. Judge each final text against its supplied source and requirement. Decide `keep`,
   `rewrite` or `omit`; explain the source-backed reason and cite exact source excerpts.
   Numbers and senior-sounding verbs are not evidence. Missing measurements can stay
   unknown. Distinguish participation, influence, independent decisions, proposals
   and actual production delivery. Preserve employers in the approved window. Two
   internal letter evidence strands need not become two narrated case studies.
4. Return JSON with `schema_version: 1`, actual `reviewer`, copied `corpus_sha256` and
   `policy_sha256`, and one `decisions` row per case: `id`, `decision`, `reason`,
   `reason_codes`, `source_quotes`. Available reason codes are `routine_baseline`,
   `unsupported_ownership`, `supported_consequence`, `unsupported_influence`,
   `supported_influence`, `unsupported_metric`, `delivery_stage`, `role_omission`,
   `cv_replay`, `vacancy_priority`, `complementary_evidence`, `channel_fit`.
5. Run `python run.py editorial evaluate --input .codex-work/editorial-decisions.json
   --output .codex-work/editorial-receipt.json`. Missing, duplicate, stale or unanchored
   decisions fail; wrong dispositions or absent expected reason codes return exit 1.
   Inspect every disagreement. Fix a real process defect, or revise a demonstrably
   wrong test expectation with evidence; never relabel the answer just to pass.
6. Keep the pack, decisions and receipt in ignored work files. Report actual coverage,
   disagreements and limitations. A fixture test of the evaluator is not an independent
   editorial pass. A passing corpus does not prove invitation-rate improvement.
   The repository finalizer requires the decisions at the exact path above for
   editorial-policy changes and reruns the evaluator against current inputs.

Do not rerun this evaluation for each vacancy or harmless prose edit. Run the ordinary
unit suite for mechanical changes; repeat the editorial pass only when the decision
policy, corpus or generation prompt changes.
