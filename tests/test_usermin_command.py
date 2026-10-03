import socket
import tempfile
import threading
import unittest
from pathlib import Path

from civic_orchestrator.custom_commands import (
    CustomCommandRegistry,
    LocalCustomCommandAdapter,
)
from civic_orchestrator.usermin_adapter import ParticipantIdentity
from civic_orchestrator.usermin_broker import handle_command_connection
from civic_orchestrator.usermin_command import (
    invoke_water_ants,
    send_command_to_broker,
)


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "contracts" / "custom-command-registry-v1.yaml"
SCHEMA_PATH = ROOT / "schemas" / "custom-command-registry-v1.schema.json"
HELP_PATH = ROOT / "contracts" / "custom-command-help-v1.yaml"
HELP_SCHEMA_PATH = ROOT / "schemas" / "custom-command-help-v1.schema.json"


class StaticParticipantRegistry:
    def resolve(self, uid):
        return ParticipantIdentity(
            uid=uid,
            username="participant1",
            participant_id="participant:test-stable",
        )


class StaticAccessPolicy:
    def require_invoke(self, participant_id, codename):
        return {"codename": codename, "discover": True, "invoke": True}


class UserminCommandHelperTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.registry = CustomCommandRegistry.load(
            REGISTRY_PATH,
            SCHEMA_PATH,
            HELP_PATH,
            HELP_SCHEMA_PATH,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def run_broker_once(self, socket_path):
        listener = socket.socket(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
        )
        listener.bind(str(socket_path))
        listener.listen(1)

        adapter = LocalCustomCommandAdapter(
            StaticParticipantRegistry(),
            self.registry,
            StaticAccessPolicy(),
        )

        def serve_once():
            conn, _ = listener.accept()
            with conn:
                handle_command_connection(conn, adapter)
            listener.close()

        thread = threading.Thread(target=serve_once)
        thread.start()
        return thread

    def test_generic_helper_gets_water_ants_stub_result(self):
        socket_path = self.root / "command.sock"
        thread = self.run_broker_once(socket_path)
        try:
            result = send_command_to_broker(
                socket_path,
                codename="water-ants",
                arguments={},
                payload=b"participant bytes",
            )
        finally:
            thread.join(timeout=2)

        self.assertEqual(result["status"], "stub")
        self.assertEqual(result["command"], "water-ants")
        self.assertFalse(result["remote_dispatch"])
        self.assertFalse(result["side_effects"])

    def test_water_ants_requires_explicit_confirmation(self):
        path = self.root / "upload.pdf"
        path.write_bytes(b"%PDF-test")

        with self.assertRaisesRegex(
            Exception,
            "explicit participant confirmation",
        ):
            invoke_water_ants(
                self.registry,
                path,
                self.root / "unused.sock",
                confirmed=False,
            )

    def test_water_ants_reads_file_then_uses_generic_frame(self):
        path = self.root / "upload.pdf"
        payload = b"%PDF-participant-test"
        path.write_bytes(payload)

        socket_path = self.root / "command.sock"
        thread = self.run_broker_once(socket_path)
        try:
            result = invoke_water_ants(
                self.registry,
                path,
                socket_path,
                confirmed=True,
            )
        finally:
            thread.join(timeout=2)

        self.assertEqual(result["status"], "stub")
        self.assertEqual(
            result["artifact"]["size_bytes"],
            len(payload),
        )


if __name__ == "__main__":
    unittest.main()
