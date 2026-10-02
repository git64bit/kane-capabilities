import http.client
import importlib.util
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SERVICE_PATH = ROOT / "services" / "publication" / "publication_service.py"
SPEC = importlib.util.spec_from_file_location(
    "civic_publication_service_test",
    SERVICE_PATH,
)
publication_service = importlib.util.module_from_spec(SPEC)
assert SPEC is not None and SPEC.loader is not None
SPEC.loader.exec_module(publication_service)


class PublicationServiceAuthenticationTests(unittest.TestCase):
    def start_server(self, bearer_token):
        class TestHandler(publication_service.Handler):
            pass

        TestHandler.bearer_token = bearer_token
        server = ThreadingHTTPServer(("127.0.0.1", 0), TestHandler)
        thread = threading.Thread(
            target=server.serve_forever,
            daemon=True,
        )
        thread.start()
        return server, thread

    def request(self, server, authorization=None):
        host, port = server.server_address
        conn = http.client.HTTPConnection(host, port, timeout=5)
        body = b"{}"
        headers = {
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
        }
        if authorization is not None:
            headers["Authorization"] = authorization
        conn.request("POST", "/v1/publications", body=body, headers=headers)
        response = conn.getresponse()
        payload = json.loads(response.read().decode("utf-8"))
        status = response.status
        conn.close()
        return status, payload

    def stop_server(self, server, thread):
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)

    def test_missing_credential_is_rejected_before_request_validation(self):
        token = b"S" * 48
        server, thread = self.start_server(token)
        try:
            status, payload = self.request(server)
        finally:
            self.stop_server(server, thread)

        self.assertEqual(status, 401)
        self.assertEqual(payload["failure_class"], "invalid-request")
        self.assertIn("authentication failed", payload["message"])

    def test_wrong_credential_is_rejected_before_request_validation(self):
        token = b"S" * 48
        server, thread = self.start_server(token)
        try:
            status, payload = self.request(
                server,
                "Bearer " + ("W" * 48),
            )
        finally:
            self.stop_server(server, thread)

        self.assertEqual(status, 401)
        self.assertEqual(payload["failure_class"], "invalid-request")

    def test_valid_credential_reaches_request_validation(self):
        token_text = "S" * 48
        server, thread = self.start_server(token_text.encode("utf-8"))
        try:
            status, payload = self.request(
                server,
                f"Bearer {token_text}",
            )
        finally:
            self.stop_server(server, thread)

        self.assertEqual(status, 400)
        self.assertEqual(payload["failure_class"], "invalid-request")
        self.assertNotIn("authentication failed", payload["message"])

    def test_unconfigured_service_authentication_fails_closed(self):
        server, thread = self.start_server(None)
        try:
            status, payload = self.request(
                server,
                "Bearer " + ("S" * 48),
            )
        finally:
            self.stop_server(server, thread)

        self.assertEqual(status, 503)
        self.assertEqual(payload["failure_class"], "service-unavailable")
        self.assertIn("not configured", payload["message"])


if __name__ == "__main__":
    unittest.main()
