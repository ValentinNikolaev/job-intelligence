from __future__ import annotations

import base64
import gzip
import hashlib
import io
import json
import re
from datetime import datetime, timezone
from email.utils import parseaddr
from html.parser import HTMLParser
from pathlib import Path
from typing import Any, Iterable, Mapping
from urllib.parse import parse_qs, urlsplit

from jobintel.models import NormalizedJob


HOSTS = {"reteinformaticalavoro.it", "www.reteinformaticalavoro.it"}


class _MailHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.links: list[str] = []
        self.hidden = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        if self.hidden:
            return
        if tag == "a" and dict(attrs).get("href"):
            self.links.append(str(dict(attrs)["href"]))
        if tag in {"br", "p", "div", "tr", "td", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        if tag in {"p", "div", "tr", "td", "li", "h1", "h2", "h3", "h4"}:
            self.parts.append("\n")

    def handle_data(self, data: str) -> None:
        if not self.hidden:
            self.parts.append(data)


class JobAlertCollector:
    api_requests = 0

    def __init__(self, config: Mapping[str, str], source: str) -> None:
        self.name = source
        default_input = Path(__file__).resolve().parents[1] / f".codex-work/job-alerts/{source}.json"
        self.input_path = Path(config.get(f"{source.upper()}_INPUT") or default_input)

    def fetch(self) -> Iterable[NormalizedJob]:
        if not self.input_path.exists():
            return
        payload = json.loads(self.input_path.read_text(encoding="utf-8-sig"))
        # Validate the whole batch before yielding anything to the storage pipeline.
        yield from normalize_batch(payload, self.name)


def _text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value.strip()


def _spaces(value: str) -> str:
    return " ".join(value.split())


def _posting(value: str, source: str) -> tuple[str, str]:
    url = urlsplit(value)
    if url.scheme not in {"http", "https"} or url.username or url.password or url.port not in {None, 443}:
        raise ValueError("invalid vacancy URL")
    if source == "indeed":
        if url.hostname == "cts.indeed.com":
            # Decode the embedded destination offline; never follow tracking links.
            match = re.fullmatch(r"/v3/([A-Za-z0-9_-]+)/[A-Za-z0-9_-]+", url.path)
            if not match:
                raise ValueError("unsupported Indeed tracking link")
            token = match[1]
            try:
                compressed = base64.urlsafe_b64decode(token + "=" * (-len(token) % 4))
                with gzip.GzipFile(fileobj=io.BytesIO(compressed)) as stream:
                    decoded = stream.read(65537)
                if len(decoded) > 65536:
                    raise ValueError("Indeed destination payload is too large")
                destination = json.loads(decoded)["u"]
                url = urlsplit(_text(destination, "Indeed destination"))
            except (ValueError, KeyError, OSError, EOFError, TypeError) as exc:
                raise ValueError("unsupported Indeed destination payload") from exc
        if (url.scheme not in {"http", "https"} or url.hostname not in {"indeed.com", "www.indeed.com", "it.indeed.com"}
                or url.username or url.password or url.port not in {None, 443}
                or url.path not in {"/viewjob", "/rc/clk", "/pagead/clk"}):
            raise ValueError("expected an Indeed vacancy URL")
        ids = parse_qs(url.query).get("jk", [])
        if len(ids) != 1 or not re.fullmatch(r"[a-fA-F0-9]{16}", ids[0]):
            raise ValueError("Indeed vacancy requires a stable 16-character jk")
        job_id = ids[0].lower()
        return job_id, f"https://it.indeed.com/viewjob?jk={job_id}"
    if url.hostname not in HOSTS:
        raise ValueError("expected a direct Reteinformaticalavoro vacancy URL")
    match = re.fullmatch(r"/lavoro/([1-9][0-9]*)/([a-zA-Z0-9_-]+)/?", url.path)
    if not match:
        raise ValueError("expected /lavoro/<numeric-id>/<slug>, not a search or account link")
    return match[1], f"https://reteinformaticalavoro.it{url.path.rstrip('/')}"


def _date(value: str) -> str:
    for pattern in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d/%m/%y", "%d-%m-%y"):
        try:
            return datetime.strptime(value, pattern).date().isoformat()
        except ValueError:
            pass
    raise ValueError("published_date must be a date copied from the email")


def normalize_batch(payload: Any, source: str) -> list[NormalizedJob]:
    if source not in {"reteinformaticalavoro", "indeed"}:
        raise ValueError("unsupported Job Alert source")
    if not isinstance(payload, dict) or set(payload) != {"schema_version", "emails"}:
        raise ValueError("expected schema_version and emails")
    if type(payload["schema_version"]) is not int or payload["schema_version"] != 1:
        raise ValueError("unsupported Job Alert schema")
    if not isinstance(payload["emails"], list):
        raise ValueError("emails must be a list")
    jobs_by_id: dict[str, NormalizedJob] = {}
    for index, email in enumerate(payload["emails"], 1):
        try:
            jobs = _normalize_email(email, source)
        except (ValueError, TypeError, KeyError) as exc:
            raise ValueError(f"Job Alert email {index}: {exc}") from exc
        for job in jobs:
            previous = jobs_by_id.get(job.source_job_id)
            # The newest received alert wins when both subscriptions repeat a role.
            if previous is None or job.source_metadata["received_at"] > previous.source_metadata["received_at"]:
                jobs_by_id[job.source_job_id] = job
    return list(jobs_by_id.values())


def _normalize_email(email: Any, source: str) -> list[NormalizedJob]:
    required = {"message_id", "sender", "subject", "received_at", "jobs"}
    if not isinstance(email, dict) or not required <= set(email) or set(email) - required - {"body_html", "body_text"}:
        raise ValueError("invalid email envelope fields")
    message_id = _text(email["message_id"], "message_id")
    sender = parseaddr(_text(email["sender"], "sender"))[1]
    sender_domains = ({"indeed.com", "jobalert.indeed.com", "match.indeed.com"} if source == "indeed"
                      else {"reteinformaticalavoro.it"})
    if sender.lower().rsplit("@", 1)[-1] not in sender_domains or "@" not in sender:
        raise ValueError("unexpected sender domain")
    _text(email["subject"], "subject")
    received = datetime.fromisoformat(_text(email["received_at"], "received_at").replace("Z", "+00:00"))
    if received.tzinfo is None:
        raise ValueError("received_at requires a timezone")
    if ("body_html" in email) == ("body_text" in email):
        raise ValueError("supply exactly one original body_html or body_text")
    if "body_html" in email:
        body = _text(email["body_html"], "body_html")
        parser = _MailHTML()
        parser.feed(body)
        evidence = _spaces("".join(parser.parts))
        links = parser.links
    else:
        body = _text(email["body_text"], "body_text")
        evidence = _spaces(body)
        links = [url.rstrip(".,;)>]") for url in re.findall(r"https?://[^\s<]+", body)]
    posting_ids: set[str] = set()
    for link in links:
        try:
            posting_ids.add(_posting(link, source)[0])
        except ValueError:
            continue
    if not posting_ids:
        raise ValueError("no direct vacancy links; this is not an importable Job Alert")
    if not isinstance(email["jobs"], list):
        raise ValueError("jobs must be a list")
    jobs = []
    for item in email["jobs"]:
        required_job = {"title", "company", "source_url", "description"}
        optional = {"location", "employment_type", "remote_working", "published_date"}
        if not isinstance(item, dict) or not required_job <= set(item) or set(item) - required_job - optional:
            raise ValueError("invalid job fields")
        job_id, source_url = _posting(_text(item["source_url"], "source_url"), source)
        if job_id not in posting_ids:
            raise ValueError("vacancy link is absent from the original email")
        fields = {key: _text(item[key], key) for key in (required_job - {"source_url"}) | (set(item) & optional)}
        for key, value in fields.items():
            if re.search(r"https?://|\b[^\s@]+@[^\s@]+\.[^\s@]+", value, re.I):
                raise ValueError(f"{key} must exclude email addresses and personal links")
            if _spaces(value) not in evidence:
                raise ValueError(f"{key} is not an exact excerpt from the email")
        for key in ("title", "company"):
            if _spaces(fields[key]) not in _spaces(fields["description"]):
                raise ValueError(f"description must include the vacancy's {key}")
        remote_value = fields.get("remote_working")
        if remote_value is not None:
            allowed_remote = ({"Remoto", "Da remoto", "Lavoro da casa", "Ibrido", "In presenza"}
                              if source == "indeed" else {"Totale", "Parziale", "No"})
            if remote_value not in allowed_remote:
                raise ValueError("unsupported remote_working evidence")
            if _spaces(remote_value) not in _spaces(fields["description"]):
                raise ValueError("remote_working is absent from this vacancy excerpt")
            if source != "indeed" and not re.search(r"Remote working\s*:\s*" + re.escape(remote_value) + r"\b", fields["description"], re.I):
                raise ValueError("remote_working needs a label in this vacancy excerpt")
        job = NormalizedJob(
            source=source, source_job_id=job_id, source_url=source_url,
            title=fields["title"], company=fields["company"], description=fields["description"],
            location=fields.get("location"), employment_type=fields.get("employment_type"),
            remote=None if remote_value is None else remote_value not in {"No", "In presenza"},
            published_at=_date(fields["published_date"]) if "published_date" in fields else None,
            source_metadata={"channel": "job_alert_email", "message_id": message_id,
                             "received_at": received.astimezone(timezone.utc).isoformat(), "description_scope": "email_excerpt",
                             "remote_working": remote_value, "email_body_sha256": hashlib.sha256(body.encode()).hexdigest()},
            analysis_priority=100,
        )
        job.validate()
        jobs.append(job)
    return jobs
