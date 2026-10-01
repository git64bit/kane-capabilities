# Phase 1 Interface Equivalence Gate

## Purpose

Phase 1 requires the same Civic operation semantics to survive changes in caller surface.

This gate uses a development acceptance harness, not production adapters. It submits the same bounded `publication.publish` operation with the three Phase 1 interface identities:

- `usermin`
- `hubzilla`
- `kane-fabric`

The harness deliberately ignores values that must differ between independent requests:

- request IDs;
- workflow IDs;
- receipt IDs;
- timestamps;
- caller subjects;
- the recorded interface identity.

It compares the Civic semantics that must remain equivalent:

- operation;
- result status;
- side-effect flag;
- selected implementation;
- selected service capability;
- authorization decision;
- authorization policy;
- ordered audit-event types;
- receipt outcome;
- receipt side-effect flag.

## Boundary

This gate does not claim that production Usermin, Hubzilla, or Kane Fabric adapters exist.

It proves that the Phase 1 orchestrator contract treats those caller surfaces equivalently while retaining the interface identity in audit evidence.

Production interaction adapters remain Phase 3 work.

## Run

On CT105:

```bash
cd /opt/civic-orchestrator/current
/opt/civic-orchestrator/venv/bin/python \
  tools/phase1_interface_equivalence.py \
  --base-url http://127.0.0.1:8045
```

Acceptance requires:

```text
status = pass
interfaces = usermin, hubzilla, kane-fabric
all semantic comparison fields identical
side_effects = false
implementation = stub
authorization_policy = stub-policy
```
