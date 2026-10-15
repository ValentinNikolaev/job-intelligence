"""Bounded intake of employer posts from HN's monthly hiring threads."""
from __future__ import annotations

import json
import re
import ssl
import sys
from collections import Counter
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urlencode
from urllib.request import HTTPSHandler, Request, build_opener

import certifi
import yaml

from .html_to_markdown import html_to_markdown
from .models import NormalizedJob
from .remote_feeds import MAX_RESPONSE_BYTES, ROLE_PATTERN, exclusion_reason, timestamp


API = "https://hn.algolia.com/api/v1/search_by_date"
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August",
          "September", "October", "November", "December")


def normalize_comment(row: Mapping[str, Any], story_id: str) -> NormalizedJob:
    identity = str(row.get("objectID") or "")
    if not identity.isdecimal() or str(row.get("parent_id")) != story_id:
        raise ValueError("not a top-level employer post")
    if row.get("deleted") or row.get("dead"):
        raise ValueError("deleted employer post")
    raw = row.get("comment_text")
    if not isinstance(raw, str) or not raw.strip():
        raise ValueError("empty employer post")
    raw = raw.strip()
    description = html_to_markdown(raw)
    header = re.split(r"<p\b[^>]*>|<br\s*/?>|\n", raw, maxsplit=1, flags=re.I)[0]
    header = html_to_markdown(header)
    parts = [part.strip() for part in header.split("|")]
    if len(parts) < 2 or not re.search(r"\bremote\b", header, re.I):
        raise ValueError("no explicit remote hiring header")
    if re.search(r"\b(?:no|not|non)[ -]+remote\b", header, re.I):
        raise ValueError("non-remote hiring header")
    titles = [part for part in parts[1:] if ROLE_PATTERN.search(part)]
    if not titles:
        raise ValueError("no relevant engineering title in hiring header")
    company = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", parts[0])
    company = re.sub(r"\s*\(https?://[^)]+\)", "", company).strip()
    if not company:
        raise ValueError("missing employer name")
    source_url = f"https://news.ycombinator.com/item?id={identity}"
    return NormalizedJob(
        source="hackernews", source_job_id=identity, source_url=source_url,
        title=" | ".join(titles), company=company, description=description,
        location=header, remote=True, published_at=timestamp(row.get("created_at")),
        source_metadata={
            "source_name": "Hacker News Who is hiring?", "attribution_url": source_url,
            "thread_url": f"https://news.ycombinator.com/item?id={story_id}",
            "original_header": header, "original_publication_value": row.get("created_at"),
            "hiring_status": "employer_post_not_independently_confirmed",
        },
    )


class HackerNewsCollector:
    name = "hackernews"

    def __init__(self, config: Mapping[str, str], default_path: Path, *,
                 opener: Callable[..., Any] | None = None,
                 clock: Callable[[], datetime] | None = None) -> None:
        path = Path(config.get("HACKERNEWS_CONFIG", "") or default_path)
        settings = yaml.safe_load(path.read_text(encoding="utf-8"))
        allowed = {"version", "enabled", "pilot_until", "timeout_seconds", "max_pages_per_thread"}
        if not isinstance(settings, dict) or set(settings) - allowed or settings.get("version") != 1:
            raise ValueError("invalid Hacker News configuration")
        self.enabled = settings.get("enabled", True)
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be boolean")
        self.pilot_until = date.fromisoformat(str(settings["pilot_until"]))
        self.timeout = self._limit(settings.get("timeout_seconds", 15), 1, 30)
        self.max_pages = self._limit(settings.get("max_pages_per_thread", 3), 1, 3)
        self._opener = opener or build_opener(HTTPSHandler(
            context=ssl.create_default_context(cafile=certifi.where()))).open
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self.api_requests = self.errors = 0
        self.filtered: Counter[str] = Counter()

    @staticmethod
    def _limit(value: object, low: int, high: int) -> int:
        if isinstance(value, bool) or not isinstance(value, int) or not low <= value <= high:
            raise ValueError(f"request setting must be an integer from {low} to {high}")
        return value

    def _request(self, **params: object) -> dict[str, Any]:
        self.api_requests += 1
        request = Request(API + "?" + urlencode(params), headers={
            "User-Agent": "job-intelligence/0.1", "Accept": "application/json"})
        with self._opener(request, timeout=self.timeout) as response:
            body = response.read(MAX_RESPONSE_BYTES + 1)
        if len(body) > MAX_RESPONSE_BYTES:
            raise ValueError("HN response exceeded 3 MB")
        payload = json.loads(body)
        if not isinstance(payload, dict) or not isinstance(payload.get("hits"), list):
            raise ValueError("HN search response has no hits list")
        return payload

    def fetch(self) -> Iterable[NormalizedJob]:
        self.api_requests = self.errors = 0
        self.filtered.clear()
        now = self._clock().astimezone(timezone.utc)
        if not self.enabled or now.date() > self.pilot_until:
            self.filtered["disabled" if not self.enabled else "pilot_expired"] += 1
            return
        cutoff = now - timedelta(days=7)
        first_month = cutoff.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        titles = {f"Ask HN: Who is hiring? ({MONTHS[value.month - 1]} {value.year})"
                  for value in (cutoff, now)}
        discovery = self._request(tags="story,author_whoishiring", query="Ask HN: Who is hiring?",
                                  restrictSearchableAttributes="title", hitsPerPage=10,
                                  numericFilters=f"created_at_i>={int(first_month.timestamp())}")
        threads = {}
        for row in discovery["hits"]:
            if (isinstance(row, dict) and row.get("author") == "whoishiring"
                    and row.get("title") in titles and str(row.get("objectID", "")).isdecimal()):
                threads[str(row["objectID"])] = row
        if not threads:
            raise ValueError("no current official HN hiring thread found")
        seen: set[str] = set()
        try:
            for story_id in sorted(threads, key=int, reverse=True):
                for page in range(self.max_pages):
                    payload = self._request(tags=f"comment,story_{story_id}", hitsPerPage=100, page=page,
                                            numericFilters=f"created_at_i>={int(cutoff.timestamp())},created_at_i<={int((now + timedelta(minutes=5)).timestamp())}")
                    for row in payload["hits"]:
                        try:
                            if not isinstance(row, dict):
                                raise ValueError("invalid comment")
                            job = normalize_comment(row, story_id)
                        except ValueError:
                            self.filtered["not_employer_remote_role"] += 1
                            continue
                        if job.source_job_id in seen:
                            self.filtered["duplicate_id"] += 1
                            continue
                        seen.add(job.source_job_id)
                        reason = exclusion_reason(job, now)
                        if reason or len(job.description) < 200:
                            self.filtered[reason or "incomplete_description"] += 1
                            continue
                        yield job
                    pages = payload.get("nbPages")
                    if not isinstance(pages, int) or isinstance(pages, bool) or pages < 0:
                        raise ValueError("invalid HN page count")
                    if page + 1 >= pages:
                        break
                    if page + 1 == self.max_pages:
                        self.filtered["page_budget"] += pages - self.max_pages
        finally:
            print(json.dumps({"event": "hackernews.filtered", "counts": dict(self.filtered),
                              "requests": self.api_requests}), file=sys.stderr)
