"""Sample HTTP service that exposes request and latency metrics.

The paths exist so a local stand can move one SLI without moving the other.
/metrics is not counted: scraping must not change the SLI.

handler is a closed set (ok, fail, slow, other). A label per URL or per user
would make the SLI unusable, so those never become labels.
"""

import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from prometheus_client import Counter, Histogram, generate_latest

REQUESTS = Counter(
    "http_requests_total",
    "HTTP requests, excluding scrapes of /metrics.",
    ["handler", "status"],
)
# 0.3 is the latency objective. The bucket must exist or the SLI cannot see it.
LATENCY = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds, excluding scrapes of /metrics.",
    ["handler", "status"],
    buckets=(0.05, 0.1, 0.2, 0.3, 0.5, 1, 2, 5),
)

SLOW_SECONDS = 0.4


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        path = self.path.split("?", 1)[0]
        if path == "/metrics":
            self._write(200, generate_latest(), "text/plain; version=0.0.4")
            return

        started = time.perf_counter()
        if path == "/fail":
            handler, status, body = "fail", 500, b"fail\n"
        elif path == "/slow":
            time.sleep(SLOW_SECONDS)
            handler, status, body = "slow", 200, b"slow\n"
        elif path in ("/", "/ok"):
            handler, status, body = "ok", 200, b"ok\n"
        else:
            handler, status, body = "other", 404, b"not found\n"

        elapsed = time.perf_counter() - started
        REQUESTS.labels(handler=handler, status=str(status)).inc()
        LATENCY.labels(handler=handler, status=str(status)).observe(elapsed)
        self._write(status, body, "text/plain; charset=utf-8")

    def _write(self, status, body, content_type):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        return


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
