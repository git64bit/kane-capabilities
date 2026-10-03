from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator

from .usermin_adapter import (
    LocalAdapterError,
    ParticipantIdentity,
    ParticipantRegistry,
    derive_artifact,
)


class CustomCommandError(LocalAdapterError):
    pass


@dataclass(frozen=True)
class CommandInvocation:
    codename: str
    arguments: dict[str, Any]
    payload: bytes


class CustomCommandRegistry:
    """Validated, trusted inventory of participant-facing Custom Commands."""

    CALLABLE_LIFECYCLES = {"stub", "validation", "available"}

    def __init__(self, value: dict[str, Any]) -> None:
        self.value = value
        commands = value["commands"]
        seen: set[str] = set()
        indexed: dict[str, dict[str, Any]] = {}

        for command in commands:
            codename = command["codename"]
            if codename in seen:
                raise CustomCommandError(
                    f"duplicate Custom Command codename: {codename}"
                )
            seen.add(codename)

            lifecycle = command["lifecycle"]
            side_effects = command["side_effects_enabled"]
            binding = command["binding"]

            if lifecycle != "available" and side_effects:
                raise CustomCommandError(
                    f"non-available command enables side effects: {codename}"
                )
            if lifecycle in self.CALLABLE_LIFECYCLES:
                if binding["status"] != "bound":
                    raise CustomCommandError(
                        f"callable command has no bound operation: {codename}"
                    )

            indexed[codename] = command

        self._commands = indexed

    @classmethod
    def load(
        cls,
        registry_path: Path,
        schema_path: Path,
    ) -> "CustomCommandRegistry":
        try:
            registry_value = yaml.safe_load(
                Path(registry_path).read_text(encoding="utf-8")
            )
            schema_value = json.loads(
                Path(schema_path).read_text(encoding="utf-8")
            )
        except (OSError, UnicodeDecodeError, json.JSONDecodeError, yaml.YAMLError) as exc:
            raise CustomCommandError(
                f"Custom Command registry cannot be loaded: {exc}"
            ) from exc

        if not isinstance(registry_value, dict):
            raise CustomCommandError("Custom Command registry must be an object")

        try:
            Draft202012Validator.check_schema(schema_value)
            Draft202012Validator(schema_value).validate(registry_value)
        except Exception as exc:
            raise CustomCommandError(
                f"Custom Command registry contract is invalid: {exc}"
            ) from exc

        return cls(registry_value)

    def lookup(self, codename: str) -> dict[str, Any]:
        try:
            return self._commands[codename]
        except KeyError as exc:
            raise CustomCommandError(
                f"unknown Custom Command codename: {codename}"
            ) from exc

    def require_callable(self, codename: str) -> dict[str, Any]:
        command = self.lookup(codename)
        if command["lifecycle"] not in self.CALLABLE_LIFECYCLES:
            raise CustomCommandError(
                f"Custom Command is not callable: {codename}"
            )
        if command["binding"]["status"] != "bound":
            raise CustomCommandError(
                f"Custom Command has no bound operation: {codename}"
            )
        return command


class LocalCustomCommandAdapter:
    """Repository-side generic Custom Command stub dispatcher.

    This class deliberately performs no remote dispatch. It proves command
    recognition, participant binding, input validation, and fixed semantic
    binding before the production Usermin command is switched to this path.
    """

    def __init__(
        self,
        participant_registry: ParticipantRegistry,
        command_registry: CustomCommandRegistry,
    ) -> None:
        self.participant_registry = participant_registry
        self.command_registry = command_registry

    def _validate_input(
        self,
        command: dict[str, Any],
        invocation: CommandInvocation,
    ) -> None:
        profile = command["input_profile"]

        if not isinstance(invocation.arguments, dict):
            raise CustomCommandError("Custom Command arguments must be an object")

        if not profile["byte_payload"] and invocation.payload:
            raise CustomCommandError(
                f"Custom Command does not accept a byte payload: {invocation.codename}"
            )

        mode = profile["mode"]
        if mode in {"none", "upload-bytes"} and invocation.arguments:
            raise CustomCommandError(
                f"Custom Command does not accept typed arguments: {invocation.codename}"
            )
        if mode == "none" and invocation.payload:
            raise CustomCommandError(
                f"Custom Command accepts no input payload: {invocation.codename}"
            )

    def handle(
        self,
        peer_uid: int,
        invocation: CommandInvocation,
    ) -> dict[str, Any]:
        participant = self.participant_registry.resolve(peer_uid)
        command = self.command_registry.require_callable(invocation.codename)
        self._validate_input(command, invocation)

        if invocation.codename != "water-ants":
            raise CustomCommandError(
                f"no repository stub handler exists for: {invocation.codename}"
            )

        artifact = derive_artifact(invocation.payload)
        binding = command["binding"]
        return {
            "status": "stub",
            "remote_dispatch": False,
            "side_effects": False,
            "command": invocation.codename,
            "operation": binding["operation"],
            "participant_id": participant.participant_id,
            "artifact": {
                "media_type": artifact["media_type"],
                "size_bytes": artifact["size_bytes"],
                "sha256": artifact["sha256"],
            },
        }
