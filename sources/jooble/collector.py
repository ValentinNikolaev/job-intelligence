from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://jooble.org/api"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
RADIUS_VALUES = {"0", "4", "8", "16", "26", "40", "80"}


@dataclass(frozen=True, slots=True)
class QueryProfile:
    name: str
    parameters: dict[str, object]
    results_per_page: int
    max_pages: int


class JoobleCollector:
    name = "jooble"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        self.api_key = config.get("JOOBLE_API_KEY", "").strip()
        config_path = Path(config.get("JOOBLE_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.request_budget = _bounded_int(
            settings.get("request_budget", 10), "request_budget", minimum=0
        )
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        default_results_per_page = _bounded_int(
            settings.get("results_per_page", 50), "results_per_page", minimum=1
        )
        default_max_pages = _bounded_int(
            settings.get("max_pages_per_profile", self.request_budget or 1),
            "max_pages_per_profile",
            minimum=1,
        )
        self.profiles = _parse_profiles(
            settings.get("query_profiles"),
            default_results_per_page,
            default_max_pages,
        )
        self._opener = opener
        self._sleep = sleep
        self._request_count = 0

    def fetch(self) -> Iterable[NormalizedJob]:
        if not self.api_key:
            raise ValueError("JOOBLE_API_KEY must be set in the environment or sources/.env")
        if not self.profiles:
            raise ValueError("Jooble query profiles are empty; edit sources/jooble/config.yaml")
        if self.request_budget == 0:
            return

        self._request_count = 0
        completed: set[int] = set()
        seen_job_ids: set[str] = set()
        largest_page_limit = max(profile.max_pages for profile in self.profiles)

        # Profiles are paginated round-robin so every enabled search receives
        # its first page before a broad search can consume the run budget.
        for page in range(1, largest_page_limit + 1):
            for index, profile in enumerate(self.profiles):
                if index in completed or page > profile.max_pages:
                    continue
                if self._request_count >= self.request_budget:
                    return

                payload = self._search(profile, page)
                results = payload.get("jobs")
                if not isinstance(results, list):
                    raise ValueError(
                        f"Jooble profile {profile.name!r}, page {page} returned no jobs list"
                    )

                for item in results:
                    if not isinstance(item, dict):
                        continue
                    job = self._normalize(item)
                    if job.source_job_id in seen_job_ids:
                        continue
                    seen_job_ids.add(job.source_job_id)
                    yield job

                total_count = payload.get("totalCount")
                reached_count = (
                    isinstance(total_count, int)
                    and page * profile.results_per_page >= total_count
                )
                if not results or reached_count or (
                    not isinstance(total_count, int)
                    and len(results) < profile.results_per_page
                ):
                    completed.add(index)
            if len(completed) == len(self.profiles):
                return

    def _search(self, profile: QueryProfile, page: int) -> dict[str, Any]:
        body = {
            **profile.parameters,
            "page": page,
            "ResultOnPage": profile.results_per_page,
        }
        request = Request(
            f"{API_ROOT}/{quote(self.api_key, safe='')}",
            data=json.dumps(body).encode("utf-8"),
            headers={
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "job-intelligence/0.1",
            },
            method="POST",
        )
        return self._get_json(request, f"Jooble profile {profile.name!r} page {page}")

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
                if exc.code == 403:
                    raise RuntimeError(f"{context} was denied: check JOOBLE_API_KEY") from exc
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
    def _normalize(payload: Mapping[str, Any]) -> NormalizedJob:
        title = html_to_markdown(_as_string(payload.get("title")))
        description = html_to_markdown(_as_string(payload.get("snippet")))
        source_job_id = str(payload.get("id") or "").strip()
        source_url = str(payload.get("link") or "").strip()
        if not source_job_id or not source_url or not title:
            raise ValueError("Jooble job is missing id, link, or title")

        company = _as_string(payload.get("company")) or "Unknown company"
        location = _as_string(payload.get("location"))
        employment_type = _as_string(payload.get("type"))
        remote_text = "\n".join((title, location or "", description)).casefold()
        remote = True if any(
            term in remote_text
            for term in (
                "remote",
                "work from home",
                "home based",
                "remoto",
                "da remoto",
                "lavoro da casa",
                "smart working",
            )
        ) else None
        return NormalizedJob(
            source="jooble",
            source_job_id=source_job_id,
            source_url=source_url,
            title=title,
            company=company,
            description=description,
            location=location,
            remote=remote,
            employment_type=employment_type,
            published_at=_as_string(payload.get("updated")),
        )


def create_collector(config: Mapping[str, str]) -> JoobleCollector:
    return JoobleCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Jooble config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Jooble YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Jooble config must be a YAML mapping: {path}")
    allowed = {
        "version",
        "request_budget",
        "results_per_page",
        "max_pages_per_profile",
        "timeout_seconds",
        "query_profiles",
    }
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown Jooble config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Jooble config version")
    return loaded


def _parse_profiles(
    value: Any,
    default_results_per_page: int,
    default_max_pages: int,
) -> list[QueryProfile]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Jooble query_profiles must be a YAML list")

    profiles: list[QueryProfile] = []
    names: set[str] = set()
    allowed = {
        "name",
        "enabled",
        "keywords",
        "location",
        "radius",
        "salary",
        "search_mode",
        "company_search",
        "results_per_page",
        "max_pages",
    }
    for index, raw_profile in enumerate(value, 1):
        if not isinstance(raw_profile, dict):
            raise ValueError(f"Jooble query profile {index} must be a mapping")
        unknown = sorted(set(raw_profile) - allowed)
        if unknown:
            raise ValueError(
                f"unknown fields in Jooble query profile {index}: {', '.join(unknown)}"
            )
        enabled = raw_profile.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"query_profiles[{index}].enabled must be true or false")
        if not enabled:
            continue

        name = str(raw_profile.get("name") or "").strip()
        if not name:
            raise ValueError(f"Jooble query profile {index} needs a name")
        normalized_name = name.casefold()
        if normalized_name in names:
            raise ValueError(f"duplicate Jooble query profile name: {name}")
        names.add(normalized_name)

        keywords = _required_string(raw_profile.get("keywords"), f"query_profiles[{index}].keywords")
        location = _required_string(raw_profile.get("location"), f"query_profiles[{index}].location")
        parameters: dict[str, object] = {"keywords": keywords, "location": location}

        if "radius" in raw_profile:
            radius = str(raw_profile["radius"]).strip()
            if radius not in RADIUS_VALUES:
                raise ValueError(
                    f"query_profiles[{index}].radius must be one of: "
                    f"{', '.join(sorted(RADIUS_VALUES, key=int))}"
                )
            parameters["radius"] = radius
        if "salary" in raw_profile:
            parameters["salary"] = _bounded_int(
                raw_profile["salary"], f"query_profiles[{index}].salary", minimum=0
            )
        if "search_mode" in raw_profile:
            parameters["SearchMode"] = _bounded_int(
                raw_profile["search_mode"],
                f"query_profiles[{index}].search_mode",
                minimum=0,
            )
        if "company_search" in raw_profile:
            company_search = raw_profile["company_search"]
            if not isinstance(company_search, bool):
                raise ValueError(
                    f"query_profiles[{index}].company_search must be true or false"
                )
            parameters["companysearch"] = company_search

        results_per_page = _bounded_int(
            raw_profile.get("results_per_page", default_results_per_page),
            f"query_profiles[{index}].results_per_page",
            minimum=1,
        )
        max_pages = _bounded_int(
            raw_profile.get("max_pages", default_max_pages),
            f"query_profiles[{index}].max_pages",
            minimum=1,
        )
        profiles.append(QueryProfile(name, parameters, results_per_page, max_pages))
    return profiles


def _required_string(value: Any, name: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{name} cannot be empty")
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
    return value.strip() if isinstance(value, str) and value.strip() else None
