"""Run the bounded phase-3 evaluator without invoking models."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobintel.match_policy_eval import project_main


if __name__ == "__main__":
    raise SystemExit(project_main(root=ROOT))
