from __future__ import annotations

import io
import os
import tempfile
import unittest
from contextlib import redirect_stderr
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jobintel import cli, storage_bridge as bridge
from jobintel.accounts import AccountConfigurationError, load_account_context
from jobintel.config import resolve_environment
from jobintel.storage_cli import cli_main
from jobintel.workflow_api import workflow_summary
from tests.account_fixtures import write_file_account_config


class AccountIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        write_file_account_config(self.root)
        self.environment = patch.dict(os.environ, {}, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.context = load_account_context(self.root)
        self.addCleanup(self._clear_stores)

    def _clear_stores(self):
        for key in list(bridge._STORES):
            if key[0] == str(self.root):
                bridge._STORES.pop(key).close()

    def _mongo_config(self):
        self.context.reference("data_services").write_text(
            "storage:\n  backend: mongodb\n  database_name: synthetic\n", encoding="utf-8",
        )

    def test_unknown_selection_rejects_every_dispatch_before_operational_access(self):
        for target in ("prepare-preflight", "validate-application", "prepare", "documents", "evidence",
                       "applications", "sheets", "storage", "timing", "editorial", "all", "catalog"):
            with self.subTest(target=target), patch("jobintel.cli._main") as dispatch, \
                    patch("jobintel.cli.load_env_file") as dotenv, \
                    patch("jobintel.preparation_timing.record_event") as timing, \
                    patch("jobintel.storage_bridge.get_store") as store, redirect_stderr(io.StringIO()):
                self.assertEqual(2, cli.main([target, "--account", "other"], root=self.root))
                dispatch.assert_not_called()
                dotenv.assert_not_called()
                timing.assert_not_called()
                store.assert_not_called()
        self.assertFalse(self.context.path("work").exists())

    def test_default_cli_and_process_selection_use_the_same_context(self):
        contexts = []
        for arguments, environ in ((["list"], {}), (["--account=current", "list"], {}),
                                   (["list"], {"JOBINTEL_ACCOUNT": "current"})):
            with patch.dict(os.environ, environ, clear=True), patch("jobintel.cli._main", return_value=0) as dispatch:
                self.assertEqual(0, cli.main(arguments, root=self.root))
                contexts.append(dispatch.call_args.kwargs["context"])
        self.assertEqual([self.context] * 3, contexts)

    def test_conflicting_roots_paths_and_selectors_fail_before_dispatch_or_timing(self):
        foreign = self.root / "foreign"
        foreign.mkdir()
        for arguments, environ in (
            (["prepare", "--project-root", str(foreign)], {}),
            (["prepare", "--registry", str(foreign / "registry")], {}),
            (["prepare", "--sources", str(foreign / "sources")], {}),
            (["prepare", "--account=current"], {"JOBINTEL_ACCOUNT": "other"}),
        ):
            with self.subTest(arguments=arguments), patch.dict(os.environ, environ, clear=True), \
                    patch("jobintel.cli._main") as dispatch, patch("jobintel.preparation_timing.record_event") as timing, \
                    redirect_stderr(io.StringIO()):
                self.assertEqual(2, cli.main(arguments, root=self.root))
                dispatch.assert_not_called()
                timing.assert_not_called()

    def test_common_project_root_selects_only_its_explicit_descriptor(self):
        with patch("jobintel.cli._main", return_value=0) as dispatch:
            self.assertEqual(0, cli.main(["--project-root=" + str(self.root), "list"]))
            self.assertEqual(self.root, dispatch.call_args.kwargs["root"])

    def test_explicit_environment_files_do_not_leak_between_storage_invocations(self):
        observed = []

        def inspect_store(root):
            observed.append(bridge.resource_environment(load_account_context(root))["MONGODB_URI"])
            self.assertNotIn("MONGODB_URI", os.environ)
            return None

        for name in ("a", "b"):
            env_file = self.root / (name + ".env")
            env_file.write_text(f"MONGODB_URI=synthetic-{name}\nJOBINTEL_ACCOUNT=other\n", encoding="utf-8")
            with patch("jobintel.storage_cli.bridge.get_store", side_effect=inspect_store):
                self.assertEqual(0, cli_main(["doctor", "--env", str(env_file)], root=self.root))
        self.assertEqual(["synthetic-a", "synthetic-b"], observed)
        self.assertEqual({}, dict(os.environ))

    def test_dotenv_selector_is_not_used_as_account_provenance(self):
        self._mongo_config()
        with patch("jobintel.mongodb_storage.MongoStore", side_effect=lambda uri, name: SimpleNamespace(close=lambda: None)) as factory:
            with bridge.operation_resources(self.context, environment={"MONGODB_URI": "synthetic-uri", "JOBINTEL_ACCOUNT": "other"}):
                self.assertIsNotNone(bridge.get_store(self.context.path("registry")))
            factory.assert_called_once_with("synthetic-uri", "synthetic")

    def test_resource_scope_restores_credentials_after_failure(self):
        with bridge.operation_resources(self.context, environment={"MONGODB_URI": "outer"}):
            with self.assertRaisesRegex(RuntimeError, "expected"):
                with bridge.operation_resources(self.context, environment={"MONGODB_URI": "inner"}):
                    self.assertEqual("inner", bridge.resource_environment(self.context)["MONGODB_URI"])
                    raise RuntimeError("expected")
            self.assertEqual("outer", bridge.resource_environment(self.context)["MONGODB_URI"])
        self.assertNotIn("MONGODB_URI", bridge.resource_environment(self.context))
        self.assertEqual({}, dict(os.environ))

    def test_storage_cache_keys_follow_effective_credentials_and_database(self):
        self._mongo_config()
        with patch("jobintel.mongodb_storage.MongoStore", side_effect=lambda uri, name: SimpleNamespace(close=lambda: None)) as factory:
            stores = []
            for uri, database in (("a", "one"), ("b", "one"), ("a", "two"), ("a", "one")):
                with bridge.operation_resources(self.context, environment={"MONGODB_URI": uri, "JOBINTEL_DATABASE_NAME": database}):
                    stores.append(bridge.get_store(self.context.path("registry")))
            self.assertEqual(3, factory.call_count)
            self.assertIs(stores[0], stores[3])
            self.assertIsNot(stores[0], stores[1])
            self.assertIsNot(stores[0], stores[2])

    def test_partial_explicit_file_preserves_same_account_default_store_credentials(self):
        self._mongo_config()
        self.context.path("sources").mkdir()
        self.context.path("environment").write_text(
            "MONGODB_URI=default-uri\nJOBINTEL_DATABASE_NAME=default-database\n", encoding="utf-8",
        )
        explicit = self.root / "partial.env"
        for content, process, expected in (
            ("ADZUNA_APP_ID=source-only\n", {}, ("default-uri", "default-database")),
            ("MONGODB_URI=explicit-uri\n", {}, ("explicit-uri", "default-database")),
            ("MONGODB_URI=explicit-uri\nJOBINTEL_DATABASE_NAME=explicit-database\n",
             {"MONGODB_URI": "process-uri", "JOBINTEL_DATABASE_NAME": "process-database"},
             ("process-uri", "process-database")),
        ):
            with self.subTest(content=content, process=process), patch.dict(os.environ, process, clear=True):
                explicit.write_text(content, encoding="utf-8")
                with patch("jobintel.mongodb_storage.MongoStore", return_value=SimpleNamespace(close=lambda: None)) as factory:
                    with bridge.operation_resources(self.context, env_path=explicit):
                        self.assertIsNotNone(bridge.get_store(self.context.path("registry")))
                    factory.assert_called_once_with(*expected)
                self.assertEqual(process, dict(os.environ))
        self.assertEqual({}, dict(os.environ))

    def test_partial_file_scopes_restore_defaults_without_leaking_explicit_values(self):
        self.context.path("sources").mkdir()
        self.context.path("environment").write_text(
            "MONGODB_URI=default-uri\nJOBINTEL_DATABASE_NAME=default-database\n", encoding="utf-8",
        )
        first = self.root / "first.env"
        first.write_text("MONGODB_URI=first-uri\nFIRST_ONLY=value\n", encoding="utf-8")
        second = self.root / "second.env"
        second.write_text("ADZUNA_APP_ID=second-source\nJOBINTEL_ACCOUNT=other\n", encoding="utf-8")
        with bridge.operation_resources(self.context, env_path=first):
            self.assertEqual("first-uri", bridge.resource_environment(self.context)["MONGODB_URI"])
        with bridge.operation_resources(self.context, env_path=second):
            effective = bridge.resource_environment(self.context)
            self.assertEqual("default-uri", effective["MONGODB_URI"])
            self.assertEqual("default-database", effective["JOBINTEL_DATABASE_NAME"])
            self.assertEqual("second-source", effective["ADZUNA_APP_ID"])
            self.assertNotIn("FIRST_ONLY", effective)
        effective = bridge.resource_environment(self.context)
        self.assertEqual("default-uri", effective["MONGODB_URI"])
        self.assertNotIn("ADZUNA_APP_ID", effective)
        self.assertNotIn("FIRST_ONLY", effective)
        self.assertEqual({}, dict(os.environ))

    def test_scoped_file_merge_remains_lazy_and_source_loading_retains_explicit_semantics(self):
        self.context.path("sources").mkdir()
        self.context.path("environment").write_text("MONGODB_URI=default-uri\n", encoding="utf-8")
        explicit = self.root / "partial.env"
        explicit.write_text("ADZUNA_APP_ID=source-only\n", encoding="utf-8")
        with patch("jobintel.storage_bridge.resolve_environment") as resolver:
            with bridge.operation_resources(self.context, env_path=explicit):
                resolver.assert_not_called()
        self.assertEqual({"ADZUNA_APP_ID": "source-only"}, cli.load_env(explicit))

    def test_foreign_operational_root_cannot_use_scope_credentials(self):
        foreign = self.root / "foreign"
        write_file_account_config(foreign)
        with bridge.operation_resources(self.context, environment={"MONGODB_URI": "private-synthetic"}), \
                patch("jobintel.storage_bridge.load_env") as dotenv:
            with self.assertRaises(AccountConfigurationError):
                bridge.get_store(foreign / "registry")
            dotenv.assert_not_called()

    def test_stale_descriptor_rejects_before_vacancy_batch_shortcut(self):
        previous = getattr(bridge._LOCAL, "store", None)
        try:
            with bridge.operation_resources(self.context):
                bridge._LOCAL.store = (self.root, object())
                descriptor = self.context.descriptor_path
                descriptor.write_bytes(descriptor.read_bytes() + b"\n# Changed descriptor\n")
                with patch("jobintel.storage_bridge.load_env") as dotenv:
                    with self.assertRaises(AccountConfigurationError):
                        bridge.get_store(self.context.path("registry"))
                    dotenv.assert_not_called()
                with self.assertRaises(AccountConfigurationError):
                    with bridge.operation_resources(load_account_context(self.root)):
                        self.fail("stale outer operation must not acquire a refreshed inner scope")
        finally:
            bridge._LOCAL.store = previous

    def test_vacancy_batch_rejects_a_changed_destination_before_using_its_store(self):
        self._mongo_config()
        previous = getattr(bridge._LOCAL, "store", None)
        try:
            with patch("jobintel.mongodb_storage.MongoStore", return_value=SimpleNamespace(close=lambda: None)):
                with bridge.operation_resources(self.context, environment={"MONGODB_URI": "a"}):
                    store = bridge.get_store(self.context.path("registry"))
                    bridge._LOCAL.store = (self.root, store)
                    for environment in ({"MONGODB_URI": "b"}, {"JOBINTEL_STORAGE_BACKEND": "yaml"}):
                        with bridge.operation_resources(self.context, environment=environment):
                            with self.assertRaises(AccountConfigurationError):
                                bridge.get_store(self.context.path("registry"))
        finally:
            bridge._LOCAL.store = previous

    def test_configured_storage_requires_descriptor_and_explicit_backend(self):
        path = self.context.reference("data_services")
        for content in (None, "{}", "storage: {}", "storage: []"):
            with self.subTest(content=content):
                if content is None:
                    path.unlink(missing_ok=True)
                else:
                    path.write_text(content, encoding="utf-8")
                with self.assertRaises((FileNotFoundError, ValueError)):
                    bridge.get_store(self.context.path("registry"))
        path.write_text("storage:\n  backend: yaml\n", encoding="utf-8")
        self.context.descriptor_path.unlink()
        with self.assertRaises(AccountConfigurationError):
            bridge.get_store(self.root / "registry")

    def test_bare_file_primitive_without_configuration_remains_descriptor_free(self):
        with tempfile.TemporaryDirectory() as temporary:
            self.assertIsNone(bridge.get_store(Path(temporary) / "registry"))

    def test_workflow_api_rejects_foreign_registry_before_snapshot(self):
        with patch("jobintel.workflow_api.load_catalog_snapshot") as snapshot:
            with self.assertRaises(AccountConfigurationError):
                workflow_summary(self.root, self.root / "foreign/registry", {}, [], context=self.context)
            snapshot.assert_not_called()

    def test_environment_resolution_preserves_process_precedence_without_mutation(self):
        path = self.root / "credentials.env"
        path.write_text("MONGODB_URI=file\nOTHER=file-only\n", encoding="utf-8")
        environment = {"MONGODB_URI": "process"}
        self.assertEqual({"MONGODB_URI": "process", "OTHER": "file-only"}, resolve_environment(path, environ=environment))
        self.assertEqual({"MONGODB_URI": "process"}, environment)
        self.assertEqual({}, dict(os.environ))


if __name__ == "__main__":
    unittest.main()
