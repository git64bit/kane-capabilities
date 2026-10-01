from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from .runtime import CivicOrchestrator, RuntimePaths


class Handler(BaseHTTPRequestHandler):
    runtime: CivicOrchestrator

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/v1/capabilities":
            self._send_json(200, self.runtime.capabilities())
            return
        if path == "/healthz":
            self._send_json(200, {"status": "ok", "phase": 1, "side_effects": False})
            return
        self._send_json(404, {"error": "not found"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/v1/operations":
            self._send_json(404, {"error": "not found"})
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._send_json(400, {"error": "invalid content length"})
            return

        if length <= 0 or length > 1024 * 1024:
            self._send_json(400, {"error": "request body size rejected"})
            return

        try:
            body = self.rfile.read(length)
            request = json.loads(body)
            if not isinstance(request, dict):
                raise ValueError("request body must be a JSON object")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self._send_json(400, {"error": str(exc), "side_effects": False})
            return

        status, payload = self.runtime.submit(request)
        self._send_json(status, payload)

    def log_message(self, format: str, *args) -> None:
        return


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--state-db", required=True)
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8045)
    args = parser.parse_args()

    runtime = CivicOrchestrator(
        RuntimePaths(repo_root=Path(args.repo_root), state_db=Path(args.state_db))
    )
    Handler.runtime = runtime
    server = ThreadingHTTPServer((args.listen, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
