# Phase 3 Usermin Adapter Boundary

## Status

**U-001 ACCEPTED — U-002 repository implementation complete, production acceptance pending — U-003 repository implementation complete, production routing/credential acceptance pending — U-004 pending**

This document records the production Usermin discovery completed on 2026-10-01/02 and the participant-facing adapter boundary together with its staged repository implementation and production-acceptance state.

### Confirmed production placement

As of 2026-10-02, the production Portal/Usermin surface is running in the same container as Witness/Hubzilla. The container hostname is `witness-hubzilla`; `usermin.service` was confirmed loaded and active there. The numeric CT/VM identifier and physical host are not established by this document. See `KANE_DEPLOYMENT_FACTS.md`.

The Usermin surface is intentionally a thin client. A participant deciding to publish a file is not required to describe its purpose, retention, document/version relationships, or future intent.

The Usermin interaction surface is not an authority and must not be allowed to invent Civic caller identity.

## Installed Usermin mechanism

The production portal exposes Webmin/Usermin **Custom Commands**.

The Usermin `commands` module consumes commands defined by Webmin's `custom` module and explicitly marked for Usermin use.

Production configuration points Usermin to:

```text
/etc/webmin/custom
```

The installed Usermin command runner supports:

- Usermin-visible command gating;
- per-user and per-Unix-group access rules;
- execution as the authenticated Unix user;
- typed command arguments;
- native upload fields;
- required/optional arguments;
- per-argument shell quoting;
- bounded command output.

## Participant identity invariant

For a Custom Command configured with execution user `*`, Usermin resolves the authenticated `$remote_user` through the local Unix account database and executes the command under that UID/GID.

Therefore the local participant identity source is:

```text
authenticated Usermin login
        -> Usermin remote_user
        -> Unix UID/GID
        -> command process credentials
```

The Civic adapter must derive the local account from process or kernel peer credentials, then map that account to a stable, never-recycled Civic participant identifier. Unix username and UID are locators, not permanent publication identity.

The participant must never provide editable values for:

```text
caller.subject
caller.authenticated_by
client.id
client.kind
```

## Frozen Custom Command profile

The first participant-facing operation is:

```text
Publish Public File
```

Required configuration:

```text
Visible in Usermin: YES
Run as user:        *
Use su mode:        NO
Access:             @civic-participants
```

Arguments:

```text
file:
    type:       Upload
    required:   YES
    quote:      YES
```

The participant-facing form is therefore conceptually:

```text
Choose file
Publish
```

No label, purpose, retention period, document path, version relationship, Kubo parameter, HTTP endpoint, Orchestrator identity, service routing, or authentication parameter is exposed to the participant form.

The `publication.publish` schema contains no descriptive label field. Usermin supplies only the file; descriptive meaning belongs to later document/catalog management.

## Upload handling

For Upload arguments, Usermin:

1. creates a temporary pathname;
2. writes the uploaded bytes;
3. changes ownership to the selected execution UID/GID;
4. passes the pathname through the configured command parameter;
5. queues the temporary file for cleanup.

The production Usermin process currently uses umask `0022`, so upload files may be mode `0644`.

Participant homes use a non-world-traversable parent directory and private primary group. The observed participant home was mode `0750`, so unrelated local accounts cannot traverse into the participant's `.tmp` directory even when the file itself is `0644`.

This deployment invariant must be preserved for participant accounts.

The observed `upload.*` files under `$HOME/.tmp` are upload-progress tracker records, not retained payload files. They contain progress metadata written by `read_parse_mime_callback`.

## Shell quoting rule

Custom Command arguments configured with `quote=YES` are referenced as quoted shell variables in the generated command string.

The Civic command must keep Usermin's `su` mode disabled. The normal execution path switches to the resolved Unix UID directly. This avoids relying on the alternate shell-fragment environment construction used by the `su` path.

## Terminal coexistence

Usermin Terminal remains available.

