from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


VACANCY_STATUSES = (
    "found",
    "reviewing",
    "prepared",
    "applied",
    "interview",
    "technical_interview",
    "final_interview",
    "offer",
    "rejected",
    "withdrawn",
    "closed",
)


@dataclass(frozen=True, slots=True)
class NormalizedJob:
    source: str
    source_job_id: str
    source_url: str
    title: str
    company: str
    description: str
    company_url: str | None = None
    location: str | None = None
    remote: bool | None = None
    employment_type: str | None = None
    published_at: str | None = None
    company_description: str | None = None
    source_metadata: Mapping[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        required = {
            "source": self.source,
            "source_job_id": self.source_job_id,
            "source_url": self.source_url,
            "title": self.title,
            "company": self.company,
        }
        missing = [name for name, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"missing required job fields: {', '.join(missing)}")


@dataclass(frozen=True, slots=True)
class UpsertResult:
    status: str
    vacancy_id: str
    directory: str


@dataclass(slots=True)
class CollectorSummary:
    source: str
    fetched: int = 0
    created: int = 0
    updated: int = 0
    merged: int = 0
    unchanged: int = 0
    rejected: int = 0
    errors: int = 0
    api_requests: int = 0
    limit_reached: bool = False

    def record(self, status: str) -> None:
        if status == "created":
            self.created += 1
        elif status == "updated":
            self.updated += 1
        elif status == "merged":
            self.merged += 1
        elif status == "unchanged":
            self.unchanged += 1
        elif status == "rejected":
            self.rejected += 1
        else:
            raise ValueError(f"unknown upsert status: {status}")

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "fetched": self.fetched,
            "created": self.created,
            "updated": self.updated,
            "duplicates_merged": self.merged,
            "unchanged": self.unchanged,
            "rejected": self.rejected,
            "errors": self.errors,
            "api_requests": self.api_requests,
            "limit_reached": self.limit_reached,
        }
