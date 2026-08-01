from __future__ import annotations

import hashlib
import re
import time
from dataclasses import dataclass, replace
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
DOU_HOST = "jobs.dou.ua"
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


@dataclass(frozen=True, slots=True)
class DouQuery:
    index: int
    name: str
    url: str
    category: str | None = None

    def discovery_metadata(self) -> dict[str, Any]:
        metadata: dict[str, Any] = {"query_index": self.index, "name": self.name, "url": self.url}
        if self.category:
            metadata["category"] = self.category
        return metadata


@dataclass(frozen=True, slots=True)
class DouListingJob:
    source_url: str
    title: str
    company: str
    company_url: str | None
    location: str | None
    summary: str
    date_label: str | None
    salary: str | None


@dataclass(frozen=True, slots=True)
class DouDetail:
    description: str
    published_at: str | None = None
    company_description: str | None = None


class DouCollector:
    name = "dou"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
        sleep: Callable[[float], None] = time.sleep,
    ) -> None:
        config_path = Path(config.get("DOU_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(config_path)
        self.timeout = _positive_float(settings.get("timeout_seconds", 30), "timeout_seconds")
        self.analysis_priority = _priority(settings.get("analysis_priority", 100))
        self.queries = _parse_queries(settings.get("queries"))
        self._opener = opener
        self._sleep = sleep
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        if not self.queries:
            raise ValueError("DOU queries are empty; edit sources/dou/config.yaml")

        jobs_by_id: dict[str, NormalizedJob] = {}
        for query in self.queries:
            listing_html = self._fetch_html(query.url, f"DOU query {query.index}")
            listing_jobs = parse_listing_page(listing_html, query)
            discovery = query.discovery_metadata()
            for listing in listing_jobs:
                detail = self._detail_or_fallback(listing)
                job = normalize_job(
                    listing,
                    detail,
                    analysis_priority=self.analysis_priority,
                    discovered_by=[discovery],
                )
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

    def _detail_or_fallback(self, listing: DouListingJob) -> DouDetail:
        try:
            html = self._fetch_html(listing.source_url, f"DOU vacancy {listing.source_url}")
        except RuntimeError:
            return DouDetail(description=listing.summary)
        detail = parse_detail_page(html)
        if detail.description:
            return detail
        return DouDetail(description=listing.summary, published_at=detail.published_at)

    def _fetch_html(self, url: str, context: str) -> str:
        _validate_dou_url(url)
        request = Request(
            url,
            headers={"Accept": "text/html", "User-Agent": "job-intelligence/0.1"},
        )
        for attempt in range(3):
            self._request_count += 1
            try:
                with self._opener(request, timeout=self.timeout) as response:
                    charset = response.headers.get_content_charset() or "utf-8"
                    return response.read().decode(charset, errors="replace")
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


def parse_listing_page(html: str, query: DouQuery) -> list[DouListingJob]:
    parser = _ListingParser()
    parser.feed(html)
    jobs: list[DouListingJob] = []
    for job in parser.jobs:
        if not job.title or not job.company or not job.source_url:
            continue
        jobs.append(job)
    return jobs


def parse_detail_page(html: str) -> DouDetail:
    parser = _DetailParser()
    parser.feed(html)
    return DouDetail(
        description=html_to_markdown(parser.description_html),
        published_at=_published_at(parser.date_text),
        company_description=html_to_markdown(parser.company_description_html) or None,
    )


def normalize_job(
    listing: DouListingJob,
    detail: DouDetail,
    *,
    analysis_priority: int,
    discovered_by: list[dict[str, Any]],
) -> NormalizedJob:
    metadata: dict[str, Any] = {"discovered_by": discovered_by}
    if listing.date_label:
        metadata["listing_date_label"] = listing.date_label
    if listing.salary:
        metadata["salary_label"] = listing.salary
    if listing.summary:
        metadata["listing_summary"] = listing.summary

    return NormalizedJob(
        source="dou",
        source_job_id=_job_identity(listing.source_url),
        source_url=listing.source_url,
        title=listing.title,
        company=listing.company,
        company_url=listing.company_url,
        description=detail.description or listing.summary,
        location=listing.location,
        remote=True if _mentions_remote(listing.location) else None,
        published_at=detail.published_at,
        company_description=detail.company_description,
        source_metadata=metadata,
        analysis_priority=analysis_priority,
    )


def create_collector(config: Mapping[str, str]) -> DouCollector:
    return DouCollector(config)


class _ListingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.jobs: list[DouListingJob] = []
        self._in_job = False
        self._job_depth = 0
        self._capture: str | None = None
        self._capture_depth = 0
        self._parts: list[str] = []
        self._html_capture: str | None = None
        self._html_depth = 0
        self._html_parts: list[str] = []
        self._current: dict[str, str | None] = {}

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = dict(attrs)
        classes = _classes(attrs_map)
        if tag == "li" and "l-vacancy" in classes:
            self._in_job = True
            self._job_depth = 1
            self._current = {}
            return
        if not self._in_job:
            return
        if tag not in VOID_TAGS:
            self._job_depth += 1

        if tag == "a" and "vt" in classes:
            self._current["source_url"] = _absolute_url(attrs_map.get("href"))
            self._start_text_capture("title")
        elif tag == "a" and "company" in classes:
            self._current["company_url"] = _absolute_url(attrs_map.get("href"))
            self._start_text_capture("company")
        elif tag == "span" and "cities" in classes:
            self._start_text_capture("location")
        elif tag == "span" and "salary" in classes:
            self._start_text_capture("salary")
        elif tag == "div" and "date" in classes:
            self._start_text_capture("date_label")
        elif tag == "div" and "sh-info" in classes:
            self._start_html_capture("summary")
            self._append_html_start(tag, attrs)
        elif self._html_capture:
            self._append_html_start(tag, attrs)

    def handle_endtag(self, tag: str) -> None:
        if not self._in_job:
            return
        if self._html_capture:
            self._append_html_end(tag)
            if tag not in VOID_TAGS:
                self._html_depth -= 1
            if self._html_depth <= 0:
                self._finish_html_capture()
        if self._capture:
            self._capture_depth -= 1
            if self._capture_depth <= 0:
                self._finish_text_capture()
        self._job_depth -= 1
        if self._job_depth <= 0:
            self._finish_job()

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)
        if self._html_capture:
            self._html_parts.append(data)

    def handle_entityref(self, name: str) -> None:
        value = f"&{name};"
        if self._capture:
            self._parts.append(value)
        if self._html_capture:
            self._html_parts.append(value)

    def handle_charref(self, name: str) -> None:
        value = f"&#{name};"
        if self._capture:
            self._parts.append(value)
        if self._html_capture:
            self._html_parts.append(value)

    def _start_text_capture(self, field: str) -> None:
        if not self._capture:
            self._capture = field
            self._capture_depth = 1
            self._parts = []

    def _finish_text_capture(self) -> None:
        if self._capture:
            self._current[self._capture] = _clean_text("".join(self._parts))
        self._capture = None
        self._parts = []

    def _start_html_capture(self, field: str) -> None:
        if not self._html_capture:
            self._html_capture = field
            self._html_depth = 1
            self._html_parts = []

    def _finish_html_capture(self) -> None:
        if self._html_capture:
            self._current[self._html_capture] = html_to_markdown("".join(self._html_parts))
        self._html_capture = None
        self._html_parts = []

    def _finish_job(self) -> None:
        self.jobs.append(
            DouListingJob(
                source_url=str(self._current.get("source_url") or ""),
                title=str(self._current.get("title") or ""),
                company=str(self._current.get("company") or ""),
                company_url=self._current.get("company_url"),
                location=self._current.get("location"),
                summary=str(self._current.get("summary") or ""),
                date_label=self._current.get("date_label"),
                salary=self._current.get("salary"),
            )
        )
        self._in_job = False
        self._job_depth = 0
        self._current = {}

    def _append_html_start(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_text = "".join(
            f' {name}="{value}"' for name, value in attrs if value is not None and name == "href"
        )
        self._html_parts.append(f"<{tag}{attrs_text}>")

    def _append_html_end(self, tag: str) -> None:
        self._html_parts.append(f"</{tag}>")


class _DetailParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.description_html = ""
        self.company_description_html = ""
        self.date_text: str | None = None
        self._capture: str | None = None
        self._depth = 0
        self._parts: list[str] = []
        self._date_depth = 0
        self._date_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        classes = _classes(dict(attrs))
        if not self._capture and tag == "div" and "b-typo" in classes and "vacancy-section" in classes:
            self._start_capture("description")
        elif not self._capture and tag == "div" and "l-t" in classes:
            self._start_capture("company_description")
        elif not self._capture and tag == "div" and "date" in classes:
            self._date_depth = 1
            self._date_parts = []
            return

        if self._capture:
            if tag not in VOID_TAGS:
                self._depth += 1
            self._append_start(tag, attrs)
        elif self._date_depth:
            if tag not in VOID_TAGS:
                self._date_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if self._capture:
            self._append_end(tag)
            if tag not in VOID_TAGS:
                self._depth -= 1
            if self._depth <= 0:
                text = "".join(self._parts)
                if self._capture == "description":
                    self.description_html = text
                elif self._capture == "company_description":
                    self.company_description_html = text
                self._capture = None
                self._parts = []
        elif self._date_depth:
            self._date_depth -= 1
            if self._date_depth <= 0 and self.date_text is None:
                self.date_text = _clean_text("".join(self._date_parts))

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(data)
        elif self._date_depth:
            self._date_parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if self._capture:
            self._parts.append(f"&{name};")
        elif self._date_depth:
            self._date_parts.append(f"&{name};")

    def handle_charref(self, name: str) -> None:
        if self._capture:
            self._parts.append(f"&#{name};")
        elif self._date_depth:
            self._date_parts.append(f"&#{name};")

    def _start_capture(self, name: str) -> None:
        self._capture = name
        self._depth = 0
        self._parts = []

    def _append_start(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_text = "".join(
            f' {name}="{value}"' for name, value in attrs if value is not None and name == "href"
        )
        self._parts.append(f"<{tag}{attrs_text}>")

    def _append_end(self, tag: str) -> None:
        self._parts.append(f"</{tag}>")


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read DOU config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid DOU YAML config {path}: {exc}") from exc
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise ValueError(f"DOU config must be a YAML mapping: {path}")
    allowed = {"version", "timeout_seconds", "analysis_priority", "queries"}
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown DOU config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported DOU config version")
    return loaded


def _parse_queries(value: Any) -> list[DouQuery]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("DOU queries must be a YAML list")
    queries: list[DouQuery] = []
    for index, raw_query in enumerate(value, 1):
        if not isinstance(raw_query, dict):
            raise ValueError(f"DOU query {index} must be a mapping")
        allowed = {"name", "url", "category"}
        unknown = sorted(set(raw_query) - allowed)
        if unknown:
            raise ValueError(f"unknown fields in DOU query {index}: {', '.join(unknown)}")
        name = _required_string(raw_query.get("name"), f"queries[{index}].name")
        url = _required_string(raw_query.get("url"), f"queries[{index}].url")
        _validate_dou_url(url)
        queries.append(
            DouQuery(
                index=index,
                name=name,
                url=url,
                category=_as_string(raw_query.get("category")),
            )
        )
    return queries


def _validate_dou_url(url: str) -> None:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.netloc.casefold() != DOU_HOST:
        raise ValueError(f"DOU URL must be on https://{DOU_HOST}: {url}")


def _absolute_url(value: str | None) -> str | None:
    if not value:
        return None
    if value.startswith("//"):
        return f"https:{value}"
    if value.startswith("/"):
        return f"https://{DOU_HOST}{value}"
    return value.strip()


def _job_identity(url: str) -> str:
    match = re.search(r"/vacancies/(\d+)/?", url)
    if match:
        return match.group(1)
    digest = hashlib.sha256(url.encode("utf-8")).hexdigest()
    return f"url-sha256:{digest}"


def _published_at(value: str | None) -> str | None:
    if not value:
        return None
    match = re.search(r"(\d{1,2})\s+([^\s]+)\s+(\d{4})", value.casefold())
    if not match:
        return value
    day = int(match.group(1))
    month = {
        "січня": 1,
        "лютого": 2,
        "березня": 3,
        "квітня": 4,
        "травня": 5,
        "червня": 6,
        "липня": 7,
        "серпня": 8,
        "вересня": 9,
        "жовтня": 10,
        "листопада": 11,
        "грудня": 12,
    }.get(match.group(2))
    if month is None:
        return value
    return f"{int(match.group(3)):04d}-{month:02d}-{day:02d}"


def _mentions_remote(value: str | None) -> bool:
    return bool(value and "віддалено" in value.casefold())


def _classes(attrs: Mapping[str, str | None]) -> set[str]:
    value = attrs.get("class")
    return set(value.split()) if value else set()


def _clean_text(value: str) -> str:
    return re.sub(r"\s+", " ", value.replace("\xa0", " ")).strip()


def _priority(value: Any) -> int:
    if isinstance(value, bool):
        raise ValueError("analysis_priority must be an integer from 0 to 100")
    try:
        result = int(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("analysis_priority must be an integer from 0 to 100") from exc
    if not 0 <= result <= 100:
        raise ValueError("analysis_priority must be an integer from 0 to 100")
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
