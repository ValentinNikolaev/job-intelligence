from __future__ import annotations

import os
import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import unquote, urlsplit

import yaml


DEFAULT_CONFIG_PATH = Path(__file__).parents[1] / "sources" / "ashby" / "config.yaml"
_BOARD_PATTERN = re.compile(r"[A-Za-z0-9](?:[A-Za-z0-9._~-]*[A-Za-z0-9])?")


@dataclass(frozen=True, slots=True)
class AshbyBoard:
    name: str
    company: str | None = None


@dataclass(frozen=True, slots=True)
class AshbyFilters:
    remote_only: bool = False
    location_terms: tuple[str, ...] = ()
    title_terms: tuple[str, ...] = ()


class AshbyBoardRegistry:
    def __init__(
        self,
        path: Path,
        boards: list[AshbyBoard] | None = None,
        *,
        timeout_seconds: float = 30.0,
        filters: AshbyFilters | None = None,
    ) -> None:
        self.path = path
        self.boards = list(boards or [])
        self.timeout_seconds = timeout_seconds
        self.filters = filters or AshbyFilters()

    @classmethod
    def load(cls, path: Path = DEFAULT_CONFIG_PATH) -> "AshbyBoardRegistry":
        try:
            loaded = yaml.safe_load(path.read_text(encoding="utf-8"))
        except OSError as exc:
            raise ValueError(f"cannot read Ashby board registry {path}: {exc}") from exc
        except yaml.YAMLError as exc:
            raise ValueError(f"invalid Ashby board registry YAML {path}: {exc}") from exc
        if loaded is None:
            loaded = {}
        if not isinstance(loaded, dict):
            raise ValueError(f"Ashby board registry must be a YAML mapping: {path}")
        unknown = sorted(set(loaded) - {"version", "timeout_seconds", "filters", "boards"})
        if unknown:
            raise ValueError(f"unknown Ashby config fields: {', '.join(unknown)}")
        if loaded.get("version", 1) != 1:
            raise ValueError("unsupported Ashby config version")

        timeout = _positive_float(loaded.get("timeout_seconds", 30), "timeout_seconds")
        raw_boards = loaded.get("boards", [])
        if not isinstance(raw_boards, list):
            raise ValueError("Ashby boards must be a YAML list")
        filters = _load_filters(loaded.get("filters"))
        registry = cls(path, timeout_seconds=timeout, filters=filters)
        for index, raw in enumerate(raw_boards, 1):
            if not isinstance(raw, dict):
                raise ValueError(f"Ashby board {index} must be a mapping")
            unknown_fields = sorted(set(raw) - {"name", "company"})
            if unknown_fields:
                raise ValueError(
                    f"unknown fields in Ashby board {index}: {', '.join(unknown_fields)}"
                )
            name = normalize_board_name(raw.get("name"))
            company = _optional_string(raw.get("company"))
            registry.add(AshbyBoard(name, company))
        return registry

    def contains(self, name: str) -> bool:
        key = normalize_board_name(name).casefold()
        return any(board.name.casefold() == key for board in self.boards)

    def add(self, board: AshbyBoard) -> bool:
        normalized = AshbyBoard(
            normalize_board_name(board.name),
            _optional_string(board.company),
        )
        if any(existing.name.casefold() == normalized.name.casefold() for existing in self.boards):
            return False
        self.boards.append(normalized)
        self.boards.sort(key=lambda item: item.name.casefold())
        return True

    def save(self) -> None:
        value: dict[str, Any] = {
            "version": 1,
            "timeout_seconds": self.timeout_seconds,
        }
        if self.filters != AshbyFilters():
            value["filters"] = {
                "remote_only": self.filters.remote_only,
                "location_terms": list(self.filters.location_terms),
                "title_terms": list(self.filters.title_terms),
            }
        value["boards"] = []
        for board in self.boards:
            item = {"name": board.name}
            if board.company:
                item["company"] = board.company
            value["boards"].append(item)
        content = yaml.safe_dump(
            value,
            allow_unicode=True,
            sort_keys=False,
            default_flow_style=False,
        )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temp_path = self.path.with_name(f".{self.path.name}.{uuid.uuid4().hex}.tmp")
        try:
            temp_path.write_text(content, encoding="utf-8", newline="\n")
            os.replace(temp_path, self.path)
        finally:
            if temp_path.exists():
                temp_path.unlink()


def extract_board_name(url: str) -> str:
    try:
        parsed = urlsplit(str(url).strip())
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid Ashby URL") from exc
    if (
        parsed.scheme.casefold() != "https"
        or parsed.hostname is None
        or parsed.hostname.casefold() != "jobs.ashbyhq.com"
        or parsed.username is not None
        or parsed.password is not None
        or port not in (None, 443)
    ):
        raise ValueError("URL must use https://jobs.ashbyhq.com")
    first_segment = parsed.path.lstrip("/").split("/", 1)[0]
    if not first_segment:
        raise ValueError("Ashby URL has no board name")
    return normalize_board_name(unquote(first_segment))


def normalize_board_name(value: object) -> str:
    name = str(value or "").strip()
    if not name or not _BOARD_PATTERN.fullmatch(name) or name in {".", ".."}:
        raise ValueError(f"invalid Ashby board name: {name!r}")
    return name


def board_name_from_candidate(value: str) -> str:
    candidate = value.strip()
    return extract_board_name(candidate) if "://" in candidate else normalize_board_name(candidate)


def _optional_string(value: object) -> str | None:
    if not isinstance(value, str):
        return None
    result = value.strip()
    return result or None


def _positive_float(value: object, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be a number")
    try:
        result = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be a number") from exc
    if result <= 0:
        raise ValueError(f"{name} must be greater than zero")
    return result


def _load_filters(value: object) -> AshbyFilters:
    if value is None:
        return AshbyFilters()
    if not isinstance(value, dict):
        raise ValueError("Ashby filters must be a YAML mapping")
    unknown = sorted(set(value) - {"remote_only", "location_terms", "title_terms"})
    if unknown:
        raise ValueError(f"unknown Ashby filter fields: {', '.join(unknown)}")
    remote_only = value.get("remote_only", False)
    if not isinstance(remote_only, bool):
        raise ValueError("Ashby filters.remote_only must be true or false")
    return AshbyFilters(
        remote_only=remote_only,
        location_terms=_string_terms(value.get("location_terms"), "filters.location_terms"),
        title_terms=_string_terms(value.get("title_terms"), "filters.title_terms"),
    )


def _string_terms(value: object, name: str) -> tuple[str, ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError(f"Ashby {name} must be a YAML list")
    result: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value, 1):
        if not isinstance(item, str) or not item.strip():
            raise ValueError(f"Ashby {name}[{index}] must be a non-empty string")
        term = item.strip()
        key = term.casefold()
        if key not in seen:
            result.append(term)
            seen.add(key)
    return tuple(result)
