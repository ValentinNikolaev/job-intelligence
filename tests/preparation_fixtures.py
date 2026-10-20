"""Explicit synthetic preparation contexts for isolated tests."""
from pathlib import Path

import yaml

from jobintel.preparation_context import load_preparation_context


def write_preparation_config(root, *, candidate_directory="registry/candidate",
        evidence_bank="registry/evidence/achievements.yaml", cv_owner_stem="ValentinNikolaev",
        career_sources=None, profile_sources=None, employer_aliases=None, career_scope=None,
        career_clarifications=None, voice_sources=None):
    root = Path(root)
    config = root / "config"
    config.mkdir(parents=True, exist_ok=True)
    path = config / "application-profile.yaml"
    profile = yaml.safe_load(path.read_text(encoding="utf-8")) if path.is_file() else {}
    profile["schema_version"] = 1
    profiles = profile_sources or [candidate_directory + "/candidate.md"]
    if isinstance(profiles, list):
        profiles = dict(preferred=profiles, fallback=profiles, supplements=[])
    profile["preparation"] = dict(cv_owner_stem=cv_owner_stem, candidate_directory=candidate_directory,
        evidence_bank=evidence_bank, profile_sources=profiles,
        career_sources=career_sources or [dict(path=candidate_directory + "/linkedin-profile.md", section="Experience")],
        employer_aliases=employer_aliases or {}, career_scope=career_scope or dict(first_employer=None, maximum_years_since_end=100),
        career_clarifications=career_clarifications or [])
    path.write_text(yaml.safe_dump(profile, allow_unicode=True, sort_keys=False), encoding="utf-8")
    review = config / "application-review.yaml"
    if voice_sources is not None or not review.is_file():
        review.write_text(yaml.safe_dump(dict(schema_version=1, voice_sources=voice_sources or ["config/test-voice.md"])), encoding="utf-8")
    editorial = config / "cv-editorial-knowledge.yaml"
    if not editorial.is_file():
        generic_policy = Path(__file__).resolve().parents[1] / "config/cv-editorial-knowledge.yaml"
        editorial.write_text(generic_policy.read_text(encoding="utf-8-sig"), encoding="utf-8")
    return load_preparation_context(root)
