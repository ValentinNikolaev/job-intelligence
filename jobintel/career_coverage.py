"""Check that a tailored CV retains every employer in the candidate record."""

from __future__ import annotations

import re
from pathlib import Path


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
_ALIASES = {
    "simple app": ("simple app", "simple.life", "simple life"),
    "pdffiller.com": ("pdffiller.com", "pdffiller"),
    "coinsbank/bit-x": ("coinsbank/bit-x", "coinsbank", "bit-x"),
}
_ALLOWED_SECTIONS = {"experience", "additional experience", "earlier experience"}


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


def _corrected_roles(source_path: Path) -> dict[str, tuple[tuple[int, int | None], tuple[int, int | None] | None]]:
    linked = _source_roles(_read_source(source_path))
    # The primary CV is another immutable source. Its employer headings can only add
    # coverage; later candidate clarifications resolve conflicting imported dates.
    primary_path = source_path.with_name("backend-engineer-cv.md")
    if primary_path.is_file() or (source_path.parents[2] / ".git").exists():
        primary = _source_roles(_read_source(primary_path), section_name="Work Experience")
        for employer, period in primary.items():
            if not any(
                employer.casefold() == other.casefold()
                or employer.casefold() in _ALIASES.get(other.casefold(), ())
                for other in linked
            ):
                linked[employer] = period

    if "Simple App" in linked or "CRURATED" in linked:
        clarification = _read_source(source_path.with_name("user-confirmed-career-clarifications.md"))
        if "Simple App" in linked:
            simple_section = re.split(r"(?m)^## Simple\.life\s*$", clarification, maxsplit=1)
            if len(simple_section) != 2:
                raise CareerCoverageError("candidate career clarification has no Simple.life dates")
            simple_period = _PERIOD.search(re.split(r"(?m)^## ", simple_section[1], maxsplit=1)[0])
            follow_up = _read_source(source_path.with_name("user-confirmed-simple-life-follow-up-2026-09-26.md"))
            if simple_period is None or "does not establish" not in follow_up or "exact employment end date" not in follow_up:
                raise CareerCoverageError("candidate Simple.life end-date clarification is incomplete")
            linked["Simple App"] = (_date_key(simple_period.group("start")), (_date_key(simple_period.group("end"))[0], None))
        if "CRURATED" in linked:
            crurated_section = re.split(r"(?m)^## CRURATED\s*$", clarification, maxsplit=1)
            if len(crurated_section) != 2:
                raise CareerCoverageError("candidate career clarification has no CRURATED dates")
            crurated_period = _PERIOD.search(re.split(r"(?m)^## ", crurated_section[1], maxsplit=1)[0])
            if crurated_period is None:
                raise CareerCoverageError("candidate career clarification has no CRURATED dates")
            linked["CRURATED"] = (_date_key(crurated_period.group("start")), _date_key(crurated_period.group("end")))
    if "PDFfiller.com" in linked:
        letter = _read_source(source_path.with_name("employment-letter-extract-2026-09-25.md"))
        correction = re.search(r"Use\s+((?:" + _MONTH + r")\s+\d{4})\s+as the PDFfiller end date", letter, re.IGNORECASE)
        if correction is None:
            raise CareerCoverageError("candidate PDFfiller end-date clarification is missing")
        linked["PDFfiller.com"] = (linked["PDFfiller.com"][0], _date_key(correction.group(1)))
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
        elif section in {"additional experience", "earlier experience"} and _PERIOD.search(line):
            entries.append((re.sub(r"^\s*[-*]\s+", "", line), line))
    return entries


def validate_career_coverage(markdown: str, source_path: Path) -> None:
    """Require every sourced employer as a dated Experience or earlier-work entry.

    The LinkedIn headings are read on each validation. A newly documented employer
    therefore enters the required set automatically, while corrupt/missing sources fail.
    """
    roles = _corrected_roles(source_path)
    entries = _cv_entries(markdown)
    for employer, (expected_start, expected_end) in roles.items():
        aliases = _ALIASES.get(employer.casefold(), (employer,))
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
                end is not None and end[0] == expected_end[0] and (
                    expected_end[1] is None or end[1] == expected_end[1]
                )
            )
            if start_ok and end_ok:
                break
        else:
            raise CareerCoverageError(f"cv_markdown has unsupported dates for {employer}")
