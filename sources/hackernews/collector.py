from pathlib import Path
from typing import Mapping

from jobintel.hackernews import HackerNewsCollector


def create_collector(config: Mapping[str, str]) -> HackerNewsCollector:
    return HackerNewsCollector(config, Path(__file__).with_name("config.yaml"))
