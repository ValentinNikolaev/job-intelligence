from __future__ import annotations

import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from jobintel.applications import ApplicationError, HostMarkdownDocxConverter, _reuse_cv_preview
from jobintel.document_quality_cli import main as document_main


class CvPreviewReuseTests(unittest.TestCase):
    def test_preview_reuses_crlf_draft_after_lf_staging(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "converter.ps1"
            options = root / "options.json"
            script.write_text("convert", encoding="utf-8")
            options.write_text("{}", encoding="utf-8")
            draft = root / ".codex-work" / "application" / "vacancy" / "cv.md"
            draft.parent.mkdir(parents=True)
            draft.write_bytes(b"## Experience\r\n- Delivered a result.\r\n")
            converter = HostMarkdownDocxConverter(root, script_path=script, options_path=options, powershell="pwsh")
            converted_source = []

            def convert(source: Path, target: Path) -> None:
                converted_source.append(source.read_bytes())
                target.write_bytes(b"reviewed fixture bytes")

            def export_pdf(source: Path, target: Path) -> Path:
                target.write_bytes(b"pdf fixture bytes")
                return target

            def render_pdf_pages(source: Path, target: Path) -> dict:
                target.mkdir()
                for index in (1, 2):
                    (target / f"page-{index}.png").write_bytes(b"page")
                return {"pages": ["page-1.png", "page-2.png"],
                        "artifact_sha256": hashlib.sha256(source.read_bytes()).hexdigest()}

            def validate_export(source: Path, artifact: Path) -> dict:
                return {"source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                        "artifact_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest()}

            with (patch("jobintel.applications.HostMarkdownDocxConverter", return_value=converter),
                  patch.object(converter, "convert", side_effect=convert),
                  patch("jobintel.document_quality_cli.preview_capabilities", return_value={}),
                  patch("jobintel.document_quality_cli.validate_export", side_effect=validate_export),
                  patch("jobintel.document_quality_cli.verify_cv_experience", return_value=1),
                  patch("jobintel.document_quality_cli.export_pdf", side_effect=export_pdf),
                  patch("jobintel.document_quality_cli.pdf_page_count", return_value=2),
                  patch("jobintel.document_quality_cli.render_pdf_pages", side_effect=render_pdf_pages),
                  patch("jobintel.document_quality_cli.cv_role_page_warnings", return_value=[]),
                  patch("jobintel.document_quality_cli.timed_call", side_effect=lambda root, stage, vacancy, action: action()),
                  redirect_stdout(io.StringIO())):
                self.assertEqual(0, document_main(["preview-cv", str(draft)], root=root))
                self.assertEqual(0, document_main(["preview-cv", str(draft)], root=root))

            staged = root / "staged" / "cv.md"
            staged.parent.mkdir()
            staged.write_bytes(b"## Experience\n- Delivered a result.\n")
            self.assertEqual(staged.read_bytes(), converted_source[0])
            target = staged.with_suffix(".docx")
            self.assertTrue(_reuse_cv_preview(draft, staged, target, converter))
            self.assertEqual(b"reviewed fixture bytes", target.read_bytes())
            self.assertEqual(1, len(converted_source))
            staged.write_bytes(b"## Experience\n- Changed result.\n")
            with self.assertRaisesRegex(ApplicationError, "no longer matches"):
                _reuse_cv_preview(draft, staged, target, converter)

    def test_reuses_exact_preview_and_refuses_changed_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "converter.ps1"
            options = root / "options.json"
            script.write_text("convert", encoding="utf-8")
            options.write_text("{}", encoding="utf-8")
            draft = root / ".codex-work" / "application" / "vacancy" / "cv.md"
            draft.parent.mkdir(parents=True)
            draft.write_bytes(b"## Experience\n- Delivered a result.\n")
            converter = HostMarkdownDocxConverter(root, script_path=script, options_path=options, powershell="pwsh")
            preview = converter.preview_directory(draft)
            preview.mkdir(parents=True)
            (preview / "cv.md").write_bytes(draft.read_bytes())
            artifact = preview / "cv.docx"
            artifact.write_bytes(b"reviewed fixture bytes")
            receipt = {"source_sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
                       "docx_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                       "page_count": 2, "rendered_pages": 2, "experience_bullets": 1}
            (preview / "receipt.json").write_text(json.dumps(receipt), encoding="utf-8")
            staged = root / "staged" / "cv.md"
            staged.parent.mkdir()
            staged.write_bytes(draft.read_bytes())
            target = staged.with_suffix(".docx")
            self.assertTrue(_reuse_cv_preview(draft, staged, target, converter))
            self.assertEqual(artifact.read_bytes(), target.read_bytes())
            artifact.write_bytes(b"changed after review")
            with self.assertRaisesRegex(ApplicationError, "no longer matches"):
                _reuse_cv_preview(draft, staged, target, converter)
            self.assertEqual(b"reviewed fixture bytes", target.read_bytes())
