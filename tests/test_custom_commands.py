import copy
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import yaml

from civic_orchestrator.custom_commands import (
    CommandInvocation,
    CustomCommandError,
    CustomCommandRegistry,
    LocalCustomCommandAdapter,
)
from civic_orchestrator.usermin_adapter import ParticipantIdentity


ROOT = Path(__file__).resolve().parents[1]
REGISTRY_PATH = ROOT / "contracts" / "custom-command-registry-v1.yaml"
SCHEMA_PATH = ROOT / "schemas" / "custom-command-registry-v1.schema.json"


class StaticParticipantRegistry:
    def resolve(self, uid):
        return ParticipantIdentity(
            uid=uid,
            username="participant1",
            participant_id="participant:test-stable",
        )


class CustomCommandTests(unittest.TestCase):
    def registry(self):
        return CustomCommandRegistry.load(REGISTRY_PATH, SCHEMA_PATH)

    def test_registry_contract_loads_and_water_ants_is_only_stub(self):
        registry = self.registry()
        water = registry.lookup("water-ants")
        self.assertEqual(water["lifecycle"], "stub")
        self.assertEqual(water["binding"]["operation"], "publication.publish")

        other_stubbed = [
            item["codename"]
            for item in registry.value["commands"]
            if item["lifecycle"] == "stub" and item["codename"] != "water-ants"
        ]
        self.assertEqual(other_stubbed, [])

    def test_declared_command_is_not_callable(self):
        with self.assertRaisesRegex(
            CustomCommandError,
            "not callable",
        ):
            self.registry().require_callable("navy-roots")

    def test_unknown_codename_is_rejected(self):
        with self.assertRaisesRegex(
            CustomCommandError,
            "unknown Custom Command",
        ):
            self.registry().require_callable("fake-name")

    def test_water_ants_stub_binds_participant_and_derives_evidence(self):
        payload = b"bounded publication bytes"
        adapter = LocalCustomCommandAdapter(
            StaticParticipantRegistry(),
            self.registry(),
        )

        result = adapter.handle(
            1002,
            CommandInvocation(
                codename="water-ants",
                arguments={},
                payload=payload,
            ),
        )

        self.assertEqual(result["status"], "stub")
        self.assertFalse(result["remote_dispatch"])
        self.assertFalse(result["side_effects"])
        self.assertEqual(result["command"], "water-ants")
        self.assertEqual(result["operation"], "publication.publish")
        self.assertEqual(result["participant_id"], "participant:test-stable")
        self.assertEqual(
            result["artifact"]["sha256"],
            hashlib.sha256(payload).hexdigest(),
        )

    def test_water_ants_rejects_typed_arguments(self):
        adapter = LocalCustomCommandAdapter(
            StaticParticipantRegistry(),
            self.registry(),
        )
        with self.assertRaisesRegex(
            CustomCommandError,
            "does not accept typed arguments",
        ):
            adapter.handle(
                1002,
                CommandInvocation(
                    codename="water-ants",
                    arguments={"operation": "shell.exec"},
                    payload=b"x",
                ),
            )

    def test_duplicate_codename_fails_closed(self):
        value = yaml.safe_load(REGISTRY_PATH.read_text(encoding="utf-8"))
        duplicate = copy.deepcopy(value["commands"][1])
        duplicate["codename"] = "water-ants"
        value["commands"].append(duplicate)

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "registry.yaml"
            path.write_text(yaml.safe_dump(value), encoding="utf-8")
            with self.assertRaisesRegex(
                CustomCommandError,
                "duplicate Custom Command codename",
            ):
                CustomCommandRegistry.load(path, SCHEMA_PATH)


if __name__ == "__main__":
    unittest.main()
