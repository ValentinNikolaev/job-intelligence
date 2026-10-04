from __future__ import annotations

import hashlib
import json
import copy
import tempfile
import unittest
from contextlib import nullcontext, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from jobintel import storage_bridge as bridge
from jobintel.applications import (
    ApplicationError,
    ApplicationGenerator,
    CodexApplicationDraftClient,
    HostMarkdownDocxConverter,
    _reuse_cv_preview,
    resolve_job_directories,
    validate_application_draft,
)
from jobintel.cli import _preflight_preparation, main
from tests.test_applications import FakeConverter, application_payload, write_quality_contract


class _Admin:
    def command(self, name):
        assert name == "hello"
        return {"setName": "rs0"}


class _Client:
    admin = _Admin()


class MongoFixtureStore:
    """Small in-memory MongoDB-shaped fixture; no registry YAML is ever created."""

    def __init__(self, directory: str, *, hard_rejection: bool = False) -> None:
        now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        self.document = {
            "_id": "fixture-vacancy",
            "revision": 1,
            "directory": directory,
            "scope": "jobs",
            "meta": {
                "id": "fixture-vacancy",
                "title": "Senior Backend Engineer",
                "company": "Fixture Company",
                "status": "analyzed",
                "discovered_at": now,
                "sources": [{"source": "fixture", "source_job_id": "1", "url": "https://example.test/1"}],
            },
            "job_text": "Build reliable PHP and Go backend services.",
            "company_text": "A fixture product company.",
            "match": {
                "score": 72,
                "recommendation": "possible_match",
                "hard_rejection": hard_rejection,
            },
        }
        self.documents = [self.document]
        self.client = _Client()
        self.records = {}

    def get_by_directory(self, directory, *, scope="jobs"):
        if scope != "jobs":
            return None
        return next((document for document in self.documents if document["directory"] == directory), None)

    def list_vacancies(self, *, scope="jobs", include_archived=False):
        return list(self.documents) if scope == "jobs" else []

    def get(self, collection, key):
        if collection == "storage_schema" and key == "operational":
            return {"schema_version": 1}
        return self.records.get((collection, key))

    def put(self, collection, key, value, *, expected_revision=0):
        self.records[(collection, key)] = {"revision": expected_revision + 1, **value}

    def lease(self, owner):
        return nullcontext()

    def transaction(self):
        return nullcontext()

    @property
    def in_vacancy_batch(self):
        return False


class MongoApplicationSnapshotTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.registry = self.root / "registry"
        (self.registry / "candidate").mkdir(parents=True)
        (self.registry / "candidate" / "match-profile.md").write_text("Verified candidate evidence.", encoding="utf-8")
        (self.root / "config").mkdir()
        (self.root / "config" / "data-services.yaml").write_text(
            "storage:\n  backend: mongodb\n  cutover_verified: true\n", encoding="utf-8"
        )
        (self.root / "config" / "codex-workflows.yaml").write_text(
            "schema_version: 1\nprepare_min_score: 65\nprepare_max_age_days: 14\nprepare_batch_size: 10\n"
            "model_profiles:\n  fixture:\n    model: fixture\n    reasoning: low\n    model_label: fixture:model\n"
            "workflows:\n  prepare:\n    default_profile: fixture\n    allowed_profiles: [fixture]\n"
            "  analyze:\n    default_profile: fixture\n    allowed_profiles: [fixture]\n",
            encoding="utf-8",
        )
        (self.root / "sources").mkdir()
        self.directory = self.registry / "jobs" / "mongo-only"
        self.store = MongoFixtureStore(self.directory.name)

    def _draft(self) -> Path:
        draft = self.root / ".codex-work" / "application" / self.directory.name
        draft.mkdir(parents=True)
        (draft / "cv.md").write_text(application_payload()["cv_markdown"], encoding="utf-8")
        write_quality_contract(draft, include_cover_letter=False)
        return draft

    def test_legacy_file_selector_remains_supported(self) -> None:
        legacy = self.registry / "jobs" / "legacy"
        legacy.mkdir(parents=True)
        (legacy / "meta.yaml").write_text("id: legacy-id\n", encoding="utf-8")
        with patch("jobintel.storage_bridge.get_store", return_value=None):
            self.assertEqual([legacy.resolve()], resolve_job_directories(self.registry, "legacy-id"))

    def test_mongo_selector_validation_preview_and_cv_publication_use_snapshot(self) -> None:
        draft = self._draft()
        with patch("jobintel.storage_bridge.get_store", return_value=self.store):
            self.assertEqual([self.directory], resolve_job_directories(self.registry, "fixture-vacancy"))
            self.assertFalse(self.directory.exists())
            validate_application_draft(self.directory, draft, document="cv")
            snapshots = list((self.root / ".codex-work" / "vacancy-snapshots" / self.directory.name).glob("*/meta.yaml"))
            self.assertEqual(1, len(snapshots))
            self.assertFalse(self.directory.exists())

            converter = HostMarkdownDocxConverter(self.root, script_path=self.root / "converter.ps1", options_path=self.root / "options.json", powershell="pwsh")
            (self.root / "converter.ps1").write_text("fixture", encoding="utf-8")
            (self.root / "options.json").write_text("{}", encoding="utf-8")
            preview = converter.preview_directory(draft / "cv.md")
            preview.mkdir(parents=True)
            canonical_cv = (draft / "cv.md").read_text(encoding="utf-8").strip().encode("utf-8") + b"\n"
            (preview / "cv.md").write_bytes(canonical_cv)
            artifact = preview / "cv.docx"
            artifact.write_bytes(b"preview")
            (preview / "receipt.json").write_text(json.dumps({
                "source_sha256": hashlib.sha256(canonical_cv).hexdigest(),
                "docx_sha256": hashlib.sha256(artifact.read_bytes()).hexdigest(),
                "page_count": 2, "rendered_pages": 2, "experience_bullets": 10,
            }), encoding="utf-8")
            staged = self.root / ".codex-work" / "staged" / "cv.md"
            staged.parent.mkdir(parents=True)
            staged.write_bytes(canonical_cv)
            self.assertTrue(_reuse_cv_preview(draft / "cv.md", staged, staged.with_suffix(".docx"), converter))

            seen_before_publication = []
            class CheckingConverter(FakeConverter):
                def convert(inner, source, target):
                    seen_before_publication.append(self.directory.exists())
                    super().convert(source, target)
            generator = ApplicationGenerator(
                self.registry, [self.registry / "candidate" / "match-profile.md"],
                self.root / "prompt.md", CodexApplicationDraftClient(draft, model="fixture:model", document="cv"),
                CheckingConverter(), document="cv", allow_legacy_drafts=True,
            )
            (self.root / "prompt.md").write_text("Fixture prompt", encoding="utf-8")
            self.assertEqual("prepared", generator.generate_directory(self.directory, force=True).status)
        self.assertEqual([False], seen_before_publication)
        self.assertTrue((self.directory / "application" / "cv.md").is_file())

    def test_preflight_reports_missing_selector_and_slotcatalog_hard_rejection_before_drafting(self) -> None:
        args = SimpleNamespace(arguments=["missing"], workflow="prepare", model_profile=None, document="cv", profile=None,
                               allow_low_score_cv_refresh=False, bypass_hard_rejection_cv_refresh=False)
        with patch("jobintel.storage_bridge.get_store", return_value=self.store):
            with self.assertRaisesRegex(ApplicationError, "not found in configured storage"):
                _preflight_preparation(args, {}, self.root, self.registry)
        blocked = MongoFixtureStore("slotcatalog-senior-php-developer", hard_rejection=True)
        blocked.document["meta"]["company"] = "SlotCatalog"
        args.arguments = ["fixture-vacancy"]
        with patch("jobintel.storage_bridge.get_store", return_value=blocked):
            with self.assertRaisesRegex(ValueError, "slotcatalog-senior-php-developer: match has hard_rejection: true"):
                _preflight_preparation(args, {}, self.root, self.registry)
        self.assertFalse(self.directory.exists())

    def test_prepare_preflight_cli_returns_machine_readable_missing_selector_reason(self) -> None:
        output = StringIO()
        with patch("jobintel.storage_bridge.get_store", return_value=self.store), redirect_stdout(output):
            result = main([
                "prepare-preflight", "missing", "--registry", str(self.registry),
                "--workflow", "prepare", "--document", "cv",
            ])
        self.assertEqual(2, result)
        payload = json.loads(output.getvalue())
        self.assertFalse(payload["ok"])
        self.assertIn("vacancy not found in configured storage: missing", payload["errors"][0])

    def test_five_mongo_only_cv_drafts_preflight_validate_and_publish_independently(self) -> None:
        directories = [f"mongo-cv-{number}" for number in range(1, 6)]
        self.store.documents = []
        for number, name in enumerate(directories, start=1):
            document = copy.deepcopy(self.store.document)
            document["_id"] = f"fixture-{number}"
            document["directory"] = name
            document["meta"]["id"] = f"fixture-{number}"
            self.store.documents.append(document)
        self.store.document = self.store.documents[0]
        args = SimpleNamespace(arguments=[f"fixture-{number}" for number in range(1, 6)], workflow="prepare", model_profile=None,
                               document="cv", profile=None, allow_low_score_cv_refresh=False)
        with patch("jobintel.storage_bridge.get_store", return_value=self.store), patch("jobintel.cli._analysis_is_current", return_value=True):
            report = _preflight_preparation(args, {}, self.root, self.registry)
            self.assertEqual(5, len(report["vacancies"]))
            for name in directories:
                directory = self.registry / "jobs" / name
                draft = self.root / ".codex-work" / "application" / name
                draft.mkdir(parents=True)
                (draft / "cv.md").write_text(application_payload()["cv_markdown"], encoding="utf-8")
                write_quality_contract(draft, include_cover_letter=False)
                validate_application_draft(directory, draft, document="cv")
                prompt = self.root / f"{name}-prompt.md"
                prompt.write_text("Fixture prompt", encoding="utf-8")
                generator = ApplicationGenerator(
                    self.registry, [self.registry / "candidate" / "match-profile.md"], prompt,
                    CodexApplicationDraftClient(draft, model="fixture:model", document="cv"),
                    FakeConverter(), document="cv", allow_legacy_drafts=True,
                )
                self.assertEqual("prepared", generator.generate_directory(directory, force=True).status)
                self.assertTrue((directory / "application" / "cv.md").is_file())


if __name__ == "__main__":
    unittest.main()
