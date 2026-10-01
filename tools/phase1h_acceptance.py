#!/usr/bin/env python3
from __future__ import annotations

import argparse
import http.client
import json
import sqlite3
import urllib.error
import urllib.parse
import urllib.request
import uuid


def request_json(method: str, url: str, payload: dict | None = None):
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return exc.code, json.loads(exc.read().decode("utf-8"))


def raw_post(host: str, port: int, path: str, body: bytes):
    conn = http.client.HTTPConnection(host, port, timeout=5)
    conn.request(
        "POST",
        path,
        body=body,
        headers={
            "Content-Type": "application/json",
            "Content-Length": str(len(body)),
        },
    )
    response = conn.getresponse()
    payload = json.loads(response.read().decode("utf-8"))
    status = response.status
    conn.close()
    return status, payload


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RuntimeError(message)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8045")
    parser.add_argument(
        "--state-db",
        default="/var/lib/civic-orchestrator/state/orchestrator.sqlite3",
    )
    args = parser.parse_args()

    parsed = urllib.parse.urlparse(args.base_url)
    host = parsed.hostname or "127.0.0.1"
    port = parsed.port or 80

    report = {}

    status, health = request_json("GET", f"{args.base_url}/healthz")
    require(status == 200, f"health status {status}")
    require(health.get("side_effects") is False, "health side_effects not false")
    report["health"] = health

    token = uuid.uuid4().hex[:12]
    request_id = f"req:phase1h-{token}"
    idempotency_key = f"idem:phase1h-{token}"

    payload = {
        "contract_version": 1,
        "request_id": request_id,
        "operation": "publication.publish",
        "caller": {
            "subject": "participant:phase1h",
            "authority": "phase1h-acceptance",
            "authenticated_by": "phase1h-local-auth",
        },
        "client": {
            "id": "phase1h-acceptance",
            "kind": "test",
        },
        "submitted_at": "2026-10-01T08:30:00Z",
        "idempotency_key": idempotency_key,
        "input": {
            "fixture": "phase1h-hardening",
        },
    }

    status, first = request_json(
        "POST",
        f"{args.base_url}/v1/operations",
        payload,
    )
    require(status == 200, f"first submit status {status}")
    require(first.get("side_effects") is False, "first submit side effects")
    report["first_submit"] = {
        "workflow_id": first["workflow_id"],
        "receipt_id": first["receipt_id"],
        "status": first["status"],
    }

    status, evidence = request_json(
        "GET",
        f"{args.base_url}/v1/workflows/{first['workflow_id']}",
    )
    require(status == 200, f"evidence status {status}")
    sequences = [item["sequence"] for item in evidence["audit_events"]]
    require(sequences == [1, 2, 3, 4], f"audit sequences {sequences}")
    accepted = evidence["audit_events"][1]
    require(
        accepted["data"]["client_id"] == "phase1h-acceptance",
        "client identity missing from evidence",
    )
    require(
        accepted["data"]["authenticated_by"] == "phase1h-local-auth",
        "authentication provenance missing from evidence",
    )
    report["evidence"] = {
        "audit_sequences": sequences,
        "authorization_policy": evidence["authorization_decisions"][0]["policy"],
        "client_id": accepted["data"]["client_id"],
        "authenticated_by": accepted["data"]["authenticated_by"],
    }

    retry = dict(payload)
    retry["request_id"] = f"{request_id}-retry"
    retry["submitted_at"] = "2026-10-01T08:31:00Z"
    status, replay = request_json(
        "POST",
        f"{args.base_url}/v1/operations",
        retry,
    )
    require(status == 200, f"replay status {status}")
    require(replay["workflow_id"] == first["workflow_id"], "replay workflow changed")
    require(replay["receipt_id"] == first["receipt_id"], "replay receipt changed")
    require(replay["result"].get("replayed") is True, "replay marker missing")
    report["replay"] = "pass"

    conflict = dict(retry)
    conflict["request_id"] = f"{request_id}-conflict"
    conflict["input"] = {"fixture": "different"}
    status, conflict_result = request_json(
        "POST",
        f"{args.base_url}/v1/operations",
        conflict,
    )
    require(status == 409, f"conflict status {status}")
    require(
        conflict_result.get("failure_class") == "conflict",
        "conflict failure envelope missing",
    )
    report["conflicting_replay"] = "pass"

    invalid_time = dict(payload)
    invalid_time["request_id"] = f"{request_id}-bad-time"
    invalid_time.pop("idempotency_key", None)
    invalid_time["submitted_at"] = "yesterday"
    status, invalid_result = request_json(
        "POST",
        f"{args.base_url}/v1/operations",
        invalid_time,
    )
    require(status == 400, f"invalid timestamp status {status}")
    require(
        invalid_result.get("failure_class") == "invalid-contract",
        "invalid timestamp not rejected by contract",
    )
    report["timestamp_validation"] = "pass"

    status, malformed = raw_post(
        host,
        port,
        "/v1/operations",
        b"{not-json",
    )
    require(status == 400, f"malformed JSON status {status}")
    require(
        malformed.get("failure_class") == "invalid-contract",
        "malformed JSON did not return failure envelope",
    )
    require(malformed.get("side_effects") is False, "malformed JSON side effects")
    report["http_failure_envelope"] = "pass"

    db_uri = f"file:{args.state_db}?mode=ro"
    with sqlite3.connect(db_uri, uri=True) as conn:
        unsequenced = conn.execute(
            "SELECT COUNT(*) FROM audit_events WHERE sequence <= 0"
        ).fetchone()[0]
    require(unsequenced == 0, f"{unsequenced} unsequenced legacy audit events")
    report["legacy_audit_backfill"] = "pass"

    print(json.dumps({
        "status": "pass",
        "phase": "1H",
        "checks": report,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (KeyError, RuntimeError, urllib.error.URLError) as exc:
        print(f"FAIL: {exc}")
        raise SystemExit(1)
