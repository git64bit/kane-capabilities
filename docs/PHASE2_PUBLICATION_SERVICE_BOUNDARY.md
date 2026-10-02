# Phase 2 Publication Service Boundary

## Status

**VALIDATION-ONLY SERVICE DEPLOYED — first real IPFS side effect still gated**

This document defines the minimum boundary for the first Phase 2 publication service and records the accepted validation-only deployment state.

The bounded publication service is reachable through the production Orchestrator route, but Kubo publication and swarm participation remain disabled.

The first real end-to-end Civic operation remains:

```text
publication.publish
```

The implementation service is a new publication/IPFS node.

## Authority

The publication node is **not** a Civic authority.

It may:

- accept an already-authorized bounded publication request from CT105;
- store exact bytes;
- add/pin exact content in Kubo/IPFS;
- return content identity and bounded publication evidence;
- retrieve/verify content it owns.

It may not:

- decide who is allowed to publish;
- reinterpret Civic workflow policy;
- mint participant standing;
- modify source content;
- possess firmware signing keys;
- execute arbitrary Kubo RPC for callers.

CT105 remains the workflow/authorization coordinator.

## State ownership

The publication node owns only publication-service state:

- Kubo repository state;
- local pin state;
- bounded publication job/result metadata where required;
- service-local diagnostics.

CT105 owns:

- workflow state;
- authorization decision;
- service-selection evidence;
- Civic receipt/audit chain;
- the participant-linked publication record and its relationship to the exact artifact/service result.

The structured publication/document catalog may use PostgreSQL in the Kane reference deployment. The publication node does not own participant document semantics.

Git/Gitea remains source/revision authority where source artifacts originate there.

## Failure domain

Compromise or failure of the publication node must not:

- grant new Civic authority;
- allow arbitrary CT105 operations;
- expose firmware signing authority;
- mutate Gitea source history;
- silently convert failed publication into successful Civic evidence.

The publication operation must fail closed if returned content identity cannot be verified against the submitted bytes.

## Interface

The service boundary must expose a bounded adapter contract for publication semantics.

It must not expose generic:

```text
kubo.rpc
shell.exec
ssh.run
filesystem.write
http.proxy
```

The first implementation may use Kubo internally, but Kubo remains behind the service adapter.

## Initial deployment decision

Use the isolated Debian Trixie publication CT on the OVH Proxmox 9 host. This node is explicitly **not** placed on `srv-b`.

The service is deployed in validation-only mode. Enabling Kubo side effects is a later acceptance gate.

The retired historical IPFS node is not part of the target architecture and should not become an authority source.

Do not import its full state.

Only explicitly required content may later be re-pinned after verification.

## Network posture

Initial service exposure remains private to the Civic service network.

No public gateway or unrestricted Kubo API is required for the first acceptance gate.

The publication/IPFS CT has no public `vmbr0` interface.

## Swarm posture

The first `publication.publish` implementation does **not** require IPFS swarm participation.

Kubo is initially used only for:

- deterministic content addressing;
- local repository storage;
- local pinning;
- read-back verification by CID.

Initial deployment therefore disables or avoids:

- public swarm listeners;
- DHT participation;
- mDNS/local peer discovery;
- relay/autonat/hole-punch behavior;
- public gateway exposure.

The Kubo RPC/API is bound only to loopback inside the publication CT and is accessed only by the bounded publication service.

If later Civic distribution requires peer replication, swarm participation is a separate architecture/network gate. It must be justified by a concrete distribution requirement rather than enabled merely because Kubo supports it.

## Frozen first-operation contract

The current implementation is deliberately limited to **inline artifacts of at most 1 MiB**.

This is an implementation limit for the first bounded adapter path, not a statement about the eventual participant document model. It deliberately avoids introducing streaming uploads, object storage, repository-fetch semantics, or upload sessions before a concrete need exists.

### Public `publication.publish` input

The Civic request carries:

```text
artifact.media_type
artifact.size_bytes
artifact.sha256
artifact.encoding = base64
artifact.content
optional label   # current v1 compatibility field; not used by the Usermin thin client
```

Authority:

`schemas/publication-publish-input-v1.schema.json`

The current v1 label is descriptive only and does not participate in content identity. It is not purpose, retention, path, version, or lifecycle metadata. The thin Usermin adapter does not expose or populate it; contract cleanup may remove or supersede it before participant-facing side effects are enabled.

### CT105 -> publication-service request

After CT105 accepts and authorizes the Civic workflow, its service adapter sends:

