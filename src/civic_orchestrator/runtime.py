from __future__ import annotations

import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import yaml
from jsonschema import Draft202012Validator, RefResolver, ValidationError


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


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
        for path in self.schemas_dir.glob("*.schema.json"):
            schema = json.loads(path.read_text(encoding="utf-8"))
            self._schemas[path.name] = schema

        store: dict[str, Any] = {}
        for name, schema in self._schemas.items():
            store[name] = schema
            if "$id" in schema:
                store[schema["$id"]] = schema

        for name, schema in self._schemas.items():
            resolver = RefResolver.from_schema(schema, store=store)
            self._validators[name] = Draft202012Validator(schema, resolver=resolver)

    def validate(self, schema_name: str, instance: Any) -> None:
        validator = self._validators[schema_name]
        errors = sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
        if errors:
            err = errors[0]
            path = ".".join(str(p) for p in err.absolute_path) or "$"
            raise ValidationError(f"{path}: {err.message}")


class OperationRegistry:
    def __init__(self, path: Path) -> None:
        raw = yaml.safe_load(path.read_text(encoding="utf-8"))
        self.contract_version = raw["contract_version"]
        self.operations = {item["operation"]: item for item in raw["operations"]}
        self.prohibited = set(raw.get("prohibited_generic_operations", []))

    def lookup(self, operation: str) -> dict[str, Any] | None:
        return self.operations.get(operation)


class StateStore:
    def __init__(self, db_path: Path) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA foreign_keys=ON")
        self._init_schema()

    def _init_schema(self) -> None:
        self.conn.executescript(
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
            """
        )
        self.conn.commit()

    def create_workflow(self, request_id: str, operation: str) -> str:
        workflow_id = f"wf:{uuid.uuid4()}"
        now = utc_now()
        self.conn.execute(
            "INSERT INTO workflows VALUES (?,?,?,?,?,?,?)",
            (workflow_id, request_id, operation, "accepted", now, now, 0),
        )
        self.conn.commit()
        return workflow_id

    def transition(self, workflow_id: str, state: str) -> None:
        self.conn.execute(
            "UPDATE workflows SET state=?, updated_at=? WHERE workflow_id=?",
            (state, utc_now(), workflow_id),
        )
        self.conn.commit()

    def audit(self, workflow_id: str, event_type: str, actor: str, data: dict[str, Any]) -> str:
        event_id = f"evt:{uuid.uuid4()}"
        self.conn.execute(
            "INSERT INTO audit_events VALUES (?,?,?,?,?,?)",
            (event_id, workflow_id, event_type, utc_now(), actor, json.dumps(data, sort_keys=True)),
        )
        self.conn.commit()
        return event_id

    def receipt(self, workflow_id: str, operation: str, outcome: str, evidence: dict[str, Any]) -> str:
        receipt_id = f"rcpt:{uuid.uuid4()}"
        self.conn.execute(
            "INSERT INTO receipts VALUES (?,?,?,?,?,?,?)",
            (receipt_id, workflow_id, operation, utc_now(), outcome, 0, json.dumps(evidence, sort_keys=True)),
        )
        self.conn.commit()
        return receipt_id


class CivicOrchestrator:
    def __init__(self, paths: RuntimePaths) -> None:
        self.contracts = ContractStore(paths.repo_root)
        self.registry = OperationRegistry(paths.repo_root / "contracts" / "operation-registry-v1.yaml")
        self.state = StateStore(paths.state_db)

    def capabilities(self) -> dict[str, Any]:
        return {
            "contract_version": self.registry.contract_version,
            "capabilities": [
                {
                    "operation": item["operation"],
                    "implementation": item["implementation"],
                }
                for item in self.registry.operations.values()
            ],
        }

    def submit(self, request: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        request_id = str(request.get("request_id", "invalid:request"))
        operation = str(request.get("operation", "audit.invalid_request"))

        try:
            self.contracts.validate("request-envelope-v1.schema.json", request)
        except ValidationError as exc:
            return 400, self._failure(
                request_id=request_id,
                operation=operation if "." in operation else "audit.invalid_request",
                failure_class="invalid-contract",
                message=str(exc),
                retryable=False,
            )

        operation = request["operation"]
        request_id = request["request_id"]

        if operation in self.registry.prohibited:
            return 403, self._failure(
                request_id, operation, "unauthorized",
                "operation is explicitly prohibited by the Civic contract", False,
            )

        descriptor = self.registry.lookup(operation)
        if descriptor is None:
            return 400, self._failure(
                request_id, operation, "unknown-operation",
                "operation is not present in the bounded operation registry", False,
            )

        workflow_id = self.state.create_workflow(request_id, operation)
        actor = request["caller"]["subject"]
        self.state.audit(
            workflow_id,
            "civic.operation.accepted",
            actor,
            {"operation": operation, "interface": request["interface"], "side_effects": False},
        )

        self.state.transition(workflow_id, "not-implemented")
        self.state.audit(
            workflow_id,
            "civic.operation.not-implemented",
            "civic-orchestrator",
            {"service_capability": descriptor["service_capability"], "side_effects": False},
        )
        receipt_id = self.state.receipt(
            workflow_id,
            operation,
            "not-implemented",
            {
                "implementation": "stub",
                "service_capability": descriptor["service_capability"],
                "side_effects": False,
            },
        )

        result = {
            "contract_version": 1,
            "request_id": request_id,
            "workflow_id": workflow_id,
            "operation": operation,
            "status": "not-implemented",
            "completed_at": utc_now(),
            "side_effects": False,
            "result": {
                "implementation": "stub",
                "service_capability": descriptor["service_capability"],
                "message": "Phase 1 stub accepted the operation but performed no backend action.",
            },
            "receipt_id": receipt_id,
        }
        self.contracts.validate("result-envelope-v1.schema.json", result)
        return 200, result

    def _failure(
        self,
        request_id: str,
        operation: str,
        failure_class: str,
        message: str,
        retryable: bool,
    ) -> dict[str, Any]:
        failure = {
            "contract_version": 1,
            "request_id": request_id,
            "operation": operation,
            "failure_class": failure_class,
            "message": message,
            "retryable": retryable,
            "side_effects": False,
        }
        # Invalid input can carry an operation that cannot itself validate against
        # the normal operation vocabulary. In those cases we still fail closed.
        try:
            self.contracts.validate("failure-envelope-v1.schema.json", failure)
        except ValidationError:
            failure["operation"] = "audit.invalid_request"
        return failure
