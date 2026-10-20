"""Synthetic, fixed-time behavior oracle for the personal-rule extraction."""
from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import asdict
from datetime import date, datetime, timedelta
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel.catalog_data import CatalogSnapshot, load_catalog_snapshot
from jobintel.cli import main
from jobintel.models import NormalizedJob
from jobintel.prefilter import CompanyRetryRule, prefilter_job
from jobintel.registry import Registry
from jobintel.triage import should_skip_model, triage_directory, write_triage
from jobintel.workflow_api import queue_items
from scripts.archive_jobs import _eligible_document, eligible


ROOT = Path(__file__).resolve().parents[1]
CORPUS = yaml.safe_load((ROOT / "tests/fixtures/selection-baseline.yaml").read_text(encoding="utf-8"))
REFERENCE_TIME = datetime.fromisoformat(CORPUS["reference_time"].replace("Z", "+00:00"))


class FixedDateTime(datetime):
    current = REFERENCE_TIME

    @classmethod
    def now(cls, tz=None):
        return cls.current.astimezone(tz) if tz else cls.current.replace(tzinfo=None)


class SelectionBaselineTests(unittest.TestCase):
    def test_prefilter_decisions_categories_reasons_and_precedence(self) -> None:
        for case in CORPUS["prefilter"]:
            with self.subTest(case=case["id"]):
                job = NormalizedJob(**(CORPUS["job_defaults"] | case["job"]))
                retry = case.get("retry")
                rules = () if retry is None else (CompanyRetryRule(
                    company=retry["company"], allow_after=date.fromisoformat(retry["allow_after"]),
                    reason=retry["reason"],
                ),)
                result = prefilter_job(job, now=REFERENCE_TIME, company_retry_rules=rules)
                self.assertEqual(case["expected"], asdict(result) if result else None)

    def test_triage_decisions_order_and_repeat_preserve_receipt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch("jobintel.triage.datetime", FixedDateTime):
            for case in CORPUS["triage"]:
                with self.subTest(case=case["id"]):
                    directory = Path(temporary) / case["id"]
                    directory.mkdir()
                    (directory / "meta.yaml").write_text(yaml.safe_dump({"id": case["id"], "title": case["title"]}), encoding="utf-8")
                    (directory / "job.md").write_text(case.get("body", ""), encoding="utf-8")
                    result = triage_directory(directory)
                    self.assertEqual(case["expected"], {key: result[key] for key in case["expected"]})
                    self.assertEqual("2026-07-23T12:00:00Z", result["triaged_at"])
                    self.assertEqual(1, result["schema_version"])
                    self.assertEqual(case["id"], result["vacancy_id"])
                    self.assertTrue(result["triage_version"])
                    first = write_triage(directory)
                    before = (directory / "triage.yaml").read_bytes()
                    with patch.object(FixedDateTime, "current", REFERENCE_TIME + timedelta(days=1)):
                        second = write_triage(directory)
                    self.assertEqual("2026-07-23T12:00:00Z", first["triaged_at"])
                    self.assertEqual(first["triaged_at"], second["triaged_at"])
                    self.assertEqual(before, (directory / "triage.yaml").read_bytes())
                    self.assertEqual(case["expected"]["skip_model"], should_skip_model(directory))

    def test_file_snapshot_pending_and_skipped_archive_consume_same_corpus(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, patch("jobintel.triage.datetime", FixedDateTime):
            project = Path(temporary)
            registry_root = project / "registry"
            (project / "config").mkdir()
            (project / "config/selection-policy.yaml").write_bytes((ROOT / "config/selection-policy.yaml").read_bytes())
            (project / "config/codex-workflows.yaml").write_bytes((ROOT / "config/codex-workflows.yaml").read_bytes())
            profile = registry_root / "candidate/match-profile.md"
            profile.parent.mkdir(parents=True)
            profile.write_text("Synthetic candidate evidence: Go backend engineering.", encoding="utf-8")
            documents = {}
            directories = {}
            for case in CORPUS["queue"]:
                registry = Registry(registry_root, clock=lambda: REFERENCE_TIME, id_factory=lambda: case["id"])
                result = registry.upsert(NormalizedJob(
                    "synthetic", case["id"], f"https://example.test/{case['id']}", case["title"],
                    "Example", case.get("body", "Build Go services."), analysis_priority=case["priority"],
                ))
                if case["status"] != "found":
                    registry.update_status(case["id"], case["status"])
                directory = registry_root / "jobs" / result.directory
                directories[case["id"]] = directory
                triage = write_triage(directory)
                meta = yaml.safe_load((directory / "meta.yaml").read_text(encoding="utf-8"))
                document = {"meta": meta, "job_text": (directory / "job.md").read_text(encoding="utf-8"), "triage": triage, "match": None}
                documents[directory.name] = document
                expected_archive = case["id"] == "title"
                self.assertEqual(expected_archive, eligible(directory, "skipped", 65, 7))
                self.assertEqual(expected_archive, _eligible_document(meta, document, "skipped", 65, 7))
            expected = [case["id"] for case in CORPUS["queue"] if case["expected"]]
            file_snapshot = load_catalog_snapshot(registry_root)
            rows = queue_items("analyze", project, registry_root, [profile], _snapshot=file_snapshot)
            self.assertEqual(expected, [row.vacancy.vacancy_id for row in rows])
            snapshot = CatalogSnapshot(file_snapshot.vacancies, documents)
            with patch("jobintel.workflow_api.should_skip_model", side_effect=AssertionError("snapshot escaped to file reader")):
                rows = queue_items("analyze", project, registry_root, [profile], _snapshot=snapshot)
            self.assertEqual(expected, [row.vacancy.vacancy_id for row in rows])
            output = StringIO()
            with redirect_stdout(output), patch("jobintel.cli.load_env", return_value={}):
                result = main(["pending", "analyze", "all", "--workflow", "analyze", "--registry", str(registry_root), "--profile", str(profile)])
            self.assertEqual(0, result, output.getvalue())
            self.assertEqual([str(directories[key]) for key in expected], output.getvalue().splitlines())
