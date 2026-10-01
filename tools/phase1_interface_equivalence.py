#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.request


INTERFACES = ("usermin", "hubzilla", "kane-fabric")
EXPECTED_EVENTS = (
    "civic.authorization.allowed",
    "civic.operation.accepted",
    "civic.service.selected",
    "civic.operation.not-implemented",
)


def request_json(method: str, url: str, payload: dict | None = None) -> dict:
    body = None
    headers = {}
    if payload is not None:
        body = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=body, headers=headers, method=method)
    with urllib.request.urlopen(req, timeout=5) as response:
        return json.loads(response.read().decode("utf-8"))


def semantic_result(result: dict, evidence: dict) -> dict:
    return {
        "operation": result["operation"],
        "status": result["status"],
        "side_effects": result["side_effects"],
        "implementation": result["result"]["implementation"],
        "service_capability": result["result"]["service_capability"],
        "authorization_decision": evidence["authorization_decisions"][0]["decision"],
        "authorization_policy": evidence["authorization_decisions"][0]["policy"],
        "audit_event_types": [item["event_type"] for item in evidence["audit_events"]],
        "receipt_outcome": evidence["receipts"][0]["outcome"],
        "receipt_side_effects": evidence["receipts"][0]["side_effects"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8045")
    args = parser.parse_args()

    semantic = {}
    observations = {}

    for interface in INTERFACES:
        payload = {
            "contract_version": 1,
            "request_id": f"req:equivalence-{interface}",
            "operation": "publication.publish",
            "caller": {
                "subject": f"participant:equivalence-{interface}",
                "authority": "phase1-equivalence",
            },
            "interface": interface,
            "submitted_at": "2026-10-01T08:00:00Z",
            "input": {
                "fixture": "phase1-interface-equivalence",
            },
        }

        result = request_json(
            "POST",
            f"{args.base_url}/v1/operations",
            payload,
        )
        evidence = request_json(
            "GET",
            f"{args.base_url}/v1/workflows/{result['workflow_id']}",
        )

        event_types = [item["event_type"] for item in evidence["audit_events"]]
        if tuple(event_types) != EXPECTED_EVENTS:
            raise RuntimeError(
                f"{interface}: unexpected event sequence: {event_types}"
            )

        accepted = next(
            item
            for item in evidence["audit_events"]
            if item["event_type"] == "civic.operation.accepted"
        )
        if accepted["data"]["interface"] != interface:
            raise RuntimeError(
                f"{interface}: interface evidence mismatch: "
                f"{accepted['data']['interface']}"
            )

        semantic[interface] = semantic_result(result, evidence)
        observations[interface] = {
            "request_id": result["request_id"],
            "workflow_id": result["workflow_id"],
            "receipt_id": result["receipt_id"],
            "semantic": semantic[interface],
        }

    baseline = semantic[INTERFACES[0]]
    for interface in INTERFACES[1:]:
        if semantic[interface] != baseline:
            raise RuntimeError(
                f"semantic mismatch: {INTERFACES[0]} != {interface}\n"
                + json.dumps(
                    {
                        INTERFACES[0]: baseline,
                        interface: semantic[interface],
                    },
                    indent=2,
                    sort_keys=True,
                )
            )

    print(json.dumps({
        "status": "pass",
        "interfaces": observations,
        "equivalent_semantics": baseline,
    }, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (urllib.error.URLError, KeyError, IndexError, RuntimeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(1)
