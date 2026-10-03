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

**Status:** ACCEPTED FOR PUBLICATION VALIDATION PATH; broader service architecture continues incrementally.

Phase 2 selected `publication.publish` as the first bounded external operation and established the publication-service boundary before enabling real IPFS side effects.

Accepted on 2026-10-01:

- isolated publication-service boundary;
- bounded HTTP/JSON service contract;
- exact byte-integrity checks;
- deterministic CID profile;
- private production route from CT105 to the publication service;
- `publication.publish` activated in the Orchestrator registry;
- real validation-only workflow with persisted authorization, audit, receipt, and expected `service-unavailable` result;
- Kubo and swarm side effects remain disabled.

Inventory of later services continues under `docs/NODE_DESIGN_GATES.md` and `docs/KANE_NODE_PLACEMENT.md`.

The current publication/document design also fixes these state roles:

- Usermin/Portal owns participant working files and quota;
- Hubzilla remains a social/visible-image surface, not arbitrary document storage;
- PostgreSQL is the intended structured publication/document catalog for the Kane reference deployment;
- Gitea is revision authority where Git is the selected revision mechanism;
- IPFS owns immutable publication bytes and Civic-controlled pin state;
- CT105 owns publication/document catalog semantics, workflow, provenance, authorization, audit, and receipts without becoming universal byte custody.

Authority:

- `docs/PHASE2_PUBLICATION_SERVICE_BOUNDARY.md`;
- `docs/CT105_PHASE2_PUBLICATION_ACCEPTANCE.md`;
- `docs/PUBLICATION_DOCUMENT_MODEL.md`;
- `docs/INTERACTION_STORAGE_BOUNDARIES.md`.

### Phase 2 acceptance rule

Every additional node exists because of an explicit trust, state, network, failure-domain, or lifecycle requirement—not because a technology normally runs on its own server.

---

## Phase 3 — Interaction adapters and participant publication catalog

**Status:** ACTIVE.

Connect human-facing and service-facing surfaces to the stable Orchestrator contracts without giving any client an alternate storage or authorization authority.

### Usermin — thin publication client

The first participant action is deliberately:

```text
Choose file
Publish
```

Usermin retains Unix identity, home directory, mailbox, quota, terminal, and ordinary working-file behavior.

The publication form does not ask for:

- label;
- purpose;
- retention duration;
- logical document path;
- pin duration;
- supersession;
- future-version intent.

Production discovery of stock Usermin Custom Commands is complete. U-001 is accepted, including direct proof that AF_UNIX `SO_PEERCRED` returns the real participant UID/GID.

Next gates:

- **U-002:** ACCEPTED on 2026-10-02 on the production Portal/Usermin host (`witness-hubzilla`). The local peer-credential broker received participant-owned bytes over AF_UNIX, derived the real Unix UID through `SO_PEERCRED`, mapped it to the stable Civic participant ID, and returned validation-only evidence with `remote_dispatch=false`.
- **U-003:** ACCEPTED on 2026-10-03 in production. The broker-to-Orchestrator route now uses protected adapter credentials, server-side fixed client/authentication provenance, private routing, and rejection of direct participant API bypass.
- **U-004:** validation-only end to end through the real Usermin Custom Command remains pending.

### Custom Command architecture and initial utility registry

Usermin Custom Commands are a bounded participant control surface, not a second application server and not a generic remote-execution facility.

Before the first production Custom Command is enabled, Phase 3 must freeze a reusable Custom Command contract that can be shared by independent Civic Infrastructure owner-operators.

The command registry follows the same discipline as the Orchestrator operation registry:

- declare the intended utility surface before implementing it;
- default undeveloped commands to declared/non-callable, no-side-effect behavior;
- distinguish declared, stub, validation, available, disabled, and retired lifecycle states;
- map each recognized command to a fixed bounded Orchestrator operation or other explicitly admitted Civic interface;
- derive participant identity from the trusted local adapter path rather than command arguments;
- keep backend topology, credentials, service names, URLs, container identities, and private-network details out of participant-controlled input;
- require companion plain-language help for every registered command, covering preflight checks, significant effects, consequences, and incident guidance;
- keep help locally readable without the broker or Civic network;
- allow high-consequence commands to require explicit acknowledgement as a usability barrier, never as authorization.

Custom Command identifiers are **non-serialized codenames**. The canonical identifier is two lowercase alphabetic tokens separated by one hyphen:

```text
[token 1: 1-5 letters]-[token 2: 1-5 letters]
```

