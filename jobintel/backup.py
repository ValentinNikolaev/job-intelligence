"""Consistent, chunked backups and isolated restore drills.

Drive delivery is deliberately outside this module.  The deterministic code creates
and verifies local parts; a Codex task uploads those exact parts and reads the remote
manifest back before declaring delivery successful.
"""
from __future__ import annotations

import hashlib
import io
import json
import os
import subprocess
import tempfile
import uuid
import zipfile
from datetime import date, datetime, timezone
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Mapping, Protocol, Sequence

from .migration import build_plan, import_plan, reconcile


BACKUP_SCHEMA_VERSION = 1
DEFAULT_PART_SIZE = 32 * 1024 * 1024
MANIFEST_NAME = "manifest.json"
_INCLUDE_ROOTS = (
    ".agents",
    ".github",
    "registry",
    "config",
    "docs",
    "jobintel",
    "prompts",
    "scripts",
    "sources",
    "tests",
)
_INCLUDE_FILES = ("AGENTS.md", "README.md", "TECHNICAL_README.md", "pyproject.toml", "run.py")
_SECRET_NAMES = {".env", "credentials.json", "service-account.json", "secrets.json"}
_SECRET_SUFFIXES = {".key", ".pem", ".p12", ".pfx", ".jks", ".keystore"}


class BackupStore(Protocol):
    database_name: str
    def ensure_schema(self) -> None: ...
    def lease(self, owner: str, *args: Any, **kwargs: Any): ...
    def snapshot(self) -> Mapping[str, Any]: ...
    def restore_snapshot(self, snapshot: Mapping[str, Any], *, require_empty: bool = True) -> Mapping[str, Any]: ...
    def list(self, collection: str, *args: Any, **kwargs: Any) -> Sequence[Mapping[str, Any]]: ...


def create_yaml_backup(
    root: Path,
    output: Path,
    *,
    sheets_snapshot: Mapping[str, Any] | None = None,
    part_size: int = DEFAULT_PART_SIZE,
) -> dict[str, Any]:
    """Create the required pre-cutover backup from the legacy YAML source."""
    root = root.resolve()
    plan = build_plan(root)
    source_snapshot = {
        "collections": {
            name: {"documents": documents}
            for name, documents in plan["collections"].items()
        }
    }
    artifact_reference_check = _validate_artifact_references(source_snapshot, root)
    payloads: dict[str, bytes] = {
        "migration/plan.json": _json_bytes(plan),
        **_compact_archive_payloads(source_snapshot, root),
    }
    sheets_meta = _add_sheets_snapshot(payloads, sheets_snapshot)
    return _create(
        root,
        output,
        backup_type="yaml-premigration",
        payloads=payloads,
        source_manifest=plan["manifest"],
        database_snapshot=None,
        sheets_meta=sheets_meta,
        artifact_reference_check=artifact_reference_check,
        part_size=part_size,
    )


def create_backup(
    store: BackupStore,
    root: Path,
    output: Path,
    *,
    sheets_snapshot: Mapping[str, Any] | None = None,
    part_size: int = DEFAULT_PART_SIZE,
) -> dict[str, Any]:
    """Create one logical DB+artifact backup while the shared writer lease is held."""
    root = root.resolve()
    backup_id = _backup_id()
    with store.lease(f"backup:{backup_id}"):
        snapshot = dict(store.snapshot())
        artifact_reference_check = _validate_artifact_references(snapshot, root)
        payloads: dict[str, bytes] = {
            "database/snapshot.json": _bson_json_bytes(snapshot),
            **_compact_archive_payloads(snapshot, root),
        }
        sheets_meta = _add_sheets_snapshot(payloads, sheets_snapshot)
        # Artifact enumeration and reads remain inside the same global lease.  All
        # operational writers use that lease, so this is the Free/Flex-safe window.
        return _create(
            root,
            output,
            backup_type="mongodb-logical",
            payloads=payloads,
            source_manifest=None,
            database_snapshot=snapshot,
            sheets_meta=sheets_meta,
            artifact_reference_check=artifact_reference_check,
            part_size=part_size,
            backup_id=backup_id,
        )


