"""Check actual exports deterministically; visual review is a separate attestation."""
from __future__ import annotations

import hashlib
import html
import json
import math
import re
import shutil
import subprocess
import sys
import tempfile
import time
import unicodedata
import zipfile
from collections.abc import Mapping
from collections import Counter
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


class DocumentQualityError(ValueError):
    pass


_W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"
_LINK = re.compile(r"(?<!!)\[([^\]\n]+)\]\(([^\s)]+)(?:\s+\"[^\"]*\")?\)")


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _tokens(text: str) -> list[str]:
    text = unicodedata.normalize("NFKC", text).replace("\u00ad", "")
    return re.findall(r"[^\W_]+", text.casefold(), flags=re.UNICODE)


def markdown_visible_text(markdown: str) -> str:
    """Normalize project text-first Markdown; fail on unsupported image/reference links."""
    if re.search(r"!\[|\[[^\]\n]+\]\s*\[|^\s*\[[^\]]+\]:", markdown, re.MULTILINE):
        raise DocumentQualityError("Export validation requires inline text links and no Markdown images")
    markdown = _LINK.sub(lambda match: match[1], markdown)
    markdown = re.sub(r"<(https?://[^>]+|[^<>\s]+@[^<>\s]+)>", r"\1", markdown)
    markdown = re.sub(r"<!--.*?-->", "", markdown, flags=re.DOTALL)
    markdown = re.sub(r"<[^>]+>", "", markdown)
    lines = []
    for line in markdown.splitlines():
        if re.match(r"^\s*(```|~~~)", line):
            continue
        if re.fullmatch(r"\s*\|?\s*:?-{3,}:?\s*(?:\|\s*:?-{3,}:?\s*)*\|?\s*", line):
            continue
        line = re.sub(r"^\s{0,3}(?:\d+[.)]\s+|[-+*]\s+|#{1,6}\s+|>\s?)", "", line)
        lines.append(line)
    return html.unescape("\n".join(lines))


def _xml(archive: zipfile.ZipFile, name: str) -> ET.Element:
    try:
        info = archive.getinfo(name)
        if info.file_size > 20_000_000:
            raise DocumentQualityError(f"DOCX XML part is too large: {name}")
        return ET.fromstring(archive.read(info))
    except (KeyError, ET.ParseError) as exc:
        raise DocumentQualityError(f"Invalid or missing DOCX XML part: {name}") from exc


def _docx_contents(path: Path, min_font_pt: float) -> tuple[str, set[str], dict[str, Any]]:
    try:
        with zipfile.ZipFile(path) as archive:
            content_types = _xml(archive, "[Content_Types].xml")
            if not any(node.get("PartName") == "/word/document.xml" and
                       node.get("ContentType") == "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
                       for node in content_types):
                raise DocumentQualityError("DOCX package does not declare the main Word document")
            package_rels = _xml(archive, "_rels/.rels")
            if not any(node.get("Type", "").endswith("/officeDocument") and
                       node.get("Target", "").lstrip("/") == "word/document.xml" for node in package_rels):
                raise DocumentQualityError("DOCX package is missing its main document relationship")
            document = _xml(archive, "word/document.xml")
            body = document.find(f"{_W}body")
            if body is None:
                raise DocumentQualityError("DOCX has no document body")
            for element in body.iter():
                if element.tag in {f"{_W}vanish", f"{_W}webHidden", f"{_W}del"} and element.get(f"{_W}val", "true") not in {"false", "0", "off"}:
                    raise DocumentQualityError("DOCX contains hidden or deleted text; accept revisions before validation")
            paragraphs = ["".join(node.text or "" if node.tag == f"{_W}t" else " "
                                   for node in paragraph.iter() if node.tag in {f"{_W}t", f"{_W}tab", f"{_W}br", f"{_W}cr"})
                          for paragraph in body.iter(f"{_W}p")]
            if not any(text.strip() for text in paragraphs):
                raise DocumentQualityError("DOCX has no readable body paragraphs")
            font_sizes = []
            applied_styles = {node.get(f"{_W}val") for node in body.iter()
                              if node.tag in {f"{_W}pStyle", f"{_W}rStyle"}}
            size_scopes = [body]
            if "word/styles.xml" in archive.namelist():
                styles = _xml(archive, "word/styles.xml")
                defaults = styles.find(f"{_W}docDefaults")
                if defaults is not None:
                    size_scopes.append(defaults)
                size_scopes.extend(style for style in styles.findall(f"{_W}style")
                                   if style.get(f"{_W}styleId") in applied_styles)
            for scope in size_scopes:
                for node in scope.iter(f"{_W}sz"):
                    try:
                        size = float(node.get(f"{_W}val", "")) / 2
                        if not math.isfinite(size) or size <= 0:
                            raise ValueError("invalid size")
                        font_sizes.append(size)
                    except ValueError as exc:
                        raise DocumentQualityError("DOCX contains an invalid font size") from exc
            if font_sizes and min(font_sizes) < min_font_pt:
                raise DocumentQualityError(f"DOCX font size {min(font_sizes):g} pt is below {min_font_pt:g} pt")
            links = set()
            if "word/_rels/document.xml.rels" in archive.namelist():
                rels = _xml(archive, "word/_rels/document.xml.rels")
                links = {node.get("Target", "") for node in rels
                         if node.get("Type", "").endswith("/hyperlink")}
            return "\n".join(paragraphs), links, {
                "readable_paragraphs": sum(bool(text.strip()) for text in paragraphs),
                "minimum_declared_font_pt": min(font_sizes) if font_sizes else None,
                "font_scope": "body runs, document defaults, directly applied styles",
            }
    except (OSError, zipfile.BadZipFile) as exc:
        raise DocumentQualityError(f"Cannot read DOCX {path}: {exc}") from exc


