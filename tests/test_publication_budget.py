import tempfile
import unittest
from pathlib import Path

from civic_orchestrator.publication_budget import (
    PublicationBudgetExceeded,
    PublicationBudgetPolicy,
)
from civic_orchestrator.runtime import StateStore


class PublicationBudgetPolicyTests(unittest.TestCase):
    def test_policy_requires_non_negative_integer_limits(self):
        with self.assertRaises(ValueError):
            PublicationBudgetPolicy(
                max_publications=-1,
                max_publication_bytes=1024,
            )
        with self.assertRaises(ValueError):
            PublicationBudgetPolicy(
                max_publications=1,
                max_publication_bytes=True,
            )


class PublicationBudgetStateTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.state = StateStore(Path(self.tmp.name) / "state.sqlite3")
        self.policy = PublicationBudgetPolicy(
            max_publications=2,
            max_publication_bytes=100,
        )

    def tearDown(self):
        self.tmp.cleanup()

    def workflow(self, request_id):
        return self.state.create_workflow(
            request_id,
            "publication.publish",
        )

    def test_reservation_is_charged_and_release_restores_capacity(self):
        workflow_id = self.workflow("req:budget-1")

        usage = self.state.reserve_publication_budget(
            workflow_id=workflow_id,
            participant_id="participant:test",
            size_bytes=40,
            policy=self.policy,
        )

        self.assertEqual(usage.charged_publications, 1)
        self.assertEqual(usage.charged_bytes, 40)
        self.assertEqual(
            self.state.publication_budget_usage(
                "participant:test"
            ).charged_bytes,
            40,
        )

        self.state.release_publication_budget_hold(workflow_id)

        usage = self.state.publication_budget_usage("participant:test")
        self.assertEqual(usage.charged_publications, 0)
        self.assertEqual(usage.charged_bytes, 0)

    def test_count_limit_is_enforced_before_second_excess_hold(self):
        first = self.workflow("req:budget-count-1")
        second = self.workflow("req:budget-count-2")
        third = self.workflow("req:budget-count-3")

        self.state.reserve_publication_budget(
            workflow_id=first,
            participant_id="participant:test",
            size_bytes=10,
            policy=self.policy,
        )
        self.state.reserve_publication_budget(
            workflow_id=second,
            participant_id="participant:test",
            size_bytes=10,
            policy=self.policy,
        )

        with self.assertRaises(PublicationBudgetExceeded):
            self.state.reserve_publication_budget(
                workflow_id=third,
                participant_id="participant:test",
                size_bytes=10,
                policy=self.policy,
            )

        usage = self.state.publication_budget_usage("participant:test")
        self.assertEqual(usage.charged_publications, 2)
        self.assertEqual(usage.charged_bytes, 20)

    def test_byte_limit_is_enforced_atomically(self):
        first = self.workflow("req:budget-bytes-1")
        second = self.workflow("req:budget-bytes-2")

        self.state.reserve_publication_budget(
            workflow_id=first,
            participant_id="participant:test",
            size_bytes=70,
            policy=self.policy,
        )

        with self.assertRaises(PublicationBudgetExceeded):
            self.state.reserve_publication_budget(
                workflow_id=second,
                participant_id="participant:test",
                size_bytes=31,
                policy=self.policy,
            )

        usage = self.state.publication_budget_usage("participant:test")
        self.assertEqual(usage.charged_publications, 1)
        self.assertEqual(usage.charged_bytes, 70)

    def test_uncertain_hold_remains_charged(self):
        workflow_id = self.workflow("req:budget-uncertain")
        self.state.reserve_publication_budget(
            workflow_id=workflow_id,
            participant_id="participant:test",
            size_bytes=25,
            policy=self.policy,
        )

        self.state.mark_publication_budget_hold(
            workflow_id,
            "uncertain",
        )

        usage = self.state.publication_budget_usage("participant:test")
        self.assertEqual(usage.charged_publications, 1)
        self.assertEqual(usage.charged_bytes, 25)

        with self.state._connect() as conn:
            row = conn.execute(
                """
                SELECT hold_state
                  FROM publication_budget_holds
                 WHERE workflow_id=?
                """,
                (workflow_id,),
            ).fetchone()
        self.assertEqual(row[0], "uncertain")


if __name__ == "__main__":
    unittest.main()
