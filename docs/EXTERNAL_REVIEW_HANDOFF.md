# External Review Handoff

## Review point

Repository state after the third independent review of the Phase 2/3 publication path. This file remains the external-review checkpoint; later live Usermin acceptance is summarized below and the current implementation handoff is `HANDOFF_U004_REMOTE_INTEGRATION.md`.

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
- participant publication budgeting implemented in CT105 authorization state with atomic reservation/hold accounting, fail-closed deployment-policy loading, and live deployment values/acceptance still gated.

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
Phase 3    U-001/U-002/U-003 accepted; U-004 local real-Usermin -> generic-broker slice accepted; remote generic-broker -> authenticated Orchestrator integration pending
Phase 4    gated; no Kubo side effects
```

Regression evidence at the `v0.1.0-alpha.3` checkpoint:

```text
73 tests on Python 3.11    PASS
73 tests on Python 3.13    PASS
```

Subsequent cleanup commits add regression coverage. Treat the 73-test count as checkpoint evidence rather than the current test inventory.

Current post-checkpoint repository regression evidence:

```text
140 tests on Python 3.11    PASS
140 tests on Python 3.13    PASS
```

This later test count is cleanup-branch evidence, not a replacement release claim for `v0.1.0-alpha.3`.

## Next review targets

Useful independent review targets now are:

- resumable external-workflow semantics under process failure;
- publication-record atomicity;
- CID-profile and CID-verification correctness;
- adapter credential to caller/client binding;
- stable participant-identity mapping;
- publication-service authentication;
- participant publication budget deployment values, live policy installation, and acceptance behavior;
- preservation of thin-client semantics while connecting the accepted generic `water-ants` broker path to the already accepted authenticated U-003 Orchestrator transport, without enabling Kubo side effects.

The next implementation step should not reopen the file-only publication model unless new evidence demonstrates a concrete defect.
