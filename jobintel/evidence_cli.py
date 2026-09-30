"""Explicit source-bank commands. Generated applications never become evidence."""
from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path

import yaml

from .evidence import EvidenceError, bootstrap_evidence_bank, validate_evidence_bank


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8-sig"))


def _output_path(root: Path, path: Path) -> Path:
    target = (root / path).resolve()
    allowed = [(root / ".codex-work").resolve(), (root / "registry" / "evidence").resolve()]
    if not any(target.is_relative_to(directory) for directory in allowed) or target.suffix not in {".yaml", ".yml"}:
        raise EvidenceError("evidence outputs must be YAML under .codex-work/ or registry/evidence/")
    return target


def main(argv: list[str] | None = None, *, root: Path) -> int:
    parser = argparse.ArgumentParser(description="Validate and maintain source-backed candidate evidence.")
    commands = parser.add_subparsers(dest="action", required=True)
    validate = commands.add_parser("validate", help="Check source quotes, hashes and verification provenance")
    validate.add_argument("--bank", type=Path, default=Path("registry/evidence/achievements.yaml"))
    bootstrap = commands.add_parser("bootstrap", help="Seal selected source excerpts as unverified; never overwrite")
    bootstrap.add_argument("--input", type=Path, required=True)
    bootstrap.add_argument("--output", type=Path, required=True)
    publish = commands.add_parser("publish", help="Publish a reviewed bank while preserving retractions")
    publish.add_argument("--input", type=Path, required=True)
    publish.add_argument("--output", type=Path, default=Path("registry/evidence/achievements.yaml"))
    args = parser.parse_args(argv)
    try:
        if args.action == "validate":
            receipt = validate_evidence_bank(_load(root / args.bank), root)
        else:
            loaded = _load(root / args.input)
            bank = bootstrap_evidence_bank(root, loaded) if args.action == "bootstrap" else loaded
            receipt = validate_evidence_bank(bank, root)
            output = _output_path(root, args.output)
            if output.exists():
                if args.action == "bootstrap":
                    raise EvidenceError("bootstrap never overwrites an existing bank")
                previous = _load(output)
                old_entries = {entry["id"]: entry for entry in previous["entries"]}
                new_entries = {entry["id"]: entry for entry in bank["entries"]}
                for identifier, entry in old_entries.items():
                    if entry["status"] in {"cannot-confirm", "retracted"} and new_entries.get(identifier) != entry:
                        raise EvidenceError(f"preserve {identifier}: cannot-confirm/retracted evidence is immutable; add separately sourced evidence instead")
                    if identifier not in new_entries:
                        raise EvidenceError(f"preserve {identifier}: retract evidence instead of deleting its history")
            output.parent.mkdir(parents=True, exist_ok=True)
            descriptor, temp_name = tempfile.mkstemp(dir=output.parent, suffix=".tmp")
            try:
                with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(yaml.safe_dump(bank, allow_unicode=True, sort_keys=False))
                os.replace(temp_name, output)
            finally:
                Path(temp_name).unlink(missing_ok=True)
            receipt["output"] = str(output.relative_to(root.resolve()))
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        print(f"Evidence error: {exc}")
        return 1
