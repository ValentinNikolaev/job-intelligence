#!/usr/bin/env bash
set -euo pipefail

# Atlas may need time to apply a new runner access entry.
for attempt in $(seq 1 12); do
  if python run.py storage doctor --ci; then
    exit 0
  fi
  if [ "$attempt" -lt 12 ]; then
    sleep 5
  fi
done
echo 'Shared storage remained unavailable after the network propagation window.' >&2
exit 1
