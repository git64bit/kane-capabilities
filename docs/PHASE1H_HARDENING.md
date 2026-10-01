# Phase 1H External Review Hardening

## Status

**ACCEPTED** on 2026-10-01.

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

`authenticated_by` is required as an adapter-supplied provenance assertion. Phase 1 records the assertion but does not independently verify the subject or bind the declared client identity to a transport credential.

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

## CT105 acceptance

The persistent CT105 deployment passed all Phase 1H gates:

```text
unit/regression suite       21 tests, PASS
persistent DB migration     PASS
legacy audit backfill       PASS
caller authenticated_by field recorded  PASS
extensible client identity  PASS
exact replay                PASS
conflicting replay          409 conflict, PASS
RFC3339 timestamp rejection PASS
malformed JSON envelope     PASS
listener                    127.0.0.1:8045 only
side_effects                false
```

A pre-Phase-1H SQLite backup was taken before migration.

The acceptance harness completed with:

```json
{
  "phase": "1H",
  "status": "pass"
}
```

Phase 1H is closed. Phase 2 may proceed after external review.


## Second external-review corrections

A second cold review identified a small set of remaining Phase 1 defects. The following corrections were accepted without introducing another architectural phase:

- rejected, conflicting, replayed, and HTTP-level failed requests now leave minimal local diagnostic evidence;
- request IDs and idempotency keys are scoped by `(client.id, caller.subject)`;
- an idempotent retry echoes the current request ID while retaining the original workflow/receipt identity;
- legacy unscoped workflows do not collide with newly scoped requests;
- package metadata declares all runtime dependencies required by `pip install .`;
- percent-encoded workflow IDs are decoded by the HTTP server;
- `schemas/catalog-v1.json` publishes URN-to-file mappings for independent validators;
- non-standard JSON numbers such as `NaN` and `Infinity` are rejected;
- the demonstrator machine-readable profile uses client identity terminology;
- the acceptance harness opens the production database read-only;
- the prohibited-operation list is documented as defense-in-depth where schema rejection occurs first.

No `federation.*` namespace, peer-orchestrator RPC, module-specific membership state, or module-admission implementation was added.

The architecture rule remains: **orchestrators do not federate; evidence may.**
