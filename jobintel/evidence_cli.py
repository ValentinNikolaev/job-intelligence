"""Explicit source-bank commands. Generated applications never become evidence."""
from __future__ import annotations

import argparse
import sys
import json
import os
import tempfile
from pathlib import Path

from .accounts import AccountConfigurationError, AccountContext, resolve_account_arguments
from .storage_bridge import operation_resources

import yaml

from .evidence import EvidenceError, bootstrap_evidence_bank, validate_evidence_bank, evidence_questions
from .preparation_context import PreparationContext, load_preparation_context


def _load(path: Path):
    return yaml.safe_load(path.read_text(encoding="utf-8-sig"))


def _output_path(root: Path, path: Path, context: PreparationContext) -> Path:
    target = (root / path).resolve()
    allowed = [(root / ".codex-work").resolve(), context.evidence_bank.parent]
    if (not target.is_relative_to(root)
            or not any(target.is_relative_to(directory) for directory in allowed)
            or target.is_relative_to(context.candidate_directory)
            or target.suffix not in {".yaml", ".yml"}):
        raise EvidenceError("evidence outputs must be YAML under .codex-work/ or the configured evidence directory")
    return target


def main(argv=None, *, root: Path | None = None, context: AccountContext | None = None) -> int:
    try:
        context, arguments = resolve_account_arguments(
            list(sys.argv[1:] if argv is None else argv), root=root, context=context,
            default_root=Path(__file__).resolve().parents[1],
        )
        with operation_resources(context):
            return _main(arguments, root=context.project_root)
    except AccountConfigurationError as exc:
        print(f"Account configuration error: {exc}", file=sys.stderr)
        return 2


def _main(argv=None, *, root: Path) -> int:
    parser = argparse.ArgumentParser(description="Validate and maintain source-backed candidate evidence.", allow_abbrev=False)
    parser.add_argument("--account", help="account identifier (default: current)")
    parser.add_argument("--project-root", type=Path, help="account project directory")
    commands = parser.add_subparsers(dest="action", required=True)
    validate = commands.add_parser("validate", help="Check source quotes, hashes and verification provenance")
    validate.add_argument("--bank", type=Path)
    questions = commands.add_parser('questions', help='List missing achievement and measurement context without changing evidence')
    questions.add_argument('--bank', type=Path)
    questions.add_argument('--id', dest='identifiers', action='append', default=[])
    bootstrap = commands.add_parser("bootstrap", help="Seal selected source excerpts as unverified; never overwrite")
    bootstrap.add_argument("--input", type=Path, required=True)
    bootstrap.add_argument("--output", type=Path, required=True)
    publish = commands.add_parser("publish", help="Publish a reviewed bank while preserving retractions")
    publish.add_argument("--input", type=Path, required=True)
    publish.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    try:
        root = root.resolve()
        context = load_preparation_context(root)
        if args.action == 'questions':
            receipt = evidence_questions(
                _load(root / args.bank if args.bank else context.evidence_bank),
                root, args.identifiers, context=context,
            )
        elif args.action == "validate":
            receipt = validate_evidence_bank(
                _load(root / args.bank if args.bank else context.evidence_bank), root, context=context
            )
        else:
            loaded = _load(root / args.input)
            bank = bootstrap_evidence_bank(root, loaded, context=context) if args.action == "bootstrap" else loaded
            receipt = validate_evidence_bank(bank, root, context=context)
            output = _output_path(root, args.output or context.evidence_bank, context)
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
            receipt["output"] = output.relative_to(root).as_posix()
        receipt["preparation_context_version"] = context.version
        print(json.dumps(receipt, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, TypeError, KeyError, yaml.YAMLError) as exc:
        print(f"Evidence error: {exc}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
