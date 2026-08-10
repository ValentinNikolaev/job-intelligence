from __future__ import annotations

import re
import unittest
from pathlib import Path


class WorkflowContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.project_root = Path(__file__).resolve().parents[1]

    def _read(self, relative_path: str) -> str:
        return (self.project_root / relative_path).read_text(encoding="utf-8")

    @staticmethod
    def _flat(text: str) -> str:
        return re.sub(r"\s+", " ", text).strip()

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

    def test_codex_commits_use_human_written_diff_specific_subjects(self) -> None:
        contract = self._read("prompts/job-intelligence-workflow.md")
        scheduled = self._read("prompts/scheduled-analyze.md")
        workflow_skill = self._read(
            ".agents/skills/job-intelligence-workflow/SKILL.md"
        )

        for text in (contract, scheduled, workflow_skill):
            self.assertIn("human-written", text)
            self.assertIn("staged diff", text)
            self.assertIn("GitHub Actions templates", text)
            self.assertIn("generic `update data`", text)

    def test_two_wave_preparation_has_parallel_parts_handoff_and_cv_barrier(self) -> None:
        prepare = self._flat(
            self._read(
                ".agents/skills/job-intelligence-workflow/references/prepare.md"
            )
        )
        application_prompt = self._flat(self._read("prompts/vacancy-application.md"))
        combined = f"{prepare} {application_prompt}"

        self.assertRegex(combined, r"(?i)wave 1.{0,300}parallel")
        self.assertRegex(
            combined,
            r"\.codex-work/application/<[^>]+>/parts/",
        )
        for filename in ("research.md", "evidence-map.md", "requirements-risks.md"):
            self.assertIn(filename, combined)
        self.assertRegex(
            combined,
            r"(?i)(?:coordinating|main) agent.{0,300}"
            r"(?:write|synthesi[sz]e|finali[sz]e).{0,120}(?:final.{0,40})?`cv\.md`",
        )
        self.assertRegex(
            combined,
            r"(?i)(?:wave 2.{0,160}(?:only after|cannot start before).{0,100}"
            r"(?:final )?cv|`cv\.md`.{0,180}(?:barrier|wave 2))",
        )

    def test_two_wave_preparation_assigns_wave_two_outputs_exclusively(self) -> None:
        prepare = self._flat(
            self._read(
                ".agents/skills/job-intelligence-workflow/references/prepare.md"
            )
        )
        contract = self._flat(self._read("prompts/job-intelligence-workflow.md"))
        combined = f"{prepare} {contract}"

        self.assertRegex(combined, r"(?i)wave 2.{0,300}parallel")
        for filename in ("cover-letter.md", "interview-preparation.md", "analysis.md"):
            self.assertIn(filename, combined)
        self.assertIn("$write-cover-letter", combined)
        self.assertRegex(combined, r"(?i)exclusive.{0,100}(?:owner|ownership)")

    def test_two_wave_preparation_routes_minimal_inputs(self) -> None:
        prepare = self._flat(
            self._read(
                ".agents/skills/job-intelligence-workflow/references/prepare.md"
            )
        )
        application_prompt = self._flat(self._read("prompts/vacancy-application.md"))
        combined = f"{prepare} {application_prompt}"

        self.assertRegex(
            combined,
            r"(?i)research.{0,240}(?:does not|must not|without).{0,100}"
            r"(?:full candidate|candidate (?:cv|profile|evidence))",
        )
        self.assertRegex(
            combined,
            r"(?i)(?:cv|evidence).{0,180}(?:does not|must not|without|"
            r"performs? no|no).{0,80}(?:web|brows)",
        )
        self.assertRegex(
            combined,
            r"(?i)evidence-map\.md.{0,220}(?:complete|full).{0,80}"
            r"(?:proposed |draft )?cv",
        )
        self.assertRegex(
            combined,
            r"(?i)wave 2.{0,800}(?:only|minimal).{0,120}(?:needed|required|specific)",
        )
        self.assertRegex(
            combined,
            r"(?i)(?:do not|must not|never).{0,100}(?:unneeded.{0,80}"
            r"(?:inputs|candidate sources)|other handoffs)",
        )

    def test_two_wave_preparation_finalizes_once_with_safe_fallback(self) -> None:
        paths = (
            ".agents/skills/job-intelligence-workflow/references/prepare.md",
            ".agents/skills/manual-vacancy-application/SKILL.md",
            "prompts/job-intelligence-workflow.md",
            "prompts/vacancy-application.md",
        )
        combined = self._flat("\n".join(self._read(path) for path in paths))

        self.assertRegex(combined, r"(?i)(?:one|single).{0,80}cross-file")
        self.assertRegex(
            combined,
            r"(?i)(?:validate-application.{0,120}\bonce\b|\bonce\b.{0,120}validate-application)",
        )
        self.assertRegex(
            combined,
            r"(?i)(?:python run\.py prepare.{0,160}\bonce\b|\bonce\b.{0,160}python run\.py prepare)",
        )
        self.assertRegex(combined, r"(?i)(?:subagents|slots).{0,120}unavailable")
        self.assertRegex(combined, r"(?i)sequential")
        self.assertRegex(
            combined,
            r"(?i)(?:vacancy isolation|isolat(?:e|ed|ion).{0,180}vacanc|"
            r"vacanc.{0,180}(?:do not|never).{0,80}(?:reuse|share))",
        )


if __name__ == "__main__":
    unittest.main()
