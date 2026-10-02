# Kane Reference Node Placement Decision

## Status

Initial Kane reference-deployment placement decision.

This document assigns the portable service classes in `REFERENCE_TOPOLOGY.md` to the current Kane infrastructure. It does **not** make these hostnames, CT numbers, IP addresses, or virtualization technologies part of the Civic Infrastructure public contract.

The independent-operator rule remains: another county may place the same capability boundaries differently while preserving the public contracts and trust model.

## Summary

| Capability / service class | Kane reference placement | Decision |
|---|---|---|
| Portal / Usermin + Witness / Hubzilla interaction surfaces | `witness-hubzilla` container | currently co-located; deployment fact recorded in `KANE_DEPLOYMENT_FACTS.md` |
| Civic Orchestrator | `srv-b` CT105 `civic-orchestrator` | keep isolated |
| Kane Fabric geographic authority | `srv-b` CT102 `kane-fabric` | retain existing |
| Secure browser origin / Wiregate | `srv-b` CT103 `kane-wiregate` | retain existing |
| Gitea source/revision authority | `srv-b` CT104 `civic-gitea` | retain existing; use for suitable document generations/revisions |
| Publication/document catalog | existing PostgreSQL service available to the Orchestrator | structured catalog only; not artifact-byte custody |
| Publication / IPFS backend | `proxmox1` CT106 `publication1.internal.diagnostics.kane-il.us` (`192.168.1.106`) | deployed validation-only; Kubo side effects remain disabled |
| RAG state / retrieval / indexes | new isolated stateful service node on `srv-b` | create after contract gate |
| Model inference | existing `annales` inference service/container | retain separate |
| Firmware signing authority | `annales` LXD `firmware-authority` software signing authority | retain protected boundary; hardware backing optional, not required |
| ESP32-S3 management / synchronization | new isolated service node | create after transport contract gate |
| Physical firmware build / programming | existing `fw` workstation | retain existing |

## 0. Interaction surfaces

### Placement

The current Kane deployment co-locates **Portal/Usermin** and **Witness/Hubzilla** in the container whose hostname is `witness-hubzilla`.

This was confirmed live on 2026-10-02. `usermin.service` is loaded and active in that container. The container also carries the `civic-participants` group used by the Usermin adapter boundary.

This is a deployment fact, not a portability requirement. The physical host and numeric CT/VM identifier are not established by this document and must not be invented. See `KANE_DEPLOYMENT_FACTS.md` for the confirmed evidence.

## 1. Civic Orchestrator

### Placement

`srv-b` CT105 `civic-orchestrator`.

### Owns

- public operation-contract validation;
- caller/authentication provenance and extensible client identification;
- workflow state and transitions;
- adapter selection;
- authorization decision records;
- audit;
- receipts;
- idempotency/replay state where required.

### Must not own

- Kane geographic authority;
- Gitea repositories;
- Kubo repository state;
- RAG corpus/index state;
- model weights/inference hardware;
- firmware-signing private keys;
- participant edge publications as exclusive custody;
- ESP32 management transport identity.

### Reason

CT105 is the fusebox. Co-locating backend authorities would collapse the exact boundaries the orchestrator exists to preserve.

## 2. Kane Fabric geographic authority

### Placement

Existing `srv-b` CT102 `kane-fabric`.

### Decision

Retain unchanged as the domain authority for:

- source acquisition;
- candidate generation;
- comparison/reconciliation;
- explicit promotion;
- authoritative county geographic state;
- deterministic geographic publication compilation.

The orchestrator invokes named `geography.*` capabilities. CT102 independently validates and executes domain operations.

### Reason

The Kane Fabric database and reconstruction/promotion lifecycle already form an accepted authority boundary. Moving them into CT105 would turn the orchestrator into a domain server and make future independent-county replacement harder.

## 3. Secure browser origin / Wiregate

### Placement

Existing `srv-b` CT103 `kane-wiregate`.

### Decision

Retain as secure browser origin / controlled proxy boundary.

It may front browser-facing access to:

- accepted county publications;
- bounded participant publications;
- selected orchestrator API paths intended for browser use.

It does not become workflow authority.

### Reason

The browser secure-origin problem and the orchestration problem are separate. Kane Fabric already specifies that HTTPS terminates at Wiregate/administrative infrastructure rather than on the ESP32-S3.

