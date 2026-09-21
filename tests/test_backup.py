from __future__ import annotations

import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import unittest
import uuid
import zipfile
from pathlib import Path
from unittest.mock import patch

from pymongo import MongoClient

from jobintel.backup import (
    _allowed,
    _artifact_bytes,
    _filesystem_path,
    _project_files,
    _safe_archive_name,
    create_backup,
    create_yaml_backup,
    restore_backup,
    verify_backup,
)
from jobintel.mongodb_storage import MongoStore


class SnapshotStore:
    database_name = "jobintel_test_backup"

    def __init__(self) -> None:
        self.restored = None
        self.schema_ensured = False

    def ensure_schema(self):
        self.schema_ensured = True

    def lease(self, owner: str):
        del owner
        return contextlib.nullcontext()

    def snapshot(self):
        return {
            "schema_version": 1,
            "database": self.database_name,
            "captured_at": "2026-09-21T10:00:00Z",
            "collections": {
                "applications": {
                    "documents": [{"_id": "app-1", "revision": 1}],
                    "indexes": [{"name": "_id_", "key": {"_id": 1}}],
                }
            },
        }

    def restore_snapshot(self, snapshot, *, require_empty=True):
        self.restored = snapshot
        return {"documents": 1, "indexes": 1, "collections": {"applications": 1}, "require_empty": require_empty}

    def list(self, collection: str, *args, **kwargs):
        del collection, args, kwargs
        return []


def tiny_plan() -> dict:
    return {
        "schema_version": 1,
        "manifest": {
            "schema_version": 1,
            "plan_id": "plan-1",
            "plan_sha256": "sha",
            "git_revision": "abc",
            "blocked": False,
            "counts": {"applications": 0},
        },
        "collections": {"applications": []},
    }


