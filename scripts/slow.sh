#!/bin/sh
# Thirty seconds of slow 200s (the server sleeps 400ms). Latency burn should
# rise. Availability should not: every response is a success.
set -eu
url="${APP_URL:-http://127.0.0.1:8080}/slow"
end=$(( $(date +%s) + 30 ))
while [ "$(date +%s)" -lt "$end" ]; do
  curl -sS -o /dev/null "$url" || true
  sleep 0.05
done
