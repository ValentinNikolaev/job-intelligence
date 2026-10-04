from __future__ import annotations

import json
import math
import sys
import time
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


BOARD_URL = "https://www.techyon.it/candidati.html"
DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")


def _official_url(href: str, base_url: str) -> str | None:
    url = urlsplit(urljoin(base_url, href))
    if url.scheme != "https" or url.netloc != "www.techyon.it":
        return None
    return urlunsplit((url.scheme, url.netloc, url.path, url.query, ""))


class _PageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.job_urls: list[str] = []
        self.page_urls: list[str] = []
        self.job_postings: list[dict[str, Any]] = []
        self.has_board = False
        self._script: list[str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        classes = (values.get("class") or "").split()
        if "job-advertisements" in classes:
            self.has_board = True
        if tag == "script" and (values.get("type") or "").lower() == "application/ld+json":
            self._script = []
        if tag != "a":
            return
        url = _official_url(values.get("href") or "", self.base_url)
        if not url:
            return
        parsed = urlsplit(url)
        if "item" in classes and parsed.path.startswith("/candidati/") and parsed.path.endswith(".html"):
            # Query strings do not identify a different posting.
            self.job_urls.append(urlunsplit((parsed.scheme, parsed.netloc, parsed.path, "", "")))
        elif "page-link" in classes and parsed.path == "/candidati.html":
            query = parse_qs(parsed.query)
            page = query.get("page", ["1"])[0]
            if page.isdecimal() and int(page) > 0:
                self.page_urls.append(BOARD_URL if int(page) == 1 else f"{BOARD_URL}?page={int(page)}")

    def handle_data(self, data: str) -> None:
        if self._script is not None:
            self._script.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag != "script" or self._script is None:
            return
        raw = "".join(self._script)
        self._script = None
        try:
            payload = json.loads(raw)
        except ValueError:
            return
        self._collect_postings(payload)

    def _collect_postings(self, payload: Any) -> None:
        if isinstance(payload, list):
            for item in payload:
                self._collect_postings(item)
        elif isinstance(payload, dict):
            types = payload.get("@type", [])
            if types == "JobPosting" or isinstance(types, list) and "JobPosting" in types:
                self.job_postings.append(payload)
            self._collect_postings(payload.get("@graph"))


def _parse_page(html: str, url: str) -> _PageParser:
    parser = _PageParser(url)
    parser.feed(html)
    parser.close()
    return parser


def _text(value: Any) -> str | None:
    return html_to_markdown(value).strip() or None if isinstance(value, str) else None


def _timestamp(value: Any) -> str | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        try:
            parsed = parsedate_to_datetime(value)
        except (TypeError, ValueError, OverflowError):
            return None
    # Keep a source date without inventing an unavailable timezone.
    if parsed.tzinfo is None:
        return parsed.isoformat()
    return parsed.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def normalize_detail(html: str, url: str) -> NormalizedJob:
    canonical = _official_url(url, BOARD_URL)
    if not canonical or not urlsplit(canonical).path.startswith("/candidati/"):
        raise ValueError("Techyon detail URL must be an official vacancy URL")
    postings = _parse_page(html, canonical).job_postings
    if len(postings) != 1:
        raise ValueError("Techyon detail must contain exactly one structured JobPosting")
    payload = postings[0]
    title, description = _text(payload.get("title")), _text(payload.get("description"))
    if not title or not description:
        raise ValueError("Techyon JobPosting is missing title or full description")
    organization = payload.get("hiringOrganization") or {}
    if not isinstance(organization, dict):
        raise ValueError("Techyon hiringOrganization must be an object")
    locations = payload.get("jobLocation") or []
    if isinstance(locations, dict):
        locations = [locations]
    if not isinstance(locations, list):
        raise ValueError("Techyon jobLocation must be an object or list")
    location_parts: list[str] = []
    for place in locations:
        address = place.get("address", {}) if isinstance(place, dict) else {}
        if not isinstance(address, dict):
            continue
        parts = [_text(address.get(field)) for field in ("addressLocality", "addressRegion", "addressCountry")]
        location = ", ".join(dict.fromkeys(part for part in parts if part))
        if location and location not in location_parts:
            location_parts.append(location)
    path = urlsplit(canonical).path
    canonical = f"https://www.techyon.it{path}"
    job = NormalizedJob(
        source="techyon", source_job_id=path.removeprefix("/candidati/").removesuffix(".html"),
        source_url=canonical, title=title, description=description,
        company=_text(organization.get("name")) or "Techyon",
        company_url=_text(organization.get("sameAs")),
        location="; ".join(location_parts) or None,
        remote=True if payload.get("jobLocationType") == "TELECOMMUTE" else None,
        employment_type=_text(payload.get("employmentType")),
        published_at=_timestamp(payload.get("datePosted")),
        source_metadata={"source_type": "headhunter", "recruiter": "Techyon",
                         "board_url": BOARD_URL, "valid_through": _timestamp(payload.get("validThrough"))},
    )
    job.validate()
    return job


class TechyonCollector:
    name = "techyon"

    def __init__(self, config: Mapping[str, str], *, opener: Callable[..., Any] = urlopen,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        path = Path(config.get("TECHYON_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = yaml.safe_load(path.read_text(encoding="utf-8"))
        if not isinstance(settings, dict):
            raise ValueError("Techyon config must be a YAML mapping")
        unknown = set(settings) - {"version", "timeout_seconds", "max_pages"}
        if unknown or settings.get("version", 1) != 1:
            raise ValueError("unsupported Techyon config fields or version")
        timeout = settings.get("timeout_seconds", 12)
        pages = settings.get("max_pages", 10)
        if isinstance(timeout, bool) or not isinstance(timeout, (int, float)) or not math.isfinite(timeout) or timeout <= 0:
            raise ValueError("Techyon timeout_seconds must be a finite positive number")
        if isinstance(pages, bool) or not isinstance(pages, int) or not 1 <= pages <= 100:
            raise ValueError("Techyon max_pages must be an integer from 1 to 100")
        self.timeout, self.max_pages = float(timeout), pages
        self._opener, self._sleep = opener, sleep
        self._request_count = 0
        self.errors = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def _get_html(self, url: str) -> str:
        request = Request(url, headers={"Accept": "text/html", "User-Agent": "job-intelligence/0.1"})
        for attempt in range(3):
            self._request_count += 1
            try:
                with self._opener(request, timeout=self.timeout) as response:
                    return response.read().decode("utf-8")
            except HTTPError as exc:
                if exc.code != 429 and exc.code < 500 or attempt == 2:
                    raise RuntimeError(f"Techyon {url} returned HTTP {exc.code}") from exc
            except (URLError, TimeoutError) as exc:
                if attempt == 2:
                    raise RuntimeError(f"Techyon {url} request failed: {exc}") from exc
            self._sleep(2**attempt)
        raise AssertionError("unreachable")

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = self.errors = 0
        pending = [BOARD_URL]
        seen_pages: set[str] = set()
        seen_jobs: set[str] = set()
        while pending and len(seen_pages) < self.max_pages:
            url = pending.pop(0)
            if url in seen_pages:
                continue
            seen_pages.add(url)
            try:
                page = _parse_page(self._get_html(url), url)
                if not page.has_board:
                    raise ValueError("Techyon response is missing the vacancy board")
            except (RuntimeError, ValueError) as exc:
                if url == BOARD_URL:
                    raise
                self._failure(url, exc)
                continue
            for next_url in page.page_urls:
                if next_url not in seen_pages and next_url not in pending:
                    pending.append(next_url)
            for detail_url in page.job_urls:
                if detail_url in seen_jobs:
                    continue
                seen_jobs.add(detail_url)
                try:
                    yield normalize_detail(self._get_html(detail_url), detail_url)
                except (RuntimeError, ValueError) as exc:
                    self._failure(detail_url, exc)

    def _failure(self, url: str, exc: Exception) -> None:
        self.errors += 1
        print(json.dumps({"event": "techyon.page.failed", "url": url, "error": str(exc)}),
              file=sys.stderr, flush=True)


def create_collector(config: Mapping[str, str]) -> TechyonCollector:
    return TechyonCollector(config)
