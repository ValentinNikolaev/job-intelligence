from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://himalayas.app/jobs/api/search"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
SEARCH_PARAMETERS = {
    "q",
    "country",
    "worldwide",
    "exclude_worldwide",
    "seniority",
    "employment_type",
    "company",
    "timezone",
    "sort",
}
BOOLEAN_PARAMETERS = {"worldwide", "exclude_worldwide"}
MULTI_VALUE_PARAMETERS = {"seniority", "employment_type", "company"}
SORT_VALUES = {
    "relevant",
    "recent",
    "salaryAsc",
    "salaryDesc",
    "nameAToZ",
    "nameZToA",
    "jobs",
}


@dataclass(frozen=True, slots=True)
class SearchQuery:
    index: int
    parameters: dict[str, str]
    max_pages: int

    def discovery_metadata(self) -> dict[str, Any]:
        return {"query_index": self.index, "parameters": dict(self.parameters)}


class HimalayasCollector:
    name = "himalayas"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        config_path = Path(config.get("HIMALAYAS_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        default_max_pages = _positive_int(
            settings.get("max_pages_per_query", 5), "max_pages_per_query"
        )
        self.queries = _parse_queries(settings.get("queries"), default_max_pages)
        self._opener = opener
        self._sleep = sleep
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        if not self.queries:
            raise ValueError("Himalayas queries are empty; edit sources/himalayas/config.yaml")

        jobs_by_id: dict[str, NormalizedJob] = {}
        completed: set[int] = set()
        largest_page_limit = max(query.max_pages for query in self.queries)

        # Keep requests sequential and paginate queries round-robin so every
        # configured search gets a first page before any broad search goes deep.
        for page in range(1, largest_page_limit + 1):
            for query in self.queries:
                if query.index in completed or page > query.max_pages:
                    continue

                payload = self._search(query, page)
                raw_jobs = payload.get("jobs")
                if not isinstance(raw_jobs, list):
                    raise ValueError(
                        f"Himalayas query {query.index}, page {page} returned no jobs list"
                    )

                discovery = query.discovery_metadata()
                for item in raw_jobs:
                    if not isinstance(item, dict):
                        continue
                    job = normalize_job(item, discovered_by=[discovery])
                    existing = jobs_by_id.get(job.source_job_id)
                    if existing is None:
                        jobs_by_id[job.source_job_id] = job
                        continue
                    discoveries = list(existing.source_metadata.get("discovered_by", []))
                    if discovery not in discoveries:
                        discoveries.append(discovery)
                        metadata = dict(existing.source_metadata)
                        metadata["discovered_by"] = discoveries
                        jobs_by_id[job.source_job_id] = replace(
                            existing, source_metadata=metadata
                        )

                if _is_last_page(payload, raw_jobs, page):
                    completed.add(query.index)
            if len(completed) == len(self.queries):
                break

        yield from jobs_by_id.values()

    def _search(self, query: SearchQuery, page: int) -> dict[str, Any]:
        url = f"{API_ROOT}?{urlencode({**query.parameters, 'page': str(page)})}"
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
        )
        return self._get_json(request, f"Himalayas query {query.index} page {page}")

    def _get_json(self, request: Request, context: str) -> dict[str, Any]:
        for attempt in range(3):
            self._request_count += 1
            try:
                with self._opener(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError(f"expected JSON object from {context}")
                return payload
            except HTTPError as exc:
                if exc.code != 429 and exc.code < 500:
                    raise RuntimeError(f"{context} returned HTTP {exc.code}") from exc
                if attempt == 2:
                    raise RuntimeError(
                        f"{context} returned HTTP {exc.code} after retries"
                    ) from exc
            except TimeoutError as exc:
                if attempt == 2:
                    raise RuntimeError(f"{context} timed out after retries") from exc
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"{context} request failed: {exc.reason}") from exc
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"{context} returned invalid JSON") from exc
            self._sleep(2**attempt)
        raise AssertionError("unreachable")


