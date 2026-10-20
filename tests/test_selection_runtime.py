from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from dataclasses import asdict, replace
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import Mock, patch

import yaml

from jobintel.catalog_data import CatalogSnapshot, load_catalog_snapshot
from jobintel.cli import _run_collector, main
from jobintel.models import NormalizedJob
from jobintel.prefilter import RejectedRegistry, prefilter_job
from jobintel.registry import Registry
from jobintel.selection_policy import DEFAULT_SELECTION_POLICY_PATH, SelectionPolicyError, load_selection_policy
from jobintel.triage import BODY_WINDOW, evaluate_triage, should_skip_model, snapshot_should_skip, write_triage
from jobintel.workflow_api import queue_items, workflow_report
from scripts.archive_jobs import _eligible_document, archive, eligible, main as archive_main


ROOT = Path(__file__).resolve().parents[1]
NOW = datetime(2026, 7, 23, 12, tzinfo=timezone.utc)
POLICY = load_selection_policy(DEFAULT_SELECTION_POLICY_PATH)


def job(**overrides):
    return NormalizedJob(**({"source": "synthetic", "source_job_id": "one", "source_url": "https://example.test/one",
                            "title": "Backend Engineer", "company": "Example", "description": "Build Go services.",
                            "published_at": "2026-07-22T12:00:00Z"} | overrides))


