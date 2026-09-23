from __future__ import annotations

import re
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


class CollectionSafetyContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.root = Path(__file__).resolve().parents[1]

    def _read(self, path: str) -> str:
        return (self.root / path).read_text(encoding="utf-8")

    def test_run_and_report_softens_only_dedicated_source_error_code(self) -> None:
        script = self._read(".github/scripts/run-and-report.sh")
        self.assertRegex(script, r"failure_mode.*soft")
        self.assertRegex(script, r'\[ "\$status" \] -eq 75|\[ "\$status" -eq 75')
        # A generic soft-mode branch would hide storage, lease, or deterministic
        # failures and is expressly outside the collection safeguard contract.
        self.assertNotRegex(script, r'if \[ "\$status" -ne 0 \].*failure_mode.*soft.*exit 0')

    def test_collection_workflow_does_not_use_hour_long_lock_wait(self) -> None:
        workflow = self._read(".github/workflows/job-intelligence-collection.yml")
        self.assertNotIn("--lock-timeout-seconds 3600", workflow)
        self.assertEqual(2, len(re.findall(r"--lock-timeout-seconds(?:=| )90", workflow)))

    def _main_with(
        self,
        collector,
        *,
        store_error=None,
        lock_error=None,
        lock_enter=None,
        usage_error=None,
    ):
        import jobintel.cli as cli

        registry = MagicMock()
        rejected = MagicMock()
        usage = MagicMock()
        if usage_error:
            usage.record.side_effect = usage_error
        lock = MagicMock()
        lock.__enter__.side_effect = lock_enter or lock_error
        lock.__exit__.return_value = False
        store_patch = patch.object(cli, "_store_collected_jobs", side_effect=store_error) if store_error else patch.object(cli, "_store_collected_jobs", side_effect=lambda name, summary, jobs, registry, rejected, **kwargs: summary)
        with patch.object(cli, "load_env", return_value={}), patch.object(
            cli, "discover_collectors", return_value={"fake": collector}
        ), patch.object(cli, "Registry", return_value=registry), patch.object(
            cli, "RejectedRegistry", return_value=rejected
        ), patch.object(cli, "ApiUsageLog", return_value=usage), patch.object(
            cli, "load_company_retry_rules", return_value=()
        ), patch.object(cli.op, "project_root", return_value=self.root), patch.object(
            cli, "workflow_lock", return_value=lock
        ), store_patch:
            return cli.main(["fake", "--sources", str(self.root), "--registry", str(self.root)])

    def test_complete_source_outage_is_fatal(self) -> None:
        class Failing:
            def fetch(self):
                raise RuntimeError("temporary source outage")

        self.assertEqual(1, self._main_with(Failing()))

    def test_partial_composite_source_failure_returns_tolerated_exit(self) -> None:
        class PartiallyFailing:
            sources_total = 3
            sources_failed = 1
            errors = 1

            def fetch(self):
                return []

        self.assertEqual(75, self._main_with(PartiallyFailing()))

    def test_fetch_completes_before_writer_lock_entry(self) -> None:
        events: list[str] = []

        class Empty:
            def fetch(self):
                events.append("fetch")
                return []

        def enter_lock():
            events.append("lock")

        self.assertEqual(0, self._main_with(Empty(), lock_enter=enter_lock))
        self.assertEqual(["fetch", "lock"], events)

    def test_persistence_and_lock_failures_are_fatal(self) -> None:
        class Empty:
            def fetch(self):
                return []

        from jobintel.storage_contract import StorageError
        self.assertEqual(1, self._main_with(Empty(), store_error=StorageError("write failed")))
        self.assertEqual(1, self._main_with(Empty(), lock_error=RuntimeError("lock failed")))

    def test_api_usage_failure_is_fatal(self) -> None:
        class Empty:
            def fetch(self):
                return []

        from jobintel.storage_contract import StorageError

        self.assertEqual(1, self._main_with(Empty(), usage_error=StorageError("usage failed")))

    def test_per_row_storage_error_is_not_converted_to_source_error(self) -> None:
        import jobintel.cli as cli
        from jobintel.models import CollectorSummary, NormalizedJob
        from jobintel.storage_contract import StorageLeaseError

        job = NormalizedJob(
            source="test",
            source_job_id="job-1",
            source_url="https://example.test/jobs/1",
            title="PHP Backend Engineer",
            company="Example",
            description="Build PHP services.",
        )
        registry = MagicMock()
        registry.upsert.side_effect = StorageLeaseError("lease lost")

        with self.assertRaises(StorageLeaseError):
            cli._store_collected_jobs(
                "test",
                CollectorSummary(source="test", fetched=1),
                [job],
                registry,
                MagicMock(),
            )


if __name__ == "__main__":
    unittest.main()
