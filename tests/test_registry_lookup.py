from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from jobintel.models import NormalizedJob
from jobintel.registry import Registry


def job(url: str, *, company: str = "Acme Ltd", title: str = "Backend Engineer") -> NormalizedJob:
    return NormalizedJob(
        source="custom", source_job_id="incoming", source_url=url, company=company,
        title=title, description="Description", location="Remote", remote=True,
    )


def entry(name: str, url: str, *, company: str = "Acme", title: str = "Backend Engineer",
          apply_url: str | None = None) -> dict:
    ref = {"source": "manual", "source_job_id": name, "url": url}
    if apply_url:
        ref["metadata"] = {"apply_url": apply_url}
    return {"path": Path(name), "meta": {
        "company": company, "title": title, "fingerprint": f"fingerprint-{name}",
        "sources": [ref],
    }}


class RegistryLookupTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.registry = Registry(Path(self.temp.name) / "registry", cache_entries=True)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def index(self, entries: list[dict]) -> None:
        self.registry._entries_cache = entries
        self.registry._rebuild_lookup_indexes()

    def assert_parity(self, incoming: NormalizedJob) -> dict | None:
        actual = self.registry._find_url_candidate_indexed(incoming)
        self.assertIs(
            self.registry._find_url_candidate(self.registry._entries_cache or [], incoming), actual
        )
        return actual

    def test_canonical_alias_and_apply_url_match_with_original_guards(self) -> None:
        direct = entry("direct", "https://job-boards.eu.greenhouse.io/acme/jobs/42")
        applied = entry("applied", "https://unrelated.test/one",
                        apply_url="https://careers.hostaway.com/o/backend/c/new")
        board = entry("board", "https://company.test/careers", title="PHP Architect")
        self.index([direct, applied, board])
        self.assertIs(direct, self.assert_parity(job("https://job-boards.greenhouse.io/acme/jobs/42")))
        self.assertIs(applied, self.assert_parity(job("https://careers.hostaway.com/o/backend")))
        self.assertIsNone(self.assert_parity(job("https://company.test/careers")))
        self.assertIsNone(self.assert_parity(job("https://careers.hostaway.com/o/backend", company="Other")))

    def test_ambiguity_and_replacement_remove_only_old_keys(self) -> None:
        first = entry("first", "https://company.test/jobs/42")
        second = entry("second", "https://company.test/jobs/42")
        self.index([first, second])
        incoming = job("https://company.test/jobs/42")
        self.assertIsNone(self.assert_parity(incoming))

        revised = dict(second["meta"])
        revised["sources"] = [{"source": "ashby", "source_job_id": "new-id",
                               "url": "https://company.test/jobs/43"}]
        revised["fingerprint"] = "new-fingerprint"
        self.registry._cache_replace_entry(second, revised)
        self.assertIs(first, self.assert_parity(incoming))
        self.assertIs(second, self.assert_parity(job("https://company.test/jobs/43")))
        self.assertIsNone(self.registry._find_source_indexed("manual", "second"))
        self.assertIs(second, self.registry._find_source_indexed("ashby", "new-id"))
        self.assertNotIn("fingerprint-second", self.registry._fingerprint_index)
        self.assertIs(second, self.registry._find_fingerprint_candidate_indexed("new-fingerprint", "custom"))

    def test_lookup_normalizes_only_incoming_url_after_index_build(self) -> None:
        self.index([entry(str(i), f"https://company.test/jobs/{i}") for i in range(1000)])
        from jobintel import registry as registry_module

        original = registry_module.canonical_vacancy_url
        with patch.object(registry_module, "canonical_vacancy_url", wraps=original) as canonical:
            for i in range(100):
                result = self.registry._find_url_candidate_indexed(job(f"https://company.test/jobs/{i}"))
                self.assertIsNotNone(result)
            self.assertEqual(100, canonical.call_count)

    def test_cached_upsert_uses_url_index_across_creation_and_update(self) -> None:
        ids = iter(["0dd976c5-c88d-4e17-8a81-62d62244e5aa",
                    "d9db0db9-0d52-4589-8f7a-1c2e1cd60e3b"])
        self.registry._id_factory = lambda: next(ids)
        first = self.registry.upsert(job("https://company.test/jobs/42"))
        merged = self.registry.upsert(NormalizedJob(
            source="manual", source_job_id="second", source_url="https://company.test/jobs/42",
            company="Acme", title="Backend Engineer", description="More detail",
            location="Rome", remote=True,
        ))
        self.assertEqual("merged", merged.status)
        self.assertEqual(first.vacancy_id, merged.vacancy_id)

        changed = self.registry.upsert(job("https://company.test/jobs/43"))
        self.assertEqual("updated", changed.status)
        self.assertIsNotNone(self.registry._find_url_candidate_indexed(job("https://company.test/jobs/43")))
        self.assertIsNotNone(self.registry._find_url_candidate_indexed(job("https://company.test/jobs/42")))
        self.assertEqual(first.directory, changed.directory)


if __name__ == "__main__":
    unittest.main()
