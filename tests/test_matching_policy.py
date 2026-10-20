from __future__ import annotations

import copy
import tempfile
import unittest
from dataclasses import FrozenInstanceError
from pathlib import Path

import yaml

from jobintel.matching import MATCH_OUTPUT_SCHEMA, current_matching_context
from jobintel.matching_policy import MatchingPolicyError, load_matching_context, load_matching_policy


ROOT = Path(__file__).resolve().parents[1]


class MatchingPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        (self.root / "prompts").mkdir()
        self.path = self.root / "config/matching-policy.yaml"
        self.raw = yaml.safe_load((ROOT / "config/matching-policy.yaml").read_text(encoding="utf-8"))
        self.path.write_text(yaml.safe_dump(self.raw), encoding="utf-8")
        (self.root / "prompts/vacancy-match.md").write_text("Synthetic generic matching prompt", encoding="utf-8")

    def load(self, raw):
        self.path.write_text(yaml.safe_dump(raw), encoding="utf-8")
        return load_matching_policy(self.path)

    def test_policy_is_immutable_replacement_data_without_implicit_preferences(self):
        raw = copy.deepcopy(self.raw)
        raw["preferred_technologies"] = ["python"]
        raw["preferred_cities"] = ["Milan"]
        raw["preferred_domains"] = []
        policy = self.load(raw)
        self.assertEqual(("python",), policy.preferred_technologies)
        self.assertEqual(("Milan",), policy.preferred_cities)
        self.assertEqual((), policy.preferred_domains)
        with self.assertRaises(FrozenInstanceError):
            policy.prefer_remote = False
        snapshot = policy.canonical_analysis_snapshot()
        snapshot["preferred_cities"].append("Other")
        self.assertEqual(("Milan",), policy.preferred_cities)

    def test_all_fields_required_unknown_types_and_contradictions_fail(self):
        for field in self.raw:
            with self.subTest(field=field):
                raw = copy.deepcopy(self.raw)
                del raw[field]
                with self.assertRaisesRegex(MatchingPolicyError, "missing required fields.*" + field):
                    self.load(raw)
        for field, value in (("schema_version", True), ("schema_version", 2), ("prefer_remote", "true"),
                             ("preferred_cities", [""]), ("preferred_cities", ["Rome", "Rome"]),
                             ("preferred_domains", ["unrecognized"]), ("preferred_technologies", "go"),
                             ("discouraged_roles", ["unknown"]), ("numeric_weights", {})):
            with self.subTest(field=field, value=value), self.assertRaises(MatchingPolicyError) as error:
                self.load(self.raw | {field: value})
            self.assertIn(str(self.path), str(error.exception))
            self.assertIn(field, str(error.exception))
        with self.assertRaisesRegex(MatchingPolicyError, "cannot also be preferred"):
            self.load(self.raw | {"discouraged_core_technologies": ["go"]})
        with self.assertRaisesRegex(MatchingPolicyError, "requires block_us"):
            self.load(self.raw | {"block_us_work_requirements": False})

    def test_duplicate_invalid_yaml_and_invalid_encoding_have_safe_diagnostics(self):
        for data in (b"prefer_remote: true\nprefer_remote: secret-value", b"[secret-value", b"secret-value: \xff",
                     b"root: &r {nested: *r}"):
            with self.subTest(data=data):
                self.path.write_bytes(data)
                with self.assertRaises(MatchingPolicyError) as error:
                    load_matching_policy(self.path)
                self.assertIn(str(self.path), str(error.exception))
                self.assertNotIn("secret-value", str(error.exception))

    def test_context_reads_both_projects_and_prompt_edits_without_module_reimport(self):
        first = current_matching_context(self.root)
        second_root = self.root / "second"
        (second_root / "config").mkdir(parents=True)
        (second_root / "prompts").mkdir()
        (second_root / "config/matching-policy.yaml").write_text(yaml.safe_dump(self.raw | {"preferred_cities": ["Other"]}), encoding="utf-8")
        (second_root / "prompts/vacancy-match.md").write_text(first.prompt, encoding="utf-8")
        second = current_matching_context(second_root)
        self.assertNotEqual(first.prompt_version, second.prompt_version)
        (self.root / "prompts/vacancy-match.md").write_text(first.prompt + " Changed decision instruction.", encoding="utf-8")
        edited = current_matching_context(self.root)
        self.assertNotEqual(first.prompt_version, edited.prompt_version)
        self.assertEqual(second.prompt_version, current_matching_context(second_root).prompt_version)

    def test_context_versions_only_analysis_inputs_and_is_canonical(self):
        original = current_matching_context(self.root)
        (self.root / "config/notification-settings.yaml").write_text("destination: changed", encoding="utf-8")
        self.assertEqual(original.prompt_version, current_matching_context(self.root).prompt_version)
        self.path.write_text(yaml.safe_dump(dict(reversed(list(self.raw.items()))), sort_keys=False), encoding="utf-8")
        self.assertEqual(original.prompt_version, current_matching_context(self.root).prompt_version)
        changed_schema = copy.deepcopy(MATCH_OUTPUT_SCHEMA)
        changed_schema["required"].append("requirements")
        changed = load_matching_context(self.root, output_schema=changed_schema)
        self.assertNotEqual(original.prompt_version, changed.prompt_version)
