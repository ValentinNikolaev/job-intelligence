#!/usr/bin/env bash
set -euo pipefail

container=jobintel-test-mongo

report_failure() {
  local failure=$?
  trap - EXIT
  if [ "$failure" -ne 0 ]; then
    echo 'MongoDB test startup failed; bounded disposable-container diagnostics follow.' >&2
    timeout --kill-after=2s 5s docker inspect --format 'status={{.State.Status}} running={{.State.Running}} exit_code={{.State.ExitCode}} oom_killed={{.State.OOMKilled}} error={{.State.Error}} started_at={{.State.StartedAt}} finished_at={{.State.FinishedAt}}' "$container" >&2 || echo 'Container state diagnostics unavailable.' >&2
    echo 'Container logs (last 120 lines, at most 32768 bytes):' >&2
    timeout --kill-after=2s 5s docker logs --tail 120 --timestamps "$container" 2>&1 | head -c 32768 >&2 || echo 'Container log diagnostics unavailable or truncated.' >&2
  fi
  exit "$failure"
}
trap report_failure EXIT

wait_for_mongo() {
  local stage=$1 expression=$2 attempt status failure=1
  for ((attempt = 1; attempt <= 30; attempt++)); do
    if timeout --kill-after=2s 5s docker exec "$container" mongosh --quiet --eval "$expression"; then
      return 0
    else
      failure=$?
    fi
    status=$(timeout --kill-after=2s 5s docker inspect --format '{{.State.Status}}' "$container")
    if [ "$status" != 'running' ]; then
      echo "MongoDB test container stopped during ${stage} (state: ${status})." >&2
      return "$failure"
    fi
    if [ "$attempt" -lt 30 ]; then sleep 1; fi
  done
  echo "MongoDB test ${stage} readiness exhausted after 30 attempts." >&2
  return "$failure"
}

timeout --kill-after=2s 60s docker run -d --name "$container" -p 127.0.0.1:27018:27017 mongo:8.0 --replSet rs0 --bind_ip_all
wait_for_mongo ping 'if (db.adminCommand({ping:1}).ok !== 1) quit(1)'
timeout --kill-after=2s 10s docker exec "$container" mongosh --quiet --eval 'const result = rs.initiate({_id:"rs0",members:[{_id:0,host:"localhost:27017"}]}); if (result.ok !== 1) quit(1)'
wait_for_mongo primary 'if (!db.hello().isWritablePrimary) quit(1)'
echo 'Disposable MongoDB replica set is writable.'
