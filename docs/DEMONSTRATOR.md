# Civic Infrastructure Demonstrator

## Purpose

The Civic Infrastructure Demonstrator is a grant-facing and engineering-facing deployment profile that exercises the real Civic contracts through a bounded, synthetic, resettable scenario.

It is not a second product, a mock architecture, or a privileged bypass around production controls.

> Nothing exists only for the demo except synthetic fixtures, evaluator navigation, demo identities, and reset tooling.

The demonstrator consumes the same public contracts as ordinary Usermin, Hubzilla, Kane Fabric, Gitea, publication, and orchestrator clients.

## Goals

The demonstrator must make the project understandable without requiring an evaluator to first absorb the complete infrastructure architecture.

It should demonstrate, in one guided sequence:

1. accepted county geography;
2. a bounded participant publication;
3. one Civic operation submitted through the orchestrator;
4. contract validation and authorization;
5. publication/provenance output;
6. independent verification;
7. the same operation semantics visible from more than one interaction surface;
8. a controlled failure path.

## Demonstration profile

The demonstrator uses:

- real Kane Fabric browser modules and publication validation;
- real Civic Orchestrator contracts;
- real schema validation;
- real workflow identifiers and audit events;
- real receipt structure;
- real publication/content identity;
- real IPFS publication after Phase 4 enables it;
- real Usermin/Hubzilla/Kane Fabric adapters as they become available.

It uses only synthetic or explicitly public demonstration data.

It must not use:

- production participant credentials;
- private participant data;
- production signing keys;
- private RAG corpora;
- hidden evaluator privileges;
- a special demo-only backend operation unavailable through the normal contract model.

## Reference evaluator journey

### Step 1 — Explore county context

Open the Kane Fabric web application and load the accepted Kane County geographic publication.

Show:

- jurisdiction identity;
- publication/content identity;
- verification status;
- selected geographic object/building context.

### Step 2 — Inspect synthetic participant publication

Load a small demonstration association publication attached to accepted geographic identity.

Suggested fixture:

```text
Demonstration Association
  6 synthetic units
  public association metadata
  2 public unit/object records
  1 synthetic restricted-classification example
  2 publication generations
```

The fixture must be obviously synthetic while remaining structurally realistic.

### Step 3 — Submit Civic operation

Use a normal client surface to submit a bounded operation such as:

```text
publication.publish
```

During Phase 1 the result is the real stub result:

```text
validated
authorized under demo/stub policy
workflow created
not implemented
side_effects = false
```

After Phase 4, the same evaluator path may perform real bounded publication.

### Step 4 — Inspect workflow evidence

Expose:

- request ID;
- workflow ID;
- caller/interface;
- operation;
- authorization decision;
- workflow states;
- result;
- receipt;
- audit/event entries;
- SHA-256 and CID when publication is active.

### Step 5 — Verify independently

Provide direct ways to:

- inspect the JSON contract instance;
- inspect the governing JSON Schema;
- inspect the OpenAPI operation;
- verify the content hash;
- retrieve/verify the published artifact when publication is active;
- view the corresponding public Git source/revision where appropriate.

### Step 6 — Cross-surface equivalence

Show the same semantic operation from at least two interaction surfaces.

Target progression:

```text
Usermin TUI        -> publication.publish
Kane Fabric browser -> publication.publish
Hubzilla addon     -> publication.publish
```

The caller/interface metadata differs. The Civic operation and result contract do not.

### Step 7 — Controlled failure

Demonstrate at least one fail-closed case.

Examples:

- tampered artifact fails hash validation;
- unavailable publication backend produces `backend-unavailable`;
- prohibited operation such as `shell.exec` is rejected;
- invalid workflow transition is rejected;
- participant publication with mismatched geographic reference is not composed.

The failure must be visible and understandable to the evaluator.

## Under-the-hood view

The demonstrator should have an optional technical panel showing the evidence chain without requiring shell access:

```text
request_id
workflow_id
operation
caller subject
interface
authorization decision
current/final workflow state
service capability
content SHA-256
CID
receipt_id
audit events
timestamps
```

Links or controls may expose:

- JSON instance;
- JSON Schema;
- OpenAPI definition;
- Git revision;
- published artifact;
- verification result.

## Reset contract

The demonstrator must be resettable to a known baseline.

Reset may remove:

- demo workflow state;
- demo audit records where policy permits;
- demo publication pointers;
- generated demo artifacts;
- demo adapter-local state.

Reset must not:

- modify production participant state;
- rotate production trust roots;
- delete non-demo IPFS pins;
- alter accepted Kane geographic authority;
- rewrite Git history;
- require manual database repair.

The reset operation is a demonstrator-administration function, not a general Civic capability exposed to ordinary participants.

## Isolation

Demo identities and production identities must be distinguishable by policy and data namespace.

A deployment may run the demonstrator on shared infrastructure only when:

- demo state cannot authorize production operations;
- demo reset cannot reach production state;
- demo data is clearly marked;
- production secrets are not copied into demo configuration.

If those conditions are difficult to prove, use a separate demonstration deployment.

## Grant-evaluation design

The evaluator should be able to understand the system at three depths:

### Level 1 — Guided

A short landing path:

```text
Explore County
Inspect Participant
Run Civic Workflow
Verify Provenance
See Another Interface
```

### Level 2 — Evidence

Show receipts, identities, hashes, workflow state, source references, and controlled failures.

### Level 3 — Architecture

Link to the portable architecture, node topology, public contracts, and independent-operator model.

The evaluator should not need administrative shell access for any of these levels.

## Engineering role

The demonstrator doubles as an integration/conformance harness.

A release should be able to run the demonstration scenario and prove:

- browser composition still works;
- request contracts still validate;
- adapters still map to the same Civic operation;
- workflow results remain schema-valid;
- fail-closed behavior remains intact;
- publication verification remains reproducible.

This prevents the grant demonstration from becoming separate demo-only software.

## Acceptance stages

### D-001 — Stub demonstrator

Available after the Phase 1 stub runtime exists.

Required:

- synthetic fixture;
- guided evaluator path;
- request submission;
- real schema validation;
- workflow/audit/receipt display;
- prohibited-operation failure;
- reset.

No production side effects.

### D-002 — Multi-interface demonstrator

Available during Phase 3.

Required:

- equivalent operation from at least two interfaces;
- caller/interface distinction visible;
- shared workflow/result semantics.

### D-003 — Publication demonstrator

Available after Phase 4.

Required:

- exact demo artifact publication;
- SHA-256;
- CID;
- verification from publication service;
- receipt;
- controlled tamper/backend-failure path.

### D-004 — Full grant demonstrator

Available after relevant Kane Fabric/RAG/edge integrations.

May add:

- geographic refresh comparison;
- RAG retrieval/inference with public demo corpus;
- ESP32 bounded publication or lifecycle evidence;
- protected signing workflow evidence without exposing production key material.

## Portability

The Demonstrator is itself a portability test.

A future Orange County or other independent operator should be able to substitute its own synthetic jurisdiction fixture and run the same guided Civic operations using the same public contracts.
