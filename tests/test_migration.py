from __future__ import annotations

import contextlib
import tempfile
import unittest
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import yaml

from jobintel.migration import (
    Evidence,
    Observation,
    _direct_artifacts,
    _package_locator,
    application_id,
    build_plan,
    export_applications,
    import_plan,
    project_vacancy_history,
    reconcile,
    source_identity_id,
    status_event_id,
    submission_confirmation_id,
)


class FakeStore:
    def __init__(self) -> None:
        self.data: dict[str, dict[str, dict]] = {}

    def get(self, collection: str, key: str):
        return self.data.get(collection, {}).get(key)

    def list(self, collection: str, *args, **kwargs):
        del args, kwargs
        return list(self.data.get(collection, {}).values())

    def put(self, collection: str, key: str, payload: dict, *, expected_revision: int = 0):
        rows = self.data.setdefault(collection, {})
        current = rows.get(key)
        actual = int(current.get("revision", 0)) if current else 0
        if actual != expected_revision:
            raise ValueError("revision conflict")
        stored = {"_id": key, **payload, "revision": actual + 1, "writer_fence": 7, "updated_at": "now"}
        rows[key] = stored
        return stored

    def lease(self, owner: str):
        del owner
        return contextlib.nullcontext()

    def transaction(self):
        return contextlib.nullcontext()


def vacancy(vacancy_id: str = "vac-1", *, status: str = "applied") -> dict:
    return {
        "_id": vacancy_id,
        "directory": "2026-01-01_acme_engineer",
        "revision": 4,
        "meta": {
            "id": vacancy_id,
            "company": "Acme",
            "title": "Engineer",
            "status": status,
            "location": "Italy",
            "remote": True,
            "sources": [{"source": "manual", "source_job_id": "job-1", "url": "https://example.test/job"}],
            "status_history": [
                {"status": "found", "changed_at": "2026-01-01T10:00:00Z"},
                {"status": "applied", "changed_at": "2026-01-02T10:00:00Z"},
            ],
        },
    }


