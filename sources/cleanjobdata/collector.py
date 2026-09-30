from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://api.cleanjobdata.com/jobs"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
PARAMETERS = {
    "title",
    "search",
    "sort_by",
    "city_id",
    "state_id",
    "country_id",
    "location",
    "remote",
    "remote_type",
    "company_name",
    "employer_id",
    "company_website_url",
    "domain",
    "salary",
    "min_salary",
    "require_salary",
    "experience_level",
    "employment_type",
    "published_after",
    "max_age",
    "created_max_age",
    "include_expired",
}
BOOLEAN_PARAMETERS = {"remote", "require_salary", "include_expired"}


@dataclass(frozen=True, slots=True)
class SearchProfile:
    name: str
    parameters: dict[str, str]
    limit: int
    max_pages: int
    extra_fields: str


class CleanJobDataCollector:
    name = "cleanjobdata"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
        monotonic: Callable[[], float] = time.monotonic,
    ) -> None:
        self.api_key = config.get("CLEANJOBDATA_API_KEY", "").strip()
        config_path = Path(config.get("CLEANJOBDATA_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.request_budget = _bounded_int(
            settings.get("request_budget", 4), "request_budget", minimum=0
        )
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        self.min_request_interval = _non_negative_float(
            settings.get("min_request_interval_seconds", 1),
            "min_request_interval_seconds",
        )
        default_limit = _bounded_int(settings.get("limit", 20), "limit", minimum=1, maximum=100)
        default_max_pages = _bounded_int(
            settings.get("max_pages_per_profile", self.request_budget or 1),
            "max_pages_per_profile",
            minimum=1,
        )
        default_extra_fields = _csv_fields(settings.get("extra_fields", ["description"]), "extra_fields")
        self.profiles = _parse_profiles(
            settings.get("search_profiles"),
            default_limit,
            default_max_pages,
            default_extra_fields,
        )
        self._opener = opener
        self._sleep = sleep
        self._monotonic = monotonic
        self._last_request_at: float | None = None
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        if not self.api_key:
            raise ValueError("CLEANJOBDATA_API_KEY must be set in the environment or sources/.env")
        if not self.profiles:
            raise ValueError(
                "CleanJobData search profiles are empty; edit sources/cleanjobdata/config.yaml"
            )
        if self.request_budget == 0:
            return

        self._request_count = 0
        cursors: dict[int, str | None] = {}
        completed: set[int] = set()
        seen_job_ids: set[str] = set()
        largest_page_limit = max(profile.max_pages for profile in self.profiles)

        for page in range(1, largest_page_limit + 1):
            for index, profile in enumerate(self.profiles):
                if index in completed or page > profile.max_pages:
                    continue
                if self._request_count >= self.request_budget:
                    return

                payload = self._search(profile, cursors.get(index), page)
                results = payload.get("data")
                if not isinstance(results, list):
                    raise ValueError(
                        f"CleanJobData profile {profile.name!r}, page {page} returned no data list"
                    )

                for item in results:
                    if not isinstance(item, dict):
                        continue
                    job = self._normalize(item, profile.name)
                    if job.source_job_id in seen_job_ids:
                        continue
                    seen_job_ids.add(job.source_job_id)
                    yield job

                pagination = payload.get("pagination")
                next_page = pagination.get("next_page") if isinstance(pagination, dict) else None
                cursors[index] = str(next_page).strip() if next_page else None
                if not results or not cursors[index] or len(results) < profile.limit:
                    completed.add(index)
            if len(completed) == len(self.profiles):
                return

    def _search(self, profile: SearchProfile, cursor: str | None, page: int) -> dict[str, Any]:
        parameters = {
            **profile.parameters,
            "limit": str(profile.limit),
            "extra_fields": profile.extra_fields,
        }
        if cursor:
            parameters["cursor"] = cursor
        request = Request(
            f"{API_ROOT}?{urlencode(parameters)}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {self.api_key}",
                "User-Agent": "job-intelligence/0.1",
            },
        )
        return self._get_json(request, f"CleanJobData profile {profile.name!r} page {page}")

    def _get_json(self, request: Request, context: str) -> dict[str, Any]:
        for attempt in range(3):
            if self._request_count >= self.request_budget:
                raise RuntimeError(f"{context} retry would exceed the per-run request budget")
            self._throttle()
            self._request_count += 1
            try:
                with self._opener(request, timeout=self.timeout) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if not isinstance(payload, dict):
                    raise ValueError(f"expected JSON object from {context}")
                return payload
            except HTTPError as exc:
                if exc.code in (401, 403):
                    raise RuntimeError(f"{context} was denied: check CLEANJOBDATA_API_KEY") from exc
                if exc.code != 429 and exc.code < 500:
                    raise RuntimeError(f"{context} returned HTTP {exc.code}") from exc
                if attempt == 2:
                    raise RuntimeError(f"{context} returned HTTP {exc.code} after retries") from exc
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"{context} request failed: {exc.reason}") from exc
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise RuntimeError(f"{context} returned invalid JSON") from exc
            self._sleep(max(2**attempt, self.min_request_interval))
        raise AssertionError("unreachable")

    def _throttle(self) -> None:
        if self.min_request_interval <= 0:
            self._last_request_at = self._monotonic()
            return
        now = self._monotonic()
        if self._last_request_at is not None:
            wait = self.min_request_interval - (now - self._last_request_at)
            if wait > 0:
                self._sleep(wait)
                now = self._monotonic()
        self._last_request_at = now

    @staticmethod
    def _normalize(payload: Mapping[str, Any], profile_name: str) -> NormalizedJob:
        title = html_to_markdown(_as_string(payload.get("title")))
        description = html_to_markdown(_as_string(payload.get("description")))
        source_job_id = str(payload.get("id") or "").strip()
        source_url = _as_string(payload.get("application_url"))
        if not source_job_id or not source_url or not title:
            raise ValueError("CleanJobData job is missing id, application_url, or title")

        company_value = payload.get("company")
        company = _nested_string(company_value, "name") or "Unknown company"
        location = _location(payload)
        remote = payload.get("has_remote") if isinstance(payload.get("has_remote"), bool) else None
        company_url = _nested_string(company_value, "website_url")
        company_description = _nested_string(company_value, "description")

        metadata = _source_metadata(payload, profile_name)
        return NormalizedJob(
            source="cleanjobdata",
            source_job_id=source_job_id,
            source_url=source_url,
            title=title,
            company=company,
            description=description,
            company_url=company_url,
            location=location,
            remote=remote,
            employment_type=_as_string(payload.get("employment_type")),
            published_at=_as_string(payload.get("published")),
            company_description=company_description,
            source_metadata=metadata,
        )


