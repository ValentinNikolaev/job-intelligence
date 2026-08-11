from __future__ import annotations

import json
import re
from collections.abc import Callable, Mapping
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit, urlunsplit
from urllib.request import Request, urlopen

from .html_to_markdown import html_to_markdown
from .models import NormalizedJob


class UrlIntakeError(RuntimeError):
    pass


Opener = Callable[..., Any]
_LEVER_HOSTS = {
    "jobs.lever.co": "api.lever.co",
    "jobs.eu.lever.co": "api.eu.lever.co",
}
_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9_-]+$")


def load_job_url(source_url: str, *, opener: Opener = urlopen, timeout_seconds: float = 20) -> NormalizedJob:
    site, posting_id, jobs_host, api_host, canonical_url = _parse_lever_url(source_url)
    endpoint = (
        f"https://{api_host}/v0/postings/{quote(site, safe='')}/"
        f"{quote(posting_id, safe='')}"
    )
    request = Request(
        endpoint,
        headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
    )
    try:
        with opener(request, timeout=timeout_seconds) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        raise UrlIntakeError(f"Lever returned HTTP {exc.code}") from exc
    except URLError as exc:
        raise UrlIntakeError(f"Lever request failed: {exc.reason}") from exc
    except TimeoutError as exc:
        raise UrlIntakeError("Lever request timed out") from exc
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UrlIntakeError("Lever returned invalid JSON") from exc
    if not isinstance(payload, Mapping):
        raise UrlIntakeError("Lever returned JSON that is not an object")
    return _normalize_lever_job(
        payload,
        site=site,
        posting_id=posting_id,
        jobs_host=jobs_host,
        canonical_url=canonical_url,
        api_endpoint=endpoint,
    )


def _parse_lever_url(source_url: str) -> tuple[str, str, str, str, str]:
    parsed = urlsplit(source_url.strip())
    host = (parsed.hostname or "").casefold()
    if parsed.scheme.casefold() != "https" or host not in _LEVER_HOSTS:
        supported = ", ".join(sorted(_LEVER_HOSTS))
        raise UrlIntakeError(f"unsupported vacancy URL; expected an HTTPS Lever URL on {supported}")
    parts = [part for part in parsed.path.split("/") if part]
    if len(parts) != 2 or not all(_SAFE_SEGMENT.fullmatch(part) for part in parts):
        raise UrlIntakeError("Lever URL must contain exactly a site and posting ID")
    site, posting_id = parts
    canonical_url = urlunsplit(("https", host, f"/{site}/{posting_id}", "", ""))
    return site, posting_id, host, _LEVER_HOSTS[host], canonical_url


def _normalize_lever_job(
    payload: Mapping[str, Any],
    *,
    site: str,
    posting_id: str,
    jobs_host: str,
    canonical_url: str,
    api_endpoint: str,
) -> NormalizedJob:
    payload_id = _as_text(payload.get("id")) or posting_id
    if payload_id != posting_id:
        raise UrlIntakeError("Lever response posting ID does not match the requested URL")
    title = _as_text(payload.get("text"))
    if not title:
        raise UrlIntakeError("Lever job is missing its title")
    description = _lever_description(payload)
    if not description:
        raise UrlIntakeError("Lever job is missing its description")
    categories = payload.get("categories")
    categories = categories if isinstance(categories, Mapping) else {}
    workplace_type = (_as_text(payload.get("workplaceType")) or "").casefold()
    remote = True if workplace_type == "remote" else False if workplace_type in {"on-site", "hybrid"} else None
    company = _as_text(payload.get("company")) or _display_site_name(site)
    apply_url = _as_text(payload.get("applyUrl"))
    metadata: dict[str, Any] = {
        "source_name": "Lever Postings API",
        "lever_site": site,
        "api_endpoint": api_endpoint,
    }
    for key, value in {
        "apply_url": apply_url,
        "team": _as_text(categories.get("team")),
        "department": _as_text(categories.get("department")),
        "workplace_type": workplace_type or None,
        "salary_range": payload.get("salaryRange"),
    }.items():
        if value not in (None, "", [], {}):
            metadata[key] = value
    job = NormalizedJob(
        source="manual",
        source_job_id=payload_id,
        source_url=canonical_url,
        title=title,
        company=company,
        company_url=f"https://{jobs_host}/{quote(site, safe='')}",
        description=description,
        location=_as_text(categories.get("location")),
        remote=remote,
        employment_type=_as_text(categories.get("commitment")),
        source_metadata=metadata,
        analysis_priority=100,
    )
    job.validate()
    return job


def _lever_description(payload: Mapping[str, Any]) -> str:
    base = _as_text(payload.get("descriptionPlain")) or html_to_markdown(
        _as_text(payload.get("description"))
    )
    parts = [base] if base else []
    lists = payload.get("lists")
    if isinstance(lists, list):
        for item in lists:
            if not isinstance(item, Mapping):
                continue
            heading = _as_text(item.get("text"))
            content = html_to_markdown(_as_text(item.get("content")))
            if content:
                parts.append(f"## {heading}\n\n{content}" if heading else content)
    additional = _as_text(payload.get("additionalPlain")) or html_to_markdown(
        _as_text(payload.get("additional"))
    )
    if additional:
        parts.append(additional)
    salary = _as_text(payload.get("salaryDescriptionPlain")) or html_to_markdown(
        _as_text(payload.get("salaryDescription"))
    )
    if salary:
        parts.append(f"## Compensation\n\n{salary}")
    return "\n\n".join(part for part in parts if part).strip()


def _display_site_name(site: str) -> str:
    return " ".join(part.capitalize() for part in re.split(r"[-_]", site) if part)


def _as_text(value: object) -> str | None:
    return value.strip() if isinstance(value, str) and value.strip() else None

