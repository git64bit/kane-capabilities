from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import uuid
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterator

import yaml
from jsonschema import Draft202012Validator, FormatChecker, ValidationError
from referencing import Registry, Resource
from rfc3339_validator import validate_rfc3339

from .publication import (
    PublicationServiceFailure,
    PublicationServiceProtocolError,
    PublicationServiceUnavailable,
)


_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:/@-]{0,159}$")
_OPERATION_RE = re.compile(
    r"^(publication|geography|participant|repository|rag|inference|edge|firmware|"
    r"signing|audit|incident)\.[a-z][a-z0-9._-]{0,159}$"
)

CIVIC_FORMAT_CHECKER = FormatChecker()

@CIVIC_FORMAT_CHECKER.checks("date-time")
def _is_rfc3339_datetime(value: object) -> bool:
    return isinstance(value, str) and bool(validate_rfc3339(value))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def canonical_json(value: Any) -> str:
    return json.dumps(
        value,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    )


class ConflictError(ValueError):
    pass


@dataclass(frozen=True)
class RuntimePaths:
    repo_root: Path
    state_db: Path


class ContractStore:
    def __init__(self, repo_root: Path) -> None:
        self.repo_root = repo_root
        self.schemas_dir = repo_root / "schemas"
        self._schemas: dict[str, dict[str, Any]] = {}
        self._validators: dict[str, Draft202012Validator] = {}
        self._load()

    def _load(self) -> None:
        registry = Registry()

        for path in self.schemas_dir.glob("*.schema.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self._schemas[path.name] = schema

        for schema in self._schemas.values():
            schema_id = schema.get("$id")
            if not schema_id:
                raise ValueError("every Civic schema must have an absolute $id")
            registry = registry.with_resource(
                schema_id,
                Resource.from_contents(schema),
            )

        for name, schema in self._schemas.items():
            self._validators[name] = Draft202012Validator(
                schema,
                registry=registry,
                format_checker=CIVIC_FORMAT_CHECKER,
            )

    def validate(self, schema_name: str, instance: Any) -> None:
        validator = self._validators[schema_name]
        errors = sorted(
            validator.iter_errors(instance),
            key=lambda e: list(e.absolute_path),
        )
        if errors:
            err = errors[0]
            path = ".".join(str(p) for p in err.absolute_path) or "$"
            raise ValidationError(f"{path}: {err.message}")


class OperationRegistry:
    def __init__(self, path: Path, contracts: ContractStore) -> None:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        contracts.validate("operation-registry-v1.schema.json", raw)

        operations = [item["operation"] for item in raw["operations"]]
        if len(operations) != len(set(operations)):
            raise ValueError("operation registry contains duplicate operations")

        self.contract_version = raw["contract_version"]
        self.operations = {item["operation"]: item for item in raw["operations"]}
        self.prohibited = set(raw.get("prohibited_generic_operations", []))

    def lookup(self, operation: str) -> dict[str, Any] | None:
        return self.operations.get(operation)


class StubWorkflowDefinition:
    def __init__(self, path: Path, contracts: ContractStore) -> None:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        contracts.validate("stub-workflow-definition-v1.schema.json", raw)
        self.authorization_policy = raw["authorization_policy"]
        self.accepted_namespaces = set(raw["accepted_namespaces"])
        self.constraints = raw["constraints"]

    def accepts(self, operation: str) -> bool:
        namespace = operation.split(".", 1)[0]
        return namespace in self.accepted_namespaces


class StateStore:
    ALLOWED_TRANSITIONS = {
        "received": {"validated", "rejected", "failed"},
        "validated": {"authorized", "rejected", "failed"},
        "authorized": {"accepted", "rejected", "failed"},
        "accepted": {"waiting", "completed", "failed", "not-implemented"},
        "waiting": {"accepted", "completed", "rejected", "failed"},
        "completed": set(),
        "rejected": set(),
        "failed": set(),
        "not-implemented": set(),
    }

    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        """Open one SQLite connection for a state operation and always close it.

        The inner connection context preserves sqlite3 commit/rollback
        semantics, including explicit BEGIN IMMEDIATE issued by callers.
        The outer finally guarantees the connection itself is closed.
        """
        conn = sqlite3.connect(self.db_path, timeout=30)
        try:
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA foreign_keys=ON")
            with conn:
                yield conn
        finally:
            conn.close()

    @staticmethod
    def _columns(conn: sqlite3.Connection, table: str) -> set[str]:
        return {row[1] for row in conn.execute(f"PRAGMA table_info({table})")}

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS workflows (
                    workflow_id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    state TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    side_effects INTEGER NOT NULL CHECK(side_effects IN (0,1))
                );

                CREATE TABLE IF NOT EXISTS authorization_decisions (
                    decision_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    request_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    decision TEXT NOT NULL,
                    decided_at TEXT NOT NULL,
                    policy TEXT NOT NULL,
                    reason TEXT,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id)
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    event_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    recorded_at TEXT NOT NULL,
                    actor TEXT NOT NULL,
                    data_json TEXT NOT NULL,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id)
                );

                CREATE TABLE IF NOT EXISTS receipts (
                    receipt_id TEXT PRIMARY KEY,
                    workflow_id TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    issued_at TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    side_effects INTEGER NOT NULL CHECK(side_effects IN (0,1)),
                    evidence_json TEXT NOT NULL,
                    FOREIGN KEY(workflow_id) REFERENCES workflows(workflow_id)
                );

                CREATE TABLE IF NOT EXISTS request_diagnostics (
                    diagnostic_id TEXT PRIMARY KEY,
                    recorded_at TEXT NOT NULL,
                    outcome TEXT NOT NULL,
                    request_id TEXT,
                    operation TEXT,
                    caller_subject TEXT,
                    client_id TEXT,
                    detail TEXT
                );
                """
            )

            workflow_columns = self._columns(conn, "workflows")
            if "idempotency_key" not in workflow_columns:
                conn.execute("ALTER TABLE workflows ADD COLUMN idempotency_key TEXT")
            if "request_fingerprint" not in workflow_columns:
                conn.execute("ALTER TABLE workflows ADD COLUMN request_fingerprint TEXT")
            if "result_json" not in workflow_columns:
                conn.execute("ALTER TABLE workflows ADD COLUMN result_json TEXT")
            if "caller_subject" not in workflow_columns:
                conn.execute("ALTER TABLE workflows ADD COLUMN caller_subject TEXT")
            if "client_id" not in workflow_columns:
                conn.execute("ALTER TABLE workflows ADD COLUMN client_id TEXT")

            audit_columns = self._columns(conn, "audit_events")
            if "sequence" not in audit_columns:
                conn.execute(
                    "ALTER TABLE audit_events ADD COLUMN sequence INTEGER NOT NULL DEFAULT 0"
                )

            conn.execute(
                "CREATE INDEX IF NOT EXISTS workflows_request_scope_idx "
                "ON workflows(client_id, caller_subject, request_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS workflows_idempotency_scope_idx "
                "ON workflows(client_id, caller_subject, idempotency_key)"
            )

            workflows = conn.execute(
                "SELECT DISTINCT workflow_id FROM audit_events WHERE sequence <= 0"
            ).fetchall()
            for (workflow_id,) in workflows:
                rows = conn.execute(
                    """
                    SELECT event_id
                      FROM audit_events
                     WHERE workflow_id=?
                     ORDER BY recorded_at, rowid
                    """,
                    (workflow_id,),
                ).fetchall()
                for sequence, (event_id,) in enumerate(rows, start=1):
                    conn.execute(
                        "UPDATE audit_events SET sequence=? WHERE event_id=?",
                        (sequence, event_id),
                    )

    @classmethod
    def _assert_transition(cls, current_state: str, next_state: str) -> None:
        allowed = cls.ALLOWED_TRANSITIONS.get(current_state, set())
        if next_state not in allowed:
            raise ValueError(
                f"invalid workflow transition: {current_state} -> {next_state}"
            )

    def create_workflow(self, request_id: str, operation: str) -> str:
        workflow_id = f"wf:{uuid.uuid4()}"
        now = utc_now()
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO workflows
                    (workflow_id, request_id, operation, state,
                     created_at, updated_at, side_effects,
                     idempotency_key, request_fingerprint, result_json,
                     caller_subject, client_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    workflow_id,
                    request_id,
                    operation,
                    "validated",
                    now,
                    now,
                    0,
                    None,
                    None,
                    None,
                    None,
                    None,
                ),
            )
        return workflow_id

    def transition(self, workflow_id: str, state: str) -> None:
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT state FROM workflows WHERE workflow_id=?",
                (workflow_id,),
            ).fetchone()
            if row is None:
                raise ValueError(f"unknown workflow: {workflow_id}")

            current_state = row[0]
            self._assert_transition(current_state, state)
            conn.execute(
                "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
                (state, utc_now(), workflow_id),
            )

    def audit(
        self,
        workflow_id: str,
        event_type: str,
        actor: str,
        data: dict[str, Any],
    ) -> str:
        event_id = f"evt:{uuid.uuid4()}"
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT COALESCE(MAX(sequence),0)+1 FROM audit_events WHERE workflow_id=?",
                (workflow_id,),
            ).fetchone()
            sequence = int(row[0])
            conn.execute(
                """
                INSERT INTO audit_events
                    (event_id, workflow_id, sequence, event_type,
                     recorded_at, actor, data_json)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    event_id,
                    workflow_id,
                    sequence,
                    event_type,
                    utc_now(),
                    actor,
                    canonical_json(data),
                ),
            )
        return event_id

    def record_request_diagnostic(
        self,
        outcome: str,
        request_id: Any = None,
        operation: Any = None,
        caller_subject: Any = None,
        client_id: Any = None,
        detail: Any = None,
    ) -> str:
        diagnostic_id = f"diag:{uuid.uuid4()}"

        def bounded(value: Any, limit: int = 500) -> str | None:
            if value is None:
                return None
            return str(value)[:limit]

        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO request_diagnostics
                    (diagnostic_id, recorded_at, outcome, request_id,
                     operation, caller_subject, client_id, detail)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    diagnostic_id,
                    utc_now(),
                    bounded(outcome, 80),
                    bounded(request_id, 160),
                    bounded(operation, 160),
                    bounded(caller_subject, 160),
                    bounded(client_id, 160),
                    bounded(detail, 500),
                ),
            )
        return diagnostic_id

    @staticmethod
    def request_fingerprint(request: dict[str, Any]) -> str:
        semantic_request = {
            "contract_version": request["contract_version"],
            "operation": request["operation"],
            "caller": request["caller"],
            "client": request["client"],
            "input": request["input"],
        }
        return hashlib.sha256(
            canonical_json(semantic_request).encode("utf-8")
        ).hexdigest()

    def begin_external_operation(
        self,
        request: dict[str, Any],
        descriptor: dict[str, Any],
        authorization_policy: str,
        authorization_reason: str,
        validate_contract: Callable[[str, Any], None],
    ) -> tuple[dict[str, Any], bool]:
        request_id = request["request_id"]
        operation = request["operation"]
        fingerprint = self.request_fingerprint(request)
        idempotency_key = request.get("idempotency_key")
        caller_subject = request["caller"]["subject"]
        client_id = request["client"]["id"]

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN IMMEDIATE")

            if idempotency_key is not None:
                existing = conn.execute(
                    """
                    SELECT request_fingerprint, result_json
                      FROM workflows
                     WHERE client_id=?
                       AND caller_subject=?
                       AND idempotency_key=?
                     ORDER BY rowid DESC
                     LIMIT 1
                    """,
                    (client_id, caller_subject, idempotency_key),
                ).fetchone()
                if existing is not None:
                    if (
                        existing["request_fingerprint"] == fingerprint
                        and existing["result_json"]
                    ):
                        return json.loads(existing["result_json"]), True
                    raise ConflictError(
                        "idempotency key was already used for a different or "
                        "in-progress request"
                    )

            existing = conn.execute(
                """
                SELECT request_fingerprint, result_json
                  FROM workflows
                 WHERE client_id=?
                   AND caller_subject=?
                   AND request_id=?
                 ORDER BY rowid DESC
                 LIMIT 1
                """,
                (client_id, caller_subject, request_id),
            ).fetchone()
            if existing is not None:
                if (
                    existing["request_fingerprint"] == fingerprint
                    and existing["result_json"]
                ):
                    return json.loads(existing["result_json"]), True
                raise ConflictError(
                    "request_id was already used for a different or "
                    "in-progress request"
                )

            workflow_id = f"wf:{uuid.uuid4()}"
            decision_id = f"authz:{uuid.uuid4()}"
            receipt_id = f"rcpt:{uuid.uuid4()}"
            created_at = utc_now()

            conn.execute(
                """
                INSERT INTO workflows
                    (workflow_id, request_id, operation, state,
                     created_at, updated_at, side_effects,
                     idempotency_key, request_fingerprint, result_json,
                     caller_subject, client_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    workflow_id,
                    request_id,
                    operation,
                    "validated",
                    created_at,
                    created_at,
                    0,
                    idempotency_key,
                    fingerprint,
                    None,
                    caller_subject,
                    client_id,
                ),
            )

            decision_record = {
                "decision_id": decision_id,
                "request_id": request_id,
                "operation": operation,
                "decision": "allow",
                "decided_at": utc_now(),
                "policy": authorization_policy,
                "reason": authorization_reason,
            }
            validate_contract(
                "authorization-decision-v1.schema.json",
                decision_record,
            )
            conn.execute(
                """
                INSERT INTO authorization_decisions
                    (decision_id, workflow_id, request_id, operation,
                     decision, decided_at, policy, reason)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    decision_record["decision_id"],
                    workflow_id,
                    decision_record["request_id"],
                    decision_record["operation"],
                    decision_record["decision"],
                    decision_record["decided_at"],
                    decision_record["policy"],
                    decision_record["reason"],
                ),
            )

            self._assert_transition("validated", "authorized")
            conn.execute(
                "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
                ("authorized", utc_now(), workflow_id),
            )
            self._assert_transition("authorized", "accepted")
            conn.execute(
                "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
                ("accepted", utc_now(), workflow_id),
            )

            events = [
                (
                    1,
                    "civic.authorization.allowed",
                    "civic-orchestrator",
                    {
                        "decision_id": decision_id,
                        "policy": authorization_policy,
                        "side_effects": False,
                    },
                ),
                (
                    2,
                    "civic.operation.accepted",
                    caller_subject,
                    {
                        "operation": operation,
                        "client_id": request["client"]["id"],
                        "client_kind": request["client"]["kind"],
                        "authenticated_by": request["caller"]["authenticated_by"],
                        "side_effects": False,
                    },
                ),
                (
                    3,
                    "civic.service.selected",
                    "civic-orchestrator",
                    {
                        "service_capability": descriptor["service_capability"],
                        "implementation": descriptor["implementation"],
                        "effect_scope": descriptor["effect_scope"],
                        "side_effects": False,
                    },
                ),
            ]

            for sequence, event_type, actor, data in events:
                event_record = {
                    "event_id": f"evt:{uuid.uuid4()}",
                    "workflow_id": workflow_id,
                    "sequence": sequence,
                    "event_type": event_type,
                    "recorded_at": utc_now(),
                    "actor": actor,
                    "data": data,
                }
                validate_contract(
                    "audit-event-v1.schema.json",
                    event_record,
                )
                conn.execute(
                    """
                    INSERT INTO audit_events
                        (event_id, workflow_id, sequence, event_type,
                         recorded_at, actor, data_json)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        event_record["event_id"],
                        workflow_id,
                        sequence,
                        event_type,
                        event_record["recorded_at"],
                        actor,
                        canonical_json(data),
                    ),
                )

            return {
                "workflow_id": workflow_id,
                "receipt_id": receipt_id,
            }, False

    def finish_external_operation(
        self,
        request: dict[str, Any],
        descriptor: dict[str, Any],
        workflow_id: str,
        receipt_id: str,
        outcome: str,
        side_effects: bool,
        detail: dict[str, Any],
        validate_contract: Callable[[str, Any], None],
    ) -> dict[str, Any]:
        if outcome not in {"completed", "failed"}:
            raise ValueError(f"invalid external operation outcome: {outcome}")

        completed_at = utc_now()
        evidence = {
            "implementation": descriptor["implementation"],
            "service_capability": descriptor["service_capability"],
            "effect_scope": descriptor["effect_scope"],
            "side_effects": bool(side_effects),
            **detail,
        }

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT state FROM workflows WHERE workflow_id=?",
                (workflow_id,),
            ).fetchone()
            if row is None:
                raise ValueError(f"unknown workflow: {workflow_id}")

            self._assert_transition(row["state"], outcome)
            conn.execute(
                """
                UPDATE workflows
                   SET state=?, updated_at=?, side_effects=?
                 WHERE workflow_id=?
                """,
                (
                    outcome,
                    completed_at,
                    1 if side_effects else 0,
                    workflow_id,
                ),
            )

            sequence = int(
                conn.execute(
                    "SELECT COALESCE(MAX(sequence),0)+1 "
                    "FROM audit_events WHERE workflow_id=?",
                    (workflow_id,),
                ).fetchone()[0]
            )
            event_record = {
                "event_id": f"evt:{uuid.uuid4()}",
                "workflow_id": workflow_id,
                "sequence": sequence,
                "event_type": f"civic.operation.{outcome}",
                "recorded_at": utc_now(),
                "actor": "civic-orchestrator",
                "data": evidence,
            }
            validate_contract(
                "audit-event-v1.schema.json",
                event_record,
            )
            conn.execute(
                """
                INSERT INTO audit_events
                    (event_id, workflow_id, sequence, event_type,
                     recorded_at, actor, data_json)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    event_record["event_id"],
                    workflow_id,
                    sequence,
                    event_record["event_type"],
                    event_record["recorded_at"],
                    event_record["actor"],
                    canonical_json(evidence),
                ),
            )

            receipt_record = {
                "receipt_id": receipt_id,
                "workflow_id": workflow_id,
                "operation": request["operation"],
                "issued_at": utc_now(),
                "outcome": outcome,
                "side_effects": bool(side_effects),
                "evidence": evidence,
            }
            validate_contract(
                "receipt-v1.schema.json",
                receipt_record,
            )
            conn.execute(
                """
                INSERT INTO receipts
                    (receipt_id, workflow_id, operation, issued_at,
                     outcome, side_effects, evidence_json)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    receipt_id,
                    workflow_id,
                    request["operation"],
                    receipt_record["issued_at"],
                    outcome,
                    1 if side_effects else 0,
                    canonical_json(evidence),
                ),
            )

            result = {
                "contract_version": 1,
                "request_id": request["request_id"],
                "workflow_id": workflow_id,
                "operation": request["operation"],
                "status": outcome,
                "completed_at": completed_at,
                "side_effects": bool(side_effects),
                "result": evidence,
                "receipt_id": receipt_id,
            }
            validate_contract(
                "result-envelope-v1.schema.json",
                result,
            )
            conn.execute(
                "UPDATE workflows SET result_json=? WHERE workflow_id=?",
                (canonical_json(result), workflow_id),
            )

        return result

    def record_stub_operation(
        self,
        request: dict[str, Any],
        descriptor: dict[str, Any],
        authorization_policy: str,
        validate_contract: Callable[[str, Any], None],
    ) -> tuple[dict[str, Any], bool]:
        request_id = request["request_id"]
        operation = request["operation"]
        fingerprint = self.request_fingerprint(request)
        idempotency_key = request.get("idempotency_key")
        caller_subject = request["caller"]["subject"]
        client_id = request["client"]["id"]

        with self._connect() as conn:
            conn.row_factory = sqlite3.Row
            conn.execute("BEGIN IMMEDIATE")

            if idempotency_key is not None:
                existing = conn.execute(
                    """
                    SELECT request_fingerprint, result_json
                      FROM workflows
                     WHERE client_id=?
                       AND caller_subject=?
                       AND idempotency_key=?
                     ORDER BY rowid DESC
                     LIMIT 1
                    """,
                    (client_id, caller_subject, idempotency_key),
                ).fetchone()
                if existing is not None:
                    if (
                        existing["request_fingerprint"] == fingerprint
                        and existing["result_json"]
                    ):
                        return json.loads(existing["result_json"]), True
                    raise ConflictError(
                        "idempotency key was already used for a different request"
                    )

            existing = conn.execute(
                """
                SELECT request_fingerprint, result_json
                  FROM workflows
                 WHERE client_id=?
                   AND caller_subject=?
                   AND request_id=?
                 ORDER BY rowid DESC
                 LIMIT 1
                """,
                (client_id, caller_subject, request_id),
            ).fetchone()
            if existing is not None:
                if (
                    existing["request_fingerprint"] == fingerprint
                    and existing["result_json"]
                ):
                    return json.loads(existing["result_json"]), True
                raise ConflictError(
                    "request_id was already used for a different request"
                )

            workflow_id = f"wf:{uuid.uuid4()}"
            decision_id = f"authz:{uuid.uuid4()}"
            receipt_id = f"rcpt:{uuid.uuid4()}"

            created_at = utc_now()
            conn.execute(
                """
                INSERT INTO workflows
                    (workflow_id, request_id, operation, state,
                     created_at, updated_at, side_effects,
                     idempotency_key, request_fingerprint, result_json,
                     caller_subject, client_id)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    workflow_id,
                    request_id,
                    operation,
                    "validated",
                    created_at,
                    created_at,
                    0,
                    idempotency_key,
                    fingerprint,
                    None,
                    caller_subject,
                    client_id,
                ),
            )

            decided_at = utc_now()
            decision_record = {
                "decision_id": decision_id,
                "request_id": request_id,
                "operation": operation,
                "decision": "allow",
                "decided_at": decided_at,
                "policy": authorization_policy,
                "reason": (
                    "Phase 1H permits registered operations only as "
                    "non-side-effect stubs."
                ),
            }
            validate_contract(
                "authorization-decision-v1.schema.json",
                decision_record,
            )
            conn.execute(
                """
                INSERT INTO authorization_decisions
                    (decision_id, workflow_id, request_id, operation,
                     decision, decided_at, policy, reason)
                VALUES (?,?,?,?,?,?,?,?)
                """,
                (
                    decision_record["decision_id"],
                    workflow_id,
                    decision_record["request_id"],
                    decision_record["operation"],
                    decision_record["decision"],
                    decision_record["decided_at"],
                    decision_record["policy"],
                    decision_record["reason"],
                ),
            )

            self._assert_transition("validated", "authorized")
            conn.execute(
                "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
                ("authorized", utc_now(), workflow_id),
            )

            events = [
                (
                    1,
                    "civic.authorization.allowed",
                    "civic-orchestrator",
                    {
                        "decision_id": decision_id,
                        "policy": authorization_policy,
                        "side_effects": False,
                    },
                ),
            ]

            self._assert_transition("authorized", "accepted")
            conn.execute(
                "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
                ("accepted", utc_now(), workflow_id),
            )
            events.append(
                (
                    2,
                    "civic.operation.accepted",
                    request["caller"]["subject"],
                    {
                        "operation": operation,
                        "client_id": request["client"]["id"],
                        "client_kind": request["client"]["kind"],
                        "authenticated_by": request["caller"]["authenticated_by"],
                        "side_effects": False,
                    },
                )
            )
            events.append(
                (
                    3,
                    "civic.service.selected",
                    "civic-orchestrator",
                    {
                        "service_capability": descriptor["service_capability"],
                        "implementation": descriptor["implementation"],
                        "effect_scope": descriptor["effect_scope"],
                        "side_effects": False,
                    },
                )
            )

            self._assert_transition("accepted", "not-implemented")
            completed_at = utc_now()
            conn.execute(
                "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
                ("not-implemented", completed_at, workflow_id),
            )
            events.append(
                (
                    4,
                    "civic.operation.not-implemented",
                    "civic-orchestrator",
                    {
                        "service_capability": descriptor["service_capability"],
                        "side_effects": False,
                    },
                )
            )

            for sequence, event_type, actor, data in events:
                event_record = {
                    "event_id": f"evt:{uuid.uuid4()}",
                    "workflow_id": workflow_id,
                    "sequence": sequence,
                    "event_type": event_type,
                    "recorded_at": utc_now(),
                    "actor": actor,
                    "data": data,
                }
                validate_contract(
                    "audit-event-v1.schema.json",
                    event_record,
                )
                conn.execute(
                    """
                    INSERT INTO audit_events
                        (event_id, workflow_id, sequence, event_type,
                         recorded_at, actor, data_json)
                    VALUES (?,?,?,?,?,?,?)
                    """,
                    (
                        event_record["event_id"],
                        workflow_id,
                        sequence,
                        event_type,
                        event_record["recorded_at"],
                        actor,
                        canonical_json(data),
                    ),
                )

            receipt_evidence = {
                "implementation": "stub",
                "service_capability": descriptor["service_capability"],
                "effect_scope": descriptor["effect_scope"],
                "side_effects": False,
            }
            receipt_record = {
                "receipt_id": receipt_id,
                "workflow_id": workflow_id,
                "operation": operation,
                "issued_at": utc_now(),
                "outcome": "not-implemented",
                "side_effects": False,
                "evidence": receipt_evidence,
            }
            validate_contract(
                "receipt-v1.schema.json",
                receipt_record,
            )
            conn.execute(
                """
                INSERT INTO receipts
                    (receipt_id, workflow_id, operation, issued_at,
                     outcome, side_effects, evidence_json)
                VALUES (?,?,?,?,?,?,?)
                """,
                (
                    receipt_id,
                    workflow_id,
                    operation,
                    receipt_record["issued_at"],
                    "not-implemented",
                    0,
                    canonical_json(receipt_evidence),
                ),
            )

            result = {
                "contract_version": 1,
                "request_id": request_id,
                "workflow_id": workflow_id,
                "operation": operation,
                "status": "not-implemented",
                "completed_at": completed_at,
                "side_effects": False,
                "result": {
                    "implementation": "stub",
                    "service_capability": descriptor["service_capability"],
                    "effect_scope": descriptor["effect_scope"],
                    "message": (
                        "Phase 1H stub accepted the operation but performed "
                        "no backend action."
                    ),
                },
                "receipt_id": receipt_id,
            }
            validate_contract(
                "result-envelope-v1.schema.json",
                result,
            )
            conn.execute(
                "UPDATE workflows SET result_json=? WHERE workflow_id=?",
                (canonical_json(result), workflow_id),
            )

            return result, False

    def get_workflow_evidence(
        self,
        workflow_id: str,
    ) -> dict[str, Any] | None:
        with self._connect() as conn:
            conn.row_factory = sqlite3.Row

            workflow = conn.execute(
                """
                SELECT workflow_id, request_id, operation, state,
                       created_at, updated_at, side_effects
                  FROM workflows
                 WHERE workflow_id=?
                """,
                (workflow_id,),
            ).fetchone()
            if workflow is None:
                return None

            decisions = conn.execute(
                """
                SELECT decision_id, request_id, operation, decision,
                       decided_at, policy, reason
                  FROM authorization_decisions
                 WHERE workflow_id=?
                 ORDER BY decided_at, decision_id
                """,
                (workflow_id,),
            ).fetchall()

            events = conn.execute(
                """
                SELECT event_id, workflow_id, sequence, event_type,
                       recorded_at, actor, data_json
                  FROM audit_events
                 WHERE workflow_id=?
                 ORDER BY sequence
                """,
                (workflow_id,),
            ).fetchall()

            receipts = conn.execute(
                """
                SELECT receipt_id, workflow_id, operation, issued_at,
                       outcome, side_effects, evidence_json
                  FROM receipts
                 WHERE workflow_id=?
                 ORDER BY issued_at, receipt_id
                """,
                (workflow_id,),
            ).fetchall()

        workflow_obj = {
            "workflow_id": workflow["workflow_id"],
            "request_id": workflow["request_id"],
            "operation": workflow["operation"],
            "state": workflow["state"],
            "created_at": workflow["created_at"],
            "updated_at": workflow["updated_at"],
            "side_effects": bool(workflow["side_effects"]),
        }

        decision_objs = []
        for row in decisions:
            item = {
                "decision_id": row["decision_id"],
                "request_id": row["request_id"],
                "operation": row["operation"],
                "decision": row["decision"],
                "decided_at": row["decided_at"],
                "policy": row["policy"],
            }
            if row["reason"] is not None:
                item["reason"] = row["reason"]
            decision_objs.append(item)

        event_objs = [
            {
                "event_id": row["event_id"],
                "workflow_id": row["workflow_id"],
                "sequence": row["sequence"],
                "event_type": row["event_type"],
                "recorded_at": row["recorded_at"],
                "actor": row["actor"],
                "data": json.loads(row["data_json"]),
            }
            for row in events
        ]

        receipt_objs = [
            {
                "receipt_id": row["receipt_id"],
                "workflow_id": row["workflow_id"],
                "operation": row["operation"],
                "issued_at": row["issued_at"],
                "outcome": row["outcome"],
                "side_effects": bool(row["side_effects"]),
                "evidence": json.loads(row["evidence_json"]),
            }
            for row in receipts
        ]

        return {
            "contract_version": 1,
            "workflow": workflow_obj,
            "authorization_decisions": decision_objs,
            "audit_events": event_objs,
            "receipts": receipt_objs,
            "side_effects": bool(workflow["side_effects"]),
        }


