# Phase 3 Usermin Adapter Boundary

## Status

**U-001 ACCEPTED — U-002 implementation pending**

This document records the production Usermin discovery completed on 2026-10-01/02 and fixes the participant-facing adapter boundary before implementation.

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

The Civic adapter must derive participant identity from the process or kernel peer credentials.

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

Preferred local shape:

```text
Usermin Custom Command
        |
        | process runs as participant Unix UID
        v
participant adapter
        |
        | Unix-domain socket
        v
Civic broker
        |
        | SO_PEERCRED
        | derive peer UID
        | UID -> Unix participant
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
- are not members of the authorized participant group;
- attempt operations outside the broker's fixed operation set.

## Remote trust boundary

The raw Civic Orchestrator HTTP API must not be exposed to participants merely because the local broker exists.

Before participant traffic is admitted, the Orchestrator must have a way to distinguish an authenticated adapter from arbitrary HTTP clients.

The remote adapter credential and transport mechanism remain an implementation gate. Whatever mechanism is selected must ensure that a participant with Terminal access cannot bypass the broker and submit arbitrary:

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

- authenticated participant identity;
- exact bytes;
- original filename where available;
- size;
- SHA-256;
- media type through bounded mechanical classification, falling back to `application/octet-stream`;
- fixed client/authentication provenance.

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

### U-002 — Local peer-credential broker

Required:

- system Unix socket;
- participant-group socket access;
- kernel `SO_PEERCRED` UID derivation;
- no caller identity accepted from request payload;
- no remote Orchestrator side effect yet;
- tests for impersonation and malformed local requests.

### U-003 — Authenticated Orchestrator transport

Required:

- broker possesses an adapter credential unavailable to participants;
- Orchestrator verifies the adapter boundary;
- participant cannot bypass the broker by directly calling the raw API;
- authenticated adapter identity is bound to the resulting request provenance.

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

Publication/document organization and lifecycle management are deliberately outside the thin Usermin form. Heavy clients consume the participant-linked publication catalog defined in `PUBLICATION_DOCUMENT_MODEL.md`.
