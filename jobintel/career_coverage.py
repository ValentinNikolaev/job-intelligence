"""Check employer coverage inside the candidate-approved CV career window."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path

from .preparation_context import PreparationContext, PreparationContextError, resolve_preparation_context


_MONTHS = (
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
)
_MONTH = "|".join(_MONTHS)
_PERIOD = re.compile(
    rf"(?P<start>(?:(?:{_MONTH})\s+)?\d{{4}})\s*[-–—]\s*"
    rf"(?P<end>Present|Current|(?:(?:{_MONTH})\s+)?\d{{4}})",
    re.IGNORECASE,
)
_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_ALLOWED_SECTIONS = {"experience"}


class CareerCoverageError(ValueError):
    pass


def _date_key(value: str) -> tuple[int, int | None]:
    words = value.split()
    if len(words) == 1:
        return int(words[0]), None
    month = next(index for index, name in enumerate(_MONTHS, 1) if name.casefold() == words[0].casefold())
    return int(words[1]), month


def _source_roles(source: str, *, section_name: str = "Experience") -> dict[str, tuple[tuple[int, int | None], tuple[int, int | None] | None]]:
    experience = source.split(f"\n## {section_name}\n", 1)
    if len(experience) != 2:
        raise CareerCoverageError(f"candidate career source has no {section_name} section")
    section = experience[1].split("\n## ", 1)[0]
    roles: dict[str, tuple[tuple[int, int | None], tuple[int, int | None] | None]] = {}
    for chunk in re.split(r"(?=^###\s+)", section, flags=re.MULTILINE):
        match = re.match(r"###\s+([^\n]+)", chunk)
        if not match:
            continue
        employer = match.group(1).strip()
        periods = list(_PERIOD.finditer(chunk))
        if not periods:
            raise CareerCoverageError(f"candidate career source has no dates for {employer}")
        starts = [_date_key(period.group("start")) for period in periods]
        if any(period.group("end").casefold() in {"present", "current"} for period in periods):
            end = None
        else:
            end = max(_date_key(period.group("end")) for period in periods)
        roles[employer] = (min(starts), end)
    if not roles:
        raise CareerCoverageError("candidate career source has no employer entries")
    return roles


def _read_source(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise CareerCoverageError(f"candidate career source unavailable: {path}") from exc


def _context(source_path: Path, context: PreparationContext | None) -> PreparationContext:
    try:
        root = next((parent for parent in source_path.resolve().parents if (parent / "config/application-profile.yaml").is_file()), source_path.resolve().parents[2])
        context = resolve_preparation_context(root, context)
        if source_path.resolve() != context.career_source_path:
            raise PreparationContextError("career source differs from its preparation context")
        return context
    except PreparationContextError as exc:
        raise CareerCoverageError(str(exc)) from exc


def _corrected_roles(source_path: Path, *, context: PreparationContext | None = None) -> dict:
    context = _context(source_path, context)
    aliases = context.employer_aliases
    linked = {}
    for source in context.preparation["career_sources"]:
        roles = _source_roles(_read_source(context.source_path(source["path"])), section_name=source["section"])
        for employer, period in roles.items():
            if not any(employer.casefold() == other.casefold()
                    or employer.casefold() in aliases.get(other.casefold(), ()) for other in linked):
                linked[employer] = period
    from .evidence import EvidenceError, _source
    corrected = set()
    for clarification in context.preparation["career_clarifications"]:
        matches = [name for name in linked if clarification["employer"].casefold() == name.casefold()
                   or clarification["employer"].casefold() in aliases.get(name.casefold(), ())]
        if len(matches) != 1:
            raise CareerCoverageError("career clarification must identify one sourced employer")
        employer = matches[0]
        if employer in corrected:
            raise CareerCoverageError("duplicate career clarification for the same sourced employer")
        corrected.add(employer)
        try:
            quotes = [_source(context.project_root, record, context=context) for record in clarification["sources"]]
        except EvidenceError as exc:
            raise CareerCoverageError(f"career clarification source is invalid: {exc}") from exc
        if not any(alias.casefold() in "\n".join(quotes).casefold() for alias in aliases.get(employer.casefold(), (employer,))):
            raise CareerCoverageError("career clarification sources do not identify the employer")
        period = list(linked[employer])
        for field, correction in clarification["corrections"].items():
            value = correction["value"]
            match = re.fullmatch(r"(?:(?:" + _MONTH + r")\s+)?\d{4}", value, re.IGNORECASE)
            quote = quotes[correction["source"]]
            if match is None or re.search(r"(?<!\w)" + re.escape(value) + r"(?!\w)", quote, re.IGNORECASE) is None:
                raise CareerCoverageError("corrected career date must occur exactly in its bound source quote")
            parsed = _date_key(value)
            if correction["precision"] == "month" and parsed[1] is None:
                raise CareerCoverageError("career correction cannot invent month precision")
            if correction["precision"] == "year" and parsed[1] is not None:
                if "uncertainty_source" not in correction:
                    raise CareerCoverageError("reduced career date precision requires an uncertainty source")
                parsed = (parsed[0], None)
            period[0 if field == "start" else 1] = parsed
        if period[1] is not None and (period[0][0], period[0][1] or 1) > (period[1][0], period[1][1] or 12):
            raise CareerCoverageError("corrected career period ends before it starts")
        linked[employer] = tuple(period)
    return linked


def _cv_entries(markdown: str) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    section = ""
    lines = markdown.splitlines()
    for index, line in enumerate(lines):
        heading = _HEADING.match(line.strip())
        if heading and len(heading.group(1)) == 2:
            section = heading.group(2).casefold()
            continue
        if section not in _ALLOWED_SECTIONS:
            continue
        if heading and len(heading.group(1)) == 3:
            title = heading.group(2)
            following = []
            for next_line in lines[index + 1:index + 5]:
                if _HEADING.match(next_line.strip()):
                    break
                following.append(next_line)
            entries.append((title, "\n".join((title, *following))))
    return entries


def _scoped_roles(roles: dict, source_path: Path, reference_date: date | datetime | None, *, context: PreparationContext | None = None) -> dict:
    context = _context(source_path, context)
    scope = context.preparation["career_scope"]
    first = scope["first_employer"]
    years = scope["maximum_years_since_end"]
    if first is not None:
        if first not in roles or roles[first][0][1] is None:
            raise CareerCoverageError("CV career boundary requires a sourced employer and month")
        start = roles[first][0]
    else:
        start = (1, 1)
    today = reference_date.date() if isinstance(reference_date, datetime) else reference_date or date.today()
    cutoff = (today.year - years, today.month)
    return {employer: period for employer, period in roles.items()
            if (period[0][0], period[0][1] or 1) >= start
            and (period[1] is None or (period[1][0], period[1][1] or 12) > cutoff)}


def validate_career_coverage(markdown: str, source_path: Path, *, reference_date: date | datetime | None = None, context: PreparationContext | None = None) -> None:
    """Require sourced employers in the approved window and reject excluded history.

    The LinkedIn headings are read on each validation. A newly documented employer
    within the approved window enters the required set automatically. Missing sources fail.
    """
    if re.search(r"^##\s+(?:Additional|Earlier) Experience\s*$", markdown, re.MULTILINE | re.IGNORECASE):
        raise CareerCoverageError("cv_markdown must keep all employers in one Experience section")
    if re.search(r"^#{1,6}\s+.*(?:&#(?:x[0-9a-f]+|\d+);|&nbsp;)", markdown, re.MULTILINE | re.IGNORECASE):
        raise CareerCoverageError("CV headings must not contain encoded whitespace or HTML entities")
    if len(re.findall(r"^##\s+Experience\s*$", markdown, re.MULTILINE | re.IGNORECASE)) != 1:
        raise CareerCoverageError("cv_markdown must have exactly one Experience section")
    section = re.split(r"(?im)^##\s+Experience\s*$", markdown, maxsplit=1)[1]
    section = re.split(r"(?m)^##\s+", section, maxsplit=1)[0]
    markers = set()
    for line in section.splitlines():
        bullet = re.match(r"^(\s*)([-*+]|\d+[.)])\s+", line)
        if bullet:
            if bullet[1] or bullet[2] not in {"-", "*", "+"}:
                raise CareerCoverageError("Experience bullets must be flat unordered lists")
            markers.add(bullet[2])
    if len(markers) > 1:
        raise CareerCoverageError("Experience bullets must use a consistent list marker")
    context = _context(source_path, context)
    all_roles = _corrected_roles(source_path, context=context)
    roles = _scoped_roles(all_roles, source_path, reference_date, context=context)
    for employer in all_roles.keys() - roles.keys():
        aliases = context.employer_aliases.get(employer.casefold(), (employer,))
        if any(re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", markdown, re.IGNORECASE) for alias in aliases):
            raise CareerCoverageError(f"cv_markdown mentions an employer outside the approved career window: {employer}")
    entries = _cv_entries(markdown)
    for employer, (expected_start, expected_end) in roles.items():
        aliases = context.employer_aliases.get(employer.casefold(), (employer,))
        matching = []
        for title, body in entries:
            if not any(re.search(r"(?<!\w)" + re.escape(alias) + r"(?!\w)", title, re.IGNORECASE) for alias in aliases):
                continue
            period = _PERIOD.search(body)
            if period is not None:
                matching.append(period)
        if not matching:
            raise CareerCoverageError(f"cv_markdown is missing a dated employer entry for {employer}")
        for period in matching:
            start = _date_key(period.group("start"))
            end_text = period.group("end")
            end = None if end_text.casefold() in {"present", "current"} else _date_key(end_text)
            start_ok = start == expected_start
            end_ok = (
                end is None if expected_end is None else
                end == expected_end
            )
            if start_ok and end_ok:
                break
        else:
            raise CareerCoverageError(f"cv_markdown has unsupported dates for {employer}")
