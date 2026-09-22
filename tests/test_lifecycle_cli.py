from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import patch

from jobintel.lifecycle_cli import main


class LifecycleCliTests(unittest.TestCase):
    def test_profile_questions_reads_local_config_without_database(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "config/application-profile.yaml").write_text("candidate:\n  notice: TODO_CONFIRM\n", encoding="utf-8")
            output = io.StringIO()
            with patch("jobintel.lifecycle_cli.ApplicationLifecycle", side_effect=AssertionError("must not access MongoDB")) as factory, redirect_stdout(output):
                self.assertEqual(main(["profile-questions"], root=root), 0)
                factory.assert_not_called()
            self.assertEqual(json.loads(output.getvalue())["questions"], [
                {"field": "candidate.notice", "value": "TODO_CONFIRM", "status": "needs_confirmation"}])

    def test_submission_routes_explicit_confirmation_and_exact_artifacts(self):
        with patch("jobintel.lifecycle_cli.ApplicationLifecycle") as factory, redirect_stdout(io.StringIO()):
            factory.return_value.record_submission.return_value = {"ok": True}
            result = main(["record-submission", "job", "--submission-id", "s1", "--sent-on", "2026-09-01",
                           "--artifact", "cv.pdf", "--artifact", "letter.pdf", "--confirm-sent", "--channel", "referral"])
            self.assertEqual(result, 0)
            kwargs = factory.return_value.record_submission.call_args.kwargs
            self.assertTrue(kwargs["confirmed"])
            self.assertEqual(kwargs["artifacts"], [Path("cv.pdf"), Path("letter.pdf")])

    def test_note_file_preserves_crlf_and_paragraph_breaks(self):
        with tempfile.TemporaryDirectory() as temporary:
            note = Path(temporary) / "note.txt"
            text = "Grazie.\r\n\r\nNon procederemo.\r\n"
            note.write_bytes(text.encode("utf-8"))
            with patch("jobintel.lifecycle_cli.ApplicationLifecycle") as factory, redirect_stdout(io.StringIO()):
                factory.return_value.record_event.return_value = {"ok": True}
                result = main(["record-event", "job", "--submission-id", "s1", "--event-id", "r1", "--kind", "rejection",
                               "--occurred-on", "2026-09-05", "--note-file", str(note), "--note-origin", "employer_message"])
                self.assertEqual(result, 0)
                self.assertEqual(factory.return_value.record_event.call_args.kwargs["note"], text)

    def test_validation_failure_returns_error_without_traceback(self):
        output = io.StringIO()
        with patch("jobintel.lifecycle_cli.ApplicationLifecycle", side_effect=RuntimeError("MongoDB unavailable")), redirect_stderr(output):
            self.assertEqual(main(["report"]), 2)
        self.assertIn("MongoDB unavailable", output.getvalue())

    def test_report_returns_json_and_no_mutation(self):
        output = io.StringIO()
        with patch("jobintel.lifecycle_cli.ApplicationLifecycle") as factory, redirect_stdout(output):
            factory.return_value.report.return_value = {"summary": {"submitted": 0}}
            self.assertEqual(main(["report", "--as-of", "2026-09-01"]), 0)
            factory.return_value.record_event.assert_not_called()
        self.assertEqual(json.loads(output.getvalue())["summary"]["submitted"], 0)

    def test_publish_requires_named_approval_argument(self):
        with redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main(["publish-draft", "job", "--kind", "answers", "--draft", "draft.json"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
