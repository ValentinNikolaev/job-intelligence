from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://api.adzuna.com/v1/api/jobs"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
COUNTRIES = {
    "at", "au", "be", "br", "ca", "ch", "de", "es", "fr", "gb",
    "in", "it", "mx", "nl", "nz", "pl", "sg", "us", "za",
}
SEARCH_PARAMETERS = {
    "what", "what_and", "what_phrase", "what_or", "what_exclude",
    "title_only", "where", "distance", "location0", "location1",
    "location2", "location3", "location4", "location5", "location6",
    "location7", "max_days_old", "category", "sort_dir", "sort_by",
    "salary_min", "salary_max", "salary_include_unknown", "full_time",
    "part_time", "contract", "permanent", "company",
}
FLAG_PARAMETERS = {
    "salary_include_unknown", "full_time", "part_time", "contract", "permanent"
}
INTEGER_PARAMETERS = {"distance", "max_days_old", "salary_min", "salary_max"}
SORT_DIRECTIONS = {"up", "down"}
SORT_FIELDS = {"default", "hybrid", "date", "salary", "relevance"}


@dataclass(frozen=True, slots=True)
class SearchQuery:
    country: str
    parameters: dict[str, str]
    max_pages: int


class AdzunaCollector:
    name = "adzuna"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.app_id = config.get("ADZUNA_APP_ID", "").strip()
        self.app_key = config.get("ADZUNA_APP_KEY", "").strip()
        config_path = Path(config.get("ADZUNA_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.results_per_page = _bounded_int(
            settings.get("results_per_page", 50), "results_per_page", minimum=1
        )
        self.request_budget = _bounded_int(
            settings.get("request_budget", 11), "request_budget", minimum=0
        )
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        default_max_pages = _bounded_int(
            settings.get("max_pages_per_query", self.request_budget or 1),
            "max_pages_per_query",
            minimum=1,
        )
        self.queries = _parse_queries(settings.get("queries"), default_max_pages)
        self._opener = opener
        self._sleep = sleep
        self._request_count = 0

    def fetch(self) -> Iterable[NormalizedJob]:
        if not self.app_id or not self.app_key:
            raise ValueError(
                "ADZUNA_APP_ID and ADZUNA_APP_KEY must be set in the environment or sources/.env"
            )
        if not self.queries:
            raise ValueError("Adzuna queries are empty; edit sources/adzuna/config.yaml")
        if self.request_budget == 0:
            return

        self._request_count = 0
        completed: set[int] = set()
        seen_job_ids: set[str] = set()
        largest_page_limit = max(query.max_pages for query in self.queries)

        # Round-robin pagination lets every configured query get its first page
        # before one broad query can consume the complete per-run request budget.
        for page in range(1, largest_page_limit + 1):
            for index, query in enumerate(self.queries):
                if index in completed or page > query.max_pages:
                    continue
                if self._request_count >= self.request_budget:
                    return
                payload = self._search(query, page)
                results = payload.get("results")
                if not isinstance(results, list):
                    raise ValueError(f"Adzuna query {index + 1}, page {page} returned no results list")

                for item in results:
                    if not isinstance(item, dict):
                        continue
                    job = self._normalize(item)
                    if job.source_job_id in seen_job_ids:
                        continue
                    seen_job_ids.add(job.source_job_id)
                    yield job

                count = payload.get("count")
                reached_count = isinstance(count, int) and page * self.results_per_page >= count
                if len(results) < self.results_per_page or reached_count:
                    completed.add(index)
            if len(completed) == len(self.queries):
                return

    def _search(self, query: SearchQuery, page: int) -> dict[str, Any]:
        parameters = {
            "app_id": self.app_id,
            "app_key": self.app_key,
            "results_per_page": str(self.results_per_page),
            **query.parameters,
        }
        country = quote(query.country, safe="")
        url = f"{API_ROOT}/{country}/search/{page}?{urlencode(parameters)}"
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
        )
        context = f"Adzuna {query.country} search page {page}"
        return self._get_json(request, context)

    def _get_json(self, request: Request, context: str) -> dict[str, Any]:
        for attempt in range(3):
            if self._request_count >= self.request_budget:
                raise RuntimeError(f"{context} retry would exceed the per-run request budget")
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
                    raise RuntimeError(f"{context} returned HTTP {exc.code} after retries") from exc
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"{context} request failed: {exc.reason}") from exc
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"{context} returned invalid JSON") from exc
            self._sleep(2**attempt)
        raise AssertionError("unreachable")

    @staticmethod
    def _normalize(payload: dict[str, Any]) -> NormalizedJob:
        company_value = payload.get("company")
        company = _nested_string(company_value, "display_name", "canonical_name") or "Unknown company"
        location_value = payload.get("location")
        location = _nested_string(location_value, "display_name")
        if not location and isinstance(location_value, dict):
            area = location_value.get("area")
            if isinstance(area, list):
                location = ", ".join(str(part).strip() for part in reversed(area) if str(part).strip()) or None

        title = html_to_markdown(_as_string(payload.get("title")))
        description = html_to_markdown(_as_string(payload.get("description")))
        source_job_id = str(payload.get("id") or "").strip()
        source_url = str(payload.get("redirect_url") or "").strip()
        if not source_job_id or not source_url or not title:
            raise ValueError("Adzuna job is missing id, redirect_url, or title")

        remote_text = "\n".join((title, location or "", description)).casefold()
        remote = True if any(
            term in remote_text for term in ("remote", "work from home", "home based", "remoto")
        ) else None
        return NormalizedJob(
            source="adzuna",
            source_job_id=source_job_id,
            source_url=source_url,
            title=title,
            company=company,
            description=description,
            location=location,
            remote=remote,
            employment_type=_employment_type(payload),
            published_at=_as_string(payload.get("created")),
        )


