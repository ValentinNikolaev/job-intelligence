"""Deterministic storage operations; no Google or model API calls."""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

import yaml

from .config import load_env
from . import storage_bridge as bridge


def _write(path, value):
    if path is not None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n", encoding="utf-8")


def configured_store(root, database=None):
    from .mongodb_storage import MongoStore
    config = yaml.safe_load((root / "config/data-services.yaml").read_text(encoding="utf-8"))
    env = load_env(root / "sources/.env")
    uri = env.get("MONGODB_URI", "")
    if not uri:
        raise ValueError("MONGODB_URI is required; no file fallback is permitted")
    return MongoStore(uri, database or env.get("JOBINTEL_DATABASE_NAME") or config["storage"]["database_name"])


def cli_main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=["doctor", "inventory", "plan", "migrate", "reconcile", "vacancy-context", "export-applications", "backup", "verify-backup", "restore"])
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--database")
    parser.add_argument("--selector")
    parser.add_argument("--artifact-output", type=Path)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true")
    mode.add_argument("--dry-run", action="store_true")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--sheets-snapshot", type=Path)
    args = parser.parse_args(argv)
    root = args.project_root.resolve()
    store = None
    try:
        from .migration import build_plan, import_plan, reconcile, export_applications
        if args.operation == "doctor":
            store = bridge.get_store(root)
            if store is None:
                result = {"backend": "yaml", "cutover": False, "ok": True}
            else:
                if args.ci and os.environ.get("JOBINTEL_MONGODB_NETWORK_READY") != "true":
                    raise ValueError("CI MongoDB access requires a verified temporary /32 network grant")
                hello = store.client.admin.command("hello")
                if not hello.get("setName"):
                    raise ValueError("MongoDB must be a replica set")
                schema = store.get("storage_schema", "operational")
                if not schema or schema.get("schema_version") != 1:
                    raise ValueError("MongoDB storage schema is missing or incompatible")
                result = {"backend": "mongodb", "database": store.database_name, "replica_set": True,
                          "vacancies": len(store.list_vacancies()), "ok": True}
        elif args.operation in {"inventory", "plan", "migrate", "reconcile"}:
            plan = json.loads(args.input.read_text(encoding="utf-8")) if args.input else build_plan(root)
            if args.operation == "inventory":
                result = plan["manifest"]
            elif args.operation == "plan":
                result = plan
            elif args.operation == "migrate" and not args.apply:
                result = import_plan(None, plan, dry_run=True)
            else:
                store = configured_store(root, args.database)
                if args.operation == "migrate":
                    store.ensure_schema()
                    result = import_plan(store, plan, dry_run=False)
                else:
                    with store.lease("migration:reconcile"):
                        result = reconcile(store, plan)
        elif args.operation == "vacancy-context":
            if not args.selector or args.selector.casefold() == "all":
                raise ValueError("vacancy-context requires one explicit --selector")
            from .applications import resolve_job_directories
            directories = resolve_job_directories(root / "registry", args.selector)
            if len(directories) != 1:
                raise ValueError("vacancy-context requires exactly one vacancy")
            directory = directories[0]
            with bridge.mutation(directory, "vacancy-context") as store:
                result = {"schema_version": 1, "directory": directory.name,
                          "backend": "mongodb" if store else "yaml", "fields": {}}
                for filename in bridge._FIELDS:
                    path = directory / filename
                    if bridge.exists(path):
                        result["fields"][filename] = bridge.read_text(path)
                if store:
                    result["source_revision"] = store.get_by_directory(directory.name)["revision"]
        elif args.operation == "export-applications":
            source = json.loads(args.input.read_text(encoding="utf-8")) if args.input else bridge.get_store(root)
            if source is None:
                source = build_plan(root)
            if isinstance(source, dict):
                result = export_applications(source, package_root=root)
            else:
                with source.lease("sheets:export"):
                    result = export_applications(source, package_root=root)
            from .sheets_sync import build_export
            result = build_export(result)
        elif args.operation == "backup":
            if args.output is None:
                raise ValueError("backup requires --output directory")
            from .backup import create_backup, create_yaml_backup
            sheets = json.loads(args.sheets_snapshot.read_text(encoding="utf-8")) if args.sheets_snapshot else None
            if sheets is None:
                raise ValueError("backup requires --sheets-snapshot with a separately timed connector read")
            store = bridge.get_store(root)
            if store is None:
                result = create_yaml_backup(root, args.output, sheets_snapshot=sheets)
            else:
                result = create_backup(store, root, args.output, sheets_snapshot=sheets)
            print(json.dumps(result, ensure_ascii=False, default=str))
            return 0
        elif args.operation == "verify-backup":
            if args.input is None:
                raise ValueError("verify-backup requires --input")
            from .backup import verify_backup
            result = verify_backup(args.input)
        else:
            if args.input is None or not args.database or not args.database.startswith(("jobintel_test_", "jobintel_restore_")):
                raise ValueError("restore requires --input and an isolated jobintel_test_/jobintel_restore_ database")
            from .mongodb_storage import MongoStore
            from .backup import restore_backup
            uri = load_env(root / "sources/.env").get("JOBINTEL_TEST_MONGODB_URI", "")
            if not uri:
                raise ValueError("restore requires a separate JOBINTEL_TEST_MONGODB_URI; production URI is never used")
            store = MongoStore(uri, args.database)
            result = restore_backup(store, args.input, artifact_output=args.artifact_output)
        _write(args.output, result)
        if args.operation == "plan":
            print(json.dumps(result["manifest"], ensure_ascii=False, default=str))
        else:
            print(json.dumps(result, ensure_ascii=False, default=str))
        return 1 if isinstance(result, dict) and result.get("ok") is False else 0
    except Exception as exc:
        # Driver errors may include connection details; report their class, not URI-bearing text.
        message = str(exc) if isinstance(exc, (ValueError, FileNotFoundError)) else type(exc).__name__
        print("Storage operation failed: " + message, file=sys.stderr)
        return 1
    finally:
        if store is not None and store not in bridge._STORES.values():
            store.close()


if __name__ == "__main__":
    raise SystemExit(cli_main())
