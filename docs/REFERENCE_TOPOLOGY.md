# Reference Service Topology

## Status

This document is an architectural starting point for Phase 2. It records service classes and trust boundaries, not final host assignments.

The topology must remain portable to an independent deployment. Names such as `srv-b`, CT numbers, and `annales` are reference-deployment locators only.

## Layer 1 — Interaction surfaces

### Portal / Usermin

Owns:

- Unix participant account;
- shell and TUI presentation;
- home directory;
- mailbox and quota;
- local participant preferences.

Does not own global workflow logic, publication authority, signing authority, geographic authority, or RAG policy.

### Hubzilla

Owns:

- channel identity;
- posts and discussion;
- federation;
- local UI;
- addon interaction behavior.

The addon is a client of orchestrated capabilities.

### Kane Fabric browser

Owns browser-native:

- artifact verification;
- source-neutral acquisition;
- geographic composition;
- participant-publication composition;
- rendering;
- inspection and interaction;
- browser-visible identity and verification state.

It calls the orchestrator for server-side Civic operations but does not become a thin server-rendered frontend.

### Gitea

Owns editable source and revision truth:

- repositories;
- commits;
- exact source revisions;
- review history;
- approved source artifacts.

It does not become workflow authority.

## Layer 2 — Civic Orchestrator

The orchestrator owns:

- contract validation;
- caller/interface identification;
- cross-service authorization decision points;
- workflow instances and transitions;
- routing to named Civic capabilities;
- provenance;
- audit;
- receipts;
- idempotency and replay controls where required.

It must not become the universal datastore or universal cryptographic authority.

## Layer 3 — Domain and service authorities

### Geographic authority

Reference implementation: Kane Fabric runtime.

Owns:

- official-source ingestion logic;
- candidate generation;
- comparison and reconciliation;
- explicit promotion;
- authoritative geographic state;
- deterministic publication compilation.

The orchestrator coordinates these capabilities but does not redefine geographic truth.

### Publication service

Owns the mechanics required to publish and retain exact approved artifacts, including IPFS/Kubo where selected.

It should accept exact content identities and bounded publication requests, not arbitrary RPC forwarding.

### RAG state/retrieval service

Owns stateful retrieval assets such as:

- corpus metadata;
- private indexes;
- vector/search state;
- SQL/case state where required;
- retrieval execution.

It remains separate from model inference where that boundary is useful.

### Inference service

Reference deployment may use `annales`.

Owns model execution and minimal inference-local state.

It should not silently become the long-term owner of Civic corpus state.

### ESP32-S3 management service

Coordinates operational lifecycle for physical edges:

- enrollment;
- synchronization;
- observed status;
- update requests;
- replacement and recovery.

Physical device identity remains separate from participant and civic-object identity.

### Signing authority

Owns protected signing keys and independent signing policy enforcement.

The orchestrator may request a signature but cannot compel one merely by possessing network access.

A compromised orchestrator must not automatically imply signing-authority compromise.

## Layer 4 — Participant-controlled edges

The reference ESP32-S3 is a bounded artifact appliance.

It may retain and serve a focused participant publication without carrying the county-wide substrate or owning participant identity.

Other hardware or software implementations may satisfy the same public edge contract.

## Reference trust flow

```text
interaction surface
        |
        v
Civic Orchestrator
        |
        +--> domain authority
        +--> publication service
        +--> retrieval service
        +--> inference service
        +--> edge management
        +--> signing authority
                    |
                    +-- independent refusal remains possible
```

## Deployment rule

No service receives its own node merely because it is a separate software package.

A separate node is justified only by one or more of:

- distinct authoritative state;
- protected secrets;
- different network exposure;
- independent failure/recovery requirements;
- hardware requirements;
- substantially different resource profile;
- operator ownership boundary;
- lifecycle or replacement requirements.

## Portability rule

A second-county deployment may co-locate or separate these service classes differently if the public contracts and trust boundaries remain intact.

Topology is therefore a deployment decision. Capability boundaries are the portable architecture.
