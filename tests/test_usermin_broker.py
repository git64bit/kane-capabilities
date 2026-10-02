import json
import os
import socket
import struct
import threading
import unittest

from civic_orchestrator.usermin_adapter import MAX_ARTIFACT_BYTES
from civic_orchestrator.usermin_broker import (
    handle_connection,
    recv_exact,
)


_FRAME = struct.Struct("!I")


class RecordingAdapter:
    def __init__(self):
        self.calls = []

    def handle(self, peer_uid, payload):
        self.calls.append((peer_uid, payload))
        return {
            "status": "validated",
            "remote_dispatch": False,
            "size": len(payload),
        }


def receive_json(conn):
    header = recv_exact(conn, _FRAME.size)
    (length,) = _FRAME.unpack(header)
    body = recv_exact(conn, length)
    return json.loads(body.decode("utf-8"))


class UserminBrokerTests(unittest.TestCase):
    def exchange(self, frame_bytes, adapter=None):
        if adapter is None:
            adapter = RecordingAdapter()
        server, client = socket.socketpair(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
        )

        thread = threading.Thread(
            target=handle_connection,
            args=(server, adapter),
        )
        thread.start()
        try:
            client.sendall(frame_bytes)
            result = receive_json(client)
        finally:
            client.close()
            thread.join(timeout=2)
            server.close()
        return result, adapter

    def test_kernel_peer_uid_is_used_with_byte_payload(self):
        payload = b'{"caller":{"subject":"operator:root"}}'
        result, adapter = self.exchange(
            _FRAME.pack(len(payload)) + payload
        )

        self.assertEqual(result["status"], "validated")
        self.assertEqual(len(adapter.calls), 1)
        peer_uid, observed_payload = adapter.calls[0]
        self.assertEqual(peer_uid, os.getuid())
        self.assertEqual(observed_payload, payload)

    def test_oversize_frame_is_rejected_before_payload_read(self):
        result, adapter = self.exchange(
            _FRAME.pack(MAX_ARTIFACT_BYTES + 1)
        )

        self.assertEqual(result["status"], "rejected")
        self.assertFalse(result["remote_dispatch"])
        self.assertIn("exceeds", result["error"])
        self.assertEqual(adapter.calls, [])

    def test_empty_file_is_valid_local_frame(self):
        result, adapter = self.exchange(_FRAME.pack(0))

        self.assertEqual(result["status"], "validated")
        self.assertEqual(adapter.calls[0][1], b"")

    def test_truncated_payload_is_rejected(self):
        server, client = socket.socketpair(
            socket.AF_UNIX,
            socket.SOCK_STREAM,
        )
        adapter = RecordingAdapter()
        thread = threading.Thread(
            target=handle_connection,
            args=(server, adapter),
        )
        thread.start()
        try:
            client.sendall(_FRAME.pack(5) + b"abc")
            client.shutdown(socket.SHUT_WR)
            result = receive_json(client)
        finally:
            client.close()
            thread.join(timeout=2)
            server.close()

        self.assertEqual(result["status"], "rejected")
        self.assertIn("unexpected end", result["error"])
        self.assertEqual(adapter.calls, [])


if __name__ == "__main__":
    unittest.main()
