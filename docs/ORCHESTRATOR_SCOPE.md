# Orchestrator Scope Rule

## Purpose

A Civic Orchestrator is a reusable architectural pattern, not a universal central orchestrator for every Civic Infrastructure application.

Each orchestrator coordinates one bounded authority/workflow domain.

A new application or service does not join an existing orchestrator merely because it is part of Civic Infrastructure or uses compatible transport technology.

## Admission rule

A component belongs behind or in front of an existing orchestrator only when it participates in the same bounded civic authority, workflow, authorization, and evidence domain.

A component should use a separate orchestrator when it belongs to a materially different authority/workflow domain, including different:

- domain-authoritative state;
- policy authority;
- workflow semantics;
- trust roots;
- service lifecycle;
- failure domain.

Identity, standing, membership, or qualification state remains with the authority that owns it; CT105 may consume an authenticated assertion for authorization without becoming its authoritative store.

Technology is not the admission criterion.

A cjdns-based component may legitimately integrate with the Kane Civic Orchestrator when it serves the same bounded Kane civic workflow domain. A utility or module may exchange data with Civic Infrastructure without becoming part of CT105's business logic.

## Shared architectural pattern

Independent orchestrators may share the same design discipline:

- named semantic operations rather than remote commands;
- bounded capability namespaces;
- explicit caller and authentication provenance;
- explicit service authority;
- deterministic workflow state rules;
- audit evidence;
- receipts;
- incident/signal separation;
- fail-closed behavior;
- portable public contracts;
- no generic shell, SSH, SQL, signing, or HTTP-proxy escape hatch.

Sharing the pattern does not make their policy, membership, state, or trust domains interchangeable.

## State and authority separation

An orchestrator may be an authorization decision point without becoming the authoritative identity or membership database.

Where membership or qualification matters, the preferred relationship is:

```text
identity / membership authority
        |
        v
authenticated assertion or claim
        |
        v
domain orchestrator
        |
        v
authorization decision and workflow
```

The owning identity or membership authority remains explicit.

## Replication rule

A future operator or application may model its own orchestrator after this repository while replacing:

- capability namespaces;
- operation registry;
- domain services;
- authorization policy;
- workflow definitions;
- identity/membership authorities;
- deployment topology.

It should preserve the architectural invariants only where they remain relevant to that domain.

## Anti-monolith rule

Do not add a capability to CT105 merely because another Civic Infrastructure project needs it.

Before admitting a new client or service, answer:

1. Does it participate in the same Kane civic authority/workflow domain?
2. Does CT105 already own the relevant cross-service workflow semantics?
3. Can its authority remain independently bounded?
4. Would integration avoid importing unrelated membership, policy, or domain state into CT105?

If the answer to the first or fourth question is unfavorable, use a separate orchestrator.


## Inter-domain evidence exchange

Orchestrators do not federate through remote operation calls, shared workflow state, distributed authorization, or knowledge of another domain's business rules.

**Orchestrators do not federate. Evidence may.**

Autonomous domains may publish and consume self-describing, schema-versioned, signed claims through ordinary publication and verification mechanisms. The receiving domain verifies the evidence locally and applies its own policy locally.

If a receiver must know the sender's internal rules to interpret a record, business logic has leaked across the domain boundary.

This rule does not create a `federation.*` capability namespace.