class SelectionRuntimeTests(unittest.TestCase):
    def test_each_prefilter_group_can_change_its_decision_without_changing_an_unrelated_one(self) -> None:
        cases = [
            (job(published_at="2026-07-15T12:00:00Z"), replace(POLICY, max_age_days=10)),
            (job(title="QA Engineer"), replace(POLICY, excluded_roles=("mobile",))),
            (job(title="Android Developer"), replace(POLICY, excluded_roles=("qa",))),
            (job(remote=False), replace(POLICY, reject_explicit_non_remote=False)),
            (job(description="German C1 required. Build Go services."), replace(POLICY, blocking_languages=())),
            (job(description="Maintain WordPress in PHP."), replace(POLICY, excluded_cms=())),
            (job(description="Build Spring Boot with PHP integrations."), replace(POLICY, excluded_technologies=())),
            (job(description="Build Python and R services with Go APIs."), replace(POLICY, excluded_combinations=())),
            (job(description="Build Python services."), replace(POLICY, target_technologies=("python",))),
        ]
        for vacancy, changed in cases:
            with self.subTest(vacancy=vacancy, changed=changed):
                self.assertIsNotNone(prefilter_job(vacancy, now=NOW, policy=POLICY))
                self.assertIsNone(prefilter_job(vacancy, now=NOW, policy=changed))
                unrelated = job(description="Spanish C1 required. Build Go services.")
                if changed.blocking_languages:
                    self.assertEqual(prefilter_job(unrelated, now=NOW, policy=POLICY), prefilter_job(unrelated, now=NOW, policy=changed))
                else:
                    unrelated = job(remote=False)
                    self.assertEqual(prefilter_job(unrelated, now=NOW, policy=POLICY), prefilter_job(unrelated, now=NOW, policy=changed))

    def test_location_groups_and_european_exception_change_independently(self) -> None:
        for field, text in (
            ("reject_us_remote", "Remote (U.S.). Build Go services."),
            ("reject_us_location", "United States applicants only. Build Go services."),
            ("reject_american_timezones", "Working LATAM time zones. Build Go services."),
            ("reject_american_location", "Must be based in North America. Build Go services."),
        ):
            with self.subTest(field=field):
                changed = replace(POLICY, location=replace(POLICY.location, **{field: False}))
                self.assertIsNotNone(prefilter_job(job(description=text), now=NOW, policy=POLICY))
                self.assertIsNone(prefilter_job(job(description=text), now=NOW, policy=changed))
                self.assertIsNotNone(prefilter_job(job(remote=False), now=NOW, policy=changed))
        vacancy = job(description="Remote (U.S.), EMEA working hours available. Build Go services.")
        changed = replace(POLICY, location=replace(POLICY.location, allow_european_exception=False))
        self.assertIsNone(prefilter_job(vacancy, now=NOW, policy=POLICY))
        self.assertEqual("location_requirement", prefilter_job(vacancy, now=NOW, policy=changed).category)

    def test_every_supported_technology_can_be_selected_and_explicit_age_override_still_wins(self) -> None:
        for technology, text in (("go", "Golang"), ("php", "PHP8"), ("python", "Python"), ("r", "R"), ("julia", "Julia"), ("spring_boot", "Spring Boot")):
            with self.subTest(technology=technology):
                changed = replace(POLICY, target_technologies=(technology,), excluded_technologies=(), excluded_combinations=())
                self.assertIsNone(prefilter_job(job(description=f"Build {text} services."), now=NOW, policy=changed))
                self.assertIsNotNone(prefilter_job(job(description="Build Java services."), now=NOW, policy=changed))
        older = job(published_at="2026-07-15T12:00:00Z")
        self.assertIsNone(prefilter_job(older, now=NOW, policy=POLICY, max_age_days=10))
        self.assertIsNotNone(prefilter_job(older, now=NOW, policy=replace(POLICY, max_age_days=10), max_age_days=7))

    def test_configured_language_cms_and_combination_order_controls_reason(self) -> None:
        changed = replace(POLICY, blocking_languages=("italian", "german"))
        self.assertEqual("hard Italian language requirement", prefilter_job(job(description="German C1 required. Italian C1 required. Build Go services."), now=NOW, policy=changed).reason)
        changed = replace(POLICY, excluded_cms=("drupal", "wordpress"))
        self.assertEqual("Drupal vacancies are ignored", prefilter_job(job(description="WordPress and Drupal in PHP."), now=NOW, policy=changed).reason)
        changed = replace(POLICY, excluded_combinations=(("python", "julia"), ("python", "r")))
        self.assertEqual("Python + Julia is not a target stack", prefilter_job(job(description="Python, R, Julia and Go services."), now=NOW, policy=changed).reason)

    def test_large_positive_age_policy_and_explicit_override_do_not_overflow(self) -> None:
        oldest = job(published_at="0001-01-01T00:00:00Z")
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "selection-policy.yaml"
            for days in (1000000, 10 ** 1000):
                with self.subTest(days=days):
                    path.write_text(yaml.safe_dump(asdict(POLICY) | {"max_age_days": days}), encoding="utf-8")
                    loaded = load_selection_policy(path)
                    self.assertIsNone(prefilter_job(oldest, now=NOW, policy=loaded))
                    self.assertIsNone(prefilter_job(oldest, now=NOW, policy=POLICY, max_age_days=days))

    def test_age_cutoff_preserves_exact_microsecond_boundary(self) -> None:
        for timestamp, stale in (
            ("2026-07-16T11:59:59.999999Z", True),
            ("2026-07-16T12:00:00.000000Z", False),
            ("2026-07-16T12:00:00.000001Z", False),
        ):
            with self.subTest(timestamp=timestamp):
                result = prefilter_job(job(published_at=timestamp), now=NOW, policy=POLICY)
                self.assertEqual(stale, result is not None)
                if result:
                    self.assertEqual("stale", result.category)
                    self.assertEqual(f"published_at {timestamp} is older than 7 days", result.reason)

    def test_triage_binding_tracks_effective_inputs_and_recognition_but_not_other_selection(self) -> None:
        meta = {"id": "one", "title": "SRE"}
        original = evaluate_triage(meta, "Build Go services.", policy=POLICY)
        unrelated = replace(POLICY, max_age_days=3, blocking_languages=())
        self.assertEqual(original, evaluate_triage(meta, "Build Go services.", policy=unrelated))
        self.assertNotEqual(original["triage_version"], evaluate_triage(meta, "Changed body", policy=POLICY)["triage_version"])
        self.assertNotEqual(original["triage_version"], evaluate_triage({**meta, "title": "Backend Engineer"}, "Build Go services.", policy=POLICY)["triage_version"])
        disabled = evaluate_triage(meta, "Build Go services.", policy=replace(POLICY, triage_exclusions=()))
        self.assertFalse(disabled["skip_model"])
        self.assertNotEqual(original["triage_version"], disabled["triage_version"])
        with patch("jobintel.triage._HIGH_CONFIDENCE_RULES", (("sre", r"\bsre\b|\breliability\b"),)):
            altered = evaluate_triage(meta, "Build Go services.", policy=replace(POLICY, triage_exclusions=("sre",)))
        unaltered = evaluate_triage(meta, "Build Go services.", policy=replace(POLICY, triage_exclusions=("sre",)))
        self.assertNotEqual(unaltered["triage_version"], altered["triage_version"])
        body = "a" * BODY_WINDOW
        self.assertEqual(evaluate_triage(meta, body, policy=POLICY), evaluate_triage(meta, body + " Sales", policy=POLICY))

    def make_project(self, root: Path):
        (root / "config").mkdir()
        for name in ("selection-policy.yaml", "codex-workflows.yaml"):
            (root / "config" / name).write_bytes((ROOT / "config" / name).read_bytes())
        (root / "prompts").mkdir()
        (root / "prompts/vacancy-match.md").write_text("Synthetic matching prompt", encoding="utf-8")
        profile = root / "synthetic-profile.md"
        profile.write_text("Synthetic Go engineering evidence", encoding="utf-8")
        registry = Registry(root / "registry", clock=lambda: NOW, id_factory=lambda: "one")
        created = registry.upsert(job(title="SRE"))
        directory = root / "registry/jobs" / created.directory
        receipt = write_triage(directory, policy=POLICY)
        return directory, profile, receipt

    def test_queue_pending_and_archive_parity_under_policy_content_and_receipt_changes(self) -> None:
        variants = ("current", "unrelated", "disabled", "retitled", "body-only", "legacy", "newly-enabled", "missing", "malformed")
        for variant in variants:
            with self.subTest(variant=variant), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                directory, profile, receipt = self.make_project(root)
                changed = POLICY
                expected_skip = variant in {"current", "unrelated", "legacy", "newly-enabled"}
                if variant == "unrelated":
                    changed = replace(POLICY, max_age_days=3, blocking_languages=())
                if variant == "disabled":
                    changed = replace(POLICY, triage_exclusions=())
                if variant in {"retitled", "body-only"}:
                    meta = yaml.safe_load((directory / "meta.yaml").read_text(encoding="utf-8"))
                    meta["title"] = "Backend Engineer"
                    (directory / "meta.yaml").write_text(yaml.safe_dump(meta), encoding="utf-8")
                    if variant == "body-only":
                        (directory / "job.md").write_text("Collaborate with sales and SRE teams", encoding="utf-8")
                if variant == "legacy":
                    receipt["triage_version"] = "deterministic-triage-v1"
                    (directory / "triage.yaml").write_text(yaml.safe_dump(receipt), encoding="utf-8")
                if variant == "newly-enabled":
                    write_triage(directory, policy=replace(POLICY, triage_exclusions=()))
                if variant == "missing":
                    (directory / "triage.yaml").unlink()
                if variant == "malformed":
                    (directory / "triage.yaml").write_text("[malformed", encoding="utf-8")
                (root / "config/selection-policy.yaml").write_text(yaml.safe_dump(asdict(changed)), encoding="utf-8")
                before = {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()}
                meta = yaml.safe_load((directory / "meta.yaml").read_text(encoding="utf-8"))
                document = {"meta": meta, "job_text": (directory / "job.md").read_text(encoding="utf-8"), "triage": None}
                if variant not in {"missing", "malformed"}:
                    document["triage"] = yaml.safe_load((directory / "triage.yaml").read_text(encoding="utf-8"))
                self.assertEqual(expected_skip, should_skip_model(directory, policy=changed))
                self.assertEqual(expected_skip, snapshot_should_skip(document, policy=changed))
                self.assertEqual(expected_skip, eligible(directory, "skipped", 65, 7, selection_policy=changed))
                self.assertEqual(expected_skip, _eligible_document(meta, document, "skipped", 65, 7, selection_policy=changed))
                snapshot = load_catalog_snapshot(root / "registry")
                rows = queue_items("analyze", root, root / "registry", [profile], _snapshot=snapshot, selection_policy=changed)
                self.assertEqual(not expected_skip, bool(rows))
                operational = CatalogSnapshot(snapshot.vacancies, {directory.name: document})
                with patch("jobintel.workflow_api.should_skip_model", side_effect=AssertionError("snapshot fallback")):
                    rows = queue_items("analyze", root, root / "registry", [profile], _snapshot=operational, selection_policy=changed)
                self.assertEqual(not expected_skip, bool(rows))
                self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir() if path.is_file()})
                output = StringIO()
                with patch("jobintel.cli.__file__", str(root / "jobintel/cli.py")), patch("jobintel.cli.load_env", return_value={}), redirect_stdout(output):
                    code = main(["pending", "analyze", "all", "--workflow", "analyze", "--registry", str(root / "registry"), "--profile", str(profile)])
                self.assertEqual(0, code, output.getvalue())
                self.assertEqual([] if expected_skip else [str(directory)], output.getvalue().splitlines())

    def test_invalid_receipts_do_not_turn_title_into_skip_without_valid_history(self) -> None:
        meta = {"id": "one", "title": "SRE"}
        valid = evaluate_triage(meta, "Build Go services", policy=POLICY)
        invalid = [None, [], {}, valid | {"schema_version": True}, valid | {"skip_model": "true"},
                   valid | {"confidence": []}, valid | {"triage_version": {}}, valid | {"vacancy_id": "other"}]
        for receipt in invalid:
            with self.subTest(receipt=receipt):
                self.assertFalse(snapshot_should_skip({"meta": meta, "job_text": "Go", "triage": receipt}, policy=POLICY))

    def test_invalid_policy_fails_before_cli_fetch_lock_or_metadata_migration(self) -> None:
        for command in (["all"], ["triage"], ["pending", "analyze", "all", "--workflow", "analyze"]):
            with self.subTest(command=command), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / "config").mkdir()
                (root / "config/selection-policy.yaml").write_text("schema_version: 999", encoding="utf-8")
                with patch("jobintel.cli.__file__", str(root / "jobintel/cli.py")), patch("jobintel.cli.load_env", return_value={}), patch("jobintel.cli.workflow_lock") as lock, patch("jobintel.cli.discover_collectors") as discover, patch("jobintel.cli._collect_selected_jobs") as fetch, patch("jobintel.cli.Registry.migrate_metadata") as migrate, redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                    result = main(command + ["--registry", str(root / "registry")])
                self.assertNotEqual(0, result)
                lock.assert_not_called()
                discover.assert_not_called()
                fetch.assert_not_called()
                migrate.assert_not_called()
                self.assertFalse((root / "registry").exists())

    def test_invalid_policy_fails_before_archive_access_and_command_lock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "config/selection-policy.yaml").write_text("schema_version: 999", encoding="utf-8")
            with patch("scripts.archive_jobs.op.get_store") as store, self.assertRaises(SelectionPolicyError):
                archive(root, "skipped", 65)
            store.assert_not_called()
            with patch("sys.argv", ["archive_jobs.py", "skipped", "--project-root", str(root)]), patch("scripts.archive_jobs.workflow_lock") as lock, self.assertRaises(SelectionPolicyError):
                archive_main()
            lock.assert_not_called()
            self.assertFalse((root / "archives").exists())
            self.assertFalse((root / "registry").exists())

    def test_invalid_policy_fails_before_library_collector_fetch_or_workflow_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            path = root / "config/selection-policy.yaml"
            path.write_text("schema_version: 999", encoding="utf-8")
            (root / "config/codex-workflows.yaml").write_bytes((ROOT / "config/codex-workflows.yaml").read_bytes())
            collector = Mock()
            with patch("jobintel.cli.DEFAULT_SELECTION_POLICY_PATH", path), self.assertRaises(SelectionPolicyError):
                _run_collector("synthetic", collector, Registry(root / "registry"), RejectedRegistry(root / "registry"), limit=None)
            collector.fetch.assert_not_called()
            with patch("jobintel.workflow_api.load_catalog_snapshot") as snapshot, self.assertRaises(SelectionPolicyError):
                workflow_report(root, root / "registry", {}, [], 10)
            snapshot.assert_not_called()

    def test_collection_loads_policy_once_before_fetch_and_applies_new_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            changed = replace(POLICY, target_technologies=("python",), max_age_days=10 ** 1000)
            (root / "config/selection-policy.yaml").write_text(yaml.safe_dump(asdict(changed)), encoding="utf-8")
            events = []

            class Collector:
                def fetch(self):
                    events.append("fetch")
                    return [job(description="Build Python services.", published_at="0001-01-01T00:00:00Z")]

            def load(path):
                result = load_selection_policy(path)
                events.append("policy")
                return result

            with patch("jobintel.cli.__file__", str(root / "jobintel/cli.py")), patch("jobintel.cli.load_env", return_value={}), patch("jobintel.cli.discover_collectors", return_value={"synthetic": Collector()}), patch("jobintel.cli.load_selection_policy", side_effect=load) as loader, redirect_stdout(StringIO()), redirect_stderr(StringIO()):
                code = main(["synthetic", "--registry", str(root / "registry")])
            self.assertEqual(0, code)
            self.assertEqual(["policy", "fetch"], events)
            loader.assert_called_once_with(root / "config/selection-policy.yaml")
            self.assertEqual(1, len(list((root / "registry/jobs").glob("*/meta.yaml"))))
            self.assertEqual([], list((root / "registry/rejected").glob("*/meta.yaml")))

    def test_triage_command_and_workflow_report_load_once_per_boundary(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            directory, profile, _ = self.make_project(root)
            changed = replace(POLICY, triage_exclusions=())
            (root / "config/selection-policy.yaml").write_text(yaml.safe_dump(asdict(changed)), encoding="utf-8")
            with patch("jobintel.cli.__file__", str(root / "jobintel/cli.py")), patch("jobintel.cli.load_selection_policy", wraps=load_selection_policy) as loader, redirect_stdout(StringIO()):
                code = main(["triage", "--registry", str(root / "registry")])
            self.assertEqual(0, code)
            loader.assert_called_once_with(root / "config/selection-policy.yaml")
            self.assertFalse(yaml.safe_load((directory / "triage.yaml").read_text(encoding="utf-8"))["skip_model"])
            with patch("jobintel.workflow_api.load_selection_policy", wraps=load_selection_policy) as loader:
                report = workflow_report(root, root / "registry", {}, [profile], 10)
            loader.assert_called_once_with(root / "config/selection-policy.yaml")
            self.assertEqual(1, report["summary"]["pending_analyze"])
