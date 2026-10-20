"""Offline operational commands against complete, explicitly selected fixture roots."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
import zipfile

import yaml

from jobintel.models import NormalizedJob
from jobintel.registry import Registry


ROOT = Path(__file__).resolve().parents[1]
RUNTIME_ENVIRONMENT = frozenset({
    "SYSTEMROOT", "WINDIR", "TEMP", "TMP", "TMPDIR", "PATH", "PATHEXT", "COMSPEC",
})


def snapshot(root: Path) -> dict[str, bytes | None]:
    return {path.relative_to(root).as_posix(): path.read_bytes() if path.is_file() else None
            for path in root.rglob("*")}


class AccountAutomationTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory(prefix="jobintel-automation-")
        self.addCleanup(temporary.cleanup)
        self.sandbox = Path(temporary.name).resolve()
        self.selected = self.sandbox / "selected"
        self.unrelated = self.sandbox / "unrelated"
        with patch.dict(os.environ, {}, clear=True):
            self.selected_jobs = self._seed_root(self.selected, "Selected")
            self._seed_root(self.unrelated, "Unrelated")
        self.unrelated_before = snapshot(self.unrelated)
        self.external_env = self.sandbox / "external/scheduled.env"
        self.external_env.parent.mkdir()
        self.external_env.write_text("JOBINTEL_COLLECTION_LIMIT=7\n", encoding="utf-8")
        self.bootstrap = self.sandbox / "bootstrap"
        self.bootstrap.mkdir()
        self.ready = self.sandbox / "guard-ready.txt"
        self.denied = self.sandbox / "guard-denied.txt"
        self._install_guard()

    def tearDown(self):
        self.assertEqual(self.unrelated_before, snapshot(self.unrelated), "foreign cwd was mutated")

    def _seed_root(self, root: Path, label: str) -> dict[str, Path]:
        (root / "config").mkdir(parents=True)
        for name in ("accounts.yaml", "selection-policy.yaml", "matching-policy.yaml", "codex-workflows.yaml"):
            (root / "config" / name).write_bytes((ROOT / "config" / name).read_bytes())
        (root / "config/data-services.yaml").write_text(
            "storage:\n  backend: yaml\n  cutover_verified: false\n", encoding="utf-8",
        )
        (root / "sources").mkdir()
        (root / "sources/.env").write_text(
            "JOBINTEL_COLLECTION_LIMIT=99\nTELEGRAM_BOT_TOKEN=synthetic-token\n"
            "TELEGRAM_CHAT_ID=synthetic-chat\n", encoding="utf-8",
        )
        (root / "registry/candidate").mkdir(parents=True)
        (root / "registry/candidate/match-profile.md").write_text(
            "# Synthetic candidate\n\nFixture evidence only: Go backend development.\n", encoding="utf-8",
        )
        (root / "prompts").mkdir()
        (root / "prompts/vacancy-match.md").write_bytes((ROOT / "prompts/vacancy-match.md").read_bytes())
        jobs = {}
        for kind in ("pending", "low"):
            registry = Registry(root / "registry", clock=lambda: datetime.now(timezone.utc),
                                id_factory=lambda kind=kind: f"{label.lower()}-{kind}")
            result = registry.upsert(NormalizedJob(
                source="direct", source_job_id=kind,
                source_url=f"https://example.test/{label.lower()}/{kind}",
                title=f"{label} {kind} Go Engineer", company=f"{label} Fixture Company",
                description="Build Go backend services. This is synthetic test data.",
                remote=True, location="Remote EU",
            ))
            jobs[kind] = root / "registry/jobs" / result.directory
        (jobs["low"] / "match.yaml").write_text(
            "score: 40\nrecommendation: weak_match\nsummary: Synthetic low score.\n", encoding="utf-8",
        )
        (root / "registry/source-api-usage.yaml").write_text(yaml.safe_dump({"sources": {
            "fixture-source": {"total_requests": 5, "last_status": "success", "runs": [
                {"requests": 5, "fetched": 3, "created": 2, "errors": 0},
            ]},
        }}), encoding="utf-8")
        return jobs

    def _install_guard(self):
        # Installed before the real entrypoint imports; no project transport is mocked.
        code = f'''
import os
from pathlib import Path
import socket
import sys
sandbox = Path({str(self.sandbox)!r})
denied = Path({str(self.denied)!r})
socketpair_depth = 0
original_socketpair = socket.socketpair
def local_socketpair(*args, **kwargs):
    global socketpair_depth
    socketpair_depth += 1
    try:
        return original_socketpair(*args, **kwargs)
    finally:
        socketpair_depth -= 1
socket.socketpair = local_socketpair
def inside(value):
    return isinstance(value, int) or Path(os.fsdecode(value)).resolve().is_relative_to(sandbox)
def guard(event, args):
    forbidden = event in {{"socket.connect", "socket.getaddrinfo", "socket.sendto", "socket.sendmsg", "subprocess.Popen", "os.system"}}
    # Windows asyncio uses the stdlib socketpair fallback for its internal wakeup pipe.
    if event == "socket.connect" and socketpair_depth and args[1][0] in {{"127.0.0.1", "::1"}}:
        forbidden = False
    if event == "open":
        path, mode, flags = args
        writing = (mode is not None and any(mark in mode for mark in "wax+")) or flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC | os.O_APPEND)
        forbidden = forbidden or (writing and not inside(path))
    if event in {{"os.mkdir", "os.remove", "os.rmdir"}}:
        forbidden = forbidden or not inside(args[0])
    if event in {{"os.rename", "os.link", "os.symlink"}}:
        forbidden = forbidden or not inside(args[0]) or not inside(args[1])
    if forbidden:
        with denied.open("a", encoding="utf-8") as output:
            output.write(event + "\\n")
        raise RuntimeError("synthetic automation guard denied " + event)
sys.addaudithook(guard)
with open({str(self.ready)!r}, "a", encoding="utf-8") as output:
    output.write(str(os.getpid()) + "\\n")
'''
        (self.bootstrap / "sitecustomize.py").write_text(code, encoding="utf-8")

    def _environment(self) -> dict[str, str]:
        environment = {key: value for key, value in os.environ.items() if key.upper() in RUNTIME_ENVIRONMENT}
        environment.update({
            "JOBINTEL_ACCOUNT": "current", "PYTHONDONTWRITEBYTECODE": "1",
            "PYTHONPATH": os.pathsep.join((str(self.bootstrap), str(ROOT))),
            "PYTHONIOENCODING": "utf-8",
        })
        return environment

    def _run(self, arguments: list[str], expected: int = 0) -> subprocess.CompletedProcess:
        previous = self.ready.read_text(encoding="utf-8").splitlines() if self.ready.exists() else []
        result = subprocess.run([sys.executable, *arguments], cwd=self.unrelated,
                                env=self._environment(), capture_output=True, text=True,
                                encoding="utf-8", timeout=30)
        ready = self.ready.read_text(encoding="utf-8").splitlines() if self.ready.exists() else []
        self.assertEqual(len(previous) + 1, len(ready), "child transport guard did not start")
        self.assertEqual(expected, result.returncode, result.stdout + result.stderr)
        if expected == 0:
            self.assertFalse(self.denied.exists(), "operational command attempted a forbidden effect")
        return result

    def _command(self, *arguments: str) -> list[str]:
        return [str(ROOT / "run.py"), "--project-root", str(self.selected), *arguments,
                "--env", str(self.external_env)]

    def _api(self, name: str) -> dict:
        return json.loads(self._run(self._command("api", name, "--json")).stdout)

    def test_seeded_benchmark_and_storage_commands_ignore_hostile_ambient_environment(self):
        selected_before = snapshot(self.selected)
        hostile = {"JOBINTEL_ACCOUNT": "other", "MONGODB_URI": "mongodb://production.invalid",
                   "JOBINTEL_DATABASE_NAME": "production", "TELEGRAM_BOT_TOKEN": "hostile-token",
                   "TELEGRAM_CHAT_ID": "hostile-chat", "JOBINTEL_COLLECTION_LIMIT": "501",
                   "PYTHONPATH": "hostile-path", "HTTP_PROXY": "http://production.invalid"}
        with patch.dict(os.environ, hostile):
            excluded = set(hostile) - {"JOBINTEL_ACCOUNT", "PYTHONPATH"}
            self.assertTrue(excluded.isdisjoint(self._environment()))
            self.assertEqual("current", self._environment()["JOBINTEL_ACCOUNT"])
            self.assertEqual("current", self._run([
                "-m", "jobintel.accounts", "--project-root", str(self.selected), "--account", "current",
            ]).stdout.strip())
            usage = self._api("source-usage")["sources"]
            self.assertEqual(["fixture-source"], [row["source"] for row in usage])
            self.assertEqual((5, 3, 2), tuple(usage[0][field] for field in ("total_requests", "last_fetched", "last_created")))
            vacancies = self._api("catalog-vacancies")["vacancies"]
            self.assertEqual({"selected-pending", "selected-low"}, {row["vacancy_id"] for row in vacancies})
            summary = self._api("workflow-summary")
            self.assertEqual((2, 1), (summary["vacancies_total"], summary["analyzed_total"]))
            self.assertGreater(summary["pending_analyze"], 0)
            self.assertEqual(7, self._api("workflow-limits")["collection_limit_per_source"])
            doctor = json.loads(self._run(self._command("storage", "doctor", "--ci")).stdout)
            self.assertEqual({"backend": "yaml", "cutover": False, "ok": True}, doctor)
        self.assertEqual(selected_before, snapshot(self.selected), "read-only commands wrote fixture data")

    def test_actions_archive_index_and_catalog_mutate_only_selected_fixture(self):
        low = self.selected_jobs["low"]
        original = snapshot(low)
        self._run([str(ROOT / "scripts/archive_jobs.py"), "low-score", "--project-root", str(self.selected)])
        self.assertFalse(low.exists())
        self.assertTrue(self.selected_jobs["pending"].exists())
        archives = list((self.selected / "archives").rglob("*.zip"))
        self.assertEqual(1, len(archives))
        with zipfile.ZipFile(archives[0]) as archive:
            archived = {name.removeprefix(low.name + "/"): archive.read(name) for name in archive.namelist()}
        self.assertEqual({name: value for name, value in original.items() if value is not None}, archived)
        self._run(self._command("reindex"))
        self._run(self._command("catalog"))
        for path in (self.selected / "registry/index.md", self.selected / "catalog/index.md"):
            content = path.read_text(encoding="utf-8")
            self.assertIn("Selected pending Go Engineer", content)
            self.assertNotIn("Selected low Go Engineer", content)
            self.assertNotIn("Unrelated", content)
        rows = self._api("catalog-vacancies")["vacancies"]
        self.assertEqual(["selected-pending"], [row["vacancy_id"] for row in rows])

    def test_telegram_duplicate_receipt_uses_real_entrypoint_without_transport(self):
        base = self.selected / "notifications/telegram"
        (base / "outbox").mkdir(parents=True)
        (base / "sent").mkdir()
        item = {"company": "Synthetic Company", "title": "Synthetic Engineer", "score": 80,
                "vacancy_id": "selected-pending", "directory": self.selected_jobs["pending"].name,
                "url": "https://example.test/selected/pending", "country_codes": []}
        payload = {"schema_version": 2, "channel": "telegram", "initiator": "fixture",
                   "minimum_score": 65, "items": [item]}
        notification_id = hashlib.sha256(json.dumps(payload, ensure_ascii=False, sort_keys=True,
                                                    separators=(",", ":")).encode("utf-8")).hexdigest()
        notification = {**payload, "notification_id": notification_id, "created_at": "2026-10-20T00:00:00Z"}
        outbox = base / "outbox/current.json"
        outbox.write_text(json.dumps(notification), encoding="utf-8")
        prior = base / "sent/prior.json"
        prior.write_text(json.dumps({**notification, "delivery_status": "sent",
                                     "delivered_vacancy_ids": ["selected-pending"]}), encoding="utf-8")
        prior_bytes = prior.read_bytes()
        self._run([str(ROOT / "scripts/deliver_telegram_outbox.py"), "--project-root", str(self.selected),
                   "--outbox-file", str(outbox), "--sent-dir", str(base / "sent"),
                   "--receipt-dir", str(base / "receipts")])
        self.assertFalse(outbox.exists())
        self.assertEqual(prior_bytes, prior.read_bytes())
        receipt = json.loads((base / "sent/current.json").read_text(encoding="utf-8"))
        self.assertEqual(notification_id, receipt["notification_id"])
        self.assertEqual("duplicate_skipped", receipt["delivery_status"])
        self.assertEqual([], receipt["delivered_vacancy_ids"])
        self.assertIsNone(receipt["telegram_message_id"])
        self.assertFalse((base / "receipts").exists())

    def test_transport_guard_rejects_connection_before_external_access(self):
        result = self._run(["-c", "import socket; socket.create_connection(('example.test', 443))"], expected=1)
        self.assertIn("synthetic automation guard denied socket.getaddrinfo", result.stderr)
        self.assertEqual("socket.getaddrinfo\n", self.denied.read_text(encoding="utf-8"))
        result = self._run(["-c", "import socket; socket.socket().connect(('127.0.0.1', 9))"], expected=1)
        self.assertIn("synthetic automation guard denied socket.connect", result.stderr)
        self.assertEqual("socket.getaddrinfo\nsocket.connect\n", self.denied.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
