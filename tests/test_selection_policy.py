from __future__ import annotations

import copy
import tempfile
import unittest
from dataclasses import FrozenInstanceError, replace
from pathlib import Path

import yaml

from jobintel.selection_policy import SelectionPolicyError, load_selection_policy


ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "config/selection-policy.yaml"


class SelectionPolicyTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "selection-policy.yaml"
        self.raw = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))

    def load(self, raw=None):
        self.path.write_text(yaml.safe_dump(self.raw if raw is None else raw, sort_keys=False), encoding="utf-8")
        return load_selection_policy(self.path)

    def test_current_file_is_typed_deeply_immutable_and_preserves_order(self) -> None:
        policy = self.load()
        self.assertEqual(7, policy.max_age_days)
        self.assertEqual(("go", "php"), policy.target_technologies)
        self.assertEqual(("python", "r"), policy.excluded_combinations[0])
        self.assertEqual("italian", policy.blocking_languages[-1])
        self.assertEqual(tuple(self.raw["triage_exclusions"]), policy.triage_exclusions)
        with self.assertRaises(FrozenInstanceError):
            policy.max_age_days = 3
        with self.assertRaises(FrozenInstanceError):
            policy.location.reject_us_remote = False
        with self.assertRaises(TypeError):
            policy.excluded_combinations[0][0] = "go"

    def test_digest_is_canonical_but_list_order_and_relevant_changes_are_visible(self) -> None:
        policy = self.load()
        reversed_fields = dict(reversed(list(self.raw.items())))
        self.assertEqual(policy.fingerprint(), self.load(reversed_fields).fingerprint())
        changed_age = replace(policy, max_age_days=3)
        self.assertNotEqual(policy.fingerprint(), changed_age.fingerprint())
        self.assertNotEqual(policy.prefilter_fingerprint(), changed_age.prefilter_fingerprint())
        self.assertEqual(policy.triage_fingerprint(), changed_age.triage_fingerprint())
        changed_triage = replace(policy, triage_exclusions=tuple(reversed(policy.triage_exclusions)))
        self.assertNotEqual(policy.triage_fingerprint(), changed_triage.triage_fingerprint())
        self.assertEqual(policy.prefilter_fingerprint(), changed_triage.prefilter_fingerprint())
        changed_language = replace(policy, blocking_languages=tuple(reversed(policy.blocking_languages)))
        self.assertNotEqual(policy.prefilter_fingerprint(), changed_language.prefilter_fingerprint())
        self.assertEqual(policy.triage_fingerprint(), changed_language.triage_fingerprint())

    def test_lists_replace_without_implicit_defaults_or_inheritance(self) -> None:
        self.raw["excluded_roles"] = []
        self.raw["blocking_languages"] = []
        self.raw["triage_exclusions"] = ["sre"]
        policy = self.load()
        self.assertEqual((), policy.excluded_roles)
        self.assertEqual((), policy.blocking_languages)
        self.assertEqual(("sre",), policy.triage_exclusions)

    def test_target_choices_use_recognizer_capabilities_not_current_preferences(self) -> None:
        self.raw["target_technologies"] = ["python"]
        self.assertEqual(("python",), self.load().target_technologies)

    def test_every_field_is_required_and_unknown_fields_are_rejected(self) -> None:
        for key in self.raw:
            with self.subTest(missing=key):
                raw = copy.deepcopy(self.raw)
                del raw[key]
                with self.assertRaisesRegex(SelectionPolicyError, "missing required fields.*" + key):
                    self.load(raw)
        for field in ("account", "allowlist", "inherits"):
            with self.subTest(unknown=field):
                with self.assertRaisesRegex(SelectionPolicyError, "unknown fields.*" + field):
                    self.load(self.raw | {field: "unsupported"})
        for field in self.raw["location"]:
            with self.subTest(missing_location=field):
                raw = copy.deepcopy(self.raw)
                del raw["location"][field]
                with self.assertRaisesRegex(SelectionPolicyError, "location.*missing required fields.*" + field):
                    self.load(raw)
        raw = copy.deepcopy(self.raw)
        raw["location"]["countries"] = ["IT"]
        with self.assertRaisesRegex(SelectionPolicyError, "location.*unknown fields.*countries"):
            self.load(raw)

    def test_invalid_types_versions_and_identifiers_report_field_and_file(self) -> None:
        cases = [
            ("schema_version", True), ("schema_version", "1"), ("schema_version", 2),
            ("max_age_days", True), ("max_age_days", 0), ("max_age_days", -1),
            ("max_age_days", 1.5), ("max_age_days", "7"),
            ("reject_explicit_non_remote", "false"), ("reject_explicit_non_remote", 1),
            ("target_technologies", []), ("target_technologies", ["javascript"]),
            ("excluded_roles", ["qa", "qa"]), ("excluded_roles", "qa"),
            ("blocking_languages", ["english"]), ("excluded_cms", ["unknown"]),
            ("triage_exclusions", [False]), ("triage_exclusions", ["backend"]),
            ("excluded_combinations", "python+r"), ("excluded_combinations", [["python"]]),
            ("excluded_combinations", [["python", "unknown"]]),
            ("excluded_combinations", [["python", "r"], ["r", "python"]]),
            ("location", []),
        ]
        for field, value in cases:
            with self.subTest(field=field, value=value):
                with self.assertRaises(SelectionPolicyError) as raised:
                    self.load(self.raw | {field: value})
                self.assertIn(str(self.path), str(raised.exception))
                self.assertIn(field, str(raised.exception))
        raw = copy.deepcopy(self.raw)
        raw["location"]["reject_us_remote"] = "false"
        with self.assertRaisesRegex(SelectionPolicyError, "location.reject_us_remote.*boolean"):
            self.load(raw)

    def test_contradictions_fail_instead_of_choosing_precedence(self) -> None:
        raw = copy.deepcopy(self.raw)
        raw["excluded_technologies"] = ["php"]
        with self.assertRaisesRegex(SelectionPolicyError, "excluded_technologies.*target"):
            self.load(raw)
        raw = copy.deepcopy(self.raw)
        raw["excluded_combinations"] = [["spring_boot", "python"]]
        with self.assertRaisesRegex(SelectionPolicyError, "excluded_combinations.*individually excluded"):
            self.load(raw)
        raw = copy.deepcopy(self.raw)
        raw["location"] = {field: field == "allow_european_exception" for field in raw["location"]}
        with self.assertRaisesRegex(SelectionPolicyError, "location.allow_european_exception.*requires"):
            self.load(raw)

    def test_duplicate_keys_and_malformed_yaml_fail_without_echoing_values(self) -> None:
        for text, field in (
            ("schema_version: 1\nschema_version: secret-value\n", "schema_version"),
            ("location:\n  reject_us_remote: true\n  reject_us_remote: secret-value\n", "location.reject_us_remote"),
            ("schema_version: [secret-value", "$"),
            ("location: &recursive {nested: *recursive}", "location.nested"),
            ("? [secret-value]\n: 1", "$"),
            ("null", "$"),
        ):
            with self.subTest(text=text):
                self.path.write_text(text, encoding="utf-8")
                with self.assertRaises(SelectionPolicyError) as raised:
                    load_selection_policy(self.path)
                self.assertIn(str(self.path), str(raised.exception))
                self.assertIn(field, str(raised.exception))
                self.assertNotIn("secret-value", str(raised.exception))

    def test_missing_file_fails_without_reading_default_policy(self) -> None:
        with self.assertRaisesRegex(SelectionPolicyError, "cannot read policy"):
            load_selection_policy(self.path)

    def test_invalid_utf8_reports_file_and_field_without_bytes(self) -> None:
        self.path.write_bytes(b"schema_version: 1\nsecret-value: \xff\n")
        with self.assertRaises(SelectionPolicyError) as raised:
            load_selection_policy(self.path)
        self.assertIn(str(self.path), str(raised.exception))
        self.assertIn("$: policy must be UTF-8 text", str(raised.exception))
        self.assertNotIn("secret-value", str(raised.exception))
