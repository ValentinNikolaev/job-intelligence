from __future__ import annotations

import hashlib
import json
import re
import sys
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen

import yaml

from jobintel.html_to_markdown import html_to_markdown
from jobintel.models import NormalizedJob


DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
USER_AGENT = "job-intelligence/0.1"


@dataclass(frozen=True, slots=True)
class SeedJob:
    title: str
    url: str


@dataclass(frozen=True, slots=True)
class CustomSource:
    name: str
    company: str
    board_url: str
    company_url: str | None = None
    source_type: str | None = None
    ats: str | None = None
    remote: bool | None = None
    location: str | None = None
    notes: str | None = None
    title_terms: tuple[str, ...] = ()
    exclude_title_terms: tuple[str, ...] = ()
    seed_jobs: tuple[SeedJob, ...] = ()


@dataclass(frozen=True, slots=True)
class CustomSettings:
    sources: tuple[CustomSource, ...]
    timeout_seconds: float
    analysis_priority: int


@dataclass(frozen=True, slots=True)
class PageData:
    title: str | None = None
    description: str = ""
    anchors: tuple[tuple[str, str], ...] = ()
    json_ld_jobs: tuple[dict[str, Any], ...] = ()
    canonical_url: str | None = None


class _PageParser(HTMLParser):
    def __init__(self, base_url: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.parts: list[str] = []
        self.anchors: list[tuple[str, str]] = []
        self.json_ld_jobs: list[dict[str, Any]] = []
        self.current_anchor_href: str | None = None
        self.current_anchor_parts: list[str] = []
        self.in_title = False
        self.title_parts: list[str] = []
        self.capture_script = False
        self.script_parts: list[str] = []
        self.skip_depth = 0
        self.canonical_url: str | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attrs_map = {name.casefold(): value for name, value in attrs}
        if tag in {"style", "noscript", "svg"}:
            self.skip_depth += 1
            return
        if tag == "script":
            script_type = (attrs_map.get("type") or "").casefold()
            if script_type == "application/ld+json":
                self.capture_script = True
                self.script_parts = []
            else:
                self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = True
        elif tag == "link" and (attrs_map.get("rel") or "").casefold() == "canonical":
            href = _clean_string(attrs_map.get("href"))
            if href:
                self.canonical_url = urljoin(self.base_url, href)
        elif tag == "a":
            href = _clean_string(attrs_map.get("href"))
            self.current_anchor_href = urljoin(self.base_url, href) if href else None
            self.current_anchor_parts = []
        if tag in {"p", "div", "section", "article", "main", "br", "hr", "li"}:
            self.parts.append("\n")
        elif tag in {"h1", "h2", "h3"}:
            self.parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"style", "noscript", "svg"}:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if tag == "script":
            if self.capture_script:
                _collect_json_ld_jobs("".join(self.script_parts), self.json_ld_jobs)
                self.capture_script = False
                self.script_parts = []
            else:
                self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag == "title":
            self.in_title = False
        elif tag == "a" and self.current_anchor_href:
            label = _clean_string(" ".join(self.current_anchor_parts))
            if label:
                self.anchors.append((label, self.current_anchor_href))
            self.current_anchor_href = None
            self.current_anchor_parts = []
        elif tag in {"p", "div", "section", "article", "main", "li"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if self.capture_script:
            self.script_parts.append(data)
            return
        if self.skip_depth:
            return
        if self.in_title:
            self.title_parts.append(data)
        if self.current_anchor_href:
            self.current_anchor_parts.append(data)
        self.parts.append(data)

    def page_data(self) -> PageData:
        return PageData(
            title=_clean_string(" ".join(self.title_parts)),
            description=html_to_markdown("\n".join(self.parts)),
            anchors=tuple(self.anchors),
            json_ld_jobs=tuple(self.json_ld_jobs),
            canonical_url=self.canonical_url,
        )


class CustomCollector:
    name = "custom"

    def __init__(
        self,
        config: Mapping[str, str],
        *,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        config_path = Path(config.get("CUSTOM_CONFIG", "") or DEFAULT_CONFIG_PATH)
        self.settings = _load_settings(config_path)
        self.timeout = self.settings.timeout_seconds
        self._opener = opener
        self.errors = 0
        self._request_count = 0

    @property
    def api_requests(self) -> int:
        return self._request_count

    def fetch(self) -> Iterable[NormalizedJob]:
        self.errors = 0
        self._request_count = 0
        seen: set[str] = set()
        for source in self.settings.sources:
            try:
                page = self._fetch_page(source.board_url)
                jobs = parse_source_page(source, page, self.settings.analysis_priority)
                for seed in source.seed_jobs:
                    seed_page = page if _canonicalize_url(seed.url) == _canonicalize_url(source.board_url) else self._fetch_page(seed.url)
                    jobs.append(normalize_seed_job(source, seed, seed_page, self.settings.analysis_priority))
                for label, url in page.anchors:
                    if not _looks_like_job_link(source, label, url):
                        continue
                    detail = self._fetch_page(url)
                    jobs.append(normalize_linked_job(source, label, url, detail, self.settings.analysis_priority))
            except Exception as exc:
                self.errors += 1
                print(f"custom: source {source.name!r} failed: {exc}", file=sys.stderr)
                continue
            for job in jobs:
                if job.source_job_id in seen:
                    continue
                seen.add(job.source_job_id)
                yield job

    def _fetch_page(self, url: str) -> PageData:
        request = Request(url, headers={"Accept": "text/html,application/xhtml+xml", "User-Agent": USER_AGENT})
        try:
            self._request_count += 1
            with self._opener(request, timeout=self.timeout) as response:
                html = response.read().decode(_response_charset(response) or "utf-8", errors="replace")
        except HTTPError as exc:
            raise RuntimeError(f"{url} returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise RuntimeError(f"{url} request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise RuntimeError(f"{url} timed out") from exc
        parser = _PageParser(url)
        parser.feed(html)
        return parser.page_data()


def parse_source_page(source: CustomSource, page: PageData, analysis_priority: int) -> list[NormalizedJob]:
    jobs: list[NormalizedJob] = []
    for payload in page.json_ld_jobs:
        title = _clean_string(payload.get("title"))
        if not title or not _title_allowed(source, title):
            continue
        source_url = _job_url(payload) or page.canonical_url or source.board_url
        description = html_to_markdown(_clean_string(payload.get("description"))) or page.description
        jobs.append(
            NormalizedJob(
                source="custom",
                source_job_id=_job_identity(source_url),
                source_url=source_url,
                title=title,
                company=_json_ld_company(payload) or source.company,
                company_url=source.company_url,
                description=description,
                location=_json_ld_location(payload) or source.location,
                remote=source.remote,
                employment_type=_clean_string(payload.get("employmentType")),
                published_at=_clean_string(payload.get("datePosted")),
                source_metadata=_metadata(source),
                analysis_priority=analysis_priority,
            )
        )
    return jobs


def normalize_seed_job(
    source: CustomSource,
    seed: SeedJob,
    page: PageData,
    analysis_priority: int,
) -> NormalizedJob:
    title = seed.title.strip()
    description = page.description or f"{title} at {source.company}."
    return NormalizedJob(
        source="custom",
        source_job_id=_job_identity(seed.url),
        source_url=seed.url,
        title=title,
        company=source.company,
        company_url=source.company_url,
        description=description,
        location=source.location,
        remote=source.remote,
        source_metadata=_metadata(source),
        analysis_priority=analysis_priority,
    )


def normalize_linked_job(
    source: CustomSource,
    label: str,
    url: str,
    page: PageData,
    analysis_priority: int,
) -> NormalizedJob:
    title = _best_title(label, page.title)
    description = page.description or f"{title} at {source.company}."
    return NormalizedJob(
        source="custom",
        source_job_id=_job_identity(url),
        source_url=url,
        title=title,
        company=source.company,
        company_url=source.company_url,
        description=description,
        location=source.location,
        remote=source.remote,
        source_metadata=_metadata(source),
        analysis_priority=analysis_priority,
    )


def create_collector(config: Mapping[str, str]) -> CustomCollector:
    return CustomCollector(config)


def _load_settings(path: Path) -> CustomSettings:
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ValueError(f"cannot read custom source config {path}: {exc}") from exc
    except yaml.YAMLError as exc:
        raise ValueError(f"invalid custom source YAML config {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise ValueError(f"custom source config must be a YAML mapping: {path}")
    allowed = {
        "version",
        "timeout_seconds",
        "analysis_priority",
        "default_title_terms",
        "default_exclude_title_terms",
        "sources",
    }
    unknown = sorted(set(loaded) - allowed)
    if unknown:
        raise ValueError(f"unknown custom source config fields: {', '.join(unknown)}")
    if loaded.get("version", 1) != 1:
        raise ValueError("unsupported custom source config version")
    default_terms = tuple(_string_list(loaded.get("default_title_terms")))
    default_excludes = tuple(_string_list(loaded.get("default_exclude_title_terms")))
    sources = tuple(_load_source(item, default_terms, default_excludes) for item in _mapping_list(loaded.get("sources"), "sources"))
    if not sources:
        raise ValueError("custom source registry is empty; edit sources/custom/config.yaml")
    return CustomSettings(
        sources=sources,
        timeout_seconds=_positive_float(loaded.get("timeout_seconds", 30), "timeout_seconds"),
        analysis_priority=_priority(loaded.get("analysis_priority", 100)),
    )


def _load_source(
    payload: Mapping[str, Any],
    default_terms: tuple[str, ...],
    default_excludes: tuple[str, ...],
) -> CustomSource:
    allowed = {
        "name",
        "company",
        "board_url",
        "company_url",
        "source_type",
        "ats",
        "remote",
        "location",
        "notes",
        "title_terms",
        "exclude_title_terms",
        "seed_jobs",
    }
    unknown = sorted(set(payload) - allowed)
    if unknown:
        raise ValueError(f"unknown custom source fields for {payload.get('name')!r}: {', '.join(unknown)}")
    name = _required_string(payload.get("name"), "source name")
    company = _required_string(payload.get("company"), f"{name} company")
    board_url = _required_url(payload.get("board_url"), f"{name} board_url")
    terms = tuple(_string_list(payload.get("title_terms"))) or default_terms
    excludes = default_excludes + tuple(_string_list(payload.get("exclude_title_terms")))
    seeds = tuple(
        SeedJob(
            title=_required_string(item.get("title"), f"{name} seed job title"),
            url=_required_url(item.get("url"), f"{name} seed job url"),
        )
        for item in _mapping_list(payload.get("seed_jobs", []), f"{name} seed_jobs")
    )
    remote = payload.get("remote")
    if remote is not None and not isinstance(remote, bool):
        raise ValueError(f"{name} remote must be true, false, or null")
    return CustomSource(
        name=name,
        company=company,
        board_url=board_url,
        company_url=_optional_url(payload.get("company_url"), f"{name} company_url"),
        source_type=_clean_string(payload.get("source_type")),
        ats=_clean_string(payload.get("ats")),
        remote=remote,
        location=_clean_string(payload.get("location")),
        notes=_clean_string(payload.get("notes")),
        title_terms=terms,
        exclude_title_terms=excludes,
        seed_jobs=seeds,
    )


def _collect_json_ld_jobs(raw: str, jobs: list[dict[str, Any]]) -> None:
    try:
        loaded = json.loads(raw)
    except json.JSONDecodeError:
        return
    for item in _json_ld_items(loaded):
        item_type = item.get("@type")
        types = item_type if isinstance(item_type, list) else [item_type]
        if any(str(value).casefold() == "jobposting" for value in types):
            jobs.append(item)


def _json_ld_items(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        graph = value.get("@graph")
        if isinstance(graph, list):
            for item in graph:
                yield from _json_ld_items(item)
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _json_ld_items(item)


def _looks_like_job_link(source: CustomSource, label: str, url: str) -> bool:
    if not _same_site(source.board_url, url):
        return False
    searchable = f"{label} {url}".casefold()
    if any(term.casefold() in searchable for term in source.exclude_title_terms):
        return False
    return any(term.casefold() in searchable for term in source.title_terms)


def _title_allowed(source: CustomSource, title: str) -> bool:
    searchable = title.casefold()
    if any(term.casefold() in searchable for term in source.exclude_title_terms):
        return False
    return any(term.casefold() in searchable for term in source.title_terms)


def _best_title(label: str, page_title: str | None) -> str:
    label = re.sub(r"\s+", " ", label).strip(" -|")
    if label:
        return label
    if page_title:
        return re.sub(r"\s+", " ", page_title).strip(" -|")
    return "Open role"


def _metadata(source: CustomSource) -> dict[str, Any]:
    metadata: dict[str, Any] = {"source_name": source.name, "board_url": source.board_url}
    for key, value in (
        ("source_type", source.source_type),
        ("ats", source.ats),
        ("remote_policy_note", source.notes),
    ):
        if value:
            metadata[key] = value
    return metadata


def _job_url(payload: Mapping[str, Any]) -> str | None:
    for key in ("url", "sameAs"):
        value = _clean_string(payload.get(key))
        if value:
            return value
    identifier = payload.get("identifier")
    if isinstance(identifier, Mapping):
        return _clean_string(identifier.get("url"))
    return None


def _json_ld_company(payload: Mapping[str, Any]) -> str | None:
    organization = payload.get("hiringOrganization")
    if isinstance(organization, Mapping):
        return _clean_string(organization.get("name"))
    return None


def _json_ld_location(payload: Mapping[str, Any]) -> str | None:
    value = payload.get("jobLocation")
    locations = value if isinstance(value, list) else [value]
    parts: list[str] = []
    for item in locations:
        if isinstance(item, Mapping):
            address = item.get("address")
            if isinstance(address, Mapping):
                locality = _clean_string(address.get("addressLocality"))
                region = _clean_string(address.get("addressRegion"))
                country = _clean_string(address.get("addressCountry"))
                parts.extend(part for part in (locality, region, country) if part)
    return ", ".join(dict.fromkeys(parts)) or None


def _job_identity(url: str) -> str:
    digest = hashlib.sha256(_canonicalize_url(url).encode("utf-8")).hexdigest()
    return f"url-sha256:{digest}"


def _canonicalize_url(url: str) -> str:
    parsed = urlsplit(url)
    return urlunsplit(
        (
            parsed.scheme.casefold(),
            parsed.netloc.casefold(),
            parsed.path.rstrip("/") or "/",
            parsed.query,
            "",
        )
    )


def _same_site(base_url: str, candidate_url: str) -> bool:
    base = urlsplit(base_url)
    candidate = urlsplit(candidate_url)
    return candidate.scheme in {"http", "https"} and candidate.netloc.casefold() == base.netloc.casefold()


def _response_charset(response: Any) -> str | None:
    headers = getattr(response, "headers", None)
    if headers is not None:
        get_content_charset = getattr(headers, "get_content_charset", None)
        if callable(get_content_charset):
            return get_content_charset()
    return None


def _mapping_list(value: Any, name: str) -> list[Mapping[str, Any]]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError(f"{name} must be a list")
    if not all(isinstance(item, Mapping) for item in value):
        raise ValueError(f"{name} entries must be mappings")
    return value


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list):
        raise ValueError("expected a list of strings")
    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _required_string(value: Any, name: str) -> str:
    result = _clean_string(value)
    if not result:
        raise ValueError(f"{name} is required")
    return result


def _clean_string(value: Any) -> str | None:
    if not isinstance(value, str):
        return None
    result = re.sub(r"\s+", " ", value).strip()
    return result or None


def _required_url(value: Any, name: str) -> str:
    result = _optional_url(value, name)
    if not result:
        raise ValueError(f"{name} is required")
    return result


def _optional_url(value: Any, name: str) -> str | None:
    result = _clean_string(value)
    if not result:
        return None
    parsed = urlsplit(result)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError(f"{name} must be an absolute HTTP(S) URL")
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
