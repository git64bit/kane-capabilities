#!/usr/bin/env python3
from __future__ import annotations

import base64
import binascii
import hashlib
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any


HOST = "192.168.1.106"
PORT = 8046
MAX_ARTIFACT_BYTES = 262_144


def json_bytes(value: dict[str, Any]) -> bytes:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")


def failure(
    workflow_id: str,
    failure_class: str,
    message: str,
    retryable: bool,
) -> dict[str, Any]:
    return {
        "contract_version": 1,
        "workflow_id": workflow_id,
        "operation": "publication.publish",
        "failure_class": failure_class,
        "message": message[:1000] or "publication request failed",
        "retryable": bool(retryable),
    }


def validate_request(value: Any) -> tuple[str, bytes, str, int]:
    if not isinstance(value, dict):
        raise ValueError("request must be an object")

    allowed = {"contract_version", "workflow_id", "operation", "artifact"}
    if set(value) != allowed:
        raise ValueError("request fields do not match publication-service contract")

    if value.get("contract_version") != 1:
        raise ValueError("contract_version must be 1")
    if value.get("operation") != "publication.publish":
        raise ValueError("operation must be publication.publish")

    workflow_id = value.get("workflow_id")
    if not isinstance(workflow_id, str) or not workflow_id or len(workflow_id) > 160:
        raise ValueError("workflow_id is invalid")

    artifact = value.get("artifact")
    if not isinstance(artifact, dict):
        raise ValueError("artifact must be an object")

    required = {"media_type", "size_bytes", "sha256", "encoding", "content"}
    if set(artifact) != required:
        raise ValueError("artifact fields do not match publication-artifact contract")

    media_type = artifact.get("media_type")
    if not isinstance(media_type, str) or "/" not in media_type or len(media_type) > 200:
        raise ValueError("media_type is invalid")

    size_bytes = artifact.get("size_bytes")
    if (
        not isinstance(size_bytes, int)
        or isinstance(size_bytes, bool)
        or size_bytes < 0
        or size_bytes > MAX_ARTIFACT_BYTES
    ):
        raise ValueError("size_bytes is outside the supported range")

    sha256 = artifact.get("sha256")
    if (
        not isinstance(sha256, str)
        or len(sha256) != 64
        or any(c not in "0123456789abcdef" for c in sha256)
    ):
        raise ValueError("sha256 must be 64 lowercase hexadecimal characters")

    if artifact.get("encoding") != "base64":
        raise ValueError("encoding must be base64")

    content = artifact.get("content")
    if not isinstance(content, str):
        raise ValueError("content must be a base64 string")

    try:
        decoded = base64.b64decode(content.encode("ascii"), validate=True)
    except (UnicodeEncodeError, binascii.Error) as exc:
        raise ValueError("content is not strict base64") from exc

    if len(decoded) != size_bytes:
        raise RuntimeError("decoded byte count does not match size_bytes")

    actual_sha256 = hashlib.sha256(decoded).hexdigest()
    if actual_sha256 != sha256:
        raise RuntimeError("decoded bytes do not match sha256")

    return workflow_id, decoded, sha256, size_bytes


class Handler(BaseHTTPRequestHandler):
    server_version = "civic-publication/0"

    def log_message(self, fmt: str, *args: Any) -> None:
        super().log_message(fmt, *args)

    def send_json(self, status: int, value: dict[str, Any]) -> None:
        body = json_bytes(value)
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        if self.path != "/healthz":
            self.send_json(
                404,
                failure(
                    "wf:invalid",
                    "invalid-request",
                    "endpoint not found",
                    False,
                ),
            )
            return
        self.send_json(
            200,
            {
                "status": "ok",
                "service": "civic-publication",
                "phase": "validation-only",
                "kubo_enabled": False,
                "swarm_enabled": False,
            },
        )

    def do_POST(self) -> None:
        if self.path != "/v1/publications":
            self.send_json(
                404,
                failure(
                    "wf:invalid",
                    "invalid-request",
                    "endpoint not found",
                    False,
                ),
            )
            return

        workflow_id = "wf:invalid"
        content_length = self.headers.get("Content-Length")
        try:
            length = int(content_length or "")
        except ValueError:
            self.send_json(
                400,
                failure(workflow_id, "invalid-request", "invalid Content-Length", False),
            )
            return

        # Single-block artifact plus base64/JSON envelope stays below this bound.
        if length < 0 or length > 1_500_000:
            self.send_json(
                413,
                failure(workflow_id, "invalid-request", "request body too large", False),
            )
            return

        try:
            raw = self.rfile.read(length)
            value = json.loads(raw.decode("utf-8"))
            if isinstance(value, dict) and isinstance(value.get("workflow_id"), str):
                workflow_id = value["workflow_id"]
            workflow_id, _decoded, _sha256, _size_bytes = validate_request(value)
        except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
            self.send_json(
                400,
                failure(workflow_id, "invalid-request", str(exc), False),
            )
            return
        except RuntimeError as exc:
            self.send_json(
                422,
                failure(workflow_id, "integrity-mismatch", str(exc), False),
            )
            return

        self.send_json(
            503,
            failure(
                workflow_id,
                "service-unavailable",
                "publication bytes validated; Kubo publication is not enabled yet",
                True,
            ),
        )


def main() -> None:
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
