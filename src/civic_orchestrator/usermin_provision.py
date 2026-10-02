from __future__ import annotations

import argparse
import fcntl
import grp
import json
import os
import pwd
import stat
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Callable

from .usermin_adapter import LocalAdapterError, ParticipantRegistry


GroupAdder = Callable[[str, str], None]


def _default_group_adder(username: str, group_name: str) -> None:
    try:
        subprocess.run(
            ["/usr/sbin/usermod", "-a", "-G", group_name, username],
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise LocalAdapterError(
            f"cannot add account to {group_name}: {exc}"
        ) from exc


def _is_group_member(
    username: str,
    primary_gid: int,
    group_name: str,
) -> bool:
    try:
        group = grp.getgrnam(group_name)
    except KeyError as exc:
        raise LocalAdapterError(
            f"required group does not exist: {group_name}"
        ) from exc

    try:
        gids = os.getgrouplist(username, primary_gid)
    except OSError as exc:
        raise LocalAdapterError(
            "cannot resolve participant group membership"
        ) from exc

    return group.gr_gid in gids


def _write_registry_atomic(
    path: Path,
    entries: list[dict],
) -> None:
    st = path.stat()
    mode = stat.S_IMODE(st.st_mode)

    fd, temporary = tempfile.mkstemp(
        prefix=".participants-v1.",
        dir=path.parent,
    )
    try:
        os.fchmod(fd, mode)
        if os.geteuid() == 0:
            os.fchown(fd, st.st_uid, st.st_gid)

        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            fd = -1
            json.dump(
                {
                    "version": 1,
                    "participants": entries,
                },
                handle,
                indent=2,
            )
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary, path)

        directory_fd = os.open(path.parent, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except Exception:
        if fd >= 0:
            os.close(fd)
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def provision_participant(
    username: str,
    registry_path: Path,
    *,
    participant_group: str = "civic-participants",
    group_adder: GroupAdder = _default_group_adder,
    require_root: bool = True,
    require_secure_file: bool = True,
) -> str:
    """Idempotently provision one existing Unix account as a Civic participant."""

    if require_root and os.geteuid() != 0:
        raise LocalAdapterError("participant provisioning requires root")

    try:
        account = pwd.getpwnam(username)
    except KeyError as exc:
        raise LocalAdapterError(
            f"Unix account does not exist: {username}"
        ) from exc

    path = Path(registry_path)
    lock_path = path.with_name(path.name + ".lock")

    lock_fd = os.open(
        lock_path,
        os.O_RDWR | os.O_CREAT,
        0o600,
    )
    with os.fdopen(lock_fd, "r+", encoding="utf-8") as lock:
        fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

        registry = ParticipantRegistry(
            path,
            participant_group=participant_group,
            require_secure_file=require_secure_file,
        )
        entries = registry._load_entries()

        exact_active = [
            item
            for item in entries
            if item["username"] == account.pw_name
            and item["uid"] == account.pw_uid
            and item["active"]
        ]
        if len(exact_active) == 1:
            participant_id = exact_active[0]["participant_id"]
        elif exact_active:
            raise LocalAdapterError(
                "Unix account has multiple active participant mappings"
            )
        else:
            exact_retired = [
                item
                for item in entries
                if item["username"] == account.pw_name
                and item["uid"] == account.pw_uid
                and not item["active"]
            ]
            if exact_retired:
                raise LocalAdapterError(
                    "retired Unix account mapping cannot be automatically reused"
                )

            known_ids = {
                item["participant_id"]
                for item in entries
            }
            while True:
                participant_id = f"participant:{uuid.uuid4()}"
                if participant_id not in known_ids:
                    break

            if not _is_group_member(
                account.pw_name,
                account.pw_gid,
                participant_group,
            ):
                group_adder(account.pw_name, participant_group)

            entries.append(
                {
                    "username": account.pw_name,
                    "uid": account.pw_uid,
                    "participant_id": participant_id,
                    "active": True,
                }
            )
            _write_registry_atomic(path, entries)

        if not _is_group_member(
            account.pw_name,
            account.pw_gid,
            participant_group,
        ):
            group_adder(account.pw_name, participant_group)

        return participant_id


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Provision an existing Portal Unix account as a Civic participant."
        )
    )
    parser.add_argument("username")
    parser.add_argument(
        "--participant-registry",
        default="/etc/civic-orchestrator/participants-v1.json",
    )
    parser.add_argument(
        "--participant-group",
        default="civic-participants",
    )
    args = parser.parse_args()

    try:
        participant_id = provision_participant(
            args.username,
            Path(args.participant_registry),
            participant_group=args.participant_group,
        )
    except LocalAdapterError as exc:
        parser.exit(1, f"provisioning rejected: {exc}\n")

    print(participant_id)


if __name__ == "__main__":
    main()
