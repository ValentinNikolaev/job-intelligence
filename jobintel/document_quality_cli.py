"""CLI for draft previews and export checks."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import tempfile
from pathlib import Path

import yaml

from .document_quality import DocumentQualityError, cv_role_page_warnings, export_pdf, pdf_page_count, preview_capabilities, render_pdf_pages, validate_export, verify_cv_experience
from .preparation_timing import timed_call


def main(argv: list[str] | None = None, *, root: Path | None = None) -> int:
    parser = argparse.ArgumentParser(prog="run.py documents")
    commands = parser.add_subparsers(dest="action", required=True)
    validate = commands.add_parser("validate", help="Compare an actual DOCX/PDF with its canonical Markdown")
    validate.add_argument("source", type=Path, help="Canonical Markdown")
    validate.add_argument("artifact", type=Path)
    validate.add_argument("--max-pages", type=int, help="PDF-only page budget")
    validate.add_argument("--min-font-pt", type=float, default=9.0, help="DOCX declared font floor")
    validate.add_argument("--visual-review", type=Path, help="YAML reviewer attestation bound to the artifact SHA-256")
    validate.add_argument("--receipt", type=Path, help="Save receipt to a new JSON file")
    export = commands.add_parser("export-pdf", help="Export an existing DOCX through LibreOffice or Windows Word")
    export.add_argument("source", type=Path)
    export.add_argument("target", type=Path)
    export.add_argument("--executable", type=Path, help="Path to soffice executable")
    render = commands.add_parser("render", help="Render PDF pages for visual inspection; does not approve layout")
    render.add_argument("source", type=Path)
    render.add_argument("target", type=Path, help="New directory for page PNGs")
    render.add_argument("--executable", type=Path, help="Path to pdftoppm executable")
    preview = commands.add_parser("preview-cv", help="Convert and render a draft CV under .codex-work before publication")
    preview.add_argument("source", type=Path, help="Draft cv.md under .codex-work")
    preview.add_argument("--max-pages", type=int, default=2)
    args = parser.parse_args(argv)
    base = Path(root or Path.cwd())

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else base / path

    try:
        if args.action == "preview-cv":
            from .applications import HostMarkdownDocxConverter, _canonical_application_markdown, _win_long_path

            source = resolve(args.source).resolve()
            work = (base / ".codex-work").resolve()
            if source.name != "cv.md" or not _win_long_path(source).is_file() or not source.is_relative_to(work):
                raise DocumentQualityError("preview-cv requires a draft cv.md under .codex-work")
            converter = HostMarkdownDocxConverter(base, timing_vacancy=source.parent.name)
            try:
                capability = preview_capabilities(converter.script_path, converter.options_path, converter.powershell)
            except DocumentQualityError as exc:
                print(json.dumps({"status": "unavailable", "source": str(source), "reason": str(exc)}, ensure_ascii=False, indent=2))
                return 1
            target = converter.preview_directory(source)
            parent = target.parent
            receipt = target / "receipt.json"
            canonical_source = _canonical_application_markdown(
                _win_long_path(source).read_text(encoding="utf-8")
            ).encode("utf-8")
            canonical_hash = hashlib.sha256(canonical_source).hexdigest()
            if receipt.is_file() and (target / "cv.docx").is_file() and (target / "cv.pdf").is_file():
                result = json.loads(receipt.read_text(encoding="utf-8"))
                if (result.get("source_sha256") != canonical_hash
                        or result.get("source_sha256") != hashlib.sha256(_win_long_path(target / "cv.md").read_bytes()).hexdigest()
                        or result.get("docx_sha256") != hashlib.sha256((target / "cv.docx").read_bytes()).hexdigest()
                        or result.get("pdf_sha256") != hashlib.sha256((target / "cv.pdf").read_bytes()).hexdigest()
                        or len(list((target / "pages").glob("page-*.png"))) != result.get("page_count")):
                    raise DocumentQualityError("cached CV preview no longer matches its source or rendered artifacts")
                if result["page_count"] > args.max_pages:
                    raise DocumentQualityError(f"PDF has {result['page_count']} pages, exceeding the budget of {args.max_pages}")
                if "layout_warnings" not in result:
                    result["layout_warnings"] = cv_role_page_warnings(source, target / "cv.pdf")
                    receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                result["cached"] = True
                validate_export(source, target / "cv.docx", require_cv_lists=True)
            else:
                parent.mkdir(parents=True, exist_ok=True)
                with tempfile.TemporaryDirectory(prefix=".preview-", dir=parent) as temporary:
                    stage = Path(temporary)
                    (stage / "cv.md").write_bytes(canonical_source)
                    converter.convert(stage / "cv.md", stage / "cv.docx")
                    docx_check = validate_export(stage / "cv.md", stage / "cv.docx", require_cv_lists=True)
                    bullets = verify_cv_experience(stage / "cv.md", stage / "cv.docx")
                    timed_call(base, "pdf_export", source.parent.name,
                               lambda: export_pdf(stage / "cv.docx", stage / "cv.pdf"))
                    page_count = pdf_page_count(stage / "cv.pdf")
                    if page_count > args.max_pages:
                        raise DocumentQualityError(f"PDF has {page_count} pages, exceeding the budget of {args.max_pages}")
                    pages = timed_call(base, "page_render", source.parent.name,
                                       lambda: render_pdf_pages(stage / "cv.pdf", stage / "pages"))
                    if len(pages["pages"]) != page_count:
                        raise DocumentQualityError("rendered page count differs from PDF metadata")
                    layout_warnings = cv_role_page_warnings(stage / "cv.md", stage / "cv.pdf")
                    if target.exists():
                        raise DocumentQualityError(f"incomplete preview already exists: {target}")
                    stage.rename(target)
                result = {"source": str(source), "docx": str(target / "cv.docx"),
                          "pdf": str(target / "cv.pdf"), "page_count": page_count,
                          "experience_bullets": bullets, "rendered_pages": len(pages["pages"]),
                          "source_sha256": docx_check["source_sha256"],
                          "docx_sha256": docx_check["artifact_sha256"],
                          "pdf_sha256": pages["artifact_sha256"],
                          "visual_review": "required", "layout_warnings": layout_warnings,
                          "cached": False}
                receipt.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            result["availability"] = capability
        elif args.action == "validate":
            review = None
            if args.visual_review:
                review = yaml.safe_load(resolve(args.visual_review).read_text(encoding="utf-8"))
                if not isinstance(review, dict):
                    raise DocumentQualityError("Visual-review YAML must contain a mapping")
            result = validate_export(resolve(args.source), resolve(args.artifact), max_pages=args.max_pages,
                                     min_font_pt=args.min_font_pt, visual_review=review)
            if args.receipt:
                target = resolve(args.receipt)
                target.parent.mkdir(parents=True, exist_ok=True)
                with target.open("x", encoding="utf-8") as output:
                    output.write(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        elif args.action == "export-pdf":
            path = export_pdf(resolve(args.source), resolve(args.target), executable=resolve(args.executable) if args.executable else None)
            result = {"pdf": str(path), "text_validation": "not_performed", "visual_review": "not_reviewed"}
        else:
            result = render_pdf_pages(resolve(args.source), resolve(args.target), executable=resolve(args.executable) if args.executable else None)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (DocumentQualityError, OSError, yaml.YAMLError) as exc:
        print(f"Document quality error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