Examples of the identifier shape include `water-ants`, `navy-roots`, and `next-penny`.

The codename is opaque and must not encode authority, order, implementation technology, deployment location, or lifecycle state. Once assigned, a codename is never recycled for a different command. A later serial/index may be added for documentation or presentation, but it does not replace the canonical codename.

The initial registry must reserve bounded utilities in these families as declared/non-callable entries. Individual commands advance to stub, validation, or available only after their own contracts and authority gates are accepted:

| Family | Initial participant utility candidates |
|---|---|
| Publication | Publish File; My Publications |
| Logical File Namespace | Bind Logical File Name; Browse Logical File Namespace; later explicit rebind/unbind |
| Publication retention | Request participant-controlled pin; request unpin; inspect desired/observed pin state |
| Attestation | My Attestation Timeline; register/submit an attestation record; verify a historical resource |
| Edge continuity | My Attestation Device; synchronize attestation state; continuity check; resolve historical resource |
| Witness/Hubzilla | Register Witness image evidence/reference; inspect nomadic-continuity state |
| Public verification material | Publish public verification material; inspect public-key/signature history; place public verification material on an authorized edge |
| Signing | Request only a specifically authorized signature operation; inspect resulting signed-object evidence |
| Firmware | Show authorized firmware; request authorized edge update; inspect update/rollback state |
| Departure continuity | Pre-departure continuity audit and final active-participation synchronization |

The first implemented Custom Command remains **Publish File**. The v1 registry freezes its canonical codename as `water-ants`; it is not assigned a serial such as `CC-001`. Repository status: `water-ants` has advanced to a generic local `stub`; the production Usermin mapping has not yet been switched to that path.

Publish File remains deliberately minimal:

```text
Choose file
Publish
```

Its first implementation exercises the Custom Command registry, local participant broker, authenticated Orchestrator transport, and the existing `publication.publish` workflow in stub/validation mode before any new side effect is enabled.

The wider command inventory does not expand the Publish File form with logical paths, retention, pinning, attestation, edge destination, title, or version intent. Those remain separate bounded operations.

#### Custom Command non-goals and prohibited escape hatches

The Custom Command framework must not implement or expose:

- arbitrary shell or command execution;
- arbitrary SSH;
- arbitrary HTTP proxy/fetch behavior;
- arbitrary SQL;
- direct Kubo/IPFS RPC;
- caller-selected service, host, container, socket, or network destination;
- caller-selected Orchestrator operation names;
- arbitrary signing or caller-supplied private-key material;
- privileged opening of participant-supplied filesystem paths;
- direct mutation of another participant's namespace, publication catalog, pin state, edge state, or attestation history;
- a replacement implementation of Hubzilla nomadic identity, email storage, ordinary Usermin file management, or IPFS itself.

When a requested utility would require one of these behaviors, implementation stops at the architecture boundary until a new bounded semantic operation and explicit authority/resource model are designed.

Authority: `docs/CUSTOM_COMMAND_ARCHITECTURE.md`; `contracts/custom-command-registry-v1.yaml`.

### Participant storage and continuity backplanes

The participant-facing architecture deliberately separates several backplanes:

- Usermin `/home` is quota-bounded participant working storage and may contain ordinary participant files of any type;
- Virtual Email Boxes are a separate email backplane; participants are encouraged to forward mail they want to retain to their own main email account;
- Hubzilla/Witness is the social and witness surface and permits visible image uploads rather than arbitrary PDF/archive/general-binary storage;
- IPFS is the content-addressed publication backplane for approved inspectable publication classes; compressed/archive containers are not publication artifacts merely because Usermin can store them;
- the Attestation Device is not bulk storage. It is a participant-controlled continuity, attestation, resolution, and verification endpoint that retains enough authenticated state to locate and verify historical resources across surviving backplanes.

The Attestation Device contract is platform-neutral. ESP32-S3 is a reference device, not the definition of the role.

A participant who leaves the Kane authority domain may lose current Portal/Witness authorization and the ability to create new Kane Civic Attestation Records, while retaining historical records, public verification material, resource identities, signatures, timeline context, and the ability to resolve publicly available resources. Continuity must not require continued Kane Portal login or continued access to a Kane private network.

### Publication/document catalog

Persist the distinction among:

- artifact — exact bytes/content identity;
- publication — immutable participant-linked publication event;
- document — participant-managed logical object;
- generation — one managed document state;
- lifecycle state — explicit later pin/unpin/retire and management actions.

The same CID may have multiple publication records.

Do not infer document/version/supersession relationships from filenames, chronology, or content similarity.

