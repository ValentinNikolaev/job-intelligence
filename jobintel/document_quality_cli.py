"""CLI for optional export checks and rendering of already prepared documents."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import yaml

from .document_quality import DocumentQualityError, export_pdf, render_pdf_pages, validate_export


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
    export = commands.add_parser("export-pdf", help="Export an existing DOCX through installed LibreOffice")
    export.add_argument("source", type=Path)
    export.add_argument("target", type=Path)
    export.add_argument("--executable", type=Path, help="Path to soffice executable")
    render = commands.add_parser("render", help="Render PDF pages for visual inspection; does not approve layout")
    render.add_argument("source", type=Path)
    render.add_argument("target", type=Path, help="New directory for page PNGs")
    render.add_argument("--executable", type=Path, help="Path to pdftoppm executable")
    args = parser.parse_args(argv)
    base = Path(root or Path.cwd())

    def resolve(path: Path) -> Path:
        return path if path.is_absolute() else base / path

    try:
        if args.action == "validate":
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