def normalize_job(
    payload: Mapping[str, Any], *, discovered_by: list[dict[str, Any]] | None = None
) -> NormalizedJob:
    title = html_to_markdown(_as_string(payload.get("title")))
    company = _as_string(payload.get("companyName"))
    source_url = _as_string(payload.get("applicationLink"))
    if not title or not company or not source_url:
        raise ValueError("Himalayas job is missing title, companyName, or applicationLink")

    guid = _as_string(payload.get("guid"))
    if guid:
        source_job_id = guid
    else:
        digest = hashlib.sha256(source_url.encode("utf-8")).hexdigest()
        source_job_id = f"url-sha256:{digest}"

    description_html = _as_string(payload.get("description"))
    description = html_to_markdown(description_html)
    if not description:
        description = html_to_markdown(_as_string(payload.get("excerpt")))

    location_restrictions = _location_restrictions(payload.get("locationRestrictions"))
    metadata = _source_metadata(payload, location_restrictions)
    if discovered_by:
        metadata["discovered_by"] = discovered_by

    return NormalizedJob(
        source="himalayas",
        source_job_id=source_job_id,
        source_url=source_url,
        title=title,
        company=company,
        description=description,
        location=_location_label(location_restrictions),
        remote=True,
        employment_type=_as_string(payload.get("employmentType")),
        published_at=_timestamp(payload.get("pubDate")),
        source_metadata=metadata,
    )


def create_collector(config: Mapping[str, str]) -> HimalayasCollector:
    return HimalayasCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Himalayas config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Himalayas YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Himalayas config must be a YAML mapping: {path}")
    allowed = {"version", "max_pages_per_query", "timeout_seconds", "queries"}
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown Himalayas config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Himalayas config version")
    return loaded


def _parse_queries(value: Any, default_max_pages: int) -> list[SearchQuery]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Himalayas queries must be a YAML list")

    queries: list[SearchQuery] = []
    for index, raw_query in enumerate(value, 1):
        if not isinstance(raw_query, dict):
            raise ValueError(f"Himalayas query {index} must be a mapping")
        if "page" in raw_query:
            raise ValueError(
                f"queries[{index}].page is managed by the collector; use max_pages instead"
            )
        allowed = SEARCH_PARAMETERS | {"max_pages"}
        unknown = sorted(set(raw_query) - allowed)
        if unknown:
            raise ValueError(
                f"unknown fields in Himalayas query {index}: {', '.join(unknown)}"
            )

        max_pages = _positive_int(
            raw_query.get("max_pages", default_max_pages),
            f"queries[{index}].max_pages",
        )
        parameters: dict[str, str] = {}
        for name in SEARCH_PARAMETERS:
            if name not in raw_query or raw_query[name] is None or raw_query[name] == "":
                continue
            parameters[name] = _query_parameter(name, raw_query[name], index)

        active_filters = set(parameters) - {"sort"}
        active_filters -= {
            name for name in BOOLEAN_PARAMETERS if parameters.get(name) == "false"
        }
        if not active_filters:
            raise ValueError(f"Himalayas query {index} needs at least one search filter")
        queries.append(SearchQuery(index, parameters, max_pages))
    return queries


def _query_parameter(name: str, value: Any, query_index: int) -> str:
    field = f"queries[{query_index}].{name}"
    if name in BOOLEAN_PARAMETERS:
        if not isinstance(value, bool):
            raise ValueError(f"{field} must be true or false")
        return str(value).lower()

    if name in MULTI_VALUE_PARAMETERS and isinstance(value, list):
        parts = [_required_string(item, field) for item in value]
        if not parts:
            raise ValueError(f"{field} cannot be empty")
        result = ",".join(parts)
    else:
        result = _required_string(value, field)
    if name == "sort" and result not in SORT_VALUES:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(SORT_VALUES))}")
    return result


