from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from jobintel.ashby_boards import AshbyBoard, AshbyBoardRegistry, AshbyFilters
from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://api.ashbyhq.com/posting-api/job-board"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


class AshbyCollector:
    name = "ashby"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        config_path = Path(config.get("ASHBY_CONFIG", "") or DEFAULT_CONFIG_PATH)
        self.registry = AshbyBoardRegistry.load(config_path)
        self.timeout = self.registry.timeout_seconds
        self._opener = opener
        self.errors = 0
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        if not self.registry.boards:
            raise ValueError(
                "Ashby board registry is empty; edit sources/ashby/config.yaml or run "
                "'python run.py ashby discover <board-or-url>'"
            )
        self.errors = 0
        self._request_count = 0
        seen: set[str] = set()
        for board in self.registry.boards:
            try:
                payload = self._fetch_board(board.name)
                jobs = parse_board_response(board, payload, self.registry.filters)
            except Exception as exc:
                self.errors += 1
                print(f"ashby: board {board.name!r} failed: {exc}", file=sys.stderr)
                continue
            for job in jobs:
                if job.source_job_id in seen:
                    continue
                seen.add(job.source_job_id)
                yield job

    def _fetch_board(self, board: str) -> dict[str, Any]:
        encoded = quote(board, safe="")
        request = Request(
            f"{API_ROOT}/{encoded}?includeCompensation=true",
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
    board: AshbyBoard,
    payload: Mapping[str, Any],
    filters: AshbyFilters | None = None,
) -> list[NormalizedJob]:
    raw_jobs = payload.get("jobs")
    if not isinstance(raw_jobs, list):
        raise ValueError("response has no jobs list")
    company = (
        board.company
        or _as_string(payload.get("organizationName"))
        or _as_string(payload.get("companyName"))
        or board.name
    )
    active_filters = filters or AshbyFilters()
    jobs: list[NormalizedJob] = []
    for index, raw_job in enumerate(raw_jobs, 1):
        if not isinstance(raw_job, dict):
            raise ValueError(f"job {index} is not an object")
        if raw_job.get("isListed") is False:
            continue
        if not _matches_filters(raw_job, active_filters):
            continue
        jobs.append(normalize_job(board, company, raw_job))
    return jobs


def normalize_job(
    board: AshbyBoard,
    company: str,
    payload: Mapping[str, Any],
) -> NormalizedJob:
    title = html_to_markdown(_as_string(payload.get("title")))
    source_url = _as_string(payload.get("jobUrl"))
    if not title or not source_url:
        raise ValueError("job is missing title or jobUrl")
    source_job_id = str(payload.get("id") or "").strip()
    if not source_job_id:
        digest = hashlib.sha256(source_url.encode("utf-8")).hexdigest()
        source_job_id = f"url-sha256:{digest}"

    description_plain = _as_string(payload.get("descriptionPlain"))
    description = description_plain.strip() if description_plain else html_to_markdown(
        _as_string(payload.get("descriptionHtml"))
    )
    metadata = _source_metadata(board.name, payload)
    remote_value = payload.get("isRemote")
    remote = remote_value if isinstance(remote_value, bool) else None
    return NormalizedJob(
        source="ashby",
        source_job_id=source_job_id,
        source_url=source_url,
        title=title,
        company=company,
        company_url=f"https://jobs.ashbyhq.com/{quote(board.name, safe='')}",
        description=description,
        location=_as_string(payload.get("location")),
        remote=remote,
        employment_type=_as_string(payload.get("employmentType")),
        published_at=_as_string(payload.get("publishedAt")),
        source_metadata=metadata,
    )


def create_collector(config: Mapping[str, str]) -> AshbyCollector:
    return AshbyCollector(config)


def _source_metadata(board: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    metadata: dict[str, Any] = {"board": board}
    fields = {
        "application_url": "applyUrl",
        "department": "department",
        "team": "team",
        "workplace_type": "workplaceType",
        "secondary_locations": "secondaryLocations",
        "compensation": "compensation",
    }
    for target, source in fields.items():
        value = payload.get(source)
        if value not in (None, "", [], {}):
            metadata[target] = value
    return metadata


def _as_string(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _matches_filters(payload: Mapping[str, Any], filters: AshbyFilters) -> bool:
    if filters.remote_only and not _is_remote(payload):
        return False
    if filters.title_terms and not _contains_term(
        _as_string(payload.get("title")) or "", filters.title_terms
    ):
        return False
    if filters.location_terms and not _contains_term(
        _location_text(payload), filters.location_terms
    ):
        return False
    return True


def _is_remote(payload: Mapping[str, Any]) -> bool:
    if payload.get("isRemote") is True:
        return True
    workplace_type = _as_string(payload.get("workplaceType"))
    return workplace_type is not None and workplace_type.casefold() == "remote"


def _contains_term(value: str, terms: tuple[str, ...]) -> bool:
    searchable = value.casefold()
    return any(term.casefold() in searchable for term in terms)


def _location_text(payload: Mapping[str, Any]) -> str:
    locations: list[str] = []
    primary = _as_string(payload.get("location"))
    if primary:
        locations.append(primary)
    secondary = payload.get("secondaryLocations")
    if isinstance(secondary, list):
        for item in secondary:
            if isinstance(item, dict):
                location = _as_string(item.get("location"))
            else:
                location = _as_string(item)
            if location:
                locations.append(location)
    return "\n".join(locations)
