from __future__ import annotations

import argparse
import json
import os
import socket
import struct
from typing import Any

from .usermin_adapter import (
    LocalAdapterError,
    LocalPublicationAdapter,
    MAX_ARTIFACT_BYTES,
    ParticipantRegistry,
)


_FRAME = struct.Struct("!I")
MAX_RESPONSE_BYTES = 65_536


class BrokerProtocolError(ValueError):
    pass


def recv_exact(conn: socket.socket, length: int) -> bytes:
    chunks: list[bytes] = []
    remaining = length
    while remaining:
        chunk = conn.recv(remaining)
        if not chunk:
            raise BrokerProtocolError("unexpected end of local broker frame")
        chunks.append(chunk)
        remaining -= len(chunk)
    return b"".join(chunks)


def recv_payload(conn: socket.socket) -> bytes:
    header = recv_exact(conn, _FRAME.size)
    (length,) = _FRAME.unpack(header)
    if length > MAX_ARTIFACT_BYTES:
        raise BrokerProtocolError(
            f"artifact exceeds {MAX_ARTIFACT_BYTES} byte publication limit"
        )
    return recv_exact(conn, length)


def send_json(conn: socket.socket, value: dict[str, Any]) -> None:
    body = json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    if len(body) > MAX_RESPONSE_BYTES:
        raise BrokerProtocolError("local broker response is too large")
    conn.sendall(_FRAME.pack(len(body)))
    conn.sendall(body)


def peer_credentials(conn: socket.socket) -> tuple[int, int, int]:
    if not hasattr(socket, "SO_PEERCRED"):
        raise BrokerProtocolError("SO_PEERCRED is unavailable")
    raw = conn.getsockopt(
        socket.SOL_SOCKET,
        socket.SO_PEERCRED,
        struct.calcsize("3i"),
    )
    return struct.unpack("3i", raw)


def handle_connection(
    conn: socket.socket,
    adapter: LocalPublicationAdapter,
) -> None:
    try:
        _pid, uid, _gid = peer_credentials(conn)
        payload = recv_payload(conn)
        response = adapter.handle(uid, payload)
    except (BrokerProtocolError, LocalAdapterError) as exc:
        response = {
            "status": "rejected",
            "remote_dispatch": False,
            "error": str(exc)[:500],
        }
    except Exception:
        response = {
            "status": "rejected",
            "remote_dispatch": False,
            "error": "internal local broker error",
        }

    send_json(conn, response)


def serve(
    listener: socket.socket,
    adapter: LocalPublicationAdapter,
) -> None:
    while True:
        conn, _ = listener.accept()
        with conn:
            handle_connection(conn, adapter)


def systemd_listener() -> socket.socket:
    try:
        listen_pid = int(os.environ.get("LISTEN_PID", "0"))
        listen_fds = int(os.environ.get("LISTEN_FDS", "0"))
    except ValueError as exc:
        raise RuntimeError("invalid systemd socket activation environment") from exc

    if listen_pid != os.getpid() or listen_fds != 1:
        raise RuntimeError(
            "exactly one systemd-activated socket is required"
        )

    return socket.fromfd(3, socket.AF_UNIX, socket.SOCK_STREAM)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--participant-registry",
        required=True,
    )
    parser.add_argument(
        "--participant-group",
        default="civic-participants",
    )
    args = parser.parse_args()

    registry = ParticipantRegistry(
        args.participant_registry,
        participant_group=args.participant_group,
    )
    adapter = LocalPublicationAdapter(registry)

    listener = systemd_listener()
    with listener:
        serve(listener, adapter)


if __name__ == "__main__":
    main()
