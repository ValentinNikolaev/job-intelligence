"""Route legacy path-shaped operations to the explicitly selected source of truth.

Paths remain artifact identities, not a MongoDB fallback. Configuration and application
packages stay files; vacancy metadata, descriptions, matches, triage and logs do not.
"""
from __future__ import annotations

import hashlib
import json
import os
import uuid
from functools import wraps
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml

from .config import load_env

_STORES: dict[tuple[str, str, str], Any] = {}
_FIELDS = {"meta.yaml": "meta", "match.yaml": "match", "triage.yaml": "triage",
           "job.md": "job_text", "company.md": "company_text"}
_LOGS = {"manual-status-log.yaml", "codex-usage.yaml", "source-api-usage.yaml", "application-confirmations.yaml"}


def project_root(path: Path) -> Path | None:
    path = path.resolve()
    for parent in (path, *path.parents):
        if parent.name == "registry":
            return parent.parent
        if (parent / "config" / "data-services.yaml").is_file():
            return parent
    return None


def get_store(path: Path):
    root = project_root(path)
    if root is None:
        return None
    config_path = root / "config" / "data-services.yaml"
    # Fixture registries without project configuration never acquire production access.
    if not config_path.is_file():
        return None
    config = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    env = load_env(root / "sources" / ".env")
    backend = env.get("JOBINTEL_STORAGE_BACKEND", config.get("storage", {}).get("backend", "yaml"))
    if backend == "yaml":
        if config.get("storage", {}).get("cutover_verified"):
            raise RuntimeError("YAML rollback is disabled after cutover; export and reconcile MongoDB first")
        return None
    if backend != "mongodb":
        raise ValueError(f"unknown storage backend: {backend}")
    uri = env.get("MONGODB_URI", "")
    if not uri:
        raise RuntimeError("MongoDB backend requires MONGODB_URI; YAML fallback is disabled")
    name = env.get("JOBINTEL_DATABASE_NAME", config.get("storage", {}).get("database_name", "job_intelligence"))
    key = (str(root), hashlib.sha256(uri.encode()).hexdigest(), name)
    if key not in _STORES:
        from .mongodb_storage import MongoStore
        _STORES[key] = MongoStore(uri, name)
    return _STORES[key]


def _address(path: Path):
    root = project_root(path)
    if root is None:
        return None
    try:
        parts = path.resolve().relative_to(root / "registry").parts
    except ValueError:
        return None
    if len(parts) == 3 and parts[0] in {"jobs", "rejected"} and parts[2] in _FIELDS:
        return ("vacancy", parts[0], parts[1], _FIELDS[parts[2]])
    if len(parts) == 1 and parts[0] in _LOGS:
        return ("log", parts[0])
    return None


def _document(path: Path):
    address = _address(path)
    if address is None:
        return None, None, None
    store = get_store(path)
    if store is None:
        return None, None, None
    if address[0] == "log":
        return store, address, store.get("operational_logs", address[1])
    return store, address, store.get_by_directory(address[2], scope=address[1])


def exists(path: Path) -> bool:
    store, address, doc = _document(path)
    if store is None:
        return path.is_file()
    return bool(doc is not None and (address[0] == "log" or doc.get(address[3]) is not None))


def read_text(path: Path, *, encoding: str = "utf-8") -> str:
    store, address, doc = _document(path)
    if store is None:
        return path.read_text(encoding=encoding)
    if doc is None:
        raise FileNotFoundError(f"operational record missing in MongoDB: {path}")
    value = doc.get("payload") if address[0] == "log" else doc.get(address[3])
    if value is None:
        raise FileNotFoundError(f"operational field missing in MongoDB: {path}")
    return value if isinstance(value, str) else yaml.safe_dump(value, allow_unicode=True, sort_keys=False)


def load_mapping(path: Path) -> Any:
    return yaml.safe_load(read_text(path))


def metadata_paths(scope_root: Path, *, include_archived: bool = False) -> list[Path]:
    store = get_store(scope_root)
    if store is None:
        return sorted(scope_root.glob("*/meta.yaml"))
    return [scope_root / doc["directory"] / "meta.yaml"
            for doc in store.list_vacancies(scope=scope_root.name, include_archived=include_archived)]


@contextmanager
def mutation(path: Path, owner: str = "operational-write"):
    store = get_store(path)
    if store is None:
        yield None
        return
    with store.lease(owner):
        with store.transaction():
            yield store


