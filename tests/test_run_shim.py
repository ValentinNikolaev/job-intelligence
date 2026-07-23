from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

import run


class RunShimTests(unittest.TestCase):
    def test_missing_runtime_dependencies_reports_pyyaml(self) -> None:
        with patch("run.importlib.util.find_spec", return_value=None):
            self.assertEqual(["PyYAML"], run._missing_runtime_dependencies())

    def test_install_runtime_dependencies_installs_editable_project(self) -> None:
        project_root = Path("project")
        with patch("run.subprocess.check_call") as check_call:
            run._install_runtime_dependencies(project_root)

        check_call.assert_called_once_with(
            [
                run.sys.executable,
                "-m",
                "pip",
                "install",
                "-e",
                str(project_root),
            ]
        )


if __name__ == "__main__":
    unittest.main()
