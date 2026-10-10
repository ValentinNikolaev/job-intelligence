from __future__ import annotations

import json
import re
import ssl
import sys
from collections import Counter
from dataclasses import replace
from datetime import date, datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlsplit
from urllib.request import HTTPSHandler, Request, build_opener
from xml.etree import ElementTree

import certifi
import yaml

from .html_to_markdown import html_to_markdown
from .models import NormalizedJob


ENDPOINTS = {
    "remotive": "https://remotive.com/api/remote-jobs?category=software-dev&limit=100",
    "remoteok": "https://remoteok.com/api",
    "larajobs": "https://larajobs.com/feed",
}
MAX_RESPONSE_BYTES = 3_000_000
ROLE_PATTERN = re.compile(
    r"\b(?:backend|back.end|software (?:engineer|developer)|platform engineer|"
    r"(?:php|golang|go|laravel|symfony) (?:engineer|developer)|"
    r"product engineer|full[ -]?stack (?:engineer|developer)|"
    r"(?:tech|technical|engineering) lead|staff engineer|principal engineer)\b", re.I
)
ELIGIBLE_LOCATION = re.compile(r"\b(?:italy|italia|europe|european union|eea|eu|emea|worldwide|anywhere|global)\b", re.I)
EXCLUDED_LOCATION = re.compile(r"\b(?:excluding|except) italy\b|\b(?:us|usa|uk|united states|united kingdom|canada|poland|france|spain|germany)[ -]only\b", re.I)


def timestamp(value: object) -> str | None:
    if not value:
        return None
    try:
        text = str(value).strip()
        try:
            result = datetime.fromisoformat(text.replace("Z", "+00:00"))
        except ValueError:
            result = parsedate_to_datetime(text)
        if result.tzinfo is None:
            result = result.replace(tzinfo=timezone.utc)
        return result.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except (TypeError, ValueError, OverflowError):
        return None


def normalize_json_job(source: str, row: Mapping[str, Any]) -> NormalizedJob:
    if source == "remotive":
        fields = ("id", "title", "company_name", "candidate_required_location", "publication_date", "job_type")
    elif source == "remoteok":
        fields = ("id", "position", "company", "location", "date", "employment_type")
    else:
        raise ValueError(f"unsupported JSON feed: {source}")
    identity, title, company, location, published, employment = (row.get(key) for key in fields)
    url = str(row.get("url") or "").strip()
    expected_host = "remotive.com" if source == "remotive" else "remoteok.com"
    if urlsplit(url).scheme != "https" or urlsplit(url).hostname != expected_host:
        raise ValueError(f"{source} job URL is not an official source URL")
    if not all(str(value or "").strip() for value in (identity, title, company)):
        raise ValueError(f"{source} job is missing id, title or company")
    return NormalizedJob(
        source=source, source_job_id=str(identity), source_url=url,
        title=html_to_markdown(str(title)), company=str(company).strip(),
        description=html_to_markdown(str(row.get("description") or "")),
        location=str(location).strip() if location else None, remote=True,
        employment_type=str(employment) if employment else None,
        published_at=timestamp(published),
        source_metadata={"source_name": "Remotive" if source == "remotive" else "Remote OK",
                         "attribution_url": url, "tags": row.get("tags") or [],
                         "salary": row.get("salary"), "original_publication_value": published},
    )


def parse_larajobs_feed(body: bytes) -> list[NormalizedJob]:
    if b"<!DOCTYPE" in body.upper() or b"<!ENTITY" in body.upper():
        raise ValueError("RSS document declarations are not allowed")
    root = ElementTree.fromstring(body)
    if root.tag != "rss" or root.find("channel") is None:
        raise ValueError("LaraJobs response is not an RSS channel")
    jobs = []
    for item in root.findall("./channel/item"):
        def value(name: str) -> str:
            return (item.findtext(name) or "").strip()
        url = value("link")
        if urlsplit(url).hostname != "larajobs.com" or not re.fullmatch(r"/job/\d+", urlsplit(url).path):
            raise ValueError("LaraJobs item has an unexpected job URL")
        company = value("{https://larajobs.com}company") or value("{http://purl.org/dc/elements/1.1/}creator")
        title = value("title")
        if not company or not title:
            raise ValueError("LaraJobs item is missing title or company")
        location = value("{https://larajobs.com}location")
        jobs.append(NormalizedJob(
            source="larajobs", source_job_id=urlsplit(url).path.rsplit("/", 1)[-1],
            source_url=url, title=title, company=company,
            description=html_to_markdown(value("{http://purl.org/rss/1.0/modules/content/}encoded") or value("description")),
            location=location or None,
            remote=True if "remote" in location.casefold() else None,
            employment_type=value("{https://larajobs.com}job_type") or None,
            published_at=timestamp(value("pubDate")),
            source_metadata={"source_name": "LaraJobs", "attribution_url": url,
                             "salary": value("{https://larajobs.com}salary"),
                             "tags": value("{https://larajobs.com}tags"),
                             "original_publication_value": value("pubDate")},
        ))
    return jobs


