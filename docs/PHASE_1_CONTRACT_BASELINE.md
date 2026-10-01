# Phase 1 Contract Baseline

## Status

Phase 1 is active. This baseline defines contracts only. No production backend side effects are permitted.

## Current artifacts

### Schemas

- `common-v1.schema.json`
- `caller-identity-v1.schema.json`
- `request-envelope-v1.schema.json`
- `result-envelope-v1.schema.json`
- `failure-envelope-v1.schema.json`
- `operation-descriptor-v1.schema.json`
- `authorization-decision-v1.schema.json`
- `workflow-v1.schema.json`
- `audit-event-v1.schema.json`
- `receipt-v1.schema.json`
- `service-capability-v1.schema.json`

### API

- `openapi/civic-orchestrator-v1.yaml`

### Workflow

- `workflows/stub-operation-v1.yaml`

### Registry

- `contracts/operation-registry-v1.yaml`

## Phase 1 invariants

Until explicitly advanced by a later acceptance gate:

- every registered operation reports `implementation: stub`;
- no backend network request is permitted;
- no production publication is permitted;
- no geographic promotion is permitted;
- no firmware update is permitted;
- no signing request reaches a signer;
- no RAG or inference backend is invoked;
- arbitrary command execution is prohibited;
- every accepted request must terminate with a contract-valid fail-closed result;
- the same operation semantics must remain independent of Usermin, Hubzilla, Kane Fabric, Gitea, or another caller surface.

## Next implementation gate

The first CT105 daemon may:

1. load the operation registry;
2. validate request envelopes;
3. reject unknown/prohibited operations;
4. create workflow identifiers;
5. execute the stub workflow only;
6. record local audit state;
7. return a result/failure envelope.

It may not yet contain real service adapters.