def _create(
    root: Path,
    output: Path,
    *,
    backup_type: str,
    payloads: dict[str, bytes],
    source_manifest: Mapping[str, Any] | None,
    database_snapshot: Mapping[str, Any] | None,
    sheets_meta: Mapping[str, Any] | None,
    artifact_reference_check: Mapping[str, Any] | None,
    part_size: int,
    backup_id: str | None = None,
) -> dict[str, Any]:
    if part_size < 1024:
        raise ValueError("backup part_size must be at least 1024 bytes")
    backup_id = backup_id or _backup_id()
    destination = output.resolve() / backup_id
    destination.mkdir(parents=True, exist_ok=False)
    object_manifest: list[dict[str, Any]] = []
    try:
        for relative in _project_files(root):
            raw = _repo_bytes(root, relative)
            archive_name = _safe_archive_name(f"project/{relative}")
            payloads[archive_name] = raw
        _validate_payload_references(
            payloads,
            artifact_reference_check.get("_required", []) if artifact_reference_check else [],
        )
        for name, raw in sorted(payloads.items()):
            _safe_archive_name(name)
            object_manifest.append(
                {"path": name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
            )
        content = {
            "schema_version": BACKUP_SCHEMA_VERSION,
            "backup_id": backup_id,
            "backup_type": backup_type,
            "objects": object_manifest,
        }
        payloads["content-manifest.json"] = _json_bytes(content)
        archive_path = destination / f".{backup_id}.zip.tmp"
        with zipfile.ZipFile(archive_path, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=6) as archive:
            for name, raw in sorted(payloads.items()):
                archive.writestr(_zip_info(name), raw)
        parts = _split_archive(archive_path, destination, backup_id, part_size)
        archive_path.unlink()
        now = _utcnow()
        manifest = {
            "schema_version": BACKUP_SCHEMA_VERSION,
            "backup_id": backup_id,
            "backup_type": backup_type,
            "created_at": now,
            "git_revision": _git_revision(root),
            "database": {
                "name": database_snapshot.get("database") if database_snapshot else None,
                "captured_at": _json_value(database_snapshot.get("captured_at")) if database_snapshot else None,
                "collections": _snapshot_counts(database_snapshot),
            },
            "sheets": dict(sheets_meta) if sheets_meta else {"included": False, "captured_at": None},
            "artifact_references": {
                key: value
                for key, value in dict(artifact_reference_check or {"files": 0, "bytes": 0}).items()
                if not str(key).startswith("_")
            },
            "legacy_source": dict(source_manifest) if source_manifest else None,
            "objects": object_manifest,
            "parts": parts,
            "archive": {
                "size": sum(int(part["size"]) for part in parts),
                "sha256": _parts_sha256(destination, parts),
            },
            "delivery": {"destination": None, "uploaded_at": None, "readback_verified": False},
        }
        _atomic_write(destination / MANIFEST_NAME, _json_bytes(manifest))
        verification = verify_backup(destination)
        if not verification["ok"]:
            raise ValueError("new backup failed local verification")
        return {"directory": str(destination), "manifest": manifest, "verification": verification}
    except Exception:
        # Keep a failed directory for diagnosis, but it has no valid final manifest
        # and therefore cannot be uploaded as a successful backup.
        (destination / "FAILED").write_text("backup creation failed\n", encoding="utf-8")
        raise


def verify_backup(source: Path) -> dict[str, Any]:
    """Verify parts, reconstructed ZIP, content manifest, and every object hash."""
    directory, manifest = _load_manifest(source)
    errors: list[str] = []
    parts = manifest.get("parts")
    if not isinstance(parts, list) or not parts:
        return {"ok": False, "errors": ["manifest contains no parts"], "backup_id": manifest.get("backup_id")}
    data = bytearray()
    for expected in parts:
        try:
            name = _safe_part_name(expected.get("name"))
        except ValueError as exc:
            errors.append(str(exc))
            continue
        path = directory / name
        if not path.is_file():
            errors.append(f"missing part: {path.name}")
            continue
        raw = path.read_bytes()
        if len(raw) != expected.get("size"):
            errors.append(f"part size mismatch: {path.name}")
        if hashlib.sha256(raw).hexdigest() != expected.get("sha256"):
            errors.append(f"part checksum mismatch: {path.name}")
        data.extend(raw)
    archive_meta = manifest.get("archive") if isinstance(manifest.get("archive"), Mapping) else {}
    if len(data) != archive_meta.get("size"):
        errors.append("reconstructed archive size mismatch")
    if hashlib.sha256(data).hexdigest() != archive_meta.get("sha256"):
        errors.append("reconstructed archive checksum mismatch")
    checked = 0
    if not errors:
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                names = archive.namelist()
                for name in names:
                    _safe_archive_name(name)
                bad = archive.testzip()
                if bad:
                    errors.append(f"ZIP CRC failure: {bad}")
                content = json.loads(archive.read("content-manifest.json"))
                if content.get("backup_id") != manifest.get("backup_id"):
                    errors.append("content manifest backup_id mismatch")
                if content.get("objects") != manifest.get("objects"):
                    errors.append("inner and outer object manifests differ")
                expected_names = {
                    _safe_archive_name(str(item.get("path")))
                    for item in content.get("objects", [])
                }
                if set(names) != {*expected_names, "content-manifest.json"}:
                    errors.append("ZIP member list differs from manifest")
                for item in content.get("objects", []):
                    name = _safe_archive_name(str(item.get("path")))
                    raw = archive.read(name)
                    if len(raw) != item.get("size"):
                        errors.append(f"object size mismatch: {name}")
                    if hashlib.sha256(raw).hexdigest() != item.get("sha256"):
                        errors.append(f"object checksum mismatch: {name}")
                    checked += 1
        except (KeyError, OSError, ValueError, zipfile.BadZipFile) as exc:
            errors.append(f"cannot verify backup ZIP: {exc}")
    return {
        "ok": not errors,
        "backup_id": manifest.get("backup_id"),
        "parts": len(parts),
        "objects_checked": checked,
        "errors": errors,
    }


def restore_backup(
    store: BackupStore,
    source: Path,
    *,
    require_empty: bool = True,
    artifact_output: Path | None = None,
) -> dict[str, Any]:
    """Restore into an isolated store and reconcile; never selects production itself."""
    verification = verify_backup(source)
    if not verification["ok"]:
        raise ValueError("backup verification failed: " + "; ".join(verification["errors"]))
    database_name = str(getattr(store, "database_name", ""))
    if not database_name.startswith(("jobintel_test_", "jobintel_restore_")):
        raise ValueError("restore target must be an isolated jobintel_test_/jobintel_restore_ database")
    directory, manifest = _load_manifest(source)
    archive = _archive_bytes(directory, manifest)
    with zipfile.ZipFile(io.BytesIO(archive)) as package:
        extraction = _restore_artifacts(package, manifest, artifact_output) if artifact_output else None
        backup_type = manifest.get("backup_type")
        if backup_type == "mongodb-logical":
            snapshot = _bson_json_loads(package.read("database/snapshot.json"))
            with store.lease(f"restore:{manifest['backup_id']}"):
                restored = store.restore_snapshot(snapshot, require_empty=require_empty)
            return {
                "backup_id": manifest["backup_id"],
                "backup_type": backup_type,
                "verification": verification,
                "restore": restored,
                "artifact_restore": extraction,
            }
        if backup_type == "yaml-premigration":
            plan = json.loads(package.read("migration/plan.json"))
            store.ensure_schema()
            if require_empty:
                occupied = {
                    name: len(store.list(name))
                    for name in plan["collections"]
                    if store.list(name)
                }
                if occupied:
                    raise ValueError(f"restore target is not empty: {occupied}")
            imported = import_plan(store, plan, dry_run=False)
            reconciliation = reconcile(store, plan)
            if not reconciliation["ok"]:
                raise ValueError("restored YAML backup failed reconciliation")
            return {
                "backup_id": manifest["backup_id"],
                "backup_type": backup_type,
                "verification": verification,
                "restore": imported,
                "reconciliation": reconciliation,
                "artifact_restore": extraction,
            }
    raise ValueError(f"unsupported backup type: {manifest.get('backup_type')!r}")


def _project_files(root: Path) -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    selected: list[str] = []
    for raw in result.stdout.split("\0"):
        if not raw:
            continue
        relative = PurePosixPath(raw).as_posix()
        parts = PurePosixPath(relative).parts
        if not parts or not _allowed(relative, parts):
            continue
        selected.append(relative)
    return sorted(set(selected))


def _allowed(relative: str, parts: tuple[str, ...]) -> bool:
    if any(part in {".git", ".codex-work", "__pycache__", ".pytest_cache", ".venv", "venv"} for part in parts):
        return False
    name = parts[-1]
    if name.casefold() in _SECRET_NAMES or Path(name).suffix.casefold() in _SECRET_SUFFIXES:
        return False
    if name.startswith("~$"):
        return False
    return parts[0] in _INCLUDE_ROOTS or relative in _INCLUDE_FILES


def _repo_bytes(root: Path, relative: str) -> bytes:
    path = root / Path(relative)
    try:
        return _filesystem_path(path).read_bytes()
    except OSError as exc:
        raise OSError(f"cannot read exact backup source {relative}: {exc}") from exc


def _add_sheets_snapshot(
    payloads: dict[str, bytes], snapshot: Mapping[str, Any] | None
) -> dict[str, Any] | None:
    if snapshot is None:
        return None
    captured_at = snapshot.get("captured_at")
    if not captured_at:
        raise ValueError("Sheets snapshot requires its own captured_at timestamp")
    raw = _json_bytes(snapshot)
    payloads["sheets/snapshot.json"] = raw
    return {
        "included": True,
        "captured_at": _json_value(captured_at),
        "size": len(raw),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def _split_archive(path: Path, destination: Path, backup_id: str, part_size: int) -> list[dict[str, Any]]:
    parts: list[dict[str, Any]] = []
    with path.open("rb") as source:
        index = 1
        while True:
            raw = source.read(part_size)
            if not raw:
                break
            name = f"{backup_id}.zip.part-{index:04d}"
            target = destination / name
            _atomic_write(target, raw)
            parts.append({"name": name, "size": len(raw), "sha256": hashlib.sha256(raw).hexdigest()})
            index += 1
    return parts


def _parts_sha256(directory: Path, parts: Sequence[Mapping[str, Any]]) -> str:
    digest = hashlib.sha256()
    for part in parts:
        digest.update((directory / str(part["name"])).read_bytes())
    return digest.hexdigest()


def _archive_bytes(directory: Path, manifest: Mapping[str, Any]) -> bytes:
    return b"".join((directory / _safe_part_name(item["name"])).read_bytes() for item in manifest["parts"])


def _load_manifest(source: Path) -> tuple[Path, dict[str, Any]]:
    path = source.resolve()
    manifest_path = path / MANIFEST_NAME if path.is_dir() else path
    if not manifest_path.is_file():
        raise FileNotFoundError(f"backup manifest not found: {manifest_path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if manifest.get("schema_version") != BACKUP_SCHEMA_VERSION:
        raise ValueError(f"unsupported backup schema: {manifest.get('schema_version')!r}")
    return manifest_path.parent, manifest


def _snapshot_counts(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    if snapshot is None:
        return {}
    result = {}
    collections = snapshot.get("collections")
    if not isinstance(collections, Mapping):
        return result
    for name, raw in sorted(collections.items()):
        item = raw if isinstance(raw, Mapping) else {}
        result[str(name)] = {
            "documents": len(item.get("documents", [])) if isinstance(item.get("documents"), list) else None,
            "indexes": len(item.get("indexes", [])) if isinstance(item.get("indexes"), list) else None,
        }
    return result


def _validate_artifact_references(snapshot: Mapping[str, Any], root: Path) -> dict[str, Any]:
    collections = snapshot.get("collections")
    if not isinstance(collections, Mapping):
        raise ValueError("database snapshot has no collections mapping")
    manifests = _collection_documents(collections, "artifact_manifests")
    checked = 0
    total = 0
    required: list[dict[str, Any]] = []
    for manifest in manifests:
        if not isinstance(manifest, Mapping):
            raise ValueError("artifact manifest must be a mapping")
        directory = str(manifest.get("directory") or "")
        files = manifest.get("files")
        if not isinstance(files, list):
            raise ValueError(f"artifact manifest {manifest.get('_id')} has no files list")
        for item in files:
            if not isinstance(item, Mapping):
                raise ValueError(f"artifact manifest {manifest.get('_id')} has an invalid file")
            locator = str(item.get("path") or "")
            expected_hash = str(item.get("sha256") or "")
            expected_size = item.get("size")
            raw = _artifact_bytes(root, directory, locator)
            if len(raw) != expected_size:
                raise ValueError(f"artifact size differs from database manifest: {locator}")
            if hashlib.sha256(raw).hexdigest() != expected_hash:
                raise ValueError(f"artifact checksum differs from database manifest: {locator}")
            checked += 1
            total += len(raw)
            required.append(
                _required_payload_reference(directory, locator, len(raw), expected_hash)
            )
    evidence_checked = 0
    for vacancy in _collection_documents(collections, "vacancies"):
        directory = str(vacancy.get("directory") or "")
        evidence = vacancy.get("legacy_evidence") or []
        if not isinstance(evidence, list):
            raise ValueError(f"vacancy {vacancy.get('_id')} has invalid legacy evidence")
        for item in evidence:
            if not isinstance(item, Mapping):
                raise ValueError(f"vacancy {vacancy.get('_id')} has invalid legacy evidence item")
            locator = str(item.get("locator") or "")
            raw = _artifact_bytes(root, directory, locator)
            if len(raw) != item.get("size") or hashlib.sha256(raw).hexdigest() != item.get("sha256"):
                raise ValueError(f"vacancy evidence differs from database manifest: {locator}")
            evidence_checked += 1
            total += len(raw)
            required.append(
                _required_payload_reference(
                    directory,
                    locator,
                    len(raw),
                    str(item.get("sha256") or ""),
                )
            )
    return {
        "files": checked,
        "evidence": evidence_checked,
        "bytes": total,
        "verified": True,
        "_required": required,
    }


def _required_payload_reference(
    directory: str,
    locator: str,
    size: int,
    sha256: str,
) -> dict[str, Any]:
    if "!" in locator:
        archive_name, member = locator.split("!", 1)
        return {
            "locator": locator,
            "object": _safe_archive_name(f"project/{_safe_archive_name(archive_name)}"),
            "member": _safe_archive_name(member),
            "size": size,
            "sha256": sha256,
        }
    safe = _safe_archive_name(locator)
    parts = PurePosixPath(safe).parts
    if parts[0] in _INCLUDE_ROOTS:
        relative = safe
    else:
        if not directory or "/" in directory or "\\" in directory or directory in {".", ".."}:
            raise ValueError(f"invalid artifact vacancy directory: {directory!r}")
        relative = PurePosixPath("registry", "jobs", directory, *parts).as_posix()
    return {
        "locator": locator,
        "object": _safe_archive_name(f"project/{relative}"),
        "member": None,
        "size": size,
        "sha256": sha256,
    }


def _validate_payload_references(
    payloads: Mapping[str, bytes],
    required: Sequence[Mapping[str, Any]],
) -> None:
    archive_cache: dict[str, dict[str, bytes]] = {}
    for reference in required:
        object_name = str(reference.get("object") or "")
        locator = str(reference.get("locator") or "")
        raw = payloads.get(object_name)
        if raw is None:
            raise ValueError(f"backup payload is missing required reference: {locator}")
        member = reference.get("member")
        if member:
            if object_name not in archive_cache:
                try:
                    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
                        archive_cache[object_name] = {
                            name: archive.read(name) for name in archive.namelist()
                        }
                except (OSError, KeyError, zipfile.BadZipFile) as exc:
                    raise ValueError(f"backup compact archive is invalid: {object_name}: {exc}") from exc
            raw = archive_cache[object_name].get(str(member))
            if raw is None:
                raise ValueError(f"backup payload is missing required archive member: {locator}")
        if len(raw) != reference.get("size") or hashlib.sha256(raw).hexdigest() != reference.get("sha256"):
            raise ValueError(f"backup payload reference differs from source: {locator}")


def _collection_documents(collections: Mapping[str, Any], name: str) -> list[Mapping[str, Any]]:
    raw = collections.get(name, {})
    documents = raw.get("documents", []) if isinstance(raw, Mapping) else raw
    if not isinstance(documents, list):
        raise ValueError(f"{name} snapshot is invalid")
    if not all(isinstance(item, Mapping) for item in documents):
        raise ValueError(f"{name} snapshot contains a non-document")
    return documents


def _compact_archive_payloads(snapshot: Mapping[str, Any], root: Path) -> dict[str, bytes]:
    collections = snapshot.get("collections")
    if not isinstance(collections, Mapping):
        raise ValueError("database snapshot has no collections mapping")
    references: dict[str, set[str]] = {}

    def add(locator: str) -> None:
        if "!" not in locator:
            return
        archive_name, member = locator.split("!", 1)
        archive_name = _safe_archive_name(archive_name)
        member = _safe_archive_name(member)
        references.setdefault(archive_name, set()).add(member)

    for vacancy in _collection_documents(collections, "vacancies"):
        for evidence in vacancy.get("legacy_evidence") or []:
            if isinstance(evidence, Mapping):
                add(str(evidence.get("locator") or ""))
    for manifest in _collection_documents(collections, "artifact_manifests"):
        add(str(manifest.get("evidence_locator") or ""))
        for item in manifest.get("files") or []:
            if isinstance(item, Mapping):
                add(str(item.get("path") or ""))

    payloads: dict[str, bytes] = {}
    for archive_name, members in sorted(references.items()):
        archive_path = _filesystem_path(root.joinpath(*PurePosixPath(archive_name).parts))
        output = io.BytesIO()
        try:
            with zipfile.ZipFile(archive_path) as source, zipfile.ZipFile(output, "w") as compact:
                for member in sorted(members):
                    compact.writestr(_zip_info(member), source.read(member))
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            raise ValueError(f"cannot create compact archive from {archive_name}: {exc}") from exc
        payloads[_safe_archive_name(f"project/{archive_name}")] = output.getvalue()
    return payloads


def _artifact_bytes(root: Path, directory: str, locator: str) -> bytes:
    if not locator:
        raise ValueError("artifact locator is empty")
    if "!" in locator:
        archive_name, member = locator.split("!", 1)
        archive_name = _safe_archive_name(archive_name)
        member = _safe_archive_name(member)
        archive_path = _filesystem_path(root.joinpath(*PurePosixPath(archive_name).parts))
        try:
            with zipfile.ZipFile(archive_path) as archive:
                return archive.read(member)
        except (OSError, KeyError, zipfile.BadZipFile) as exc:
            raise ValueError(f"cannot read archived artifact {locator}: {exc}") from exc
    safe = _safe_archive_name(locator)
    parts = PurePosixPath(safe).parts
    if parts[0] in _INCLUDE_ROOTS:
        path = root.joinpath(*parts)
    else:
        if not directory or "/" in directory or "\\" in directory or directory in {".", ".."}:
            raise ValueError(f"invalid artifact vacancy directory: {directory!r}")
        path = root / "registry" / "jobs" / directory
        path = path.joinpath(*parts)
    try:
        return _filesystem_path(path).read_bytes()
    except OSError as exc:
        raise ValueError(f"cannot read artifact referenced by database: {locator}: {exc}") from exc


def _restore_artifacts(
    package: zipfile.ZipFile,
    manifest: Mapping[str, Any],
    artifact_output: Path,
) -> dict[str, Any]:
    target = artifact_output.resolve()
    if target.exists():
        raise FileExistsError(f"artifact restore output already exists: {target}")
    target.mkdir(parents=True, exist_ok=False)
    selected = [
        item
        for item in manifest.get("objects", [])
        if str(item.get("path", "")).startswith(("project/", "sheets/"))
    ]
    digest = hashlib.sha256()
    total = 0
    for item in selected:
        name = _safe_archive_name(str(item.get("path")))
        raw = package.read(name)
        expected_hash = str(item.get("sha256"))
        if len(raw) != item.get("size") or hashlib.sha256(raw).hexdigest() != expected_hash:
            raise ValueError(f"artifact changed after backup verification: {name}")
        destination = target.joinpath(*PurePosixPath(name).parts)
        resolved = destination.resolve()
        if target != resolved and target not in resolved.parents:
            raise ValueError(f"artifact restore path escapes output: {name}")
        destination = _filesystem_path(resolved)
        _filesystem_path(resolved.parent).mkdir(parents=True, exist_ok=True)
        with destination.open("xb") as handle:
            handle.write(raw)
        digest.update(name.encode("utf-8"))
        digest.update(b"\0")
        digest.update(expected_hash.encode("ascii"))
        total += len(raw)
    return {
        "output": str(target),
        "files": len(selected),
        "bytes": total,
        "manifest_sha256": digest.hexdigest(),
    }


def _filesystem_path(path: Path) -> Path:
    """Return a Windows extended-length path after callers perform safety checks."""
    if os.name != "nt":
        return path
    absolute = str(path.absolute())
    if absolute.startswith("\\\\?\\"):
        return path
    if absolute.startswith("\\\\"):
        return Path("\\\\?\\UNC\\" + absolute[2:])
    return Path("\\\\?\\" + absolute)


def _safe_archive_name(value: str) -> str:
    if not value or "\\" in value:
        raise ValueError(f"unsafe backup object path: {value!r}")
    path = PurePosixPath(value)
    windows = PureWindowsPath(value)
    if (
        path.is_absolute()
        or windows.is_absolute()
        or windows.drive
        or any(part in {"", ".", ".."} or ":" in part for part in path.parts)
    ):
        raise ValueError(f"unsafe backup object path: {value!r}")
    normalized = path.as_posix()
    if normalized != value:
        raise ValueError(f"non-canonical backup object path: {value!r}")
    return normalized


def _safe_part_name(value: Any) -> str:
    if not isinstance(value, str) or not value or value in {".", ".."}:
        raise ValueError(f"unsafe backup part name: {value!r}")
    if Path(value).name != value or "/" in value or "\\" in value or ":" in value:
        raise ValueError(f"unsafe backup part name: {value!r}")
    return value


def _bson_json_bytes(value: Any) -> bytes:
    # Mapping order is semantic for MongoDB compound index key specifications.
    try:
        from bson import json_util
    except ImportError:
        text = json.dumps(
            _json_value(value),
            ensure_ascii=False,
            separators=(",", ":"),
        )
        return (text + "\n").encode("utf-8")
    text = json_util.dumps(
        value,
        json_options=json_util.CANONICAL_JSON_OPTIONS,
        ensure_ascii=False,
        separators=(",", ":"),
    )
    return (text + "\n").encode("utf-8")


def _bson_json_loads(raw: bytes) -> Any:
    try:
        from bson import json_util
    except ImportError:
        return json.loads(raw)
    return json_util.loads(raw.decode("utf-8"), json_options=json_util.CANONICAL_JSON_OPTIONS)


def _json_value(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_value(item) for item in value]
    return value


def _json_bytes(value: Any) -> bytes:
    return (json.dumps(_json_value(value), ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def _zip_info(name: str) -> zipfile.ZipInfo:
    info = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o600 << 16
    return info


def _atomic_write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temporary.write_bytes(raw)
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def _git_revision(root: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True, encoding="utf-8"
    )
    return result.stdout.strip()


def _backup_id() -> str:
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"{stamp}-{uuid.uuid4().hex}"


def _utcnow() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
