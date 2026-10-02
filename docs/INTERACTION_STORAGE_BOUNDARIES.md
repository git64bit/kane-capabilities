# Interaction and Storage Boundaries

## Purpose

Civic Infrastructure interaction surfaces do not all receive the same file-storage privileges.

A richer user interface does not automatically become another storage authority.

The reference deployment deliberately separates:

- participant working storage;
- visible social/image content;
- revision storage;
- structured publication/document metadata;
- immutable published bytes.

## Usermin / Portal

Usermin is the participant working-storage and thin-publication surface.

It owns or exposes:

- Unix participant account;
- participant home directory;
- decisive storage quota;
- mailbox;
- terminal;
- ordinary participant file operations;
- the thin `Publish Public File` action.

The publication action should require only a file selection.

Usermin must not be expanded into the heavy document-management client merely because Custom Commands can accept more fields.

The participant may organize ordinary working files using normal Unix facilities subject to quota.

## Hubzilla

Hubzilla remains the discussion/channel/social-evidence surface.

General arbitrary-file storage is intentionally excluded from the Civic Infrastructure Hubzilla role.

The reference policy is:

- allow visible image upload where required by the channel/post experience;
- disable general document/file storage;
- do not require Civic operators or moderators to open arbitrary participant files in order to determine what they contain.

Images are directly visible in the social interface and can be moderated as visible content.

Arbitrary files create a different moderation burden because inspection would require opening and interpreting the payload. Civic Infrastructure does not make that a routine moderator responsibility.

A Hubzilla addon may display or manage publication records through bounded Orchestrator capabilities without becoming an arbitrary file repository.

## Kane Fabric

Kane Fabric is a heavy client.

It may provide a full online management experience and a reduced offline experience over the same Civic records.

It may expose:

- publication catalog views;
- document organization;
- POSIX-like logical paths;
- generation history;
- revision references;
- metadata;
- verification;
- pin/unpin/retire actions;
- workflow and receipt evidence.

Kane Fabric does not obtain a separate storage authority merely because its interface is richer.

Offline operation may cache catalog/verification state without requiring every artifact body to be cached.

## Gitea

Gitea remains revision/source authority where Git is the selected revision mechanism.

It may version participant-managed document generations between IPFS publications.

The Orchestrator may maintain exact repository/commit/path relationships to managed document generations.

Gitea does not become:

- the universal participant filesystem;
- the publication authority;
- the participant identity authority;
- the Orchestrator workflow authority.

## PostgreSQL catalog

The Kane reference deployment uses PostgreSQL for structured publication/document catalog state.

Typical state includes:

- participant/publication associations;
- artifact metadata;
- logical path tree;
- document identifiers;
- generation relationships;
- timestamps;
- annotations;
- revision references;
- IPFS publication references;
- current Civic-controlled pin/lifecycle state.

PostgreSQL stores structured state, not the authoritative immutable IPFS payload merely because the catalog points to it.

## IPFS publication service

The publication service owns the mechanics of content-addressed publication and Civic-controlled pin state.

It does not decide:

- participant identity;
- document purpose;
- logical path;
- version relationships;
- retention intent;
- social visibility.

Those are either Orchestrator/catalog facts or later participant management choices.

## Storage-authority rule

The same participant may interact through Usermin, Kane Fabric, Hubzilla, Gitea-oriented tooling, or another approved client.

Those surfaces may have different utility, but they must converge on the same underlying authority boundaries.

Conceptually:

```text
Usermin ------------------+
Kane Fabric --------------+
Hubzilla addon -----------+----> Civic Orchestrator
Gitea integration --------+          |
                                     +--> PostgreSQL catalog
                                     +--> Gitea revision service
                                     +--> publication/IPFS service
```

No client receives an alternate bypass merely because it is more capable.

## Moderation boundary

Civic Infrastructure should avoid designing a general file repository whose safety model depends on an operator opening participant files for routine moderation.

Controls should instead rely on:

- authenticated participant provenance;
- bounded quota;
- explicit publication records;
- classification/policy at the operation level;
- visible-content moderation where the surface naturally renders the content;
- incident handling when concrete evidence warrants it.

This boundary does not assert that arbitrary published files are safe. It prevents routine operator inspection of private or opaque participant files from becoming a prerequisite for ordinary storage or publication.

Mechanical publication processing such as byte counting, hashing, encoding, integrity verification, and bounded media-type classification is permitted because it does not require a human moderator to open and interpret the content.

## Working copy versus publication

Deleting a participant working file is an ordinary storage operation.

Unpinning a published CID is a publication-lifecycle operation.

Retiring a publication from an active catalog is a catalog operation.

These are different actions and must not be represented by one ambiguous "delete" control.

An IPFS publication must never promise global erasure merely because Civic-controlled infrastructure stops pinning it.
