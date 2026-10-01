# Civic Orchestrator Roadmap

## Purpose

The roadmap deliberately starts with a contract-only orchestrator and designs service/trust nodes only after the calling and capability boundaries are explicit.

The sequence is intended to prevent two failure modes:

- rebuilding backend logic independently in Usermin, Hubzilla, Kane Fabric, Gitea, or later interfaces;
- creating one infrastructure node per technology without a justified trust, state, or availability boundary.

## Phase 0 — Repository and architecture reset

**Status:** COMPLETE — architecture baseline frozen.

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

**Status:** COMPLETE — contract-bearing stub runtime accepted on CT105; no production side effects.

Build CT105 as a deliberately limited service that can validate and route requests but cannot yet perform production civic actions.

### 1.1 Contract set

Define versioned schemas for:

- request envelope;
- result envelope;
- error/failure envelope;
- caller identity, authentication provenance, and extensible client identity;
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
- `incident.*`

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

**Accepted on 2026-10-01.**

The Phase 1 development acceptance harness exercised equivalent `usermin`, `hubzilla`, and `kane-fabric` interface identities against the same bounded Civic operation and produced equivalent contract-valid semantics without backend side effects.

The runtime also proved:

- schema-valid request/result/failure handling;
- bounded capability registry;
- schema-level rejection of prohibited generic operations;
- explicit authorization-decision persistence;
- opaque workflow identifiers and deterministic workflow-state rules;
- fail-closed workflow transition validation;
- explicit service-capability selection evidence;
- audit-event persistence;
- receipt issuance;
- read-only workflow evidence retrieval;
- threaded SQLite safety;
- hardened persistent systemd service;
- loopback-only listener;
- `side_effects=false` throughout Phase 1.

Production Usermin, Hubzilla, and Kane Fabric adapters remain Phase 3 work.

---

## Phase 1H — Contract hardening and external-review closure

**Status:** COMPLETE — final Phase 1 review corrections accepted on persistent CT105 on 2026-10-01.

Phase 1H closes defects found by an independent consumer review before additional orchestrators or production adapters begin depending on the v1 contracts.

Scope is intentionally finite:

- formal orchestrator scope/admission rule;
- extensible caller/client identity and authentication provenance;
- request replay/idempotency behavior;
- contract-valid HTTP failure handling;
- timestamp format enforcement;
- registry/workflow definition validation;
- ordered audit sequencing;
- transactional request persistence;
- meaningful side-effect classification;
- portable JSON Schema reference resolution;
- current Kane signing-authority correction;
- documentation and repository housekeeping.

Phase 1H does **not** add Mechanical Compiler-specific groups, membership state, or operations to CT105. Other Civic Infrastructure applications may instantiate their own orchestrators using this architecture.

Authority: `docs/ORCHESTRATOR_SCOPE.md`.

### Phase 1H acceptance

**Accepted on 2026-10-01.**

The hardened runtime passed the 21-test regression suite and the persistent CT105 acceptance harness.

Verified:

- additive SQLite migration against the existing state database;
- legacy audit-event sequence backfill;
- explicit caller authentication provenance;
- extensible client identity;
- atomic stub-request persistence;
- exact replay returning the original workflow and receipt;
- conflicting replay returning `409 conflict`;
- RFC 3339 timestamp rejection;
- contract-valid malformed-JSON HTTP failure handling;
- loopback-only service exposure;
- `side_effects=false` throughout.

The public contract remains intentionally free of Mechanical Compiler-specific membership, group, or domain semantics.

### Final Phase 1 closure

The second external-review corrections were accepted on persistent CT105.

Verified after the final review pass:

- 30 regression tests pass;
- additive migration against the persistent database succeeds;
- caller-scoped request and idempotency keys work;
- replay diagnostics and failure diagnostics persist;
- percent-encoded workflow IDs resolve;
- clean `pip install .` imports the runtime successfully;
- schema catalog is present for independent validators;
- listener remains loopback-only;
- all Phase 1 execution remains `side_effects=false`.

