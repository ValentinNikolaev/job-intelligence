from __future__ import annotations

import html
import re
import ssl
import time
from dataclasses import dataclass, replace
from datetime import datetime
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qs, parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import certifi
import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
JOB_PATH = re.compile(r"^/jobs/(\d+)-[^/]+/?$")
DATE = re.compile(r"\b(\d{2}\.\d{2}\.\d{4})\b")
VOID_TAGS = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


@dataclass(frozen=True, slots=True)
class Query:
    index: int
    name: str
    url: str
    category: str

    def discovery(self) -> dict[str, Any]:
        return {"query_index": self.index, "name": self.name, "url": self.url, "category": self.category}


class DjinniCollector:
    name = "djinni"

    def __init__(self, config: Mapping[str, str], *, opener: Callable[..., Any] = urlopen,
                 sleep: Callable[[float], None] = time.sleep) -> None:
        path = Path(config.get("DJINNI_CONFIG", "") or DEFAULT_CONFIG_PATH)
        settings = _load_settings(path)
        self.timeout = _positive_float(settings.get("timeout_seconds", 12), "timeout_seconds")
        self.max_pages = _positive_int(settings.get("max_pages_per_query", 5), "max_pages_per_query")
        self.priority = _priority(settings.get("analysis_priority", 100))
        self.queries = _parse_queries(settings.get("queries"))
        self._opener = opener
        self._sleep = sleep
        self._context = ssl.create_default_context(cafile=certifi.where())
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self._request_count = 0
        if not self.queries:
            raise ValueError("Djinni queries are empty; edit sources/djinni/config.yaml")
        jobs_by_id: dict[str, NormalizedJob] = {}
        for query in self.queries:
            for page in range(1, self.max_pages + 1):
                page_url = _page_url(query.url, page)
                document = self._fetch_html(page_url)
                parser = _ListingParser()
                parser.feed(document)
                if page == 1 and not parser.cards:
                    raise RuntimeError(f"Djinni query {query.name} returned no job cards")
                for job_id, card_html in parser.cards:
                    job = parse_card(job_id, card_html, query, self.priority)
                    if job is None:
                        continue
                    existing = jobs_by_id.get(job_id)
                    if existing is None:
                        jobs_by_id[job_id] = job
                    else:
                        discoveries = list(existing.source_metadata["discovered_by"])
                        discovery = query.discovery()
                        if discovery not in discoveries:
                            discoveries.append(discovery)
                            jobs_by_id[job_id] = replace(
                                existing, source_metadata={**existing.source_metadata, "discovered_by": discoveries}
                            )
                if page + 1 not in parser.pages:
                    break
        yield from jobs_by_id.values()

    def _fetch_html(self, url: str) -> str:
        _validate_search_url(url)
        request = Request(url, headers={"Accept": "text/html", "User-Agent": "job-intelligence/0.1"})
        for attempt in range(3):
            self._request_count += 1
            try:
                with self._opener(request, timeout=self.timeout, context=self._context) as response:
                    charset = response.headers.get_content_charset() or "utf-8"
                    return response.read().decode(charset, errors="replace")
            except HTTPError as exc:
                if exc.code != 429 and exc.code < 500:
                    raise RuntimeError(f"Djinni search returned HTTP {exc.code}: {url}") from exc
                if attempt == 2:
                    raise RuntimeError(f"Djinni search returned HTTP {exc.code} after retries: {url}") from exc
            except (TimeoutError, URLError) as exc:
                if attempt == 2:
                    raise RuntimeError(f"Djinni search failed after retries: {url}: {exc}") from exc
            self._sleep(2 ** attempt)
        raise AssertionError("unreachable")


def parse_card(job_id: str, markup: str, query: Query, priority: int) -> NormalizedJob | None:
    parser = _CardParser()
    parser.feed(markup)
    if not parser.remote or not parser.url or not parser.title or not parser.company:
        return None
    parsed_url = urlsplit(parser.url)
    match = JOB_PATH.fullmatch(parsed_url.path)
    if parsed_url.scheme != "https" or parsed_url.netloc != "djinni.co" or not match or match.group(1) != job_id:
        return None
    date = None
    if parser.date:
        try:
            date = datetime.strptime(parser.date, "%d.%m.%Y").date().isoformat()
        except ValueError:
            pass
    return NormalizedJob(
        source="djinni", source_job_id=job_id, source_url=parser.url,
        title=parser.title, company=parser.company,
        description=html_to_markdown(parser.description or parser.summary),
        location=parser.location, remote=True, published_at=date,
        source_metadata={"category": query.category, "discovered_by": [query.discovery()]},
        analysis_priority=priority,
    )


def create_collector(config: Mapping[str, str]) -> DjinniCollector:
    return DjinniCollector(config)


class _ListingParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.cards: list[tuple[str, str]] = []
        self.pages: set[int] = set()
        self._card_id: str | None = None
        self._depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if self._card_id is None:
            match = re.fullmatch(r"job-item-(\d+)", attributes.get("id") or "")
            if tag == "div" and match and "job-item" in _classes(attributes):
                self._card_id = match.group(1)
                self._depth = 1
                self._parts = [self.get_starttag_text()]
            elif tag == "a" and "page-link" in _classes(attributes):
                href = html.unescape(attributes.get("href") or "")
                page = parse_qs(urlsplit(href).query).get("page", [])
                if page and page[0].isdigit():
                    self.pages.add(int(page[0]))
            return
        self._parts.append(self.get_starttag_text())
        if tag not in VOID_TAGS:
            self._depth += 1

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._card_id is not None:
            self._parts.append(self.get_starttag_text())

    def handle_endtag(self, tag: str) -> None:
        if self._card_id is None:
            return
        self._parts.append(f"</{tag}>")
        if tag not in VOID_TAGS:
            self._depth -= 1
        if self._depth == 0:
            self.cards.append((self._card_id, "".join(self._parts)))
            self._card_id = None
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._card_id is not None:
            self._parts.append(html.escape(data))


