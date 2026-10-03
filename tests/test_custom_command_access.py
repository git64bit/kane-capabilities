import copy
import json
import unittest
from pathlib import Path

import yaml
from jsonschema import Draft202012Validator, ValidationError


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = ROOT / "schemas" / "custom-command-access-v1.schema.json"
EXAMPLE = ROOT / "deploy" / "usermin" / "custom-command-access-v1.example.yaml"


class CustomCommandAccessContractTests(unittest.TestCase):
    def values(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        value = yaml.safe_load(EXAMPLE.read_text(encoding="utf-8"))
        return schema, value

    def test_example_validates_and_defaults_deny(self):
        schema, value = self.values()
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(
            schema,
            format_checker=Draft202012Validator.FORMAT_CHECKER,
        ).validate(value)

        self.assertEqual(
            value["defaults"],
            {"discover": False, "invoke": False},
        )
        self.assertTrue(
            value["qualification_semantics"]["descriptive_only"]
        )
        self.assertFalse(
            value["qualification_semantics"]["automatic_grants"]
        )

    def test_invoke_requires_discovery(self):
        schema, value = self.values()
        broken = copy.deepcopy(value)
        grant = broken["participants"][0]["command_access"][0]
        grant["discover"] = False
        grant["invoke"] = True

        with self.assertRaises(ValidationError):
            Draft202012Validator(
                schema,
                format_checker=Draft202012Validator.FORMAT_CHECKER,
            ).validate(broken)

    def test_qualification_does_not_create_command_access(self):
        _, value = self.values()
        participant = value["participants"][1]
        self.assertTrue(participant["qualifications"])
        self.assertEqual(participant["command_access"], [])


if __name__ == "__main__":
    unittest.main()