def exclusion_reason(job: NormalizedJob, now: datetime) -> str | None:
    if not job.published_at:
        return "unknown_publication_date"
    published = datetime.fromisoformat(job.published_at.replace("Z", "+00:00"))
    if published < now - timedelta(days=7):
        return "stale"
    if published > now + timedelta(minutes=5):
        return "future_publication_date"
    if not ROLE_PATTERN.search(job.title) or re.search(r"\b(?:junior|intern|internship|trainer)\b", job.title, re.I):
        return "role_mismatch"
    location = job.location or ""
    if not ELIGIBLE_LOCATION.search(location):
        return "unconfirmed_italy_eligibility"
    if EXCLUDED_LOCATION.search(location + "\n" + job.description):
        return "country_restriction"
    for clause in re.split(r"[\n.;]", job.description):
        if (re.search(r"\bmust (?:be (?:based|located|resident)|reside|live) in\b", clause, re.I)
                and re.search(r"\b(?:poland|france|spain|germany|netherlands|portugal|switzerland|uk|united kingdom|usa|united states|canada)\b", clause, re.I)
                and not ELIGIBLE_LOCATION.search(clause)):
            return "country_restriction"
    return None


class PublicRemoteFeedCollector:
    def __init__(self, source: str, config: Mapping[str, str], default_path: Path,
                 *, opener: Callable[..., Any] | None = None,
                 clock: Callable[[], datetime] | None = None) -> None:
        self.name = source
        path = Path(config.get(source.upper() + "_CONFIG", "") or default_path)
        settings = yaml.safe_load(path.read_text(encoding="utf-8"))
        allowed = {"version", "enabled", "pilot_until", "timeout_seconds", "max_items", "max_detail_requests"}
        if not isinstance(settings, dict) or set(settings) - allowed or settings.get("version") != 1:
            raise ValueError(f"invalid {source} feed configuration")
        self.enabled = settings.get("enabled", True)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be boolean")
        self.pilot_until = date.fromisoformat(str(settings["pilot_until"]))
        self.timeout = self._limit(settings.get("timeout_seconds", 15), 1, 30, "timeout_seconds")
        self.max_items = self._limit(settings.get("max_items", 100), 1, 100, "max_items")
        self.max_detail_requests = self._limit(settings.get("max_detail_requests", 0), 0, 5, "max_detail_requests")
        if source != "larajobs" and self.max_detail_requests:
            raise ValueError("JSON feeds must not make detail requests")
        self._opener = opener or build_opener(HTTPSHandler(context=ssl.create_default_context(cafile=certifi.where()))).open
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.api_requests = 0
        self.errors = 0
        self.filtered: Counter[str] = Counter()

    @staticmethod
    def _limit(value: object, minimum: int, maximum: int, name: str) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
            raise ValueError(f"{name} must be an integer from {minimum} to {maximum}")
        return value

    def _request(self, url: str) -> bytes:
        self.api_requests += 1
        request = Request(url, headers={"User-Agent": "job-intelligence/0.1", "Accept": "application/json, application/rss+xml, text/html"})
        with self._opener(request, timeout=self.timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("feed response exceeded 3 MB")
        return body

    def fetch(self) -> Iterable[NormalizedJob]:
        self.api_requests = self.errors = 0
        self.filtered.clear()
        now = self._clock()
        if not self.enabled or now.date() > self.pilot_until:
            print(json.dumps({"event": "remote_feed.skipped", "source": self.name,
                              "reason": "disabled" if not self.enabled else "pilot_expired"}), file=sys.stderr)
            return
        body = self._request(ENDPOINTS[self.name])
        if self.name == "larajobs":
            jobs = parse_larajobs_feed(body)[:self.max_items]
        else:
            payload = json.loads(body)
            rows = payload.get("jobs") if isinstance(payload, dict) else payload
            if not isinstance(rows, list):
                raise ValueError(f"{self.name} response has no job list")
            jobs = []
            for row in rows[:self.max_items]:
                if isinstance(row, dict) and "legal" in row:
                    continue
                try:
                    if not isinstance(row, dict):
                        raise ValueError("job row is not an object")
                    jobs.append(normalize_json_job(self.name, row))
                except ValueError as exc:
                    self.errors += 1
                    print(f"{self.name}: invalid job: {exc}", file=sys.stderr)
        seen = set()
        detail_requests = 0
        try:
            for job in jobs:
                if job.source_job_id in seen:
                    self.filtered["duplicate_id"] += 1
                    continue
                seen.add(job.source_job_id)
                reason = exclusion_reason(job, now)
                if reason:
                    self.filtered[reason] += 1
                    continue
                if self.name == "larajobs" and len(job.description) < 200:
                    if detail_requests >= self.max_detail_requests:
                        self.filtered["detail_budget"] += 1
                        continue
                    detail_requests += 1
                    try:
                        description = html_to_markdown(self._request(job.source_url).decode("utf-8"))
                        job = replace(job, description=description)
                    except Exception as exc:
                        self.errors += 1
                        print(f"larajobs: detail failed for {job.source_job_id}: {exc}", file=sys.stderr)
                        continue
                if len(job.description) < 200:
                    self.filtered["incomplete_description"] += 1
                    continue
                # Recheck country restrictions after RSS detail enrichment.
                reason = exclusion_reason(job, now)
                if reason:
                    self.filtered[reason] += 1
                    continue
                yield job
        finally:
            print(json.dumps({"event": "remote_feed.filtered", "source": self.name,
                              "counts": dict(self.filtered), "requests": self.api_requests}), file=sys.stderr)
