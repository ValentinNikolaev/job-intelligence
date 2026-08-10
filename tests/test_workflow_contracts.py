from __future__ import annotations

import unittest
from pathlib import Path


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parents[1]

    def _read(self, relative_path: str) -> str:
        return (self.project_root / relative_path).read_text(encoding="utf-8")

    def test_manual_skill_uses_direct_single_vacancy_analysis(self) -> None:
        source = self._read("skills/manual-vacancy-application/SKILL.md")
        distributed = self._read(
            ".agents/skills/manual-vacancy-application/SKILL.md"
        )

        self.assertEqual(source, distributed)
        self.assertNotIn("manual-job-intake", source)
        self.assertIn("python run.py add-manual --input <draft.yaml>", source)
        self.assertIn("python run.py analyze <vacancy-directory>", source)
        self.assertIn("Do not run triage", source)
        self.assertIn("`pending analyze all`", source)
        self.assertIn("`analyze-batch`", source)

    def test_shared_manual_contract_does_not_use_the_scheduled_queue(self) -> None:
        contract = self._read("prompts/job-intelligence-workflow.md")
        manual_section = contract.split("### `manual-application`", 1)[1].split(
            "### `scheduled-analysis`", 1
        )[0]

        self.assertIn("python run.py analyze <directory>", manual_section)
        self.assertIn("Do not run triage", manual_section)
        self.assertIn("`pending analyze all`", manual_section)
        self.assertIn("`analyze-batch`", manual_section)
        self.assertIn("python run.py validate-application <directory>", manual_section)

    def test_git_preflight_happens_once_before_model_work(self) -> None:
        contract = self._read("prompts/job-intelligence-workflow.md")
        workflow_skill = self._read(
            ".agents/skills/job-intelligence-workflow/SKILL.md"
        )

        self.assertIn("## One-time Git preflight", contract)
        self.assertIn("git status --short", contract)
        self.assertIn("git fetch origin", contract)
        self.assertIn("git rev-list --left-right --count", contract)
        self.assertIn("Do not repeat the fetch", contract)
        self.assertIn("one-time Git preflight", workflow_skill)

    def test_application_contract_has_bounded_research_and_output(self) -> None:
        prompt = self._read("prompts/vacancy-application.md")
        prepare = self._read(
            ".agents/skills/job-intelligence-workflow/references/prepare.md"
        )

        self.assertIn("Target 500–700 words for `cv_markdown`", prompt)
        self.assertIn("300–450 for `cover_letter_markdown`", prompt)
        self.assertIn("700–900 for `analysis_markdown`", prompt)
        self.assertIn("800–1000 for", prompt)
        self.assertIn("Hard ceilings are 800 words for the CV", prompt)
        self.assertIn("at most two primary", prompt)
        self.assertIn("one research pass", prompt)
        self.assertIn("at most two primary", prepare)
        self.assertIn("python run.py validate-application <vacancy-directory>", prepare)

    def test_final_repository_checks_run_once(self) -> None:
        contract = self._read("prompts/job-intelligence-workflow.md")
        workflow_skill = self._read(
            ".agents/skills/job-intelligence-workflow/SKILL.md"
        )
        manual_skill = self._read(
            ".agents/skills/manual-vacancy-application/SKILL.md"
        )

        for text in (contract, workflow_skill, manual_skill):
            self.assertIn("exactly once", text)
        self.assertRegex(contract, r"Repeat only a\s+specific failed check")


if __name__ == "__main__":
    unittest.main()
