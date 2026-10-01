# Phase 1H External Review Hardening

## Status

**ACTIVE** — implementation committed; CT105 acceptance pending.

This pass follows an independent cold review by a prospective consumer of the Civic Orchestrator architectural pattern.

The review was useful precisely because that consumer was not part of the original Phase 1 design.

## Scope decision

The Mechanical Compiler is **not** a client of this Kane Orchestrator.

It may use its own orchestrator modeled after this repository.

Accordingly, Phase 1H does not add Mechanical Compiler groups, membership policy, or domain operations to CT105.

The architectural correction is instead:

> one orchestrator coordinates one bounded authority/workflow domain.

See `ORCHESTRATOR_SCOPE.md`.

## Review items accepted

### Signing baseline

Corrected the Kane node-placement document to the current software-signer baseline.

The invariant retained is:

```text
compromise of CT105
    != possession of signing authority
    != automatic ability to sign arbitrary firmware
```

Phase 7 is explicitly signing **integration**, not a prohibition on building/testing the signing authority earlier.

### Workflow identifier wording

Removed the incorrect claim that UUID workflow identifiers are deterministic.

Workflow IDs are opaque/unique; the workflow transition rules are deterministic.

### Caller and client identity

Replaced the fixed application-name interface enum with two concepts:

```text
caller.subject
caller.authority
caller.authenticated_by

client.id
client.kind
```

Authentication provenance is required.

Client IDs are extensible and do not require a schema revision for each legitimate future program.

Client extensibility does not grant admission to CT105; scope admission remains separate.

### Replay and idempotency

`request_id` and optional `idempotency_key` are no longer ignored.

The Phase 1H stub runtime:

- replays the original result for an equivalent retry;
- does not create a second workflow/audit trail/receipt on replay;
- returns `409 conflict` when a request ID or idempotency key is reused for different semantics.

### Failure envelopes

Failure construction now normalizes untrusted request IDs and operation names, limits messages to the schema maximum, and validates the final failure envelope.

HTTP request parsing failures and unexpected request-processing exceptions now return contract-valid failure envelopes rather than ad-hoc `{"error": ...}` responses or an empty connection.

### Timestamp validation

JSON Schema date-time formats are now enforced with `FormatChecker`.

### Registry and workflow validation

The operation registry and stub workflow definition now have schemas and are validated at runtime startup.

The stub workflow contributes its authorization policy and accepted namespaces to runtime behavior.

### Audit ordering

Audit events now carry an explicit increasing `sequence` within each workflow.

Legacy CT105 events are backfilled during the additive SQLite migration.

Evidence retrieval orders by sequence rather than timestamp plus random UUID.

### Transactional persistence

A normal accepted Phase 1H stub request is persisted inside one SQLite `BEGIN IMMEDIATE` transaction:

- workflow;
- authorization decision;
- ordered audit events;
- receipt;
- replay result.

A failure before commit rolls back the request record rather than intentionally leaving a partial evidence chain.

Standalone transition/audit helpers remain for diagnostics/tests and also serialize state mutation with immediate transactions.

### Effect scope

The ambiguous `side_effect_class: none|bounded` field was replaced by:

- `none`
- `orchestrator-state`
- `external-bounded`

Actual Phase 1H execution remains `side_effects=false`.

### JSON Schema portability

Schema cross-references now use absolute Civic URNs.

Runtime validation uses `referencing.Registry` rather than deprecated `RefResolver`.

### Housekeeping

- README no longer claims implementation code is absent.
- Python cache artifacts are ignored.
- pre-reset capability inventory is explicitly historical, not active authority.
- repository naming remains an explicit later decision rather than an incidental rename.

## Claim correction

The former "interface equivalence" gate is now described more narrowly as client-semantics equivalence.

It proves that declared client identity does not alter Civic operation semantics while client identity remains visible in evidence.

It does not prove real Usermin, Hubzilla, and Kane Fabric adapters behave equivalently. That remains Phase 3 work.

## CT105 acceptance still required

Before Phase 1H closes, CT105 must prove:

1. the full test suite passes;
2. the existing persistent SQLite database migrates additively;
3. legacy audit events receive valid sequence numbers;
4. a fresh request records caller authentication/client identity;
5. exact replay returns the original workflow and receipt;
6. conflicting replay returns `409`;
7. malformed timestamp is rejected;
8. HTTP malformed JSON returns a valid failure envelope;
9. service remains loopback-only and side-effect-free.

Phase 2 does not begin until these gates pass.