This does not weaken the intended authorization boundary.

A participant may manually invoke the same participant adapter command from the shell, but must still be limited to the identity and capability represented by their actual Unix credentials.

Therefore hiding the underlying command is a usability property, not a security boundary.

## Local broker requirement

Custom Commands provides a suitable UI and authenticated Unix execution identity, but it is not sufficient by itself to authenticate a remote Orchestrator request.

The participant-side adapter must communicate with a local privileged or dedicated Civic broker over an authenticated local IPC boundary.

The privileged broker must never open a participant-supplied pathname. The participant process opens and reads its own Usermin upload under its existing Unix credentials, then sends bounded bytes to the broker. This prevents a privileged path-open race or symlink escape.

Preferred local shape:

```text
Usermin Custom Command
        |
        | process runs as participant Unix UID
        v
participant adapter
        |
        | Unix-domain socket
        | bounded artifact bytes
        v
Civic broker
        |
        | SO_PEERCRED
        | derive peer UID
        | UID -> Portal account
        | account -> stable participant_id
        | derive size/hash/media type
        | fixed client identity
        | fixed authentication provenance
        v
authenticated Orchestrator transport
```

The production portal host supports:

- Linux AF_UNIX sockets;
- `SO_PEERCRED`;
- systemd system services;
- Python 3.12.

The absence of `/run/user/<participant-uid>` is irrelevant because the broker is a system service and should use a system runtime directory.

## Broker socket boundary

The intended broker socket is system-owned and group-accessible only to Civic participants.

Conceptually:

```text
/run/civic-orchestrator/usermin.sock
owner: broker service
group: civic-participants
mode: 0660
```

The broker must not trust a username supplied in the request body. It must obtain the connecting process UID from `SO_PEERCRED` and resolve that UID locally.

The broker must reject peers that:

- cannot be resolved to a Unix account;
- cannot be mapped to a stable Civic participant identifier;
- are not members of the authorized participant group;
- attempt operations outside the broker's fixed operation set;
- exceed the current artifact-size bound.

The broker receives bytes, not a privileged filesystem pathname.

### Participant provisioning invariant

New Portal/Usermin participant accounts must be provisioned automatically rather than by hand-editing `participants-v1.json`. The provisioning path must add the Unix account to `civic-participants` and allocate exactly one UUID-based stable Civic `participant_id`. Re-provisioning the same active Unix account is idempotent and returns the existing ID. Retired mappings remain tombstones and are not automatically reused.

The repository provides `civic_orchestrator.usermin_provision` and the deployment wrapper `deploy/usermin/usermin-participant-provision`. Production acceptance still requires wiring that helper into the actual account-creation path on `witness-hubzilla`.

## Remote trust boundary

The raw Civic Orchestrator HTTP API must not be exposed to participants merely because the local broker exists.

Before participant traffic is admitted, the Orchestrator must distinguish an authenticated adapter from arbitrary HTTP clients. The repository-side CT105 mechanism now does this with a protected bearer credential resolved server-side to an `AuthenticatedAdapterBinding`.

The repository now contains the U-003 Usermin broker publisher: it loads a protected adapter credential, constructs only the bounded participant `publication.publish` request, and dispatches only when an Orchestrator endpoint is explicitly configured. Production route selection, credential provisioning, and live acceptance remain pending. A participant with Terminal access must not be able to bypass the broker and submit arbitrary:

- caller subjects;
- authentication provenance;
- client identities.

A raw TCP relay to the current Orchestrator HTTP listener is explicitly insufficient.

## First adapter semantics

The Usermin adapter is permitted to construct only the semantic operation:

```text
publication.publish
```

The participant supplies only the file to publish.

The adapter or broker derives or records factual publication metadata, including:

- stable authenticated participant identity;
- exact bytes;
- size;
- SHA-256;
- media type through bounded mechanical classification, falling back to `application/octet-stream`;
- fixed client/authentication provenance.

The source filename is not part of the publication contract.

