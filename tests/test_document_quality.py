from __future__ import annotations

import json
import shutil
import tempfile
import unittest
import zipfile
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
from pathlib import Path
from unittest.mock import patch
from xml.sax.saxutils import escape

from jobintel.document_quality import (
    DocumentQualityError, _tool, cv_role_page_warnings, export_pdf, file_sha256, markdown_visible_text,
    render_pdf_pages, validate_export,
)
from jobintel.document_quality_cli import main


def write_docx(path: Path, paragraphs: list[str], *, link: str | None = None,
               size: int = 22, hidden: bool = False) -> None:
    runs = ''.join('<w:p><w:r><w:rPr><w:sz w:val="%s"/>%s</w:rPr><w:t>%s</w:t></w:r></w:p>' %
                   (size, '<w:vanish/>' if hidden else '', escape(text)) for text in paragraphs)
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/></Types>')
        archive.writestr("_rels/.rels", '<Relationships><Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>')
        archive.writestr("word/document.xml", '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>' + runs + '</w:body></w:document>')
        if link:
            archive.writestr("word/_rels/document.xml.rels", '<Relationships><Relationship Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink" Target="' + escape(link, {'"': '&quot;'}) + '"/></Relationships>')


def write_pdf(path: Path, pages: list[str]) -> None:
    """Small real PDF fixture, requiring no PDF authoring dependency."""
    objects = [b"<< /Type /Catalog /Pages 2 0 R >>", b"", b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>"]
    page_ids = []
    for content in pages:
        page_id = len(objects) + 1
        page_ids.append(page_id)
        objects.append(f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Resources << /Font << /F1 3 0 R >> >> /Contents {page_id + 1} 0 R >>".encode())
        stream = ("BT /F1 12 Tf 50 740 Td (" + content + ") Tj ET").encode("ascii")
        objects.append(f"<< /Length {len(stream)} >>\nstream\n".encode() + stream + b"\nendstream")
    objects[1] = (f"<< /Type /Pages /Count {len(pages)} /Kids [" + " ".join(f"{i} 0 R" for i in page_ids) + "] >>").encode()
    output = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, body in enumerate(objects, 1):
        offsets.append(len(output))
        output += f"{index} 0 obj\n".encode() + body + b"\nendobj\n"
    xref = len(output)
    output += f"xref\n0 {len(objects) + 1}\n0000000000 65535 f \n".encode()
    for offset in offsets:
        output += f"{offset:010d} 00000 n \n".encode()
    output += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode()
    path.write_bytes(output)


class CvListFormattingTests(unittest.TestCase):
    def test_detects_formatting_damage_despite_preserved_text(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source, artifact = root / "cv.md", root / "cv.docx"
            source.write_text("## Experience\n### Employer\n- Built service.\n- Improved reliability.\n", encoding="utf-8")
            for damage in (None, "missing", "nested", "decimal", "indent"):
                with self.subTest(damage=damage):
                    write_docx(artifact, ["Experience", "Employer", "Built service.", "Improved reliability."])
                    with zipfile.ZipFile(artifact) as archive:
                        entries = {name: archive.read(name) for name in archive.namelist()}
                    props = '<w:pPr><w:numPr><w:ilvl w:val="0"/><w:numId w:val="1"/></w:numPr></w:pPr>'
                    xml = entries["word/document.xml"].decode()
                    xml = xml.replace('<w:p><w:r><w:rPr>', '<w:p>' + props + '<w:r><w:rPr>')
                    if damage == "missing":
                        xml = xml.replace(props, "", 3)
                    elif damage == "nested":
                        xml = xml.replace('w:ilvl w:val="0"', 'w:ilvl w:val="1"')
                    elif damage == "indent":
                        xml = xml.replace('<w:p>' + props, '<w:p>' + props.replace('</w:pPr>', '<w:ind w:left="800"/></w:pPr>'), 3)
                    entries["word/document.xml"] = xml.encode()
                    fmt = "decimal" if damage == "decimal" else "bullet"
                    entries["word/numbering.xml"] = ('<w:numbering xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:abstractNum w:abstractNumId="0"><w:lvl w:ilvl="0"><w:numFmt w:val="' + fmt + '"/><w:lvlText w:val="bullet"/><w:pPr><w:ind w:left="720" w:hanging="360"/></w:pPr></w:lvl></w:abstractNum><w:num w:numId="1"><w:abstractNumId w:val="0"/></w:num></w:numbering>').encode()
                    with zipfile.ZipFile(artifact, "w") as archive:
                        for name, content in entries.items():
                            archive.writestr(name, content)
                    validate_export(source, artifact)  # Text preservation still passes.
                    if damage is None:
                        validate_export(source, artifact, require_cv_lists=True)
                    else:
                        with self.assertRaises(DocumentQualityError):
                            validate_export(source, artifact, require_cv_lists=True)


class CvPageLayoutTests(unittest.TestCase):
    def test_flags_role_heading_orphaned_on_previous_page(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "cv.md"
            source.write_text(
                "## Experience\n\n### Recent Role | 2023 - 2026\n"
                "- Built a backend service for support operations.\n"
                "- Improved its production reliability.\n\n## Education\nMSc\n",
                encoding="utf-8",
            )
            page1 = "Experience Recent Role 2023 2026"
            page2 = "Built a backend service for support operations Improved its production reliability Education MSc"
            with patch("jobintel.document_quality._pdf_contents", return_value=(page1 + "\f" + page2 + "\f", 2)):
                warnings = cv_role_page_warnings(source, Path(temporary) / "cv.pdf")
            self.assertEqual("heading_orphaned", warnings[0]["reason"])
            self.assertEqual(1, warnings[0]["heading_page"])
            self.assertEqual(2, warnings[0]["first_bullet_page"])

    def test_complete_role_on_one_page_has_no_warning(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "cv.md"
            source.write_text("## Experience\n\n### Recent Role | 2023 - 2026\n"
                              "- Built a backend service for support operations.\n"
                              "- Improved its production reliability.\n\n## Education\nMSc\n",
                              encoding="utf-8")
            text = "Experience Recent Role 2023 2026 Built a backend service for support operations Improved its production reliability Education MSc\f"
            with patch("jobintel.document_quality._pdf_contents", return_value=(text, 1)):
                self.assertEqual([], cv_role_page_warnings(source, Path(temporary) / "cv.pdf"))

    def test_flags_technologies_line_left_on_next_page(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            source = Path(temporary) / "cv.md"
            source.write_text("## Experience\n\n### Recent Role | 2023 - 2026\n"
                              "- Built a backend service.\nTechnologies: Go, PostgreSQL\n"
                              "\n## Education\nMSc\n", encoding="utf-8")
            pages = "Experience Recent Role 2023 2026 Built a backend service\fTechnologies Go PostgreSQL Education MSc\f"
            with patch("jobintel.document_quality._pdf_contents", return_value=(pages, 2)):
                warnings = cv_role_page_warnings(source, Path(temporary) / "cv.pdf")
            self.assertEqual("technologies_orphaned", warnings[0]["reason"])


class ExportQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "cv.md"
        self.artifact = self.root / "cv.docx"
        self.paragraphs = ["Candidate", "candidate@example.test", "Summary", "Backend PHP engineer",
                           "Experience", "Engineer 2020 - 2026", "Reduced latency by 25%", "Education", "Computer Science"]
        self.source.write_text("# Candidate\n\ncandidate@example.test\n\n## Summary\nBackend PHP engineer\n\n## Experience\nEngineer 2020 - 2026\n- Reduced latency by 25%\n\n## Education\nComputer Science", encoding="utf-8")
        write_docx(self.artifact, self.paragraphs)

    def test_valid_docx_receipt_covers_real_bytes_but_does_not_claim_visual_review(self) -> None:
        receipt = validate_export(self.source, self.artifact)
        self.assertEqual(file_sha256(self.artifact), receipt["artifact_sha256"])
        self.assertEqual(file_sha256(self.source), receipt["source_sha256"])
        self.assertTrue(receipt["checks"]["canonical_text_preserved_in_order"])
        self.assertEqual("not_reviewed", receipt["visual_review"]["status"])
        self.assertIsNone(receipt["page_count"])

    def test_rejects_lost_contacts_dates_metrics_and_section_order(self) -> None:
        for index, replacement in [(1, ""), (5, "Engineer 2021 - 2026"), (6, "Reduced latency by 20%")]:
            with self.subTest(index=index):
                paragraphs = self.paragraphs.copy()
                paragraphs[index] = replacement
                write_docx(self.artifact, paragraphs)
                with self.assertRaisesRegex(DocumentQualityError, "lost or"):
                    validate_export(self.source, self.artifact)
        write_docx(self.artifact, self.paragraphs[:2] + self.paragraphs[4:7] + self.paragraphs[2:4] + self.paragraphs[7:])
        with self.assertRaisesRegex(DocumentQualityError, "lost or reordered"):
            validate_export(self.source, self.artifact)

    def test_rejects_nonempty_fake_docx_and_empty_body(self) -> None:
        self.artifact.write_bytes(b"not an actual DOCX")
        with self.assertRaisesRegex(DocumentQualityError, "Cannot read DOCX"):
            validate_export(self.source, self.artifact)
        write_docx(self.artifact, [""])
        with self.assertRaisesRegex(DocumentQualityError, "no readable"):
            validate_export(self.source, self.artifact)

    def test_critical_punctuation_cannot_be_discarded_by_token_normalization(self) -> None:
        for index, replacement in [(1, "candidate-example.test"), (6, "Reduced latency by 25")]:
            with self.subTest(index=index):
                paragraphs = self.paragraphs.copy()
                paragraphs[index] = replacement
                write_docx(self.artifact, paragraphs)
                with self.assertRaisesRegex(DocumentQualityError, "contact or numeric"):
                    validate_export(self.source, self.artifact)

    def test_rejects_hidden_text_and_small_font(self) -> None:
        write_docx(self.artifact, self.paragraphs, hidden=True)
        with self.assertRaisesRegex(DocumentQualityError, "hidden"):
            validate_export(self.source, self.artifact)
        write_docx(self.artifact, self.paragraphs, size=16)
        with self.assertRaisesRegex(DocumentQualityError, "below"):
            validate_export(self.source, self.artifact)

    def test_hyperlink_target_must_survive_conversion(self) -> None:
        self.source.write_text("[Contact](mailto:candidate@example.test)", encoding="utf-8")
        write_docx(self.artifact, ["Contact"], link="mailto:other@example.test")
        with self.assertRaisesRegex(DocumentQualityError, "hyperlink"):
            validate_export(self.source, self.artifact)
        write_docx(self.artifact, ["Contact"], link="mailto:candidate@example.test")
        self.assertEqual("verified", validate_export(self.source, self.artifact)["checks"]["hyperlink_targets"])

    def test_review_is_explicit_and_invalidated_by_changed_artifact(self) -> None:
        review = {"status": "reviewed", "artifact_sha256": file_sha256(self.artifact), "reviewer": "Codex visual pass",
                  "reviewed_at": "2026-09-22T10:00:00Z", "checks": {key: True for key in ("page_breaks", "overflow", "readability", "blank_pages")}}
        self.assertEqual("reviewed", validate_export(self.source, self.artifact, visual_review=review)["visual_review"]["status"])
        write_docx(self.artifact, self.paragraphs, size=24)
        with self.assertRaisesRegex(DocumentQualityError, "artifact_sha256"):
            validate_export(self.source, self.artifact, visual_review=review)

    def test_docx_page_budget_requires_a_renderer(self) -> None:
        with self.assertRaisesRegex(DocumentQualityError, "renderer-dependent"):
            validate_export(self.source, self.artifact, max_pages=2)

    def test_markdown_tables_and_numbered_lists_preserve_only_visible_text(self) -> None:
        source = "## Skills\n| Name | Level |\n| --- | --- |\n| PHP | Strong |\n1. Delivery\n2. Testing"
        self.source.write_text(source, encoding="utf-8")
        write_docx(self.artifact, ["Skills", "Name", "Level", "PHP", "Strong", "Delivery", "Testing"])
        validate_export(self.source, self.artifact)
        with self.assertRaises(DocumentQualityError):
            markdown_visible_text("[Contact][email]\n[email]: mailto:a@example.test")

    def test_missing_optional_tool_is_an_explicit_error(self) -> None:
        with patch("jobintel.document_quality.shutil.which", return_value=None):
            with self.assertRaisesRegex(DocumentQualityError, "no PDF check was performed"):
                _tool("pdfinfo")
            with self.assertRaisesRegex(DocumentQualityError, "LibreOffice"):
                export_pdf(self.artifact, self.root / "cv.pdf")

    def test_cli_writes_receipt_and_refuses_overwrite(self) -> None:
        with redirect_stdout(StringIO()):
            self.assertEqual(0, main(["validate", "cv.md", "cv.docx", "--receipt", "receipt.json"], root=self.root))
        receipt = json.loads((self.root / "receipt.json").read_text())
        self.assertEqual("not_reviewed", receipt["visual_review"]["status"])
        with redirect_stderr(StringIO()):
            self.assertEqual(1, main(["validate", "cv.md", "cv.docx", "--receipt", "receipt.json"], root=self.root))

    def test_pdf_checks_extracted_pages_text_loss_and_budget_without_optional_tools(self) -> None:
        pdf = self.root / "cv.pdf"
        write_pdf(pdf, ["Candidate PHP engineer"])
        self.source.write_text("Candidate PHP engineer", encoding="utf-8")
        cases = [(["Pages: 1\n", "Candidate PHP engineer\n\f"], 1, None),
                 (["Pages: 2\n", "Candidate PHP\fengineer\f"], 1, "exceeding"),
                 (["Pages: 2\n", "Candidate PHP engineer\f\f"], None, "blank/unreadable"),
                 (["Pages: 1\n", "Candidate engineer\f"], None, "lost or reordered")]
        for outputs, budget, error in cases:
            with self.subTest(outputs=outputs), patch("jobintel.document_quality._tool", side_effect=lambda name: name), patch("jobintel.document_quality._run", side_effect=outputs):
                if error:
                    with self.assertRaisesRegex(DocumentQualityError, error):
                        validate_export(self.source, pdf, max_pages=budget)
                else:
                    self.assertEqual(1, validate_export(self.source, pdf, max_pages=budget)["page_count"])

    def test_pdf_conversion_uses_private_profile_and_refuses_existing_target(self) -> None:
        target = self.root / "cv.pdf"

        def convert(command: list[str]) -> str:
            self.assertIn("--headless", command)
            self.assertTrue(any(part.startswith("-env:UserInstallation=file:") for part in command))
            outdir = Path(command[command.index("--outdir") + 1])
            self.assertNotEqual(target.parent, outdir.parent)
            write_pdf(outdir / "cv.pdf", ["Candidate"])
            return "converted"

        with patch("jobintel.document_quality._tool", return_value="soffice"), patch("jobintel.document_quality._run", side_effect=convert):
            self.assertEqual(target, export_pdf(self.artifact, target))
            saved = target.read_bytes()
            with self.assertRaisesRegex(DocumentQualityError, "new .pdf"):
                export_pdf(self.artifact, target)
            self.assertEqual(saved, target.read_bytes())

    def test_pdf_conversion_retries_transient_windows_profile_cleanup(self) -> None:
        target = self.root / "cv.pdf"
        remove = shutil.rmtree
        attempts = 0

        def convert(command: list[str]) -> str:
            work = Path(command[command.index("--outdir") + 1])
            write_pdf(work / "cv.pdf", ["Candidate"])
            return "converted"

        def remove_after_retry(path: Path) -> None:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                error = OSError(145, "Directory not empty")
                error.winerror = 145
                raise error
            remove(path)

        with patch("jobintel.document_quality._tool", return_value="soffice"), \
             patch("jobintel.document_quality._run", side_effect=convert), \
             patch("jobintel.document_quality.shutil.rmtree", side_effect=remove_after_retry), \
             patch("jobintel.document_quality.time.sleep"):
            self.assertEqual(target, export_pdf(self.artifact, target))
        self.assertEqual(2, attempts)
        self.assertTrue(target.is_file())


class RealPdfQualityTests(unittest.TestCase):
    def setUp(self) -> None:
        try:
            _tool("pdfinfo")
            _tool("pdftotext")
        except DocumentQualityError as exc:
            self.skipTest(str(exc))
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.source = self.root / "cv.md"
        self.source.write_text("Candidate PHP engineer 2020 2026", encoding="utf-8")
        self.pdf = self.root / "cv.pdf"

    def test_real_pdf_extraction_page_budget_and_rendering(self) -> None:
        write_pdf(self.pdf, ["Candidate PHP engineer 2020 2026"])
        self.assertEqual(1, validate_export(self.source, self.pdf, max_pages=1)["page_count"])
        try:
            _tool("pdftoppm")
        except DocumentQualityError:
            return
        receipt = render_pdf_pages(self.pdf, self.root / "pages")
        self.assertEqual(1, len(receipt["pages"]))
        self.assertEqual("not_reviewed", receipt["visual_review"]["status"])
        self.assertTrue(Path(receipt["pages"][0]["path"]).read_bytes().startswith(b"\x89PNG"))

    def test_real_pdf_blank_page_and_over_budget_are_rejected(self) -> None:
        write_pdf(self.pdf, ["Candidate PHP engineer 2020 2026", ""])
        with self.assertRaisesRegex(DocumentQualityError, "blank/unreadable"):
            validate_export(self.source, self.pdf)
        write_pdf(self.pdf, ["Candidate PHP engineer", "2020 2026"])
        with self.assertRaisesRegex(DocumentQualityError, "exceeding the budget"):
            validate_export(self.source, self.pdf, max_pages=1)


if __name__ == "__main__":
    unittest.main()
