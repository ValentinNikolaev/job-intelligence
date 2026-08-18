from __future__ import annotations

import hashlib
import re
import time
import xml.etree.ElementTree as ET
from dataclasses import dataclass, replace
from datetime import timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
USER_AGENT = "job-intelligence/0.1"


@dataclass(frozen=True, slots=True)
class Feed:
    index: int
    name: str
    url: str


class WeWorkRemotelyCollector:
    name = "weworkremotely"

    def __init__(self, config: Mapping[str, str], *, opener: Callable[..., Any] = urlopen,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        config_path = Path(config.get("WEWORKREMOTELY_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        self.feeds = _parse_feeds(settings.get("feeds"))
        self._opener = opener
        self._sleep = sleep
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        if not self.feeds:
            raise ValueError("We Work Remotely feeds are empty; edit sources/weworkremotely/config.yaml")
        jobs_by_id: dict[str, NormalizedJob] = {}
        for feed in self.feeds:
            request = Request(feed.url, headers={
                "Accept": "application/rss+xml, application/xml;q=0.9", "User-Agent": USER_AGENT,
            })
            payload = self._get_bytes(request, f"We Work Remotely feed {feed.name!r}")
            discovery = {"feed_index": feed.index, "feed": feed.name, "url": feed.url}
            for job in parse_feed(payload):
                existing = jobs_by_id.get(job.source_job_id)
                if existing is None:
                    metadata = dict(job.source_metadata)
                    metadata["discovered_by"] = [discovery]
                    jobs_by_id[job.source_job_id] = replace(job, source_metadata=metadata)
                else:
                    discoveries = list(existing.source_metadata.get("discovered_by", []))
                    if discovery not in discoveries:
                        discoveries.append(discovery)
                        metadata = dict(existing.source_metadata)
                        metadata["discovered_by"] = discoveries
                        jobs_by_id[job.source_job_id] = replace(existing, source_metadata=metadata)
        yield from jobs_by_id.values()

    def _get_bytes(self, request: Request, context: str) -> bytes:
        for attempt in range(3):
            self._request_count += 1
            try:
                with self._opener(request, timeout=self.timeout) as response:
                    return response.read()
            except HTTPError as exc:
                if exc.code != 429 and exc.code < 500:
                    raise RuntimeError(f"{context} returned HTTP {exc.code}") from exc
                if attempt == 2:
                    raise RuntimeError(f"{context} returned HTTP {exc.code} after retries") from exc
            except TimeoutError as exc:
                if attempt == 2: raise RuntimeError(f"{context} timed out after retries") from exc
            except URLError as exc:
                if attempt == 2: raise RuntimeError(f"{context} request failed: {exc.reason}") from exc
            self._sleep(2**attempt)
        raise AssertionError("unreachable")


def parse_feed(payload: bytes | str) -> list[NormalizedJob]:
    try:
        root = ET.fromstring(payload)
    except (ET.ParseError, ValueError) as exc:
        raise RuntimeError("We Work Remotely feed returned invalid XML") from exc
    jobs: list[NormalizedJob] = []
    seen: set[str] = set()
    for index, item in enumerate(_descendants(root, "item"), 1):
        try: job = normalize_item(item)
        except ValueError as exc: raise ValueError(f"We Work Remotely item {index}: {exc}") from exc
        if job.source_job_id not in seen:
            seen.add(job.source_job_id)
            jobs.append(job)
    return jobs


def normalize_item(item: ET.Element) -> NormalizedJob:
    combined = html_to_markdown(_first_text(item, "title"))
    company, separator, title = combined.partition(":")
    company, title = company.strip(), title.strip()
    source_url = _clean_string(_first_text(item, "link"))
    if not separator or not company or not title or not source_url:
        raise ValueError("missing 'Company: Role' title or link")
    description = _first_text(item, "encoded") or _first_text(item, "description")
    region = _clean_string(_first_text(item, "region"))
    country = _clean_string(_first_text(item, "country"))
    state = _clean_string(_first_text(item, "state"))
    restrictions = _unique_strings([region, country, state])
    categories = _all_text(item, "category")
    skills = _list_values(_all_text(item, "skills"))
    metadata: dict[str, Any] = {}
    if categories: metadata["categories"] = categories
    if skills: metadata["skills"] = skills
    if restrictions: metadata["location_restrictions"] = restrictions
    expires_at = _rss_timestamp(_first_text(item, "expires_at"))
    if expires_at: metadata["expires_at"] = expires_at
    return NormalizedJob(
        source="weworkremotely", source_job_id=_source_job_id(item, source_url),
        source_url=source_url, title=title, company=company,
        description=html_to_markdown(description), location=", ".join(restrictions) or None,
        remote=True, employment_type=_clean_string(_first_text(item, "type")),
        published_at=_rss_timestamp(_first_text(item, "pubDate")), source_metadata=metadata,
    )


def create_collector(config: Mapping[str, str]) -> WeWorkRemotelyCollector:
    return WeWorkRemotelyCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try: loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc: raise ValueError(f"cannot read We Work Remotely config {path}: {exc}") from exc
    except yaml.YAMLError as exc: raise ValueError(f"invalid We Work Remotely YAML config {path}: {exc}") from exc
    if loaded is None: return {}
    if not isinstance(loaded, dict): raise ValueError(f"We Work Remotely config must be a YAML mapping: {path}")
    unknown = sorted(set(loaded) - {"version", "timeout_seconds", "feeds"})
    if unknown: raise ValueError(f"unknown We Work Remotely config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1: raise ValueError("unsupported We Work Remotely config version")
    return loaded


def _parse_feeds(value: Any) -> list[Feed]:
    if value is None: return []
    if not isinstance(value, list): raise ValueError("We Work Remotely feeds must be a YAML list")
    feeds: list[Feed] = []
    names: set[str] = set()
    urls: set[str] = set()
    for index, raw in enumerate(value, 1):
        if not isinstance(raw, dict): raise ValueError(f"We Work Remotely feed {index} must be a mapping")
        unknown = sorted(set(raw) - {"name", "url", "enabled"})
        if unknown: raise ValueError(f"unknown fields in We Work Remotely feed {index}: {', '.join(unknown)}")
        enabled = raw.get("enabled", True)
        if not isinstance(enabled, bool): raise ValueError(f"feeds[{index}].enabled must be true or false")
        if not enabled: continue
        name = _required_string(raw.get("name"), f"feeds[{index}].name")
        url = _feed_url(raw.get("url"), index)
        if name.casefold() in names: raise ValueError(f"duplicate We Work Remotely feed name: {name}")
        if url in urls: raise ValueError(f"duplicate We Work Remotely feed URL: {url}")
        names.add(name.casefold()); urls.add(url); feeds.append(Feed(index, name, url))
    return feeds


def _feed_url(value: Any, index: int) -> str:
    url = _required_string(value, f"feeds[{index}].url")
    parsed = urlsplit(url)
    if (parsed.scheme != "https" or not parsed.hostname or
        parsed.hostname.casefold() not in {"weworkremotely.com", "www.weworkremotely.com"} or
        not parsed.path.endswith(".rss") or parsed.query or parsed.fragment):
        raise ValueError(f"feeds[{index}].url must be an official HTTPS weworkremotely.com RSS URL")
    return url


def _source_job_id(item: ET.Element, source_url: str) -> str:
    guid = _clean_string(_first_text(item, "guid"))
    if guid: return guid
    digest = hashlib.sha256(_canonical_url(source_url).encode("utf-8")).hexdigest()
    return f"url-sha256:{digest}"


def _rss_timestamp(value: str | None) -> str | None:
    if not value: return None
    try: parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError): return None
    if parsed.tzinfo is None: parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _descendants(root: ET.Element, name: str) -> Iterable[ET.Element]:
    return (element for element in root.iter() if _local_name(element.tag) == name)


def _first_text(element: ET.Element, *names: str) -> str | None:
    expected = {name.casefold() for name in names}
    for child in element.iter():
        if child is not element and _local_name(child.tag).casefold() in expected:
            value = "".join(child.itertext()).strip()
            if value: return value
    return None


def _all_text(element: ET.Element, name: str) -> list[str]:
    values: list[str] = []
    for child in element.iter():
        if _local_name(child.tag).casefold() == name.casefold():
            value = "".join(child.itertext()).strip()
            if value and value not in values: values.append(value)
    return values


def _list_values(values: list[str]) -> list[str]:
    result: list[str] = []
    for value in values:
        for part in re.split(r"[,;]", value):
            cleaned = part.strip()
            if cleaned and cleaned not in result: result.append(cleaned)
    return result


def _unique_strings(values: Iterable[str | None]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value and value.casefold() not in seen:
            seen.add(value.casefold()); result.append(value)
    return result


def _local_name(tag: str) -> str: return tag.rsplit("}", 1)[-1]
def _canonical_url(value: str) -> str:
    parsed = urlsplit(value)
    return urlunsplit((parsed.scheme.casefold(), parsed.netloc.casefold(), parsed.path.rstrip("/") or "/", "", ""))
def _required_string(value: Any, name: str) -> str:
    result = str(value or "").strip()
    if not result: raise ValueError(f"{name} cannot be empty")
    return result
def _clean_string(value: str | None) -> str | None:
    result = re.sub(r"\s+", " ", value or "").strip()
    return result or None
def _positive_float(value: Any, name: str) -> float:
    if isinstance(value, bool): raise ValueError(f"{name} must be a number")
    try: result = float(value)
    except (TypeError, ValueError) as exc: raise ValueError(f"{name} must be a number") from exc
    if result <= 0: raise ValueError(f"{name} must be greater than zero")
    return result
