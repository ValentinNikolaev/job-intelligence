from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Any
from urllib.error import HTTPError

import yaml


COLLECTOR_PATH = Path(__file__).parents[1] / "sources" / "greenhouse" / "collector.py"
SPEC = importlib.util.spec_from_file_location("test_greenhouse_collector", COLLECTOR_PATH)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
GreenhouseBoard = MODULE.GreenhouseBoard
GreenhouseCollector = MODULE.GreenhouseCollector
GreenhouseFilters = MODULE.GreenhouseFilters
parse_board_response = MODULE.parse_board_response


class FakeResponse:
    def __init__(self, value: Any) -> None:
        self.payload = json.dumps(value).encode("utf-8")

    def __enter__(self) -> "FakeResponse":
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.payload


def api_job(**overrides: Any) -> dict[str, Any]:
    value = {
        "id": 6123195004,
        "internal_job_id": 5187356004,
        "title": "Senior Backend Engineer - Databases - Loki Ingest | Germany | Remote",
        "absolute_url": "https://job-boards.greenhouse.io/grafanalabs/jobs/6123195004",
        "location": {"name": "Germany (Remote)"},
        "company_name": "Grafana Labs",
        "first_published": "2026-07-23T08:00:00-04:00",
        "updated_at": "2026-07-24T10:00:00-04:00",
        "requisition_id": "27401",
        "application_deadline": None,
        "content": (
            "&lt;div&gt;&lt;p&gt;Build &lt;strong&gt;Loki&lt;/strong&gt; ingest "
            "services.&lt;/p&gt;&lt;/div&gt;"
        ),
        "departments": [{"id": 4044018004, "name": "R&D : Databases"}],
        "offices": [{"id": 4087968004, "name": "Germany (Remote)"}],
        "metadata": [{"name": "Employment Type", "value": "Full-time"}],
        "data_compliance": [{"type": "gdpr", "requires_consent": False}],
    }
    value.update(overrides)
    return value


class GreenhouseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.config_path = Path(self.temp.name) / "greenhouse.yaml"

    def tearDown(self) -> None:
        self.temp.cleanup()

    def _write_config(self, boards: list[dict[str, str] | str]) -> None:
        self.config_path.write_text(
            yaml.safe_dump({"version": 1, "timeout_seconds": 12, "boards": boards}),
            encoding="utf-8",
        )

    def test_fetches_board_with_content_and_normalizes_jobs(self) -> None:
        self._write_config([{"token": "grafanalabs", "company": "Grafana Labs"}])

        def opener(request: Any, timeout: float) -> FakeResponse:
            self.assertEqual(12.0, timeout)
            self.assertEqual(
                "https://boards-api.greenhouse.io/v1/boards/grafanalabs/jobs?content=true",
                request.full_url,
            )
            self.assertEqual("application/json", request.headers["Accept"])
            return FakeResponse({"jobs": [api_job()]})

        collector = GreenhouseCollector(
            {"GREENHOUSE_CONFIG": str(self.config_path)}, opener=opener
        )
        jobs = list(collector.fetch())

        self.assertEqual(1, len(jobs))
        job = jobs[0]
        self.assertEqual("greenhouse", job.source)
        self.assertEqual("6123195004", job.source_job_id)
        self.assertEqual("Grafana Labs", job.company)
        self.assertEqual("Germany (Remote)", job.location)
        self.assertTrue(job.remote)
        self.assertEqual("2026-07-23T08:00:00-04:00", job.published_at)
        self.assertIn("Build **Loki** ingest services.", job.description)
        self.assertEqual("grafanalabs", job.source_metadata["board"])
        self.assertEqual("27401", job.source_metadata["requisition_id"])
        self.assertEqual("R&D : Databases", job.source_metadata["departments"][0]["name"])
        self.assertEqual("Germany (Remote)", job.source_metadata["offices"][0]["name"])

    def test_parses_response_with_filters_and_remote_detection_from_title_or_location(self) -> None:
        filters = GreenhouseFilters(
            remote_only=True,
            location_terms=("Germany", "Europe"),
            title_terms=("backend", "platform engineer"),
        )
        jobs = parse_board_response(
            GreenhouseBoard("grafanalabs", "Grafana Labs"),
            {
                "jobs": [
                    api_job(id=1, title="Backend Engineer | Germany | Remote"),
                    api_job(id=2, title="Platform Engineer | Remote", location={"name": "Europe (Remote)"}),
                    api_job(id=3, title="Backend Engineer", location={"name": "Berlin"}),
                    api_job(id=4, title="Account Executive | Germany | Remote"),
                    api_job(
                        id=5,
                        title="Backend Engineer | United States | Remote",
                        location={"name": "United States (Remote)"},
                        offices=[],
                    ),
                ]
            },
            filters,
        )

        self.assertEqual(["1", "2"], [job.source_job_id for job in jobs])
        self.assertTrue(all(job.remote for job in jobs))

    def test_board_company_falls_back_to_payload_company_name(self) -> None:
        job = parse_board_response(
            GreenhouseBoard("grafanalabs"),
            {"jobs": [api_job(company_name="Grafana Labs")]},
        )[0]

        self.assertEqual("Grafana Labs", job.company)

    def test_failing_board_does_not_stop_other_boards(self) -> None:
        self._write_config(
            [
                {"token": "broken", "company": "Broken"},
                {"token": "grafanalabs", "company": "Grafana Labs"},
            ]
        )

        def opener(request: Any, timeout: float) -> FakeResponse:
            if "/broken/" in request.full_url:
                raise HTTPError(request.full_url, 404, "Not Found", None, None)
            return FakeResponse({"jobs": [api_job()]})

        collector = GreenhouseCollector(
            {"GREENHOUSE_CONFIG": str(self.config_path)}, opener=opener
        )
        jobs = list(collector.fetch())

        self.assertEqual(["Grafana Labs"], [job.company for job in jobs])
        self.assertEqual(1, collector.errors)

    def test_config_rejects_unknown_fields_and_invalid_tokens(self) -> None:
        cases = [
            {"version": 1, "unknown": True, "boards": []},
            {"version": 1, "boards": [{"token": "bad/token"}]},
            {"version": 1, "filters": {"remote_only": "yes"}, "boards": []},
            {"version": 1, "filters": {"title_terms": "backend"}, "boards": []},
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                self.config_path.write_text(
                    yaml.safe_dump(payload),
                    encoding="utf-8",
                )
                with self.assertRaises(ValueError):
                    GreenhouseCollector({"GREENHOUSE_CONFIG": str(self.config_path)})


if __name__ == "__main__":
    unittest.main()
