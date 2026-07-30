from __future__ import annotations

import re
import os
import uuid
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

from .models import NormalizedJob
from .normalization import normalize_company, slug
from .registry import _dump_yaml, _render_job_markdown, _utc_iso


MAX_JOB_AGE_DAYS = 7


@dataclass(frozen=True, slots=True)
class Rejection:
    category: str
    reason: str


@dataclass(frozen=True, slots=True)
class CompanyRetryRule:
    company: str
    allow_after: date
    reason: str
    aliases: tuple[str, ...] = ()

    def matches(self, company: str) -> bool:
        candidates = (self.company, *self.aliases)
        normalized = normalize_company(company)
        return any(normalize_company(candidate) == normalized for candidate in candidates)


def prefilter_job(
    job: NormalizedJob,
    *,
    now: datetime | None = None,
    max_age_days: int = MAX_JOB_AGE_DAYS,
    company_retry_rules: tuple[CompanyRetryRule, ...] = (),
) -> Rejection | None:
    now = now or datetime.now(timezone.utc)
    if now.tzinfo is None:
        now = now.replace(tzinfo=timezone.utc)
    now = now.astimezone(timezone.utc)

    retry_rejection = _company_retry_rejection(job.company, company_retry_rules, now.date())
    if retry_rejection is not None:
        return retry_rejection

    published_at = _parse_timestamp(job.published_at)
    if published_at is not None and published_at < now - timedelta(days=max_age_days):
        return Rejection(
            "stale",
            f"published_at {job.published_at} is older than {max_age_days} days",
        )

    title_text = _normalize_text(job.title)
    if _is_obvious_role_mismatch(title_text):
        return Rejection("role_mismatch", "title is an obvious mismatch for a backend profile")

    full_text = _normalize_text(
        "\n".join(
            part
            for part in (
                job.title,
                job.description,
                job.location or "",
                job.employment_type or "",
            )
            if part
        )
    )
    if _has_english_requirement(full_text):
        return None
    blocking_language = _hard_blocking_language_requirement(full_text)
    if blocking_language is not None:
        return Rejection(
            "language_requirement",
            f"hard {blocking_language} language requirement without English green light",
        )
    if _has_hard_language_requirement(full_text, "italian"):
        return Rejection("language_requirement", "hard Italian language requirement without English green light")
    blacklisted_stack = _blacklisted_stack(full_text)
    if blacklisted_stack is not None:
        return Rejection("tech_stack", f"{blacklisted_stack} is not a target stack")
    if not _has_target_stack(full_text):
        return Rejection("tech_stack", "role does not mention Go/Golang or PHP")
    return None


