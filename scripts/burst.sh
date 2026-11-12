#!/bin/sh
# Thirty seconds of 500s. Availability burn on the 5m window should rise.
# Latency does not move: a 5xx is not a latency sample.
# The fast page also requires the 1h window, so this burst does not page
# on a stand that already has a healthy hour behind it.
set -eu
url="${APP_URL:-http://127.0.0.1:8080}/fail"
end=$(( $(date +%s) + 30 ))
while [ "$(date +%s)" -lt "$end" ]; do
  curl -sS -o /dev/null "$url" || true
  sleep 0.05
done
