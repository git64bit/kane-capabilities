import json
import os
import socket
import struct
import tempfile
import threading
import unittest
from pathlib import Path

from civic_orchestrator.usermin_adapter import MAX_ARTIFACT_BYTES
from civic_orchestrator.usermin_broker import handle_connection
from civic_orchestrator.usermin_upload import (
    UploadClientError,
    publish_file,
    read_owned_regular_file,
    send_to_broker,
)


class EchoAdapter:
    def __init__(self):
        self.calls = []

    def handle(self, peer_uid, payload):
        self.calls.append((peer_uid, payload))
        return {
            "status": "validated",
            "remote_dispatch": False,
            "participant_id": "participant:test",
            "artifact": {
                "size_bytes": len(payload),
            },
        }


class UserminUploadTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_participant_reads_owned_regular_file(self):
        path = self.root / "upload.bin"
        path.write_bytes(b"hello civic")

        self.assertEqual(
            read_owned_regular_file(path),
            b"hello civic",
        )

    def test_symlink_is_rejected(self):
        target = self.root / "target.bin"
        target.write_bytes(b"secret-ish bytes")
        link = self.root / "upload-link"
        link.symlink_to(target)

        with self.assertRaisesRegex(
            UploadClientError,
            "cannot open publication file",
        ):
            read_owned_regular_file(link)

    def test_non_regular_file_is_rejected(self):
        with self.assertRaisesRegex(
            UploadClientError,
            "regular file",
        ):
            read_owned_regular_file(self.root)

    def test_file_owned_by_other_uid_is_rejected(self):
        path = self.root / "upload.bin"
        path.write_bytes(b"hello")

        with self.assertRaisesRegex(
            UploadClientError,
            "owned by the invoking participant",
        ):
            read_owned_regular_file(
                path,
                effective_uid=os.geteuid() + 1,
            )

    def test_oversize_file_is_rejected_before_socket_use(self):
        path = self.root / "large.bin"
        path.write_bytes(b"x" * (MAX_ARTIFACT_BYTES + 1))

        with self.assertRaisesRegex(
            UploadClientError,
            "exceeds",
        ):
            read_owned_regular_file(path)

    def test_send_to_broker_transmits_bytes_only(self):
        sock_path = self.root / "broker.sock"
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(sock_path))
        listener.listen(1)
        adapter = EchoAdapter()

        def serve_once():
            conn, _ = listener.accept()
            with conn:
                handle_connection(conn, adapter)

        thread = threading.Thread(target=serve_once)
        thread.start()
        try:
            result = send_to_broker(
                sock_path,
                b'{"client":{"id":"forged"}}',
            )
        finally:
            thread.join(timeout=2)
            listener.close()

        self.assertEqual(result["status"], "validated")
        self.assertFalse(result["remote_dispatch"])
        self.assertEqual(len(adapter.calls), 1)
        self.assertEqual(
            adapter.calls[0][1],
            b'{"client":{"id":"forged"}}',
        )

    def test_publish_file_reads_as_participant_then_sends_content(self):
        path = self.root / "upload.bin"
        payload = b"participant-owned upload"
        path.write_bytes(payload)

        sock_path = self.root / "broker.sock"
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(sock_path))
        listener.listen(1)
        adapter = EchoAdapter()

        def serve_once():
            conn, _ = listener.accept()
            with conn:
                handle_connection(conn, adapter)

        thread = threading.Thread(target=serve_once)
        thread.start()
        try:
            result = publish_file(path, sock_path)
        finally:
            thread.join(timeout=2)
            listener.close()

        self.assertEqual(result["status"], "validated")
        self.assertEqual(adapter.calls[0][1], payload)


if __name__ == "__main__":
    unittest.main()
