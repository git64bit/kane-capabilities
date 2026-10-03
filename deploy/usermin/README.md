# Usermin U-002 / U-003 Deployment Assets

## Status

Repository implementation only. These files do not establish production acceptance until the real Portal/Usermin host (`witness-hubzilla` in the current Kane deployment) passes the staged U-002/U-003 acceptance checks.

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

It must remain root-owned and not group/world writable. When the broker runs as the dedicated non-root `civic-usermin-broker` service account, the production file should be `root:civic-usermin-broker 0640` so the broker can read it without gaining write access.

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

The base U-002 service has no remote publisher configured. A successful local-only response therefore contains:

```json
{
  "status": "validated",
  "remote_dispatch": false
}
```

The U-003 remote publisher and CT105 authenticated-ingress boundary are implemented in the repository. Remote dispatch remains disabled in the base U-002 unit and is enabled only through the explicit U-003 deployment overlay (`20-orchestrator.conf.example`) together with a protected adapter credential and deployment-specific Orchestrator endpoint. Live route selection, credential provisioning, deployment, and production acceptance remain pending.

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


## Generic Custom Command helper — repository stage

The repository now contains a generic participant helper:

```text
python -m civic_orchestrator.usermin_command list
python -m civic_orchestrator.usermin_command help water-ants
python -m civic_orchestrator.usermin_command run water-ants --file <path> --confirm
```

The `list` and `help` paths are local and registry-backed. They do not require the broker or Orchestrator.

The helper validates both:

```text
/etc/civic-orchestrator/custom-command-registry-v1.yaml
/etc/civic-orchestrator/custom-command-help-v1.yaml
```

against their schemas and requires exact codename coverage.

The generic invocation protocol is intentionally **not** deployed over the accepted production publication socket. Its reserved default socket is:

```text
/run/civic-orchestrator/custom-command.sock
```

No production systemd socket or Usermin mapping is created by this repository step. The existing `usermin-publication-upload` path remains unchanged until a separate acceptance step.