## 4. Gitea source/revision authority

### Placement

Existing `srv-b` CT104 `civic-gitea`.

### Decision

Retain.

The orchestrator may request exact repository/commit/path content, relate managed document generations to exact revisions, and return publication records or controlled metadata, but Gitea remains editable source/revision truth.

Gitea is not the universal participant filesystem. The structured publication/document catalog may relate a logical document generation to a Gitea commit without making the Git path the universal Civic document identity.

### Reason

Git authority and workflow authority are different concerns. Gitea also has its own intentional outbound-mail exception and should not be folded into the generic CT105 network policy.


## 4A. Publication/document catalog

### Placement

Use the existing PostgreSQL service available to the Orchestrator for the structured participant publication/document catalog projection and later mutable document-management state.

Before catalog implementation begins, the Kane deployment record must identify the exact PostgreSQL service/node and its operating owner. This document does not invent that locator.

The catalog may hold:

- participant/publication associations;
- artifact metadata;
- POSIX-like logical paths;
- document and generation identifiers;
- timestamps;
- Gitea revision references;
- IPFS publication references;
- current Civic-controlled pin/lifecycle state.

It must not become the artifact-byte store merely because it contains metadata about those artifacts.

The immutable publication record itself remains authoritative in CT105 SQLite and is committed atomically with terminal workflow/audit/receipt state. PostgreSQL initially consumes a rebuildable projection keyed by `publication_id`.

### Reason

Structured catalog state and immutable artifact custody are different responsibilities. PostgreSQL is appropriate for relationships, paths, timestamps, and lifecycle state; Gitea remains revision authority where selected, and IPFS remains publication-byte custody.

## 5. Publication / IPFS backend

### Placement

The isolated Trixie-based publication CT is `proxmox1 / CT106 / publication1.internal.diagnostics.kane-il.us` at private address `192.168.1.106`. The publication/IPFS backend is explicitly **not hosted on `srv-b`**.

The current service is validation-only. Kubo publication and swarm participation remain disabled until the participant trust and first-side-effect gates are accepted.

This placement is a Kane reference-deployment decision. Proxmox 9, Debian Trixie, OVH, the eventual CT number, and the eventual hostname are not part of the portable Civic Infrastructure contract.

Reference placeholder only:

```text
publication service
  persistent Kubo/IPFS state
  exact-artifact input contract
  pin/verify implementation
  no participant-facing shell
```

These CT, hostname, and address values are Kane deployment locators rather than public Civic identity.

### Do not place in CT105

Kubo owns:

- persistent repository state;
- network participation;
- garbage-collection/pinning behavior;
- resource and lifecycle concerns distinct from workflow coordination.

### Existing `witness-ipfs`

The existing `witness-ipfs` node is **retired from the target architecture**. It served its earlier purpose and will not be reused as the shared Civic publication backend.

Migration rule:

1. initialize new publication state under the bounded `publication.*` contract;
2. replicate or re-pin only the content that is explicitly required;
3. verify required CIDs/content identities from the new node;
4. enable real orchestrated publication only after the participant trust gate;
5. shut down the old `witness-ipfs` node after required migration evidence is complete;
6. retain only the evidence needed to reconstruct the migration decision.

The old node must not remain an accidental parallel authority after cutover.

## 6. RAG state / retrieval / indexes

### Placement

Create a **new isolated stateful service node on `srv-b`** after the `rag.*` contract is frozen.

### Owns

- corpus metadata;
- private indexes;
- vector/search state;
- SQL/case state where required;
- retrieval execution;
- context assembly inputs that are stateful/private.

### Does not own

- final UI;
- cross-service workflow state;
- general-purpose model inference.

### Reason

This state is potentially large, private, mutable, and backup-sensitive. It should not share CT105's small control-plane failure domain.

The Kane reference design keeps stateful retrieval close to the service-control infrastructure while allowing `annales` to remain the GPU/inference domain.

## 7. Model inference

### Placement

Existing `annales` inference service/container.

### Decision

Retain as a separate capability behind `inference.*`.

### Reason

Inference has:

- GPU/hardware requirements;
- a substantially different resource profile;
- replaceable model/runtime implementation;
- no need to own the authoritative Civic corpus or orchestrator workflow state.