def create_collector(config: Mapping[str, str]) -> AdzunaCollector:
    return AdzunaCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Adzuna config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Adzuna YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Adzuna config must be a YAML mapping: {path}")
    allowed = {
        "version", "request_budget", "results_per_page", "max_pages_per_query",
        "timeout_seconds", "queries",
    }
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown Adzuna config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Adzuna config version")
    return loaded


def _parse_queries(value: Any, default_max_pages: int) -> list[SearchQuery]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Adzuna queries must be a YAML list")
    queries: list[SearchQuery] = []
    for index, raw_query in enumerate(value, 1):
        if not isinstance(raw_query, dict):
            raise ValueError(f"Adzuna query {index} must be a mapping")
        allowed = SEARCH_PARAMETERS | {"country", "max_pages"}
        unknown = sorted(set(raw_query) - allowed)
        if unknown:
            raise ValueError(f"unknown fields in Adzuna query {index}: {', '.join(unknown)}")
        country = str(raw_query.get("country", "it")).strip().casefold()
        if country not in COUNTRIES:
            raise ValueError(f"unsupported country in Adzuna query {index}: {country}")
        max_pages = _bounded_int(
            raw_query.get("max_pages", default_max_pages),
            f"queries[{index}].max_pages",
            minimum=1,
        )
        parameters: dict[str, str] = {}
        for name in SEARCH_PARAMETERS:
            if name not in raw_query or raw_query[name] is None or raw_query[name] == "":
                continue
            parameters[name] = _query_parameter(name, raw_query[name], index)
        if not any(parameters.get(name) for name in ("what", "what_and", "what_phrase", "what_or", "title_only")):
            raise ValueError(f"Adzuna query {index} needs a search term such as 'what'")
        queries.append(SearchQuery(country, parameters, max_pages))
    return queries


def _query_parameter(name: str, value: Any, query_index: int) -> str:
    field = f"queries[{query_index}].{name}"
    if name in FLAG_PARAMETERS:
        if value in (True, 1, "1"):
            return "1"
        if value in (False, 0, "0"):
            raise ValueError(f"{field}: omit disabled flags instead of setting false")
        raise ValueError(f"{field} must be true or 1")
    if name in INTEGER_PARAMETERS:
        return str(_bounded_int(value, field, minimum=0))
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} cannot be empty")
    if name == "sort_dir" and result not in SORT_DIRECTIONS:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(SORT_DIRECTIONS))}")
    if name == "sort_by" and result not in SORT_FIELDS:
        raise ValueError(f"{field} must be one of: {', '.join(sorted(SORT_FIELDS))}")
    return result


def _bounded_int(value: Any, name: str, *, minimum: int) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
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


def _as_string(value: Any) -> str | None:
    return value if isinstance(value, str) and value.strip() else None


def _nested_string(value: Any, *keys: str) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in keys:
        result = _as_string(value.get(key))
        if result:
            return result.strip()
    return None


def _employment_type(payload: Mapping[str, Any]) -> str | None:
    values = []
    contract_time = _as_string(payload.get("contract_time"))
    contract_type = _as_string(payload.get("contract_type"))
    if contract_time:
        values.append(contract_time.replace("_", "-"))
    if contract_type:
        values.append(contract_type.replace("_", "-"))
    return ", ".join(values) or None
