from __future__ import annotations

import argparse
import json
import socket
import struct
from pathlib import Path
from typing import Any

from .custom_commands import CustomCommandError, CustomCommandRegistry
from .usermin_adapter import MAX_ARTIFACT_BYTES
from .usermin_broker import MAX_RESPONSE_BYTES, recv_exact
from .usermin_upload import UploadClientError, read_owned_regular_file


_COMMAND_FRAME = struct.Struct("!II")
_RESPONSE_FRAME = struct.Struct("!I")

DEFAULT_SOCKET = Path("/run/civic-orchestrator/custom-command.sock")
DEFAULT_REGISTRY = Path(
    "/etc/civic-orchestrator/custom-command-registry-v1.yaml"
)
DEFAULT_SCHEMA = Path(
    "/etc/civic-orchestrator/custom-command-registry-v1.schema.json"
)
DEFAULT_HELP = Path(
    "/etc/civic-orchestrator/custom-command-help-v1.yaml"
)
DEFAULT_HELP_SCHEMA = Path(
    "/etc/civic-orchestrator/custom-command-help-v1.schema.json"
)


class CommandClientError(ValueError):
    pass


def send_command_to_broker(
    socket_path: Path,
    *,
    codename: str,
    arguments: dict[str, Any],
    payload: bytes,
) -> dict[str, Any]:
    if len(payload) > MAX_ARTIFACT_BYTES:
        raise CommandClientError(
            f"payload exceeds {MAX_ARTIFACT_BYTES} byte Custom Command limit"
        )

    metadata = json.dumps(
        {
            "protocol_version": 1,
            "codename": codename,
            "arguments": arguments,
        },
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")

    conn = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    try:
        conn.connect(str(socket_path))
        conn.sendall(_COMMAND_FRAME.pack(len(metadata), len(payload)))
        conn.sendall(metadata)
        conn.sendall(payload)

        header = recv_exact(conn, _RESPONSE_FRAME.size)
        (length,) = _RESPONSE_FRAME.unpack(header)
        if length > MAX_RESPONSE_BYTES:
            raise CommandClientError(
                "local Custom Command response is too large"
            )
        raw = recv_exact(conn, length)
    except OSError as exc:
        raise CommandClientError(
            f"local Custom Command broker unavailable: {exc}"
        ) from exc
    finally:
        conn.close()

    try:
        value = json.loads(raw.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise CommandClientError(
            "local Custom Command broker returned invalid JSON"
        ) from exc

    if not isinstance(value, dict):
        raise CommandClientError(
            "local Custom Command broker response must be an object"
        )
    return value


def invoke_water_ants(
    registry: CustomCommandRegistry,
    file_path: Path,
    socket_path: Path,
    *,
    confirmed: bool,
) -> dict[str, Any]:
    registry.require_callable("water-ants")
    registry.require_confirmation("water-ants", confirmed)
    payload = read_owned_regular_file(file_path)
    return send_command_to_broker(
        socket_path,
        codename="water-ants",
        arguments={},
        payload=payload,
    )


def load_registry(args: argparse.Namespace) -> CustomCommandRegistry:
    return CustomCommandRegistry.load(
        args.registry,
        args.schema,
        args.help_catalog,
        args.help_schema,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Participant-facing Civic Custom Command helper"
    )
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument(
        "--help-catalog",
        type=Path,
        default=DEFAULT_HELP,
    )
    parser.add_argument(
        "--help-schema",
        type=Path,
        default=DEFAULT_HELP_SCHEMA,
    )

    sub = parser.add_subparsers(dest="action", required=True)

    listing = sub.add_parser(
        "list",
        help="Show participant-discoverable Custom Commands",
    )
    listing.add_argument(
        "--all",
        action="store_true",
        help="Include declared future commands",
    )

    help_cmd = sub.add_parser(
        "help",
        help="Show plain-language help for one Custom Command",
    )
    help_cmd.add_argument("codename")

    run = sub.add_parser(
        "run",
        help="Invoke a bounded Custom Command",
    )
    run.add_argument("codename")
    run.add_argument("--file", type=Path)
    run.add_argument("--socket", type=Path, default=DEFAULT_SOCKET)
    run.add_argument(
        "--confirm",
        action="store_true",
        help=(
            "Record explicit participant acknowledgement when the "
            "command help profile requires it"
        ),
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    try:
        registry = load_registry(args)

        if args.action == "list":
            print(
                registry.render_catalog(
                    include_declared=args.all,
                )
            )
            return

        if args.action == "help":
            print(registry.render_help(args.codename))
            return

        if args.codename != "water-ants":
            raise CommandClientError(
                "no participant helper implementation exists for: "
                f"{args.codename}"
            )
        if args.file is None:
            raise CommandClientError(
                "water-ants requires --file"
            )

        result = invoke_water_ants(
            registry,
            args.file,
            args.socket,
            confirmed=args.confirm,
        )
    except (
        CustomCommandError,
        UploadClientError,
        CommandClientError,
    ) as exc:
        print(
            json.dumps(
                {
                    "status": "rejected",
                    "remote_dispatch": False,
                    "side_effects": False,
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
