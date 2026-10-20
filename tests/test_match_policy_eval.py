import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import yaml

from jobintel.match_policy_eval import (
    digest, evaluate_decisions, export_pack, main, project_inputs, project_export_pack,
    project_evaluate_decisions, project_main,
)


class MatchPolicyEvaluationTests(unittest.TestCase):
    def setUp(self):
        self.root = Path(__file__).resolve().parents[1]
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.work = Path(self.temporary.name)
        self.prompt = self.work / "current.md"
        self.prompt.write_text("Evaluate fit using the supplied policy snapshot.\n", encoding="utf-8")
        self.inputs = dict(
            corpus_path=self.root / "tests/fixtures/match-policy-corpus.yaml",
            baseline_prompt_path=self.root / "tests/fixtures/match-policy-baseline-prompt.md",
            current_prompt_path=self.prompt,
            baseline_schema={"type": "object", "schema": "original-output"},
            current_schema={"type": "object", "schema": "current-output"},
            policy_snapshot={"schema_version": 1, "analysis_preferences": {"remote": "prefer"}},
        )
        self.corpus = yaml.safe_load(self.inputs["corpus_path"].read_text(encoding="utf-8"))
        self.pack = export_pack(**self.inputs)
        self.answers = self._fixture_answers()

    def _fixture_answers(self):
        rows = []
        for variant_index, variant in enumerate(self.pack["variants"]):
            for case in self.pack["cases"]:
                original = next(c for c in self.corpus["cases"]
                                if {v["source"] for v in c["vacancies"]} == {v["source"] for v in case["vacancies"]})
                expected = original["expected"]
                id_map = {v["id"]: next(x["id"] for x in case["vacancies"] if x["source"] == v["source"])
                          for v in original["vacancies"]}
                vacancies = []
                for vacancy in original["vacancies"]:
                    hard = expected["hard_rejection"][vacancy["id"]]
                    score = 15 if hard else (76 if vacancy["id"] == expected["preferred"] else 68) + variant_index
                    vacancies.append(dict(
                        id=id_map[vacancy["id"]], score=score,
                        recommendation="not_match" if hard else "match",
                        hard_rejection=hard,
                        hard_rejection_reason="An evidenced mandatory condition conflicts with the synthetic candidate." if hard else None,
                        reason="This fixture decision follows the curated source-backed preference boundary.",
                        source_quotes={"candidate": [self.corpus["candidate"]], "vacancy": [vacancy["source"]]},
                        uncertainties=["The stated arrangement is unspecified and needs clarification."]
                        if vacancy["id"] in expected["uncertainty"] else [],
                    ))
                rows.append(dict(variant_id=variant["id"], case_id=case["id"], vacancies=vacancies,
                                 preferred=id_map[expected["preferred"]], effect_reason=expected["rationale"],
                                 tie_reason="", limitation=""))
        return dict(schema_version=1, reviewer="synthetic fixture evaluator; not an independent Codex pass",
                    bindings=copy.deepcopy(self.pack["bindings"]), blind_pack_sha256=self.pack["blind_pack_sha256"],
                    decisions=rows)

    def evaluate(self, answers=None, **overrides):
        return evaluate_decisions(self.answers if answers is None else answers, **(self.inputs | overrides))

    def test_export_is_deterministic_and_opaque_without_answers(self):
        self.assertEqual(self.pack, export_pack(**self.inputs))
        self.assertEqual(14, len(self.pack["cases"]))
        self.assertEqual(2, len(self.pack["variants"]))
        self.assertTrue(all(set(c) == {"id", "vacancies"} for c in self.pack["cases"]))
        exported_ids = {c["id"] for c in self.pack["cases"]}
        self.assertTrue(all(c["id"] not in exported_ids for c in self.corpus["cases"]))
        self.assertNotIn('"expected"', json.dumps(self.pack))
        self.assertNotIn('"rationale"', json.dumps(self.pack))
        self.assertNotIn("registry/candidate", json.dumps(self.pack))
        self.assertTrue(all(v["id"].startswith("x") for v in self.pack["variants"]))

    def test_fixture_answers_pass_without_identical_cross_variant_scores(self):
        receipt = self.evaluate()
        self.assertTrue(receipt["ok"])
        self.assertEqual(28, receipt["variant_case_count"])
        self.assertEqual(56, receipt["vacancy_judgment_count"])
        self.assertEqual(digest(self.answers), receipt["decisions_sha256"])
        self.assertEqual([], receipt["ties"])

    def test_saved_baseline_is_the_original_prompt_and_schema(self):
        original = self.inputs["baseline_prompt_path"].read_bytes()
        self.assertNotIn(b"\r", original)
        self.assertEqual("98f9d0657557afc0a256b0a2a9140300738d2e38d1cec59ca40bc167acc5cb47",
                         hashlib.sha256(original).hexdigest())
        schema = json.loads((self.root / "tests/fixtures/match-policy-baseline-schema.json").read_text(encoding="utf-8"))
        self.assertIn("requirements", schema["properties"])
        self.assertFalse(schema["additionalProperties"])

    def test_actual_corpus_edit_invalidates_decisions(self):
        changed = copy.deepcopy(self.corpus)
        changed["cases"][0]["vacancies"][0]["source"] += " The employer has clarified its office arrangement."
        path = self.work / "changed-corpus.yaml"
        path.write_text(yaml.safe_dump(changed), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.evaluate(corpus_path=path)

    def test_missing_fields_unknown_fields_and_boolean_version_fail(self):
        for mutation in ("missing_blocker_reason", "unknown_pair", "unknown_top", "boolean_schema"):
            with self.subTest(mutation=mutation):
                answers = copy.deepcopy(self.answers)
                if mutation == "missing_blocker_reason":
                    del answers["decisions"][0]["vacancies"][0]["hard_rejection_reason"]
                elif mutation == "unknown_pair":
                    answers["decisions"][0]["expected"] = "leaked answer"
                elif mutation == "unknown_top":
                    answers["extra"] = "unrecognized"
                else:
                    answers["schema_version"] = True
                with self.assertRaises(ValueError):
                    self.evaluate(answers)

    def test_every_hash_binding_rejects_stale_decisions(self):
        for field in self.pack["bindings"]:
            with self.subTest(field=field):
                answers = copy.deepcopy(self.answers)
                answers["bindings"][field] = "stale"
                with self.assertRaisesRegex(ValueError, "stale"):
                    self.evaluate(answers)
        answers = copy.deepcopy(self.answers)
        answers["blind_pack_sha256"] = "stale"
        with self.assertRaisesRegex(ValueError, "stale"):
            self.evaluate(answers)

    def test_changed_current_prompt_policy_schema_and_baseline_are_detected(self):
        for field, value in (
            ("policy_snapshot", {"schema_version": 1, "analysis_preferences": {"remote": "neutral"}}),
            ("current_schema", {"type": "object", "schema": "changed"}),
            ("baseline_schema", {"type": "object", "schema": "changed"}),
        ):
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "stale"):
                self.evaluate(**{field: value})
        self.prompt.write_text("Changed current prompt.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.evaluate()
        changed = self.work / "baseline.md"
        changed.write_text("Changed original baseline.\n", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "stale"):
            self.evaluate(baseline_prompt_path=changed)

    def test_canonical_policy_ignores_mapping_order_but_not_semantic_values(self):
        reordered = {"analysis_preferences": {"remote": "prefer"}, "schema_version": 1}
        self.assertEqual(self.pack, export_pack(**(self.inputs | {"policy_snapshot": reordered})))

    def test_missing_duplicate_unknown_variant_and_vacancy_keys_rejected(self):
        for mutation in ("missing", "duplicate", "unknown_variant", "unknown_case", "missing_vacancy", "duplicate_vacancy"):
            with self.subTest(mutation=mutation):
                answers = copy.deepcopy(self.answers)
                if mutation == "missing":
                    answers["decisions"].pop()
                elif mutation == "duplicate":
                    answers["decisions"][1] = copy.deepcopy(answers["decisions"][0])
                elif mutation == "unknown_variant":
                    answers["decisions"][0]["variant_id"] = "unknown"
                elif mutation == "unknown_case":
                    answers["decisions"][0]["case_id"] = "unknown"
                elif mutation == "missing_vacancy":
                    answers["decisions"][0]["vacancies"].pop()
                else:
                    answers["decisions"][0]["vacancies"][1] = copy.deepcopy(answers["decisions"][0]["vacancies"][0])
                with self.assertRaises(ValueError):
                    self.evaluate(answers)

    def test_fabricated_or_empty_anchors_rejected(self):
        for anchor, value in (("candidate", ["Alex is fluent in German."]), ("vacancy", ["invented"]), ("vacancy", []), ("vacancy", [""])):
            with self.subTest(anchor=anchor, value=value):
                answers = copy.deepcopy(self.answers)
                answers["decisions"][0]["vacancies"][0]["source_quotes"][anchor] = value
                with self.assertRaisesRegex(ValueError, "source excerpts"):
                    self.evaluate(answers)

    def test_inverted_qualitative_preference_and_numeric_order_fail(self):
        for mutation in ("preference", "numeric"):
            with self.subTest(mutation=mutation):
                answers = copy.deepcopy(self.answers)
                row = answers["decisions"][0]
                other = next(v for v in row["vacancies"] if v["id"] != row["preferred"])
                if mutation == "preference":
                    row["preferred"] = other["id"]
                else:
                    preferred = next(v for v in row["vacancies"] if v["id"] == row["preferred"])
                    if other["hard_rejection"]:
                        row = next(r for r in answers["decisions"] if not any(v["hard_rejection"] for v in r["vacancies"]))
                        preferred = next(v for v in row["vacancies"] if v["id"] == row["preferred"])
                        other = next(v for v in row["vacancies"] if v["id"] != row["preferred"])
                    preferred["score"], other["score"] = 68, 76
                receipt = self.evaluate(answers)
                self.assertFalse(receipt["ok"])
                self.assertIn("inverted_preference", {f["reason"] for f in receipt["failures"]})

    def test_optional_german_hard_rejection_fails(self):
        answers = copy.deepcopy(self.answers)
        for row in answers["decisions"]:
            source_case = next(c for c in self.pack["cases"] if c["id"] == row["case_id"])
            optional = next((v for v in source_case["vacancies"] if "German at C1 is optional" in v["source"]), None)
            if optional:
                answer = next(v for v in row["vacancies"] if v["id"] == optional["id"])
                answer.update(score=20, recommendation="not_match", hard_rejection=True,
                              hard_rejection_reason="Unsupported optional-language blocker introduced by a faulty decision.")
                break
        receipt = self.evaluate(answers)
        self.assertFalse(receipt["ok"])
        self.assertIn("blocker_boundary", {f["reason"] for f in receipt["failures"]})

    def test_unknown_arrangement_requires_uncertainty(self):
        answers = copy.deepcopy(self.answers)
        for row in answers["decisions"]:
            for vacancy in row["vacancies"]:
                vacancy["uncertainties"] = []
        receipt = self.evaluate(answers)
        self.assertFalse(receipt["ok"])
        self.assertEqual(4, len([f for f in receipt["failures"] if f["reason"] == "missing_uncertainty"]))

    def test_explained_ties_require_review_and_block_the_gate(self):
        answers = copy.deepcopy(self.answers)
        row = next(r for r in answers["decisions"] if not any(v["hard_rejection"] for v in r["vacancies"]))
        for vacancy in row["vacancies"]:
            vacancy["score"] = 75
        row["preferred"] = "tie"
        with self.assertRaisesRegex(ValueError, "tie reason"):
            self.evaluate(answers)
        row["tie_reason"] = "The preference exists but the overall fit remains in the same score bucket."
        with self.assertRaisesRegex(ValueError, "tie limitation"):
            self.evaluate(answers)
        row["limitation"] = "This tie cannot establish the strength of the configured preference."
        receipt = self.evaluate(answers)
        self.assertFalse(receipt["ok"])
        self.assertTrue(receipt["review_required"])
        self.assertEqual(1, len(receipt["ties"]))

    def test_all_24_soft_comparisons_tied_cannot_pass_project_gate(self):
        project, answers = self._project_fixture()
        tied = 0
        for row in answers["decisions"]:
            if not any(v["hard_rejection"] for v in row["vacancies"]):
                for vacancy in row["vacancies"]:
                    vacancy["score"] = 75
                row.update(preferred="tie", tie_reason="Both vacancies fall in the same overall scoring bucket.",
                           limitation="This comparison does not demonstrate the intended preference direction.")
                tied += 1
        self.assertEqual(24, tied)
        receipt = project_evaluate_decisions(project, answers)
        self.assertFalse(receipt["ok"])
        self.assertTrue(receipt["review_required"])
        self.assertEqual([], receipt["failures"])
        self.assertEqual(24, len(receipt["ties"]))
        decisions = project / ".codex-work/match-policy-decisions.json"
        decisions.parent.mkdir()
        decisions.write_text(json.dumps(answers), encoding="utf-8")
        self.assertEqual(1, project_main([
            "evaluate", "--input", str(decisions), "--output", ".codex-work/match-policy-receipt.json",
        ], root=project))

    def test_band_blocker_boolean_and_score_types_are_checked(self):
        mutations = ({"score": True}, {"score": 101}, {"score": 75, "recommendation": "strong_match"},
                     {"hard_rejection": "false"}, {"hard_rejection": True, "hard_rejection_reason": "A decisive mandatory conflict is claimed but inconsistent with the numeric score."})
        for mutation in mutations:
            with self.subTest(mutation=mutation):
                answers = copy.deepcopy(self.answers)
                answer = next(v for r in answers["decisions"] for v in r["vacancies"] if not v["hard_rejection"])
                answer.update(mutation)
                with self.assertRaises(ValueError):
                    self.evaluate(answers)

    def test_cli_export_restricts_output_to_ignored_json(self):
        baseline_schema, current_schema, policy = [self.work / name for name in ("old.json", "new.json", "policy.json")]
        for path, value in ((baseline_schema, self.inputs["baseline_schema"]),
                            (current_schema, self.inputs["current_schema"]), (policy, self.inputs["policy_snapshot"])):
            path.write_text(json.dumps(value), encoding="utf-8")
        common = ["--corpus", str(self.inputs["corpus_path"]), "--baseline-prompt", str(self.inputs["baseline_prompt_path"]),
                  "--current-prompt", str(self.prompt), "--baseline-schema", str(baseline_schema),
                  "--current-schema", str(current_schema), "--policy", str(policy)]
        output = self.work / ".codex-work/pack.json"
        self.assertEqual(0, main(["export", *common, "--output", str(output)], root=self.work))
        self.assertEqual(self.pack, json.loads(output.read_text(encoding="utf-8")))
        self.assertEqual(1, main(["export", *common, "--output", str(self.work / "tracked.json")], root=self.work))
        self.assertFalse((self.work / "tracked.json").exists())

    def _project_fixture(self):
        project = self.work / "project"
        for relative in (
            "config/matching-policy.yaml", "prompts/vacancy-match.md",
            "tests/fixtures/match-policy-corpus.yaml", "tests/fixtures/match-policy-baseline-prompt.md",
            "tests/fixtures/match-policy-baseline-schema.json",
        ):
            path = project / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes((self.root / relative).read_bytes())
        self.pack = project_export_pack(project)
        return project, self._fixture_answers()

    def test_project_evaluation_resolves_effective_typed_inputs(self):
        project, answers = self._project_fixture()
        from jobintel.matching import current_matching_context
        context = current_matching_context(project)
        effective = project_inputs(project)
        self.assertEqual(context.policy.canonical_analysis_snapshot(), effective["policy_snapshot"])
        self.assertEqual(context.prompt, effective["current_prompt_text"])
        self.assertEqual(json.loads(context.schema_json), effective["current_schema"])
        self.assertTrue(project_evaluate_decisions(project, answers)["ok"])

    def test_project_evaluation_rejects_actual_policy_and_prompt_edits(self):
        for changed_input in ("policy", "prompt"):
            with self.subTest(changed_input=changed_input):
                project, answers = self._project_fixture()
                if changed_input == "policy":
                    path = project / "config/matching-policy.yaml"
                    policy = yaml.safe_load(path.read_text(encoding="utf-8"))
                    policy["prefer_remote"] = not policy["prefer_remote"]
                    path.write_text(yaml.safe_dump(policy), encoding="utf-8")
                else:
                    path = project / "prompts/vacancy-match.md"
                    path.write_text(path.read_text(encoding="utf-8") + "\nChanged actual policy instructions.\n", encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "stale"):
                    project_evaluate_decisions(project, answers)

    def test_project_evaluation_rejects_actual_runtime_schema_edit(self):
        project, answers = self._project_fixture()
        from jobintel.matching import MATCH_OUTPUT_SCHEMA
        schema = copy.deepcopy(MATCH_OUTPUT_SCHEMA)
        schema["properties"]["score"]["description"] = "Changed runtime schema description"
        with patch("jobintel.matching.MATCH_OUTPUT_SCHEMA", schema):
            with self.assertRaisesRegex(ValueError, "stale"):
                project_evaluate_decisions(project, answers)

    def test_project_cli_has_no_policy_override_and_ignores_copied_receipts(self):
        project, answers = self._project_fixture()
        with self.assertRaises(SystemExit) as raised:
            project_main(["export", "--output", ".codex-work/pack.json", "--policy", "fake.yaml"], root=project)
        self.assertEqual(2, raised.exception.code)
        decisions = project / ".codex-work/match-policy-decisions.json"
        decisions.parent.mkdir(parents=True, exist_ok=True)
        decisions.write_text(json.dumps(answers), encoding="utf-8")
        receipt = project / ".codex-work/match-policy-receipt.json"
        receipt.write_text('{"ok":true,"copied":true}', encoding="utf-8")
        answers["bindings"]["policy_sha256"] = "stale"
        decisions.write_text(json.dumps(answers), encoding="utf-8")
        self.assertEqual(1, project_main([
            "evaluate", "--input", str(decisions), "--output", str(receipt),
        ], root=project))
        self.assertEqual({"ok": True, "copied": True}, json.loads(receipt.read_text(encoding="utf-8")))

    def test_project_cli_export_and_evaluate_use_runtime_inputs(self):
        project, answers = self._project_fixture()
        self.assertEqual(0, project_main(["export", "--output", ".codex-work/match-policy-pack.json"], root=project))
        self.assertEqual(self.pack, json.loads((project / ".codex-work/match-policy-pack.json").read_text(encoding="utf-8")))
        decisions = project / ".codex-work/match-policy-decisions.json"
        decisions.write_text(json.dumps(answers), encoding="utf-8")
        self.assertEqual(0, project_main([
            "evaluate", "--input", str(decisions), "--output", ".codex-work/match-policy-receipt.json",
        ], root=project))
        self.assertTrue(json.loads((project / ".codex-work/match-policy-receipt.json").read_text(encoding="utf-8"))["ok"])


if __name__ == "__main__":
    unittest.main()