Phase 1 is now closed. Further work should prioritize one real bounded operation rather than another stub-hardening cycle.

---

## Phase 2 — Service and trust node architecture

Do not begin broad backend integration until Phase 1 contracts are stable enough to reveal actual capability boundaries.

Inventory each required service using the node-design gates in `docs/NODE_DESIGN_GATES.md`. The current Kane reference placement is recorded in `docs/KANE_NODE_PLACEMENT.md`.

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

## Phase 7 — ESP32-S3 lifecycle and signing integration

This phase governs **Orchestrator integration** of edge lifecycle and signing. It does not delay independent construction or testing of the signing authority.

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

---

## Cross-cutting Track I — Operational incidents and abuse signals

**Status:** CONTRACT STUB — no automatic ingestion or enforcement.

Purpose:

- preserve important core, transport, delivery, security, and participant-facing failures as stateful operational incidents when warranted;
- keep immutable audit evidence distinct from observed signals, mutable incident workflow, and enforcement policy;
- allow deployments to classify incident domain, severity, visibility, and source without embedding local policy into the core transport;
- provide a future path for adapters such as systemd/sudo, Hubzilla delivery reporting, SMTP, publication, edge, and other bounded services.

Initial Phase 1 contract surface:

- `incident.report`
- `incident.get`
- `incident.acknowledge`
- `incident.resolve`

All are stubs with `side_effects=false`.

Later phases may add bounded signal ingestion, aggregation, notifications, throttling, quarantine, or escalation only after explicit policy and authorization contracts exist. A signal must not itself be treated as proof of abuse.

Authority: `docs/INCIDENT_MODEL.md`.

---

## Parallel Track D — Civic Infrastructure Demonstrator

**Status:** ACTIVE DESIGN — implementation begins with the Phase 1 stub runtime.

The Demonstrator is a grant-facing and engineering-facing deployment profile that exercises the real Civic contracts with synthetic, resettable data.

It is not a second product and receives no privileged demo-only backend capabilities.

Stages:

- **D-001 — Stub demonstrator:** guided evaluator path, synthetic fixture, real schema validation, workflow/audit/receipt display, prohibited-operation failure, reset.
- **D-002 — Multi-interface demonstrator:** equivalent Civic operation from at least two interaction surfaces.
- **D-003 — Publication demonstrator:** real bounded publication, SHA-256, CID, verification, receipt, controlled failure.
- **D-004 — Full grant demonstrator:** selected Kane Fabric, RAG/inference, and ESP32/signing evidence as those production capabilities become available.

The Demonstrator doubles as an integration/conformance harness and must remain portable to an independent-jurisdiction deployment.

Authority: `docs/DEMONSTRATOR.md`.


## Post-Phase-1 maintenance

### v0.1.0-alpha.2 SQLite lifecycle correction

**Status:** ACCEPTED on persistent CT105 on 2026-10-01.

The Phase 1 baseline inherited a Python `sqlite3` lifecycle defect: the connection context manager committed or rolled back transactions but did not close the connection object.

The maintenance correction:

- makes `StateStore._connect()` an explicit closing context manager;
- preserves existing transaction and `BEGIN IMMEDIATE` semantics;
- closes the acceptance harness read-only SQLite connection explicitly;
- adds connection-lifecycle regression coverage.

Accepted evidence:

```text
33 regression tests                  PASS
persistent CT105 acceptance          PASS
listener 127.0.0.1:8045 only         PASS
side_effects=false                    PASS
```

This correction does not change Civic contracts or Phase 1 architecture.

## Phase 2 — Service and trust node architecture

**Status:** ACTIVE.

Phase 2 begins with the publication/IPFS service boundary because `publication.publish` remains the preferred first real end-to-end operation.

The first Phase 2 task is architecture only: define authority, state ownership, failure domain, transport, and acceptance gates for the new publication node before assigning a CT number or installing Kubo.