def _is_last_page(payload: Mapping[str, Any], jobs: list[Any], page: int) -> bool:
    if not jobs:
        return True
    total = _non_negative_int(payload.get("totalCount"))
    limit = _positive_int_or_none(payload.get("limit"))
    offset = _non_negative_int(payload.get("offset"))
    if total is not None:
        if offset is not None and offset + len(jobs) >= total:
            return True
        if limit is not None and page * limit >= total:
            return True
    return limit is not None and len(jobs) < limit


def _location_restrictions(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        return []
    restrictions: list[dict[str, str]] = []
    for item in value:
        if isinstance(item, str) and item.strip():
            restrictions.append({"name": item.strip()})
            continue
        if not isinstance(item, Mapping):
            continue
        restriction = {
            name: text
            for name in ("alpha2", "name", "slug")
            if (text := _as_string(item.get(name))) is not None
        }
        if restriction:
            restrictions.append(restriction)
    return restrictions


def _location_label(restrictions: list[dict[str, str]]) -> str:
    if not restrictions:
        return "Worldwide"
    labels = [item.get("name") or item.get("alpha2") or item.get("slug") for item in restrictions]
    return ", ".join(label for label in labels if label) or "Worldwide"


def _source_metadata(
    payload: Mapping[str, Any], location_restrictions: list[dict[str, str]]
) -> dict[str, Any]:
    metadata: dict[str, Any] = {"location_restrictions": location_restrictions}
    fields = {
        "excerpt": "excerpt",
        "company_slug": "companySlug",
        "company_logo": "companyLogo",
        "seniority": "seniority",
        "parent_categories": "parentCategories",
    }
    for target, source in fields.items():
        value = payload.get(source)
        if value not in (None, "", [], {}):
            metadata[target] = value

    timezone_restrictions = payload.get(
        "timezoneRestrictions", payload.get("timezoneRestriction")
    )
    if isinstance(timezone_restrictions, list):
        metadata["timezone_restrictions"] = timezone_restrictions

    categories = payload.get("categories", payload.get("category"))
    if isinstance(categories, list):
        metadata["categories"] = categories

    salary = _salary_metadata(payload)
    if salary:
        metadata["salary"] = salary
    expiry_at = _timestamp(payload.get("expiryDate"))
    if expiry_at:
        metadata["expiry_at"] = expiry_at
    return metadata


def _salary_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
    minimum = _number(payload.get("minSalary"))
    maximum = _number(payload.get("maxSalary"))
    if minimum is None and maximum is None:
        return {}
    salary: dict[str, Any] = {
        "period": _as_string(payload.get("salaryPeriod")) or "annual"
    }
    if minimum is not None:
        salary["min"] = minimum
    if maximum is not None:
        salary["max"] = maximum
    currency = _as_string(payload.get("currency"))
    if currency:
        salary["currency"] = currency
    return salary


def _timestamp(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        text = value.strip()
        try:
            parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            return text
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
            "+00:00", "Z"
        )
    number = _number(value)
    if number is None:
        return None
    try:
        seconds = number / 1000 if abs(number) >= 100_000_000_000 else number
        parsed = datetime.fromtimestamp(seconds, timezone.utc).replace(microsecond=0)
    except (OverflowError, OSError, ValueError):
        return None
    return parsed.isoformat().replace("+00:00", "Z")


def _number(value: Any) -> int | float | None:
    return value if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _non_negative_int(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value >= 0 else None


def _positive_int_or_none(value: Any) -> int | None:
    return value if isinstance(value, int) and not isinstance(value, bool) and value > 0 else None


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if result < 1:
        raise ValueError(f"{name} must be at least 1")
    return result


def _positive_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if result <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return result


def _required_string(value: Any, name: str) -> str:
    result = str(value).strip()
    if not result:
        raise ValueError(f"{name} cannot be empty")
    return result


def _as_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
