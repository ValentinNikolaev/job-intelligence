from __future__ import annotations

import re
from html.parser import HTMLParser
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit, urlunsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from jobintel.job_alerts import _MailHTML, _posting


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, *args):
        return None


def _tracking_url(value: str) -> str:
    url = urlsplit(value)
    if (url.scheme not in {"http", "https"} or url.hostname != "url8035.arc.dev"
            or url.path != "/ls/click" or url.username or url.password
            or url.port not in {None, 443} or set(parse_qs(url.query)) != {"upn"}):
        raise ValueError("unsupported Arc tracking URL")
    return urlunsplit(url._replace(scheme="https", fragment=""))


def resolve_tracking(value: str, *, opener=None) -> str:
    """Resolve an authorized job-card link without following its final destination."""
    url = _tracking_url(value)
    opener = opener or build_opener(_NoRedirect())
    seen = set()
    for _ in range(4):
        if url in seen:
            raise ValueError("Arc tracking redirect loop")
        seen.add(url)
        try:
            response = opener.open(Request(url, method="HEAD"), timeout=20)
        except HTTPError as exc:
            response = exc
        try:
            status = response.code
            destination = response.headers.get("Location")
        finally:
            response.close()
        if status not in {301, 302, 303, 307, 308} or not destination:
            raise ValueError(f"Arc tracking returned no job destination (HTTP {status})")
        if urlsplit(destination).hostname in {"arc.dev", "www.arc.dev"}:
            return _posting(destination, "arc")[1]
        url = _tracking_url(destination)
    raise ValueError("too many Arc tracking redirects")


class _Cards(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.card = None
        self.cards = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.card = (dict(attrs).get("href"), _MailHTML())
        elif self.card:
            self.card[1].handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if tag == "a" and self.card:
            url, parser = self.card
            lines = [line.strip() for line in "".join(parser.parts).splitlines() if line.strip()]
            if (url and len(lines) >= 4 and re.fullmatch(r"(?:\d+ \w+ )?ago", lines[1])
                    and lines[3] in {"Permanent", "Contract", "Freelance", "Full time", "Part time"}):
                self.cards.append({"title": lines[2], "company": lines[0], "source_url": url,
                                   "description": "\n".join(lines), "employment_type": lines[3]})
            self.card = None
        elif self.card:
            self.card[1].handle_endtag(tag)

    def handle_data(self, data):
        if self.card:
            self.card[1].handle_data(data)


def go_php_cards(body_html: str) -> tuple[list[dict], int]:
    parser = _Cards()
    parser.feed(body_html)
    selected = [card for card in parser.cards if re.search(r"\b(?:Go(?:lang)?|PHP)\b", card["description"], re.I)]
    return selected, len(parser.cards) - len(selected)
