from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from typing import Iterable, Mapping, Protocol

from .models import NormalizedJob


class Collector(Protocol):
    name: str

    def fetch(self) -> Iterable[NormalizedJob]: ...


def discover_collectors(sources_dir: Path, config: Mapping[str, str]) -> dict[str, Collector]:
    collectors: dict[str, Collector] = {}
    if not sources_dir.exists():
        return collectors

    for path in sorted(sources_dir.glob("*/collector.py")):
        module_name = f"jobintel_source_{path.parent.name}"
        spec = importlib.util.spec_from_file_location(module_name, path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot load collector module: {path}")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        try:
            spec.loader.exec_module(module)
        except Exception:
            sys.modules.pop(module_name, None)
            raise
        factory = getattr(module, "create_collector", None)
        if not callable(factory):
            raise RuntimeError(f"collector module must expose create_collector(config): {path}")
        collector = factory(config)
        name = str(getattr(collector, "name", "")).strip().lower()
        if not name:
            raise RuntimeError(f"collector has no name: {path}")
        if name in collectors:
            raise RuntimeError(f"duplicate collector name: {name}")
        collectors[name] = collector
    return collectors
