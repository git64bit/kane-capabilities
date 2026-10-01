# External Review Handoff

## Review point

Repository state after Phase 1H acceptance on 2026-10-01.

This is the preferred starting point for an independent cold review before Phase 2.

## Architectural scope

The Kane Civic Orchestrator is **not** the universal orchestrator for every Civic Infrastructure application.

It coordinates one bounded Kane authority/workflow domain.

Other applications may instantiate their own orchestrators modeled after this architecture when they own different domain state, membership, policy, trust roots, or workflow authority.

Authority: `docs/ORCHESTRATOR_SCOPE.md`.

## What changed after the first external review

- corrected stale hardware-signer assumption to the current software-signer baseline;
- clarified that Phase 7 is Orchestrator signing integration, not signer construction order;
- removed the fixed application-name interface enum;
- separated authenticated caller identity from extensible client identity;
- required `authenticated_by`;
- implemented request replay/idempotency semantics;
- normalized and schema-validated failure envelopes;
- made HTTP parser/internal failures contract-valid;
- enforced RFC 3339 timestamps;
- validated operation registry and stub workflow definitions at startup;
- added explicit monotonic audit sequence numbers;
- made normal accepted stub-request persistence transactional;
- replaced ambiguous side-effect classification with effect scope;
- moved JSON Schema resolution to absolute Civic URNs and `referencing.Registry`;
- narrowed the former interface-equivalence claim to what it actually proves;
- added Python cache exclusions and corrected stale README text.

## Deliberate non-changes

The repository does **not** add:

- Mechanical Compiler-specific operations;
- 3D-printer membership/group state;
- a universal Civic Infrastructure membership database;
- production service adapters;
- production side effects;
- external CT105 network exposure.

## Acceptance state

```text
Phase 0   COMPLETE
Phase 1   COMPLETE
Phase 1H  COMPLETE
Phase 2   NOT STARTED
```

The current persistent CT105 runtime passed:

```text
21 regression tests
Phase 1H persistent-state acceptance harness
loopback-only listener verification
side_effects=false
```

## Review request

Review this repository as an independent prospective consumer of the **orchestrator architectural pattern**, not as though every Civic Infrastructure application must connect to this Kane CT105 instance.

Useful review targets include:

- contract portability;
- domain-boundary leakage;
- replay/idempotency semantics;
- transactional evidence guarantees;
- authentication provenance;
- schema interoperability;
- service-authority separation;
- unintentional coupling to Kane-specific applications or deployment details;
- remaining claims that exceed what tests actually prove.
