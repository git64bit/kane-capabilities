# Usermin U-002 Deployment Assets

## Status

Repository implementation only. These files do not establish production acceptance until the real Portal/Usermin host passes the U-002 acceptance checks.

## Components

- `civic-usermin-broker.socket` — systemd-owned AF_UNIX socket, mode `0660`, accessible to `civic-participants`.
- `civic-usermin-broker.service` — dedicated non-root validation broker restricted to AF_UNIX.
- `usermin-publication-upload` — participant-side helper invoked by the Usermin Custom Command.
- `participants-v1.example.json` — example of the provisioning-owned stable participant mapping.

## Stable participant mapping

The production registry is expected at:

```text
/etc/civic-orchestrator/participants-v1.json
```

It must be root-owned and not group/world writable.

A participant identifier is permanent publication provenance. When an account is retired, its registry entry is retained with:

```json
"active": false
```

Do **not** delete tombstones and do not reuse a `participant_id` for another Unix account.

The broker requires both:

- current membership in `civic-participants`;
- exactly one active registry mapping matching the current Unix username and UID.

## Byte-only boundary

The privileged broker never receives or opens the participant's pathname.

The participant-side helper:

1. runs under the participant's Unix UID;
2. opens the file with `O_NOFOLLOW`;
3. requires a regular file owned by the invoking UID;
4. enforces the current 262,144-byte limit;
5. sends only the file bytes to the AF_UNIX socket.

The broker derives peer UID with `SO_PEERCRED`, resolves the stable participant identifier, and derives artifact size, SHA-256, and the safe media type `application/octet-stream`.

U-002 has no remote publisher configured. A successful local response therefore contains:

```json
{
  "status": "validated",
  "remote_dispatch": false
}
```

The CT105-side authenticated-ingress primitive for U-003 is already implemented. U-003 remains incomplete here because this local broker has no authenticated remote publisher configured; protected credential use, broker-to-CT105 routing, and production acceptance are later deployment/integration work.

## Usermin Custom Command target

The eventual production command remains conceptually:

```text
Publish Public File

file:
    type: Upload
    required: YES
    quote: YES
```

The command wrapper receives the Usermin temporary file path only because it runs as that participant. That path is consumed locally by the participant helper and is never forwarded to the broker or Orchestrator.
