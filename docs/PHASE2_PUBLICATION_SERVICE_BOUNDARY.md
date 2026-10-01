# Phase 2 Publication Service Boundary

## Status

**DESIGN GATE — no service deployment yet**

This document defines the minimum boundary for the first Phase 2 service node.

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
- Civic receipt/audit chain.

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

Create a **new Debian Trixie unprivileged CT** on the existing OVH Proxmox 9 host.

The retired historical IPFS node is not part of the target architecture and should not become an authority source.

Do not import its full state.

Only explicitly required content may later be re-pinned after verification.

## Network posture

Initial service exposure should remain private to the Civic service network.

No public gateway or unrestricted Kubo API is required for the first acceptance gate.

Exact network placement and firewall rules are assigned only after the service contract is frozen.

## Frozen first-operation contract

The first implementation is deliberately limited to **inline artifacts of at most 1 MiB**.

This is sufficient for the first Civic publication targets such as policy text, manifests, attestations, and other small immutable records. It deliberately avoids introducing streaming uploads, object storage, repository-fetch semantics, or upload sessions before a concrete need exists.

### Public `publication.publish` input

The Civic request carries:

```text
artifact.media_type
artifact.size_bytes
artifact.sha256
artifact.encoding = base64
artifact.content
optional label
```

Authority:

`schemas/publication-publish-input-v1.schema.json`

The label is descriptive only. It does not participate in content identity.

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

A retry of the same exact artifact is safe because:

- the fixed content profile produces the same CID;
- pinning an already-pinned CID is idempotent;
- the service repeats exact-byte verification before returning success.

The same artifact may legitimately be published by different Civic workflows and resolve to the same CID.

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

The service binds only to its private CT address. The initial network rule permits CT105 to reach the publication endpoint and does not expose the Kubo API or service endpoint publicly.

TLS, service credentials, or stronger adapter authentication may be added when the production trust boundary requires them. They are not prerequisites for proving the first bounded operation on the isolated service network.

## Pre-deployment gate status

The required design questions are now frozen:

1. publication request fields — **FROZEN**;
2. exact byte-integrity rule — **FROZEN**;
3. returned content identity/result — **FROZEN**;
4. retry/idempotency ownership — **FROZEN: CT105**;
5. bounded service failure classes — **FROZEN**;
6. extra service-local database — **NO for first implementation**;
7. private transport — **FROZEN: HTTP/JSON on private service network**.

No additional capability namespace is introduced by this node.

The next step may assign the new Trixie CT identity and deploy the publication service without revisiting these decisions unless testing exposes a concrete defect.