def create_collector(config: Mapping[str, str]) -> CleanJobDataCollector:
    return CleanJobDataCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read CleanJobData config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid CleanJobData YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"CleanJobData config must be a YAML mapping: {path}")
    allowed = {
        "version",
        "request_budget",
        "limit",
        "max_pages_per_profile",
        "timeout_seconds",
        "min_request_interval_seconds",
        "extra_fields",
        "search_profiles",
    }
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown CleanJobData config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported CleanJobData config version")
    return loaded


def _parse_profiles(
    value: Any,
    default_limit: int,
    default_max_pages: int,
    default_extra_fields: str,
) -> list[SearchProfile]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("CleanJobData search_profiles must be a YAML list")

    profiles: list[SearchProfile] = []
    names: set[str] = set()
    allowed = PARAMETERS | {"name", "enabled", "limit", "max_pages", "extra_fields"}
    for index, raw_profile in enumerate(value, 1):
        if not isinstance(raw_profile, dict):
            raise ValueError(f"CleanJobData search profile {index} must be a mapping")
        unknown = sorted(set(raw_profile) - allowed)
        if unknown:
            raise ValueError(
                f"unknown fields in CleanJobData search profile {index}: {', '.join(unknown)}"
            )
        enabled = raw_profile.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"search_profiles[{index}].enabled must be true or false")
        if not enabled:
            continue

        name = _required_string(raw_profile.get("name"), f"search_profiles[{index}].name")
        normalized_name = name.casefold()
        if normalized_name in names:
            raise ValueError(f"duplicate CleanJobData search profile name: {name}")
        names.add(normalized_name)

        parameters: dict[str, str] = {}
        for parameter in PARAMETERS:
            if parameter not in raw_profile or raw_profile[parameter] in (None, ""):
                continue
            parameters[parameter] = _query_parameter(parameter, raw_profile[parameter], index)
        if not any(parameters.get(name) for name in ("title", "search", "company_name", "employer_id")):
            raise ValueError(
                f"CleanJobData search profile {index} needs title, search, company_name, or employer_id"
            )

        limit = _bounded_int(
            raw_profile.get("limit", default_limit),
            f"search_profiles[{index}].limit",
            minimum=1,
            maximum=100,
        )
        max_pages = _bounded_int(
            raw_profile.get("max_pages", default_max_pages),
            f"search_profiles[{index}].max_pages",
            minimum=1,
        )
        extra_fields = _csv_fields(
            raw_profile.get("extra_fields", default_extra_fields),
            f"search_profiles[{index}].extra_fields",
        )
        profiles.append(SearchProfile(name, parameters, limit, max_pages, extra_fields))
    return profiles


