from __future__ import annotations

import unittest

from jobintel.matching import MatchError, validate_match, render_match_markdown
from jobintel.requirements import validate_requirements
from tests.test_matching import match_payload


def row(**changes):
    value = dict(requirement="Python", importance="high", basis="structural",
                 jd_quote="Build Python services.", match="strong",
                 candidate_quote="using Python", risk="", mitigation="", hard_blocker=False)
    value.update(changes)
    return value


class RequirementTests(unittest.TestCase):
    def test_verified_quotes_survive_match_and_markdown(self):
        payload = {**match_payload(), "requirements": [row()]}
        result = validate_match(payload, vacancy_text="Build Python services.", candidate_text="Engineer using Python")
        self.assertEqual("high", result["requirements"][0]["importance"])
        self.assertIn("Build Python services.", render_match_markdown(result))

    def test_fabricated_source_quote_is_rejected(self):
        with self.assertRaisesRegex(MatchError, "selected vacancy"):
            validate_match({**match_payload(), "requirements": [row()]}, vacancy_text="Java developer")
        with self.assertRaisesRegex(MatchError, "candidate evidence"):
            validate_match({**match_payload(), "requirements": [row()]}, candidate_text="Java developer")

    def test_market_guess_cannot_create_obligation(self):
        for overrides in [dict(importance="high"), dict(importance="meaningful", hard_blocker=True)]:
            with self.subTest(overrides=overrides), self.assertRaisesRegex(ValueError, "inferred"):
                validate_requirements([row(basis="inferred", jd_quote="", **overrides)])

    def test_unknown_does_not_become_hard_blocker(self):
        with self.assertRaisesRegex(ValueError, "established missing"):
            validate_requirements([row(basis="stated", match="unknown", candidate_quote="", risk="Unclear", mitigation="Ask candidate", hard_blocker=True)])

    def test_high_priority_gap_requires_action(self):
        with self.assertRaisesRegex(ValueError, "risk and mitigation"):
            validate_requirements([row(match="partial")])

    def test_blocker_and_recommendation_must_agree(self):
        with self.assertRaisesRegex(MatchError, "requires hard_rejection"):
            validate_match({**match_payload(), "requirements": [row(basis="stated", match="missing", risk="Required", mitigation="Do not apply", hard_blocker=True)]})

    def test_legacy_match_remains_readable(self):
        self.assertNotIn("requirements", validate_match(match_payload()))

    def test_duplicate_rows_are_not_weighted_twice(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_requirements([row(), row(requirement="PYTHON")])


if __name__ == "__main__":
    unittest.main()
