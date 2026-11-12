#!/bin/sh
# Thirty seconds of 404s. They are outside both SLIs.
# Run this next to quiet.sh: availability should stay put.
# Run it alone: the SLI goes blank. It must not show 100%.
set -eu
url="${APP_URL:-http://127.0.0.1:8080}/missing"
end=$(( $(date +%s) + 30 ))
while [ "$(date +%s)" -lt "$end" ]; do
  curl -sS -o /dev/null "$url" || true
  sleep 0.05
done
