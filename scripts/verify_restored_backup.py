"""Verify a downloaded backup against an isolated restored MongoDB database."""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import sys
import uuid
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Mapping, Sequence

from bson import json_util
from pymongo.uri_parser import parse_uri


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from jobintel import storage_bridge
from jobintel.backup import (
    _archive_bytes,
    _bson_json_loads,
    _load_manifest,
    _validate_artifact_references,
    verify_backup,
)
from jobintel.catalog_data import load_catalog_vacancies
from jobintel.config import load_env
from jobintel.migration import export_applications
from jobintel.mongodb_storage import MongoStore
from jobintel.sheets_sync import build_export


SCHEMA_VERSION = 1
LOOPBACK_HOSTS = frozenset({"127.0.0.1", "localhost", "::1"})


class VerificationError(ValueError):
    pass


def verify_restored_backup(
    downloaded_backup: Path,
    database: str,
    artifact_output: Path,
) -> dict[str, Any]:
    """Validate restored data and artifacts without changing source or production."""
    if not database.startswith(("jobintel_test_", "jobintel_restore_")):
        raise VerificationError("database must use the isolated jobintel_test_/jobintel_restore_ prefix")
    if len(database.encode("utf-8")) > 63:
        raise VerificationError("isolated database name must be at most 63 UTF-8 bytes")

    verification = verify_backup(downloaded_backup)
    if not verification.get("ok"):
        raise VerificationError("downloaded backup verification failed")
    backup_directory, manifest = _load_manifest(downloaded_backup)
    if manifest.get("backup_type") != "mongodb-logical":
        raise VerificationError("restored verifier requires a mongodb-logical backup")
    expected = _snapshot_from_backup(backup_directory, manifest)

    restored_project = artifact_output.resolve() / "project"
    if not restored_project.is_dir():
        raise VerificationError(f"restored project directory is missing: {restored_project}")

    env = load_env(PROJECT_ROOT / "sources" / ".env")
    test_uri = str(env.get("JOBINTEL_TEST_MONGODB_URI") or "")
    production_uri = str(env.get("MONGODB_URI") or "")
    _validate_test_uri(test_uri, production_uri)

    store = MongoStore(test_uri, database)
    try:
        hello = store.client.admin.command("hello")
        if hello.get("setName") != "rs0":
            raise VerificationError("test MongoDB must report replica set rs0")
        with store.lease(f"verify-restored:{manifest['backup_id']}"):
            actual = store.snapshot()
            snapshot_report = _compare_snapshots(expected, actual)
            reference_report = {
                key: value
                for key, value in _validate_artifact_references(actual, restored_project).items()
                if not str(key).startswith("_")
            }
            invariant_report = _validate_links_and_history(actual)
            exported = build_export(export_applications(store))

        with _restored_store_environment(test_uri, database):
            catalog = load_catalog_vacancies(restored_project / "registry")
        catalog_ids = sorted(item.vacancy_id for item in catalog)
        expected_catalog_ids = sorted(
            str(item["_id"])
            for item in _documents(actual, "vacancies")
            if not item.get("archived")
        )
        if catalog_ids != expected_catalog_ids:
            raise VerificationError("catalog vacancy IDs differ from restored active vacancies")

        result = {
            "schema_version": SCHEMA_VERSION,
            "state": "success",
            "backup_id": manifest["backup_id"],
            "database": database,
            "input_manifest_sha256": _sha256((backup_directory / "manifest.json").read_bytes()),
            "backup_manifest": _manifest_summary(manifest),
            "snapshot": snapshot_report,
            "artifact_references": reference_report,
            "invariants": invariant_report,
            "catalog": {
                "vacancies": len(catalog_ids),
                "vacancy_ids_sha256": _json_sha256(catalog_ids),
            },
            "application_export": {
                "applications": len(exported["applications"]),
                "events": len(exported["events"]),
                "source_revision": exported["source_revision"],
                "payload_sha256": exported["payload_sha256"],
            },
            "source_files_mutated": False,
        }
        result["receipt_sha256"] = _json_sha256(result)
        return result
    finally:
        store.close()
        _close_bridge_stores()


