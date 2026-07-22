from __future__ import annotations

import json
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from jobintel.ashby_boards import (
    AshbyBoard,
    AshbyBoardRegistry,
    DEFAULT_CONFIG_PATH,
    board_name_from_candidate,
)


API_ROOT = "https://api.ashbyhq.com/posting-api/job-board"


@dataclass(slots=True)
class DiscoveryResult:
    added: list[str] = field(default_factory=list)
    existing: list[str] = field(default_factory=list)
    invalid: dict[str, str] = field(default_factory=dict)


class AshbyBoardDiscovery:
    def __init__(
        self,
        registry: AshbyBoardRegistry,
        *,
        opener: Callable[..., Any] = urlopen,
    ) -> None:
        self.registry = registry
        self._opener = opener

    def discover(self, candidates: Iterable[str]) -> DiscoveryResult:
        result = DiscoveryResult()
        processed: set[str] = set()
        changed = False
        for candidate in candidates:
            try:
                board = board_name_from_candidate(candidate)
            except ValueError as exc:
                result.invalid[candidate] = str(exc)
                continue
            key = board.casefold()
            if key in processed or self.registry.contains(board):
                result.existing.append(board)
                processed.add(key)
                continue
            processed.add(key)
            try:
                self._validate(board)
            except Exception as exc:
                result.invalid[candidate] = str(exc)
                continue
            if self.registry.add(AshbyBoard(board)):
                result.added.append(board)
                changed = True
        if changed:
            self.registry.save()
        return result

    def _validate(self, board: str) -> None:
        request = Request(
            f"{API_ROOT}/{quote(board, safe='')}",
            headers={"Accept": "application/json", "User-Agent": "job-intelligence/0.1"},
        )
        try:
            with self._opener(request, timeout=self.registry.timeout_seconds) as response:
                payload = json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            raise ValueError(f"validation returned HTTP {exc.code}") from exc
        except URLError as exc:
            raise ValueError(f"validation request failed: {exc.reason}") from exc
        except TimeoutError as exc:
            raise ValueError("validation request timed out") from exc
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise ValueError("validation returned invalid JSON") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("jobs"), list):
            raise ValueError("validation response has no jobs list")


def discover_boards(
    candidates: list[str],
    config: Mapping[str, str],
    default_path: Path = DEFAULT_CONFIG_PATH,
) -> int:
    path = Path(config.get("ASHBY_CONFIG", "") or default_path)
    registry = AshbyBoardRegistry.load(path)
    result = AshbyBoardDiscovery(registry).discover(candidates)
    for board in result.added:
        print(f"Added Ashby board: {board}")
    for board in result.existing:
        print(f"Already registered: {board}")
    for candidate, reason in result.invalid.items():
        print(f"Invalid Ashby board {candidate!r}: {reason}", file=sys.stderr)
    return 1 if result.invalid else 0
