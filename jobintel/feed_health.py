"""Distinguish a stale upstream feed from a successful empty search."""
from collections.abc import Sequence
from datetime import datetime

from .models import NormalizedJob


def require_current_feed(jobs: Sequence[NormalizedJob], cutoff: datetime, source: str) -> None:
    if not jobs:
        return
    dates = []
    for job in jobs:
        if job.published_at:
            try:
                value = datetime.fromisoformat(job.published_at.replace("Z", "+00:00"))
            except ValueError:
                continue
            if value.tzinfo is not None:
                dates.append(value)
    if not dates:
        raise RuntimeError(f"{source} feed has no usable publication dates")
    newest = max(dates)
    if newest < cutoff:
        raise RuntimeError(f"{source} feed is stale: newest publication {newest.isoformat()}; cutoff {cutoff.isoformat()}")
