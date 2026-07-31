from __future__ import annotations

import argparse
import datetime as dt
import shutil
import tempfile
import zipfile
from pathlib import Path

import yaml


THRESHOLD = 100


def read_yaml(path: Path) -> dict:
    loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def eligible(directory: Path, category: str, low_score: int) -> bool:
    meta_path = directory / "meta.yaml"
    if not meta_path.is_file():
        return False
    meta = read_yaml(meta_path)
    if category == "low-score":
        match_path = directory / "match.yaml"
        if not match_path.is_file():
            return False
        score = read_yaml(match_path).get("score")
        return isinstance(score, int) and score < low_score
    triage_path = directory / "triage.yaml"
    return triage_path.is_file() and read_yaml(triage_path).get("skip_model") is True


def archive(project_root: Path, category: str, low_score: int) -> int:
    jobs_root = project_root / "registry" / "jobs"
    archive_root = project_root / "archives" / category
    archive_root.mkdir(parents=True, exist_ok=True)
    today = dt.date.today().isoformat()
    destination = archive_root / f"{today}.zip"
    candidates = sorted(
        path for path in jobs_root.iterdir() if path.is_dir() and eligible(path, category, low_score)
    )
    print(f"{category}: eligible={len(candidates)} threshold={THRESHOLD}")
    if len(candidates) <= THRESHOLD:
        print("No archive created; threshold not exceeded.")
        return 0
    if destination.exists():
        raise RuntimeError(f"archive already exists for {today}: {destination}")

    with tempfile.NamedTemporaryFile(prefix=f"{category}-{today}-", suffix=".zip", dir=archive_root, delete=False) as handle:
        temporary = Path(handle.name)
    try:
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED) as archive_file:
            for directory in candidates:
                for path in sorted(directory.rglob("*")):
                    if path.is_file():
                        archive_file.write(path, path.relative_to(jobs_root).as_posix())
        with zipfile.ZipFile(temporary) as archive_file:
            names = set(archive_file.namelist())
        expected = {
            path.relative_to(jobs_root).as_posix()
            for directory in candidates
            for path in directory.rglob("*")
            if path.is_file()
        }
        if names != expected:
            raise RuntimeError("archive validation failed: ZIP contents differ from source files")
        temporary.replace(destination)
        for directory in candidates:
            shutil.rmtree(directory)
    except Exception:
        temporary.unlink(missing_ok=True)
        destination.unlink(missing_ok=True)
        raise
    print(f"Created {destination} and removed {len(candidates)} vacancy directories.")
    return len(candidates)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("category", choices=("low-score", "skipped"))
    parser.add_argument("--project-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--low-score", type=int, default=65)
    args = parser.parse_args()
    return 0 if archive(args.project_root.resolve(), args.category, args.low_score) >= 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
