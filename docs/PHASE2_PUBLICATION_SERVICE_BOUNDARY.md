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

## Phase 2 acceptance gates before deployment

Before assigning a CT number or installing Kubo, freeze:

1. `publication.publish` request fields required by the service adapter;
2. exact byte-integrity verification rule;
3. returned content-identity/result fields;
4. ownership of retry/idempotency behavior;
5. service failure classes visible to CT105;
6. whether publication metadata needs persistent service-local storage beyond Kubo;
7. private transport between CT105 and the publication node.

No additional capability namespace is introduced by this node.
