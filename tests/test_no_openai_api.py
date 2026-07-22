from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCAN_ROOTS = (ROOT / "jobintel", ROOT / "sources", ROOT / "config")
BANNED = (
    "api." + "openai.com",
    "OPENAI_" + "API_KEY",
    "/v1/" + "responses",
    "/v1/" + "chat/completions",
    "from " + "openai import",
    "import " + "openai",
)


class NoOpenAIApiTests(unittest.TestCase):
    def test_project_runtime_contains_no_openai_platform_client(self) -> None:
        violations: list[str] = []
        paths = [ROOT / "pyproject.toml"]
        for scan_root in SCAN_ROOTS:
            paths.extend(path for path in scan_root.rglob("*") if path.is_file())

        for path in paths:
            if path.suffix.lower() not in {".py", ".toml", ".yaml", ".yml", ".json"}:
                continue
            content = path.read_text(encoding="utf-8", errors="ignore").casefold()
            for marker in BANNED:
                if marker.casefold() in content:
                    violations.append(f"{path.relative_to(ROOT)}: {marker}")

        self.assertEqual([], violations, "Prohibited OpenAI Platform integration found")


if __name__ == "__main__":
    unittest.main()
