# Capability Boundaries

## Purpose

This document defines the initial capability namespaces and the powers CT105 is allowed to expose.

A namespace is a semantic boundary, not permission to implement every conceivable action beneath it.

## Initial namespaces

### `publication.*`

Intended for exact-artifact publication, verification, pin/distribution requests, and receipts.

Must not expose arbitrary Kubo/IPFS RPC.

### `geography.*`

Intended for Kane Fabric source refresh, candidate creation, comparison, reconciliation, explicit promotion, compilation, and publication coordination.

Kane Fabric remains geographic authority.

### `participant.*`

Intended for bounded participant-publication workflows, validation, discovery, and composition-support operations.

Participant identity must remain separate from physical edge identity.

### `repository.*`

Intended for exact Gitea repository/commit/path references, approved source retrieval, controlled metadata callbacks, and publication record integration.

Must not expose a generic Git shell.

### `rag.*`

Intended for retrieval/context operations over authorized corpus/index state.

Must not silently grant inference access or bypass visibility/authorization rules.

### `inference.*`

Intended for bounded model-inference requests to an isolated inference service such as `annales`.

The orchestrator coordinates context and provenance; inference nodes need not own long-lived Civic state.

### `edge.*`

Intended for ESP32-S3 or other conforming edge enrollment, state observation, artifact synchronization, update coordination, replacement, and recovery.

Physical device identity is not civic participant identity.

### `firmware.*`

Intended for firmware artifact lifecycle, candidate identity, release metadata, rollout policy, and update coordination.

### `signing.*`

Intended for bounded requests to protected signing authorities.

CT105 must not possess protected signing private keys merely because it coordinates signing workflows.

### `audit.*`

Intended for audit queries, receipt verification, workflow history, and conformance evidence.

Audit access remains subject to classification and authorization.

## Explicitly prohibited generic capabilities

The public orchestrator contract must not contain general operations equivalent to:

- arbitrary command execution;
- arbitrary SSH;
- arbitrary filesystem access;
- arbitrary SQL;
- arbitrary Git commands;
- arbitrary HTTP proxying;
- arbitrary IPFS/Kubo RPC;
- arbitrary signing of caller-supplied bytes;
- arbitrary LLM tool execution.

If a legitimate Civic workflow requires an implementation-specific action, that action belongs inside a bounded service adapter behind a named Civic capability.
