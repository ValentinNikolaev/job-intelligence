from __future__ import annotations

import json
import unittest
from urllib.request import Request

from jobintel.url_intake import UrlIntakeError, load_job_url


class _Response:
    def __init__(self, payload: object) -> None:
        self.body = json.dumps(payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        return None

    def read(self) -> bytes:
        return self.body


class UrlIntakeTests(unittest.TestCase):
    def test_eu_lever_url_uses_public_postings_api_and_normalizes_job(self) -> None:
        requests: list[tuple[Request, float]] = []

        def opener(request: Request, *, timeout: float):
            requests.append((request, timeout))
            return _Response(
                {
                    "id": "posting-42",
                    "text": "Senior PHP Backend Engineer",
                    "descriptionPlain": "Build reliable payment services.",
                    "lists": [
                        {"text": "Requirements", "content": "<ul><li>PHP</li><li>MySQL</li></ul>"}
                    ],
                    "additionalPlain": "Remote in Europe.",
                    "categories": {
                        "location": "Remote - Europe",
                        "commitment": "Full-time",
                        "team": "Engineering",
                    },
                    "workplaceType": "remote",
                    "applyUrl": "https://jobs.eu.lever.co/example/posting-42/apply",
                }
            )

        job = load_job_url(
            "https://jobs.eu.lever.co/example/posting-42?ref=ignored",
            opener=opener,
        )

        self.assertEqual(
            "https://api.eu.lever.co/v0/postings/example/posting-42",
            requests[0][0].full_url,
        )
        self.assertEqual(20, requests[0][1])
        self.assertEqual("manual", job.source)
        self.assertEqual("posting-42", job.source_job_id)
        self.assertEqual("https://jobs.eu.lever.co/example/posting-42", job.source_url)
        self.assertEqual("Example", job.company)
        self.assertEqual("Remote - Europe", job.location)
        self.assertTrue(job.remote)
        self.assertEqual("Full-time", job.employment_type)
        self.assertEqual(100, job.analysis_priority)
        self.assertIn("## Requirements\n\n- PHP\n- MySQL", job.description)
        self.assertEqual("Lever Postings API", job.source_metadata["source_name"])

    def test_global_lever_url_uses_global_api(self) -> None:
        seen: list[str] = []

        def opener(request: Request, *, timeout: float):
            del timeout
            seen.append(request.full_url)
            return _Response(
                {
                    "id": "abc",
                    "text": "Backend Engineer",
                    "descriptionPlain": "Build APIs.",
                    "categories": {},
                }
            )

        load_job_url("https://jobs.lever.co/acme/abc", opener=opener)
        self.assertEqual("https://api.lever.co/v0/postings/acme/abc", seen[0])

    def test_rejects_non_lever_urls_before_network_access(self) -> None:
        with self.assertRaisesRegex(UrlIntakeError, "unsupported vacancy URL"):
            load_job_url("https://example.test/jobs/42")

    def test_rejects_mismatched_posting_id(self) -> None:
        def opener(request: Request, *, timeout: float):
            del request, timeout
            return _Response(
                {"id": "other", "text": "Engineer", "descriptionPlain": "Build services."}
            )

        with self.assertRaisesRegex(UrlIntakeError, "does not match"):
            load_job_url("https://jobs.lever.co/acme/expected", opener=opener)


if __name__ == "__main__":
    unittest.main()

