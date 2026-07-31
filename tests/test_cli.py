from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import yaml

from jobintel.cli import _run_collector, _run_doctor, main
from jobintel.models import NormalizedJob
from jobintel.prefilter import RejectedRegistry
from jobintel.registry import Registry


class CliTests(unittest.TestCase):
    def test_offline_commands_do_not_parse_source_env(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            env_path = root / "broken.env"
            env_path.write_text("this is not dotenv\n", encoding="utf-8")
            registry = Registry(
                registry_root,
                clock=lambda: datetime(2026, 7, 23, tzinfo=timezone.utc),
                id_factory=lambda: "vacancy-1",
            )
            created = registry.upsert(
                NormalizedJob(
                    source="direct",
                    source_job_id="job-1",
                    source_url="https://example.test/jobs/1",
                    title="Backend Engineer",
                    company="Example",
                    description="Build services.",
                )
            )

            with redirect_stdout(StringIO()):
                self.assertEqual(
                    0,
                    main(["reindex", "--registry", str(registry_root), "--env", str(env_path)]),
                )
                self.assertEqual(
                    0,
                    main(
                        [
                            "status",
                            created.vacancy_id,
                            "reviewing",
                            "--registry",
                            str(registry_root),
                            "--env",
                            str(env_path),
                        ]
                    ),
                )
                with patch(
                    "jobintel.cli.generate_catalog",
                    return_value=SimpleNamespace(monthly=False, changed_files=[], vacancies=1),
                ):
                    self.assertEqual(
                        0,
                        main(
                            ["catalog", "--registry", str(registry_root), "--env", str(env_path)]
                        ),
                    )

    def test_add_manual_publishes_manual_vacancy_with_priority(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            draft = root / "manual.yaml"
            draft.write_text(
                "\n".join(
                    [
                        "source_url: https://example.test/jobs/42",
                        "company: Priority Co",
                        "title: Platform Engineer",
                        "description: Build internal platforms.",
                        "analysis_priority: 100",
                        "remote: true",
                        "",
                    ]
                ),
                encoding="utf-8",
            )

            output = StringIO()
            with redirect_stdout(output):
                exit_code = main(["add-manual", "--registry", str(registry_root), "--input", str(draft)])

            self.assertEqual(0, exit_code)
            self.assertIn("Manual job created", output.getvalue())
            meta_path = next((registry_root / "jobs").glob("*/meta.yaml"))
            meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
            self.assertEqual("manual", meta["data_source"])
            self.assertEqual(100, meta["analysis_priority"])
            self.assertEqual("manual", meta["sources"][0]["source"])

    def test_collector_limit_is_per_source(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            jobs = [
                NormalizedJob(
                    source="direct",
                    source_job_id=f"job-{index}",
                    source_url=f"https://example.test/jobs/{index}",
                    title=f"Backend Engineer {index}",
                    company="Example",
                    description="Build services.",
                )
                for index in range(3)
            ]

            class FakeCollector:
                name = "fake"

                def fetch(self):
                    yield from jobs

            registry = Registry(registry_root)
            rejected = RejectedRegistry(registry_root)
            first = _run_collector("fake", FakeCollector(), registry, rejected, limit=2)
            second = _run_collector("fake2", FakeCollector(), registry, rejected, limit=2)

            self.assertEqual(2, first.fetched)
            self.assertTrue(first.limit_reached)
            self.assertEqual(2, second.fetched)
            self.assertTrue(second.limit_reached)

    def test_top_lists_analyzed_active_vacancies_without_source_env(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            env_path = root / "broken.env"
            env_path.write_text("this is not dotenv\n", encoding="utf-8")
            registry = Registry(
                registry_root,
                clock=lambda: datetime(2026, 7, 23, tzinfo=timezone.utc),
                id_factory=lambda: "vacancy-1",
            )
            first = registry.upsert(
                NormalizedJob(
                    source="direct",
                    source_job_id="job-1",
                    source_url="https://example.test/jobs/1",
                    title="Backend Engineer",
                    company="Example",
                    description="Build services.",
                )
            )
            registry.update_status(first.vacancy_id, "closed")
            registry = Registry(
                registry_root,
                clock=lambda: datetime(2026, 7, 24, tzinfo=timezone.utc),
                id_factory=lambda: "vacancy-2",
            )
            second = registry.upsert(
                NormalizedJob(
                    source="direct",
                    source_job_id="job-2",
                    source_url="https://example.test/jobs/2",
                    title="Senior Backend Engineer",
                    company="Example",
                    description="Build services.",
                )
            )
            third = registry.upsert(
                NormalizedJob(
                    source="direct",
                    source_job_id="job-3",
                    source_url="https://example.test/jobs/3",
                    title="Platform Engineer",
                    company="Acme",
                    description="Build platforms.",
                )
            )
            _write_match(registry_root, first.directory, 99)
            _write_match(registry_root, second.directory, 84)
            _write_match(registry_root, third.directory, 91)

            output = StringIO()
            with redirect_stdout(output):
                self.assertEqual(
                    0,
                    main(["top", "5", "--registry", str(registry_root), "--env", str(env_path)]),
                )

            text = output.getvalue()
            self.assertIn("Top vacancies: 2", text)
            self.assertIn("1. 91/100 Acme", text)
            self.assertIn("2. 84/100 Example", text)
            self.assertNotIn("99/100", text)

    def test_doctor_ci_skips_only_host_local_converter_checks(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / "config").mkdir()
            (root / "config" / "codex-workflows.yaml").write_text(
                yaml.safe_dump(
                    {
                        "schema_version": 1,
                        "prepare_min_score": 65,
                        "priority_score": 75,
                        "prepare_max_age_days": 7,
                        "workflows": {
                            "analyze": {
                                "model": "gpt-5.6-luna",
                                "reasoning": "low",
                                "model_label": "codex:gpt-5.6-luna:low",
                            },
                            "prepare": {
                                "model": "gpt-5.6-terra",
                                "reasoning": "medium",
                                "model_label": "codex:gpt-5.6-terra:medium",
                            },
                        },
                    },
                    sort_keys=False,
                ),
                encoding="utf-8",
            )
            registry_root = root / "registry"
            candidate = registry_root / "candidate"
            candidate.mkdir(parents=True)
            (candidate / "linkedin-profile.md").write_text("LinkedIn\n", encoding="utf-8")
            (candidate / "backend-engineer-cv.md").write_text("CV\n", encoding="utf-8")
            prompts = root / "prompts"
            prompts.mkdir()
            (prompts / "vacancy-match.md").write_text("Match\n", encoding="utf-8")
            (prompts / "vacancy-application.md").write_text("Apply\n", encoding="utf-8")
            sources = root / "sources"
            sources.mkdir()
            env_path = sources / ".env"
            env_path.write_text("", encoding="utf-8")
            args = SimpleNamespace(
                arguments=[],
                force=False,
                profile=None,
                input=None,
                workflow=None,
                ci=True,
            )

            with patch(
                "jobintel.cli.HostMarkdownDocxConverter",
                return_value=SimpleNamespace(
                    script_path=root / "missing.ps1",
                    options_path=root / "missing.json",
                    powershell=None,
                ),
            ), redirect_stdout(StringIO()):
                self.assertEqual(0, _run_doctor(args, root, sources, registry_root, env_path))

            args.ci = False
            with patch(
                "jobintel.cli.HostMarkdownDocxConverter",
                return_value=SimpleNamespace(
                    script_path=root / "missing.ps1",
                    options_path=root / "missing.json",
                    powershell=None,
                ),
            ), redirect_stdout(StringIO()):
                self.assertEqual(1, _run_doctor(args, root, sources, registry_root, env_path))


def _write_match(registry_root: Path, directory: str, score: int) -> None:
    (registry_root / "jobs" / directory / "match.yaml").write_text(
        yaml.safe_dump(
            {
                "score": score,
                "recommendation": "strong_match",
                "summary": "Good fit.",
                "strengths": ["Backend"],
                "gaps": [],
                "concerns": [],
                "hard_rejection": False,
                "hard_rejection_reason": None,
            },
            allow_unicode=True,
            sort_keys=False,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    unittest.main()
