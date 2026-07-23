from __future__ import annotations

import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from typing import Any, Mapping

import yaml

from jobintel.cli import main
from jobintel.matching import MatchAnalyzer
from jobintel.models import CollectorSummary, NormalizedJob
from jobintel.api_usage import ApiUsageLog
from jobintel.registry import Registry
from jobintel.workflow_api import catalog_vacancies, queue_response, source_usage, workflow_summary


class FakeMatchClient:
    model = "codex:gpt-5.6-luna:low"

    def __init__(self, score: int) -> None:
        self.score = score

    def analyze(self, **_: object) -> Mapping[str, Any]:
        return {
            "score": self.score,
            "recommendation": "match",
            "summary": "Evidence-based fit.",
            "strengths": ["Backend experience"],
            "gaps": [],
            "concerns": [],
            "hard_rejection": False,
            "hard_rejection_reason": None,
        }


class WorkflowApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.registry_root = self.project / "registry"
        self.sources = self.project / "sources"
        self.sources.mkdir()
        (self.project / "config").mkdir()
        (self.project / "config" / "codex-workflows.yaml").write_text(
            yaml.safe_dump(
                {
                    "schema_version": 1,
                    "prepare_min_score": 65,
                    "priority_score": 75,
                    "workflows": {
                        "analyze": {
                            "model": "gpt-5.6-luna",
                            "reasoning": "low",
                            "model_label": "codex:gpt-5.6-luna:low",
                        },
                        "prepare": {
                            "model": "gpt-5.5",
                            "reasoning": "medium",
                            "model_label": "codex:gpt-5.5:medium",
                        },
                        "prepare_priority": {
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
        (self.project / "prompts").mkdir()
        (self.project / "prompts" / "vacancy-match.md").write_text("Match one vacancy.\n", encoding="utf-8")
        (self.project / "prompts" / "vacancy-application.md").write_text("Prepare one vacancy.\n", encoding="utf-8")
        self.profile = self.project / "profile.md"
        self.profile.write_text("# Candidate\n\nBackend engineer using Go.\n", encoding="utf-8")
        registry = Registry(
            self.registry_root,
            clock=lambda: datetime(2026, 7, 23, tzinfo=timezone.utc),
            id_factory=lambda: "vacancy-analyze",
        )
        self.pending = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="pending",
                source_url="https://example.test/pending",
                title="Backend Engineer",
                company="Example",
                description="Build Go services.",
            )
        )
        registry = Registry(
            self.registry_root,
            clock=lambda: datetime(2026, 7, 24, tzinfo=timezone.utc),
            id_factory=lambda: "vacancy-prepare",
        )
        self.preparable = registry.upsert(
            NormalizedJob(
                source="direct",
                source_job_id="prepare",
                source_url="https://example.test/prepare",
                title="Senior Backend Engineer",
                company="Acme",
                description="Build APIs.",
            )
        )
        MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeMatchClient(72),
            clock=lambda: datetime(2026, 7, 24, tzinfo=timezone.utc),
        ).analyze_directory(self.registry_root / "jobs" / self.preparable.directory)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_summary_and_queues_are_json_ready(self) -> None:
        summary = workflow_summary(self.project, self.registry_root, {}, [self.profile])
        analyze = queue_response("analyze", self.project, self.registry_root, [self.profile])
        prepare = queue_response("prepare", self.project, self.registry_root, [self.profile])

        self.assertEqual(2, summary["vacancies_total"])
        self.assertEqual(1, summary["pending_analyze"])
        self.assertEqual(1, summary["pending_prepare"])
        self.assertEqual(self.pending.directory, analyze["items"][0]["directory"])
        self.assertEqual(self.preparable.directory, prepare["items"][0]["directory"])
        self.assertEqual("ok", prepare["items"][0]["budget_status"])

    def test_source_usage_and_catalog_contracts(self) -> None:
        ApiUsageLog(self.registry_root / "source-api-usage.yaml").record(
            CollectorSummary(source="adzuna", fetched=3, created=2, rejected=1, api_requests=4),
            run_started_at="2026-07-23T10:00:00Z",
        )

        usage = source_usage(self.registry_root)
        catalog = catalog_vacancies(self.registry_root)

        self.assertEqual("adzuna", usage["sources"][0]["source"])
        self.assertEqual(4, usage["sources"][0]["total_requests"])
        self.assertEqual(2, len(catalog["vacancies"]))
        self.assertIn("artifacts", catalog["vacancies"][0])

    def test_cli_api_outputs_json_without_source_env(self) -> None:
        broken_env = self.sources / ".env"
        broken_env.write_text("not dotenv\n", encoding="utf-8")
        output = StringIO()

        with redirect_stdout(output):
            exit_code = main(
                [
                    "api",
                    "queues",
                    "prepare",
                    "--json",
                    "--registry",
                    str(self.registry_root),
                    "--sources",
                    str(self.sources),
                    "--env",
                    str(broken_env),
                    "--profile",
                    str(self.profile),
                ]
            )

        self.assertEqual(0, exit_code)
        payload = json.loads(output.getvalue())
        self.assertEqual("prepare", payload["workflow"])
        self.assertEqual(1, len(payload["items"]))


if __name__ == "__main__":
    unittest.main()
