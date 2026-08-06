from __future__ import annotations

import os
import shutil
import uuid
from collections import defaultdict
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import yaml

from .models import VACANCY_STATUSES, NormalizedJob, UpsertResult
from .normalization import slug, vacancy_fingerprint


SCHEMA_VERSION = 2
SOURCE_RANKS = {
    "adzuna": 10,
    "arbeitnow": 10,
    "himalayas": 10,
    "jobicy": 10,
    "jooble": 10,
    "direct": 20,
    "manual": 25,
    "ashby": 30,
    "custom": 35,
    "dou": 10,
}

_CANONICAL_FIELDS = (
    "title",
    "company",
    "company_url",
    "location",
    "remote",
    "employment_type",
    "published_at",
)


class RegistryError(RuntimeError):
    pass


class Registry:
    def __init__(
        self,
        root: Path,
        *,
        clock: Callable[[], datetime] | None = None,
        id_factory: Callable[[], str] | None = None,
        cache_entries: bool = False,
    ) -> None:
        self.root = root
        self.jobs_dir = root / "jobs"
        self.index_path = root / "index.md"
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._id_factory = id_factory or (lambda: str(uuid.uuid4()))
        self._cache_entries = cache_entries
        self._entries_cache: list[dict[str, Any]] | None = None
        self._source_index: dict[tuple[str, str], list[dict[str, Any]]] | None = None
        self._fingerprint_index: dict[str, list[dict[str, Any]]] | None = None
        self.jobs_dir.mkdir(parents=True, exist_ok=True)

    def upsert(self, job: NormalizedJob) -> UpsertResult:
        job.validate()
        source = job.source.strip().lower()
        fingerprint = vacancy_fingerprint(job.company, job.title, job.location)
        entries = self._scan()
        exact = (
            self._find_source_indexed(source, job.source_job_id)
            if self._cache_entries
            else self._find_source(entries, source, job.source_job_id)
        )

        if exact is not None:
            return self._update_existing(exact, job, fingerprint, is_merge=False)

        candidate = (
            self._find_fingerprint_candidate_indexed(fingerprint, source)
            if self._cache_entries
            else self._find_fingerprint_candidate(entries, fingerprint, source)
        )
        if candidate is not None:
            return self._update_existing(candidate, job, fingerprint, is_merge=True)

        return self._create(job, fingerprint)

    def regenerate_index(self) -> bool:
        rows: list[tuple[dict[str, Any], Path, dict[str, Any] | None]] = []
        for entry in self._scan():
            rows.append((entry["meta"], entry["path"], _read_match_summary(entry["path"] / "match.yaml")))
        rows.sort(
            key=lambda item: (
                item[2]["score"] if item[2] is not None else -1,
                str(item[0]["discovered_at"]),
                str(item[0]["id"]),
            ),
            reverse=True,
        )

        lines = [
            "# Job Registry",
            "",
            "| Score | Discovered | Company | Title | Location | Recommendation | Sources | Job |",
            "|---:|---|---|---|---|---|---|---|",
        ]
        for meta, directory, match in rows:
            discovered = str(meta.get("discovered_at", ""))[:10]
            sources = []
            for ref in meta.get("sources", []):
                label = _escape_cell(str(ref.get("source", "")).title())
                url = str(ref.get("url", "")).strip()
                sources.append(f"[{label}]({_markdown_url(url)})" if url else label)
            relative_job = f"jobs/{directory.name}/job.md"
            lines.append(
                "| "
                + " | ".join(
                    (
                        str(match["score"]) if match is not None else "—",
                        _escape_cell(discovered),
                        _escape_cell(meta.get("company")),
                        _escape_cell(meta.get("title")),
                        _escape_cell(meta.get("location")),
                        _recommendation_label(match["recommendation"]) if match is not None else "Not analyzed",
                        ", ".join(sources),
                        f"[Open]({relative_job})",
                    )
                )
                + " |"
            )
        content = "\n".join(lines) + "\n"
        return _write_atomic_if_changed(self.index_path, content)

    def migrate_metadata(self) -> None:
        """Apply supported one-time metadata migrations without changing vacancy status."""
        self._scan()

    def update_status(
        self,
        selector: str,
        status: str,
        *,
        on_updated: Callable[[dict[str, Any], dict[str, Any], Path], None] | None = None,
    ) -> bool:
        status = status.strip().casefold()
        if status not in VACANCY_STATUSES:
            raise RegistryError(
                f"invalid vacancy status {status!r}; expected one of: "
                + ", ".join(VACANCY_STATUSES)
            )
        matches = [
            entry
            for entry in self._scan()
            if entry["path"].name == selector or str(entry["meta"].get("id")) == selector
        ]
        if not matches:
            raise RegistryError(f"vacancy not found: {selector}")
        if len(matches) > 1:
            raise RegistryError(f"vacancy selector is ambiguous: {selector}")

        entry = matches[0]
        original = entry["meta"]
        meta = dict(original)
        current = str(meta.get("status", ""))
        if current == status:
            return False
        history = meta.get("status_history")
        if not isinstance(history, list) or not history:
            raise RegistryError(f"vacancy has invalid status_history: {entry['path']}")
        meta["status_history"] = [dict(item) for item in history]
        now = _utc_iso(self._clock())
        meta["status"] = status
        meta["status_history"].append({"status": status, "changed_at": now})
        meta["updated_at"] = now
        meta_path = entry["path"] / "meta.yaml"
        changed = _write_atomic_if_changed(meta_path, _dump_yaml(meta))
        if not changed:
            return False
        try:
            if on_updated is not None:
                on_updated(dict(original), dict(meta), entry["path"])
        except Exception as exc:
            try:
                _write_atomic_if_changed(meta_path, _dump_yaml(original))
            except Exception as rollback_exc:
                raise RegistryError(
                    f"status audit failed and metadata rollback failed for {entry['path']}: "
                    f"{rollback_exc}"
                ) from exc
            raise
        entry["meta"] = meta
        return True

    def _scan(self) -> list[dict[str, Any]]:
        if self._cache_entries and self._entries_cache is not None:
            return self._entries_cache
        entries: list[dict[str, Any]] = []
        if not self.jobs_dir.exists():
            return entries
        for meta_path in sorted(self.jobs_dir.glob("*/meta.yaml")):
            try:
                loaded = yaml.safe_load(meta_path.read_text(encoding="utf-8"))
            except (OSError, yaml.YAMLError) as exc:
                raise RegistryError(f"cannot read registry metadata {meta_path}: {exc}") from exc
            if not isinstance(loaded, dict):
                raise RegistryError(f"registry metadata is not a mapping: {meta_path}")
            loaded = _migrate_metadata(meta_path, loaded)
            missing = [
                key
                for key in (
                    "id",
                    "title",
                    "company",
                    "sources",
                    "fingerprint",
                    "discovered_at",
                    "status",
                    "status_history",
                )
                if key not in loaded
            ]
            if missing:
                raise RegistryError(f"registry metadata missing {', '.join(missing)}: {meta_path}")
            if not isinstance(loaded["sources"], list):
                raise RegistryError(f"registry sources must be a list: {meta_path}")
            entries.append({"meta": loaded, "path": meta_path.parent})
        if self._cache_entries:
            self._entries_cache = entries
            self._rebuild_lookup_indexes()
        return entries

    def _rebuild_lookup_indexes(self) -> None:
        self._source_index = defaultdict(list)
        self._fingerprint_index = defaultdict(list)
        for entry in self._entries_cache or []:
            self._index_entry(entry)

    def _index_entry(self, entry: dict[str, Any]) -> None:
        assert self._source_index is not None
        assert self._fingerprint_index is not None
        for ref in entry["meta"]["sources"]:
            key = (str(ref.get("source")), str(ref.get("source_job_id")))
            self._source_index[key].append(entry)
        fingerprint = str(entry["meta"].get("fingerprint") or "")
        self._fingerprint_index[fingerprint].append(entry)

    def _find_source_indexed(self, source: str, source_job_id: str) -> dict[str, Any] | None:
        assert self._source_index is not None
        matches = self._source_index.get((source, source_job_id), [])
        if len(matches) > 1:
            raise RegistryError(f"source identity appears in multiple vacancies: {source}:{source_job_id}")
        return matches[0] if matches else None

    def _find_fingerprint_candidate_indexed(
        self, fingerprint: str, incoming_source: str
    ) -> dict[str, Any] | None:
        assert self._fingerprint_index is not None
        candidates = [
            entry
            for entry in self._fingerprint_index.get(fingerprint, [])
            if incoming_source
            not in {str(ref.get("source")) for ref in entry["meta"]["sources"]}
        ]
        return candidates[0] if len(candidates) == 1 else None

    def _cache_add_entry(self, entry: dict[str, Any]) -> None:
        if not self._cache_entries or self._entries_cache is None:
            return
        self._entries_cache.append(entry)
        self._index_entry(entry)

    def _cache_replace_entry(self, entry: dict[str, Any], meta: dict[str, Any]) -> None:
        if not self._cache_entries:
            entry["meta"] = meta
            return
        assert self._source_index is not None
        assert self._fingerprint_index is not None
        for rows in (*self._source_index.values(), *self._fingerprint_index.values()):
            rows[:] = [candidate for candidate in rows if candidate is not entry]
        entry["meta"] = meta
        self._index_entry(entry)

    @staticmethod
    def _find_source(entries: list[dict[str, Any]], source: str, source_job_id: str) -> dict[str, Any] | None:
        matches = []
        for entry in entries:
            for ref in entry["meta"]["sources"]:
                if str(ref.get("source")) == source and str(ref.get("source_job_id")) == source_job_id:
                    matches.append(entry)
        if len(matches) > 1:
            raise RegistryError(f"source identity appears in multiple vacancies: {source}:{source_job_id}")
        return matches[0] if matches else None

    @staticmethod
    def _find_fingerprint_candidate(
        entries: list[dict[str, Any]], fingerprint: str, incoming_source: str
    ) -> dict[str, Any] | None:
        candidates = []
        for entry in entries:
            if entry["meta"].get("fingerprint") != fingerprint:
                continue
            existing_sources = {str(ref.get("source")) for ref in entry["meta"]["sources"]}
            if incoming_source not in existing_sources:
                candidates.append(entry)
        # Ambiguity is kept separate. A false separation is safer than a false merge.
        return candidates[0] if len(candidates) == 1 else None

    def _create(self, job: NormalizedJob, fingerprint: str) -> UpsertResult:
        now = _utc_iso(self._clock())
        vacancy_id = self._id_factory()
        meta = {
            "schema_version": SCHEMA_VERSION,
            "id": vacancy_id,
            "title": job.title.strip(),
            "company": job.company.strip(),
            "company_url": _clean_optional(job.company_url),
            "location": _clean_optional(job.location),
            "remote": job.remote,
            "employment_type": _clean_optional(job.employment_type),
            "sources": [_source_ref(job)],
            "published_at": _clean_optional(job.published_at),
            "discovered_at": now,
            "updated_at": now,
            "status": "found",
            "status_history": [{"status": "found", "changed_at": now}],
            "analysis_priority": job.analysis_priority,
            "fingerprint": fingerprint,
            "data_source": job.source.strip().lower(),
            "content_source": job.source.strip().lower() if job.description.strip() else None,
            "company_content_source": job.source.strip().lower() if _clean_optional(job.company_description) else None,
        }
        timestamp = _parse_datetime(now).strftime("%Y-%m-%d_%H%M%S")
        base_name = f"{timestamp}_{slug(job.company)}_{slug(job.title)}"
        final_dir = self.jobs_dir / base_name
        if final_dir.exists():
            final_dir = self.jobs_dir / f"{base_name}_{vacancy_id[:8]}"
        temp_dir = self.jobs_dir / f".tmp-{vacancy_id}"
        if temp_dir.exists():
            raise RegistryError(f"temporary registry path already exists: {temp_dir}")
        try:
            temp_dir.mkdir(parents=False)
            (temp_dir / "meta.yaml").write_text(_dump_yaml(meta), encoding="utf-8", newline="\n")
            (temp_dir / "job.md").write_text(
                _render_job_markdown(meta["title"], job.description, meta["published_at"]),
                encoding="utf-8",
                newline="\n",
            )
            if meta["company_content_source"]:
                (temp_dir / "company.md").write_text(
                    _render_markdown(meta["company"], job.company_description or ""),
                    encoding="utf-8",
                    newline="\n",
                )
            os.replace(temp_dir, final_dir)
        except Exception:
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            raise
        self._cache_add_entry({"meta": meta, "path": final_dir})
        return UpsertResult("created", vacancy_id, final_dir.name)

    def _update_existing(
        self,
        entry: dict[str, Any],
        job: NormalizedJob,
        fingerprint: str,
        *,
        is_merge: bool,
    ) -> UpsertResult:
        directory: Path = entry["path"]
        original: dict[str, Any] = entry["meta"]
        meta = dict(original)
        meta["sources"] = [dict(ref) for ref in original["sources"]]
        source = job.source.strip().lower()

        ref = _source_ref(job)
        existing_ref = next(
            (
                current
                for current in meta["sources"]
                if current.get("source") == source
                and str(current.get("source_job_id")) == job.source_job_id
            ),
            None,
        )
        if existing_ref is None:
            meta["sources"].append(ref)
        else:
            existing_ref.clear()
            existing_ref.update(ref)
        meta["sources"].sort(key=lambda item: (str(item.get("source")), str(item.get("source_job_id"))))

        current_data_source = str(meta.get("data_source") or _best_source(meta["sources"]))
        incoming_rank = _source_rank(source)
        current_rank = _source_rank(current_data_source)
        owns_data = source == current_data_source
        replace_data = incoming_rank > current_rank
        fill_only = incoming_rank < current_rank or (incoming_rank == current_rank and not owns_data)
        incoming_values = {
            "title": job.title.strip(),
            "company": job.company.strip(),
            "company_url": _clean_optional(job.company_url),
            "location": _clean_optional(job.location),
            "remote": job.remote,
            "employment_type": _clean_optional(job.employment_type),
            "published_at": _clean_optional(job.published_at),
        }
        for field in _CANONICAL_FIELDS:
            incoming = incoming_values[field]
            if incoming is None:
                continue
            if replace_data or owns_data or (fill_only and meta.get(field) is None):
                meta[field] = incoming
        if replace_data:
            meta["data_source"] = source
        if job.analysis_priority > _analysis_priority(meta.get("analysis_priority")):
            meta["analysis_priority"] = job.analysis_priority

        # An authoritative same-source record may legitimately change its identity fields.
        if not is_merge:
            meta["fingerprint"] = fingerprint

        job_path = directory / "job.md"
        current_job_body = _read_markdown_body(job_path)
        selected_job_body = current_job_body
        content_source = meta.get("content_source")
        if job.description.strip():
            if _prefer_content(source, job.description, content_source, current_job_body):
                selected_job_body = job.description.strip()
                meta["content_source"] = source

        company_path = directory / "company.md"
        current_company_body = _read_markdown_body(company_path)
        selected_company_body = current_company_body
        company_content_source = meta.get("company_content_source")
        if _clean_optional(job.company_description):
            if _prefer_content(
                source,
                job.company_description or "",
                company_content_source,
                current_company_body,
            ):
                selected_company_body = (job.company_description or "").strip()
                meta["company_content_source"] = source

        new_job_markdown = _render_job_markdown(
            str(meta["title"]),
            selected_job_body,
            _clean_optional(meta.get("published_at")),
        )
        old_job_markdown = job_path.read_text(encoding="utf-8") if job_path.exists() else ""
        new_company_markdown = (
            _render_markdown(str(meta["company"]), selected_company_body)
            if selected_company_body
            else None
        )
        old_company_markdown = company_path.read_text(encoding="utf-8") if company_path.exists() else None

        comparable_meta = dict(meta)
        comparable_meta["updated_at"] = original.get("updated_at")
        metadata_changed = comparable_meta != original
        content_changed = new_job_markdown != old_job_markdown or new_company_markdown != old_company_markdown
        if not metadata_changed and not content_changed:
            return UpsertResult("unchanged", str(meta["id"]), directory.name)

        meta["updated_at"] = _utc_iso(self._clock())
        _write_atomic_if_changed(job_path, new_job_markdown)
        if new_company_markdown is not None:
            _write_atomic_if_changed(company_path, new_company_markdown)
        _write_atomic_if_changed(directory / "meta.yaml", _dump_yaml(meta))
        self._cache_replace_entry(entry, meta)
        status = "merged" if is_merge else "updated"
        return UpsertResult(status, str(meta["id"]), directory.name)


