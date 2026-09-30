from __future__ import annotations

import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from jobintel.config import apply_env_file, load_env
from jobintel.storage_cli import cli_main


class EnvironmentFileTests(unittest.TestCase):
    def test_apply_env_file_preserves_process_override(self) -> None:
        with TemporaryDirectory() as temporary:
            env_path = Path(temporary) / ".env"
            env_path.write_text("MONGODB_URI=file-uri\nFROM_FILE=value\n", encoding="utf-8")

            with patch.dict(os.environ, {"MONGODB_URI": "process-uri"}, clear=True):
                apply_env_file(env_path, require_exists=True)

                self.assertEqual("process-uri", os.environ["MONGODB_URI"])
                self.assertEqual("value", os.environ["FROM_FILE"])
                self.assertEqual("process-uri", load_env(env_path)["MONGODB_URI"])

    def test_apply_env_file_requires_explicit_path_to_exist(self) -> None:
        with TemporaryDirectory() as temporary:
            with self.assertRaisesRegex(FileNotFoundError, "environment file does not exist"):
                apply_env_file(Path(temporary) / "missing.env", require_exists=True)

    def test_storage_cli_loads_explicit_env_before_opening_store(self) -> None:
        with TemporaryDirectory() as temporary:
            root = Path(temporary) / "worktree"
            root.mkdir()
            env_path = Path(temporary) / "primary.env"
            env_path.write_text("MONGODB_URI=file-uri\n", encoding="utf-8")

            def assert_env(_root: Path) -> None:
                self.assertEqual("file-uri", os.environ["MONGODB_URI"])
                return None

            with patch.dict(os.environ, {}, clear=True), patch(
                "jobintel.storage_cli.bridge.get_store", side_effect=assert_env
            ):
                self.assertEqual(
                    0,
                    cli_main(["doctor", "--project-root", str(root), "--env", str(env_path)]),
                )