def _query_parameter(name: str, value: Any, profile_index: int) -> str:
    field = f"search_profiles[{profile_index}].{name}"
    if name in BOOLEAN_PARAMETERS:
        if value is True:
            return "true"
        if value is False:
            return "false"
        if isinstance(value, str) and value.strip().casefold() in {"true", "false"}:
            return value.strip().casefold()
        raise ValueError(f"{field} must be true or false")
    result = str(value).strip()
    if not result:
        raise ValueError(f"{field} cannot be empty")
    return result


def _csv_fields(value: Any, name: str) -> str:
    if isinstance(value, str):
        fields = [part.strip() for part in value.split(",")]
    elif isinstance(value, list):
        fields = [str(part).strip() for part in value]
    else:
        raise ValueError(f"{name} must be a comma-separated string or list")
    fields = [field for field in fields if field]
    if not fields:
        raise ValueError(f"{name} cannot be empty")
    return ",".join(fields)


def _bounded_int(value: Any, name: str, *, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer") from exc
    if result < minimum:
        raise ValueError(f"{name} must be at least {minimum}")
    if maximum is not None and result > maximum:
        raise ValueError(f"{name} must be at most {maximum}")
    return result


def _positive_float(value: Any, name: str) -> float:
    result = _non_negative_float(value, name)
    if result <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return result


def _non_negative_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if result < 0:
        raise ValueError(f"{name} must be at least zero")
    return result


def _required_string(value: Any, name: str) -> str:
    result = str(value or "").strip()
    if not result:
        raise ValueError(f"{name} cannot be empty")
    return result


def _as_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _nested_string(value: Any, *keys: str) -> str | None:
    if not isinstance(value, dict):
        return None
    for key in keys:
        result = _as_string(value.get(key))
        if result:
            return result
    return None


def _location(payload: Mapping[str, Any]) -> str | None:
    location = _as_string(payload.get("location"))
    if location:
        return location
    locations = payload.get("locations")
    if not isinstance(locations, list):
        return None
    labels: list[str] = []
    for item in locations:
        if not isinstance(item, dict):
            continue
        label = _as_string(item.get("display_label"))
        if label and label not in labels:
            labels.append(label)
    return "; ".join(labels) or None


def _source_metadata(payload: Mapping[str, Any], profile_name: str) -> dict[str, Any]:
    metadata: dict[str, Any] = {"profile": profile_name}
    for key in (
        "employer_id",
        "remote_type",
        "is_active",
        "expired_at",
        "language",
        "salary_min",
        "salary_max",
        "salary_currency",
        "salary_text",
        "experience_level",
        "experience_levels",
    ):
        value = payload.get(key)
        if value not in (None, "", []):
            metadata[key] = value
    company = payload.get("company")
    if isinstance(company, dict):
        for source_key, target_key in (
            ("industry", "company_industry"),
            ("employee_count", "company_employee_count"),
            ("linkedin_url", "company_linkedin_url"),
            ("github_url", "company_github_url"),
        ):
            value = company.get(source_key)
            if value not in (None, "", []):
                metadata[target_key] = value
    return metadata