Document purpose, logical path, retention duration, pin duration, supersession, and version intent are not publication prerequisites.

The adapter or broker derives and fixes everything else required by the Civic request envelope.

## Acceptance gates

### U-001 — Usermin surface discovery

Accepted when:

- Custom Commands behavior is understood;
- authenticated Unix execution is proven;
- group access behavior is understood;
- upload lifecycle is understood;
- Terminal coexistence is explicitly accounted for.

**Status: ACCEPTED.**

Production discovery also proved the kernel identity primitive directly: an AF_UNIX connection from the participant process returned the actual participant PID/UID/GID through `SO_PEERCRED`, resolving UID 1002 to `sase25sep26a`. This proves the local broker can derive peer identity without trusting a username in request data.

### U-002 repository implementation

The repository now contains the validation-only local adapter implementation:

```text
src/civic_orchestrator/usermin_adapter.py
src/civic_orchestrator/usermin_broker.py
src/civic_orchestrator/usermin_upload.py
deploy/usermin/
```

The participant helper opens the Usermin upload under the participant UID with `O_NOFOLLOW`, requires a participant-owned regular file, enforces the current artifact bound, and sends only bytes over AF_UNIX.

The broker derives the peer UID through `SO_PEERCRED`, checks current `civic-participants` membership, maps the Unix account through a provisioning-owned stable participant registry, and derives the content evidence.

The local request framing contains only a 32-bit byte length followed by artifact bytes. It has no pathname, username, participant identifier, caller, client, or authentication-provenance field.

The U-002 service is deliberately restricted to `AF_UNIX` and has no remote publisher configured. Successful repository-level execution therefore returns `remote_dispatch=false`.

Production acceptance still requires deployment through the real Usermin Custom Command and verification under the real Portal account/service identities.

### U-002 — Local peer-credential broker

Required:

- system Unix socket;
- participant-group socket access;
- kernel `SO_PEERCRED` UID derivation;
- stable, never-recycled participant-ID mapping;
- participant process sends bounded bytes; broker never opens a participant-supplied path;
- broker derives size, SHA-256, and bounded media type;
- no caller identity accepted from request payload;
- no remote Orchestrator side effect yet;
- tests for impersonation, path/symlink abuse, oversize input, and malformed local requests.

**Repository status:** IMPLEMENTED and regression-tested. **Production status:** NOT YET ACCEPTED.

### U-003 — Authenticated Orchestrator transport

Required:

- broker possesses an adapter credential unavailable to participants;
- Orchestrator verifies the adapter boundary;
- each credential maps server-side to a fixed `client.id`, fixed `client.kind`, fixed `authenticated_by`, and allowed subject namespace/mapping;
- transport-derived adapter identity constrains request-body identity claims; the body can never widen them;
- participant cannot bypass the broker by directly calling the raw API;
- authenticated adapter identity is bound to the resulting request provenance;
- contradictory body claims are rejected with a diagnostic.

**Repository status:** CT105 authenticated ingress and the Usermin broker remote publisher are implemented and regression-tested. The broker remains local-only unless its U-003 overlay explicitly supplies an Orchestrator endpoint and protected adapter credential. **Production status:** route selection, protected credential provisioning, deployment, and live acceptance remain pending.

### U-004 — Validation-only end to end

Required:

- real Usermin Custom Command;
- real local broker;
- authenticated Orchestrator transport;
- real `publication.publish` workflow;
- current validation-only backend result;
- persisted workflow/audit/receipt evidence;
- no Kubo side effect.

Only after U-004 should Usermin publication be considered a production participant route.

U-004 remains validation-only. Real Kubo side effects additionally require every gate in `PHASE4_PUBLICATION_SAFETY_GATES.md`.

Publication/document organization and lifecycle management are deliberately outside the thin Usermin form. Heavy clients consume the participant-linked publication catalog defined in `PUBLICATION_DOCUMENT_MODEL.md`.