def load_company_retry_rules(profile_path: Path) -> tuple[CompanyRetryRule, ...]:
    if not profile_path.exists():
        return ()
    try:
        loaded = yaml.safe_load(profile_path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise ValueError(f"cannot read company retry policy {profile_path}: {exc}") from exc
    if not isinstance(loaded, dict):
        return ()
    raw_rules = loaded.get("company_retry_after", [])
    if raw_rules is None:
        return ()
    if not isinstance(raw_rules, list):
        raise ValueError("company_retry_after must be a list")
    rules: list[CompanyRetryRule] = []
    for index, raw in enumerate(raw_rules, start=1):
        if not isinstance(raw, dict):
            raise ValueError(f"company_retry_after[{index}] must be a mapping")
        company = str(raw.get("company") or "").strip()
        raw_date = raw.get("allow_after")
        if not company or raw_date in (None, ""):
            raise ValueError(f"company_retry_after[{index}] needs company and allow_after")
        if isinstance(raw_date, date):
            allow_after = raw_date
        else:
            try:
                allow_after = date.fromisoformat(str(raw_date).strip())
            except ValueError as exc:
                raise ValueError(
                    f"company_retry_after[{index}].allow_after must be YYYY-MM-DD"
                ) from exc
        raw_aliases = raw.get("aliases") or ()
        if not isinstance(raw_aliases, list):
            raise ValueError(f"company_retry_after[{index}].aliases must be a list")
        reason = str(raw.get("reason") or "CV rejected; retry is temporarily blocked.").strip()
        rules.append(
            CompanyRetryRule(
                company=company,
                allow_after=allow_after,
                reason=reason,
                aliases=tuple(str(alias).strip() for alias in raw_aliases if str(alias).strip()),
            )
        )
    return tuple(rules)


def _company_retry_rejection(
    company: str,
    rules: tuple[CompanyRetryRule, ...],
    today: date,
) -> Rejection | None:
    for rule in rules:
        if rule.matches(company) and today < rule.allow_after:
            return Rejection(
                "company_retry_block",
                f"{rule.company} is blocked until {rule.allow_after.isoformat()}: {rule.reason}",
            )
    return None


class RejectedRegistry:
    def __init__(self, registry_root: Path) -> None:
        self.root = registry_root / "rejected"
        self.root.mkdir(parents=True, exist_ok=True)

    def upsert(self, job: NormalizedJob, rejection: Rejection) -> None:
        source = job.source.strip().lower()
        source_job_id = job.source_job_id.strip()
        existing = self._find(source, source_job_id)
        now = _utc_iso(datetime.now(timezone.utc))
        meta = {
            "schema_version": 1,
            "source": source,
            "source_job_id": source_job_id,
            "source_url": job.source_url.strip(),
            "title": job.title.strip(),
            "company": job.company.strip(),
            "location": (job.location or "").strip() or None,
            "published_at": (job.published_at or "").strip() or None,
            "rejection_category": rejection.category,
            "rejection_reason": rejection.reason,
            "updated_at": now,
        }
        if existing is None:
            meta["rejected_at"] = now
            directory = self.root / f"{_timestamp_slug(now)}_{source}_{slug(job.company)}_{slug(job.title)}"
            if directory.exists():
                directory = self.root / f"{directory.name}_{uuid.uuid4().hex[:8]}"
        else:
            directory, previous = existing
            meta["rejected_at"] = previous.get("rejected_at", now)

        directory.mkdir(parents=True, exist_ok=True)
        _write_text_if_changed(directory / "meta.yaml", _dump_yaml(meta))
        _write_text_if_changed(directory / "job.md", _render_rejected_markdown(job, rejection))

    def _find(self, source: str, source_job_id: str) -> tuple[Path, dict[str, Any]] | None:
        for meta_path in sorted(self.root.glob("*/meta.yaml")):
            try:
                loaded = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError):
                continue
            if not isinstance(loaded, dict):
                continue
            if loaded.get("source") == source and str(loaded.get("source_job_id")) == source_job_id:
                return meta_path.parent, loaded
        return None


def _is_obvious_role_mismatch(title_text: str) -> bool:
    patterns = (
        r"\bqa\b",
        r"\bquality assurance\b",
        r"\btest automation\b",
        r"\bautomation tester\b",
        r"\bandroid\b",
        r"\bios\b",
        r"\bmobile engineer\b",
        r"\bmobile developer\b",
    )
    return any(re.search(pattern, title_text) for pattern in patterns)


def _has_english_requirement(text: str) -> bool:
    return bool(
        re.search(
            r"\b(english|inglese|anglais|englisch)\b.{0,80}\b(required|mandatory|fluent|professional|b2|c1|c2|native|excellent|good)\b",
            text,
        )
        or re.search(
            r"\b(required|mandatory|fluent|professional|b2|c1|c2|native|excellent|good)\b.{0,80}\b(english|inglese|anglais|englisch)\b",
            text,
        )
    )


