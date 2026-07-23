from __future__ import annotations

import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from jobintel.cli import _run_collector, main
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


if __name__ == "__main__":
    unittest.main()
