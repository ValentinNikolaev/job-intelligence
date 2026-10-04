from typing import Mapping

from jobintel.job_alerts import JobAlertCollector


def create_collector(config: Mapping[str, str]) -> JobAlertCollector:
    return JobAlertCollector(config, "reteinformaticalavoro")
