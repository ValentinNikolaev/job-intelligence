#!/usr/bin/env bash
set +e

label="$1"
failure_mode="$2"
shift 2

started_ms="$(date +%s%3N)"
echo "## ${label}" >> "$GITHUB_STEP_SUMMARY"
echo '```text' >> "$GITHUB_STEP_SUMMARY"
echo "+ $*" >> "$GITHUB_STEP_SUMMARY"
"$@" 2>&1 | tee -a "$GITHUB_STEP_SUMMARY"
status=${PIPESTATUS[0]}
finished_ms="$(date +%s%3N)"
elapsed_ms=$((finished_ms - started_ms))
echo '```' >> "$GITHUB_STEP_SUMMARY"
echo "Exit code: ${status}" >> "$GITHUB_STEP_SUMMARY"
printf 'Estimated time: %d ms (%.3f s)\n' "$elapsed_ms" "$(awk "BEGIN { printf \"%.3f\", ${elapsed_ms}/1000 }")" >> "$GITHUB_STEP_SUMMARY"
echo >> "$GITHUB_STEP_SUMMARY"

if [ "$status" -ne 0 ] && [ "$failure_mode" = "soft" ]; then
  echo "::warning title=${label} failed::Continuing because collection sources can have transient network/API failures; deterministic checks still gate commits."
  exit 0
fi

exit "$status"
