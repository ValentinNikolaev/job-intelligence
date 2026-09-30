from __future__ import annotations

import hashlib
import json
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


API_ROOT = "https://jobicy.com/api/v2/remote-jobs"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
QUERY_PARAMETERS = {"count", "geo", "industry", "tag"}


@dataclass(frozen=True, slots=True)
class QueryProfile:
    index: int
    parameters: dict[str, str]

    def discovery_metadata(self) -> dict[str, Any]:
        return {"query_index": self.index, "parameters": dict(self.parameters)}


class JobicyCollector:
    name = "jobicy"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        config_path = Path(config.get("JOBICY_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        self.queries = _parse_queries(settings.get("queries"))
        self._opener = opener
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        if not self.queries:
            raise ValueError("Jobicy queries are empty; edit sources/jobicy/config.yaml")

        jobs_by_id: dict[str, NormalizedJob] = {}
        for query in self.queries:
            payload = self._search(query)
            jobs = parse_api_response(payload)
            discovery = query.discovery_metadata()
            for job in jobs:
                job = replace(job, source_metadata={**job.source_metadata, "discovered_by": [discovery]})
                existing = jobs_by_id.get(job.source_job_id)
                if existing is None:
                    jobs_by_id[job.source_job_id] = job
                    continue
                discoveries = list(existing.source_metadata.get("discovered_by", []))
                if discovery not in discoveries:
                    discoveries.append(discovery)
                    jobs_by_id[job.source_job_id] = replace(
                        existing,
                        source_metadata={**existing.source_metadata, "discovered_by": discoveries},
                    )

        yield from jobs_by_id.values()

    def _search(self, query: QueryProfile) -> dict[str, Any]:
        url = f"{API_ROOT}?{urlencode(query.parameters)}" if query.parameters else API_ROOT
        request = Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
        )
        context = f"Jobicy query {query.index}"
        try:
            self._request_count += 1
            with self._opener(request, timeout=self.timeout) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise RuntimeError(f"{context} returned HTTP {exc.code}") from exc
        except TimeoutError as exc:
            raise RuntimeError(f"{context} timed out") from exc
        except URLError as exc:
            raise RuntimeError(f"{context} request failed: {exc.reason}") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"{context} returned invalid JSON") from exc
        if not isinstance(payload, dict):
            raise ValueError(f"expected JSON object from {context}")
        return payload


def parse_api_response(payload: Mapping[str, Any]) -> list[NormalizedJob]:
    raw_jobs = payload.get("jobs")
    if not isinstance(raw_jobs, list):
        raise ValueError("Jobicy response has no jobs list")

    jobs: list[NormalizedJob] = []
    for index, raw_job in enumerate(raw_jobs, 1):
        if not isinstance(raw_job, Mapping):
            raise ValueError(f"Jobicy job {index} is not an object")
        jobs.append(normalize_job(raw_job))
    return jobs


def normalize_job(payload: Mapping[str, Any]) -> NormalizedJob:
    title = html_to_markdown(_as_string(payload.get("jobTitle")))
    company = _as_string(payload.get("companyName"))
    source_url = _as_string(payload.get("url"))
    if not title or not company or not source_url:
        raise ValueError("Jobicy job is missing jobTitle, companyName, or url")

    job_id = _identity_value(payload.get("id"))
    source_job_id = job_id or _url_identity(source_url)
    description = html_to_markdown(_as_string(payload.get("jobDescription")))
    if not description:
        description = html_to_markdown(_as_string(payload.get("jobExcerpt")))

    metadata: dict[str, Any] = {}
    metadata_fields = {
        "company_logo": "companyLogo",
        "industry": "jobIndustry",
        "level": "jobLevel",
    }
    for target, source in metadata_fields.items():
        value = payload.get(source)
        if value not in (None, "", [], {}):
            metadata[target] = value
    excerpt = html_to_markdown(_as_string(payload.get("jobExcerpt")))
    if excerpt:
        metadata["excerpt"] = excerpt
    salary = _salary_metadata(payload)
    if salary:
        metadata["salary"] = salary

    return NormalizedJob(
        source="jobicy",
        source_job_id=source_job_id,
        source_url=source_url,
        title=title,
        company=company,
        description=description,
        location=_as_string(payload.get("jobGeo")),
        remote=True,
        employment_type=_as_string(payload.get("jobType")),
        published_at=_timestamp(payload.get("pubDate")),
        source_metadata=metadata,
    )


def create_collector(config: Mapping[str, str]) -> JobicyCollector:
    return JobicyCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Jobicy config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Jobicy YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Jobicy config must be a YAML mapping: {path}")
    allowed = {"version", "timeout_seconds", "queries"}
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown Jobicy config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Jobicy config version")
    return loaded


def _parse_queries(value: Any) -> list[QueryProfile]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("Jobicy queries must be a YAML list")

    queries: list[QueryProfile] = []
    for index, raw_query in enumerate(value, 1):
        if not isinstance(raw_query, dict):
            raise ValueError(f"Jobicy query {index} must be a mapping")
        unknown = sorted(set(raw_query) - QUERY_PARAMETERS)
        if unknown:
            raise ValueError(f"unknown fields in Jobicy query {index}: {', '.join(unknown)}")

        parameters: dict[str, str] = {}
        for name in QUERY_PARAMETERS:
            value = raw_query.get(name)
            if value is None or value == "":
                continue
            if name == "count":
                parameters[name] = str(_count(value, f"queries[{index}].count"))
            else:
                parameters[name] = _required_string(value, f"queries[{index}].{name}")
        queries.append(QueryProfile(index, parameters))
    return queries


def _salary_metadata(payload: Mapping[str, Any]) -> dict[str, Any]:
    minimum = _number(payload.get("salaryMin"))
    maximum = _number(payload.get("salaryMax"))
    currency = _as_string(payload.get("salaryCurrency"))
    period = _as_string(payload.get("salaryPeriod"))
    if minimum is None and maximum is None and not currency and not period:
        return {}
    salary: dict[str, Any] = {}
    if minimum is not None:
        salary["min"] = minimum
    if maximum is not None:
        salary["max"] = maximum
    if currency:
        salary["currency"] = currency.upper()
    if period:
        salary["period"] = period.casefold()
    return salary


def _timestamp(value: Any) -> str | None:
    text = _as_string(value)
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return text
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace(
        "+00:00", "Z"
    )


def _url_identity(url: str) -> str:
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return f"url-sha256:{digest}"


def _identity_value(value: Any) -> str | None:
    if isinstance(value, bool) or value is None:
        return None
    result = str(value).strip()
    return result or None


def _number(value: Any) -> int | float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        number = value
    elif isinstance(value, str):
        try:
            number = float(value.strip().replace(",", ""))
        except ValueError:
            return None
    else:
        return None
    return int(number) if float(number).is_integer() else number


def _count(value: Any, name: str) -> int:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer from 1 to 100")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer from 1 to 100") from exc
    if not 1 <= result <= 100:
        raise ValueError(f"{name} must be from 1 to 100")
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
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _as_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None
