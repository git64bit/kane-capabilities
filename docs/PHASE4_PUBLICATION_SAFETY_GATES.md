# Phase 4 Publication Safety Gates

## Status

**REQUIRED BEFORE KUBO SIDE EFFECTS**

This document records the corrections accepted from the third external review of the Phase 2/3 publication path.

The review did not reopen the core publication model. The following decisions remain fixed:

- publication is file-only at ingress;
- artifact, publication, document, and generation remain distinct;
- one CID may have many publication records;
- no purpose, label, retention, path, or version intent is inferred at publication time;
- Usermin remains the thin quota-bounded publication client;
- Kane Fabric remains the heavy management client;
- Hubzilla does not become arbitrary file storage;
- Gitea remains a revision mechanism rather than the universal participant filesystem;
- the local Usermin broker derives the peer through `SO_PEERCRED`;
- Kubo remains disabled until the gates below are accepted.

## Current gate state

Repository implementation and production acceptance are tracked separately.

| Gate | Repository state | Production acceptance state |
| --- | --- | --- |
| P4-001 independent CID verification | implemented and regression-covered | awaits real side-effect gate |
| P4-002 resumable external workflow | implemented and regression-covered | awaits real side-effect gate |
| P4-003 authenticated adapter binding | CT105-side primitive implemented and regression-covered | broker integration and production acceptance pending |
| P4-004 publication-service authentication | both endpoint/client primitives implemented | credential provisioning and live acceptance pending |
| P4-005 stable participant identity | registry/mapping model implemented in U-002 code | real Portal mapping deployment and acceptance pending |
| P4-006 participant publication budget | **not implemented** | pending |
| P4-007 authoritative publication record | implemented in CT105 SQLite completion path | awaits real successful publication acceptance |
| P4-008 no original filename | design decision closed | no separate deployment gate |
| P4-009 side-effect certainty | implemented and regression-covered | awaits live failure-path acceptance where applicable |

A repository implementation marked complete here does not authorize Kubo. The corresponding production path must still be deployed and accepted where the gate has a deployment component.

## P4-001 — Independent CID verification

A publication result is not accepted merely because the publication service echoes the submitted SHA-256 and size.

CT105 must independently compute the expected CID for the frozen publication profile and compare it to the returned CID before completing the workflow.

The service result must include:

```text
cid_profile = civic-ipfs-kubo-v1
```

The profile identifies:

```text
CID version     1
multihash       sha2-256
raw leaves      true
chunker         size-262144
pin             true
CID rendering   base32
```

Until CT105 implements deterministic UnixFS root calculation for multi-chunk artifacts, the accepted artifact limit is reduced to **262,144 bytes**. This guarantees that the root is a single raw leaf and permits independent CID verification using only the standard library.

Increasing the limit again is a later tested implementation change, not a contract reinterpretation.

## P4-002 — Resumable external workflow

Dispatch to an external service and terminal workflow persistence are separated by a crash boundary.

Therefore:

- a matching non-terminal external workflow must be resumable using the same `workflow_id`;
- a retryable backend condition must not become an immutable replay result;
- startup reconciliation must identify non-terminal external workflows;
- redispatch of the same exact artifact/workflow is permitted because the publication service is idempotent for exact bytes and independently verifies them;
- crash-injection tests are required before Kubo is enabled.

A terminal receipt is created only when the workflow becomes terminal.

## P4-003 — Authenticated adapter identity binding

A valid adapter credential is not permission to assert arbitrary Civic identity.

Each accepted adapter credential maps server-side to:

- fixed `client.id`;
- fixed `client.kind`;
- fixed `authenticated_by`;
- an allowed Civic subject namespace or subject-mapping rule.

The Orchestrator derives or validates these values from the authenticated transport context.

A request-body claim may repeat them for inspectability, but it can never widen or contradict the authenticated adapter identity.

## P4-004 — Publication-service authentication

Network reachability to the publication service is not publication authority.

Before Kubo is enabled:

