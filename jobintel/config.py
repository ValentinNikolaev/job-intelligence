from __future__ import annotations

import os
from pathlib import Path


def load_env_file(path: Path) -> dict[str, str]:
    """Read dotenv values without inheriting the current process environment."""
    values: dict[str, str] = {}
    if path.exists():
        for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("export "):
                line = line[7:].lstrip()
            if "=" not in line:
                raise ValueError(f"invalid .env line {line_number}: expected NAME=value")
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if not key:
                raise ValueError(f"invalid .env line {line_number}: empty name")
            if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
                value = value[1:-1]
            values[key] = value
    return values


def apply_env_file(path: Path, *, require_exists: bool = False) -> None:
    """Load dotenv values into this process without replacing environment overrides."""
    if require_exists and not path.is_file():
        raise FileNotFoundError(f"environment file does not exist: {path}")
    for key, value in load_env_file(path).items():
        os.environ.setdefault(key, value)


def load_env(path: Path) -> dict[str, str]:
    values = load_env_file(path)

    # Process environment deliberately wins over the shared file.
    values.update({key: value for key, value in os.environ.items() if value is not None})
    return values

