from __future__ import annotations

import argparse
import json
import os
import socket
import stat
import struct
from pathlib import Path
from typing import Any

from .usermin_adapter import MAX_ARTIFACT_BYTES
from .usermin_broker import MAX_RESPONSE_BYTES, recv_exact


_FRAME = struct.Struct("!I")


class UploadClientError(ValueError):
    pass


def read_owned_regular_file(
    path: Path,
    *,
    effective_uid: int | None = None,
) -> bytes:
    path = Path(path)
    if effective_uid is None:
        effective_uid = os.geteuid()

    if not hasattr(os, "O_NOFOLLOW"):
        raise UploadClientError("O_NOFOLLOW is required")

    flags = os.O_RDONLY | os.O_CLOEXEC | os.O_NOFOLLOW
    try:
        fd = os.open(path, flags)
    except OSError as exc:
        raise UploadClientError(f"cannot open publication file: {exc}") from exc

    try:
        st = os.fstat(fd)
        if not stat.S_ISREG(st.st_mode):
            raise UploadClientError("publication input must be a regular file")
        if st.st_uid != effective_uid:
            raise UploadClientError(
                "publication input must be owned by the invoking participant"
            )
        if st.st_size > MAX_ARTIFACT_BYTES:
            raise UploadClientError(
                f"artifact exceeds {MAX_ARTIFACT_BYTES} byte publication limit"
            )

        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(65_536, MAX_ARTIFACT_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_ARTIFACT_BYTES:
                raise UploadClientError(
                    f"artifact exceeds {MAX_ARTIFACT_BYTES} byte publication limit"
                )

        return b"".join(chunks)
    finally:
        os.close(fd)


def send_to_broker(
    socket_path: Path,
    payload: bytes,
) -> dict[str, Any]:
    if len(payload) > MAX_ARTIFACT_BYTES:
        raise UploadClientError(
            f"artifact exceeds {MAX_ARTIFACT_BYTES} byte publication limit"
        )

    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        conn.connect(str(socket_path))
        conn.sendall(_FRAME.pack(len(payload)))
        conn.sendall(payload)

        header = recv_exact(conn, _FRAME.size)
        (length,) = _FRAME.unpack(header)
        if length > MAX_RESPONSE_BYTES:
            raise UploadClientError("local broker response is too large")
        raw = recv_exact(conn, length)
    except OSError as exc:
        raise UploadClientError(f"local publication broker unavailable: {exc}") from exc
    finally:
        conn.close()

    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise UploadClientError("local broker returned invalid JSON") from exc

    if not isinstance(value, dict):
        raise UploadClientError("local broker response must be an object")
    return value


def publish_file(
    path: Path,
    socket_path: Path,
) -> dict[str, Any]:
    payload = read_owned_regular_file(path)
    return send_to_broker(socket_path, payload)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("file")
    parser.add_argument(
        "--socket",
        default="/run/civic-orchestrator/usermin.sock",
    )
    args = parser.parse_args()

    try:
        result = publish_file(
            Path(args.file),
            Path(args.socket),
        )
    except UploadClientError as exc:
        print(
            json.dumps(
                {
                    "status": "rejected",
                    "remote_dispatch": False,
                    "error": str(exc),
                },
                sort_keys=True,
            )
        )
        raise SystemExit(1)

    print(json.dumps(result, sort_keys=True))
    if result.get("status") == "rejected":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