class CivicOrchestrator:
    def __init__(
        self,
        paths: RuntimePaths,
        publication_client: Any | None = None,
    ) -> None:
        self.contracts = ContractStore(paths.repo_root)
        self.registry = OperationRegistry(
            paths.repo_root / "contracts" / "operation-registry-v1.yaml",
            self.contracts,
        )
        self.workflow = StubWorkflowDefinition(
            paths.repo_root / "workflows" / "stub-operation-v1.yaml",
            self.contracts,
        )

        for operation in self.registry.operations:
            if not self.workflow.accepts(operation):
                raise ValueError(
                    f"operation registry/workflow namespace drift: {operation}"
                )

        self.state = StateStore(paths.state_db)
        self.publication_client = publication_client

    def capabilities(self) -> dict[str, Any]:
        return {
            "contract_version": self.registry.contract_version,
            "capabilities": [
                {
                    "operation": item["operation"],
                    "implementation": item["implementation"],
                    "effect_scope": item["effect_scope"],
                }
                for item in self.registry.operations.values()
            ],
        }

    def health(self) -> dict[str, Any]:
        available = [
            item
            for item in self.registry.operations.values()
            if item["implementation"] == "available"
        ]
        return {
            "status": "ok",
            "phase": "2" if available else "1H",
            "side_effects": any(
                item["effect_scope"] != "none"
                for item in available
            ),
        }

    def submit(self, request: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        raw_request_id = request.get("request_id") if isinstance(request, dict) else None
        raw_operation = request.get("operation") if isinstance(request, dict) else None

        caller_subject = None
        client_id = None
        if isinstance(request, dict):
            caller = request.get("caller")
            client = request.get("client")
            if isinstance(caller, dict):
                caller_subject = caller.get("subject")
            if isinstance(client, dict):
                client_id = client.get("id")

        try:
            canonical_json(request)
            self.contracts.validate("request-envelope-v1.schema.json", request)
        except (TypeError, ValueError, ValidationError) as exc:
            self.state.record_request_diagnostic(
                "invalid-contract",
                raw_request_id,
                raw_operation,
                caller_subject,
                client_id,
                exc,
            )
            return 400, self.failure(
                request_id=raw_request_id,
                operation=raw_operation,
                failure_class="invalid-contract",
                message=str(exc),
                retryable=False,
            )

        operation = request["operation"]
        request_id = request["request_id"]

        if operation in self.registry.prohibited:
            self.state.record_request_diagnostic(
                "unauthorized",
                request_id,
                operation,
                caller_subject,
                client_id,
                "operation is explicitly prohibited",
            )
            return 403, self.failure(
                request_id,
                operation,
                "unauthorized",
                "operation is explicitly prohibited by the Civic contract",
                False,
            )

        descriptor = self.registry.lookup(operation)
        if descriptor is None or not self.workflow.accepts(operation):
            self.state.record_request_diagnostic(
                "unknown-operation",
                request_id,
                operation,
                caller_subject,
                client_id,
                "operation is not present in the bounded workflow registry",
            )
            return 400, self.failure(
                request_id,
                operation,
                "unknown-operation",
                "operation is not present in the bounded workflow registry",
                False,
            )

        if (
            operation == "publication.publish"
            and descriptor["implementation"] == "available"
        ):
            return self._submit_publication(
                request,
                descriptor,
                caller_subject,
                client_id,
            )

        try:
            result, replayed = self.state.record_stub_operation(
                request,
                descriptor,
                self.workflow.authorization_policy,
                self.contracts.validate,
            )
        except ConflictError as exc:
            self.state.record_request_diagnostic(
                "conflict",
                request_id,
                operation,
                caller_subject,
                client_id,
                exc,
            )
            return 409, self.failure(
                request_id,
                operation,
                "conflict",
                str(exc),
                False,
            )

        self.contracts.validate("result-envelope-v1.schema.json", result)
        if replayed:
            original_request_id = result["request_id"]
            result = dict(result)
            result["request_id"] = request_id
            result["result"] = dict(result["result"])
            result["result"]["replayed"] = True
            result["result"]["original_request_id"] = original_request_id
            self.state.record_request_diagnostic(
                "replay",
                request_id,
                operation,
                caller_subject,
                client_id,
                f"original_request_id={original_request_id}",
            )
            self.contracts.validate("result-envelope-v1.schema.json", result)

        return 200, result

    def _submit_publication(
        self,
        request: dict[str, Any],
        descriptor: dict[str, Any],
        caller_subject: str,
        client_id: str,
    ) -> tuple[int, dict[str, Any]]:
        request_id = request["request_id"]
        operation = request["operation"]

        try:
            self.contracts.validate(
                "publication-publish-input-v1.schema.json",
                request["input"],
            )
        except ValidationError as exc:
            self.state.record_request_diagnostic(
                "invalid-contract",
                request_id,
                operation,
                caller_subject,
                client_id,
                exc,
            )
            return 400, self.failure(
                request_id,
                operation,
                "invalid-contract",
                str(exc),
                False,
            )

        if self.publication_client is None:
            message = "publication service client is not configured"
            self.state.record_request_diagnostic(
                "backend-unavailable",
                request_id,
                operation,
                caller_subject,
                client_id,
                message,
            )
            return 500, self.failure(
                request_id,
                operation,
                "backend-unavailable",
                message,
                True,
            )

        try:
            start, replayed = self.state.begin_external_operation(
                request,
                descriptor,
                "publication-policy-v1",
                (
                    "Bounded publication operation accepted for the "
                    "configured publication service."
                ),
                self.contracts.validate,
            )
        except ConflictError as exc:
            self.state.record_request_diagnostic(
                "conflict",
                request_id,
                operation,
                caller_subject,
                client_id,
                exc,
            )
            return 409, self.failure(
                request_id,
                operation,
                "conflict",
                str(exc),
                False,
            )

        if replayed:
            original_request_id = start["request_id"]
            result = dict(start)
            result["request_id"] = request_id
            result["result"] = dict(result["result"])
            result["result"]["replayed"] = True
            result["result"]["original_request_id"] = original_request_id
            self.state.record_request_diagnostic(
                "replay",
                request_id,
                operation,
                caller_subject,
                client_id,
                f"original_request_id={original_request_id}",
            )
            self.contracts.validate(
                "result-envelope-v1.schema.json",
                result,
            )
            return 200, result

        workflow_id = start["workflow_id"]
        receipt_id = start["receipt_id"]

        try:
            service_result = self.publication_client.publish(
                workflow_id,
                request["input"]["artifact"],
            )
        except PublicationServiceFailure as exc:
            side_effects = exc.failure_class in {
                "publication-failed",
                "verification-failed",
            }
            result = self.state.finish_external_operation(
                request=request,
                descriptor=descriptor,
                workflow_id=workflow_id,
                receipt_id=receipt_id,
                outcome="failed",
                side_effects=side_effects,
                detail={
                    "failure_class": exc.failure_class,
                    "message": exc.message,
                    "retryable": exc.retryable,
                },
                validate_contract=self.contracts.validate,
            )
            return 200, result
        except PublicationServiceUnavailable as exc:
            result = self.state.finish_external_operation(
                request=request,
                descriptor=descriptor,
                workflow_id=workflow_id,
                receipt_id=receipt_id,
                outcome="failed",
                side_effects=True,
                detail={
                    "failure_class": "backend-unavailable",
                    "message": str(exc)[:1000],
                    "retryable": True,
                },
                validate_contract=self.contracts.validate,
            )
            return 200, result
        except PublicationServiceProtocolError as exc:
            result = self.state.finish_external_operation(
                request=request,
                descriptor=descriptor,
                workflow_id=workflow_id,
                receipt_id=receipt_id,
                outcome="failed",
                side_effects=True,
                detail={
                    "failure_class": "internal",
                    "message": str(exc)[:1000],
                    "retryable": False,
                },
                validate_contract=self.contracts.validate,
            )
            return 200, result
        except Exception as exc:
            result = self.state.finish_external_operation(
                request=request,
                descriptor=descriptor,
                workflow_id=workflow_id,
                receipt_id=receipt_id,
                outcome="failed",
                side_effects=True,
                detail={
                    "failure_class": "internal",
                    "message": (
                        f"unexpected publication adapter failure: {exc}"
                    )[:1000],
                    "retryable": False,
                },
                validate_contract=self.contracts.validate,
            )
            return 200, result

        result = self.state.finish_external_operation(
            request=request,
            descriptor=descriptor,
            workflow_id=workflow_id,
            receipt_id=receipt_id,
            outcome="completed",
            side_effects=True,
            detail={
                "sha256": service_result["sha256"],
                "size_bytes": service_result["size_bytes"],
                "cid": service_result["cid"],
                "pinned": service_result["pinned"],
                "verified": service_result["verified"],
            },
            validate_contract=self.contracts.validate,
        )
        return 200, result

    def workflow_evidence(
        self,
        workflow_id: str,
    ) -> tuple[int, dict[str, Any]]:
        evidence = self.state.get_workflow_evidence(workflow_id)
        if evidence is None:
            return 404, {
                "contract_version": 1,
                "workflow_id": workflow_id,
                "error": "workflow-not-found",
                "side_effects": False,
            }

        self.contracts.validate("workflow-evidence-v1.schema.json", evidence)
        return 200, evidence

    def failure(
        self,
        request_id: Any,
        operation: Any,
        failure_class: str,
        message: Any,
        retryable: bool,
    ) -> dict[str, Any]:
        normalized_request_id = (
            request_id
            if isinstance(request_id, str) and _ID_RE.fullmatch(request_id)
            else "invalid:request"
        )

        normalized_operation = (
            operation
            if isinstance(operation, str)
            and len(operation) <= 160
            and _OPERATION_RE.fullmatch(operation)
            else "audit.invalid_request"
        )

        normalized_message = str(message)[:1000]
        if not normalized_message:
            normalized_message = "request failed"

        failure = {
            "contract_version": 1,
            "request_id": normalized_request_id,
            "operation": normalized_operation,
            "failure_class": failure_class,
            "message": normalized_message,
            "retryable": bool(retryable),
            "side_effects": False,
        }
        self.contracts.validate("failure-envelope-v1.schema.json", failure)
        return failure
