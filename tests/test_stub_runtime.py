import json
import tempfile
import threading
import unittest
from pathlib import Path

from civic_orchestrator.runtime import CivicOrchestrator, RuntimePaths


ROOT = Path(__file__).resolve().parents[1]


class StubRuntimeTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.runtime = CivicOrchestrator(
            RuntimePaths(
                repo_root=ROOT,
                state_db=Path(self.tmp.name) / "state.sqlite3",
            )
        )

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, operation="publication.publish"):
        return {
            "contract_version": 1,
            "request_id": "req:test-001",
            "operation": operation,
            "caller": {
                "subject": "participant:test",
                "authority": "test-authority"
            },
            "interface": "test",
            "submitted_at": "2026-10-01T06:00:00Z",
            "input": {}
        }

    def test_known_operation_is_stubbed_without_side_effects(self):
        status, result = self.runtime.submit(self.request())
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "not-implemented")
        self.assertFalse(result["side_effects"])
        self.assertTrue(result["workflow_id"].startswith("wf:"))
        self.assertTrue(result["receipt_id"].startswith("rcpt:"))

    def test_unknown_operation_fails_closed(self):
        status, result = self.runtime.submit(self.request("publication.unknown"))
        self.assertEqual(status, 400)
        self.assertEqual(result["failure_class"], "unknown-operation")
        self.assertFalse(result["side_effects"])

    def test_prohibited_operation_fails_closed(self):
        request = self.request()
        request["operation"] = "shell.exec"
        status, result = self.runtime.submit(request)
        self.assertEqual(status, 400)
        self.assertEqual(result["failure_class"], "invalid-contract")
        self.assertFalse(result["side_effects"])

    def test_invalid_contract_fails_closed(self):
        request = self.request()
        del request["caller"]
        status, result = self.runtime.submit(request)
        self.assertEqual(status, 400)
        self.assertEqual(result["failure_class"], "invalid-contract")
        self.assertFalse(result["side_effects"])

    def test_capability_advertisement_contains_stub(self):
        caps = self.runtime.capabilities()
        self.assertTrue(any(
            item["operation"] == "publication.publish" and item["implementation"] == "stub"
            for item in caps["capabilities"]
        ))

    def test_incident_operations_are_bounded_stubs(self):
        caps = self.runtime.capabilities()
        operations = {item["operation"] for item in caps["capabilities"]}
        self.assertIn("incident.report", operations)
        self.assertIn("incident.get", operations)
        self.assertIn("incident.acknowledge", operations)
        self.assertIn("incident.resolve", operations)

        status, result = self.runtime.submit(self.request("incident.report"))
        self.assertEqual(status, 200)
        self.assertEqual(result["status"], "not-implemented")
        self.assertFalse(result["side_effects"])
        self.assertEqual(
            result["result"]["service_capability"],
            "incident.report",
        )

    def test_workflow_evidence_is_read_only_and_schema_valid(self):
        status, result = self.runtime.submit(self.request())
        self.assertEqual(status, 200)

        evidence_status, evidence = self.runtime.workflow_evidence(result["workflow_id"])
        self.assertEqual(evidence_status, 200)
        self.assertEqual(evidence["workflow"]["workflow_id"], result["workflow_id"])
        self.assertEqual(evidence["workflow"]["state"], "not-implemented")
        self.assertFalse(evidence["side_effects"])
        self.assertEqual(len(evidence["authorization_decisions"]), 1)
        decision = evidence["authorization_decisions"][0]
        self.assertEqual(decision["decision"], "allow")
        self.assertEqual(decision["policy"], "stub-policy")
        self.assertEqual(len(evidence["audit_events"]), 3)
        self.assertEqual(len(evidence["receipts"]), 1)
        self.assertEqual(evidence["receipts"][0]["receipt_id"], result["receipt_id"])

    def test_authorization_decision_is_recorded_before_stub_execution(self):
        status, result = self.runtime.submit(self.request())
        self.assertEqual(status, 200)

        evidence_status, evidence = self.runtime.workflow_evidence(result["workflow_id"])
        self.assertEqual(evidence_status, 200)
        self.assertEqual(len(evidence["authorization_decisions"]), 1)
        self.assertEqual(
            evidence["audit_events"][0]["event_type"],
            "civic.authorization.allowed",
        )
        self.assertEqual(
            evidence["authorization_decisions"][0]["request_id"],
            result["request_id"],
        )
        self.assertFalse(evidence["side_effects"])

    def test_missing_workflow_evidence_fails_closed(self):
        status, result = self.runtime.workflow_evidence("wf:does-not-exist")
        self.assertEqual(status, 404)
        self.assertEqual(result["error"], "workflow-not-found")
        self.assertFalse(result["side_effects"])

    def test_threaded_submit_uses_safe_sqlite_connections(self):
        results = []
        errors = []

        def worker(index):
            try:
                request = self.request()
                request["request_id"] = f"req:thread-{index}"
                results.append(self.runtime.submit(request))
            except Exception as exc:
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(i,)) for i in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()

        self.assertEqual(errors, [])
        self.assertEqual(len(results), 4)
        for status, result in results:
            self.assertEqual(status, 200)
            self.assertEqual(result["status"], "not-implemented")
            self.assertFalse(result["side_effects"])


if __name__ == "__main__":
    unittest.main()
