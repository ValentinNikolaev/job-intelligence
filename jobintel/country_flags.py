from __future__ import annotations

import gettext
import re
from functools import lru_cache

import pycountry


MAX_COUNTRY_FLAGS = 5
COUNTRY_FLAGS = {
    code: "".join(chr(0x1F1E6 + ord(letter) - ord("A")) for letter in code)
    for code in [*(country.alpha_2 for country in pycountry.countries), "XK"]
}
_ALIASES = {
    "Britain": "GB",
    "Great Britain": "GB",
    "England": "GB",
    "Scotland": "GB",
    "Wales": "GB",
    "Northern Ireland": "GB",
    "Великобритания": "GB",
    "Велика Британія": "GB",
    "Russia": "RU",
    "South Korea": "KR",
    "North Korea": "KP",
    "Vietnam": "VN",
    "Taiwan": "TW",
    "Bolivia": "BO",
    "Venezuela": "VE",
    "Iran": "IR",
    "Syria": "SY",
    "Tanzania": "TZ",
    "Moldova": "MD",
    "Kosovo": "XK",
    "Косово": "XK",
}
_ABBREVIATIONS = {
    "UK": "GB", "U.K.": "GB", "US": "US", "USA": "US",
    "U.S.": "US", "U.S.A.": "US", "UAE": "AE", "США": "US",
}


@lru_cache(maxsize=1)
def _country_names() -> tuple[dict[str, str], re.Pattern[str]]:
    translations = [
        gettext.translation("iso3166-1", pycountry.LOCALES_DIR, languages=[language])
        for language in ("ru", "uk", "it", "de", "fr", "es", "pl", "pt")
    ]
    names = {}
    for country in pycountry.countries:
        for field in ("name", "official_name", "common_name"):
            name = dict(country).get(field)
            if name:
                names[name.casefold()] = country.alpha_2
                for translation in translations:
                    names[translation.gettext(name).casefold()] = country.alpha_2
    names.update({name.casefold(): code for name, code in _ALIASES.items()})
    # Longest names first keeps Northern Ireland and Guinea-Bissau intact.
    pattern = re.compile(
        r"(?<!\w)(?:" + "|".join(re.escape(name) for name in sorted(names, key=lambda x: (-len(x), x)))
        + r")(?!\w)",
        re.IGNORECASE,
    )
    return names, pattern


def country_codes_for_location(location: object) -> list[str]:
    """Recognize explicit countries, without geocoding cities or expanding regions."""
    if not isinstance(location, str) or not location.strip():
        return []
    location = location.strip()
    tokens = re.split(r"[\s,;/|]+", location)
    codes = [_ABBREVIATIONS.get(token, token) for token in tokens]
    # Arbitrary ISO codes require a field containing only country codes, so 'in'
    # and 'San Francisco, CA' cannot be mistaken for India or Canada.
    if all(code in COUNTRY_FLAGS for code in codes):
        return list(dict.fromkeys(codes))

    names, pattern = _country_names()
    matches = [(match.start(), names[match.group().casefold()]) for match in pattern.finditer(location)]
    abbreviations = re.compile(
        r"(?<!\w)(?:" + "|".join(re.escape(name) for name in sorted(_ABBREVIATIONS, key=len, reverse=True))
        + r")(?!\w)"
    )
    matches.extend(
        (match.start(), _ABBREVIATIONS[match.group()]) for match in abbreviations.finditer(location)
    )
    return list(dict.fromkeys(code for _, code in sorted(matches)))


def render_country_flags(country_codes: list[str]) -> str:
    unique = dict.fromkeys(code for code in country_codes if code in COUNTRY_FLAGS)
    return " ".join(COUNTRY_FLAGS[code] for code in list(unique)[:MAX_COUNTRY_FLAGS])