class _CardParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.url: str | None = None
        self.title: str | None = None
        self.company: str | None = None
        self.location: str | None = None
        self.description = ""
        self.summary = ""
        self.remote = False
        self.date: str | None = None
        self._capture: str | None = None
        self._depth = 0
        self._parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = _classes(attributes)
        if self._capture:
            self._parts.append(self.get_starttag_text())
            if tag not in VOID_TAGS:
                self._depth += 1
            return
        if tag == "a" and "job_item__header-link" in classes:
            href = attributes.get("href") or ""
            if JOB_PATH.fullmatch(urlsplit(href).path):
                self.url = f"https://djinni.co{href}" if href.startswith("/") else href
        if not self.date and tag == "span":
            match = DATE.search(attributes.get("title") or "")
            if match:
                self.date = match.group(1)
        field = None
        if tag == "h2" and "job-item__position" in classes:
            field = "title"
        elif tag == "span" and {"small", "text-gray-800"} <= classes:
            field = "company"
        elif tag == "span" and "location-text" in classes:
            field = "location"
        elif tag == "span" and "text-nowrap" in classes:
            field = "remote_label"
        elif tag == "span" and "js-original-text" in classes:
            field = "description"
        elif tag == "span" and "js-truncated-text" in classes:
            field = "summary"
        if field:
            self._capture = field
            self._depth = 1
            self._parts = []

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if self._capture:
            self._parts.append(self.get_starttag_text())

    def handle_endtag(self, tag: str) -> None:
        if not self._capture:
            return
        if self._depth > 1:
            self._parts.append(f"</{tag}>")
        self._depth -= 1
        if self._depth == 0:
            value = "".join(self._parts).strip()
            if self._capture == "remote_label":
                self.remote |= html.unescape(value).strip().casefold() == "full remote"
            elif self._capture in {"description", "summary"}:
                setattr(self, self._capture, value)
            else:
                setattr(self, self._capture, html_to_markdown(value).strip())
            self._capture = None
            self._parts = []

    def handle_data(self, data: str) -> None:
        if self._capture:
            self._parts.append(html.escape(data))


def _load_settings(path: Path) -> dict[str, Any]:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read Djinni config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid Djinni YAML config {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError("Djinni config must be a YAML mapping")
    unknown = sorted(set(loaded) - {"version", "timeout_seconds", "max_pages_per_query", "analysis_priority", "queries"})
    if unknown:
        raise ValueError(f"unknown Djinni config fields: {', '.join(unknown)}")
    if loaded.get("version") != 1:
        raise ValueError("unsupported Djinni config version")
    return loaded


def _parse_queries(value: Any) -> list[Query]:
    if not isinstance(value, list):
        raise ValueError("Djinni queries must be a YAML list")
    queries = []
    names: set[str] = set()
    urls: set[str] = set()
    for index, raw in enumerate(value, 1):
        if not isinstance(raw, dict) or set(raw) != {"name", "url", "category"}:
            raise ValueError(f"Djinni query {index} needs name, url, and category")
        name = _required_string(raw["name"], f"queries[{index}].name")
        url = _required_string(raw["url"], f"queries[{index}].url")
        category = _required_string(raw["category"], f"queries[{index}].category")
        _validate_search_url(url)
        if parse_qs(urlsplit(url).query)["primary_keyword"] != [category]:
            raise ValueError(f"Djinni query {index} category must match its URL")
        if name.casefold() in names or url in urls:
            raise ValueError(f"duplicate Djinni query: {name}")
        names.add(name.casefold())
        urls.add(url)
        queries.append(Query(index, name, url, category))
    return queries


def _validate_search_url(url: str) -> None:
    parsed = urlsplit(url)
    parameters = parse_qs(parsed.query)
    if (parsed.scheme != "https" or parsed.netloc != "djinni.co" or parsed.path != "/jobs/"
            or parsed.fragment or parameters.get("employment") != ["remote"]
            or len(parameters.get("primary_keyword", [])) != 1
            or set(parameters) - {"primary_keyword", "employment", "page"}):
        raise ValueError(f"Djinni URL must be an official remote category search: {url}")
    if "page" in parameters and (len(parameters["page"]) != 1 or not parameters["page"][0].isdigit()):
        raise ValueError(f"invalid Djinni page URL: {url}")


def _page_url(url: str, page: int) -> str:
    if page == 1:
        return url
    parsed = urlsplit(url)
    parameters = [(key, value) for key, value in parse_qsl(parsed.query) if key != "page"]
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(parameters + [("page", page)]), ""))


def _classes(attrs: Mapping[str, str | None]) -> set[str]:
    return set((attrs.get("class") or "").split())


def _required_string(value: Any, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def _positive_float(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a positive number")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a positive number") from exc
    if result <= 0:
        raise ValueError(f"{name} must be a positive number")
    return result


def _positive_int(value: Any, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise ValueError(f"{name} must be a positive integer")
    return value


def _priority(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or not 0 <= value <= 100:
        raise ValueError("analysis_priority must be an integer from 0 to 100")
    return value
