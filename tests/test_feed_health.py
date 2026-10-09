from datetime import datetime, timezone
import unittest

from jobintel.feed_health import require_current_feed
from jobintel.models import NormalizedJob


class FeedHealthTests(unittest.TestCase):
    def test_stale_feed_is_not_reported_as_successful_empty_result(self):
        job = NormalizedJob(source="test", source_job_id="1", source_url="https://example.test/1",
                            title="Developer", company="Acme", description="Go", published_at="2026-08-29T02:12:12Z")
        with self.assertRaisesRegex(RuntimeError, "feed is stale.*2026-08-29"):
            require_current_feed([job], datetime(2026, 10, 2, tzinfo=timezone.utc), "Test")

    def test_empty_feed_and_fresh_feed_are_valid(self):
        cutoff = datetime(2026, 10, 2, tzinfo=timezone.utc)
        require_current_feed([], cutoff, "Test")
        job = NormalizedJob(source="test", source_job_id="1", source_url="https://example.test/1",
                            title="Developer", company="Acme", description="Go", published_at="2026-10-09T02:12:12Z")
        require_current_feed([job], cutoff, "Test")

    def test_nonempty_feed_without_dates_fails_clearly(self):
        job = NormalizedJob(source="test", source_job_id="1", source_url="https://example.test/1",
                            title="Developer", company="Acme", description="Go")
        with self.assertRaisesRegex(RuntimeError, "no usable publication dates"):
            require_current_feed([job], datetime(2026, 10, 2, tzinfo=timezone.utc), "Test")
