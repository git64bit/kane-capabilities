import base64
import hashlib
import tempfile
import unittest
from pathlib import Path

from civic_orchestrator.publication import (
    PublicationServiceFailure,
    PublicationServiceProtocolError,
    PublicationServiceUnavailable,
)
from civic_orchestrator.runtime import CivicOrchestrator, RuntimePaths


ROOT = Path(__file__).resolve().parents[1]


class FakePublicationClient:
    def __init__(self, mode="success"):
        self.mode = mode
        self.calls = []

    def publish(self, workflow_id, artifact):
        self.calls.append((workflow_id, artifact))
        if self.mode == "service-failure":
            raise PublicationServiceFailure(
                status_code=503,
                failure_class="service-unavailable",
                message="publication backend unavailable",
                retryable=True,
                response={
                    "contract_version": 1,
                    "workflow_id": workflow_id,
                    "operation": "publication.publish",
                    "failure_class": "service-unavailable",
                    "message": "publication backend unavailable",
                    "retryable": True,
                },
            )
        if self.mode == "transport-failure":
            raise PublicationServiceUnavailable("connection refused")
        if self.mode == "protocol-failure":
            raise PublicationServiceProtocolError("invalid service result")
        if self.mode == "unexpected-failure":
            raise RuntimeError("unexpected adapter defect")

        return {
            "contract_version": 1,
            "workflow_id": workflow_id,
            "operation": "publication.publish",
            "sha256": artifact["sha256"],
            "size_bytes": artifact["size_bytes"],
            "cid": "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylzgf4p5l2h4q",
            "pinned": True,
            "verified": True,
        }


class PublicationRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.client = FakePublicationClient()
        self.runtime = CivicOrchestrator(
            RuntimePaths(
                repo_root=ROOT,
                state_db=Path(self.tmp.name) / "state.sqlite3",
            ),
            publication_client=self.client,
        )
        self.runtime.registry.operations["publication.publish"][
            "implementation"
        ] = "available"
        self.payload = b"civic publication\n"
        self.artifact = {
            "media_type": "text/plain",
            "size_bytes": len(self.payload),
            "sha256": hashlib.sha256(self.payload).hexdigest(),
            "encoding": "base64",
            "content": base64.b64encode(self.payload).decode("ascii"),
        }

    def tearDown(self):
        self.tmp.cleanup()

    def request(self):
        return {
            "contract_version": 1,
            "request_id": "req:publication-runtime-001",
            "operation": "publication.publish",
            "caller": {
                "subject": "participant:test",
                "authority": "test-authority",
                "authenticated_by": "test-authenticator",
            },
            "client": {
                "id": "test-client",
                "kind": "test",
            },
            "submitted_at": "2026-10-01T17:00:00Z",
            "idempotency_key": "idem:publication-runtime-001",
            "input": {
                "artifact": self.artifact,
                "label": "test publication",
            },
        }

    def test_publication_success_completes_existing_workflow_model(self):
        status, result = self.runtime.submit(self.request())

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "completed")
        self.assertTrue(result["side_effects"])
        self.assertEqual(result["result"]["sha256"], self.artifact["sha256"])
        self.assertEqual(
            result["result"]["cid"],
            "bafybeigdyrzt5sfp7udm7hu76uh7y26nf3efuylzgf4p5l2h4q",
        )
        self.assertTrue(result["result"]["pinned"])
        self.assertTrue(result["result"]["verified"])
        self.assertEqual(len(self.client.calls), 1)
        self.assertEqual(self.client.calls[0][1], self.artifact)

        evidence_status, evidence = self.runtime.workflow_evidence(
            result["workflow_id"]
        )
        self.assertEqual(evidence_status, 200)
        self.assertEqual(evidence["workflow"]["state"], "completed")
        self.assertTrue(evidence["workflow"]["side_effects"])
        self.assertTrue(evidence["side_effects"])
        self.assertEqual(
            [event["event_type"] for event in evidence["audit_events"]],
            [
                "civic.authorization.allowed",
                "civic.operation.accepted",
                "civic.service.selected",
                "civic.operation.completed",
            ],
        )
        self.assertEqual(
            evidence["authorization_decisions"][0]["policy"],
            "publication-policy-v1",
        )
        self.assertEqual(evidence["receipts"][0]["outcome"], "completed")
        self.assertTrue(evidence["receipts"][0]["side_effects"])
        self.assertEqual(
            evidence["receipts"][0]["evidence"]["cid"],
            result["result"]["cid"],
        )

    def test_publication_specific_input_is_validated_before_backend_call(self):
        request = self.request()
        request["input"]["artifact"]["encoding"] = "hex"

        status, result = self.runtime.submit(request)

        self.assertEqual(status, 400)
        self.assertEqual(result["failure_class"], "invalid-contract")
        self.assertFalse(result["side_effects"])
        self.assertEqual(self.client.calls, [])

    def test_bounded_service_failure_becomes_failed_workflow(self):
        self.client.mode = "service-failure"

        status, result = self.runtime.submit(self.request())

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "failed")
        self.assertFalse(result["side_effects"])
        self.assertEqual(
            result["result"]["failure_class"],
            "service-unavailable",
        )
        self.assertTrue(result["result"]["retryable"])

        _, evidence = self.runtime.workflow_evidence(result["workflow_id"])
        self.assertEqual(evidence["workflow"]["state"], "failed")
        self.assertEqual(
            evidence["audit_events"][-1]["event_type"],
            "civic.operation.failed",
        )
        self.assertEqual(evidence["receipts"][0]["outcome"], "failed")

    def test_verification_failure_is_conservatively_side_effecting(self):
        def fail_after_publication(workflow_id, artifact):
            raise PublicationServiceFailure(
                status_code=500,
                failure_class="verification-failed",
                message="read-back verification failed",
                retryable=False,
                response={
                    "contract_version": 1,
                    "workflow_id": workflow_id,
                    "operation": "publication.publish",
                    "failure_class": "verification-failed",
                    "message": "read-back verification failed",
                    "retryable": False,
                },
            )

        self.client.publish = fail_after_publication

        status, result = self.runtime.submit(self.request())

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["side_effects"])
        self.assertEqual(
            result["result"]["failure_class"],
            "verification-failed",
        )

    def test_transport_failure_becomes_backend_unavailable_workflow(self):
        self.client.mode = "transport-failure"

        status, result = self.runtime.submit(self.request())

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["side_effects"])
        self.assertEqual(
            result["result"]["failure_class"],
            "backend-unavailable",
        )
        self.assertTrue(result["result"]["retryable"])

    def test_protocol_failure_becomes_internal_failed_workflow(self):
        self.client.mode = "protocol-failure"

        status, result = self.runtime.submit(self.request())

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["side_effects"])
        self.assertEqual(result["result"]["failure_class"], "internal")
        self.assertFalse(result["result"]["retryable"])

    def test_unexpected_adapter_failure_is_persisted_as_failed(self):
        self.client.mode = "unexpected-failure"

        status, result = self.runtime.submit(self.request())

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "failed")
        self.assertTrue(result["side_effects"])
        self.assertEqual(result["result"]["failure_class"], "internal")
        self.assertIn(
            "unexpected publication adapter failure",
            result["result"]["message"],
        )

        _, evidence = self.runtime.workflow_evidence(result["workflow_id"])
        self.assertEqual(evidence["workflow"]["state"], "failed")
        self.assertEqual(evidence["receipts"][0]["outcome"], "failed")

    def test_publication_replay_does_not_call_backend_twice(self):
        request = self.request()
        status, first = self.runtime.submit(request)
        self.assertEqual(status, 200)

        retry = self.request()
        retry["request_id"] = "req:publication-runtime-002"
        retry["submitted_at"] = "2026-10-01T17:01:00Z"
        status, second = self.runtime.submit(retry)

        self.assertEqual(status, 200)
        self.assertEqual(second["workflow_id"], first["workflow_id"])
        self.assertEqual(second["receipt_id"], first["receipt_id"])
        self.assertTrue(second["result"]["replayed"])
        self.assertEqual(
            second["result"]["original_request_id"],
            first["request_id"],
        )
        self.assertEqual(len(self.client.calls), 1)

    def test_other_operations_remain_on_stub_path(self):
        request = self.request()
        request["request_id"] = "req:repository-stub"
        request["operation"] = "repository.fetch_exact"
        request["idempotency_key"] = "idem:repository-stub"
        request["input"] = {}

        status, result = self.runtime.submit(request)

        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "not-implemented")
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["result"]["implementation"], "stub")
        self.assertEqual(len(self.client.calls), 0)

    def test_available_publication_without_client_fails_before_workflow(self):
        runtime = CivicOrchestrator(
            RuntimePaths(
                repo_root=ROOT,
                state_db=Path(self.tmp.name) / "no-client.sqlite3",
            )
        )
        runtime.registry.operations["publication.publish"][
            "implementation"
        ] = "available"

        status, result = runtime.submit(self.request())

        self.assertEqual(status, 500)
        self.assertEqual(result["failure_class"], "backend-unavailable")
        self.assertFalse(result["side_effects"])

        with runtime.state._connect() as conn:
            count = conn.execute(
                "SELECT COUNT(*) FROM workflows"
            ).fetchone()[0]
        self.assertEqual(count, 0)


if __name__ == "__main__":
    unittest.main()