def transactional(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        root = getattr(self, "registry_root", None) or getattr(self, "root", None) or getattr(self, "path", None)
        with mutation(root, method.__qualname__):
            # A registry object can outlive another writer's transaction.
            if get_store(root) is not None:
                for cache_name in ("_entries_cache", "_entry_cache"):
                    if hasattr(self, cache_name):
                        setattr(self, cache_name, None)
            return method(self, *args, **kwargs)
    return wrapped


def exclusive(method):
    @wraps(method)
    def wrapped(self, *args, **kwargs):
        root = getattr(self, "registry_root", None) or getattr(self, "root", None)
        store = get_store(root)
        if store is None:
            return method(self, *args, **kwargs)
        with store.lease(method.__qualname__):
            return method(self, *args, **kwargs)
    return wrapped


def write_operational(path: Path, content: str) -> bool | None:
    """None means a file artifact; bool means an operational write was handled."""
    address = _address(path)
    store = get_store(path) if address else None
    if store is None:
        return None
    with mutation(path) as store:
        if address[0] == "log":
            payload = yaml.safe_load(content)
            previous = store.get("operational_logs", address[1])
            if previous and previous.get("payload") == payload:
                return False
            if address[1] == "manual-status-log.yaml":
                old_events = (previous or {}).get("payload", {}).get("events", [])
                events = payload.get("events", [])
                if events[:len(old_events)] != old_events:
                    raise ValueError("manual status history is append-only")
                affected = {event["vacancy_id"] for event in events[len(old_events):]}
                from .migration import project_vacancy_history
                for vacancy_id in sorted(affected):
                    vacancy = store.get("vacancies", vacancy_id)
                    if vacancy is None:
                        raise ValueError("manual status event refers to an unknown vacancy")
                    applications, history, _ = project_vacancy_history(vacancy, events)
                    for collection, records in (("applications", applications), ("status_events", history)):
                        for record in records:
                            prior = store.get(collection, record["_id"])
                            if collection == "applications" and prior and not record.get("package_locator"):
                                record["package_locator"] = prior.get("package_locator")
                            store.put(collection, record["_id"], record,
                                      expected_revision=prior["revision"] if prior else 0)
            store.put("operational_logs", address[1], {"payload": payload},
                      expected_revision=previous["revision"] if previous else 0)
            return True
        doc = store.get_by_directory(address[2], scope=address[1])
        field = address[3]
        value = content if field.endswith("_text") else yaml.safe_load(content)
        if doc is None:
            if field != "meta":
                raise RuntimeError("create vacancy metadata before writing its operational fields")
            meta = value
            return bool(store.save_vacancy(address[2], meta, "", None, scope=address[1], expected_revision=0))
        if doc.get(field) == value:
            return False
        if field == "meta":
            store.save_vacancy(address[2], value, doc.get("job_text", ""), doc.get("company_text"),
                               scope=address[1], expected_revision=doc["revision"])
        else:
            updated = {k: v for k, v in doc.items() if k not in {"_id", "revision"}}
            updated[field] = value
            collection = "prefilter_rejections" if address[1] == "rejected" else "vacancies"
            store.put(collection, doc["_id"], updated, expected_revision=doc["revision"])
        return True


def create_vacancy(directory: Path, meta: dict, job_text: str, company_text: str | None):
    store = get_store(directory)
    if store is None:
        return False
    with mutation(directory, "create-vacancy"):
        store.save_vacancy(directory.name, meta, job_text, company_text,
                           scope=directory.parent.name, expected_revision=0)
    return True


def archive_vacancy(directory: Path, archive_relative: str | None) -> None:
    store = get_store(directory)
    if store is None:
        return
    with mutation(directory, "archive-vacancy"):
        doc = store.get_by_directory(directory.name, scope=directory.parent.name)
        if doc:
            payload = {k: v for k, v in doc.items() if k not in {"_id", "revision"}}
            payload.update(archived=True, archive_path=archive_relative)
            collection = "prefilter_rejections" if directory.parent.name == "rejected" else "vacancies"
            store.put(collection, doc["_id"], payload, expected_revision=doc["revision"])


def record_package(directory: Path, application: Path) -> None:
    store = get_store(directory)
    if store is None:
        return
    with mutation(directory, "record-package"):
        doc = store.get_by_directory(directory.name, scope="jobs")
        from .migration import stable_id
        root = project_root(directory)
        files = [{"path": p.relative_to(root).as_posix(), "size": p.stat().st_size,
                  "sha256": hashlib.sha256(p.read_bytes()).hexdigest()}
                 for package in sorted(directory.glob("application*")) if package.is_dir()
                 for p in sorted(package.rglob("*")) if p.is_file()]
        locator = directory.relative_to(root).as_posix()
        key = stable_id("jobintel:package:v1", doc["_id"], locator)
        previous = store.get("artifact_manifests", key)
        store.put("artifact_manifests", key, {"schema_version": 1, "vacancy_id": doc["_id"], "directory": directory.name,
                  "evidence_locator": locator + "/meta.yaml", "files": files},
                  expected_revision=previous["revision"] if previous else 0)
