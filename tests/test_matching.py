from __future__ import annotations

import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import yaml

from jobintel.matching import CodexMatchDraftClient, MatchAnalyzer, MatchError, PROMPT_VERSION
from jobintel.models import NormalizedJob
from jobintel.registry import Registry


ROOT = Path(__file__).resolve().parents[1]


def make_job(**overrides: object) -> NormalizedJob:
    values: dict[str, object] = {
        "source": "direct",
        "source_job_id": "job-1",
        "source_url": "https://example.test/jobs/1",
        "title": "Backend Engineer",
        "company": "Example",
        "description": "Build Python services. Remote in Europe.",
        "location": "Remote Europe",
        "remote": True,
        "employment_type": "full-time",
    }
    values.update(overrides)
    return NormalizedJob(**values)  # type: ignore[arg-type]


def match_payload(score: int = 84) -> dict[str, Any]:
    return {
        "score": score,
        "recommendation": "strong_match" if score >= 80 else "possible_match",
        "summary": "The role aligns with the documented backend experience.",
        "strengths": ["Backend responsibilities match"],
        "gaps": ["One preferred tool is not documented"],
        "concerns": ["Salary is not specified"],
        "hard_rejection": False,
        "hard_rejection_reason": None,
    }


class FakeClient:
    def __init__(self, payload: Mapping[str, Any] | None = None) -> None:
        self.payload = payload or match_payload()
        self.calls: list[tuple[str, Mapping[str, Any]]] = []

    def analyze(self, *, candidate_profile: str, vacancy: Mapping[str, Any]) -> Mapping[str, Any]:
        self.calls.append((candidate_profile, vacancy))
        return self.payload


class MatchingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.project = Path(self.temp.name)
        self.registry_root = self.project / "registry"
        self.profile = self.project / "profile.md"
        self.profile.write_text(
            "# Candidate\n\nExperienced backend engineer using Python. Prefers remote EU roles.\n",
            encoding="utf-8",
        )
        self.now = datetime(2026, 7, 22, 20, 0, tzinfo=timezone.utc)
        self.registry = Registry(
            self.registry_root,
            clock=lambda: self.now,
            id_factory=lambda: "vacancy-1",
        )
        created = self.registry.upsert(
            make_job(
                source_metadata={
                    "salary": {"currency": "EUR", "minimum": 70000},
                    "company_logo": "https://example.test/logo.png",
                    "discovered_by": [{"query": "python"}],
                }
            )
        )
        self.directory = self.registry_root / "jobs" / created.directory

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_analysis_writes_valid_files_and_skips_matching_versions(self) -> None:
        client = FakeClient()
        analyzer = MatchAnalyzer(
            self.registry_root,
            [self.profile],
            client,
            clock=lambda: self.now,
        )

        first = analyzer.analyze_directory(self.directory)
        before = (self.directory / "match.yaml").read_bytes()
        second = analyzer.analyze_directory(self.directory)

        match = yaml.safe_load(before.decode("utf-8"))
        markdown = (self.directory / "match.md").read_text(encoding="utf-8")
        self.assertEqual("analyzed", first.status)
        self.assertEqual("skipped", second.status)
        self.assertEqual(1, len(client.calls))
        self.assertEqual(before, (self.directory / "match.yaml").read_bytes())
        self.assertEqual(PROMPT_VERSION, match["prompt_version"])
        self.assertEqual("2026-07-22T20:00:00Z", match["analyzed_at"])
        self.assertIn("**Score:** 84/100", markdown)
        self.assertIn("## Why it matches", markdown)
        sent_metadata = client.calls[0][1]["metadata"]["sources"][0]["metadata"]
        self.assertIn("salary", sent_metadata)
        self.assertNotIn("company_logo", sent_metadata)
        self.assertNotIn("discovered_by", sent_metadata)

    def test_profile_change_and_force_both_bypass_cache(self) -> None:
        client = FakeClient()
        analyzer = MatchAnalyzer(self.registry_root, [self.profile], client, clock=lambda: self.now)
        analyzer.analyze_directory(self.directory)

        self.profile.write_text("# Candidate\n\nPython and Go backend engineer.\n", encoding="utf-8")
        analyzer.analyze_directory(self.directory)
        analyzer.analyze_directory(self.directory, force=True)

        self.assertEqual(3, len(client.calls))

    def test_cloudflare_email_hash_and_updated_at_do_not_stale_analysis(self) -> None:
        (self.directory / "job.md").write_text(
            "Build Go services.\n\n"
            "Apply at [[email protected](/cdn-cgi/l/email-protection#abc123)]\n",
            encoding="utf-8",
        )
        client = FakeClient()
        analyzer = MatchAnalyzer(self.registry_root, [self.profile], client, clock=lambda: self.now)
        analyzer.analyze_directory(self.directory)

        meta_path = self.directory / "meta.yaml"
        meta = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
        meta["updated_at"] = "2026-07-22T21:00:00Z"
        meta_path.write_text(yaml.safe_dump(meta, allow_unicode=True, sort_keys=False), encoding="utf-8")
        (self.directory / "job.md").write_text(
            "Build Go services.\n\n"
            "Apply at [[email protected](/cdn-cgi/l/email-protection#def456)]\n",
            encoding="utf-8",
        )

        second = analyzer.analyze_directory(self.directory)

        self.assertEqual("skipped", second.status)
        self.assertEqual(1, len(client.calls))
        self.assertTrue(analyzer.is_current(self.directory))

    def test_invalid_model_result_is_not_saved(self) -> None:
        invalid = match_payload()
        invalid["score"] = 101
        analyzer = MatchAnalyzer(self.registry_root, [self.profile], FakeClient(invalid))

        with self.assertRaises(MatchError):
            analyzer.analyze_directory(self.directory)

        self.assertFalse((self.directory / "match.yaml").exists())
        self.assertFalse((self.directory / "match.md").exists())

    def test_codex_draft_client_reads_yaml_without_network(self) -> None:
        draft = self.project / "match-draft.yaml"
        draft.write_text(
            yaml.safe_dump(match_payload(), allow_unicode=True, sort_keys=False),
            encoding="utf-8",
        )
        client = CodexMatchDraftClient(
            draft, model="codex:gpt-5.6-luna:low"
        )
        result = client.analyze(candidate_profile="Profile", vacancy={"title": "Engineer"})

        self.assertEqual(84, result["score"])
        self.assertEqual("codex:gpt-5.6-luna:low", client.model)

    def test_match_prompt_documents_candidate_specific_score_adjustments(self) -> None:
        prompt = (ROOT / "prompts" / "vacancy-match.md").read_text(encoding="utf-8")

        self.assertIn("decrease the score for roles that are not remote", prompt)
        self.assertIn("decrease the score when Spring Boot is a central requirement", prompt)
        self.assertIn("decrease the score for Site Reliability Engineer or SRE roles", prompt)
        self.assertIn("increase the score when the role offers a relocation package", prompt)
        self.assertIn("increase the score when PHP is a meaningful part of the role", prompt)
        self.assertIn("increase the score when Go or Golang is a meaningful part of the role", prompt)
        self.assertIn("increase the score when the role is based in Roma or Rome", prompt)
        self.assertIn("increase the score when the role involves support automation", prompt)
        self.assertIn("increase the score when the role is in the mail/email domain", prompt)
        self.assertIn("increase the score when the role is in the support domain", prompt)

    def test_index_orders_analyzed_scores_then_unanalyzed(self) -> None:
        ids = iter(("vacancy-2", "vacancy-3"))
        registry = Registry(self.registry_root, clock=lambda: self.now, id_factory=lambda: next(ids))
        high = registry.upsert(
            make_job(
                source_job_id="job-2",
                source_url="https://example.test/jobs/2",
                title="Platform Engineer",
            )
        )
        registry.upsert(
            make_job(
                source_job_id="job-3",
                source_url="https://example.test/jobs/3",
                title="Data Engineer",
            )
        )
        analyzer = MatchAnalyzer(
            self.registry_root,
            [self.profile],
            FakeClient(match_payload(92)),
            clock=lambda: self.now,
        )
        analyzer.analyze_directory(self.registry_root / "jobs" / high.directory)

        registry.regenerate_index()
        index = (self.registry_root / "index.md").read_text(encoding="utf-8")
        self.assertLess(index.index("Platform Engineer"), index.index("Backend Engineer"))
        self.assertIn("| 92 |", index)
        self.assertIn("Not analyzed", index)


if __name__ == "__main__":
    unittest.main()
