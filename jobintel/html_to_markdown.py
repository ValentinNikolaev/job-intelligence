from __future__ import annotations

import html
import re
from html.parser import HTMLParser


class _MarkdownParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.list_depth = 0
        self.link_hrefs: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style", "nav"}:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag in {"p", "div", "section", "article", "br", "hr"}:
            self.parts.append("\n\n" if tag != "br" else "\n")
        elif tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            self.parts.append(f"\n\n{'#' * int(tag[1])} ")
        elif tag in {"ul", "ol"}:
            self.list_depth += 1
            self.parts.append("\n")
        elif tag == "li":
            self.parts.append(f"\n{'  ' * max(0, self.list_depth - 1)}- ")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "a":
            href = dict(attrs).get("href")
            self.link_hrefs.append(href)
            if href:
                self.parts.append(f"[\x00{href}\x00")

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style", "nav"}:
            self.skip_depth = max(0, self.skip_depth - 1)
            return
        if self.skip_depth:
            return
        if tag in {"ul", "ol"}:
            self.list_depth = max(0, self.list_depth - 1)
            self.parts.append("\n")
        elif tag in {"strong", "b"}:
            self.parts.append("**")
        elif tag in {"em", "i"}:
            self.parts.append("*")
        elif tag == "a":
            href = self.link_hrefs.pop() if self.link_hrefs else None
            if href:
                # A marker inserted at start contains the href and is resolved later.
                self.parts.append("]")
        elif tag in {"p", "div", "section", "article"}:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)


def html_to_markdown(value: str | None) -> str:
    if not value:
        return ""
    decoded = html.unescape(html.unescape(value))
    parser = _MarkdownParser()
    parser.feed(decoded)
    text = "".join(parser.parts)
    # Turn the start marker `[\0href\0label]` into `[label](href)`.
    text = re.sub(r"\[\x00([^\x00]+)\x00([^]]*)\]", r"[\2](\1)", text)
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r" *\n *", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()