def _source_rank(source: str | None) -> int:
    return SOURCE_RANKS.get(str(source or "").casefold(), 0)


def _analysis_priority(value: Any) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        return 0
    return value if 0 <= value <= 100 else 0


def _migrate_metadata(meta_path: Path, loaded: dict[str, Any]) -> dict[str, Any]:
    version = loaded.get("schema_version", 1)
    if version == SCHEMA_VERSION:
        return loaded
    if version != 1:
        raise RegistryError(f"unsupported registry schema {version!r}: {meta_path}")

    discovered_at = loaded.get("discovered_at")
    if not isinstance(discovered_at, str) or not discovered_at.strip():
        raise RegistryError(f"legacy registry metadata has no discovered_at: {meta_path}")
    status = loaded.get("status", "found")
    if status not in VACANCY_STATUSES:
        raise RegistryError(f"legacy registry metadata has invalid status: {meta_path}")
    history = loaded.get("status_history")
    if history is None:
        history = [{"status": status, "changed_at": discovered_at}]
    if not isinstance(history, list) or not history:
        raise RegistryError(f"legacy registry metadata has invalid status_history: {meta_path}")

    migrated = dict(loaded)
    migrated["schema_version"] = SCHEMA_VERSION
    migrated["status"] = status
    migrated["status_history"] = history
    _write_atomic_if_changed(meta_path, _dump_yaml(migrated))
    return migrated


