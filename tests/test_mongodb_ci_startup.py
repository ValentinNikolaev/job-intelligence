from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
from tempfile import TemporaryDirectory
import unittest

import yaml


ROOT = Path(__file__).resolve().parents[1]
HELPER = ROOT / ".github/scripts/start-test-mongodb.sh"


class MongoCIStartupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bash = ("C:/Program Files/Git/bin/bash.exe" if os.name == "nt" else shutil.which("bash"))
        if not cls.bash or not Path(cls.bash).is_file():
            raise unittest.SkipTest("Bash is unavailable for MongoDB CI helper checks")

    def run_startup(self, scenario):
        with TemporaryDirectory() as temporary:
            root = Path(temporary)
            calls = root / "calls.txt"
            docker = root / "docker"
            docker.write_text("""#!/usr/bin/env bash
printf '%s\\n' "$*" >> "$STUB_CALLS"
case "$1" in
  run)
    if [ "$STUB_SCENARIO" = run-failure ]; then exit 23; fi
    echo synthetic-container ;;
  inspect)
    if [[ "$3" == *exit_code* ]]; then
      if [ "$STUB_SCENARIO" = diagnostics-failure ]; then exit 91; fi
      echo 'status=exited running=false exit_code=42 oom_killed=true error=synthetic started_at=synthetic finished_at=synthetic'
    elif [[ "$STUB_SCENARIO" == early-exit || "$STUB_SCENARIO" == command-timeout || "$STUB_SCENARIO" == stubborn-command ]]; then echo exited
    else echo running; fi ;;
  logs)
    if [ "$STUB_SCENARIO" = diagnostics-failure ]; then exit 92; fi
    if [ "$STUB_SCENARIO" = oversized-logs ]; then printf '%040000d\\n' 0; exit 0; fi
    echo 'synthetic MongoDB log' ;;
  exec)
    if [ "$STUB_SCENARIO" = command-timeout ]; then exec /usr/bin/sleep 20; fi
    if [ "$STUB_SCENARIO" = stubborn-command ]; then trap '' TERM; exec /usr/bin/sleep 20; fi
    if [[ "$*" == *rs.initiate* ]]; then
      if [[ "$STUB_SCENARIO" == init-failure || "$STUB_SCENARIO" == diagnostics-failure || "$STUB_SCENARIO" == oversized-logs ]]; then exit 42; fi
    elif [[ "$*" == *db.hello* ]]; then
      if [ "$STUB_SCENARIO" = primary-timeout ]; then exit 7; fi
    elif [[ "$STUB_SCENARIO" == early-exit || "$STUB_SCENARIO" == ping-timeout ]]; then exit 6
    fi ;;
  *) exit 93 ;;
esac
""", encoding="utf-8", newline="\n")
            docker.chmod(0o755)
            sleeper = root / "sleep"
            sleeper.write_text("#!/usr/bin/env bash\nexit 0\n", encoding="utf-8", newline="\n")
            sleeper.chmod(0o755)
            environment = dict(os.environ, STUB_SCENARIO=scenario, STUB_CALLS=calls.as_posix())
            result = subprocess.run(
                [self.bash, "-c", 'stub_directory=$(cd "$1" && pwd); export PATH="$stub_directory:$PATH"; bash "$2"',
                 "mongo-startup-test", root.as_posix(), HELPER.as_posix()],
                cwd=ROOT, env=environment, capture_output=True, text=True, timeout=60,
            )
            return result, calls.read_text(encoding="utf-8").splitlines()

    def assert_diagnostics(self, result, calls):
        self.assertIn("bounded disposable-container diagnostics", result.stderr)
        self.assertTrue(any("inspect --format status={{.State.Status}}" in call for call in calls))
        self.assertIn("logs --tail 120 --timestamps jobintel-test-mongo", calls)
        self.assertNotIn(".Config", "\n".join(calls))
        self.assertFalse(any(call.startswith(("rm ", "restart ")) for call in calls))

    def test_success_starts_only_loopback_service_and_waits_for_primary(self):
        result, calls = self.run_startup("success")
        self.assertEqual(0, result.returncode, result.stderr)
        self.assertEqual("run -d --name jobintel-test-mongo -p 127.0.0.1:27018:27017 mongo:8.0 --replSet rs0 --bind_ip_all", calls[0])
        self.assertEqual(4, len(calls))
        self.assertIn("isWritablePrimary", calls[-1])
        self.assertNotIn("diagnostics", result.stderr)

    def test_early_container_exit_stops_polling_and_reports_state(self):
        result, calls = self.run_startup("early-exit")
        self.assertEqual(6, result.returncode, result.stderr)
        self.assertIn("stopped during ping", result.stderr)
        self.assertEqual(1, sum(call.startswith("exec ") for call in calls))
        self.assertIn("exit_code=42 oom_killed=true", result.stderr)
        self.assert_diagnostics(result, calls)

    def test_ping_readiness_exhaustion_never_initializes_replication(self):
        result, calls = self.run_startup("ping-timeout")
        self.assertEqual(6, result.returncode, result.stderr)
        self.assertIn("ping readiness exhausted after 30 attempts", result.stderr)
        self.assertEqual(30, sum(call.startswith("exec ") for call in calls))
        self.assertFalse(any("rs.initiate" in call for call in calls))
        self.assert_diagnostics(result, calls)

    def test_primary_readiness_exhaustion_is_a_failure(self):
        result, calls = self.run_startup("primary-timeout")
        self.assertEqual(7, result.returncode, result.stderr)
        self.assertIn("primary readiness exhausted after 30 attempts", result.stderr)
        self.assertEqual(30, sum("db.hello" in call for call in calls))
        self.assert_diagnostics(result, calls)

    def test_initialization_failure_preserves_command_status(self):
        result, calls = self.run_startup("init-failure")
        self.assertEqual(42, result.returncode, result.stderr)
        self.assertFalse(any("db.hello" in call for call in calls))
        self.assert_diagnostics(result, calls)

    def test_diagnostics_failures_cannot_replace_original_failure(self):
        result, calls = self.run_startup("diagnostics-failure")
        self.assertEqual(42, result.returncode, result.stderr)
        self.assertIn("Container state diagnostics unavailable", result.stderr)
        self.assertIn("Container log diagnostics unavailable", result.stderr)
        self.assert_diagnostics(result, calls)

    def test_run_failure_still_collects_diagnostics(self):
        result, calls = self.run_startup("run-failure")
        self.assertEqual(23, result.returncode, result.stderr)
        self.assertFalse(any(call.startswith("exec ") for call in calls))
        self.assert_diagnostics(result, calls)

    def test_a_stuck_docker_command_is_terminated(self):
        result, calls = self.run_startup("command-timeout")
        self.assertEqual(124, result.returncode, result.stderr)
        self.assertEqual(1, sum(call.startswith("exec ") for call in calls))
        self.assert_diagnostics(result, calls)

    def test_a_command_ignoring_termination_is_killed(self):
        result, calls = self.run_startup("stubborn-command")
        self.assertEqual(137, result.returncode, result.stderr)
        self.assertEqual(1, sum(call.startswith("exec ") for call in calls))
        self.assert_diagnostics(result, calls)

    def test_log_output_is_capped_even_for_a_single_oversized_line(self):
        result, calls = self.run_startup("oversized-logs")
        self.assertEqual(42, result.returncode, result.stderr)
        self.assertLess(len(result.stderr.encode("utf-8")), 34000)
        self.assertIn("0" * 1000, result.stderr)
        self.assert_diagnostics(result, calls)

    def test_checked_in_helper_has_lf_and_valid_bash_syntax(self):
        self.assertNotIn(b"\r", HELPER.read_bytes())
        result = subprocess.run([self.bash, "-n", str(HELPER)], cwd=ROOT, capture_output=True, text=True, timeout=10)
        self.assertEqual(0, result.returncode, result.stderr)
        attributes = (ROOT / ".gitattributes").read_text(encoding="utf-8")
        self.assertIn("/.github/scripts/start-test-mongodb.sh text eol=lf", attributes.splitlines())

    def test_workflow_keeps_real_tests_and_always_cleanup(self):
        workflow = yaml.safe_load((ROOT / ".github/workflows/mongodb-tests.yml").read_text(encoding="utf-8"))
        triggers = workflow.get("on", workflow.get(True))
        self.assertIn(".github/scripts/start-test-mongodb.sh", triggers["push"]["paths"])
        steps = workflow["jobs"]["tests"]["steps"]
        self.assertIn("bash .github/scripts/start-test-mongodb.sh", [step.get("run") for step in steps])
        tests = next(step for step in steps if step.get("run") == "python -m unittest discover -v")
        self.assertEqual("current", tests["env"]["JOBINTEL_ACCOUNT"])
        self.assertEqual("mongodb://127.0.0.1:27018/?replicaSet=rs0&directConnection=true", tests["env"]["JOBINTEL_TEST_MONGODB_URI"])
        cleanup = next(step for step in steps if step.get("run") == "docker rm -f jobintel-test-mongo")
        self.assertEqual("always()", cleanup["if"])


if __name__ == "__main__":
    unittest.main()
