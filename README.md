# Kane Capabilities

Kane Capabilities defines the **Civic Orchestrator contract and capability boundary** for the Civic Infrastructure stack.

The repository is not a collection of application use cases and it is not the implementation repository for Kane Fabric, Hubzilla, Usermin, Gitea, IPFS, RAG/LLM, ESP32-S3 firmware, or the signing authority.

Its purpose is narrower:

> define how independent Civic Infrastructure surfaces request bounded civic operations, how those operations are authorized and advanced through workflows, and how specialized services are reached without exposing their implementation details to callers.

The reference orchestrator is CT105 `civic-orchestrator` on `srv-b`.

## Architectural position

```text
Usermin thin publication ----+
Hubzilla addon ---------------+
Kane Fabric heavy client -----+----> Civic Orchestrator ----> specialized services
Gitea integration ------------+
mail-driven adapters ---------+
future interfaces ------------+
```

The orchestrator is the fusebox between interaction surfaces and service/trust nodes. It owns cross-cutting workflow semantics, not the local responsibilities of those systems.

## Core rules

1. **Civic operations, not remote commands.** Callers request operations such as publication, verification, promotion, retrieval, signing, or edge lifecycle actions. They do not request arbitrary shell commands, SSH sessions, Kubo RPC methods, SQL statements, or backend-specific procedures.
2. **Reuse mature protocols.** The project does not invent a new network protocol merely to serialize JSON. HTTP, OpenAPI, JSON Schema, and CloudEvents are the initial standards baseline.
3. **Fail closed.** Unknown operations, unavailable backends, missing authority, invalid state transitions, and unimplemented adapters must not produce side effects.
4. **Keep client roles explicit.** Usermin remains a thin quota-bounded working-storage/publication surface; Hubzilla remains a social/image surface; Kane Fabric may be a heavy management client; Gitea remains a revision mechanism. Shared policy, publication/document catalog semantics, and cross-service workflow logic belong centrally.
5. **Separate workflow authority from service authority.** The orchestrator may coordinate signing, publication, geographic promotion, inference, or edge updates without possessing every backend's private authority.
6. **No implementation technology becomes civic identity.** Hostnames, ESP32 hardware identity, Git repositories, Unix accounts, service URLs, and transport endpoints are locators or implementation details unless an explicit civic contract says otherwise.
7. **Kane County is the reference deployment, not the product boundary.** Public contracts must be implementable by an independent operator in another jurisdiction without Kane County private infrastructure.
8. **Cryptography is evidence infrastructure, not an economy.** Hashes, signatures, capabilities, receipts, attestations, and certificates establish identity, integrity, authorization, and provenance; they do not imply currency, utility-token value, ownership, or transferable governance weight.
9. **One orchestrator, one bounded authority/workflow domain.** Civic Infrastructure applications do not all plug into CT105. Independent applications may adopt the same orchestrator pattern while retaining separate state, membership, policy, trust, and workflow authority.

## Repository authority

Start with:

1. [ROADMAP.md](ROADMAP.md)
2. [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)
3. [docs/CONTRACT_STACK.md](docs/CONTRACT_STACK.md)
4. [docs/CAPABILITY_BOUNDARIES.md](docs/CAPABILITY_BOUNDARIES.md)
5. [docs/NODE_DESIGN_GATES.md](docs/NODE_DESIGN_GATES.md)
6. [docs/PORTABILITY_AND_TRUST.md](docs/PORTABILITY_AND_TRUST.md)
7. [docs/REFERENCE_TOPOLOGY.md](docs/REFERENCE_TOPOLOGY.md)
8. [docs/KANE_NODE_PLACEMENT.md](docs/KANE_NODE_PLACEMENT.md)
9. [docs/DEMONSTRATOR.md](docs/DEMONSTRATOR.md)
10. [docs/ORCHESTRATOR_SCOPE.md](docs/ORCHESTRATOR_SCOPE.md)
11. [docs/PHASE1H_HARDENING.md](docs/PHASE1H_HARDENING.md)
12. [docs/PUBLICATION_DOCUMENT_MODEL.md](docs/PUBLICATION_DOCUMENT_MODEL.md)
13. [docs/INTERACTION_STORAGE_BOUNDARIES.md](docs/INTERACTION_STORAGE_BOUNDARIES.md)
14. [docs/PHASE3_USERMIN_ADAPTER_BOUNDARY.md](docs/PHASE3_USERMIN_ADAPTER_BOUNDARY.md)
15. [docs/CT105_PHASE2_PUBLICATION_ACCEPTANCE.md](docs/CT105_PHASE2_PUBLICATION_ACCEPTANCE.md)
16. [docs/EXTERNAL_REVIEW_HANDOFF.md](docs/EXTERNAL_REVIEW_HANDOFF.md)

The repository contains the accepted Phase 1 contract-bearing runtime and the accepted Phase 2 validation-only `publication.publish` path. The publication backend is reachable through the bounded service adapter, but Kubo/IPFS side effects remain disabled. Phase 3 is in staged implementation and production acceptance: U-001 is accepted; the U-002 local broker is implemented in the repository but is not yet production-accepted; CT105 authenticated-adapter ingress and separate CT105-to-publication-service authentication primitives are implemented in the repository; broker-to-CT105 integration, live credential provisioning, and U-004 validation-only end-to-end acceptance remain pending. The Phase 4 participant publication budget control is also implemented in the repository with atomic CT105 accounting and deployment-policy loading, while Kane-specific limits and live acceptance remain pending.

The Civic Infrastructure Demonstrator is a parallel deployment profile for grant evaluation and conformance. It uses synthetic/resettable data but the same public contracts as the production architecture.


## Repository history

The pre-reset Kane Fabric capability inventory remains available in Git history for provenance and archaeology, but it is not current contract authority. The files listed above define the active architecture and contracts.

The repository name `kane-capabilities` is retained during the current Kane reference deployment. Whether it should later be renamed to reflect the portable Civic Orchestrator product boundary remains an explicit naming decision, not a contract change.
