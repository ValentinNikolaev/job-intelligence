from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path


def _missing_runtime_dependencies() -> list[str]:
    missing: list[str] = []
    if importlib.util.find_spec("yaml") is None:
        missing.append("PyYAML")
    return missing


def _install_runtime_dependencies(project_root: Path) -> None:
    subprocess.check_call(
        [
            sys.executable,
            "-m",
            "pip",
            "install",
            "-e",
            str(project_root),
        ]
    )


def _main() -> int:
    project_root = Path(__file__).resolve().parent
    missing = _missing_runtime_dependencies()
    if missing:
        print(
            "Installing missing runtime dependencies: " + ", ".join(missing),
            file=sys.stderr,
        )
        _install_runtime_dependencies(project_root)

    from jobintel.cli import main

    return main()


if __name__ == "__main__":
    raise SystemExit(_main())
