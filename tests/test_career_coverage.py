import tempfile
import unittest
from pathlib import Path
from datetime import date

from jobintel.application_lint import _cv_lint
from jobintel.career_coverage import CareerCoverageError, validate_career_coverage


SOURCE = """# Candidate
## Experience
### Simple App
Software Developer
November 2023 - Present
### airSlate
#### Technical Lead
January 2023 - August 2023
#### Senior Developer
February 2021 - January 2023
### Hyprr
Technical Lead
November 2019 - January 2021
### Upwork freelance
Software Developer
July 2008 - September 2016
## Education
"""
CV = """## Summary
Worked at airSlate and Hyprr.
## Skills
airSlate, Hyprr
## Experience
### Simple.life — Software Developer | November 2023 - 2026
- Delivered work.
### airSlate — Software Developer | February 2021 - August 2023
- Delivered work.
### Hyprr — Technical Lead | November 2019 - January 2021
- Delivered work.
## Earlier Experience
- **Upwork freelance**, Software Developer | July 2008 - September 2016
"""


class CareerCoverageTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.source = Path(self.temp.name) / "linkedin-profile.md"
        self.source.write_text(SOURCE, encoding="utf-8")
        self.source.with_name("user-confirmed-career-clarifications.md").write_text(
            "## Simple.life\n- **Dates:** November 2023 - July 2026\n", encoding="utf-8"
        )
        self.source.with_name("user-confirmed-simple-life-follow-up-2026-09-26.md").write_text(
            "This does not establish the exact employment end date.", encoding="utf-8"
        )

    def test_accepts_detailed_and_dated_earlier_employers(self) -> None:
        validate_career_coverage(CV, self.source)

    def test_rejects_missing_airslate_and_hyprr_despite_summary_and_skills_mentions(self) -> None:
        for employer in ("airSlate", "Hyprr"):
            with self.subTest(employer=employer):
                markdown = CV.replace(
                    next(line for line in CV.splitlines() if line.startswith(f"### {employer}")),
                    "### Another Company | February 2021 - August 2023",
                )
                with self.assertRaisesRegex(CareerCoverageError, employer):
                    validate_career_coverage(markdown, self.source)

    def test_rejects_missing_dated_historical_entry(self) -> None:
        with self.assertRaisesRegex(CareerCoverageError, "Upwork freelance"):
            validate_career_coverage(CV.replace("- **Upwork freelance**, Software Developer | July 2008 - September 2016", ""), self.source)

    def test_new_source_employer_is_required(self) -> None:
        self.source.write_text(SOURCE.replace("## Education", "### New Employer\nEngineer\nJanuary 2017 - October 2017\n## Education"), encoding="utf-8")
        with self.assertRaisesRegex(CareerCoverageError, "New Employer"):
            validate_career_coverage(CV, self.source)

    def test_new_primary_cv_employer_is_required(self) -> None:
        primary = self.source.with_name("backend-engineer-cv.md")
        primary.write_text("# Candidate\n## Work Experience\n### Other Firm\nEngineer\nMarch 2017 - May 2018\n## Education\n", encoding="utf-8")
        with self.assertRaisesRegex(CareerCoverageError, "Other Firm"):
            validate_career_coverage(CV, self.source)

    def test_new_ongoing_employer_requires_ongoing_cv_entry(self) -> None:
        self.source.write_text(
            SOURCE.replace("## Education", "### New Employer\nEngineer\nMarch 2026 - Present\n## Education"),
            encoding="utf-8",
        )
        with self.assertRaisesRegex(CareerCoverageError, "New Employer"):
            validate_career_coverage(CV, self.source)
        active_cv = CV.replace("## Earlier Experience", "### New Employer | March 2026 - Present\n## Earlier Experience")
        validate_career_coverage(active_cv, self.source)
        closed_cv = active_cv.replace("New Employer | March 2026 - Present", "New Employer | March 2026 - October 2026")
        with self.assertRaisesRegex(CareerCoverageError, "unsupported dates for New Employer"):
            validate_career_coverage(closed_cv, self.source)

    def test_missing_and_corrupt_source_fail_closed(self) -> None:
        self.source.unlink()
        with self.assertRaisesRegex(CareerCoverageError, "unavailable"):
            validate_career_coverage(CV, self.source)
        self.source.write_text("# Corrupt source", encoding="utf-8")
        with self.assertRaisesRegex(CareerCoverageError, "no Experience"):
            validate_career_coverage(CV, self.source)

    def test_project_inventory_requires_all_nine_documented_companies(self) -> None:
        project_source = Path(__file__).resolve().parents[1] / "registry/candidate/linkedin-profile.md"
        cv = """## Experience
### Simple.life | November 2023 - 2026
### CRURATED | August 2024 - January 2026
### airSlate | February 2021 - August 2023
### Hyprr | November 2019 - January 2021
### PDFfiller | October 2016 - November 2019
## Earlier Experience
Sixt | December 2018 - November 2019
Aurum Software | November 2015 - November 2016
CoinsBank/bit-x | January 2014 - November 2015
Upwork freelance | July 2008 - September 2016
"""
        validate_career_coverage(cv, project_source)
        for employer in ("airSlate", "Hyprr", "Sixt", "Aurum Software", "CoinsBank/bit-x", "Upwork freelance"):
            with self.subTest(employer=employer):
                omission = "\n".join(line for line in cv.splitlines() if employer not in line)
                with self.assertRaisesRegex(CareerCoverageError, employer):
                    validate_career_coverage(omission, project_source)

    def test_lint_uses_month_precision_for_five_year_bullet_cutoff(self) -> None:
        for end_month, expected_depth_warning in (("January", False), ("October", True)):
            with self.subTest(end_month=end_month):
                cv = (
                    "## Experience\n"
                    f"### Hyprr | November 2019 - {end_month} 2021\n"
                    "- Delivered the first outcome.\n- Delivered the second outcome.\n"
                )
                diagnostics = []
                _cv_lint(cv, {}, Path("cv.md"), diagnostics, reference_date=date(2026, 10, 5))
                self.assertEqual(expected_depth_warning, any(item["code"] == "CV_ROLE_DEPTH" for item in diagnostics))


if __name__ == "__main__":
    unittest.main()
