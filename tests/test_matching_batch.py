from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml

from jobintel.matching import (
    MAX_ANALYSIS_BATCH_SIZE,
    MatchError,
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
    def test_pack_excludes_current_analysis_for_selected_model(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer with Python experience.", encoding="utf-8")
            registry = Registry(registry_root, id_factory=iter(("one", "two")).__next__)
            first = registry.upsert(NormalizedJob("direct", "1", "https://e/1", "Backend One", "Example", "Build APIs."))
            second = registry.upsert(NormalizedJob("direct", "2", "https://e/2", "Backend Two", "Example", "Build APIs."))
            pack = build_analysis_pack(registry_root, [profile], limit=1, model="codex:test")
            analyzer = MatchAnalyzer(registry_root, [profile], type("Client", (), {"model": "codex:test"})())
            publish_analysis_batch({"items": list(pack.items)}, {pack.items[0]["directory"]: payload(80)}, analyzer)
            next_pack = build_analysis_pack(registry_root, [profile], limit=1, model="codex:test")
            self.assertNotEqual(pack.items[0]["directory"], next_pack.items[0]["directory"])
            self.assertIn(next_pack.items[0]["directory"], {first.directory, second.directory})

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
            self.assertEqual(
                {"https://e/1", "https://e/2"},
                {item["source_url"] for item in pack.items},
            )
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

    def test_batch_rejects_pack_that_became_current_before_publish(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            registry = Registry(registry_root, id_factory=lambda: "one")
            created = registry.upsert(
                NormalizedJob("direct", "1", "https://e/1", "Backend", "Example", "Build APIs.")
            )
            pack = build_analysis_pack(registry_root, [profile], model="codex:test")
            results = {created.directory: payload(82)}
            analyzer = MatchAnalyzer(
                registry_root,
                [profile],
                type("Client", (), {"model": "codex:test"})(),
            )
            publish_analysis_batch({"items": list(pack.items)}, results, analyzer)

            with self.assertRaisesRegex(MatchError, "analysis pack is stale"):
                publish_analysis_batch({"items": list(pack.items)}, results, analyzer)

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

    def test_analysis_pack_can_be_scoped_to_selected_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            ids = iter(("first", "selected"))
            registry = Registry(registry_root, id_factory=lambda: next(ids))
            registry.upsert(
                NormalizedJob("direct", "1", "https://e/1", "Backend One", "Example", "Build APIs.")
            )
            selected = registry.upsert(
                NormalizedJob("direct", "2", "https://e/2", "Backend Two", "Example", "Build APIs.")
            )
            selected_directory = registry_root / "jobs" / selected.directory

            pack = build_analysis_pack(
                registry_root,
                [profile],
                directories=[selected_directory],
            )

            self.assertEqual([selected.directory], [item["directory"] for item in pack.items])

    def test_analysis_pack_skips_applied_vacancies(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            ids = iter(("applied", "fresh"))
            registry = Registry(registry_root, id_factory=lambda: next(ids))
            applied = registry.upsert(NormalizedJob("direct", "1", "https://e/1", "Backend One", "Example", "Build APIs."))
            fresh = registry.upsert(NormalizedJob("direct", "2", "https://e/2", "Backend Two", "Example", "Build APIs."))
            registry.update_status(applied.vacancy_id, "applied")

            pack = build_analysis_pack(registry_root, [profile])

            self.assertEqual([fresh.directory], [item["directory"] for item in pack.items])

    def test_batch_publish_skips_vacancy_applied_after_pack_creation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            registry = Registry(registry_root, id_factory=lambda: "one")
            created = registry.upsert(NormalizedJob("direct", "1", "https://e/1", "Backend", "Example", "Build APIs."))
            pack = build_analysis_pack(registry_root, [profile])
            registry.update_status(created.vacancy_id, "applied")

            summary = publish_analysis_batch(
                {"items": list(pack.items)},
                {created.directory: payload(82)},
                MatchAnalyzer(registry_root, [profile], type("Client", (), {"model": "codex:test"})()),
            )

            self.assertEqual(1, summary.selected)
            self.assertEqual(0, summary.analyzed)
            self.assertEqual(1, summary.skipped)
            self.assertFalse((registry_root / "jobs" / created.directory / "match.yaml").exists())

    def test_analysis_pack_caps_default_batch_and_rejects_invalid_limits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            ids = iter(f"job-{index}" for index in range(MAX_ANALYSIS_BATCH_SIZE + 1))
            registry = Registry(registry_root, id_factory=lambda: next(ids))
            for index in range(MAX_ANALYSIS_BATCH_SIZE + 1):
                registry.upsert(
                    NormalizedJob(
                        "direct",
                        str(index),
                        f"https://e/{index}",
                        f"Backend {index}",
                        "Example",
                        "Build APIs.",
                    )
                )

            self.assertEqual(
                MAX_ANALYSIS_BATCH_SIZE,
                len(build_analysis_pack(registry_root, [profile]).items),
            )
            for limit in (0, -1, MAX_ANALYSIS_BATCH_SIZE + 1):
                with self.subTest(limit=limit), self.assertRaises(MatchError):
                    build_analysis_pack(registry_root, [profile], limit=limit)

    def test_analysis_pack_skips_all_post_analysis_statuses(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            registry_root = root / "registry"
            profile = root / "profile.md"
            profile.write_text("Backend engineer.", encoding="utf-8")
            statuses = (
                "prepared",
                "applied",
                "interview",
                "technical_interview",
                "final_interview",
                "offer",
                "rejected",
                "withdrawn",
                "closed",
            )
            ids = iter(statuses)
            registry = Registry(registry_root, id_factory=lambda: next(ids))
            for index, status in enumerate(statuses):
                created = registry.upsert(
                    NormalizedJob(
                        "direct",
                        str(index),
                        f"https://e/{index}",
                        f"Backend {index}",
                        "Example",
                        "Build APIs.",
                    )
                )
                registry.update_status(created.vacancy_id, status)

            self.assertEqual((), build_analysis_pack(registry_root, [profile]).items)


if __name__ == "__main__":
    unittest.main()
