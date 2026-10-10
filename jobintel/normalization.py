from __future__ import annotations

import hashlib
import re
import unicodedata
import uuid
from urllib.parse import urlsplit, urlunsplit


_COMPANY_SUFFIXES = {
    "corp",
    "corporation",
    "inc",
    "incorporated",
    "limited",
    "llc",
    "ltd",
}


def normalize_text(value: str | None) -> str:
    text = unicodedata.normalize("NFKC", value or "").casefold()
    text = re.sub(r"[^\w\s]", " ", text, flags=re.UNICODE)
    return " ".join(text.split())


def normalize_company(value: str) -> str:
    words = normalize_text(value).split()
    while words and words[-1] in _COMPANY_SUFFIXES:
        words.pop()
    return " ".join(words)


def canonical_vacancy_url(value: str) -> str:
    parts = urlsplit(value.strip())
    host = (parts.hostname or "").casefold()
    if parts.scheme not in {"http", "https"} or not host:
        return ""
    if host == "job-boards.eu.greenhouse.io":
        host = "job-boards.greenhouse.io"
    path = parts.path.rstrip("/")
    path = re.sub(r"(/o/[^/]+)/c/new$", r"\1", path)
    return urlunsplit(("https", host, path, parts.query, ""))


def vacancy_url_variants(value: str) -> tuple[str, ...]:
    canonical = canonical_vacancy_url(value)
    if not canonical:
        return ()
    variants = {value.strip(), canonical}
    parts = urlsplit(canonical)
    if re.fullmatch(r"/o/[^/]+", parts.path):
        variants.add(canonical + "/c/new")
    if parts.hostname == "job-boards.greenhouse.io":
        variants.add(canonical.replace("job-boards.greenhouse.io", "job-boards.eu.greenhouse.io", 1))
    return tuple(sorted(variants))


def normalize_location(value: str | None) -> str:
    text = normalize_text(value)
    replacements = (
        (r"\bwork from home\b", "remote"),
        (r"\bhome based\b", "remote"),
        (r"\bfully remote\b", "remote"),
    )
    for pattern, replacement in replacements:
        text = re.sub(pattern, replacement, text)
    return " ".join(text.split())


def vacancy_fingerprint(company: str, title: str, location: str | None) -> str:
    identity = "|".join(
        (normalize_company(company), normalize_text(title), normalize_location(location))
    )
    return f"sha256:{hashlib.sha256(identity.encode('utf-8')).hexdigest()}"


def slug(value: str, *, fallback: str = "job", max_length: int = 48) -> str:
    result = normalize_text(value).replace("_", "-").replace(" ", "-")
    result = re.sub(r"-+", "-", result).strip("-")
    return (result or fallback)[:max_length].rstrip("-")


def record_directory_name(discovered_at: str, company: str, record_id: str) -> str:
    """Bound new registry folder names without truncating UUID identity."""
    date_part = discovered_at[:10].replace("-", "")
    company_part = slug(company, fallback="company", max_length=14)
    try:
        identity = uuid.UUID(record_id).hex
    except ValueError:
        identity = hashlib.sha256(record_id.encode("utf-8")).hexdigest()[:32]
    return f"{date_part}_{company_part}_{identity}"

