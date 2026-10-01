# v0.1.0-alpha.2 — Civic Orchestrator Phase 1 Baseline Maintenance

**Status:** pre-production / non-production reference release

**Date:** 2026-10-01

This release is a maintenance correction to `v0.1.0-alpha.1`.

It does not change the Civic Orchestrator public contracts, capability namespaces, workflow semantics, or domain architecture.

## Correction

The Phase 1 baseline used Python's `sqlite3.Connection` context manager as though it also closed the database connection.

It does not: the context manager commits or rolls back the transaction but leaves connection closure to the caller.

`v0.1.0-alpha.2` corrects that lifecycle boundary.

## Changes

- `StateStore._connect()` now owns and explicitly closes every SQLite connection it opens.
- Existing commit/rollback behavior is preserved.
- Existing `BEGIN IMMEDIATE` transaction behavior is preserved.
- The read-only SQLite connection in the Phase 1 acceptance harness is explicitly closed.
- New regression tests exercise accepted requests, replay, conflict rollback, rejected-request diagnostics, workflow evidence, transition helpers, and audit helpers.
- Resource-warning coverage verifies that database connections do not leak to garbage collection.

## Acceptance

```text
33 regression tests                  PASS
persistent CT105 acceptance          PASS
listener 127.0.0.1:8045 only         PASS
side_effects=false                    PASS
```

## Compatibility

This is the preferred non-production reference baseline for new orchestrator implementations.

Projects based on `v0.1.0-alpha.1` need only carry the SQLite lifecycle correction; no contract migration is required.

The architectural rule remains:

> Orchestrators do not federate. Evidence may.
