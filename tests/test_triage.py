from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import yaml

from jobintel.triage import should_skip_model, triage_directory, write_triage


def write_vacancy(directory: Path, *, title: str, body: str = "") -> None:
    directory.mkdir(parents=True)
    (directory / "meta.yaml").write_text(
        yaml.safe_dump(
            {
                "id": "vacancy-1",
                "title": title,
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )
    (directory / "job.md").write_text(body, encoding="utf-8")


class TriageTests(unittest.TestCase):
    def test_sre_title_is_high_confidence_model_skip(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "vacancy"
            write_vacancy(directory, title="Site Reliability Engineer")

            result = triage_directory(directory)

            self.assertTrue(result["skip_model"])
            self.assertEqual("sre", result["reason"])
            self.assertEqual("high", result["confidence"])
            self.assertEqual(["sre"], result["matched_title_rules"])

    def test_sre_body_only_match_does_not_skip_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "vacancy"
            write_vacancy(
                directory,
                title="Backend Engineer",
                body="Collaborate with the SRE team on incident response.",
            )

            result = triage_directory(directory)

            self.assertFalse(result["skip_model"])
            self.assertEqual("sre", result["reason"])
            self.assertEqual("medium", result["confidence"])
            self.assertEqual([], result["matched_title_rules"])

    def test_written_sre_triage_skips_model(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "vacancy"
            write_vacancy(directory, title="SRE")

            write_triage(directory)

            self.assertTrue(should_skip_model(directory))


if __name__ == "__main__":
    unittest.main()
