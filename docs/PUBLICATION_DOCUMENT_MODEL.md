# Publication, Document, and Lifecycle Model

## Purpose

This document fixes the separation between publishing exact bytes and later managing the meaning, organization, and lifecycle of those bytes.

The first participant publication action is deliberately minimal:

> Publish this file.

A participant does not have to decide, at publication time:

- why the file is being published;
- how long it should remain pinned;
- whether another version will follow;
- whether it supersedes an earlier file;
- which collection or logical directory it belongs to;
- whether the file is part of a larger document history.

Those are later management concerns.

## Publication invariant

`publication.publish` records an objective event:

```text
an authenticated participant
        |
        | submitted exact bytes
        v
Civic Orchestrator
        |
        | authorized and recorded publication
        v
publication service
        |
        | content-addressed publication
        v
CID / verification evidence
```

The publication event must remain true even if later metadata, document organization, pin state, or working copies change.

## Four distinct objects

### Artifact

An artifact is exact content.

Typical derived properties:

- SHA-256;
- byte size;
- media type where determinable;
- CID after publication.

Content identity is independent of participant intent.

Two participants may publish identical bytes and therefore receive the same CID.

That does **not** collapse their publication histories into one event.

### Publication

A publication is the immutable Civic record that an authenticated participant published an artifact through an accepted workflow.

A publication record may contain:

- publication identifier;
- participant identity/provenance;
- artifact SHA-256;
- byte size;
- media type;
- original filename as factual ingress metadata where available;
- CID;
- publication timestamp;
- client surface;
- workflow identifier;
- receipt identifier;
- verification result;
- publication-service result;
- current infrastructure pin state.

The same artifact may have multiple publication records.

Example:

```text
Participant A -> artifact X -> CID abc -> publication P1
Participant B -> artifact X -> CID abc -> publication P2
```

The CID is shared content identity. P1 and P2 remain distinct provenance events.

### Document

A document is a participant-managed logical object.

A document may have:

- a stable document identifier;
- owner/controlling participant;
- POSIX-like logical path;
- name;
- creation and update timestamps;
- zero or more generations;
- zero or more publications;
- participant-supplied annotations and relationships.

A document is not created merely because a file was published.

A later heavy client may organize an existing publication into a document without rewriting the publication event.

### Generation

A generation is one state of a managed document.

A generation may be:

- working-only;
- revisioned in Gitea;
- published to IPFS;
- both revisioned and published.

Example:

```text
/hoa/bylaws/bylaws.pdf

generation 1   working only
generation 2   working/revision history
generation 3   published -> CID A
generation 4   working/revision history
generation 5   published -> CID B
```

The Orchestrator must not infer that separately published files are generations of one document merely because filenames are similar.

Version, supersession, collection, and document relationships are explicit management actions.

## Publish first, organize later

A valid participant flow is:

```text
Usermin
  choose file
  publish
        |
        v
publication record exists
        |
        +---- no document relationship yet
        |
        +---- later heavy client may:
                assign logical path
                attach to document
                create generation relationship
                annotate
                pin/unpin
                retire from active catalog
```

Publication therefore does not depend on prior document modeling.

## Minimal publication input

The thin-client publication surface supplies only the file.

The infrastructure derives or records the rest:

- authenticated participant;
- exact bytes;
- original filename where available;
- byte size;
- SHA-256;
- media type derived mechanically by the adapter, with `application/octet-stream` as the safe fallback when no narrower type is established;
- workflow/audit/receipt identifiers;
- timestamp;
- CID and verification result when publication succeeds.

The participant does not supply publication purpose, retention duration, future-version intent, document path, supersession relationship, or pin duration as part of the thin publication action.

Mechanical processing required to publish exact bytes—reading the bytes, counting them, hashing them, base64 transport, and bounded media-type classification—is not content moderation and must not require a human operator to open or interpret the file.

The current v1 publication schema still permits an optional descriptive `label`. That field is not part of the Usermin thin-client surface and carries no lifecycle semantics. Contract cleanup may remove or supersede it before the first participant-facing side-effect gate.

