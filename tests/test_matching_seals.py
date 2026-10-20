from __future__ import annotations

import copy
import os
import subprocess
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from jobintel import cli
from jobintel.catalog_data import CatalogSnapshot, load_catalog_snapshot
from jobintel.matching import (
    APPROVED_EXTRACTION_VERSION, LEGACY_PROMPT_VERSION, MATCH_OUTPUT_SCHEMA,
    CodexMatchDraftClient, MatchAnalyzer, MatchError, _content_version,
    build_analysis_pack, current_matching_context, load_analysis_pack, publish_analysis_batch,
)
from jobintel.matching_policy import canonical, digest
from jobintel.models import NormalizedJob
from jobintel.registry import Registry
from jobintel.workflow_api import queue_items
from jobintel.workflows import load_workflow_policy


ROOT = Path(__file__).resolve().parents[1]


def result():
    return {"score": 84, "recommendation": "strong_match", "summary": "Supported synthetic backend fit.",
            "strengths": ["Synthetic backend evidence"], "gaps": [], "concerns": [], "hard_rejection": False,
            "hard_rejection_reason": None, "requirements": []}


def reseal(pack):
    pack["pack_sha256"] = digest({key: value for key, value in pack.items() if key not in {"results", "pack_sha256"}})
    return pack


class MatchingSealTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / "config").mkdir()
        for name in ("matching-policy.yaml", "selection-policy.yaml", "codex-workflows.yaml"):
            (self.root / "config" / name).write_bytes((ROOT / "config" / name).read_bytes())
        (self.root / "prompts").mkdir()
        (self.root / "prompts/vacancy-match.md").write_bytes((ROOT / "prompts/vacancy-match.md").read_bytes())
        self.profile = self.root / "synthetic-profile.md"
        self.profile.write_text("Synthetic candidate has documented PHP and Go backend experience.", encoding="utf-8")
        self.registry_root = self.root / "registry"
        self.registry = Registry(self.registry_root, id_factory=iter(("one", "two")).__next__)
        self.directories = []
        for name in ("one", "two"):
            created = self.registry.upsert(NormalizedJob("synthetic", name, f"https://example.test/{name}", "Backend Engineer", "Example", "Build Go backend services remotely in Europe."))
            self.directories.append(self.registry_root / "jobs" / created.directory)
        self.context = current_matching_context(self.root)
        self.workflow = load_workflow_policy(self.root / "config/codex-workflows.yaml")
        self.model = self.workflow.workflow("analyze").model_label
        self.client = SimpleNamespace(model=self.model, analyze=lambda **kwargs: result())
        self.analyzer = MatchAnalyzer(self.registry_root, [self.profile], self.client, context=self.context)

    def pack(self):
        return build_analysis_pack(self.registry_root, [self.profile], context=self.context).to_dict()

    def call(self, arguments):
        output = StringIO()
        with patch("jobintel.cli.__file__", str(self.root / "jobintel/cli.py")), patch("jobintel.cli.load_env", return_value={}), redirect_stdout(output), redirect_stderr(output):
            code = cli.main(arguments + ["--registry", str(self.registry_root), "--profile", str(self.profile)])
        return code, output.getvalue()

    def assert_unpublished(self):
        self.assertTrue(all(not (directory / "match.yaml").exists() for directory in self.directories))

    def test_actual_payload_tampering_fails_loader_and_direct_publisher_even_with_resealed_outer_hash(self):
        original = self.pack()
        changes = (
            lambda p: p["profile"].update(text="Fabricated candidate evidence"),
            lambda p: p["items"][0]["vacancy"].update(job_description="Fabricated vacancy"),
            lambda p: p["policy"].update(preferred_cities=["Other"]),
            lambda p: p.update(prompt=p["prompt"] + " Changed instruction"),
            lambda p: p["output_schema"].update(required=[]),
            lambda p: p["items"][0].update(vacancy_id="other"),
        )
        for index, change in enumerate(changes):
            for force in (False, True):
                with self.subTest(change=index, force=force):
                    altered = copy.deepcopy(original)
                    change(altered)
                    reseal(altered)
                    path = self.root / "altered.yaml"
                    path.write_text(yaml.safe_dump(altered), encoding="utf-8")
                    with self.assertRaises(MatchError):
                        load_analysis_pack(path, context=self.context)
                    with self.assertRaises(MatchError):
                        publish_analysis_batch(altered, {item["directory"]: result() for item in altered["items"]}, self.analyzer, force=force)
                    self.assert_unpublished()

    def test_fully_rehashed_fabricated_profile_or_vacancy_still_must_match_canonical_inputs(self):
        for field in ("profile", "vacancy"):
            with self.subTest(field=field):
                pack = self.pack()
                if field == "profile":
                    pack["profile"]["text"] = "Fabricated candidate evidence"
                    pack["profile"]["version"] = _content_version(pack["profile"]["text"])
                    for item in pack["items"]:
                        item["profile_version"] = pack["profile"]["version"]
                else:
                    pack["items"][0]["vacancy"]["job_description"] = "Fabricated vacancy"
                    pack["items"][0]["job_version"] = _content_version(canonical(pack["items"][0]["vacancy"]))
                reseal(pack)
                with self.assertRaisesRegex(MatchError, "differs from current"):
                    publish_analysis_batch(pack, {item["directory"]: result() for item in pack["items"]}, self.analyzer, force=True)
                self.assert_unpublished()

    def test_stale_last_item_prevents_first_write_and_context_changes_invalidate_existing_pack(self):
        pack = self.pack()
        last = self.registry_root / "jobs" / pack["items"][-1]["directory"]
        (last / "job.md").write_text("Changed actual source text", encoding="utf-8")
        with self.assertRaises(MatchError):
            publish_analysis_batch(pack, {item["directory"]: result() for item in pack["items"]}, self.analyzer)
        self.assert_unpublished()
        raw = yaml.safe_load((self.root / "config/matching-policy.yaml").read_text(encoding="utf-8"))
        (self.root / "config/matching-policy.yaml").write_text(yaml.safe_dump(raw | {"preferred_cities": ["Other"]}), encoding="utf-8")
        current = MatchAnalyzer(self.registry_root, [self.profile], self.client, context=current_matching_context(self.root))
        with self.assertRaisesRegex(MatchError, "matching policy is stale"):
            publish_analysis_batch(pack, {item["directory"]: result() for item in pack["items"]}, current, force=True)
        self.assert_unpublished()

    def test_public_publication_requires_real_sealed_payload_even_with_copied_tags_and_force(self):
        pack = self.pack()
        item = pack["items"][0]
        directory = self.registry_root / "jobs" / item["directory"]
        raw = yaml.safe_load((self.root / "config/matching-policy.yaml").read_text(encoding="utf-8"))
        (self.root / "config/matching-policy.yaml").write_text(yaml.safe_dump(raw | {"preferred_cities": ["Other"]}), encoding="utf-8")
        current = MatchAnalyzer(self.registry_root, [self.profile], self.client, context=current_matching_context(self.root))
        for force in (False, True):
            for copied in ({}, {"expected_profile_version": item["profile_version"], "expected_job_version": item["job_version"],
                               "expected_prompt_version": current.matching_context().prompt_version}):
                with self.subTest(force=force, copied=bool(copied)), patch.object(current, "_publish_analysis") as write:
                    with self.assertRaisesRegex(MatchError, "schema-2 sealed pack"):
                        current.publish_analysis(directory, result(), force=force, **copied)
                    write.assert_not_called()
        with self.assertRaisesRegex(MatchError, "matching policy is stale"):
            current.publish_analysis(directory, pack | {"results": {row["directory"]: result() for row in pack["items"]}}, force=True)
        self.assert_unpublished()

    def test_public_publication_accepts_a_current_complete_single_pack(self):
        directory = self.directories[0]
        pack = build_analysis_pack(self.registry_root, [self.profile], directories=[directory], context=self.context).to_dict()
        published = self.analyzer.publish_analysis(directory, pack | {"results": {directory.name: result()}})
        self.assertEqual("analyzed", published.status)
        self.assertTrue(self.analyzer.is_current(directory))

    def test_last_item_resealed_source_url_tampering_fails_before_any_write(self):
        pack = self.pack()
        pack["items"][-1]["source_url"] = "https://example.test/altered-notification-url"
        reseal(pack)
        with patch.object(self.analyzer, "_publish_analysis") as write, self.assertRaisesRegex(MatchError, "source URL differs"):
            publish_analysis_batch(pack, {item["directory"]: result() for item in pack["items"]}, self.analyzer)
        write.assert_not_called()
        self.assert_unpublished()

    def test_jobs_only_selectors_and_direct_pack_paths_fail_before_input_reads(self):
        for name in ("../outside", "/outside", "C:/outside", "C:outside", "\\\\host\\share", "sub\\name", ".", ".."):
            with self.subTest(name=name):
                with self.assertRaises(MatchError):
                    self.analyzer.resolve(name)
                pack = self.pack()
                pack["items"][0]["directory"] = name
                reseal(pack)
                with patch.object(self.analyzer, "_inputs") as inputs, self.assertRaises(MatchError):
                    publish_analysis_batch(pack, {}, self.analyzer)
                inputs.assert_not_called()
        with patch.object(self.analyzer, "_load_profile") as profile, self.assertRaises(MatchError):
            self.analyzer._inputs(self.root / "outside")
        profile.assert_not_called()

    def test_symlink_escape_fails_at_direct_inputs_and_publisher(self):
        outside = self.root / "outside"
        outside.mkdir()
        alias = self.registry_root / "jobs/escape"
        try:
            alias.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            if os.name != "nt":
                self.skipTest(f"directory symlinks unavailable: {exc}")
            junction = subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(outside)], capture_output=True)
            if junction.returncode:
                self.skipTest("directory symlinks and junctions are unavailable")
        with self.assertRaises(MatchError):
            self.analyzer.resolve("escape")
        pack = self.pack()
        pack["items"][0]["directory"] = "escape"
        reseal(pack)
        with patch.object(self.analyzer, "_inputs") as inputs, self.assertRaises(MatchError):
            publish_analysis_batch(pack, {item["directory"]: result() for item in pack["items"]}, self.analyzer)
        inputs.assert_not_called()

    def test_duplicate_yaml_results_and_duplicate_pack_directories_fail_closed(self):
        path = self.root / "duplicate.yaml"
        pack = self.pack()
        path.write_text(yaml.safe_dump(pack) + "results: {}\nresults: {}\n", encoding="utf-8")
        with self.assertRaisesRegex(MatchError, "duplicate YAML"):
            load_analysis_pack(path, context=self.context)
        pack["items"].append(copy.deepcopy(pack["items"][0]))
        reseal(pack)
        with self.assertRaisesRegex(MatchError, "duplicate directories"):
            publish_analysis_batch(pack, {}, self.analyzer)
        self.assert_unpublished()

    def test_single_export_publish_and_selector_mismatch_use_same_seal(self):
        path = self.root / "single.yaml"
        code, output = self.call(["analyze", self.directories[0].name, "--pack", str(path), "--workflow", "analyze"])
        self.assertEqual(0, code, output)
        pack = load_analysis_pack(path, context=self.context)
        self.assertEqual(1, len(pack["items"]))
        pack["results"] = {self.directories[0].name: result()}
        path.write_text(yaml.safe_dump(pack), encoding="utf-8")
        code, output = self.call(["analyze", self.directories[1].name, "--input", str(path), "--workflow", "analyze", "--force"])
        self.assertNotEqual(0, code, output)
        self.assert_unpublished()
        with patch("jobintel.cli.current_matching_context", wraps=current_matching_context) as context:
            code, output = self.call(["analyze", self.directories[0].name, "--input", str(path), "--workflow", "analyze"])
        self.assertEqual(0, code, output)
        context.assert_called_once_with(self.root)
        saved = yaml.safe_load((self.directories[0] / "match.yaml").read_text(encoding="utf-8"))
        self.assertEqual(self.context.prompt_version, saved["prompt_version"])
        self.assertEqual(self.model, saved["model"])

    def test_single_client_validates_candidate_and_vacancy_arguments_and_rejects_raw_draft(self):
        pack = build_analysis_pack(self.registry_root, [self.profile], directories=[self.directories[0]], context=self.context).to_dict()
        path = self.root / "single.yaml"
        path.write_text(yaml.safe_dump(pack | {"results": {self.directories[0].name: result()}}), encoding="utf-8")
        client = CodexMatchDraftClient(path, model=self.model, context=self.context)
        with self.assertRaisesRegex(MatchError, "not bound"):
            client.analyze(candidate_profile="Different candidate", vacancy=pack["items"][0]["vacancy"])
        with self.assertRaisesRegex(MatchError, "not bound"):
            client.analyze(candidate_profile=pack["profile"]["text"], vacancy={"job_description": "Different source"})
        path.write_text(yaml.safe_dump(result()), encoding="utf-8")
        with self.assertRaisesRegex(MatchError, "schema-2 sealed pack"):
            client.analyze(candidate_profile=pack["profile"]["text"], vacancy=pack["items"][0]["vacancy"])

    def test_real_preflight_and_file_snapshot_freshness_agree_on_effective_policy_changes(self):
        directory = self.directories[0]
        self.analyzer.analyze_directory(directory)
        before = (directory / "match.yaml").read_bytes()
        profile_version = self.analyzer._load_profile()[1]
        args = SimpleNamespace(arguments=[directory.name], workflow="prepare", model_profile=None, document="cv",
                               profile=[self.profile], allow_low_score_cv_refresh=False, bypass_hard_rejection_cv_refresh=False)
        report = cli._preflight_preparation(args, {}, self.root, self.registry_root)
        self.assertTrue(report["vacancies"][0]["ok"])
        self.assertEqual(84, report["vacancies"][0]["score"])
        self.assertEqual(profile_version, self.analyzer._load_profile()[1])
        (self.root / "config/notification-settings.yaml").write_text("destination: changed", encoding="utf-8")
        self.assertTrue(cli._preflight_preparation(args, {}, self.root, self.registry_root)["vacancies"][0]["ok"])
        raw = yaml.safe_load((self.root / "config/matching-policy.yaml").read_text(encoding="utf-8"))
        (self.root / "config/matching-policy.yaml").write_text(yaml.safe_dump(raw | {"preferred_cities": ["Other"]}), encoding="utf-8")
        context = current_matching_context(self.root)
        with self.assertRaisesRegex(ValueError, "match analysis is missing, stale"):
            cli._preflight_preparation(args, {}, self.root, self.registry_root)
        current = MatchAnalyzer(self.registry_root, [self.profile], self.client, context=context)
        self.assertFalse(current.is_current(directory))
        snapshot = load_catalog_snapshot(self.registry_root)
        documents = {}
        for row in snapshot.vacancies:
            path = row.directory
            documents[path.name] = {"meta": yaml.safe_load((path / "meta.yaml").read_text(encoding="utf-8")),
                                    "job_text": (path / "job.md").read_text(encoding="utf-8"), "triage": None,
                                    "match": yaml.safe_load((path / "match.yaml").read_text(encoding="utf-8")) if (path / "match.yaml").exists() else None}
        for view in (snapshot, CatalogSnapshot(snapshot.vacancies, documents)):
            rows = queue_items("analyze", self.root, self.registry_root, [self.profile], _snapshot=view)
            self.assertIn(directory.name, [row.vacancy.directory.name for row in rows])
        self.assertEqual(before, (directory / "match.yaml").read_bytes())
        self.assertEqual(profile_version, self.analyzer._load_profile()[1])

    def test_production_legacy_pin_matches_actual_reviewed_default_context(self):
        self.assertEqual(current_matching_context(ROOT).prompt_version, APPROVED_EXTRACTION_VERSION)
        self.assertEqual(self.context.prompt_version, APPROVED_EXTRACTION_VERSION)

    def test_actual_current_and_legacy_matches_reuse_without_writes_and_invalidate_changed_inputs(self):
        directory = self.directories[0]
        self.analyzer.analyze_directory(directory)
        path = directory / "match.yaml"
        match = yaml.safe_load(path.read_text(encoding="utf-8"))
        sources = (self.profile, directory / "job.md", self.root / "prompts/vacancy-match.md",
                   self.root / "config/matching-policy.yaml")
        originals = {source: source.read_bytes() for source in sources}
        history = {source: source.read_bytes() for source in (directory / "meta.yaml", directory / "match.md")}
        for version in (self.context.prompt_version, LEGACY_PROMPT_VERSION):
            with self.subTest(version=version):
                match["prompt_version"] = version
                path.write_text(yaml.safe_dump(match), encoding="utf-8")
                before = path.read_bytes()
                with patch.object(self.client, "analyze") as client, patch.object(self.analyzer, "_publish_analysis") as write:
                    self.assertTrue(self.analyzer.is_current(directory))
                    self.assertEqual("skipped", self.analyzer.analyze_directory(directory).status)
                    client.assert_not_called()
                    write.assert_not_called()
                self.assertEqual(before, path.read_bytes())
                for changed_input in ("prompt", "schema", "policy", "profile", "job", "model"):
                    with self.subTest(changed_input=changed_input):
                        schema = copy.deepcopy(MATCH_OUTPUT_SCHEMA)
                        try:
                            if changed_input == "schema":
                                schema["properties"]["summary"]["minLength"] = 1
                            elif changed_input == "policy":
                                policy = yaml.safe_load(sources[3].read_text(encoding="utf-8"))
                                sources[3].write_text(yaml.safe_dump(policy | {"preferred_cities": ["Other"]}), encoding="utf-8")
                            elif changed_input == "model":
                                path.write_text(yaml.safe_dump(match | {"model": "unapproved-synthetic-model"}), encoding="utf-8")
                            else:
                                source = {"prompt": sources[2], "profile": sources[0], "job": sources[1]}[changed_input]
                                source.write_bytes(originals[source] + b"\nChanged synthetic input.")
                            receipt = path.read_bytes()
                            with patch("jobintel.matching.MATCH_OUTPUT_SCHEMA", schema):
                                changed = MatchAnalyzer(self.registry_root, [self.profile], self.client, context=current_matching_context(self.root))
                                self.assertFalse(changed.is_current(directory))
                            self.assertEqual(receipt, path.read_bytes())
                            for source, content in history.items():
                                self.assertEqual(content, source.read_bytes())
                        finally:
                            for source, content in originals.items():
                                source.write_bytes(content)
                            path.write_bytes(before)

    def test_invalid_context_precedes_leases_migration_materialization_clients_and_notifications(self):
        (self.root / "config/matching-policy.yaml").write_text("schema_version: 999", encoding="utf-8")
        commands = (["analyze", self.directories[0].name, "--input", "unused.yaml", "--workflow", "analyze"],
                    ["analyze-batch", "--input", "unused.yaml", "--workflow", "analyze"],
                    ["pending", "analyze", "all", "--workflow", "analyze"],
                    ["prepare", self.directories[0].name, "--input", "unused", "--workflow", "prepare"])
        for arguments in commands:
            with self.subTest(arguments=arguments), patch("jobintel.cli.workflow_lock") as lock, patch("jobintel.cli.Registry.migrate_metadata") as migrate, patch("jobintel.cli.op.materialize_vacancy_snapshot") as materialize, patch("jobintel.cli.CodexMatchDraftClient") as client, patch("jobintel.cli.build_analysis_notification") as notification:
                code, output = self.call(arguments)
                self.assertNotEqual(0, code, output)
                for action in (lock, migrate, materialize, client, notification):
                    action.assert_not_called()
        args = SimpleNamespace(arguments=[self.directories[0].name])
        with patch("jobintel.cli.op.materialize_vacancy_snapshot") as materialize, self.assertRaises(ValueError):
            cli._preflight_preparation(args, {}, self.root, self.registry_root)
        materialize.assert_not_called()
        self.assert_unpublished()
