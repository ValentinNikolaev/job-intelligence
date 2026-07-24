from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from jobintel.matching import (
    MatchAnalyzer,
    build_analysis_pack,
    dump_analysis_pack,
    load_analysis_pack,
    publish_analysis_batch,
)
from jobintel.models import NormalizedJob
from jobintel.registry import Registry


def payload(score: int) -> dict[str, Any]:
    return {
        "score": score,
        "recommendation": "match",
        "summary": "Aligned backend role.",
        "strengths": ["Backend"],
        "gaps": [],
        "concerns": [],
        "hard_rejection": False,
        "hard_rejection_reason": None,
    }


class MatchingBatchTests(unittest.TestCase):
    def test_pack_round_trip_and_strict_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer with Python experience.", encoding="utf-8")
            registry = Registry(
                registry_root,
                clock=lambda: datetime(2026, 7, 23, tzinfo=timezone.utc),
                id_factory=iter(("one", "two")).__next__,
            )
            first = registry.upsert(NormalizedJob("direct", "1", "https://e/1", "Backend One", "Example", "Build APIs."))
            second = registry.upsert(NormalizedJob("direct", "2", "https://e/2", "Backend Two", "Example", "Build APIs."))
            pack = build_analysis_pack(registry_root, [profile], limit=2)
            pack_path = root / "pack.yaml"
            dump_analysis_pack(pack, pack_path)
            loaded = load_analysis_pack(pack_path)
            results = {item["directory"]: payload(80 + index) for index, item in enumerate(loaded["items"])}
            analyzer = MatchAnalyzer(registry_root, [profile], type("Client", (), {"model": "codex:test"})())
            publish_analysis_batch(loaded, results, analyzer)
            self.assertTrue((registry_root / "jobs" / first.directory / "match.yaml").is_file())
            self.assertTrue((registry_root / "jobs" / second.directory / "match.yaml").is_file())

    def test_batch_rejects_missing_result_before_writing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            registry = Registry(registry_root, id_factory=lambda: "one")
            created = registry.upsert(NormalizedJob("direct", "1", "https://e/1", "Backend", "Example", "Build APIs."))
            pack = build_analysis_pack(registry_root, [profile])
            with self.assertRaises(Exception):
                publish_analysis_batch(
                    {"items": list(pack.items)},
                    {},
                    MatchAnalyzer(registry_root, [profile], type("Client", (), {"model": "codex:test"})()),
                )
            self.assertFalse((registry_root / "jobs" / created.directory / "match.yaml").exists())

    def test_analysis_pack_orders_priority_vacancies_first(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            ids = iter(("normal", "priority"))
            now = datetime(2026, 7, 23, tzinfo=timezone.utc)
            registry = Registry(registry_root, clock=lambda: now, id_factory=lambda: next(ids))
            normal = registry.upsert(NormalizedJob("direct", "1", "https://e/1", "Backend", "Example", "Build APIs."))
            priority = registry.upsert(
                NormalizedJob(
                    "manual",
                    "2",
                    "https://e/2",
                    "Platform Engineer",
                    "Priority Co",
                    "Build platforms.",
                    analysis_priority=100,
                )
            )

            pack = build_analysis_pack(registry_root, [profile], limit=1)

            self.assertEqual(priority.directory, pack.items[0]["directory"])
            self.assertNotEqual(normal.directory, pack.items[0]["directory"])


if __name__ == "__main__":
    unittest.main()
