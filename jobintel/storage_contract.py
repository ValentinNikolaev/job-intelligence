from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping, Protocol, Sequence


class StorageError(RuntimeError):
    """Base error for operational storage failures."""


class StorageConfigurationError(StorageError):
    pass


class StorageLeaseError(StorageError):
    pass


class StorageConflictError(StorageError):
    pass


class StorageRestoreError(StorageError):
    pass


class SourceIdentityConflict(StorageConflictError):
    def __init__(
        self,
        source: str,
        source_job_id: str,
        existing_vacancy_id: str,
        incoming_vacancy_id: str,
    ) -> None:
        self.source = source
        self.source_job_id = source_job_id
        self.existing_vacancy_id = existing_vacancy_id
        self.incoming_vacancy_id = incoming_vacancy_id
        super().__init__(
            "source identity belongs to another vacancy: "
            f"{source}:{source_job_id} -> {existing_vacancy_id} "
            f"(incoming {incoming_vacancy_id})"
        )


@dataclass(frozen=True, slots=True)
class WriterLease:
    owner: str
    token: str
    fence: int
    acquired_at: datetime
    expires_at: datetime


class OperationalStore(Protocol):
    def ensure_schema(self) -> None: ...

    def get(self, collection: str, document_id: Any) -> dict[str, Any] | None: ...

    def list(
        self,
        collection: str,
        query: Mapping[str, Any] | None = None,
        *,
        sort: Sequence[tuple[str, int]] | None = None,
    ) -> list[dict[str, Any]]: ...

    def put(
        self,
        collection: str,
        document_id: Any,
        payload: Mapping[str, Any],
        *,
        expected_revision: int | None = None,
    ) -> dict[str, Any]: ...

    def delete(
        self,
        collection: str,
        document_id: Any,
        *,
        expected_revision: int | None = None,
    ) -> bool: ...

    def save_vacancy(
        self,
        directory: str,
        meta: Mapping[str, Any],
        job_text: str,
        company_text: str | None,
        *,
        scope: str = "jobs",
        expected_revision: int | None = None,
    ) -> dict[str, Any]: ...

    def get_by_directory(
        self, directory: str, *, scope: str = "jobs"
    ) -> dict[str, Any] | None: ...

    def resolve_source(
        self, source: str, source_job_id: str
    ) -> dict[str, Any] | None: ...

    def rejected_source_owner(
        self, source: str, source_job_id: str
    ) -> dict[str, Any] | None: ...

    def list_vacancies(
        self, *, scope: str = "jobs", include_archived: bool = False
    ) -> list[dict[str, Any]]: ...

    def snapshot(self) -> dict[str, Any]: ...

    def restore_snapshot(
        self, snapshot: Mapping[str, Any], *, require_empty: bool = True
    ) -> dict[str, Any]: ...