- CT105 must possess a publication-service credential unavailable to participants and unrelated services;
- the publication service must reject requests without a valid credential;
- the credential mechanism must be conventional and replaceable, such as a protected bearer credential or mTLS;
- firewall/relay restrictions remain defense in depth rather than the sole authorization boundary.

## P4-005 — Stable participant identity

Unix UID and username are local account locators, not permanent Civic publication identity.

The Portal identity authority must map the authenticated Unix account to a stable, never-recycled Civic participant identifier.

Conceptually:

```text
SO_PEERCRED UID
      -> current Portal account
      -> stable participant_id
      -> caller.subject
```

Deleting, renaming, or recreating a Unix account must not transfer historical publication provenance.

The participant identifier format is deployment-independent; the Kane reference deployment may use opaque identifiers such as UUID-derived `participant:...` subjects.

## P4-006 — Participant publication budget

Usermin filesystem quota does not bound IPFS storage.

Before real publication, CT105 authorization must enforce a deployment policy that bounds participant use of Civic-controlled publication storage.

The policy may include:

- active pinned-byte budget;
- publication-count budget;
- rate/burst limits.

These numerical limits are deployment policy, not portable Civic contract constants.

A historical publication record remains valid after Civic-controlled content is unpinned.

## P4-007 — Authoritative publication record

The immutable publication fact is Orchestrator evidence and must be committed atomically with terminal workflow completion.

The authoritative publication record is therefore stored in the Orchestrator state database in the same SQLite transaction that records:

- terminal workflow state;
- final audit event;
- receipt;
- result envelope.

Minimum publication evidence:

```text
publication_id
participant_id
workflow_id
receipt_id
sha256
size_bytes
media_type
cid
cid_profile
published_at
client provenance
verification state
```

The PostgreSQL publication/document catalog is initially a **rebuildable projection** keyed by `publication_id`.

PostgreSQL becomes authoritative only for later mutable document-management semantics that are deliberately separate from the immutable publication fact, such as logical paths, document/generation relationships, annotations, and catalog organization.

## P4-008 — No original filename in the publication record

The initial publication contract does not preserve the source filename.

A working filename is local descriptive context, not part of exact-byte identity and not required to establish the fact of publication.

The participant may later assign a document name or logical path through a heavy management client.

## P4-009 — Side-effect certainty

The existing Boolean `side_effects` remains conservative for compatibility.

Evidence for external operations must additionally distinguish:

```text
side_effects_certainty = known | unknown
```

Examples:

```text
connection refused before acceptance   false / known
successful verified publication        true  / known
timeout after dispatch                  true  / unknown
verification failure after publication true  / known
```

The Boolean answers whether external effects must be treated as present for safety. The certainty field records whether that conclusion is directly known.

## U-002 broker constraints

The privileged broker must never open an arbitrary pathname supplied by a participant.

The participant process, already running under the participant Unix identity, opens and reads its own Usermin upload and sends bounded bytes to the broker.

The broker receives:

- peer credentials from the kernel;
- artifact bytes.

It does not receive authority to traverse a participant-provided filesystem path.

The broker derives:

- stable participant identity;
- size;
- SHA-256;
- bounded media type;
- request provenance.

The broker enforces the current artifact limit before remote dispatch.

## Remaining acceptance sequence

The repository-side corrections above are not a substitute for production acceptance. The remaining sequence is:

1. deploy and accept the authenticated CT105 ingress and protected CT105 credentials on `srv-b / CT105 / civic-orchestrator`;
2. deploy and accept the matching CT105-to-publication-service credential on the publication-service host while the backend remains validation-only;
3. deploy and accept the real U-002 Usermin local broker, stable participant mapping, and Custom Command path;
4. complete U-003 broker-to-CT105 authenticated remote publishing over the production route;
5. complete U-004 validation-only end to end and verify persisted workflow/audit/receipt evidence with no Kubo side effect;
6. implement and accept P4-006 participant publication budgeting in CT105 authorization policy;
7. perform a separate Phase 4 first-side-effect gate before enabling Kubo.

No Kubo side effect is permitted before all applicable gates are accepted.