Store the immutable publication fact atomically with terminal workflow evidence in the Orchestrator SQLite state. Use PostgreSQL as a rebuildable publication/document catalog projection and later as authority for mutable document-management semantics. The **Logical File Namespace** uses a deliberately restricted forward-slash path notation for participant organization. Its POSIX-like appearance describes syntax only: it is not a filesystem, carries no symlink/hardlink/mount/device/permission semantics, and is not proof of physical filesystem placement.

A future `document.*` namespace may be admitted only after its contract is frozen.

### Hubzilla

Keep Hubzilla as the discussion/channel/social-evidence surface.

Reference policy:

- visible image upload may remain available where required;
- general arbitrary-file storage is disabled;
- the addon may display or manage publication records through bounded Orchestrator operations;
- routine moderation must not depend on operators opening arbitrary participant files.

### Kane Fabric — heavy client

Kane Fabric is the primary full-featured online and reduced-offline management client.

It may expose:

- participant publication history;
- file type/size/timestamps;
- SHA-256/CID/verification;
- logical paths;
- document generations;
- Gitea revision references;
- workflow/receipt evidence;
- later pin/unpin/retire and explicit relationship management.

Its richer UI does not grant different storage authority.

### Gitea

Integrate exact repo/commit/path references and controlled callbacks/events while preserving Gitea as editable revision truth where Git is appropriate.

Gitea does not become the universal participant filesystem or universal Civic document identity.

### Phase 3 acceptance

The same Civic records and operation semantics are available through multiple interfaces without duplicating backend workflow logic or creating competing storage authorities.

---

## Phase 4 — First real IPFS side effect

**Status:** GATED.

Enable Kubo publication only after the trusted participant-adapter route is accepted.

The first real side-effect pattern remains:

```text
authenticated participant
  -> exact bytes
  -> authorized publication workflow
  -> deterministic content identity
  -> publish/pin
  -> read-back verify
  -> participant-linked publication record
  -> receipt
```

Publication itself does not require purpose, retention duration, document organization, or version intent.

Requirements:

- exact input identity;
- stable, never-recycled participant identity;
- authenticated adapter transport with transport-bound caller/client provenance;
- authenticated CT105-to-publication-service transport;
- deterministic result contract with explicit `cid_profile`;
- CT105-independent CID calculation and comparison;
- resumable/idempotent external workflows and startup reconciliation;
- participant publication budget — repository implementation and regression coverage complete; Kane deployment values, CT105 policy installation, and live acceptance pending;
- participant-linked publication record committed atomically with terminal workflow evidence;
- audit and receipt;
- backend isolation;
- explicit side-effect certainty for ambiguous transport outcomes;
- fail-closed verification;
- no claim that later unpinning globally deletes IPFS content.

Authority: `docs/PHASE4_PUBLICATION_SAFETY_GATES.md`.

No second production side-effect capability is enabled until publication demonstrates the complete end-to-end control pattern.

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

## Phase 7 — Attestation edge lifecycle, continuity, and signing integration

This phase governs **Orchestrator integration** of participant Attestation Device lifecycle, edge continuity, firmware lifecycle, and signing. It does not delay independent construction or testing of signing authority or platform-specific edge implementations.

ESP32-S3 remains the current reference implementation only. The durable role is a replaceable participant-controlled Attestation Device that can operate through the participant's ordinary network path and may use direct WireGuard or owner-operator proxies where available.

Treat publication custody, attestation/history semantics, edge continuity, transport, and firmware trust as separate planes.

The orchestrator may coordinate:

- edge enrollment and replacement;
- logical edge-placement intent;
- attestation-record submission and verification;
- synchronization of authenticated participant timeline state;
- resolution/availability observations for historical resources;
- artifact synchronization;
- firmware candidate selection;
- signing requests;
- signed release manifests;
- update authorization;
- rollout status;
- recovery/replacement workflows;
- pre-departure continuity verification while participation remains active.

The Attestation Device must not become a bulk backup device, permanent participant identity, Kane-only hardware root, or substitute storage authority. Loss or replacement of the physical device must not erase the participant's historical Civic meaning.

Historical verification must remain useful after current Kane participation ends. Continued Portal/Witness login, a Kane hostname, a Kane private address, or access to one Kane WireGuard network must not be required merely to interpret already-authenticated historical records.

The orchestrator must not hold firmware-signing or Civic-signing private keys.

Each signing authority must independently validate enough request context to reject unauthorized signing even if CT105 is compromised.

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

