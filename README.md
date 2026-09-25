# kane-capabilities

Finite, cryptographically controlled capabilities for Kane Fabric, representing bounded rights, attestations, opportunities, and responsibilities with verifiable issuance, exercise, expiration, and evidence binding.

## Milestone 0 — Capability Semantics

The first milestone defines the abstract Kane Capability and its lifecycle before any implementation work begins.

The project starts from one principle:

> A capability represents a bounded right, opportunity, or responsibility. It is not money.

The initial model defines only:

- issuer
- holder
- purpose
- validity interval
- quantity
- state
- evidence reference
- signatures

The initial lifecycle is:

```text
AUTHORIZED
    |
  ISSUED
    |
  ACTIVE
   /   \
EXERCISED EXPIRED
```

The initial conservation invariant is:

```text
AUTHORIZED = UNISSUED + ACTIVE + EXERCISED + EXPIRED
```

See [docs/capability-model.md](docs/capability-model.md).

## Capability inventories

- [Kane Fabric Use-Case Inventory](docs/kane-fabric-use-case-inventory.md)
- [RAG / Email and Ceremony Capabilities](docs/rag-email-ceremony-capabilities.md)

## Explicit non-goals for Milestone 0

Milestone 0 does **not** define or implement:

- Pi integration
- Stellar integration
- IPFS publishing or pinning mechanics
- smart contracts
- wallets
- voting logic
- witness-attestation logic
- user interfaces
- Annales integration
- production serialization
- network protocols

These are intentionally deferred until the capability semantics are stable.
