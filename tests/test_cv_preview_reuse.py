from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from jobintel.applications import ApplicationError, HostMarkdownDocxConverter, _reuse_cv_preview


class CvPreviewReuseTests(unittest.TestCase):
    def test_reuses_exact_preview_and_refuses_changed_artifact(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root / "converter.ps1"
            options = root / "options.json"
            script.write_text("convert", encoding="utf-8")
            options.write_text("{}", encoding="utf-8")
            draft = root / ".codex-work" / "application" / "vacancy" / "cv.md"
            draft.parent.mkdir(parents=True)
            draft.write_text("## Experience\n- Delivered a result.\n", encoding="utf-8")
            converter = HostMarkdownDocxConverter(root, script_path=script, options_path=options, powershell="pwsh")
            preview = converter.preview_directory(draft)
            preview.mkdir(parents=True)
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