def _snapshot_from_backup(directory: Path, manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    import io
    import zipfile

    raw = _archive_bytes(directory, manifest)
    try:
        with zipfile.ZipFile(io.BytesIO(raw)) as package:
            snapshot = _bson_json_loads(package.read("database/snapshot.json"))
    except (KeyError, OSError, zipfile.BadZipFile) as exc:
        raise VerificationError(f"cannot read database snapshot from backup: {exc}") from exc
    if not isinstance(snapshot, Mapping):
        raise VerificationError("database snapshot must be a mapping")
    return snapshot


def _validate_test_uri(test_uri: str, production_uri: str = "") -> None:
    if not test_uri:
        raise VerificationError("JOBINTEL_TEST_MONGODB_URI is required")
    try:
        parsed = parse_uri(test_uri)
    except Exception as exc:
        raise VerificationError("JOBINTEL_TEST_MONGODB_URI is invalid") from exc
    hosts = {str(host).casefold() for host, _ in parsed.get("nodelist", [])}
    if not hosts or not hosts.issubset(LOOPBACK_HOSTS):
        raise VerificationError("JOBINTEL_TEST_MONGODB_URI must contain loopback hosts only")
    if production_uri and test_uri.strip() == production_uri.strip():
        raise VerificationError("test and production MongoDB URIs must differ")


def _manifest_summary(manifest: Mapping[str, Any]) -> dict[str, Any]:
    parts = manifest.get("parts") if isinstance(manifest.get("parts"), list) else []
    return {
        "backup_type": manifest.get("backup_type"),
        "created_at": manifest.get("created_at"),
        "git_revision": manifest.get("git_revision"),
        "database": copy.deepcopy(manifest.get("database")),
        "sheets": copy.deepcopy(manifest.get("sheets")),
        "archive": copy.deepcopy(manifest.get("archive")),
        "artifact_references": copy.deepcopy(manifest.get("artifact_references")),
        "parts": len(parts),
        "parts_sha256": _json_sha256(parts),
    }


def _compare_snapshots(expected: Mapping[str, Any], actual: Mapping[str, Any]) -> dict[str, Any]:
    expected_collections = expected.get("collections")
    actual_collections = actual.get("collections")
    if not isinstance(expected_collections, Mapping) or not isinstance(actual_collections, Mapping):
        raise VerificationError("snapshot collections must be mappings")
    if set(expected_collections) != set(actual_collections):
        raise VerificationError("restored collection names differ from backup snapshot")

    collection_counts: dict[str, dict[str, int]] = {}
    total_documents = 0
    total_indexes = 0
    document_hashes: dict[str, str] = {}
    index_hashes: dict[str, str] = {}
    for name in sorted(expected_collections):
        expected_documents = _documents(expected, name)
        actual_documents = _documents(actual, name)
        expected_indexes = _indexes(expected, name)
        actual_indexes = _indexes(actual, name)
        expected_document_hash = _bson_sha256(expected_documents)
        actual_document_hash = _bson_sha256(actual_documents)
        expected_index_hash = _json_sha256(_normalized_indexes(expected_indexes))
        actual_index_hash = _json_sha256(_normalized_indexes(actual_indexes))
        if expected_document_hash != actual_document_hash:
            raise VerificationError(f"restored documents differ in collection {name}")
        if expected_index_hash != actual_index_hash:
            raise VerificationError(f"restored indexes differ in collection {name}")
        collection_counts[name] = {
            "documents": len(actual_documents),
            "indexes": len(actual_indexes),
        }
        total_documents += len(actual_documents)
        total_indexes += len(actual_indexes)
        document_hashes[name] = actual_document_hash
        index_hashes[name] = actual_index_hash
    return {
        "exact_match": True,
        "collections": collection_counts,
        "documents": total_documents,
        "indexes": total_indexes,
        "documents_sha256": _json_sha256(document_hashes),
        "indexes_sha256": _json_sha256(index_hashes),
    }


def _documents(snapshot: Mapping[str, Any], collection: str) -> list[Mapping[str, Any]]:
    collections = snapshot.get("collections")
    raw = collections.get(collection) if isinstance(collections, Mapping) else None
    documents = raw.get("documents") if isinstance(raw, Mapping) else None
    if not isinstance(documents, list) or not all(isinstance(item, Mapping) for item in documents):
        raise VerificationError(f"collection {collection} has invalid documents")
    return documents


def _indexes(snapshot: Mapping[str, Any], collection: str) -> list[Mapping[str, Any]]:
    collections = snapshot.get("collections")
    raw = collections.get(collection) if isinstance(collections, Mapping) else None
    indexes = raw.get("indexes") if isinstance(raw, Mapping) else None
    if not isinstance(indexes, list) or not all(isinstance(item, Mapping) for item in indexes):
        raise VerificationError(f"collection {collection} has invalid indexes")
    return indexes


def _normalized_indexes(indexes: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    for raw in indexes:
        item = copy.deepcopy(dict(raw))
        key = item.get("key")
        if not isinstance(key, Mapping):
            raise VerificationError("index key must be a mapping")
        item["key"] = [[str(field), direction] for field, direction in key.items()]
        normalized.append(item)
    return sorted(normalized, key=lambda item: str(item.get("name") or ""))


def _validate_links_and_history(snapshot: Mapping[str, Any]) -> dict[str, Any]:
    vacancies = {str(item["_id"]): item for item in _documents(snapshot, "vacancies")}
    prefilters = {str(item["_id"]): item for item in _documents(snapshot, "prefilter_rejections")}
    applications = {str(item["_id"]): item for item in _documents(snapshot, "applications")}
    events = {str(item["_id"]): item for item in _documents(snapshot, "status_events")}
    history_entries = 0
    for vacancy_id, vacancy in vacancies.items():
        meta = vacancy.get("meta")
        history = meta.get("status_history") if isinstance(meta, Mapping) else None
        if not isinstance(history, list) or not history:
            raise VerificationError(f"vacancy {vacancy_id} has invalid status_history")
        timestamps = [str(item.get("changed_at") or "") for item in history if isinstance(item, Mapping)]
        if len(timestamps) != len(history) or any(not value for value in timestamps):
            raise VerificationError(f"vacancy {vacancy_id} has incomplete status_history")
        if timestamps != sorted(timestamps):
            raise VerificationError(f"vacancy {vacancy_id} status_history is not chronological")
        if history[-1].get("status") != meta.get("status"):
            raise VerificationError(f"vacancy {vacancy_id} status differs from status_history")
        history_entries += len(history)

    for identity in _documents(snapshot, "source_identities"):
        unknown_vacancies = set(map(str, identity.get("vacancy_ids") or [])) - set(vacancies)
        unknown_prefilters = set(map(str, identity.get("prefilter_ids") or [])) - set(prefilters)
        if unknown_vacancies or unknown_prefilters:
            raise VerificationError(f"source identity {identity['_id']} has dangling owners")
    for application_id, application in applications.items():
        if str(application.get("vacancy_id")) not in vacancies:
            raise VerificationError(f"application {application_id} has a dangling vacancy")
        applied_event_id = application.get("applied_event_id")
        if applied_event_id and str(applied_event_id) not in events:
            raise VerificationError(f"application {application_id} has a dangling applied event")
    linked_events = 0
    for event_id, event in events.items():
        if str(event.get("vacancy_id")) not in vacancies:
            raise VerificationError(f"status event {event_id} has a dangling vacancy")
        linked = event.get("application_id")
        if linked:
            linked_events += 1
            if str(linked) not in applications:
                raise VerificationError(f"status event {event_id} has a dangling application")
    for collection in ("feedback", "artifact_manifests"):
        for item in _documents(snapshot, collection):
            if str(item.get("vacancy_id")) not in vacancies:
                raise VerificationError(f"{collection} {item['_id']} has a dangling vacancy")
    return {
        "vacancies": len(vacancies),
        "prefilter_rejections": len(prefilters),
        "applications": len(applications),
        "status_events": len(events),
        "linked_status_events": linked_events,
        "status_history_entries": history_entries,
        "dangling_references": 0,
    }


@contextmanager
def _restored_store_environment(uri: str, database: str):
    keys = ("MONGODB_URI", "JOBINTEL_DATABASE_NAME", "JOBINTEL_STORAGE_BACKEND")
    previous = {key: os.environ.get(key) for key in keys}
    os.environ.update(
        {
            "MONGODB_URI": uri,
            "JOBINTEL_DATABASE_NAME": database,
            "JOBINTEL_STORAGE_BACKEND": "mongodb",
        }
    )
    try:
        yield
    finally:
        _close_bridge_stores()
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def _close_bridge_stores() -> None:
    for store in list(storage_bridge._STORES.values()):
        store.close()
    storage_bridge._STORES.clear()


def _bson_sha256(value: Any) -> str:
    text = json_util.dumps(
        value,
        json_options=json_util.CANONICAL_JSON_OPTIONS,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _json_sha256(value: Any) -> str:
    raw = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _sha256(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _write_receipt(path: Path, value: Mapping[str, Any]) -> None:
    path = path.resolve()
    if path.exists():
        raise FileExistsError(f"receipt already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    raw = (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2, default=str) + "\n").encode("utf-8")
    try:
        with temporary.open("xb") as handle:
            handle.write(raw)
            handle.flush()
            os.fsync(handle.fileno())
        os.rename(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, dest="downloaded_backup")
    parser.add_argument("--database", required=True)
    parser.add_argument("--artifact-output", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path, dest="receipt")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        result = verify_restored_backup(
            args.downloaded_backup,
            args.database,
            args.artifact_output,
        )
        exit_code = 0
    except Exception as exc:
        message = str(exc) if isinstance(exc, (VerificationError, FileNotFoundError, ValueError)) else type(exc).__name__
        result = {
            "schema_version": SCHEMA_VERSION,
            "state": "failed",
            "database": args.database,
            "error": {"type": type(exc).__name__, "message": message},
            "source_files_mutated": False,
        }
        result["receipt_sha256"] = _json_sha256(result)
        exit_code = 1
    try:
        _write_receipt(args.receipt, result)
    except Exception as exc:
        print(f"Cannot persist verification receipt: {type(exc).__name__}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, default=str))
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
