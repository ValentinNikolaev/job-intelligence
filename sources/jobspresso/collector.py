from __future__ import annotations

import hashlib
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


FEED_URL = "https://jobspresso.co/jobs/feed/"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
USER_AGENT = "job-intelligence/0.1"


class JobspressoCollector:
    name = "jobspresso"

    def __init__(self, config: Mapping[str, str], *, opener: Callable[..., Any] = urlopen,
                 sleep: Callable[[float], None] = time.sleep,
                 now: Callable[[], datetime] | None = None) -> None:
        config_path = Path(config.get("JOBSPRESSO_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        self.max_age_days = _positive_float(settings.get("max_age_days", 7), "max_age_days")
        self.cheap_mode = _boolean(settings.get("cheap_mode", True), "cheap_mode")
        self._opener = opener
        self._sleep = sleep
        self._now = now or (lambda: datetime.now(timezone.utc))
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        request = Request(FEED_URL, headers={
            "Accept": "application/rss+xml, application/xml;q=0.9",
            "User-Agent": USER_AGENT,
        })
        jobs = parse_feed(self._get_bytes(request, "Jobspresso jobs feed"))
        if self.cheap_mode:
            cutoff = self._now().astimezone(timezone.utc) - timedelta(days=self.max_age_days)
            jobs = [job for job in jobs if _is_recent(job.published_at, cutoff) and _is_relevant(job)]
        yield from jobs

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
                if attempt == 2:
                    raise RuntimeError(f"{context} timed out after retries") from exc
            except URLError as exc:
                if attempt == 2:
                    raise RuntimeError(f"{context} request failed: {exc.reason}") from exc
            self._sleep(2**attempt)
        raise AssertionError("unreachable")


def parse_feed(payload: bytes | str) -> list[NormalizedJob]:
    try:
        root = ET.fromstring(payload)
    except (ET.ParseError, ValueError) as exc:
        raise RuntimeError("Jobspresso feed returned invalid XML") from exc
    jobs: list[NormalizedJob] = []
    seen_keys: set[str] = set()
    for index, item in enumerate(_descendants(root, "item"), 1):
        try:
            job = normalize_item(item)
        except ValueError as exc:
            raise ValueError(f"Jobspresso item {index}: {exc}") from exc
        keys = {
            f"id:{job.source_job_id}",
            f"url:{_canonical_url(job.source_url)}",
            f"posting:{_identity_text(job.company)}:{_identity_text(job.title)}",
        }
        if not (keys & seen_keys):
            seen_keys.update(keys)
            jobs.append(job)
    return jobs


def normalize_item(item: ET.Element) -> NormalizedJob:
    title = html_to_markdown(_first_text(item, "title"))
    source_url = _clean_string(_first_text(item, "link"))
    company, location = _creator_parts(_first_text(item, "creator"))
    if not title or not source_url or not company:
        raise ValueError("missing title, link, or dc:creator company")
    description_html = _first_text(item, "encoded") or _first_text(item, "description")
    categories = _all_text(item, "category")
    metadata: dict[str, Any] = {"categories": categories} if categories else {}
    return NormalizedJob(
        source="jobspresso", source_job_id=_source_job_id(item, source_url),
        source_url=source_url, title=title, company=company,
        description=html_to_markdown(description_html), location=location, remote=True,
        published_at=_rss_timestamp(_first_text(item, "pubDate")), source_metadata=metadata,
    )


def create_collector(config: Mapping[str, str]) -> JobspressoCollector:
    return JobspressoCollector(config)


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Jobspresso config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Jobspresso YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Jobspresso config must be a YAML mapping: {path}")
    unknown = sorted(set(loaded) - {"version", "timeout_seconds", "max_age_days", "cheap_mode"})
    if unknown:
        raise ValueError(f"unknown Jobspresso config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported Jobspresso config version")
    return loaded


def _source_job_id(item: ET.Element, source_url: str) -> str:
    post_id = _first_text(item, "post-id", "post_id", "postid")
    if post_id:
        return post_id.strip()
    guid = _clean_string(_first_text(item, "guid"))
    if guid:
        query_id = parse_qs(urlsplit(guid).query).get("p")
        if query_id and query_id[0].strip():
            return query_id[0].strip()
        return guid
    digest = hashlib.sha256(_canonical_url(source_url).encode("utf-8")).hexdigest()
    return f"url-sha256:{digest}"


def _creator_parts(value: str | None) -> tuple[str | None, str | None]:
    if not value:
        return None, None
    separated = re.sub(r"(?i)<br\s*/?>", "\n", unescape(value))
    lines = [html_to_markdown(part).strip() for part in separated.splitlines()]
    lines = [line for line in lines if line]
    if len(lines) > 1:
        lines[1] = re.sub(r"^[⚲📍]+\s*", "", lines[1]).strip()
    return (lines[0] if lines else None, lines[1] if len(lines) > 1 else None)


def _rss_timestamp(value: str | None) -> str | None:
    if not value:
        return None
    try:
        parsed = parsedate_to_datetime(value)
    except (TypeError, ValueError, OverflowError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _descendants(root: ET.Element, name: str) -> Iterable[ET.Element]:
    return (element for element in root.iter() if _local_name(element.tag) == name)


def _first_text(element: ET.Element, *names: str) -> str | None:
    expected = {name.casefold() for name in names}
    for child in element.iter():
        if child is not element and _local_name(child.tag).casefold() in expected:
            value = "".join(child.itertext()).strip()
            if value:
                return value
    return None


def _all_text(element: ET.Element, name: str) -> list[str]:
    values: list[str] = []
    for child in element.iter():
        if _local_name(child.tag).casefold() == name.casefold():
            value = "".join(child.itertext()).strip()
            if value and value not in values:
                values.append(value)
    return values


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _canonical_url(value: str) -> str:
    parsed = urlsplit(value)
    return urlunsplit((parsed.scheme.casefold(), parsed.netloc.casefold(),
                       parsed.path.rstrip("/") or "/", "", ""))


def _clean_string(value: str | None) -> str | None:
    result = re.sub(r"\s+", " ", value or "").strip()
    return result or None


def _is_recent(published_at: str | None, cutoff: datetime) -> bool:
    if not published_at:
        return False
    try:
        published = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    except ValueError:
        return False
    return published >= cutoff


def _is_relevant(job: NormalizedJob) -> bool:
    title = job.title.casefold()
    original_body = f"{job.title}\n{job.description}"
    body = original_body.casefold()
    noise = (
        "marketing", "sales", "account manager", "customer success", "recruiter",
        "designer", "copywriter", "content writer", "finance", "human resources",
    )
    if any(term in title for term in noise):
        return False
    stack = re.search(r"(?<![a-z0-9])(?:php|laravel|symfony|golang)(?![a-z0-9])", body)
    if not stack and not re.search(r"(?<![A-Za-z0-9])Go(?![A-Za-z0-9])", original_body):
        return False
    return bool(re.search(r"\b(?:back[ -]?end|software|platform|api|engineer|developer|lead|manager)\b", body))


def _identity_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip()


def _boolean(value: Any, name: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(f"{name} must be a boolean")
    return value


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
