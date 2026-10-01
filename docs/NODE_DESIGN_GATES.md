# Service and Trust Node Design Gates

## Rule

A new node is created because a capability requires a distinct boundary, not because a product traditionally runs on its own server.

Before adding or co-locating a service, answer each gate.

## 1. State ownership

- What authoritative state does the service own?
- Is that state mutable, append-only, or immutable?
- Could another node safely reconstruct it?

## 2. Trust and secrets

- What secrets or private keys exist?
- What happens if CT105 is compromised?
- Must the service independently reject unauthorized requests?
- Does co-location collapse a protection boundary?

## 3. Network exposure

- Which callers need access?
- Is the service internet-facing, service-network-only, or host-mediated?
- Does it require inbound participant connectivity?
- Can the orchestrator broker access instead?

## 4. Failure domain

- What must continue if this service fails?
- Could failure corrupt another authority if co-located?
- Is independent restart/recovery required?

## 5. Resource profile

- CPU, RAM, persistent storage, flash/artifact storage;
- burst versus steady workload;
- hardware-specific requirements.

## 6. Lifecycle

- update mechanism;
- rollback;
- backup/restore;
- replacement;
- key rotation;
- disaster recovery.

## 7. Orchestrator contract

- exact capability namespace;
- request schema;
- result schema;
- authorization requirements;
- idempotency semantics;
- timeout/retry behavior;
- audit/receipt requirements.

## 8. Co-location decision

Only after the previous gates are answered decide whether the service:

- belongs inside CT105;
- belongs in an existing node;
- requires a new isolated node;
- belongs on `annales`;
- belongs on a participant-controlled edge;
- should remain external.

## Initial node-design targets

The first topology review must cover:

1. Kane Fabric geographic authority/runtime;
2. Wiregate / secure browser origin;
3. Gitea source authority;
4. IPFS/Kubo publication service;
5. RAG state/retrieval/index service;
6. `annales` inference service;
7. protected firmware/civic signing authority;
8. ESP32-S3 management/synchronization service.

No deployment decision in this list is implied by its presence here.
