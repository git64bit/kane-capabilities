# External Review Handoff

## Review point

Repository state after the third independent review of the Phase 2/3 publication path.

Phase 1/1H remain closed. Phase 2 has one available bounded operation, `publication.publish`, routed to a validation-only publication service. Kubo/IPFS side effects remain disabled.

The current correction authority is:

- `PHASE4_PUBLICATION_SAFETY_GATES.md`;
- `PHASE3_USERMIN_ADAPTER_BOUNDARY.md`;
- `PHASE2_PUBLICATION_SERVICE_BOUNDARY.md`;
- `PUBLICATION_DOCUMENT_MODEL.md`;
- `ROADMAP.md`.

## Current architecture

The Kane Civic Orchestrator coordinates one bounded Kane authority/workflow domain. It is not a universal orchestrator or datastore.

The participant publication model remains deliberately narrow:

```text
authenticated participant
    -> exact file bytes
    -> publication.publish
    -> immutable publication evidence
    -> later optional document/catalog management
```

Publication-time input does not include label, purpose, source filename, retention duration, logical path, pin duration, supersession, or version intent.

## Accepted third-review corrections

The current branch/release line incorporates or gates:

- independent CT105 CID calculation and comparison;
- explicit `cid_profile`;
- temporary 262,144-byte single-raw-block publication limit;
- resumable retryable publication workflows;
- startup reconciliation of accepted external workflows after process restart;
- side-effect certainty evidence;
- atomic immutable publication records in the Orchestrator SQLite completion transaction;
- PostgreSQL as a rebuildable publication projection / later mutable document-management store;
- stable, never-recycled participant identity as a requirement before U-002 acceptance;
- U-002 byte transfer rather than privileged broker path opening;
- U-003 transport-bound adapter identity constraints;
- CT105-to-publication-service authentication as a Phase 4 gate;
- participant publication budget as a Phase 4 gate.

## Deliberate non-changes

The repository still does **not**:

- enable Kubo publication or swarm participation;
- expose the raw Orchestrator HTTP API to participants;
- implement `document.*`;
- make Hubzilla an arbitrary file store;
- make Gitea the universal participant filesystem;
- infer document meaning or version relationships from filenames or chronology;
- make PostgreSQL the authoritative origin of immutable publication evidence.

## Acceptance state

```text
Phase 0    COMPLETE
Phase 1    COMPLETE
Phase 1H   COMPLETE
Phase 2    publication validation path accepted
Phase 3    U-001 accepted; U-002 repo implementation complete / production pending; U-003 CT105 ingress primitive implemented / integration and production pending; U-004 pending
Phase 4    gated; no Kubo side effects
```

Current repository regression suite:

```text
73 tests on Python 3.11    PASS
73 tests on Python 3.13    PASS
```

## Next review targets

Useful independent review targets now are:

- resumable external-workflow semantics under process failure;
- publication-record atomicity;
- CID-profile and CID-verification correctness;
- adapter credential to caller/client binding;
- stable participant-identity mapping;
- publication-service authentication;
- participant publication budgets;
- preservation of thin-client semantics through U-002 production acceptance and U-003 broker integration/production acceptance.

The next implementation step should not reopen the file-only publication model unless new evidence demonstrates a concrete defect.
