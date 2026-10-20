from __future__ import annotations

import hashlib
import io
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import FrozenInstanceError, replace
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel.accounts import (
    AccountConfigurationError,
    extract_account_selector,
    load_account_context,
    main,
    require_account_context,
)
from tests.account_fixtures import write_account_config


class AccountSelectorTests(unittest.TestCase):
    def test_extracts_selector_before_after_and_between_command_arguments(self):
        cases = [
            (["--account", "current", "evidence", "questions"], ["evidence", "questions"]),
            (["storage", "doctor", "--account=current"], ["storage", "doctor"]),
            (["prepare", "--account", "current", "vacancy", "--document", "cv"],
             ["prepare", "vacancy", "--document", "cv"]),
        ]
        for argv, expected in cases:
            with self.subTest(argv=argv):
                original = list(argv)
                self.assertEqual(("current", expected), extract_account_selector(argv))
                self.assertEqual(original, argv)

    def test_identical_repeated_selectors_are_accepted(self):
        self.assertEqual(
            ("current", ["storage", "doctor"]),
            extract_account_selector(["--account=current", "storage", "--account", "current", "doctor"]),
        )

    def test_conflicting_repeated_selectors_fail(self):
        with self.assertRaisesRegex(AccountConfigurationError, "conflicting"):
            extract_account_selector(["--account=current", "--account", "another"])

    def test_selector_extraction_stops_at_argument_delimiter(self):
        self.assertEqual(
            ("current", ["command", "--", "--account", "another"]),
            extract_account_selector(["--account", "current", "command", "--", "--account", "another"]),
        )
        self.assertEqual(
            (None, ["command", "--", "--account=another"]),
            extract_account_selector(["command", "--", "--account=another"]),
        )

    def test_extractor_leaves_other_flags_and_values_unchanged(self):
        argv = ["command", "--acc=current", "--input=--account=another", "current"]
        self.assertEqual((None, argv), extract_account_selector(argv))

    def test_missing_blank_whitespace_and_invalid_selectors_fail_without_echoing_values(self):
        for args in [
            ["--account"], ["--account", "--env"], ["--account="],
            ["--account", ""], ["--account", " current"], ["--account", "current "],
            ["--account", "Current"], ["--account", "secret://credential"],
        ]:
            with self.subTest(args=args), self.assertRaises(AccountConfigurationError) as error:
                extract_account_selector(args)
            self.assertNotIn("secret://credential", str(error.exception))


class AccountContextTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name).resolve()
        self.root = self.base / "project"
        self.root.mkdir()
        self.descriptor = write_account_config(self.root)
        self.original = self.descriptor.read_bytes()

    def load(self, **kwargs):
        kwargs.setdefault("environ", {})
        return load_account_context(self.root, **kwargs)

    def write(self, payload):
        self.descriptor.write_text(yaml.safe_dump(payload, sort_keys=False), encoding="utf-8")

    def payload(self):
        return yaml.safe_load(self.original.decode("utf-8"))

    def test_default_explicit_and_environment_selection_have_equal_contexts(self):
        expected = self.load()
        self.assertEqual(expected, self.load(account="current"))
        self.assertEqual(expected, self.load(environ={"JOBINTEL_ACCOUNT": "current"}))
        self.assertEqual(expected, self.load(account="current", environ={"JOBINTEL_ACCOUNT": "current"}))
        self.assertEqual("current", expected.account_id)
        self.assertEqual(hashlib.sha256(self.original).hexdigest(), expected.descriptor_sha256)
        self.assertEqual(self.root, expected.project_root)
        self.assertEqual(self.root / "registry", expected.path("registry"))
        self.assertEqual(self.root / "sources/.env", expected.path("environment"))
        self.assertEqual(self.root / "config/application-profile.yaml", expected.reference("application_profile"))

    def test_context_is_immutable_and_references_are_not_mutable_mappings(self):
        context = self.load()
        with self.assertRaises(FrozenInstanceError):
            context.account_id = "another"
        with self.assertRaises(TypeError):
            context.references[0] = ("selection_policy", "elsewhere.yaml")
        changed = dict(context.paths)
        changed["registry"] = "another"
        self.assertEqual(self.root / "registry", context.path("registry"))

    def test_unknown_lookup_names_fail_without_echoing_them(self):
        context = self.load()
        for method in (context.reference, context.path):
            with self.assertRaises(AccountConfigurationError) as error:
                method("sensitive-input")
            self.assertNotIn("sensitive-input", str(error.exception))

    def test_explicit_empty_environment_does_not_inherit_process_selector(self):
        with patch.dict(os.environ, {"JOBINTEL_ACCOUNT": "another"}):
            self.assertEqual("current", self.load(environ={}).account_id)
            with self.assertRaisesRegex(AccountConfigurationError, "not enabled"):
                load_account_context(self.root)

    def test_unknown_and_conflicting_selectors_fail_before_descriptor_read(self):
        for kwargs in [
            {"account": "another"},
            {"environ": {"JOBINTEL_ACCOUNT": "another"}},
            {"account": "current", "environ": {"JOBINTEL_ACCOUNT": "another"}},
            {"account": "another", "environ": {"JOBINTEL_ACCOUNT": "current"}},
            {"account": ""},
            {"environ": {"JOBINTEL_ACCOUNT": " current"}},
        ]:
            with self.subTest(kwargs=kwargs), patch.object(Path, "read_bytes", side_effect=AssertionError("read")):
                with self.assertRaises(AccountConfigurationError):
                    self.load(**kwargs)

    def test_loader_reads_only_descriptor_and_never_creates_linked_paths(self):
        (self.root / "sources").mkdir()
        (self.root / "sources/.env").write_text("invalid dotenv containing sensitive-input", encoding="utf-8")
        (self.root / "config/application-profile.yaml").write_text("invalid profile", encoding="utf-8")
        before = {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        real_read_bytes = Path.read_bytes
        reads = []

        def read_only_descriptor(path):
            reads.append(path)
            if path != self.descriptor:
                raise AssertionError("loader accessed linked input")
            return real_read_bytes(path)

        environment = {"JOBINTEL_ACCOUNT": "current", "MONGODB_URI": "synthetic-process-value"}
        with patch.dict(os.environ, environment, clear=True), patch.object(Path, "read_bytes", read_only_descriptor):
            self.assertEqual("current", self.load().account_id)
            self.assertEqual(environment, dict(os.environ))
        self.assertEqual([self.descriptor], reads)
        self.assertEqual(before, {p.relative_to(self.root): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})
        self.assertFalse((self.root / ".codex-work").exists())
        self.assertFalse((self.root / "registry").exists())

    def test_missing_descriptor_does_not_search_parent_or_executable_root(self):
        nested = self.root / "nested"
        nested.mkdir()
        with self.assertRaisesRegex(AccountConfigurationError, "cannot read"):
            load_account_context(nested, environ={})
        self.descriptor.unlink()
        with self.assertRaisesRegex(AccountConfigurationError, "cannot read"):
            self.load()

    def test_missing_or_file_project_root_is_rejected(self):
        for root in (self.base / "absent", self.descriptor):
            with self.subTest(root=root), self.assertRaisesRegex(AccountConfigurationError, "existing directory"):
                load_account_context(root, environ={})

    def test_accepts_utf8_bom_and_hashes_actual_descriptor_bytes(self):
        content = b"\xef\xbb\xbf" + self.original
        self.descriptor.write_bytes(content)
        self.assertEqual(hashlib.sha256(content).hexdigest(), self.load().descriptor_sha256)

    def test_malformed_yaml_and_encoding_errors_do_not_reveal_content(self):
        for raw in [b"secret-value: [unterminated", b"\xffsecret-value", b"!!python/object:secret-value {}"]:
            with self.subTest(raw=raw):
                self.descriptor.write_bytes(raw)
                with self.assertRaises(AccountConfigurationError) as error:
                    self.load()
                self.assertNotIn("secret-value", str(error.exception))

    def test_duplicate_nontext_and_recursive_keys_are_rejected(self):
        variants = [
            self.original + b"schema_version: 1\n",
            self.original.replace(b"      registry: registry\n", b"      registry: registry\n      registry: registry\n"),
            self.original + b"42: hidden\n",
            b"? [sequence, key]\n: hidden\n",
            b"accounts: &loop\n  current: *loop\n",
            b"root: &defaults {schema_version: 1}\n<<: *defaults\n",
        ]
        for raw in variants:
            with self.subTest(raw=raw):
                self.descriptor.write_bytes(raw)
                with self.assertRaises(AccountConfigurationError):
                    self.load()

    def test_schema_version_is_exactly_integer_one(self):
        for version in (True, False, 0, 2, "1", 1.0, None):
            with self.subTest(version=version):
                payload = self.payload()
                payload["schema_version"] = version
                self.write(payload)
                with self.assertRaisesRegex(AccountConfigurationError, "schema_version"):
                    self.load()

    def test_missing_and_unknown_fields_at_every_level_are_rejected(self):
        locations = [
            (),
            ("accounts", "current"),
            ("accounts", "current", "references"),
            ("accounts", "current", "paths"),
        ]
        for location in locations:
            for mode in ("missing", "unknown"):
                with self.subTest(location=location, mode=mode):
                    payload = self.payload()
                    target = payload
                    for key in location:
                        target = target[key]
                    if mode == "missing":
                        del target[next(iter(target))]
                    else:
                        target["secret-field"] = "secret-value"
                    self.write(payload)
                    with self.assertRaises(AccountConfigurationError) as error:
                        self.load()
                    self.assertNotIn("secret", str(error.exception))

    def test_only_one_current_account_and_matching_default_are_allowed(self):
        variants = [
            ("default_account", "another"),
            ("default_account", " current"),
            ("accounts", {}),
            ("accounts", {"another": self.payload()["accounts"]["current"]}),
            ("accounts", {**self.payload()["accounts"], "another": self.payload()["accounts"]["current"]}),
        ]
        for key, value in variants:
            with self.subTest(key=key, value=value):
                payload = self.payload()
                payload[key] = value
                self.write(payload)
                with self.assertRaises(AccountConfigurationError):
                    self.load()

    def test_pinned_references_and_paths_reject_relocation_and_wrong_types(self):
        for group, name in (("references", "application_profile"), ("paths", "registry")):
            for value in (
                "../elsewhere", "/absolute", "C:/absolute", "C:relative", "registry\\jobs",
                "registry/../registry", "registry//jobs", "other/registry", None, True, [],
            ):
                with self.subTest(group=group, value=value):
                    payload = self.payload()
                    payload["accounts"]["current"][group][name] = value
                    self.write(payload)
                    with self.assertRaisesRegex(AccountConfigurationError, "schema-1 paths"):
                        self.load()

    def test_resolved_path_escape_or_internal_redirection_is_rejected(self):
        real_resolve = Path.resolve
        for path in (self.descriptor, self.root / "registry", self.root / "sources/.env",
                     self.root / "config/application-profile.yaml"):
            for destination in (self.base / "outside", self.root / "redirected"):
                def redirected(candidate, *args, **kwargs):
                    return destination if candidate == path else real_resolve(candidate, *args, **kwargs)

                with self.subTest(path=path, destination=destination), patch.object(Path, "resolve", redirected):
                    with self.assertRaisesRegex(AccountConfigurationError, "escapes|redirected"):
                        self.load()

    def test_path_lookup_rechecks_redirection_after_context_was_created(self):
        context = self.load()
        real_resolve = Path.resolve

        def redirected(path, *args, **kwargs):
            return self.base / "outside" if path == self.root / "registry" else real_resolve(path, *args, **kwargs)

        with patch.object(Path, "resolve", redirected):
            with self.assertRaisesRegex(AccountConfigurationError, "escapes"):
                context.path("registry")

    def test_distinct_roots_never_share_context_or_paths(self):
        other = self.base / "other"
        write_account_config(other)
        first = self.load()
        second = load_account_context(other, environ={})
        self.assertNotEqual(first, second)
        self.assertEqual(first.descriptor_sha256, second.descriptor_sha256)
        self.assertNotEqual(first.path("registry"), second.path("registry"))
        with self.assertRaisesRegex(AccountConfigurationError, "another project root"):
            require_account_context(other, first, environ={})

    def test_supplied_context_requires_fresh_descriptor_bytes(self):
        context = self.load()
        self.assertEqual(context, require_account_context(self.root, context, environ={}))
        self.descriptor.write_bytes(self.original + b"# changed descriptor\n")
        with self.assertRaisesRegex(AccountConfigurationError, "stale"):
            require_account_context(self.root, context, environ={})
        self.assertNotEqual(context.descriptor_sha256, require_account_context(self.root, environ={}).descriptor_sha256)

    def test_supplied_context_cannot_hide_invalid_or_deleted_descriptor(self):
        context = self.load()
        self.descriptor.write_text("broken: config\n", encoding="utf-8")
        with self.assertRaises(AccountConfigurationError):
            require_account_context(self.root, context, environ={})
        self.descriptor.unlink()
        with self.assertRaises(AccountConfigurationError):
            require_account_context(self.root, context, environ={})

    def test_supplied_context_cannot_change_paths_or_account(self):
        context = self.load()
        for supplied in (
            replace(context, account_id="another"),
            replace(context, paths=(("registry", "another"),)),
            object(),
        ):
            with self.subTest(supplied=supplied), self.assertRaises(AccountConfigurationError):
                require_account_context(self.root, supplied, environ={})

    def test_fixture_helper_is_idempotent_and_does_not_seed_linked_data(self):
        before = {p.relative_to(self.root): p.stat().st_mtime_ns for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.descriptor, write_account_config(self.root))
        self.assertEqual(before, {p.relative_to(self.root): p.stat().st_mtime_ns for p in self.root.rglob("*") if p.is_file()})
        self.assertEqual([Path("config/accounts.yaml")], list(before))

    def test_module_cli_reports_only_current_account_without_operational_access(self):
        (self.root / "sources").mkdir()
        (self.root / "sources/.env").write_text("not dotenv: secret-value", encoding="utf-8")
        output = io.StringIO()
        with patch.dict(os.environ, {}, clear=True), redirect_stdout(output):
            self.assertEqual(0, main(["--account=current", "--project-root", str(self.root)]))
        self.assertEqual("current\n", output.getvalue())
        self.assertFalse((self.root / ".codex-work").exists())
        self.assertFalse((self.root / "registry").exists())

    def test_module_cli_rejects_selection_before_reading_descriptor(self):
        for argv, environment in (
            (["--account=another"], {}),
            (["--account=current"], {"JOBINTEL_ACCOUNT": "another"}),
            (["--account=current", "--account=another"], {}),
        ):
            error = io.StringIO()
            output = io.StringIO()
            with self.subTest(argv=argv, environment=environment), patch.dict(os.environ, environment, clear=True):
                with patch.object(Path, "read_bytes", side_effect=AssertionError("descriptor read")):
                    with redirect_stderr(error), redirect_stdout(output):
                        self.assertEqual(2, main([*argv, "--project-root", str(self.root)]))
            self.assertEqual("", output.getvalue())
            self.assertIn("Account configuration error:", error.getvalue())

    def test_module_cli_rejects_abbreviated_account_option(self):
        with patch.object(Path, "read_bytes", side_effect=AssertionError("descriptor read")):
            with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
                main(["--acc=another", "--project-root", str(self.root)])
        self.assertEqual(2, error.exception.code)

    def test_real_module_entrypoint_uses_explicit_root_from_another_working_directory(self):
        environment = dict(os.environ)
        environment.pop("JOBINTEL_ACCOUNT", None)
        repository = Path(__file__).resolve().parents[1]
        environment["PYTHONPATH"] = str(repository)
        result = subprocess.run(
            [sys.executable, "-m", "jobintel.accounts", "--project-root", str(self.root),
             "--account", "current"],
            cwd=self.base,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("current\n", result.stdout)
        self.assertEqual("", result.stderr)

    def test_account_resolution_preserves_matching_and_preparation_semantic_identities(self):
        from jobintel.matching import current_matching_context
        from jobintel.preparation_context import load_preparation_context
        from tests.preparation_fixtures import write_preparation_config

        repository = Path(__file__).resolve().parents[1]
        (self.root / "prompts").mkdir()
        for relative in ("config/matching-policy.yaml", "prompts/vacancy-match.md"):
            (self.root / relative).write_bytes((repository / relative).read_bytes())
        before_preparation = write_preparation_config(
            self.root, candidate_directory="synthetic/person", evidence_bank="synthetic/proofs/bank.yaml",
            cv_owner_stem="SyntheticCandidate",
        )
        before_matching = current_matching_context(self.root)
        context = self.load()
        self.assertEqual(before_matching.prompt_version, current_matching_context(context.project_root).prompt_version)
        self.assertEqual(before_preparation.version, load_preparation_context(context.project_root).version)
        self.assertEqual(self.root / "synthetic/person", before_preparation.candidate_directory)


if __name__ == "__main__":
    unittest.main()