def _tool(name: str, explicit: str | Path | None = None) -> str:
    candidate = str(explicit) if explicit else shutil.which(name)
    if candidate and (Path(candidate).is_file() or shutil.which(candidate)):
        return candidate
    if explicit is None and name in {"pdftotext", "pdfinfo", "pdftoppm"}:
        for sibling in ("pdfinfo", "pdftoppm", "pdftotext"):
            located = shutil.which(sibling)
            if located:
                path = Path(located).with_name(name + Path(located).suffix)
                if path.is_file():
                    return str(path)
    hint = "Poppler (pdfinfo, pdftotext, pdftoppm)" if name.startswith("pdf") else "LibreOffice (soffice)"
    raise DocumentQualityError(f"Required tool {name} is unavailable. Install {hint} or provide its executable path; no PDF check was performed.")


def preview_capabilities(
    converter_script: str | Path,
    options_path: str | Path,
    powershell: str | None,
) -> dict[str, Any]:
    """Check every CV-preview prerequisite without creating an artifact."""
    script, options = Path(converter_script), Path(options_path)
    if not script.is_file():
        raise DocumentQualityError(f"Markdown-to-DOCX converter not found: {script}")
    if not options.is_file():
        raise DocumentQualityError(f"DOCX options file not found: {options}")
    if not powershell:
        raise DocumentQualityError("PowerShell is required by the Markdown-to-DOCX converter")
    try:
        json.loads(options.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise DocumentQualityError(f"DOCX options are unavailable or invalid: {options}") from exc
    return {"status": "available", "converter": str(script.resolve()),
            "options": str(options.resolve()), "renderer": _tool("pdftoppm"),
            "pdf_exporter": _tool("soffice"), "pdf_info": _tool("pdfinfo"),
            "pdf_text": _tool("pdftotext")}


def _run(command: list[str]) -> str:
    try:
        result = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=180, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise DocumentQualityError(f"Document tool failed: {exc}") from exc
    if result.returncode:
        raise DocumentQualityError(f"Document tool failed: {(result.stderr or result.stdout).strip()[:1000]}")
    return result.stdout


def _pdf_contents(path: Path) -> tuple[str, int]:
    info = _run([_tool("pdfinfo"), str(path.resolve())])
    match = re.search(r"^Pages:\s*(\d+)\s*$", info, re.MULTILINE)
    if not match or int(match[1]) < 1:
        raise DocumentQualityError("PDF page count could not be verified")
    text = _run([_tool("pdftotext"), "-enc", "UTF-8", str(path.resolve()), "-"])
    pages = text.split("\f")
    if pages and not pages[-1].strip():
        pages.pop()
    if len(pages) != int(match[1]) or any(not _tokens(page) for page in pages):
        raise DocumentQualityError("PDF has blank/unreadable pages or extracted page count differs from pdfinfo")
    return text, int(match[1])


def pdf_page_count(path: Path) -> int:
    info = _run([_tool("pdfinfo"), str(Path(path).resolve())])
    match = re.search(r"^Pages:\s*(\d+)\s*$", info, re.MULTILINE)
    if not match or int(match[1]) < 1:
        raise DocumentQualityError("PDF page count could not be verified")
    return int(match[1])


def verify_cv_experience(source: Path, artifact: Path) -> int:
    """Require actual Experience bullets to survive document text extraction."""
    markdown = source.read_text(encoding="utf-8-sig")
    match = re.search(r"(?im)^(?P<marks>#{1,3})\s+Experience\s*$", markdown)
    if not match:
        raise DocumentQualityError("CV has no Experience section")
    remainder = markdown[match.end():]
    following = re.search(rf"(?m)^#{{1,{len(match['marks'])}}}\s+\S", remainder)
    section = remainder[:following.start()] if following else remainder
    bullets = [line for line in section.splitlines() if re.match(r"^\s*[-*]\s+\S", line)]
    if not bullets:
        raise DocumentQualityError("CV Experience has no extractable bullets")
    if artifact.suffix.lower() == ".docx":
        text = _docx_contents(artifact, 9.0)[0]
    else:
        text = _pdf_contents(artifact)[0]
    actual = _tokens(text)
    cursor = 0
    for token in _tokens(markdown_visible_text(section)):
        while cursor < len(actual) and actual[cursor] != token:
            cursor += 1
        if cursor == len(actual):
            raise DocumentQualityError("Export lost or reordered Experience text")
        cursor += 1
    return len(bullets)


def cv_role_page_warnings(source: Path, pdf: Path) -> list[dict[str, str | int]]:
    """Flag role blocks spanning PDF pages for the required human layout review."""
    markdown = source.read_text(encoding="utf-8-sig")
    match = re.search(r"(?im)^(?P<marks>#{1,3})\s+Experience\s*$", markdown)
    if not match:
        raise DocumentQualityError("CV has no Experience section")
    remainder = markdown[match.end():]
    following = re.search(rf"(?m)^#{{1,{len(match['marks'])}}}\s+\S", remainder)
    section = remainder[:following.start()] if following else remainder
    roles: list[dict[str, object]] = []
    for line in section.splitlines():
        heading = re.match(r"^###\s+(.+?)\s*$", line)
        if heading:
            roles.append({"heading": heading.group(1), "bullets": [], "technologies": None})
        elif roles and re.match(r"^\s*[-*]\s+\S", line):
            bullets = roles[-1]["bullets"]
            assert isinstance(bullets, list)
            bullets.append(re.sub(r"^\s*[-*]\s+", "", line))
        elif roles and re.match(r"^\s*Technologies\s*:", line, re.IGNORECASE):
            roles[-1]["technologies"] = line.strip()
    text, _ = _pdf_contents(pdf)
    pages = [_tokens(page) for page in text.split("\f") if page.strip()]

    def page_for(fragment: str) -> int | None:
        sought = _tokens(fragment)
        if not sought:
            return None
        return next((index for index, tokens in enumerate(pages, 1)
                     if any(tokens[offset:offset + len(sought)] == sought
                            for offset in range(len(tokens) - len(sought) + 1))), None)

    warnings: list[dict[str, str | int]] = []
    for role in roles:
        heading = str(role["heading"])
        bullets = role["bullets"]
        assert isinstance(bullets, list)
        heading_page = page_for(heading)
        bullet_pages = [page_for(bullet) for bullet in bullets]
        if heading_page is None or any(page is None for page in bullet_pages):
            warnings.append({"role": heading, "reason": "page_location_unverified"})
        elif bullet_pages and heading_page != bullet_pages[0]:
            warnings.append({"role": heading, "reason": "heading_orphaned",
                             "heading_page": heading_page, "first_bullet_page": bullet_pages[0]})
        elif len(set(bullet_pages)) > 1:
            warnings.append({"role": heading, "reason": "role_split",
                             "first_page": bullet_pages[0], "last_page": bullet_pages[-1]})
        technologies = role["technologies"]
        if technologies is not None and bullet_pages and all(page is not None for page in bullet_pages):
            technologies_page = page_for(str(technologies))
            if technologies_page is None:
                warnings.append({"role": heading, "reason": "technologies_page_unverified"})
            elif technologies_page != bullet_pages[-1]:
                warnings.append({"role": heading, "reason": "technologies_orphaned",
                                 "last_bullet_page": bullet_pages[-1],
                                 "technologies_page": technologies_page})
    return warnings


def _review(artifact_hash: str, value: Mapping[str, Any] | None) -> dict[str, Any]:
    if value is None:
        return {"status": "not_reviewed", "artifact_sha256": artifact_hash}
    if value.get("status") != "reviewed" or value.get("artifact_sha256") != artifact_hash:
        raise DocumentQualityError("Visual review must be reviewed and reference the current artifact_sha256")
    if not isinstance(value.get("reviewer"), str) or not value["reviewer"].strip():
        raise DocumentQualityError("Visual review requires a reviewer")
    try:
        reviewed_at = datetime.fromisoformat(str(value.get("reviewed_at", "")).replace("Z", "+00:00"))
        if reviewed_at.tzinfo is None:
            raise ValueError("timezone required")
    except ValueError as exc:
        raise DocumentQualityError("Visual review requires an ISO timestamp with timezone") from exc
    required = {"page_breaks", "overflow", "readability", "blank_pages"}
    checks = value.get("checks")
    if not isinstance(checks, Mapping) or any(checks.get(key) is not True for key in required):
        raise DocumentQualityError("Visual review must attest page_breaks, overflow, readability, blank_pages checks")
    return {"status": "reviewed", "artifact_sha256": artifact_hash,
            "reviewer": value["reviewer"].strip(), "reviewed_at": value["reviewed_at"],
            "checks": {key: True for key in sorted(required)},
            "method": "recorded reviewer attestation; not an automated visual judgment"}


def _validate_cv_lists(markdown: str, artifact: Path) -> None:
    """Check actual Word numbering; preserved text alone cannot detect broken lists."""
    section = re.split(r"(?im)^##\s+Experience\s*$", markdown, maxsplit=1)
    if len(section) != 2:
        raise DocumentQualityError("CV has no Experience section")
    experience = re.split(r"(?m)^##\s+", section[1], maxsplit=1)[0]
    bullets = [_tokens(markdown_visible_text(line[2:])) for line in experience.splitlines()
               if re.match(r"^[-*+]\s+", line)]
    if not bullets:
        raise DocumentQualityError("CV has no Experience bullets")
    with zipfile.ZipFile(artifact) as archive:
        document = _xml(archive, "word/document.xml")
        numbering = _xml(archive, "word/numbering.xml")
        paragraphs = list(document.iter(_W + "p"))
        cursor = 0
        formats = set()
        for bullet in bullets:
            while cursor < len(paragraphs):
                paragraph = paragraphs[cursor]
                cursor += 1
                text = "".join(node.text or "" for node in paragraph.iter(_W + "t"))
                if _tokens(text) == bullet:
                    break
            else:
                raise DocumentQualityError("DOCX lost a CV bullet paragraph")
            num = paragraph.find(_W + "pPr/" + _W + "numPr")
            if num is None or num.find(_W + "ilvl") is None or num.find(_W + "numId") is None:
                raise DocumentQualityError("DOCX Experience bullet lost list formatting")
            if num.find(_W + "ilvl").get(_W + "val") != "0":
                raise DocumentQualityError("DOCX Experience bullets must not be nested")
            num_id = num.find(_W + "numId").get(_W + "val")
            definition = next((node for node in numbering.findall(_W + "num")
                               if node.get(_W + "numId") == num_id), None)
            abstract = definition.find(_W + "abstractNumId") if definition is not None else None
            level = next((next((level for level in node.findall(_W + "lvl")
                               if level.get(_W + "ilvl") == "0"), None)
                          for node in numbering.findall(_W + "abstractNum")
                          if abstract is not None and node.get(_W + "abstractNumId") == abstract.get(_W + "val")), None)
            if level is None or level.find(_W + "numFmt") is None or level.find(_W + "numFmt").get(_W + "val") != "bullet":
                raise DocumentQualityError("DOCX Experience lists must use bullet markers")
            marker = level.find(_W + "lvlText")
            indent = paragraph.find(_W + "pPr/" + _W + "ind")
            if indent is None:
                indent = level.find(_W + "pPr/" + _W + "ind")
            formats.add((marker.get(_W + "val") if marker is not None else None,
                         tuple(sorted(indent.attrib.items())) if indent is not None else ()))
        if len(formats) > 1:
            raise DocumentQualityError("DOCX Experience bullet markers and indentation must be consistent")


def validate_export(source: Path, artifact: Path, *, max_pages: int | None = None,
                    min_font_pt: float = 9.0, visual_review: Mapping[str, Any] | None = None,
                    require_cv_lists: bool = False) -> dict[str, Any]:
    """Validate all visible source tokens in order; bind receipt to exact artifact bytes."""
    source, artifact = Path(source), Path(artifact)
    if max_pages is not None and (type(max_pages) is not int or max_pages < 1):
        raise DocumentQualityError("max_pages must be a positive integer")
    if not math.isfinite(min_font_pt) or min_font_pt <= 0:
        raise DocumentQualityError("min_font_pt must be positive")
    try:
        markdown = source.read_text(encoding="utf-8-sig")
        artifact_hash = file_sha256(artifact)
    except (OSError, UnicodeError) as exc:
        raise DocumentQualityError(f"Cannot read export inputs: {exc}") from exc
    visible = markdown_visible_text(markdown)
    expected = _tokens(visible)
    if not expected:
        raise DocumentQualityError("Canonical Markdown has no readable text")
    page_count = None
    structure: dict[str, Any] = {}
    if artifact.suffix.lower() == ".docx":
        text, links, structure = _docx_contents(artifact, min_font_pt)
        if require_cv_lists:
            _validate_cv_lists(markdown, artifact)
        if max_pages is not None:
            raise DocumentQualityError("DOCX page count is renderer-dependent; export PDF to enforce a page budget")
        for match in _LINK.finditer(markdown):
            target = html.unescape(match[2].strip("<>"))
            if target.startswith(("https://", "http://", "mailto:", "tel:")) and target not in links:
                raise DocumentQualityError(f"DOCX lost a Markdown hyperlink target: {target}")
    elif artifact.suffix.lower() == ".pdf":
        text, page_count = _pdf_contents(artifact)
        if max_pages is not None and page_count > max_pages:
            raise DocumentQualityError(f"PDF has {page_count} pages, exceeding the budget of {max_pages}")
    else:
        raise DocumentQualityError("Export must be a DOCX or PDF file")
    actual = _tokens(text)
    # Token normalization ignores punctuation, so preserve contacts and numeric
    # expressions separately: 25% must not become 25 or an email become a URL.
    for pattern in (r"[\w.+-]+@[\w.-]+\.[a-zA-Z]{2,}",
                    r"https?://[^\s<>()|]+", r"(?<!\w)\d+(?:[.,]\d+)*(?:\s*%)?"):
        normalize = lambda item: re.sub(r"\s+", "", item).casefold().rstrip(".,;")
        required_values = Counter(normalize(item) for item in re.findall(pattern, visible))
        exported_values = Counter(normalize(item) for item in re.findall(pattern, text))
        if required_values - exported_values:
            missing = next(iter(required_values - exported_values))
            raise DocumentQualityError(f"Export lost or changed a contact or numeric value: {missing}")
    cursor = 0
    for index, token in enumerate(expected):
        while cursor < len(actual) and actual[cursor] != token:
            cursor += 1
        if cursor == len(actual):
            context = " ".join(expected[max(0, index - 4):index + 6])
            raise DocumentQualityError(f"Export lost or reordered canonical text near: {context}")
        cursor += 1
    return {
        "schema_version": 1, "source_file": source.name, "artifact_file": artifact.name,
        "source_sha256": file_sha256(source), "artifact_sha256": artifact_hash,
        "extracted_text_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "canonical_tokens": len(expected), "extracted_tokens": len(actual),
        "checks": {"readable_text": True, "canonical_text_preserved_in_order": True,
                    "contacts_and_numeric_values_preserved": True,
                    "cv_experience_list_formatting": "verified" if require_cv_lists and artifact.suffix.lower() == ".docx" else "not_checked",
                   "hyperlink_targets": "verified" if artifact.suffix.lower() == ".docx" else "not_checked"},
        "structure": structure, "page_count": page_count, "max_pages": max_pages,
        "visual_review": _review(artifact_hash, visual_review),
        "limits": "Token comparison checks preservation, not factual truth or visual layout. PDF annotations and inherited fonts are not audited.",
    }


def export_pdf(source: Path, target: Path, *, executable: str | Path | None = None) -> Path:
    """Convert with LibreOffice or Windows Word, without overwriting a PDF."""
    source, target = Path(source).resolve(), Path(target).resolve()
    if source.suffix.lower() != ".docx" or not source.is_file():
        raise DocumentQualityError("PDF export requires an existing DOCX")
    if target.suffix.lower() != ".pdf" or target.exists():
        raise DocumentQualityError("PDF target must be a new .pdf file")
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        office_executable = _tool("soffice", executable)
    except DocumentQualityError:
        if executable is not None or not shutil.which("pwsh") or sys.platform != "win32":
            raise
        script = Path(__file__).resolve().parents[1] / "scripts" / "export_docx_pdf_word.ps1"
        if not script.is_file():
            raise DocumentQualityError(f"Word PDF export script is missing: {script}")
        _run([shutil.which("pwsh"), "-NoProfile", "-File", str(script), "-InputPath", str(source), "-OutputPath", str(target)])
        if not target.is_file() or target.stat().st_size == 0:
            raise DocumentQualityError("Word did not create a nonempty PDF")
        return target
    work = Path(tempfile.mkdtemp(prefix="jobintel-pdf-"))
    try:
        _run([office_executable, f"-env:UserInstallation={(work / 'profile').as_uri()}", "--headless", "--convert-to", "pdf", "--outdir", str(work), str(source)])
        converted = work / (source.stem + ".pdf")
        if not converted.is_file() or converted.stat().st_size == 0:
            raise DocumentQualityError("LibreOffice did not create a nonempty PDF")
        with target.open("xb") as output:
            output.write(converted.read_bytes())
    finally:
        for attempt in range(20):
            try:
                shutil.rmtree(work)
                break
            except FileNotFoundError:
                break
            except OSError as exc:
                if getattr(exc, "winerror", None) not in (32, 145) or attempt == 19:
                    raise DocumentQualityError(f"Could not remove LibreOffice profile: {exc}") from exc
                time.sleep(0.25)
    return target


def render_pdf_pages(source: Path, target_directory: Path, *, executable: str | Path | None = None) -> dict[str, Any]:
    """Render page PNGs for a reviewer; creation is never visual approval."""
    source, target_directory = Path(source).resolve(), Path(target_directory).resolve()
    if source.suffix.lower() != ".pdf" or not source.is_file():
        raise DocumentQualityError("Rendering requires an existing PDF")
    executable = _tool("pdftoppm", executable)
    target_directory.mkdir(parents=True, exist_ok=False)
    _run([executable, "-png", "-r", "120", str(source), str(target_directory / "page")])
    pages = sorted(target_directory.glob("page-*.png"))
    if not pages or any(path.stat().st_size == 0 for path in pages):
        raise DocumentQualityError("PDF renderer produced no usable page images")
    return {"artifact_sha256": file_sha256(source), "visual_review": {"status": "not_reviewed"},
            "pages": [{"path": str(path), "sha256": file_sha256(path)} for path in pages]}
