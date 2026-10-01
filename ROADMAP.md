# Civic Orchestrator Roadmap

## Purpose

The roadmap deliberately starts with a contract-only orchestrator and designs service/trust nodes only after the calling and capability boundaries are explicit.

The sequence is intended to prevent two failure modes:

- rebuilding backend logic independently in Usermin, Hubzilla, Kane Fabric, Gitea, or later interfaces;
- creating one infrastructure node per technology without a justified trust, state, or availability boundary.

## Phase 0 — Repository and architecture reset

**Status:** active baseline.

Deliverables:

- repository purpose and authority;
- top-level architecture;
- standards/protocol decision;
- capability boundary;
- node-design gates;
- portability and independent-operator rules;
- non-monetary cryptographic trust boundary;
- portable reference topology;
- no production side effects.

Acceptance:

- this repository can explain what the orchestrator is and is not without relying on implementation code;
- every future service must enter through a named capability and contract;
- the architecture can be described without assuming Kane County private infrastructure;
- no cryptographic mechanism is required to carry monetary or transferable token semantics.

## Phase 1 — Contract-bearing orchestrator skeleton

Build CT105 as a deliberately limited service that can validate and route requests but cannot yet perform production civic actions.

### 1.1 Contract set

Define versioned schemas for:

- request envelope;
- result envelope;
- error/failure envelope;
- caller/interface identity;
- operation descriptor;
- authorization decision;
- workflow instance and transition;
- audit event;
- receipt;
- service capability advertisement.

### 1.2 Interface standards

Initial baseline:

- HTTP for synchronous service calls;
- OpenAPI 3.1 for callable interface description;
- JSON Schema 2020-12 for payload validation;
- CloudEvents 1.0 for asynchronous event envelopes;
- JSON as the default human-inspectable representation.

No custom wire protocol is introduced.

### 1.3 Stub capability namespaces

Create fail-closed stubs for at least:

- `publication.*`
- `geography.*`
- `participant.*`
- `repository.*`
- `rag.*`
- `inference.*`
- `edge.*`
- `firmware.*`
- `signing.*`
- `audit.*`

Each stub must accept only schema-valid operations and return an explicit non-side-effect result.

### 1.4 Workflow core

Implement the minimum deterministic workflow state machine needed to prove:

- request accepted or rejected;
- authorization decision recorded;
- state transition validated;
- service adapter selected;
- stub invoked;
- event/audit record emitted;
- receipt/result returned.

Do not introduce arbitrary command execution.

### Phase 1 acceptance

A Usermin command, Hubzilla test client, and Kane Fabric development client can submit equivalent test operations and receive equivalent contract-valid responses without any backend side effect.

---

## Phase 2 — Service and trust node architecture

Do not begin broad backend integration until Phase 1 contracts are stable enough to reveal actual capability boundaries.

Inventory each required service using the node-design gates in `docs/NODE_DESIGN_GATES.md`.

For every capability determine:

- state owner;
- trust level;
- secret/private-key ownership;
- network exposure;
- availability requirement;
- storage requirement;
- recovery model;
- whether co-location is permitted;
- exact orchestrator-facing interface.

Expected service classes include:

- Kane Fabric geographic authority/runtime;
- administrative/browser secure origin and Wiregate;
- IPFS/Kubo publication service;
- Gitea source/revision authority;
- RAG state/retrieval/index service;
- inference service on `annales`;
- firmware signing authority;
- ESP32-S3 management/synchronization service;
- future replicated/distribution services.

### Phase 2 acceptance

Every additional node exists because of an explicit trust, state, network, failure-domain, or lifecycle requirement—not because a technology normally runs on its own server.

---

## Phase 3 — Interaction adapters

Connect human-facing and service-facing surfaces to the stable orchestrator contracts.

### Usermin

Provide bounded CLI/TUI operations suitable for shell and curses-style forms. Unix identity, home directory, mailbox, quota, and local preferences remain Portal responsibilities.

### Hubzilla

Provide a thin addon/client for authenticated operation requests, workflow/status display, returned CIDs/receipts/results, and selected Civic actions. Hubzilla remains the discussion/channel surface.

### Kane Fabric

Integrate orchestrated operations around the existing browser-native verification, map composition, administrative descriptors, participant publications, and interaction model. Do not move browser-native verification/rendering into CT105.

### Gitea

Integrate exact repo/commit/path artifact references and controlled callbacks/events while preserving Gitea as editable source/revision truth.

### Phase 3 acceptance

The same operation semantics are available through multiple interfaces without duplicating backend workflow logic.

---

## Phase 4 — First real side-effect service

Choose one narrowly bounded service adapter as the first production capability.

The preferred candidate is publication because its authority can be tightly expressed:

```text
exact approved bytes
  -> content identity
  -> publish/pin
  -> verify
  -> receipt
```

Requirements:

- exact input identity;
- explicit authorization;
- deterministic result contract;
- idempotency;
- audit record;
- backend isolation;
- fail-closed verification.

No second production capability is enabled until the first demonstrates the complete end-to-end control pattern.

---

## Phase 5 — Kane Fabric geographic orchestration

Connect existing Kane Fabric candidate/comparison/reconciliation/promotion/compilation operations behind Civic semantic capabilities.

Representative operations:

- `geography.acquire_candidate`
- `geography.compare_candidate`
- `geography.request_promotion`
- `geography.promote`
- `geography.compile_publication`
- `geography.publish`

The orchestrator coordinates state and authority; Kane Fabric remains the geographic domain authority.

Acceptance requires preservation of Kane Fabric provenance, explicit promotion, durable geographic identity, and deterministic publication behavior.

---

## Phase 6 — RAG and inference orchestration

Connect:

- stateful corpus/index/vector/SQL/retrieval services;
- policy/context selection;
- essentially stateless inference on `annales`;
- result provenance and audit.

Usermin, Hubzilla, Kane Fabric, and later clients must use the same orchestration path instead of implementing separate retrieval pipelines.

---

## Phase 7 — ESP32-S3 lifecycle and signing

Treat publication custody and firmware trust as separate planes.

The orchestrator may coordinate:

- device/edge enrollment;
- artifact synchronization;
- firmware candidate selection;
- signing requests;
- signed release manifests;
- update authorization;
- rollout status;
- recovery/replacement workflows.

The orchestrator must not hold the firmware signing private key.

The signing authority must independently validate enough request context to reject unauthorized signing even if CT105 is compromised.

---

## Phase 8 — Durable workflows

Only after real long-running workflows exist, evaluate whether the small built-in state machine remains sufficient.

Candidates may include a mature durable workflow engine, but adoption is conditional on:

- preserving Civic operation semantics;
- keeping external contracts stable;
- avoiding a backend job model becoming the Civic domain model;
- operational cost justified by measured workflow complexity.

Rundeck-class tooling may be used behind adapters for infrastructure execution. Temporal-class tooling may be considered for long-lived durable workflows. Neither is an initial architectural dependency.

---

## Phase 9 — Conformance, replication, appliance bootstrap, and operator portability

Complete:

- contract conformance suites;
- independent-client tests;
- service-adapter tests;
- replay/idempotency tests;
- audit/receipt verification;
- backup/restore gates;
- node replacement tests;
- independent operator implementation guidance;
- second-jurisdiction conformance exercise using public contracts alone;
- bootstrap manifest/trust-root model suitable for later appliance deployment;
- network-bootstrap/reprovisioning proof when the appliance workstream becomes active;
- multi-node distribution where required.

The end state is a Civic Infrastructure control plane whose contracts survive replacement of individual applications, hosts, devices, or service implementations.
