from __future__ import annotations

import json
import sys
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://boards-api.greenhouse.io/v1/boards"
BOARD_ROOT = "https://job-boards.greenhouse.io"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


@dataclass(frozen=True, slots=True)
class GreenhouseBoard:
    token: str
    company: str | None = None


@dataclass(frozen=True, slots=True)
class GreenhouseFilters:
    remote_only: bool = False
    location_terms: tuple[str, ...] = ()
    title_terms: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class GreenhouseSettings:
    boards: tuple[GreenhouseBoard, ...]
    filters: GreenhouseFilters
    timeout_seconds: float


class GreenhouseCollector:
    name = "greenhouse"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        config_path = Path(config.get("GREENHOUSE_CONFIG", "") or DEFAULT_CONFIG_PATH)
        self.settings = _load_settings(config_path)
        self.timeout = self.settings.timeout_seconds
        self._opener = opener
        self.errors = 0
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        if not self.settings.boards:
            raise ValueError(
                "Greenhouse board registry is empty; edit sources/greenhouse/config.yaml"
            )
        self.errors = 0
        self._request_count = 0
        seen: set[str] = set()
        for board in self.settings.boards:
            try:
                payload = self._fetch_board(board.token)
                jobs = parse_board_response(board, payload, self.settings.filters)
            except Exception as exc:
                self.errors += 1
                print(f"greenhouse: board {board.token!r} failed: {exc}", file=sys.stderr)
                continue
            for job in jobs:
                if job.source_job_id in seen:
                    continue
                seen.add(job.source_job_id)
                yield job

    def _fetch_board(self, token: str) -> dict[str, Any]:
        encoded = quote(token, safe="")
        request = Request(
            f"{API_ROOT}/{encoded}/jobs?content=true",
            headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
        )
        try:
            self._request_count += 1
            with self._opener(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise RuntimeError("request timed out") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError("returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError("returned JSON that is not an object")
        return payload


def parse_board_response(
    board: GreenhouseBoard,
    payload: Mapping[str, Any],
    filters: GreenhouseFilters | None = None,
) -> list[NormalizedJob]:
    raw_jobs = payload.get("jobs")
    if not isinstance(raw_jobs, list):
        raise ValueError("response has no jobs list")
    active_filters = filters or GreenhouseFilters()
    jobs: list[NormalizedJob] = []
    for index, raw_job in enumerate(raw_jobs, 1):
        if not isinstance(raw_job, dict):
            raise ValueError(f"job {index} is not an object")
        if not _matches_filters(raw_job, active_filters):
            continue
        jobs.append(normalize_job(board, raw_job))
    return jobs


def normalize_job(board: GreenhouseBoard, payload: Mapping[str, Any]) -> NormalizedJob:
    title = html_to_markdown(_as_string(payload.get("title")))
    source_url = _as_string(payload.get("absolute_url"))
    source_job_id = _as_string(payload.get("id"))
    company = board.company or _as_string(payload.get("company_name")) or board.token
    if not title or not source_url or not source_job_id:
        raise ValueError("job is missing title, absolute_url, or id")

    return NormalizedJob(
        source="greenhouse",
        source_job_id=source_job_id,
        source_url=source_url,
        title=title,
        company=company,
        company_url=f"{BOARD_ROOT}/{quote(board.token, safe='')}",
        description=html_to_markdown(_as_string(payload.get("content"))),
        location=_location_name(payload),
        remote=_is_remote(payload),
        employment_type=_as_string(payload.get("employment")),
        published_at=_as_string(payload.get("first_published")),
        source_metadata=_source_metadata(board.token, payload),
    )


def create_collector(config: Mapping[str, str]) -> GreenhouseCollector:
    return GreenhouseCollector(config)


def _load_settings(path: Path) -> GreenhouseSettings:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Greenhouse config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Greenhouse YAML config {path}: {exc}") from exc
    if loaded is None:
        loaded = {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Greenhouse config must be a YAML mapping: {path}")
    allowed = {"version", "timeout_seconds", "filters", "boards"}
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown Greenhouse config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Greenhouse config version")
    filters = _load_filters(loaded.get("filters"))
    boards = tuple(
        _load_board(item, index)
        for index, item in enumerate(loaded.get("boards") or [], 1)
    )
    return GreenhouseSettings(
        boards=boards,
        filters=filters,
        timeout_seconds=_positive_float(loaded.get("timeout_seconds", 30), "timeout_seconds"),
    )


def _load_filters(value: object) -> GreenhouseFilters:
    if value is None:
        return GreenhouseFilters()
    if not isinstance(value, dict):
        raise ValueError("Greenhouse filters must be a YAML mapping")
    allowed = {"remote_only", "location_terms", "title_terms"}
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ValueError(f"unknown Greenhouse filter fields: {', '.join(unknown)}")
    return GreenhouseFilters(
        remote_only=_optional_bool(value.get("remote_only"), "remote_only") or False,
        location_terms=_string_tuple(value.get("location_terms"), "location_terms"),
        title_terms=_string_tuple(value.get("title_terms"), "title_terms"),
    )


def _load_board(value: object, index: int) -> GreenhouseBoard:
    if isinstance(value, str):
        token = value.strip()
        company = None
    elif isinstance(value, dict):
        allowed = {"token", "company"}
        unknown = sorted(set(value) - allowed)
        if unknown:
            raise ValueError(f"unknown Greenhouse board {index} fields: {', '.join(unknown)}")
        token = _as_string(value.get("token")) or ""
        company = _as_string(value.get("company"))
    else:
        raise ValueError(f"Greenhouse board {index} must be a string or mapping")
    if not token:
        raise ValueError(f"Greenhouse board {index} has no token")
    if "/" in token or " " in token or token.startswith(("http://", "https://")):
        raise ValueError(f"invalid Greenhouse board token: {token}")
    return GreenhouseBoard(token=token, company=company)


def _source_metadata(board: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {"board": board}
    fields = {
        "internal_job_id": "internal_job_id",
        "requisition_id": "requisition_id",
        "updated_at": "updated_at",
        "application_deadline": "application_deadline",
        "departments": "departments",
        "offices": "offices",
        "metadata": "metadata",
        "data_compliance": "data_compliance",
        "ai_disclaimer": "ai_disclaimer",
        "ai_opt_out_request_url": "ai_opt_out_request_url",
    }
    for target, source in fields.items():
        value = payload.get(source)
        if value not in (None, "", [], {}):
            metadata[target] = value
    return metadata


def _matches_filters(payload: Mapping[str, Any], filters: GreenhouseFilters) -> bool:
    if filters.remote_only and not _is_remote(payload):
        return False
    if filters.location_terms and not _contains_term(
        _location_text(payload), filters.location_terms
    ):
        return False
    if filters.title_terms and not _contains_term(
        _as_string(payload.get("title")) or "", filters.title_terms
    ):
        return False
    return True


def _is_remote(payload: Mapping[str, Any]) -> bool:
    searchable = "\n".join(
        value for value in (_as_string(payload.get("title")), _location_name(payload)) if value
    )
    return "remote" in searchable.casefold()


def _location_name(payload: Mapping[str, Any]) -> str | None:
    location = payload.get("location")
    if isinstance(location, Mapping):
        return _as_string(location.get("name"))
    return _as_string(location)


def _location_text(payload: Mapping[str, Any]) -> str:
    locations: list[str] = []
    primary = _location_name(payload)
    if primary:
        locations.append(primary)
    offices = payload.get("offices")
    if isinstance(offices, list):
        for item in offices:
            if isinstance(item, Mapping):
                name = _as_string(item.get("name"))
                if name:
                    locations.append(name)
    return "\n".join(locations)


def _contains_term(value: str, terms: tuple[str, ...]) -> bool:
    searchable = value.casefold()
    return any(term.casefold() in searchable for term in terms)


def _as_string(value: object) -> str | None:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return str(value)
    return value.strip() if isinstance(value, str) and value.strip() else None


def _string_tuple(value: object, field: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"Greenhouse {field} must be a list")
    result = []
    for index, item in enumerate(value, 1):
        text = _as_string(item)
        if not text:
            raise ValueError(f"Greenhouse {field} item {index} must be a non-empty string")
        result.append(text)
    return tuple(result)


def _optional_bool(value: object, field: str) -> bool | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return value
    raise ValueError(f"Greenhouse {field} must be a boolean")


def _positive_float(value: object, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"Greenhouse {field} must be positive")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Greenhouse {field} must be positive") from exc
    if result <= 0:
        raise ValueError(f"Greenhouse {field} must be positive")
    return result