class MigrationProjectionTests(unittest.TestCase):
    def test_ids_use_exact_stable_prefixes(self) -> None:
        event = status_event_id("vac-1", "2026-01-02T10:00:00Z", "found", "applied")
        expected = uuid.uuid5(
            uuid.NAMESPACE_URL,
            "\0".join(("jobintel:status-event:v1", "vac-1", "2026-01-02T10:00:00Z", "found", "applied")),
        )
        self.assertEqual(str(expected), event)
        self.assertEqual(application_id("vac-1", event), application_id("vac-1", event))

    def test_applied_time_is_unknown_without_effective_date(self) -> None:
        manual = [{
            "vacancy_id": "vac-1", "changed_at": "2026-01-02T10:00:00Z",
            "from_status": "found", "to_status": "applied", "reason": "submitted",
        }]
        applications, events, issues = project_vacancy_history(vacancy(), manual)
        self.assertIsNone(applications[0]["applied_at_effective"])
        self.assertEqual("2026-01-02T10:00:00Z", applications[0]["applied_at_recorded"])
        self.assertEqual("confirmed", applications[0]["confirmation"]["state"])
        self.assertIsNone(applications[0]["channel"])
        self.assertFalse(issues)
        self.assertEqual(applications[0]["application_id"], events[1]["application_id"])

    def test_application_channel_requires_submission_evidence(self) -> None:
        manual = [{
            "vacancy_id": "vac-1", "changed_at": "2026-01-02T10:00:00Z",
            "from_status": "found", "to_status": "applied", "application_channel": "employer portal",
        }]
        applications, _, _ = project_vacancy_history(vacancy(), manual)
        self.assertEqual("employer portal", applications[0]["channel"])

    def test_package_locator_links_direct_folder_or_archive_at_revision(self) -> None:
        direct = Observation(
            directory="job-a", scope="jobs", archived=False, archive_category=None, meta={},
            meta_evidence=Evidence("registry/jobs/job-a/meta.yaml", "0" * 64, 1),
            artifacts=[{"path": "registry/jobs/job-a/application/cv.md"}],
        )
        archived = Observation(
            directory="job-b", scope="jobs", archived=True, archive_category="stale", meta={},
            meta_evidence=Evidence("archives/stale/2026-01-01.zip!job-b/meta.yaml", "0" * 64, 1),
            artifacts=[{"path": "archives/stale/2026-01-01.zip!job-b/application/cv.md"}],
        )
        self.assertEqual(
            "https://github.com/ValentinNikolaev/job-intelligence/tree/deadbeef/registry/jobs/job-a/application",
            _package_locator(direct, "deadbeef"),
        )
        self.assertEqual(
            "https://github.com/ValentinNikolaev/job-intelligence/blob/deadbeef/archives/stale/2026-01-01.zip",
            _package_locator(archived, "deadbeef"),
        )

    def test_manual_status_keeps_recorded_time_without_inventing_effective_time(self) -> None:
        record = vacancy(status="rejected")
        record["meta"]["status_history"].append(
            {"status": "rejected", "changed_at": "2026-01-03T10:00:00Z"}
        )
        manual = [{
            "vacancy_id": "vac-1", "changed_at": "2026-01-03T10:00:00Z",
            "from_status": "applied", "to_status": "rejected", "reason": "employer declined",
        }]
        _, events, _ = project_vacancy_history(record, manual)
        rejection = events[-1]
        self.assertIsNone(rejection["effective_at"])
        self.assertEqual("2026-01-03T10:00:00Z", rejection["recorded_at"])

    def test_explicit_actual_date_and_contradiction_are_preserved(self) -> None:
        manual = [{
            "vacancy_id": "vac-1", "changed_at": "2026-01-02T10:00:00Z",
            "from_status": "found", "to_status": "applied", "reason": "workflow status",
            "note": "Actual application date reported by user: 2026-01-01; external form not submitted",
        }]
        applications, _, issues = project_vacancy_history(vacancy(), manual)
        self.assertEqual("2026-01-01", applications[0]["applied_at_effective"])
        self.assertEqual("needs_review", applications[0]["confirmation"]["state"])
        self.assertEqual("contradictory_applied_event", issues[0]["code"])

    def test_repeated_applications_have_independent_status_windows(self) -> None:
        record = vacancy(status="interview")
        record["meta"]["status_history"].extend(
            [
                {"status": "rejected", "changed_at": "2026-01-03T10:00:00Z"},
                {"status": "applied", "changed_at": "2026-02-01T10:00:00Z"},
                {"status": "interview", "changed_at": "2026-02-02T10:00:00Z"},
            ]
        )
        manual = [
            {"vacancy_id": "vac-1", "changed_at": "2026-01-02T10:00:00Z", "from_status": "found", "to_status": "applied"},
            {"vacancy_id": "vac-1", "changed_at": "2026-02-01T10:00:00Z", "from_status": "rejected", "to_status": "applied"},
        ]
        applications, events, _ = project_vacancy_history(record, manual)
        self.assertEqual(["rejected", "interview"], [item["current_status"] for item in applications])
        self.assertNotEqual(applications[0]["application_id"], applications[1]["application_id"])
        self.assertEqual(applications[0]["application_id"], events[2]["application_id"])
        self.assertEqual(applications[1]["application_id"], events[-1]["application_id"])

    def test_same_second_transitions_follow_history_not_uuid_order(self) -> None:
        record = vacancy(status="applied")
        stamp = "2026-02-01T10:00:00Z"
        record["meta"]["status_history"] = [
            {"status": "found", "changed_at": "2026-01-01T10:00:00Z"},
            {"status": "applied", "changed_at": stamp},
            {"status": "interview", "changed_at": stamp},
            {"status": "applied", "changed_at": stamp},
        ]
        manual = [
            {"vacancy_id": "vac-1", "changed_at": stamp, "from_status": "found", "to_status": "applied"},
            {"vacancy_id": "vac-1", "changed_at": stamp, "from_status": "applied", "to_status": "interview"},
            {"vacancy_id": "vac-1", "changed_at": stamp, "from_status": "interview", "to_status": "applied"},
        ]
        applications, events, _ = project_vacancy_history(record, manual)
        self.assertEqual(["found", "applied", "interview", "applied"], [event["status"] for event in events])
        self.assertEqual(["interview", "applied"], [item["current_status"] for item in applications])
        self.assertEqual(applications[0]["application_id"], events[2]["application_id"])
        self.assertEqual(applications[1]["application_id"], events[3]["application_id"])

    def test_completion_reason_is_scoped_to_each_attempt(self) -> None:
        record = vacancy(status="rejected")
        record["meta"]["status_history"].extend(
            [
                {"status": "rejected", "changed_at": "2026-01-03T10:00:00Z"},
                {"status": "applied", "changed_at": "2026-02-01T10:00:00Z"},
                {"status": "rejected", "changed_at": "2026-02-03T10:00:00Z"},
            ]
        )
        manual = [
            {"vacancy_id": "vac-1", "changed_at": "2026-01-02T10:00:00Z", "from_status": "found", "to_status": "applied"},
            {"vacancy_id": "vac-1", "changed_at": "2026-01-03T10:00:00Z", "from_status": "applied", "to_status": "rejected", "reason": "first reason"},
            {"vacancy_id": "vac-1", "changed_at": "2026-02-01T10:00:00Z", "from_status": "rejected", "to_status": "applied"},
            {"vacancy_id": "vac-1", "changed_at": "2026-02-03T10:00:00Z", "from_status": "applied", "to_status": "rejected", "reason": "second reason"},
        ]
        applications, events, _ = project_vacancy_history(record, manual)
        export = export_applications(
            {"collections": {"applications": applications, "status_events": events}}
        )
        by_id = {item["application_id"]: item for item in export["applications"]}
        self.assertEqual("first reason", by_id[applications[0]["application_id"]]["completion_reason"])
        self.assertEqual("second reason", by_id[applications[1]["application_id"]]["completion_reason"])

    def test_explicit_submission_confirmation_creates_no_synthetic_status_event(self) -> None:
        record = vacancy(status="interview")
        record["meta"]["status_history"] = [
            {"status": "found", "changed_at": "2026-01-01T10:00:00Z"},
            {"status": "interview", "changed_at": "2026-01-05T10:00:00Z"},
        ]
        record["submission_confirmation"] = {
            "vacancy_id": "vac-1",
            "recorded_at": "2026-09-21T22:55:55Z",
            "submitted_at": None,
            "actor": "user",
            "source": "codex_user_confirmation",
            "note": "Confirmed by user",
        }
        applications, events, issues = project_vacancy_history(record, [])

        confirmation_id = submission_confirmation_id("vac-1", "2026-09-21T22:55:55Z")
        self.assertEqual(1, len(applications))
        self.assertEqual(application_id("vac-1", confirmation_id), applications[0]["application_id"])
        self.assertIsNone(applications[0]["applied_event_id"])
        self.assertEqual(confirmation_id, applications[0]["submission_confirmation_id"])
        self.assertIsNone(applications[0]["applied_at_effective"])
        self.assertEqual("2026-09-21T22:55:55Z", applications[0]["applied_at_recorded"])
        self.assertEqual("interview", applications[0]["current_status"])
        self.assertEqual(["found", "interview"], [event["status"] for event in events])
        self.assertIsNone(events[0]["application_id"])
        self.assertEqual(applications[0]["application_id"], events[1]["application_id"])
        self.assertFalse(issues)

    def test_confirmation_attempt_survives_later_reapplication(self) -> None:
        record = vacancy(status="applied")
        reapplied_at = "2026-09-21T22:55:55Z"
        record["meta"]["status_history"] = [
            {"status": "found", "changed_at": "2026-01-01T10:00:00Z"},
            {"status": "interview", "changed_at": "2026-01-05T10:00:00Z"},
            {"status": "rejected", "changed_at": "2026-01-06T10:00:00Z"},
            {"status": "applied", "changed_at": reapplied_at},
        ]
        record["submission_confirmation"] = {
            "vacancy_id": "vac-1",
            "recorded_at": reapplied_at,
            "submitted_at": None,
            "actor": "user",
            "source": "codex_user_confirmation",
            "note": "Earlier application confirmed by user",
        }
        manual = [{
            "vacancy_id": "vac-1", "changed_at": reapplied_at,
            "from_status": "rejected", "to_status": "applied", "reason": "reapplied",
        }]
        applications, events, issues = project_vacancy_history(record, manual)

        self.assertEqual(2, len(applications))
        confirmation_app, reapplied_app = applications
        self.assertEqual("rejected", confirmation_app["current_status"])
        self.assertEqual("applied", reapplied_app["current_status"])
        self.assertEqual(
            [None, confirmation_app["application_id"], confirmation_app["application_id"], reapplied_app["application_id"]],
            [event["application_id"] for event in events],
        )
        self.assertFalse(issues)


