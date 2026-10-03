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

The ordinary Participant `list` and `help` paths are broker-resolved so discovery can be filtered by stable Participant identity and explicit access grants. They require the local AF_UNIX broker but no Orchestrator or external network service.

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

The repository now includes a **parallel validation-only** socket/service pair:

```text
civic-custom-command-broker.socket
civic-custom-command-broker.service
```

The socket is:

```text
/run/civic-orchestrator/custom-command.sock
owner: civic-usermin-broker
group: civic-participants
mode: 0660
```

The generic service uses a **separate Python environment**:

```text
/opt/civic-custom-command-broker/venv
```

It does not replace or upgrade the accepted publication broker environment at `/opt/civic-usermin-broker/venv`.

Before live installation, the generic service must also load a deployment-local, root/operator-maintained access policy conforming to:

```text
schemas/custom-command-access-v1.schema.json
```

The policy defaults discovery and invocation to deny. Membership in `civic-participants` alone does not grant any Custom Command. Qualifications are human-curated context and create no automatic grants.

The generic service:

- is restricted to `AF_UNIX`;
- loads the stable participant registry plus the Custom Command registry and help catalog;
- derives participant identity through the same `SO_PEERCRED` path;
- has no Orchestrator URL option;
- has no adapter credential;
- has no remote publisher;
- invokes only the repository-side `LocalCustomCommandAdapter`;
- therefore cannot perform remote dispatch at this checkpoint.

This is a repository deployment asset only. It does **not** replace `/run/civic-orchestrator/usermin.sock`, does not modify `usermin-publication-upload`, and does not change the current Usermin Custom Command mapping.

The generic runtime now enforces the curated per-Participant access policy. Production-host validation may resume only with an explicit deployment-local access record for the specifically granted Participant. Switching the visible Usermin Publish command remains a separate acceptance decision.


## Kane production-host validation

The one-host, one-write-at-a-time acceptance procedure for the parallel generic socket is:

```text
docs/KANE_CUSTOM_COMMAND_VALIDATION_ACCEPTANCE.md
```

That runbook pins an exact repository revision, preserves the accepted publication broker process and venv, and stops before any Usermin mapping or remote Orchestrator dispatch is enabled.


## Participant account preservation

The Custom Command system does not standardize Participant shell environments. It must not require edits to shell profiles, aliases, PATH, home-directory layout, or automatic per-Participant agents. Manual qualification and command-access curation belong to operator-maintained Civic policy, not Participant dotfiles.
