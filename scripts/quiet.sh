#!/bin/sh
# Steady successful traffic. Both SLIs should stay near their objectives.
set -eu
url="${APP_URL:-http://127.0.0.1:8080}/ok"
while true; do
  curl -fsS -o /dev/null "$url" || true
  sleep 0.2
done