class BackupTests(unittest.TestCase):
    def _root(self, temporary: str) -> Path:
        root = Path(temporary) / "repo"
        (root / "registry").mkdir(parents=True)
        (root / "registry" / "manual-status-log.yaml").write_text("schema_version: 1\nevents: []\n", encoding="utf-8")
        return root

    def test_yaml_backup_is_chunked_and_verified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            output = Path(temporary) / "out"
            sheets = {"captured_at": "2026-09-21T11:00:00Z", "rows": [{"note": "manual"}]}
            with patch("jobintel.backup.build_plan", return_value=tiny_plan()), patch(
                "jobintel.backup._project_files", return_value=["registry/manual-status-log.yaml"]
            ), patch("jobintel.backup._git_revision", return_value="abc"):
                result = create_yaml_backup(root, output, sheets_snapshot=sheets, part_size=1024)
            report = verify_backup(Path(result["directory"]))
            self.assertTrue(report["ok"])
            self.assertGreaterEqual(report["objects_checked"], 3)
            self.assertEqual("2026-09-21T11:00:00Z", result["manifest"]["sheets"]["captured_at"])

    def test_project_snapshot_includes_agent_and_github_configuration(self) -> None:
        self.assertTrue(
            _allowed(".agents/skills/workflow/SKILL.md", (".agents", "skills", "workflow", "SKILL.md"))
        )
        self.assertTrue(_allowed(".github/scripts/verify.sh", (".github", "scripts", "verify.sh")))

    def test_corrupt_part_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            output = Path(temporary) / "out"
            with patch("jobintel.backup.build_plan", return_value=tiny_plan()), patch(
                "jobintel.backup._project_files", return_value=[]
            ), patch("jobintel.backup._git_revision", return_value="abc"):
                result = create_yaml_backup(root, output, part_size=1024)
            directory = Path(result["directory"])
            manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8"))
            part = directory / manifest["parts"][0]["name"]
            raw = bytearray(part.read_bytes())
            raw[0] ^= 0xFF
            part.write_bytes(raw)
            self.assertFalse(verify_backup(directory)["ok"])

    def test_manifest_part_path_cannot_escape_backup_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            output = Path(temporary) / "out"
            with patch("jobintel.backup.build_plan", return_value=tiny_plan()), patch(
                "jobintel.backup._project_files", return_value=[]
            ), patch("jobintel.backup._git_revision", return_value="abc"):
                result = create_yaml_backup(root, output, part_size=1024)
            directory = Path(result["directory"])
            manifest_path = directory / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["parts"][0]["name"] = "../escape"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            report = verify_backup(directory)
            self.assertFalse(report["ok"])
            self.assertIn("unsafe backup part", report["errors"][0])

    def test_windows_drive_and_ads_paths_are_rejected_cross_platform(self) -> None:
        for value in ("project/C:/escape.txt", "project/file.txt:stream", "C:/escape.txt"):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, "unsafe"):
                _safe_archive_name(value)

    def test_mongodb_backup_restores_verified_snapshot_under_lease(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            output = Path(temporary) / "out"
            store = SnapshotStore()
            with patch("jobintel.backup._project_files", return_value=[]), patch(
                "jobintel.backup._git_revision", return_value="abc"
            ):
                result = create_backup(
                    store,
                    root,
                    output,
                    sheets_snapshot={"captured_at": "2026-09-21T11:00:00Z", "rows": []},
                    part_size=1024,
                )
            artifact_output = Path(temporary) / "restore-output"
            restored = restore_backup(
                store, Path(result["directory"]), artifact_output=artifact_output
            )
            self.assertEqual(1, restored["restore"]["documents"])
            self.assertEqual("jobintel_test_backup", store.restored["database"])
            self.assertEqual(1, restored["artifact_restore"]["files"])
            self.assertTrue((artifact_output / "sheets" / "snapshot.json").is_file())

    def test_mongodb_backup_preserves_compound_index_order_on_real_restore(self) -> None:
        uri = os.environ.get("JOBINTEL_TEST_MONGODB_URI", "").strip()
        if not uri:
            self.skipTest("JOBINTEL_TEST_MONGODB_URI is not configured")
        source_name = "jobintel_test_" + uuid.uuid4().hex
        target_name = "jobintel_restore_" + uuid.uuid4().hex
        source = MongoStore(uri, source_name, lease_seconds=2)
        target = MongoStore(uri, target_name, lease_seconds=2)
        try:
            source.ensure_schema()
            with tempfile.TemporaryDirectory() as temporary:
                root = self._root(temporary)
                with patch("jobintel.backup._project_files", return_value=[]), patch(
                    "jobintel.backup._git_revision", return_value="abc"
                ):
                    backup = create_backup(
                        source, root, Path(temporary) / "out", part_size=1024
                    )
                restored = restore_backup(target, Path(backup["directory"]))

            self.assertGreaterEqual(restored["restore"]["indexes"], 1)
            index = target.database["prefilter_rejections"].index_information()[
                "scope_directory_unique"
            ]
            self.assertEqual(
                [("scope", 1), ("directory", 1)], list(index["key"])
            )
        finally:
            source.close()
            target.close()
            client = MongoClient(uri)
            try:
                client.drop_database(source_name)
                client.drop_database(target_name)
            finally:
                client.close()

    def test_restore_refuses_nonisolated_database(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            output = Path(temporary) / "out"
            store = SnapshotStore()
            with patch("jobintel.backup._project_files", return_value=[]), patch(
                "jobintel.backup._git_revision", return_value="abc"
            ):
                result = create_backup(store, root, output, part_size=1024)
            store.database_name = "job_intelligence"
            with self.assertRaisesRegex(ValueError, "isolated"):
                restore_backup(store, Path(result["directory"]))

    def test_yaml_restore_initializes_schema_before_import(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            store = SnapshotStore()
            with patch("jobintel.backup.build_plan", return_value=tiny_plan()), patch(
                "jobintel.backup._project_files", return_value=[]
            ), patch("jobintel.backup._git_revision", return_value="abc"):
                result = create_yaml_backup(root, Path(temporary) / "out", part_size=1024)
            with patch("jobintel.backup.import_plan", return_value={"inserted": {}}), patch(
                "jobintel.backup.reconcile", return_value={"ok": True}
            ):
                restore_backup(store, Path(result["directory"]))
            self.assertTrue(store.schema_ensured)

    def test_compact_backup_restores_only_referenced_archive_members(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            archive_path = root / "archives" / "stale" / "old.zip"
            archive_path.parent.mkdir(parents=True)
            meta = b"id: confirmed\n"
            cv = b"confirmed cv"
            with zipfile.ZipFile(archive_path, "w") as archive:
                archive.writestr("confirmed/meta.yaml", meta)
                archive.writestr("confirmed/application/cv.md", cv)
                archive.writestr("unrelated/meta.yaml", b"id: unrelated\n")
            plan = tiny_plan()
            plan["collections"] = {
                "vacancies": [{
                    "_id": "confirmed", "directory": "confirmed",
                    "legacy_evidence": [{
                        "locator": "archives/stale/old.zip!confirmed/meta.yaml",
                        "size": len(meta), "sha256": hashlib.sha256(meta).hexdigest(),
                    }],
                }],
                "artifact_manifests": [{
                    "_id": "package", "directory": "confirmed",
                    "evidence_locator": "archives/stale/old.zip!confirmed/meta.yaml",
                    "files": [{
                        "path": "archives/stale/old.zip!confirmed/application/cv.md",
                        "size": len(cv), "sha256": hashlib.sha256(cv).hexdigest(),
                    }],
                }],
            }
            with patch("jobintel.backup.build_plan", return_value=plan), patch(
                "jobintel.backup._project_files", return_value=[]
            ), patch("jobintel.backup._git_revision", return_value="abc"):
                result = create_yaml_backup(root, Path(temporary) / "out", part_size=1024)
            restored_root = Path(temporary) / "restored"
            store = SnapshotStore()
            with patch("jobintel.backup.import_plan", return_value={"inserted": {}}), patch(
                "jobintel.backup.reconcile", return_value={"ok": True}
            ):
                restore_backup(store, Path(result["directory"]), artifact_output=restored_root)
            compact = restored_root / "project" / "archives" / "stale" / "old.zip"
            with zipfile.ZipFile(compact) as archive:
                self.assertEqual(
                    ["confirmed/application/cv.md", "confirmed/meta.yaml"],
                    sorted(archive.namelist()),
                )

    def test_restore_and_read_support_windows_extended_length_paths(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            directory = "vacancy-" + "a" * 110
            filename = "CV_" + "b" * 120 + ".docx"
            relative = f"registry/jobs/{directory}/application/{filename}"
            artifact_output = Path(temporary) / "restored-v2"
            destination = artifact_output / "project" / Path(relative)
            self.assertGreater(len(str(destination)), 260)
            with patch("jobintel.backup.build_plan", return_value=tiny_plan()), patch(
                "jobintel.backup._project_files", return_value=[relative]
            ), patch("jobintel.backup._repo_bytes", return_value=b"document"), patch(
                "jobintel.backup._git_revision", return_value="abc"
            ):
                result = create_yaml_backup(root, Path(temporary) / "out", part_size=1024)
            store = SnapshotStore()
            with patch("jobintel.backup.import_plan", return_value={"inserted": {}}), patch(
                "jobintel.backup.reconcile", return_value={"ok": True}
            ):
                restore_backup(store, Path(result["directory"]), artifact_output=artifact_output)

            self.assertTrue(_filesystem_path(destination).is_file())
            self.assertEqual(b"document", _artifact_bytes(artifact_output / "project", directory, relative))
            shutil.rmtree(_filesystem_path(artifact_output))

    def test_non_ascii_tracked_reference_is_backed_up_and_restored(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            directory = "2026-09-21_propelahed_laravel-розробник"
            vacancy = root / "registry" / "jobs" / directory
            application = vacancy / "application"
            application.mkdir(parents=True)
            meta_path = vacancy / "meta.yaml"
            artifact_path = application / "резюме.md"
            meta = b"id: vacancy-propelahed\n"
            artifact = "підтверджений документ\n".encode("utf-8")
            meta_path.write_bytes(meta)
            artifact_path.write_bytes(artifact)
            subprocess.run(["git", "init", "-q"], cwd=root, check=True)
            subprocess.run(["git", "add", "--", "registry"], cwd=root, check=True)
            meta_relative = meta_path.relative_to(root).as_posix()
            artifact_relative = artifact_path.relative_to(root).as_posix()
            self.assertIn(meta_relative, _project_files(root))
            self.assertIn(artifact_relative, _project_files(root))

            plan = tiny_plan()
            plan["collections"] = {
                "vacancies": [{
                    "_id": "vacancy-propelahed", "directory": directory,
                    "legacy_evidence": [{
                        "locator": meta_relative,
                        "size": len(meta), "sha256": hashlib.sha256(meta).hexdigest(),
                    }],
                }],
                "artifact_manifests": [{
                    "_id": "package-propelahed", "directory": directory,
                    "evidence_locator": meta_relative,
                    "files": [{
                        "path": artifact_relative,
                        "size": len(artifact), "sha256": hashlib.sha256(artifact).hexdigest(),
                    }],
                }],
            }
            with patch("jobintel.backup.build_plan", return_value=plan), patch(
                "jobintel.backup._git_revision", return_value="abc"
            ):
                result = create_yaml_backup(root, Path(temporary) / "out", part_size=1024)
            restored_root = Path(temporary) / "restored-unicode"
            store = SnapshotStore()
            with patch("jobintel.backup.import_plan", return_value={"inserted": {}}), patch(
                "jobintel.backup.reconcile", return_value={"ok": True}
            ):
                restore_backup(store, Path(result["directory"]), artifact_output=restored_root)

            project = restored_root / "project"
            self.assertEqual(meta, _artifact_bytes(project, directory, meta_relative))
            self.assertEqual(artifact, _artifact_bytes(project, directory, artifact_relative))

    def test_backup_checks_database_artifact_hashes(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            artifact = root / "registry" / "jobs" / "job-a" / "application" / "cv.md"
            artifact.parent.mkdir(parents=True)
            artifact.write_text("new", encoding="utf-8")
            store = SnapshotStore()
            snapshot = store.snapshot()
            snapshot["collections"]["artifact_manifests"] = {
                "documents": [{
                    "_id": "package-1", "directory": "job-a",
                    "files": [{"path": "application/cv.md", "size": 3, "sha256": "0" * 64}],
                }],
                "indexes": [],
            }
            store.snapshot = lambda: snapshot
            with patch("jobintel.backup._project_files", return_value=[]):
                with self.assertRaisesRegex(ValueError, "checksum"):
                    create_backup(store, root, Path(temporary) / "out", part_size=1024)

    def test_sheets_snapshot_requires_independent_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = self._root(temporary)
            with patch("jobintel.backup.build_plan", return_value=tiny_plan()), patch(
                "jobintel.backup._project_files", return_value=[]
            ):
                with self.assertRaisesRegex(ValueError, "captured_at"):
                    create_yaml_backup(root, Path(temporary) / "out", sheets_snapshot={"rows": []})


if __name__ == "__main__":
    unittest.main()