```text
contract_version = 1
workflow_id
operation = publication.publish
artifact
```

Authority:

`schemas/publication-service-request-v1.schema.json`

Caller identity, client identity, and Civic authorization policy are intentionally not forwarded as service-side authority. CT105 has already made the authorization decision and records it in the Civic workflow evidence.

### Integrity rule

A publication service must independently perform all of the following before publication:

1. strict base64 decode;
2. decoded byte count equals `size_bytes`;
3. SHA-256 of decoded bytes equals `sha256`.

After Kubo adds and pins the content, the service must read the artifact back by the returned CID and verify the exact byte count and SHA-256 again.

A success response is prohibited unless both pre-publication and post-publication verification succeed.

CT105 must verify that the service result repeats the expected `sha256` and `size_bytes` before completing the Civic workflow.

### Kubo content-identity profile

The first implementation fixes the Kubo add profile so the same bytes produce the same publication identity across conforming nodes:

```text
CID version     1
multihash       sha2-256
raw leaves      true
chunker         size-262144
pin             true
CID rendering   base32
```

These are service implementation parameters, not caller-selectable Civic request fields.

### Successful service result

The publication service returns:

```text
contract_version = 1
workflow_id
operation = publication.publish
sha256
size_bytes
cid              CIDv1, base32
pinned = true
verified = true
```

Authority:

`schemas/publication-service-result-v1.schema.json`

The CID is publication evidence. The SHA-256 remains the exact-byte integrity identity supplied by the Civic request.

### Service failure classes

The bounded service contract exposes only:

```text
invalid-request
integrity-mismatch
publication-failed
verification-failed
service-unavailable
```

Authority:

`schemas/publication-service-failure-v1.schema.json`

The publication service does not expose raw Kubo errors as Civic semantics. Implementation diagnostics may retain them locally.

### Retry and idempotency ownership

CT105 owns Civic request replay and idempotency.

The publication service does not require a second idempotency database for the first implementation.

A repeated CID does not collapse publication provenance. Separate authorized workflows may produce distinct participant publication records even when the exact bytes resolve to the same CID.

A retry of the same exact artifact is safe because:

- the fixed content profile produces the same CID;
- pinning an already-pinned CID is idempotent;
- the service repeats exact-byte verification before returning success.

The same artifact may legitimately be published by different Civic workflows and resolve to the same CID.


### Retention and pinning semantics

The participant does not have to choose pin duration or retention intent when invoking `publication.publish`.

The publication service follows the current deployment default for Civic-controlled pin state. A later heavy client may request explicit pin/unpin/retire lifecycle changes through bounded Civic operations once those contracts are frozen.

Unpinning Civic-controlled infrastructure must never be represented as guaranteed global deletion from IPFS.

### Service-local persistence

No additional SQL/service job database is required for the first implementation.

The publication node persists:

- the Kubo repository;
- pin state;
- ordinary service diagnostics/logs.

CT105 persists the authoritative Civic workflow, authorization decision, audit events, receipt, and service result.

If later requirements show that publication jobs need durable independent state, that is a new design decision rather than an assumption in the first node.

### Private transport

The first service adapter uses ordinary HTTP/JSON on the private Civic service network.

Initial endpoints:

```text
GET  /healthz
POST /v1/publications
```

The bounded publication service binds only to its private CT address. The initial network rule permits Kane CT105 to reach that service endpoint and does not expose the Kubo API publicly. Kubo itself remains loopback-only inside the publication CT.

TLS, service credentials, or stronger adapter authentication may be added when the production trust boundary requires them. They are not prerequisites for proving the first bounded operation on the isolated service network.

## Validation-only acceptance state

Accepted on 2026-10-01:

1. bounded publication request/result/failure contracts;
2. exact byte-integrity validation;
3. deterministic content-identity profile;
4. CT105-owned replay/idempotency;
5. bounded service failure classes;
6. no extra service-local SQL database;
7. private HTTP/JSON service transport;
8. production Orchestrator routing to the validation-only backend;
9. persisted workflow/audit/receipt evidence for the expected no-side-effect failure;
10. Kubo and swarm side effects remain disabled.

No additional capability namespace is introduced by the publication node.

Before real participant-facing publication, the remaining gates are the trusted interaction-adapter boundary, authenticated Orchestrator transport, and the first Kubo side-effect acceptance. The file-only Usermin surface is defined in `PHASE3_USERMIN_ADAPTER_BOUNDARY.md`; the broader publication/document lifecycle is defined in `PUBLICATION_DOCUMENT_MODEL.md`.