def _has_hard_language_requirement(text: str, language: str) -> bool:
    aliases = {
        "albanian": r"albanian|shqip",
        "bulgarian": r"bulgarian|български|bulgaro",
        "croatian": r"croatian|hrvatski|croato",
        "czech": r"czech|čeština|czech language|ceco",
        "danish": r"danish|dansk|danese",
        "dutch": r"dutch|nederlands|olandese",
        "estonian": r"estonian|eesti|estone",
        "finnish": r"finnish|suomi|finlandese",
        "german": r"german|deutsch|tedesco|allemand",
        "greek": r"greek|ελληνικά|greco",
        "hungarian": r"hungarian|magyar|ungherese",
        "french": r"french|français|francais|francese",
        "italian": r"italian|italiano|italien|italienne",
        "latvian": r"latvian|latviešu|lettone",
        "lithuanian": r"lithuanian|lietuvių|lituano",
        "norwegian": r"norwegian|norsk|norvegese",
        "polish": r"polish|polski|polacco",
        "portuguese": r"portuguese|português|portoghese",
        "romanian": r"romanian|română|rumeno",
        "serbian": r"serbian|srpski|serbo",
        "slovak": r"slovak|slovenčina|slovacco",
        "slovenian": r"slovenian|slovenščina|sloveno",
        "spanish": r"spanish|español|espanol|spagnolo",
        "swedish": r"swedish|svenska|svedese",
        "turkish": r"turkish|türkçe|turco",
    }[language]
    hard = r"required|mandatory|must|fluent|native|excellent|professional|mother tongue|b2|c1|c2"
    return bool(
        re.search(rf"\b({aliases})\b.{{0,80}}\b({hard})\b", text)
        or re.search(rf"\b({hard})\b.{{0,80}}\b({aliases})\b", text)
        or (language == "german" and re.search(r"\bdeutschkenntnisse\b", text))
        or (language == "italian" and re.search(r"\bmadrelingua italiana\b", text))
    )


def _hard_blocking_language_requirement(text: str) -> str | None:
    languages = (
        "albanian",
        "bulgarian",
        "croatian",
        "czech",
        "danish",
        "dutch",
        "estonian",
        "finnish",
        "french",
        "german",
        "greek",
        "hungarian",
        "latvian",
        "lithuanian",
        "norwegian",
        "polish",
        "portuguese",
        "romanian",
        "serbian",
        "slovak",
        "slovenian",
        "spanish",
        "swedish",
        "turkish",
    )
    for language in languages:
        if _has_hard_language_requirement(text, language):
            return language.title()
    return None


def _blacklisted_stack(text: str) -> str | None:
    if re.search(r"\bspring boot\b", text):
        return "Spring Boot"
    if _has_python_stack(text) and _has_r_stack(text):
        return "Python + R"
    if _has_python_stack(text) and re.search(r"\bjulia\b", text):
        return "Python + Julia"
    return None


def _has_target_stack(text: str) -> bool:
    return bool(_has_go_stack(text) or _has_php_stack(text))


def _has_go_stack(text: str) -> bool:
    return bool(
        re.search(r"\b(golang|go-lang|go language)\b", text)
        or re.search(r"\bgo\b.{0,40}\b(backend|service|services|api|apis|microservice|microservices|developer|engineer|platform)\b", text)
        or re.search(r"\b(backend|service|services|api|apis|microservice|microservices|developer|engineer|platform)\b.{0,40}\bgo\b", text)
    )


def _has_php_stack(text: str) -> bool:
    return bool(re.search(r"\bphp\s*(?:5|7|8)(?:\.\d+)?\b|\bphp(?:5|7|8)(?:\.\d+)?\b|\bphp\b", text))


def _has_python_stack(text: str) -> bool:
    return bool(re.search(r"\bpython\b", text))


def _has_r_stack(text: str) -> bool:
    return bool(re.search(r"\br\b|\br language\b|\br-lang\b", text))


def _parse_timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_text(value: str) -> str:
    return " ".join(value.casefold().split())


def _timestamp_slug(value: str) -> str:
    return value.replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")


def _render_rejected_markdown(job: NormalizedJob, rejection: Rejection) -> str:
    reason = (
        "## Rejection\n\n"
        f"- Category: {rejection.category}\n"
        f"- Reason: {rejection.reason}\n"
    )
    return _render_job_markdown(job.title, reason + "\n" + job.description, job.published_at)


def _write_text_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return True
