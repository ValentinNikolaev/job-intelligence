from pathlib import Path
from typing import Mapping

from jobintel.remote_feeds import PublicRemoteFeedCollector


def create_collector(config: Mapping[str, str]) -> PublicRemoteFeedCollector:
    return PublicRemoteFeedCollector("remoteok", config, Path(__file__).with_name("config.yaml"))
