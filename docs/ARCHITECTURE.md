# Civic Orchestrator Architecture

## Role

The Civic Orchestrator is the shared service-control layer between interaction surfaces and specialized Civic Infrastructure services.

It is neither the universal datastore nor the universal authority.

```text
Interaction surfaces                  Civic Orchestrator                 Service / trust plane

Usermin CLI/TUI -----------+
Hubzilla addon ------------+
Kane Fabric browser -------+------> contract validation -----------> Kane Fabric authority
Gitea integration ---------+        authorization                  -> IPFS/Kubo
mail-driven adapter -------+        workflow transitions           -> RAG/retrieval
future clients ------------+        routing                        -> annales inference
                                    provenance                     -> firmware signer
                                    audit                           -> ESP32 management
                                    receipts                       -> other bounded services
```

## Ownership rule

### Interaction surfaces retain

- local user interface;
- local identity/session integration;
- local storage and preferences;
- domain behavior that is intrinsically client-side;
- presentation.

Examples:

- Usermin retains Unix account and shell behavior.
- Hubzilla retains channels, posts, comments, federation, and addon UI.
- Kane Fabric retains browser-side artifact verification, map composition, rendering, inspection, and source-neutral acquisition logic.
- Gitea retains Git repositories, commits, revisions, and editable source history.

### The orchestrator owns

- operation contracts;
- cross-service authorization decision points;
- workflow instances and allowed transitions;
- service selection/routing;
- cross-service provenance;
- audit;
- receipts;
- idempotency and replay protection where required;
- backend-independent result semantics.

### Specialized services retain

- domain-authoritative state;
- protected keys/secrets;
- implementation-specific data;
- backend lifecycle;
- service-specific acceptance rules.

## Semantic boundary

The orchestrator API describes **Civic actions**.

Good:

- `publication.publish`
- `geography.compare_candidate`
- `geography.promote`
- `rag.query`
- `firmware.request_signature`
- `edge.request_update`

Rejected as top-level Civic operations:

- `shell.exec`
- `ssh.run`
- `sqlite.execute`
- `kubo.pin_add`
- `git.command`

Backend adapters may internally perform implementation-specific work, but those mechanics do not become public Civic semantics.

## Trust principle

Coordination does not imply possession of authority.

A workflow may require an isolated signer, geographic authority, repository authority, or participant-controlled edge. CT105 coordinates the request and records the result while the owning service retains the power to independently refuse it.

This property is essential for protected signing operations:

```text
compromise of orchestrator != possession of signing key
```

## State principle

The orchestrator stores only state required to coordinate workflows and prove their history. It must not silently become the exclusive custodian of:

- participant publications;
- county geographic source truth;
- Git source truth;
- private RAG corpus data;
- firmware signing keys;
- Hubzilla social content;
- Portal home directories or mailboxes.

## Initial execution model

Phase 1 uses a small deterministic state machine and fail-closed service stubs.

No general-purpose arbitrary scripting facility is exposed through the public operation contract.

A mature workflow engine may later execute internal workflow definitions if measured complexity justifies it, but the external Civic contracts must not depend on that engine.


## Portability principle

Kane County is the reference deployment. The orchestrator architecture is not Kane County-specific.

A conforming independent operator may replace jurisdiction data sources, hostnames, accounts, trust roots, source adapters, physical hosts, and service placement while preserving the public Civic contracts and capability boundaries.

Reference deployment locators such as CT numbers, `srv-b`, and `annales` must not become durable protocol identity.

See `PORTABILITY_AND_TRUST.md`.

## Non-monetary cryptographic trust

Cryptographic mechanisms in Civic Infrastructure establish evidence, integrity, authorization, provenance, or software trust.

They do not create currency, utility-token value, ownership interest, or transferable governance weight.

A blockchain or token system is not part of the required architecture. Any future proposal for one must demonstrate a concrete Civic requirement that cannot be met adequately by simpler signed records, append-only logs, content addressing, WORM storage, replication, or independent witnesses.

## Appliance direction

The long-term deployment model should remain compatible with a network-bootstrapped appliance that can discover deployment configuration, verify trust roots, obtain public contracts and jurisdiction adapters, configure services, and prove conformance.

This is a portability target, not a requirement to design the appliance during the initial orchestrator milestones.
