# v0.1.0-alpha.1 — Civic Orchestrator Phase 1 Baseline

**Status:** pre-production / non-production reference release

**Date:** 2026-10-01

This release freezes the completed Phase 1 Civic Orchestrator baseline after two external review passes and persistent CT105 acceptance.

## Intended use

This release is suitable as a reference implementation for another bounded Civic Infrastructure orchestrator.

It is **not** a production orchestrator release and contains no production service adapters.

A downstream project should copy the architectural pattern, not inherit Kane-specific domain policy.

## Architectural invariants

- one orchestrator coordinates one bounded authority/workflow domain;
- Civic operations are semantic operations, not generic remote commands;
- workflow coordination does not confer backend authority;
- caller identity, authentication provenance, and client identity are distinct;
- service/domain authorities remain independently bounded;
- audit evidence and receipts are explicit;
- unknown or invalid operations fail closed;
- cryptography is evidence/authorization infrastructure, not an economy;
- orchestrators do not federate through RPC or shared workflow state;
- evidence may be exchanged through self-describing signed publication and local verification.

## Phase 1 runtime

The baseline provides:

- HTTP/JSON request handling;
- OpenAPI 3.1 description;
- JSON Schema 2020-12 contracts;
- bounded operation registry;
- validated declarative stub workflow;
- authorization-decision evidence;
- deterministic state-transition rules;
- explicit service selection evidence;
- monotonic per-workflow audit sequence;
- receipts;
- replay/idempotency handling;
- caller/client-scoped request identities;
- minimal diagnostics for rejected/conflicting/replayed requests;
- transactional accepted-request persistence;
- read-only workflow evidence retrieval;
- SQLite additive migration;
- loopback-only systemd service profile.

## Portability

- public schemas use stable Civic URNs;
- `schemas/catalog-v1.json` maps URNs to repository files;
- package metadata declares runtime dependencies;
- clean `pip install .` is accepted;
- Kane hostnames, CT numbers, signing implementation, and topology are reference-deployment details rather than public contract requirements.

## Deliberately absent

This release does not provide:

- production publication;
- production signing;
- production geography operations;
- RAG/inference integration;
- production Usermin/Hubzilla/Kane Fabric adapters;
- module-specific membership or qualification logic;
- peer-orchestrator RPC;
- `federation.*` capability;
- distributed workflow state;
- production authentication binding for `authenticated_by` or `client.id`.

Production adapter authentication must bind those assertions before the corresponding adapter is trusted.

## Acceptance

Final accepted state:

```text
30 regression tests                  PASS
persistent CT105 acceptance          PASS
clean package installation/import    PASS
listener 127.0.0.1:8045 only         PASS
side_effects=false                    PASS
```

The next engineering step for the Kane reference deployment should make one narrowly bounded operation work end to end rather than introduce another general hardening phase.
