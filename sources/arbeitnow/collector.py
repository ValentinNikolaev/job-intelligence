from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


API_ROOT = "https://www.arbeitnow.com/api/job-board-api"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


@dataclass(frozen=True, slots=True)
class ArbeitnowPage:
    jobs: list[NormalizedJob]
    next_url: str | None


class ArbeitnowCollector:
    name = "arbeitnow"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        config_path = Path(config.get("ARBEITNOW_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.max_pages = _optional_positive_int(settings.get("max_pages"), "max_pages")
        self.visa_sponsorship = _optional_bool(
            settings.get("visa_sponsorship"), "visa_sponsorship"
        )
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        self._opener = opener
        self._sleep = sleep
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        url = _initial_url(self.visa_sponsorship)
        visited_pages: set[str] = set()
        seen_job_ids: set[str] = set()
        page_number = 0

        while url:
            if self.max_pages is not None and page_number >= self.max_pages:
                return
            if url in visited_pages:
                raise RuntimeError(f"Arbeitnow pagination repeated a page URL: {url}")
            _validate_page_url(url, self.visa_sponsorship)
            visited_pages.add(url)
            page_number += 1

            request = Request(
                url,
                headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
            )
            payload = self._get_json(request, f"Arbeitnow page {page_number}")
            page = parse_api_response(payload)
            if not page.jobs:
                return

            for job in page.jobs:
                if job.source_job_id in seen_job_ids:
                    continue
                seen_job_ids.add(job.source_job_id)
                yield job
            url = page.next_url

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


def parse_api_response(payload: Mapping[str, Any]) -> ArbeitnowPage:
    raw_jobs = payload.get("data")
    if not isinstance(raw_jobs, list):
        raise ValueError("Arbeitnow response has no data list")

    jobs: list[NormalizedJob] = []
    for index, raw_job in enumerate(raw_jobs, 1):
        if not isinstance(raw_job, dict):
            raise ValueError(f"Arbeitnow job {index} is not an object")
        jobs.append(normalize_job(raw_job))

    # An empty data page is a valid end-of-feed response even if pagination
    # metadata is absent or stale.
    if not jobs:
        return ArbeitnowPage([], None)

    links = payload.get("links")
    if not isinstance(links, Mapping):
        raise ValueError("Arbeitnow response has no links object")
    raw_next = links.get("next")
    if raw_next is None:
        next_url = None
    elif isinstance(raw_next, str) and raw_next.strip():
        next_url = raw_next.strip()
    else:
        raise ValueError("Arbeitnow response has an invalid links.next value")
    return ArbeitnowPage(jobs, next_url)


def normalize_job(payload: Mapping[str, Any]) -> NormalizedJob:
    title = html_to_markdown(_as_string(payload.get("title")))
    company = _as_string(payload.get("company_name"))
    source_url = _as_string(payload.get("url"))
    if not title or not company or not source_url:
        raise ValueError("Arbeitnow job is missing title, company_name, or url")

    slug = _as_string(payload.get("slug"))
    source_job_id = slug or _url_identity(source_url)
    remote_value = payload.get("remote")
    remote = remote_value if isinstance(remote_value, bool) else None

    job_types = _string_list(payload.get("job_types"))
    tags = _string_list(payload.get("tags"))
    metadata: dict[str, Any] = {}
    if tags:
        metadata["tags"] = tags
    if job_types:
        metadata["job_types"] = job_types

    return NormalizedJob(
        source="arbeitnow",
        source_job_id=source_job_id,
        source_url=source_url,
        title=title,
        company=company,
        description=html_to_markdown(_as_string(payload.get("description"))),
        location=_as_string(payload.get("location")),
        remote=remote,
        employment_type=", ".join(job_types) or None,
        published_at=_epoch_timestamp(payload.get("created_at")),
        source_metadata=metadata,
    )


def create_collector(config: Mapping[str, str]) -> ArbeitnowCollector:
    return ArbeitnowCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Arbeitnow config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Arbeitnow YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Arbeitnow config must be a YAML mapping: {path}")
    allowed = {"version", "max_pages", "timeout_seconds", "visa_sponsorship"}
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown Arbeitnow config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Arbeitnow config version")
    return loaded


def _initial_url(visa_sponsorship: bool | None) -> str:
    if visa_sponsorship is None:
        return API_ROOT
    query = urlencode({"visa_sponsorship": str(visa_sponsorship).lower()})
    return f"{API_ROOT}?{query}"


def _validate_page_url(url: str, visa_sponsorship: bool | None) -> None:
    parsed = urlsplit(url)
    if (
        parsed.scheme != "https"
        or parsed.netloc.casefold() != "www.arbeitnow.com"
        or parsed.path.rstrip("/") != "/api/job-board-api"
        or parsed.fragment
    ):
        raise RuntimeError(f"Arbeitnow returned an invalid pagination URL: {url}")
    if visa_sponsorship is not None:
        expected = f"visa_sponsorship={str(visa_sponsorship).lower()}"
        if expected not in parsed.query.split("&"):
            raise RuntimeError("Arbeitnow pagination dropped the visa_sponsorship filter")


def _url_identity(url: str) -> str:
    parsed = urlsplit(url)
    canonical = urlunsplit(
        (parsed.scheme.casefold(), parsed.netloc.casefold(), parsed.path, parsed.query, "")
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    return f"url-sha256:{digest}"


def _epoch_timestamp(value: Any) -> str | None:
    if isinstance(value, bool):
        return None
    try:
        timestamp = int(value)
        result = datetime.fromtimestamp(timestamp, timezone.utc).replace(microsecond=0)
    except (TypeError, ValueError, OverflowError, OSError):
        return None
    return result.isoformat().replace("+00:00", "Z")


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _as_string(value: Any) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None


def _optional_positive_int(value: Any, name: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError(f"{name} must be an integer or null")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be an integer or null") from exc
    if result < 1:
        raise ValueError(f"{name} must be at least 1")
    return result


def _optional_bool(value: Any, name: str) -> bool | None:
    if value is None or isinstance(value, bool):
        return value
    raise ValueError(f"{name} must be true, false, or null")


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