## Pinning and removal semantics

Publishing to IPFS does not imply a promise that content can later be erased globally.

A Civic client may manage infrastructure under Civic control with operations such as:

- pin;
- unpin;
- retire from the active participant catalog;
- remove a working copy;
- remove a revision-managed working object where policy permits.

A client must not claim that unpinning or retiring a publication deletes the CID from IPFS globally.

Another node may already retain the content.

Pin duration is not required at publication time. The publication service follows the deployment's current default retention/pinning policy until a later management action changes Civic-controlled state.

## Structured catalog

The Orchestrator owns the bounded semantics of the participant publication/document catalog.

For the Kane reference deployment, PostgreSQL is the intended structured store for catalog state such as:

- participants and publication associations;
- artifact metadata;
- publication records;
- document identifiers;
- POSIX-like logical paths;
- generation relationships;
- timestamps;
- publication-to-generation links;
- annotations;
- current Civic-controlled pin/lifecycle state.

This does not make PostgreSQL a content-byte store or a universal Civic datastore.

Existing Orchestrator workflow/audit persistence may remain separate from the document/publication catalog where that separation is operationally useful.

## Logical paths

POSIX-like paths are participant-facing organization, not proof of physical filesystem placement.

Example:

```text
/hoa/
  bylaws/
    current.pdf
  assessments/
    2026-budget.pdf
```

The catalog may map a logical generation to:

- a Usermin working file;
- a Gitea repository/commit/path;
- an immutable IPFS publication;
- another bounded storage implementation.

A rename or move changes participant organization. It must not rewrite an immutable historical publication record or change a CID.

## Gitea role

Gitea is a revision mechanism and source/revision authority, not the universal participant blob store.

It is appropriate for:

- text;
- JSON;
- Markdown;
- source;
- manifests;
- governance documents;
- other artifacts that benefit from Git history;
- exact repository/commit/path references.

Binary artifacts may also be revisioned when useful, but Civic document identity must not depend on Git being an efficient binary-diff engine.

The Orchestrator catalog can relate a document generation to a Gitea commit without making the Git path the universal document identity.

## Heavy clients

A heavy client may expose substantially more utility than Usermin.

Kane Fabric is the primary example: a full online client with reduced offline capability.

A heavy client may present:

- publication history;
- artifact type and size;
- timestamps;
- SHA-256 and CID;
- verification state;
- workflow and receipt evidence;
- logical directories;
- document generations;
- revision references;
- annotations;
- pin state;
- retire/unpin controls;
- relationships among publications and generations.

A heavy client gains more presentation and management utility, not a different storage or authorization authority.

Hubzilla addons, Gitea-integrated views, or a dedicated website may provide subsets of the same management model.

## Capability separation

`publication.*` concerns immutable publication events and Civic-controlled publication lifecycle.

`repository.*` concerns exact repository/revision mechanics.

A future `document.*` namespace may expose logical document/path/generation management once its contract is frozen.

The runtime must not expose generic filesystem, SQL, Git, or Kubo operations merely to implement those semantics.

## Non-inference rule

The Orchestrator records known facts and explicit participant actions.

It must not infer:

- purpose from filename;
- document identity from similar names;
- supersession from chronology;
- retention intent from file type;
- pin duration from client surface;
- version relationships from matching directories.

A heavy client may ask the participant to establish those relationships later.

## Implementation sequence

1. Keep Usermin publication file-only.
2. Complete the trusted Usermin adapter/broker path.
3. Persist participant-linked publication records for successful publication.
4. Enable the first real Kubo/IPFS publication only after the trust gates pass.
5. Add structured publication/document catalog state.
6. Add heavy-client read/list/detail views.
7. Add explicit document/generation/path management.
8. Add explicit pin/unpin/retire controls.
9. Integrate Gitea revision relationships where appropriate.
10. Preserve immutable publication evidence throughout.