The orchestrator supplies authorized context and records result provenance.

## 8. Firmware signing authority

### Placement

Existing/planned `annales` LXD `firmware-authority` using the current Kane Fabric software-signer baseline.

Hardware-backed key custody may be introduced later as an implementation hardening option, but it is not a baseline architectural requirement.

### Decision

Retain the independent signing-authority boundary.

The Firmware Authority service may be network-reachable through a narrowly defined authenticated interface, but **direct unrestricted public Internet exposure is not required by the architecture**.

The orchestrator sends a bounded `signing.*` request. The authority independently verifies enough request state to refuse unauthorized signing.

### Required property

```text
compromise of CT105
    !=
possession of firmware-signing private key
    !=
automatic ability to sign arbitrary firmware
```

### Reason

The current Kane Fabric decision makes a software signing authority the baseline. The architectural invariant is not a particular hardware device; it is that CT105 does not possess signing authority and that the signing service can independently refuse unauthorized signing.

## 9. ESP32-S3 management / synchronization

### Placement

Create a **new isolated service node**, after the management-transport contract is resolved.

No CT number or hostname is assigned yet.

### Owns

- edge enrollment;
- observed edge state;
- synchronization scheduling;
- artifact-transfer/update coordination;
- replacement/recovery coordination;
- management-transport implementation.

### Must not own

- participant civic identity;
- firmware signing authority;
- county geographic authority.

### Transport constraint

Kane Fabric MS5-008 explicitly **deferred** retaining WireGuard on the ESP32-S3. Therefore this node must not be designed around a permanent per-device WireGuard assumption.

The management contract must continue to support ordinary participant NAT without requiring:

- inbound port forwarding;
- static participant LAN addresses;
- DHCP reservations;
- operator administration of participant routers.

The final transport is a later decision; the service boundary is required now.

## 10. Physical firmware build / programming workstation

### Placement

Existing physical host `fw`.

### Decision

Retain.

`fw` owns:

- pinned firmware builds;
- direct USB programming;
- physical ESP32 acceptance;
- build evidence.

It does not become the signing authority merely because it creates firmware binaries.

### Reason

Separating build execution from protected release signing is a valuable supply-chain boundary and is already established in Kane Fabric.

## Remaining new-node count implied by this decision

The publication service node has now been deployed in validation-only mode.

The current architecture still anticipates **two additional new service nodes beyond the already deployed CT105/publication stack**, unless later audits justify safe reuse:

1. RAG state / retrieval service;
2. ESP32-S3 management / synchronization service.

Neither should be created solely from this count. Each remains gated by its Orchestrator-facing contract and resource/trust specification.

## Existing Kane reference topology

```text
Interaction
  Portal/Usermin
  Hubzilla
  Kane Fabric browser
  Gitea integration
       |
       v
srv-b
  CT105 civic-orchestrator
       |
       +---- CT102 kane-fabric -------- geographic authority
       +---- CT103 kane-wiregate ------ secure browser origin
       +---- CT104 civic-gitea -------- source/revision authority
       +---- PostgreSQL catalog -------- publication/document metadata
       +---- publication client path ---+---------------------------> OVH Proxmox 9
       |                                  `-- publication/IPFS CT (validation-only; Kubo disabled)
       +---- NEW retrieval ------------ RAG/index/private state
       +---- NEW edge-management ------ ESP32 lifecycle/sync
       |
       +================ CPE / controlled network ================+
                                                                  |
                                                               annales
                                                                  |
                                                 +----------------+----------------+
                                                 |                                 |
                                            inference                       firmware-authority
                                                                               software signer
                                                                      (hardware backing optional)

fw workstation
  pinned builds / USB programming / physical device acceptance

participant site
  ESP32-S3 or other conforming bounded edge
```

## Portability interpretation

For another jurisdiction, the boxes above are **roles**, not mandated machines.

An independent operator may:

- use VMs instead of LXC/LXD;
- use a different Git service;
- use another IPFS implementation or another publication backend if the contract permits;
- use another inference platform;
- use another edge hardware family;
- combine low-risk roles where the node-design gates remain satisfied.

What must remain stable are the public Civic capability and trust boundaries.
