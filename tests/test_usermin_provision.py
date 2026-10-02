import json
import os
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from civic_orchestrator.usermin_adapter import LocalAdapterError
from civic_orchestrator.usermin_provision import provision_participant


class UserminProvisionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.registry_path = Path(self.tmp.name) / "participants-v1.json"
        self.registry_path.write_text(
            json.dumps({"version": 1, "participants": []}) + "\n",
            encoding="utf-8",
        )
        os.chmod(self.registry_path, 0o640)
        self.memberships = [1003]
        self.group_add_calls = []

    def tearDown(self):
        self.tmp.cleanup()

    def account_patches(self):
        account = SimpleNamespace(
            pw_name="participant1",
            pw_uid=1002,
            pw_gid=1003,
        )
        group = SimpleNamespace(gr_gid=1004)

        def getgrouplist(_username, _primary_gid):
            return list(self.memberships)

        return (
            patch(
                "civic_orchestrator.usermin_provision.pwd.getpwnam",
                return_value=account,
            ),
            patch(
                "civic_orchestrator.usermin_provision.grp.getgrnam",
                return_value=group,
            ),
            patch(
                "civic_orchestrator.usermin_provision.os.getgrouplist",
                side_effect=getgrouplist,
            ),
        )

    def group_adder(self, username, group_name):
        self.group_add_calls.append((username, group_name))
        if 1004 not in self.memberships:
            self.memberships.append(1004)

    def read_entries(self):
        return json.loads(
            self.registry_path.read_text(encoding="utf-8")
        )["participants"]

    def provision(self):
        p1, p2, p3 = self.account_patches()
        with p1, p2, p3:
            return provision_participant(
                "participant1",
                self.registry_path,
                participant_group="civic-participants",
                group_adder=self.group_adder,
                require_root=False,
                require_secure_file=False,
            )

    def test_new_account_gets_group_and_stable_participant_id(self):
        participant_id = self.provision()

        self.assertRegex(
            participant_id,
            r"^participant:[0-9a-f-]{36}$",
        )
        self.assertEqual(
            self.group_add_calls,
            [("participant1", "civic-participants")],
        )

        entries = self.read_entries()
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["username"], "participant1")
        self.assertEqual(entries[0]["uid"], 1002)
        self.assertEqual(entries[0]["participant_id"], participant_id)
        self.assertTrue(entries[0]["active"])

    def test_repeated_provisioning_returns_same_id_without_duplicate(self):
        first = self.provision()
        self.group_add_calls.clear()

        second = self.provision()

        self.assertEqual(second, first)
        self.assertEqual(self.group_add_calls, [])
        self.assertEqual(len(self.read_entries()), 1)

    def test_existing_mapping_repairs_missing_group_membership(self):
        first = self.provision()
        self.memberships = [1003]
        self.group_add_calls.clear()

        second = self.provision()

        self.assertEqual(second, first)
        self.assertEqual(
            self.group_add_calls,
            [("participant1", "civic-participants")],
        )
        self.assertEqual(len(self.read_entries()), 1)

    def test_retired_exact_account_mapping_is_not_reused(self):
        self.registry_path.write_text(
            json.dumps(
                {
                    "version": 1,
                    "participants": [
                        {
                            "username": "participant1",
                            "uid": 1002,
                            "participant_id": "participant:retired-one",
                            "active": False,
                        }
                    ],
                }
            )
            + "\n",
            encoding="utf-8",
        )
        os.chmod(self.registry_path, 0o640)

        with self.assertRaisesRegex(
            LocalAdapterError,
            "cannot be automatically reused",
        ):
            self.provision()

        self.assertEqual(self.group_add_calls, [])


if __name__ == "__main__":
    unittest.main()
