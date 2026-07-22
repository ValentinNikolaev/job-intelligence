from __future__ import annotations

import hashlib
import re
import unicodedata


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