def _best_source(refs: list[dict[str, Any]]) -> str:
    sources = sorted((str(ref.get("source", "")) for ref in refs), key=lambda value: (_source_rank(value), value))
    return sources[-1] if sources else ""


def _prefer_content(
    incoming_source: str,
    incoming_body: str,
    current_source: str | None,
    current_body: str,
) -> bool:
    if not current_body:
        return True
    incoming_rank = _source_rank(incoming_source)
    current_rank = _source_rank(current_source)
    if incoming_source == current_source:
        return incoming_body.strip() != current_body.strip()
    if incoming_rank != current_rank:
        return incoming_rank > current_rank
    return len(incoming_body.strip()) > len(current_body.strip())


def _source_ref(job: NormalizedJob) -> dict[str, Any]:
    ref: dict[str, Any] = {
        "source": job.source.strip().lower(),
        "source_job_id": job.source_job_id.strip(),
        "url": job.source_url.strip(),
    }
    if job.source_metadata:
        ref["metadata"] = dict(job.source_metadata)
    return ref


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _utc_iso(value: datetime) -> str:
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    value = value.astimezone(timezone.utc).replace(microsecond=0)
    return value.isoformat().replace("+00:00", "Z")


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _dump_yaml(value: dict[str, Any]) -> str:
    return yaml.safe_dump(value, allow_unicode=True, sort_keys=False, default_flow_style=False)


