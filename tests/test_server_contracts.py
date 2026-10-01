import http.client
import json
import tempfile
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path

from civic_orchestrator.runtime import CivicOrchestrator, RuntimePaths
from civic_orchestrator.server import Handler


ROOT = Path(__file__).resolve().parents[1]


class ServerContractTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime = CivicOrchestrator(
            RuntimePaths(
                repo_root=ROOT,
                state_db=Path(self.tmp.name) / "state.sqlite3",
            )
        )
        Handler.runtime = self.runtime
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = threading.Thread(
            target=self.server.serve_forever,
            daemon=True,
        )
        self.thread.start()
        self.host, self.port = self.server.server_address

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)
        self.tmp.cleanup()

    def request(self, method, path, body=None, headers=None):
        conn = http.client.HTTPConnection(
            self.host,
            self.port,
            timeout=5,
        )
        conn.request(method, path, body=body, headers=headers or {})
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        status = response.status
        conn.close()
        return status, payload

    def test_bad_json_returns_failure_envelope(self):
        status, payload = self.request(
            "POST",
            "/v1/operations",
            body="{not-json",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "9",
            },
        )
        self.assertEqual(status, 400)
        self.runtime.contracts.validate(
            "failure-envelope-v1.schema.json",
            payload,
        )
        self.assertEqual(payload["failure_class"], "invalid-contract")

    def test_wrong_post_path_returns_failure_envelope(self):
        status, payload = self.request(
            "POST",
            "/v1/not-an-operation-endpoint",
            body="{}",
            headers={
                "Content-Type": "application/json",
                "Content-Length": "2",
            },
        )
        self.assertEqual(status, 404)
        self.runtime.contracts.validate(
            "failure-envelope-v1.schema.json",
            payload,
        )
        self.assertFalse(payload["side_effects"])

    def test_unexpected_submit_exception_returns_internal_failure(self):
        original = self.runtime.submit

        def explode(_request):
            raise RuntimeError("synthetic server test")

        self.runtime.submit = explode
        try:
            body = json.dumps({
                "contract_version": 1,
                "request_id": "req:server-exception",
                "operation": "publication.publish",
                "caller": {
                    "subject": "participant:test",
                    "authenticated_by": "test-auth",
                },
                "client": {
                    "id": "test-client",
                    "kind": "test",
                },
                "submitted_at": "2026-10-01T08:00:00Z",
                "input": {},
            })
            status, payload = self.request(
                "POST",
                "/v1/operations",
                body=body,
                headers={
                    "Content-Type": "application/json",
                    "Content-Length": str(len(body.encode("utf-8"))),
                },
            )
        finally:
            self.runtime.submit = original

        self.assertEqual(status, 500)
        self.runtime.contracts.validate(
            "failure-envelope-v1.schema.json",
            payload,
        )
        self.assertEqual(payload["failure_class"], "internal")
        self.assertFalse(payload["side_effects"])


if __name__ == "__main__":
    unittest.main()