class MigrationPlanTests(unittest.TestCase):
    def test_direct_artifact_git_inventory_uses_nul_for_non_ascii_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory = root / "registry" / "jobs" / "laravel-розробник"
            directory.mkdir(parents=True)
            relative = "registry/jobs/laravel-розробник/application/резюме.md"
            completed = type("Completed", (), {"returncode": 0, "stdout": relative + "\0"})()
            with patch("jobintel.migration.subprocess.run", return_value=completed) as run, patch(
                "jobintel.migration._repo_bytes", return_value=b"cv"
            ):
                artifacts = _direct_artifacts(root, directory)
        self.assertEqual(relative, artifacts[0]["path"])
        self.assertIn("-rz", run.call_args.args[0])

    def test_plan_retains_uuid_collision_as_ambiguous_identity(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "registry" / "jobs").mkdir(parents=True)
            (root / "registry" / "rejected").mkdir()
            (root / "archives" / "stale").mkdir(parents=True)
            first = vacancy("vac-1")
            second = vacancy("vac-2")
            for meta, name in ((first["meta"], "one"), (second["meta"], "two")):
                directory = root / "registry" / "jobs" / name
                directory.mkdir()
                (directory / "meta.yaml").write_text(yaml.safe_dump(meta, sort_keys=False), encoding="utf-8")
                (directory / "job.md").write_text("job", encoding="utf-8")
            log = {"schema_version": 1, "events": []}
            (root / "registry" / "manual-status-log.yaml").write_text(yaml.safe_dump(log), encoding="utf-8")
            with patch("jobintel.migration._git_revision", return_value="abc"), patch(
                "jobintel.migration._direct_artifacts", return_value=[]
            ):
                plan = build_plan(root)
        identity = next(item for item in plan["collections"]["source_identities"] if item["source"] == "manual")
        self.assertEqual(source_identity_id("manual", "job-1"), identity["_id"])
        self.assertTrue(identity["ambiguous"])
        self.assertEqual(["vac-1", "vac-2"], identity["vacancy_ids"])
        self.assertEqual(1, plan["manifest"]["issue_counts"]["ambiguous_source_identity"])

    def test_prefilter_document_uses_runtime_vacancy_wrapper(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "registry" / "jobs").mkdir(parents=True)
            rejected = root / "registry" / "rejected" / "filtered"
            rejected.mkdir(parents=True)
            (root / "archives").mkdir()
            meta = {
                "schema_version": 1, "source": "feed", "source_job_id": "42",
                "source_url": "https://example.test/42", "company": "Acme", "title": "Other",
                "rejection_reason": "not relevant", "updated_at": "2026-01-01T00:00:00Z",
            }
            (rejected / "meta.yaml").write_text(yaml.safe_dump(meta), encoding="utf-8")
            (rejected / "job.md").write_text("description", encoding="utf-8")
            with patch("jobintel.migration._git_revision", return_value="abc"):
                plan = build_plan(root)
        document = plan["collections"]["prefilter_rejections"][0]
        self.assertEqual("rejected", document["scope"])
        self.assertEqual("filtered", document["directory"])
        self.assertEqual(meta, document["meta"])
        self.assertNotIn("latest", document)

    def test_unreadable_archive_blocks_plan(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "registry" / "jobs").mkdir(parents=True)
            (root / "registry" / "rejected").mkdir()
            archive = root / "archives" / "stale" / "broken.zip"
            archive.parent.mkdir(parents=True)
            archive.write_bytes(b"not a zip")
            log = {"schema_version": 1, "events": [{
                "vacancy_id": "confirmed-missing", "changed_at": "2026-01-02T10:00:00Z",
                "from_status": "found", "to_status": "applied",
            }]}
            (root / "registry" / "manual-status-log.yaml").write_text(
                yaml.safe_dump(log), encoding="utf-8"
            )
            with patch("jobintel.migration._git_revision", return_value="abc"):
                plan = build_plan(root)
        self.assertTrue(plan["manifest"]["blocked"])
        self.assertEqual(1, plan["manifest"]["issue_counts"]["invalid_archive"])
        self.assertEqual(1, plan["manifest"]["issue_counts"]["confirmed_application_without_vacancy"])

    def test_archive_scope_retains_only_confirmed_application_vacancy(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "registry" / "jobs").mkdir(parents=True)
            (root / "registry" / "rejected").mkdir()
            archive_path = root / "archives" / "stale" / "old.zip"
            archive_path.parent.mkdir(parents=True)
            confirmed = vacancy("confirmed")
            excluded = vacancy("excluded")
            excluded["meta"]["sources"][0]["source_job_id"] = "excluded-job"
            with zipfile.ZipFile(archive_path, "w") as archive:
                for name, record in (("confirmed", confirmed), ("excluded", excluded)):
                    archive.writestr(f"{name}/meta.yaml", yaml.safe_dump(record["meta"]))
                    archive.writestr(f"{name}/job.md", f"{name} job")
                    archive.writestr(f"{name}/application/cv.md", f"{name} cv")
            log = {"schema_version": 1, "events": [{
                "vacancy_id": "confirmed", "changed_at": "2026-01-02T10:00:00Z",
                "from_status": "found", "to_status": "applied", "reason": "submitted",
            }]}
            (root / "registry" / "manual-status-log.yaml").write_text(
                yaml.safe_dump(log), encoding="utf-8"
            )
            with patch("jobintel.migration._git_revision", return_value="abc"):
                plan = build_plan(root)

        self.assertEqual(["confirmed"], [item["_id"] for item in plan["collections"]["vacancies"]])
        self.assertEqual(["confirmed"], [item["vacancy_id"] for item in plan["collections"]["artifact_manifests"]])
        identities = plan["collections"]["source_identities"]
        self.assertEqual(["job-1"], [item["source_job_id"] for item in identities])
        self.assertEqual(1, plan["manifest"]["archive_metadata"])
        self.assertEqual(1, plan["manifest"]["archive_stats"]["stale"]["metadata_excluded"])

    def test_import_is_idempotent_and_reconcile_ignores_store_envelope(self) -> None:
        plan = {
            "manifest": {"plan_id": "plan-1", "plan_sha256": "sha", "git_revision": "git", "blocked": False},
            "collections": {"applications": [{"_id": "app-1", "value": 1}]},
        }
        store = FakeStore()
        first = import_plan(store, plan, dry_run=False)
        second = import_plan(store, plan, dry_run=False)
        self.assertEqual(1, first["inserted"]["applications"])
        self.assertEqual(1, second["unchanged"]["applications"])
        self.assertTrue(reconcile(store, plan)["ok"])
        store.data["applications"]["unexpected"] = {"_id": "unexpected", "revision": 1}
        report = reconcile(store, plan)
        self.assertFalse(report["ok"])
        self.assertEqual(["unexpected"], report["collections"]["applications"]["unexpected"])

    def test_export_excludes_needs_review_and_includes_events(self) -> None:
        apps, events, _ = project_vacancy_history(
            vacancy(),
            [{
                "vacancy_id": "vac-1", "changed_at": "2026-01-02T10:00:00Z",
                "from_status": "found", "to_status": "applied", "reason": "submitted",
            }],
        )
        questionable, _, _ = project_vacancy_history(
            vacancy("vac-2"),
            [{
                "vacancy_id": "vac-2", "changed_at": "2026-01-02T10:00:00Z",
                "from_status": "found", "to_status": "applied", "note": "form not submitted",
            }],
        )
        questionable[0].update(
            revision=2,
            writer_fence=4,
            updated_at=datetime(2026, 1, 3, tzinfo=timezone.utc),
        )
        export = export_applications(
            {"collections": {"applications": apps + questionable, "status_events": events}}
        )
        self.assertEqual(1, len(export["applications"]))
        self.assertEqual(1, export["coverage"]["needs_review"])
        self.assertNotIn("updated_at", export["coverage"]["needs_review_records"][0])
        self.assertEqual(1, len(export["events"]))
        self.assertEqual(2, export["coverage"]["status_events_total"])
        self.assertIn("application_channel", export["applications"][0])
        self.assertEqual(4, export["source_revision"])


if __name__ == "__main__":
    unittest.main()