def _render_markdown(heading: str, body: str) -> str:
    cleaned = body.strip()
    return f"# {heading.strip()}\n" + (f"\n{cleaned}\n" if cleaned else "")


def _render_job_markdown(heading: str, body: str, published_at: str | None) -> str:
    metadata = ""
    if _clean_optional(published_at):
        metadata = f"\nPosted: {str(published_at).strip()}\n"
    cleaned = body.strip()
    return f"# {heading.strip()}\n{metadata}" + (f"\n{cleaned}\n" if cleaned else "")


def _read_markdown_body(path: Path) -> str:
    if not path.exists():
        return ""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    if lines and lines[0] == "":
        lines = lines[1:]
    if lines and lines[0].startswith("Posted: "):
        lines = lines[1:]
    return "\n".join(lines).strip()


def _write_atomic_if_changed(path: Path, content: str) -> bool:
    if path.exists() and path.read_text(encoding="utf-8") == content:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    try:
        temp_path.write_text(content, encoding="utf-8", newline="\n")
        os.replace(temp_path, path)
    finally:
        if temp_path.exists():
            temp_path.unlink()
    return True


def _escape_cell(value: Any) -> str:
    return str(value or "").replace("|", "\\|").replace("\r", " ").replace("\n", " ")


def _markdown_url(value: str) -> str:
    return quote(value, safe=":/?#[]@!$&'*+,;-._~=%")


def _read_match_summary(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    try:
        loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, yaml.YAMLError) as exc:
        raise RegistryError(f"cannot read match analysis {path}: {exc}") from exc
    if not isinstance(loaded, dict):
        raise RegistryError(f"match analysis is not a mapping: {path}")
    score = loaded.get("score")
    recommendation = loaded.get("recommendation")
    if isinstance(score, bool) or not isinstance(score, int) or not 0 <= score <= 100:
        raise RegistryError(f"match analysis has invalid score: {path}")
    if recommendation not in {
        "strong_match",
        "match",
        "possible_match",
        "weak_match",
        "not_match",
    }:
        raise RegistryError(f"match analysis has invalid recommendation: {path}")
    return {"score": score, "recommendation": recommendation}


def _recommendation_label(value: Any) -> str:
    return str(value).replace("_", " ").title()
