from __future__ import annotations

import copy
import re
import threading
import time
import uuid
from collections.abc import Iterator, Mapping, Sequence
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
from typing import Any

from pymongo import ASCENDING, MongoClient, ReturnDocument
from pymongo.client_session import ClientSession
from pymongo.errors import BulkWriteError, DuplicateKeyError, PyMongoError
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern

from .storage_contract import (
    SourceIdentityConflict,
    StorageConfigurationError,
    StorageConflictError,
    StorageLeaseError,
    StorageRestoreError,
    WriterLease,
)


SCHEMA_VERSION = 1
LEASE_ID = "operational-writer"
DEFAULT_LEASE_SECONDS = 30.0
_COLLECTION_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_.-]{0,119}$")
_DATABASE_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,62}$")
_VACANCY_SCOPES = frozenset({"jobs", "rejected"})
_INTERNAL_COLLECTIONS = frozenset(
    {"storage_schema", "writer_leases", "writer_fence_guards"}
)


class MongoStore:
    """Revisioned operational storage guarded by one cross-machine writer lease."""

    def __init__(
        self,
        uri: str,
        database_name: str,
        *,
        lease_seconds: float = DEFAULT_LEASE_SECONDS,
        client: MongoClient[Mapping[str, Any]] | None = None,
    ) -> None:
        if not uri.strip():
            raise StorageConfigurationError("MongoDB URI must not be empty")
        if not database_name.strip() or not _DATABASE_RE.fullmatch(database_name):
            raise StorageConfigurationError(f"invalid MongoDB database name: {database_name!r}")
        if database_name.casefold() in {"admin", "config", "local"}:
            raise StorageConfigurationError("a system MongoDB database cannot be used")
        if lease_seconds <= 0:
            raise StorageConfigurationError("lease_seconds must be positive")
        self.client = client or MongoClient(
            uri,
            appname="job-intelligence",
            tz_aware=True,
            serverSelectionTimeoutMS=5_000,
            connectTimeoutMS=5_000,
        )
        self.database = self.client[database_name]
        self.database_name = database_name
        self.lease_seconds = float(lease_seconds)
        self._local = threading.local()

    def close(self) -> None:
        self.client.close()

    def ensure_schema(self) -> None:
        existing = self.database["storage_schema"].find_one({"_id": "operational"})
        if existing is not None and existing.get("schema_version") != SCHEMA_VERSION:
            raise StorageConfigurationError(
                "incompatible operational storage schema: "
                f"expected {SCHEMA_VERSION}, found {existing.get('schema_version')!r}"
            )
        with self.lease("storage:ensure-schema", timeout_seconds=10):
            existing = self.database["storage_schema"].find_one({"_id": "operational"})
            if existing is not None and existing.get("schema_version") != SCHEMA_VERSION:
                raise StorageConfigurationError(
                    "incompatible operational storage schema: "
                    f"expected {SCHEMA_VERSION}, found {existing.get('schema_version')!r}"
                )
            self.database["storage_schema"].create_index(
                [("schema_version", ASCENDING)], name="schema_version"
            )
            self.database["writer_leases"].create_index(
                [("expires_at", ASCENDING)], name="expires_at"
            )
            for collection in ("vacancies", "prefilter_rejections"):
                self.database[collection].create_index(
                    [("scope", ASCENDING), ("directory", ASCENDING)],
                    unique=True,
                    name="scope_directory_unique",
                )
                self.database[collection].create_index(
                    [
                        ("scope", ASCENDING),
                        ("archived", ASCENDING),
                        ("meta.status", ASCENDING),
                    ],
                    name="scope_archive_status",
                )
            self.database["vacancies"].create_index(
                [("meta.fingerprint", ASCENDING)], name="fingerprint_nonunique"
            )
            self.database["source_identities"].create_index(
                [("source", ASCENDING), ("source_job_id", ASCENDING)],
                unique=True,
                name="source_identity_unique",
            )
            self.database["source_identities"].create_index(
                [("vacancy_id", ASCENDING)], name="vacancy_id"
            )
            self.put(
                "storage_schema",
                "operational",
                {"schema_version": SCHEMA_VERSION},
            )

    @contextmanager
    def lease(
        self,
        owner: str,
        *,
        timeout_seconds: float = 0,
    ) -> Iterator[WriterLease]:
        owner = owner.strip()
        if not owner:
            raise StorageLeaseError("writer lease owner must not be empty")
        current = getattr(self._local, "lease_state", None)
        if current is not None:
            current["depth"] += 1
            try:
                self._assert_lease_live(current)
                yield current["lease"]
            finally:
                current["depth"] -= 1
            return

        state = self._acquire_lease(owner, max(0.0, float(timeout_seconds)))
        self._local.lease_state = state
        heartbeat = threading.Thread(
            target=self._heartbeat,
            args=(state,),
            name="jobintel-mongodb-lease",
            daemon=True,
        )
        state["heartbeat"] = heartbeat
        heartbeat.start()
        try:
            yield state["lease"]
            self._assert_lease_live(state)
        finally:
            state["stop"].set()
            heartbeat.join(timeout=max(1.0, self.lease_seconds))
            try:
                self._release_lease(state)
            finally:
                self._local.lease_state = None

    @contextmanager
    def transaction(self) -> Iterator[MongoStore]:
        state = self._require_lease()
        existing = getattr(self._local, "session", None)
        if existing is not None:
            self._assert_lease_live(state)
            yield self
            return

        with self.client.start_session() as session:
            self._local.session = session
            try:
                session.start_transaction(
                    read_concern=ReadConcern("snapshot"),
                    write_concern=WriteConcern("majority"),
                )
                self._assert_lease_live(state)
                self._touch_fence_guard(state, session)
                yield self
                self._assert_lease_live(state)
                self._touch_fence_guard(state, session)
                session.commit_transaction()
            except Exception:
                if session.in_transaction:
                    session.abort_transaction()
                raise
            finally:
                self._local.session = None

    def get(self, collection: str, document_id: Any) -> dict[str, Any] | None:
        row = self.database[self._collection_name(collection)].find_one(
            {"_id": document_id}, session=self._session()
        )
        return copy.deepcopy(row) if row is not None else None

    def list(
        self,
        collection: str,
        query: Mapping[str, Any] | None = None,
        *,
        sort: Sequence[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]:
        cursor = self.database[self._collection_name(collection)].find(
            dict(query or {}), session=self._session()
        )
        if sort:
            cursor = cursor.sort(list(sort))
        return [copy.deepcopy(row) for row in cursor]

    def put(
        self,
        collection: str,
        document_id: Any,
        payload: Mapping[str, Any],
        *,
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        name = self._collection_name(collection)
        if name == "writer_leases":
            raise StorageConfigurationError("writer leases cannot be changed through put")
        with self.transaction():
            return self._put(name, document_id, payload, expected_revision=expected_revision)

    def insert_batch(
        self,
        collection: str,
        documents: Sequence[Mapping[str, Any]],
    ) -> int:
        name = self._collection_name(collection)
        if name == "writer_leases":
            raise StorageConfigurationError(
                "writer leases cannot be changed through insert_batch"
            )

        payloads: list[dict[str, Any]] = []
        for offset, document in enumerate(documents):
            if not isinstance(document, Mapping):
                raise StorageConfigurationError(
                    f"batch document at offset {offset} must be a mapping"
                )
            clean = copy.deepcopy(dict(document))
            if "_id" not in clean:
                raise StorageConfigurationError(
                    f"batch document at offset {offset} requires an _id"
                )
            envelope = sorted(
                field
                for field in ("revision", "writer_fence", "updated_at")
                if field in clean
            )
            if envelope:
                raise StorageConfigurationError(
                    f"batch document at offset {offset} contains storage envelope fields: "
                    + ", ".join(envelope)
                )
            payloads.append(clean)

        with self.transaction():
            state = self._require_lease()
            if not payloads:
                return 0
            updated_at = self._utcnow()
            stored = [
                {
                    **payload,
                    "revision": 1,
                    "writer_fence": state["lease"].fence,
                    "updated_at": updated_at,
                }
                for payload in payloads
            ]
            try:
                result = self.database[name].insert_many(
                    stored, ordered=True, session=self._session()
                )
            except DuplicateKeyError as exc:
                raise StorageConflictError(
                    f"concurrent batch insert conflict for {name}"
                ) from exc
            except BulkWriteError as exc:
                write_errors = (exc.details or {}).get("writeErrors", [])
                if not any(
                    error.get("code") in {11000, 11001, 12582}
                    for error in write_errors
                ):
                    raise
                raise StorageConflictError(
                    f"concurrent batch insert conflict for {name}"
                ) from exc
            return len(result.inserted_ids)

    def delete(
        self,
        collection: str,
        document_id: Any,
        *,
        expected_revision: int | None = None,
    ) -> bool:
        name = self._collection_name(collection)
        if name in {"writer_leases", "storage_schema"}:
            raise StorageConfigurationError(f"{name} cannot be deleted through the generic API")
        with self.transaction():
            current = self.database[name].find_one({"_id": document_id}, session=self._session())
            if current is None:
                return False
            self._check_revision(current, expected_revision, name, document_id)
            result = self.database[name].delete_one(
                {"_id": document_id, "revision": current.get("revision")},
                session=self._session(),
            )
            if result.deleted_count != 1:
                raise StorageConflictError(f"concurrent delete conflict for {name}:{document_id}")
            return True

    def save_vacancy(
        self,
        directory: str,
        meta: Mapping[str, Any],
        job_text: str,
        company_text: str | None,
        *,
        scope: str = "jobs",
        expected_revision: int | None = None,
    ) -> dict[str, Any]:
        directory = directory.strip()
        if not directory or "/" in directory or "\\" in directory:
            raise StorageConfigurationError(f"invalid vacancy directory: {directory!r}")
        if scope not in _VACANCY_SCOPES:
            raise StorageConfigurationError(f"invalid vacancy scope: {scope!r}")
        normalized_meta = copy.deepcopy(dict(meta))
        sources = self._source_rows(normalized_meta, scope=scope)
        vacancy_id = str(normalized_meta.get("id") or "").strip()
        if not vacancy_id:
            if scope != "rejected":
                raise StorageConfigurationError("active vacancy metadata requires an id")
            vacancy_id = self._rejected_vacancy_id(sources, directory)

        collection = "vacancies" if scope == "jobs" else "prefilter_rejections"
        with self.transaction():
            current = self.database[collection].find_one(
                {"_id": vacancy_id}, session=self._session()
            )
            if current is not None:
                if current.get("scope") != scope or current.get("directory") != directory:
                    raise StorageConflictError(
                        f"vacancy {vacancy_id} is already bound to "
                        f"{current.get('scope')}:{current.get('directory')}"
                    )
            elif expected_revision not in (None, 0):
                raise StorageConflictError(
                    f"{collection}:{vacancy_id} does not exist at revision {expected_revision}"
                )

            for source, source_job_id, reference in sources:
                identity_id = self._source_identity_id(source, source_job_id)
                identity = self.database["source_identities"].find_one(
                    {"_id": identity_id}, session=self._session()
                )
                vacancy_ids = sorted(
                    {str(value) for value in (identity or {}).get("vacancy_ids", []) if value}
                )
                prefilter_ids = sorted(
                    {str(value) for value in (identity or {}).get("prefilter_ids", []) if value}
                )
                if scope == "jobs" and (
                    (identity or {}).get("ambiguous")
                    or (vacancy_ids and vacancy_ids != [vacancy_id])
                ):
                    raise SourceIdentityConflict(
                        source,
                        source_job_id,
                        ",".join(vacancy_ids) or "ambiguous",
                        vacancy_id,
                    )
                if scope == "rejected":
                    prefilter_ids = sorted({*prefilter_ids, vacancy_id})
                else:
                    vacancy_ids = sorted({*vacancy_ids, vacancy_id})
                if identity is None:
                    self._put(
                        "source_identities",
                        identity_id,
                        {
                            "source": source,
                            "source_job_id": source_job_id,
                            "vacancy_ids": vacancy_ids,
                            "prefilter_ids": prefilter_ids,
                            "ambiguous": len(vacancy_ids) > 1,
                            "reference": reference,
                        },
                        expected_revision=0,
                    )
                elif (
                    identity.get("reference") != reference
                    or identity.get("vacancy_ids") != vacancy_ids
                    or identity.get("prefilter_ids") != prefilter_ids
                ):
                    updated = {
                        key: value
                        for key, value in identity.items()
                        if key not in {"_id", "revision", "writer_fence", "updated_at"}
                    }
                    updated.update(
                        {
                            "vacancy_ids": vacancy_ids,
                            "prefilter_ids": prefilter_ids,
                            "ambiguous": len(vacancy_ids) > 1,
                            "reference": reference,
                        }
                    )
                    self._put(
                        "source_identities",
                        identity_id,
                        updated,
                        expected_revision=int(identity["revision"]),
                    )

            payload = (
                {
                    key: copy.deepcopy(value)
                    for key, value in current.items()
                    if key not in {"_id", "revision", "writer_fence", "updated_at"}
                }
                if current
                else {}
            )
            stored_meta = (
                copy.deepcopy(current.get("meta"))
                if current and isinstance(current.get("meta"), Mapping)
                else {}
            )
            stored_meta.update(normalized_meta)
            payload.update({
                "directory": directory,
                "scope": scope,
                "archived": bool(current.get("archived", False)) if current else False,
                "meta": stored_meta,
                "job_text": job_text,
                "company_text": company_text,
                "match": copy.deepcopy(current.get("match")) if current else None,
                "triage": copy.deepcopy(current.get("triage")) if current else None,
            })
            return self._put(
                collection,
                vacancy_id,
                payload,
                expected_revision=expected_revision,
            )

    def get_by_directory(
        self, directory: str, *, scope: str = "jobs"
    ) -> dict[str, Any] | None:
        collection = self._vacancy_collection(scope)
        row = self.database[collection].find_one(
            {"scope": scope, "directory": directory}, session=self._session()
        )
        return copy.deepcopy(row) if row is not None else None

    def resolve_source(self, source: str, source_job_id: str) -> dict[str, Any] | None:
        source = source.strip().casefold()
        source_job_id = source_job_id.strip()
        if not source or not source_job_id:
            raise StorageConfigurationError("source lookup requires source and source_job_id")
        identity = self.get(
            "source_identities", self._source_identity_id(source, source_job_id)
        )
        if identity is None:
            return None
        vacancy_ids = sorted(
            {str(value) for value in identity.get("vacancy_ids", []) if value}
        )
        if identity.get("ambiguous") or len(vacancy_ids) > 1:
            raise SourceIdentityConflict(
                source,
                source_job_id,
                ",".join(vacancy_ids) or "ambiguous",
                "lookup",
            )
        if not vacancy_ids:
            # Prefilter evidence does not own the source identity for active collection.
            return None
        vacancy = self.get("vacancies", vacancy_ids[0])
        if vacancy is None:
            raise StorageConflictError(
                f"source identity {source}:{source_job_id} references missing vacancy {vacancy_ids[0]}"
            )
        return vacancy

    def list_vacancies(
        self, *, scope: str = "jobs", include_archived: bool = False
    ) -> list[dict[str, Any]]:
        collection = self._vacancy_collection(scope)
        query: dict[str, Any] = {"scope": scope}
        if not include_archived:
            query["archived"] = False
        return self.list(collection, query, sort=[("directory", ASCENDING)])

    def snapshot(self) -> dict[str, Any]:
        self._require_lease()
        names = sorted(
            name
            for name in self.database.list_collection_names()
            if not name.startswith("system.") and name not in _INTERNAL_COLLECTIONS
        )
        indexes = {
            name: [copy.deepcopy(index) for index in self.database[name].list_indexes()]
            for name in names
        }
        with self.transaction():
            collections: dict[str, Any] = {}
            for name in names:
                collections[name] = {
                    "documents": self.list(name, sort=[("_id", ASCENDING)]),
                    "indexes": indexes[name],
                }
            return {
                "schema_version": SCHEMA_VERSION,
                "database": self.database_name,
                "captured_at": self._utcnow(),
                "collections": collections,
            }

    def restore_snapshot(
        self,
        snapshot: Mapping[str, Any],
        *,
        require_empty: bool = True,
    ) -> dict[str, Any]:
        self._require_lease()
        if not self.database_name.startswith(("jobintel_test_", "jobintel_restore_")):
            raise StorageRestoreError(
                "snapshot restore is restricted to jobintel_test_* or jobintel_restore_* databases"
            )
        if snapshot.get("schema_version") != SCHEMA_VERSION:
            raise StorageRestoreError(
                "incompatible snapshot schema: "
                f"expected {SCHEMA_VERSION}, found {snapshot.get('schema_version')!r}"
            )
        raw_collections = snapshot.get("collections")
        if not isinstance(raw_collections, Mapping):
            raise StorageRestoreError("snapshot collections must be a mapping")
        collections: dict[str, Mapping[str, Any]] = {}
        for raw_name, raw in raw_collections.items():
            name = self._collection_name(str(raw_name))
            if name in _INTERNAL_COLLECTIONS:
                raise StorageRestoreError(
                    f"snapshot must not contain internal collection {name!r}"
                )
            if not isinstance(raw, Mapping):
                raise StorageRestoreError(f"snapshot collection {name!r} must be a mapping")
            if not isinstance(raw.get("documents"), list) or not isinstance(
                raw.get("indexes"), list
            ):
                raise StorageRestoreError(
                    f"snapshot collection {name!r} requires documents and indexes lists"
                )
            collections[name] = raw

        self.ensure_schema()
        data_names = sorted(
            name
            for name in self.database.list_collection_names()
            if not name.startswith("system.") and name not in _INTERNAL_COLLECTIONS
        )
        if require_empty:
            populated = [
                name for name in data_names if self.database[name].count_documents({}) > 0
            ]
            if populated:
                raise StorageRestoreError(
                    "restore target contains operational documents: " + ", ".join(populated)
                )

        inserted: dict[str, list[Any]] = {}
        created_indexes: list[tuple[str, str]] = []
        created_collections: list[str] = []
        counts: dict[str, int] = {}
        try:
            for name, raw in sorted(collections.items()):
                if name not in self.database.list_collection_names():
                    self.database.create_collection(name)
                    created_collections.append(name)
                documents = [copy.deepcopy(value) for value in raw["documents"]]
                if any(not isinstance(value, Mapping) or "_id" not in value for value in documents):
                    raise StorageRestoreError(
                        f"snapshot collection {name!r} contains an invalid document"
                    )
                inserted[name] = []
                for offset in range(0, len(documents), 250):
                    batch = documents[offset : offset + 250]
                    pending: list[dict[str, Any]] = []
                    for document in batch:
                        existing = self.database[name].find_one({"_id": document["_id"]})
                        if existing is None:
                            pending.append(dict(document))
                        elif existing != document:
                            raise StorageRestoreError(
                                f"restore conflict for {name}:{document['_id']}"
                            )
                    if pending:
                        with self.transaction():
                            self.database[name].insert_many(
                                pending, ordered=True, session=self._session()
                            )
                        inserted[name].extend(document["_id"] for document in pending)
                counts[name] = len(documents)

            for name, raw in sorted(collections.items()):
                existing_indexes = {
                    str(spec["name"]): self._semantic_index(spec)
                    for spec in self.database[name].list_indexes()
                }
                for raw_spec in raw["indexes"]:
                    if not isinstance(raw_spec, Mapping):
                        raise StorageRestoreError(
                            f"snapshot collection {name!r} contains an invalid index"
                        )
                    semantic = self._semantic_index(raw_spec)
                    index_name = semantic["name"]
                    if index_name == "_id_":
                        continue
                    if index_name in existing_indexes:
                        if existing_indexes[index_name] != semantic:
                            raise StorageRestoreError(
                                f"index mismatch for {name}:{index_name}"
                            )
                        continue
                    options: dict[str, Any] = {"name": index_name}
                    if semantic["unique"]:
                        options["unique"] = True
                    if semantic["partialFilterExpression"] is not None:
                        options["partialFilterExpression"] = semantic[
                            "partialFilterExpression"
                        ]
                    self.database[name].create_index(semantic["key"], **options)
                    created_indexes.append((name, index_name))
                    existing_indexes[index_name] = semantic

                verified = {
                    str(spec["name"]): self._semantic_index(spec)
                    for spec in self.database[name].list_indexes()
                }
                for raw_spec in raw["indexes"]:
                    semantic = self._semantic_index(raw_spec)
                    if verified.get(semantic["name"]) != semantic:
                        raise StorageRestoreError(
                            f"restored index verification failed for {name}:{semantic['name']}"
                        )
        except Exception as exc:
            self._rollback_restore(inserted, created_indexes, created_collections)
            if isinstance(exc, StorageRestoreError):
                raise
            raise StorageRestoreError(
                f"snapshot restore failed ({type(exc).__name__}); inserted documents were removed"
            ) from exc

        return {
            "collections": counts,
            "documents": sum(counts.values()),
            "indexes": sum(
                len([index for index in raw["indexes"] if index.get("name") != "_id_"])
                for raw in collections.values()
            ),
        }

    def _put(
        self,
        collection: str,
        document_id: Any,
        payload: Mapping[str, Any],
        *,
        expected_revision: int | None,
    ) -> dict[str, Any]:
        state = self._require_lease()
        clean = copy.deepcopy(dict(payload))
        supplied_id = clean.pop("_id", document_id)
        if supplied_id != document_id:
            raise StorageConfigurationError("payload _id does not match document_id")
        for reserved in ("revision", "writer_fence", "updated_at"):
            clean.pop(reserved, None)
        current = self.database[collection].find_one(
            {"_id": document_id}, session=self._session()
        )
        if current is None:
            if expected_revision not in (None, 0):
                raise StorageConflictError(
                    f"{collection}:{document_id} does not exist at revision {expected_revision}"
                )
            revision = 1
            selector = {"_id": document_id, "revision": {"$exists": False}}
        else:
            if self._same_payload(current, clean):
                return copy.deepcopy(current)
            self._check_revision(current, expected_revision, collection, document_id)
            revision = int(current.get("revision", 0)) + 1
            selector = {"_id": document_id, "revision": current.get("revision")}
        stored = {
            "_id": document_id,
            **clean,
            "revision": revision,
            "writer_fence": state["lease"].fence,
            "updated_at": self._utcnow(),
        }
        try:
            result = self.database[collection].replace_one(
                selector,
                stored,
                upsert=current is None,
                session=self._session(),
            )
        except DuplicateKeyError as exc:
            raise StorageConflictError(
                f"concurrent write conflict for {collection}:{document_id}"
            ) from exc
        if result.matched_count != 1 and result.upserted_id is None:
            raise StorageConflictError(
                f"concurrent write conflict for {collection}:{document_id}"
            )
        return copy.deepcopy(stored)

    def _acquire_lease(self, owner: str, timeout_seconds: float) -> dict[str, Any]:
        token = uuid.uuid4().hex
        deadline = time.monotonic() + timeout_seconds
        leases = self.database["writer_leases"]
        while True:
            now = self._utcnow()
            try:
                with self.client.start_session() as session:
                    session.start_transaction(write_concern=WriteConcern("majority"))
                    current = leases.find_one({"_id": LEASE_ID}, session=session)
                    if current is not None and current.get("expires_at", now) > now:
                        session.abort_transaction()
                        row = None
                    else:
                        fence = int((current or {}).get("fence", 0)) + 1
                        row = {
                            "_id": LEASE_ID,
                            "owner": owner,
                            "token": token,
                            "fence": fence,
                            "acquired_at": now,
                            "expires_at": now + timedelta(seconds=self.lease_seconds),
                        }
                        if current is None:
                            leases.insert_one(row, session=session)
                        else:
                            result = leases.replace_one(
                                {
                                    "_id": LEASE_ID,
                                    "fence": current.get("fence"),
                                    "expires_at": current.get("expires_at"),
                                },
                                row,
                                session=session,
                            )
                            if result.matched_count != 1:
                                raise StorageLeaseError(
                                    "MongoDB writer lease changed during acquisition"
                                )
                        self.database["writer_fence_guards"].replace_one(
                            {"_id": LEASE_ID},
                            {"_id": LEASE_ID, "fence": fence, "taken_over_at": now},
                            upsert=True,
                            session=session,
                        )
                        session.commit_transaction()
            except DuplicateKeyError:
                row = None
            except PyMongoError as exc:
                if exc.has_error_label("TransientTransactionError") and time.monotonic() < deadline:
                    time.sleep(0.02)
                    continue
                raise StorageLeaseError(
                    f"cannot acquire MongoDB writer lease ({type(exc).__name__})"
                ) from exc
            if row is not None:
                lease = WriterLease(
                    owner,
                    token,
                    int(row["fence"]),
                    row["acquired_at"],
                    row["expires_at"],
                )
                return {
                    "lease": lease,
                    "depth": 1,
                    "stop": threading.Event(),
                    "lost": threading.Event(),
                    "error": None,
                    "last_renewed_at": row["acquired_at"],
                    "loss_cause": None,
                }
            if time.monotonic() >= deadline:
                holder = leases.find_one({"_id": LEASE_ID}) or {}
                raise StorageLeaseError(
                    "MongoDB writer lease is already held by "
                    f"{holder.get('owner', 'unknown')} until {holder.get('expires_at', 'unknown')}"
                )
            time.sleep(min(0.1, max(0.01, deadline - time.monotonic())))

    def _heartbeat(self, state: dict[str, Any]) -> None:
        interval = max(0.05, self.lease_seconds / 3)
        lease: WriterLease = state["lease"]
        while not state["stop"].wait(interval):
            now = self._utcnow()
            try:
                row = self.database["writer_leases"].find_one_and_update(
                    {
                        "_id": LEASE_ID,
                        "token": lease.token,
                        "fence": lease.fence,
                        "expires_at": {"$gt": now},
                    },
                    {"$set": {"expires_at": now + timedelta(seconds=self.lease_seconds)}},
                    return_document=ReturnDocument.AFTER,
                )
            except PyMongoError as exc:
                state["error"] = exc
                state["loss_cause"] = "heartbeat renewal failed"
                state["lost"].set()
                return
            if row is None:
                state["loss_cause"] = "heartbeat renewal no longer matched the active lease"
                state["lost"].set()
                return
            state["last_renewed_at"] = now

    def _release_lease(self, state: dict[str, Any]) -> None:
        lease: WriterLease = state["lease"]
        try:
            self.database["writer_leases"].update_one(
                {"_id": LEASE_ID, "token": lease.token, "fence": lease.fence},
                {
                    "$set": {
                        "released_at": self._utcnow(),
                        "expires_at": self._utcnow(),
                    },
                    "$unset": {"token": ""},
                },
            )
        except PyMongoError as exc:
            if not state["lost"].is_set():
                raise StorageLeaseError(
                    f"cannot release MongoDB writer lease ({type(exc).__name__})"
                ) from exc

    def _assert_lease_live(self, state: dict[str, Any]) -> None:
        """Check the current lease document, never a transaction snapshot."""
        if state["lost"].is_set():
            raise self._lease_lost_error(state, "lease was previously marked lost")
        lease: WriterLease = state["lease"]
        row = self.database["writer_leases"].find_one(
            {
                "_id": LEASE_ID,
                "token": lease.token,
                "fence": lease.fence,
                "expires_at": {"$gt": self._utcnow()},
            }
        )
        if row is None:
            state["loss_cause"] = "lease expired or was fenced"
            state["lost"].set()
            raise self._lease_lost_error(state, "lease expired or was fenced")

    def _touch_fence_guard(
        self, state: dict[str, Any], session: ClientSession
    ) -> None:
        lease: WriterLease = state["lease"]
        result = self.database["writer_fence_guards"].update_one(
            {"_id": LEASE_ID, "fence": lease.fence},
            {"$set": {"last_transaction_at": self._utcnow()}},
            session=session,
        )
        if result.matched_count != 1:
            state["loss_cause"] = "writer fence guard no longer matched the active lease"
            state["lost"].set()
            raise self._lease_lost_error(state, "writer transaction was fenced")

    def _lease_lost_error(self, state: Mapping[str, Any], cause: str) -> StorageLeaseError:
        """Return diagnostics that identify a lease without exposing its token or URI."""
        lease: WriterLease = state["lease"]
        details = [
            f"owner={lease.owner}",
            f"fence={lease.fence}",
            f"last_renewed_at={state.get('last_renewed_at', 'unknown')}",
            f"cause={state.get('loss_cause') or cause}",
        ]
        heartbeat_error = state.get("error")
        if heartbeat_error is not None:
            details.append(f"heartbeat_error={type(heartbeat_error).__name__}")
        try:
            holder = self.database["writer_leases"].find_one({"_id": LEASE_ID}) or {}
        except PyMongoError:
            holder = {}
        if holder:
            details.extend(
                [
                    f"current_owner={holder.get('owner', 'unknown')}",
                    f"current_fence={holder.get('fence', 'unknown')}",
                ]
            )
        return StorageLeaseError("MongoDB writer lease was lost (" + ", ".join(details) + ")")

    def _rollback_restore(
        self,
        inserted: Mapping[str, Sequence[Any]],
        created_indexes: Sequence[tuple[str, str]],
        created_collections: Sequence[str],
    ) -> None:
        failures: list[str] = []
        for collection, index_name in reversed(created_indexes):
            try:
                self.database[collection].drop_index(index_name)
            except PyMongoError:
                failures.append(f"index {collection}:{index_name}")
        for collection, document_ids in inserted.items():
            for offset in range(0, len(document_ids), 250):
                batch = list(document_ids[offset : offset + 250])
                if not batch:
                    continue
                try:
                    with self.transaction():
                        self.database[collection].delete_many(
                            {"_id": {"$in": batch}}, session=self._session()
                        )
                except Exception:
                    failures.append(f"documents in {collection}")
        for collection in reversed(created_collections):
            try:
                self.database.drop_collection(collection)
            except PyMongoError:
                failures.append(f"collection {collection}")
        if failures:
            raise StorageRestoreError(
                "restore cleanup was incomplete for: " + ", ".join(failures)
            )

    def _require_lease(self) -> dict[str, Any]:
        state = getattr(self._local, "lease_state", None)
        if state is None:
            raise StorageLeaseError("a MongoDB writer lease is required for mutations")
        self._assert_lease_live(state)
        return state

    def _session(self) -> ClientSession | None:
        return getattr(self._local, "session", None)

    @staticmethod
    def _check_revision(
        current: Mapping[str, Any],
        expected_revision: int | None,
        collection: str,
        document_id: Any,
    ) -> None:
        if expected_revision is None:
            return
        actual = current.get("revision")
        if actual != expected_revision:
            raise StorageConflictError(
                f"revision conflict for {collection}:{document_id}; "
                f"expected {expected_revision}, found {actual}"
            )

    @staticmethod
    def _same_payload(current: Mapping[str, Any], clean: Mapping[str, Any]) -> bool:
        comparable = {
            key: value
            for key, value in current.items()
            if key not in {"_id", "revision", "writer_fence", "updated_at"}
        }
        return comparable == dict(clean)

    @staticmethod
    def _semantic_index(spec: Mapping[str, Any]) -> dict[str, Any]:
        name = str(spec.get("name") or "").strip()
        raw_key = spec.get("key")
        if not name:
            raise StorageRestoreError("snapshot index requires a name")
        if isinstance(raw_key, Mapping):
            key = [(str(field), direction) for field, direction in raw_key.items()]
        elif isinstance(raw_key, Sequence) and not isinstance(raw_key, (str, bytes)):
            key = []
            for value in raw_key:
                if not isinstance(value, Sequence) or isinstance(value, (str, bytes)) or len(value) != 2:
                    raise StorageRestoreError(f"snapshot index {name!r} has an invalid key")
                key.append((str(value[0]), value[1]))
        else:
            raise StorageRestoreError(f"snapshot index {name!r} has an invalid key")
        return {
            "name": name,
            "key": key,
            "unique": bool(spec.get("unique", False)),
            "partialFilterExpression": copy.deepcopy(spec.get("partialFilterExpression")),
        }

    @staticmethod
    def _source_rows(
        meta: Mapping[str, Any],
        *,
        scope: str,
    ) -> list[tuple[str, str, dict[str, Any]]]:
        raw_sources = meta.get("sources")
        if raw_sources is None and scope == "rejected":
            raw_sources = [
                {
                    "source": meta.get("source"),
                    "source_job_id": meta.get("source_job_id"),
                    "url": meta.get("source_url"),
                }
            ]
        if not isinstance(raw_sources, list) or not raw_sources:
            raise StorageConfigurationError("vacancy metadata requires a non-empty sources list")
        rows: list[tuple[str, str, dict[str, Any]]] = []
        seen: set[tuple[str, str]] = set()
        for raw in raw_sources:
            if not isinstance(raw, Mapping):
                raise StorageConfigurationError("vacancy source reference must be a mapping")
            reference = copy.deepcopy(dict(raw))
            source = str(reference.get("source") or "").strip().casefold()
            source_job_id = str(reference.get("source_job_id") or "").strip()
            if not source or not source_job_id:
                raise StorageConfigurationError(
                    "vacancy source requires source and source_job_id"
                )
            key = (source, source_job_id)
            if key in seen:
                raise StorageConfigurationError(
                    f"duplicate source identity in vacancy metadata: {source}:{source_job_id}"
                )
            seen.add(key)
            reference["source"] = source
            reference["source_job_id"] = source_job_id
            rows.append((source, source_job_id, reference))
        return rows

    @staticmethod
    def _source_identity_id(source: str, source_job_id: str) -> str:
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                "jobintel:source-identity:v1\0" + source + "\0" + source_job_id,
            )
        )

    @staticmethod
    def _rejected_vacancy_id(
        sources: Sequence[tuple[str, str, Mapping[str, Any]]], directory: str
    ) -> str:
        if not sources:
            raise StorageConfigurationError("prefilter vacancy requires a source identity")
        source, source_job_id, _ = sorted(sources, key=lambda row: (row[0], row[1]))[0]
        return str(
            uuid.uuid5(
                uuid.NAMESPACE_URL,
                "jobintel:prefilter:v1\0" + source + "\0" + source_job_id,
            )
        )

    @staticmethod
    def _collection_name(value: str) -> str:
        name = value.strip()
        if not _COLLECTION_RE.fullmatch(name) or name.startswith("system."):
            raise StorageConfigurationError(f"invalid MongoDB collection name: {value!r}")
        return name

    @staticmethod
    def _vacancy_collection(scope: str) -> str:
        if scope == "jobs":
            return "vacancies"
        if scope == "rejected":
            return "prefilter_rejections"
        raise StorageConfigurationError(f"invalid vacancy scope: {scope!r}")

    @staticmethod
    def _utcnow() -> datetime:
        now = datetime.now(timezone.utc)
        return now.replace(microsecond=(now.microsecond // 1000) * 1000)
