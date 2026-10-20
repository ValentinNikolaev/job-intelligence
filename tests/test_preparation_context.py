"""Preparation identities, source isolation and clarification failure boundaries."""
import copy
import hashlib
import tempfile
import unittest
from pathlib import Path

import yaml

from jobintel.application_review import validate_voice_review
from jobintel.applications import ApplicationError, _cv_export_stem, _validate_v2_grounding
from jobintel.career_coverage import CareerCoverageError, _corrected_roles, validate_career_coverage
from jobintel.evidence import EvidenceError, bootstrap_evidence_bank, validate_evidence_bank
from jobintel.preparation_context import PreparationContextError, load_preparation_context
from tests.preparation_fixtures import write_preparation_config


class PreparationContextTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.context = write_preparation_config(self.root)
        self.candidate = self.root / "registry/candidate"
        self.candidate.mkdir(parents=True)
        self.source = self.candidate / "linkedin-profile.md"
        self.source.write_text("# Candidate\n## Experience\n### Example\nEngineer\nJanuary 2022 - Present\n", encoding="utf-8")

    def update(self, change):
        path = self.root / "config/application-profile.yaml"
        profile = yaml.safe_load(path.read_text(encoding="utf-8"))
        change(profile)
        path.write_text(yaml.safe_dump(profile), encoding="utf-8")
        return load_preparation_context(self.root)

    def test_context_identity_ignores_unrelated_candidate_answers_and_newlines(self):
        original = self.context.version
        context = self.update(lambda value: value.update(candidate=dict(full_name="Another answer"), reusable_answers=dict(motivation="Changed")))
        self.assertEqual(original, context.version)
        editorial = self.root / "config/cv-editorial-knowledge.yaml"
        text = editorial.read_text(encoding="utf-8")
        editorial.write_bytes(text.replace("\n", "\r\n").encode("utf-8"))
        self.assertEqual(original, load_preparation_context(self.root).version)
        editorial.write_bytes(text.encode("utf-8"))
        self.assertEqual(original, load_preparation_context(self.root).version)

    def test_frozen_snapshot_cannot_be_mutated_through_nested_configuration(self):
        snapshot = self.context.preparation
        snapshot["career_scope"]["maximum_years_since_end"] = 1
        self.assertEqual(100, self.context.preparation["career_scope"]["maximum_years_since_end"])

    def test_missing_duplicate_unknown_and_traversal_configuration_fail_closed(self):
        original = (self.root / "config/application-profile.yaml").read_text(encoding="utf-8")
        for change in (
            lambda profile: profile["preparation"].update(unknown=True),
            lambda profile: profile["preparation"].update(candidate_directory="registry/../candidate"),
            lambda profile: profile["preparation"].update(candidate_directory="registry/jobs/example/application"),
            lambda profile: profile["preparation"].update(cv_owner_stem="../Other"),
            lambda profile: profile["preparation"]["career_scope"].update(maximum_years_since_end=True),
            lambda profile: profile["preparation"].update(employer_aliases={"Alpha": ["shared"], "Beta": ["shared"]}),
        ):
            (self.root / "config/application-profile.yaml").write_text(original, encoding="utf-8")
            with self.assertRaises(PreparationContextError):
                self.update(change)
        path = self.root / "config/application-profile.yaml"
        path.write_text(original + "\npreparation: {}\n", encoding="utf-8")
        with self.assertRaisesRegex(PreparationContextError, "duplicate"):
            load_preparation_context(self.root)
        path.unlink()
        with self.assertRaises(PreparationContextError):
            load_preparation_context(self.root)

    def test_profile_resolution_preserves_fallback_and_supplement_order(self):
        self.context = write_preparation_config(self.root, profile_sources=dict(
            preferred=["registry/candidate/compact.md"],
            fallback=["registry/candidate/linkedin-profile.md", "registry/candidate/cv.md"],
            supplements=["registry/candidate/confirmed-*.md"]))
        for name in ("cv.md", "confirmed-z.md", "confirmed-a.md"):
            (self.candidate / name).write_text(name, encoding="utf-8")
        self.assertEqual(["linkedin-profile.md", "cv.md", "confirmed-a.md", "confirmed-z.md"], [path.name for path in self.context.profile_paths])
        (self.candidate / "compact.md").write_text("Compact", encoding="utf-8")
        self.assertEqual(["compact.md", "confirmed-a.md", "confirmed-z.md"], [path.name for path in self.context.profile_paths])

    def test_alternate_context_cannot_use_previous_candidate_sources(self):
        bank = bootstrap_evidence_bank(self.root, [dict(id="example", source=dict(path="registry/candidate/linkedin-profile.md", quote="Engineer"))])
        alternate = write_preparation_config(self.root, candidate_directory="registry/other-candidate", evidence_bank="registry/other-evidence/bank.yaml", cv_owner_stem="OtherCandidate")
        self.assertNotEqual(self.context.version, alternate.version)
        with self.assertRaises(EvidenceError):
            validate_evidence_bank(bank, self.root, context=alternate)
        self.assertTrue(_cv_export_stem(company="Example", title="Engineer", owner_stem=alternate.cv_owner_stem).startswith("CV_OtherCandidate_"))

    def test_voice_configuration_is_lazy_and_accepts_another_exact_source_list(self):
        context = write_preparation_config(self.root, voice_sources=["I:/inaccessible/other-voice.md"])
        self.assertTrue(context.version)
        voice = self.root / "config/alternative-voice.md"
        voice.write_text("Use supported specific statements.", encoding="utf-8")
        context = write_preparation_config(self.root, voice_sources=["config/alternative-voice.md"])
        review = dict(voice=dict(language="English", notes="Reviewed final wording.", rules=[dict(path="config/alternative-voice.md", sha256=hashlib.sha256(voice.read_bytes()).hexdigest())]))
        validate_voice_review(review, self.root, context=context)
        review["voice"]["rules"][0]["path"] = "config/another-voice.md"
        with self.assertRaisesRegex(ValueError, "stale"):
            validate_voice_review(review, self.root, context=context)

    def clarification(self):
        source = self.candidate / "clarification.md"
        source.write_text("Example dates: February 2022 - July 2026. The exact end month remains uncertain.", encoding="utf-8")
        record = dict(path="registry/candidate/clarification.md", quote=source.read_text(encoding="utf-8"), sha256=hashlib.sha256(source.read_bytes()).hexdigest())
        correction = dict(employer="Example", reviewed=dict(reviewer="fixture", reason="Preserve supported uncertainty."), sources=[record], corrections=dict(start=dict(value="February 2022", precision="month", source=0), end=dict(value="July 2026", precision="year", source=0, uncertainty_source=0)))
        return source, correction

    def test_source_bound_clarifications_preserve_precision_and_reject_unsourced_dates(self):
        source, correction = self.clarification()
        context = write_preparation_config(self.root, career_clarifications=[correction])
        self.assertEqual(((2022, 2), (2026, None)), _corrected_roles(self.source, context=context)["Example"])
        for field, value in (("value", "August 2026"), ("precision", "month")):
            bad = copy.deepcopy(correction)
            if field == "precision":
                bad["corrections"]["end"]["value"] = "2026"
            bad["corrections"]["end"][field] = value
            context = write_preparation_config(self.root, career_clarifications=[bad])
            with self.assertRaises(CareerCoverageError):
                _corrected_roles(self.source, context=context)
        context = write_preparation_config(self.root, career_clarifications=[correction])
        source.write_text("Changed after review.", encoding="utf-8")
        with self.assertRaisesRegex(CareerCoverageError, "source"):
            _corrected_roles(self.source, context=context)

    def test_year_only_career_dates_reject_invented_months_and_changed_years(self):
        _, correction = self.clarification()
        context = write_preparation_config(self.root, career_clarifications=[correction])
        validate_career_coverage("## Experience\n### Example | February 2022 - 2026\n", self.source, context=context)
        for end in ("July 2026", "December 2026", "2027"):
            with self.subTest(end=end), self.assertRaisesRegex(CareerCoverageError, "unsupported dates"):
                validate_career_coverage(f"## Experience\n### Example | February 2022 - {end}\n", self.source, context=context)
        correction["corrections"]["start"].update(precision="year", uncertainty_source=0)
        context = write_preparation_config(self.root, career_clarifications=[correction])
        validate_career_coverage("## Experience\n### Example | 2022 - 2026\n", self.source, context=context)
        with self.assertRaisesRegex(CareerCoverageError, "unsupported dates"):
            validate_career_coverage("## Experience\n### Example | February 2022 - 2026\n", self.source, context=context)

    def test_unknown_employer_and_unbound_precision_reduction_are_rejected(self):
        _, correction = self.clarification()
        for change in (lambda row: row.update(employer="Unrecorded"), lambda row: row["corrections"]["end"].pop("uncertainty_source")):
            bad = copy.deepcopy(correction)
            change(bad)
            context = write_preparation_config(self.root, career_clarifications=[bad])
            with self.assertRaises(CareerCoverageError):
                _corrected_roles(self.source, context=context)

    def test_new_quality_must_bind_the_exact_context_before_other_grounding(self):
        for version in (None, "preparation-v1:sha256:another-context"):
            quality = dict(schema_version=3, preparation_context_version=version)
            with self.assertRaisesRegex(ApplicationError, "preparation_context_version"):
                _validate_v2_grounding(quality, {}, self.root, self.root, context=self.context)


if __name__ == "__main__":
    unittest.main()
