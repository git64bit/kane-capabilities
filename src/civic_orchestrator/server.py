from __future__ import annotations

import argparse
import hmac
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

from .publication import PublicationServiceClient
from .runtime import (
    AuthenticatedAdapterBinding,
    CivicOrchestrator,
    RuntimePaths,
)


MAX_OPERATION_REQUEST_BYTES = 1_500_000


class AdapterCredentialError(ValueError):
    pass


class BearerAdapterAuthenticator:
    """Resolve an HTTP bearer credential to one fixed adapter binding."""

    def __init__(
        self,
        credentials: list[
            tuple[str, AuthenticatedAdapterBinding]
        ],
    ) -> None:
        if not credentials:
            raise ValueError("at least one adapter credential is required")
        normalized: list[tuple[bytes, AuthenticatedAdapterBinding]] = []
        for token, binding in credentials:
            if not isinstance(token, str) or not token:
                raise ValueError("adapter bearer credential is invalid")
            normalized.append((token.encode("utf-8"), binding))
        self._credentials = tuple(normalized)

    def authenticate(
        self,
        authorization_header: str | None,
    ) -> AuthenticatedAdapterBinding:
        if not isinstance(authorization_header, str):
            raise AdapterCredentialError("adapter credential is required")
        scheme, sep, token = authorization_header.partition(" ")
        if sep != " " or scheme != "Bearer" or not token:
            raise AdapterCredentialError("adapter credential is invalid")

        token_bytes = token.encode("utf-8")
        for expected, binding in self._credentials:
            if hmac.compare_digest(token_bytes, expected):
                return binding

        raise AdapterCredentialError("adapter credential is invalid")


class Handler(BaseHTTPRequestHandler):
    runtime: CivicOrchestrator
    adapter_authenticator: BearerAdapterAuthenticator | None = None

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _operation_failure(
        self,
        status: int,
        failure_class: str,
        message: str,
        request_id=None,
        operation=None,
        retryable: bool = False,
    ) -> None:
        self.runtime.state.record_request_diagnostic(
            f"http-{failure_class}",
            request_id=request_id,
            operation=operation,
            detail=message,
        )
        self._send_json(
            status,
            self.runtime.failure(
                request_id=request_id,
                operation=operation,
                failure_class=failure_class,
                message=message,
                retryable=retryable,
            ),
        )

    def do_GET(self) -> None:
        path = urlparse(self.path).path

        if path == "/v1/capabilities":
            self._send_json(200, self.runtime.capabilities())
            return

        if path == "/healthz":
            self._send_json(200, self.runtime.health())
            return

        if path.startswith("/v1/workflows/"):
            workflow_id = unquote(path[len("/v1/workflows/"):])
            if not workflow_id:
                self._send_json(
                    404,
                    {
                        "contract_version": 1,
                        "workflow_id": "invalid:workflow",
                        "error": "workflow-not-found",
                        "side_effects": False,
                    },
                )
                return
            try:
                status, payload = self.runtime.workflow_evidence(workflow_id)
                self._send_json(status, payload)
            except Exception:
                self._operation_failure(
                    500,
                    "internal",
                    "internal workflow evidence error",
                    operation="audit.get_workflow",
                )
            return

        self._operation_failure(
            404,
            "invalid-contract",
            "endpoint not found",
        )

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/v1/operations":
            self._operation_failure(
                404,
                "invalid-contract",
                "endpoint not found",
            )
            return

        if self.adapter_authenticator is None:
            self._operation_failure(
                503,
                "backend-unavailable",
                "authenticated adapter ingress is not configured",
                retryable=False,
            )
            return

        try:
            adapter_binding = self.adapter_authenticator.authenticate(
                self.headers.get("Authorization")
            )
        except AdapterCredentialError as exc:
            self._operation_failure(
                401,
                "unauthorized",
                str(exc),
                retryable=False,
            )
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            self._operation_failure(
                400,
                "invalid-contract",
                "invalid content length",
            )
            return

        if length <= 0 or length > MAX_OPERATION_REQUEST_BYTES:
            self._operation_failure(
                400,
                "invalid-contract",
                "request body size rejected",
            )
            return

        try:
            body = self.rfile.read(length)
            request = json.loads(body)
            if not isinstance(request, dict):
                raise ValueError("request body must be a JSON object")
        except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
            self._operation_failure(
                400,
                "invalid-contract",
                str(exc),
            )
            return

        try:
            status, payload = self.runtime.submit_authenticated(
                request,
                adapter_binding,
            )
        except Exception:
            self._operation_failure(
                500,
                "internal",
                "internal request processing error",
                request_id=request.get("request_id"),
                operation=request.get("operation"),
            )
            return

        self._send_json(status, payload)

    def log_message(self, format: str, *args) -> None:
        return



def build_runtime(
    repo_root: Path,
    state_db: Path,
    publication_base_url: str | None = None,
) -> CivicOrchestrator:
    runtime = CivicOrchestrator(
        RuntimePaths(
            repo_root=repo_root,
            state_db=state_db,
        )
    )
    if publication_base_url:
        runtime.publication_client = PublicationServiceClient(
            publication_base_url,
            runtime.contracts.validate,
        )
    return runtime


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True)
    parser.add_argument("--state-db", required=True)
    parser.add_argument("--listen", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8045)
    parser.add_argument("--publication-base-url")
    args = parser.parse_args()

    runtime = build_runtime(
        repo_root=Path(args.repo_root),
        state_db=Path(args.state_db),
        publication_base_url=args.publication_base_url,
    )
    Handler.runtime = runtime
    server = ThreadingHTTPServer((args.listen, args.port), Handler)
    server.serve_forever()


if __name__ == "__main__":
    main()
