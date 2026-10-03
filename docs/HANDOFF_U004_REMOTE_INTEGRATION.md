# U-004 Remote Integration Handoff

## Scope

This handoff transfers the **remaining U-004 work** to a new implementation Assistant.

Do not reopen Usermin discovery. The real Participant-facing Usermin Custom Command path is already accepted. The next problem is narrower:

> connect the accepted generic `water-ants` Custom Command broker path to the already accepted U-003 authenticated Orchestrator `publication.publish` transport, while preserving all current authority boundaries and keeping Kubo/IPFS side effects disabled.

Architecture first. Do not change production or write integration code until the remote-binding design is reviewed.

## Accepted state

Phase 3 currently has:

```text
U-001  accepted
U-002  accepted
U-003  accepted
U-004  real Usermin -> generic local broker slice accepted
       generic broker -> authenticated Orchestrator integration pending
```

The real Participant UI now provides only:

```text
Choose file
explicit Yes/No acknowledgement (No by default)
Publish
```

Stock Usermin was sufficient; no Perl modification was required.

The negative real-Usermin path rejects missing acknowledgement with:

```text
remote_dispatch=false
side_effects=false
```

The confirmed real-Usermin path reaches `water-ants`, derives the stable Participant identity through the local credential boundary, binds to `publication.publish`, and returns:

```text
status=stub
remote_dispatch=false
side_effects=false
```

Usermin temporary uploads were observed under `/tmp/.webmin/` during the real form tests and were removed after both rejected and successful runs.

## Live first-command configuration

The first Civic Usermin definition is:

```text
/etc/webmin/custom/1791060803.cmd
```

Command:

```text
/usr/local/bin/civic-custom-command run water-ants --file $file $confirm
```

Effective command metadata:

```text
user=*
raw=0
su=0
order=0
noshow=0
usermin=1
timeout=0
clear=0
format=-
```

There is no `1791060803.hosts` file.

The Usermin command ACL is deliberately per-Participant:

```text
access=sase25sep26a: 1791060803
```

The Unix group `civic-participants` is only a coarse local-admission boundary; it is not entitlement to the command inventory.

Reference Participant:

```text
Unix account:    sase25sep26a
stable Civic ID: participant:f58aeb92-f8fd-49f4-b314-d77c2b3e8536
```

## Two broker paths that must not be conflated

Accepted U-003 publication path:

```text
/run/civic-orchestrator/usermin.sock
  -> civic-usermin-broker.service
  -> protected adapter credential
  -> authenticated Orchestrator transport
  -> publication.publish
  -> validation-only publication backend
```

Accepted generic Custom Command local path:

```text
/run/civic-orchestrator/custom-command.sock
  -> civic-custom-command-broker
  -> registry/help/access contracts
  -> SO_PEERCRED
  -> stable Participant ID
  -> water-ants binding
  -> local stub
```

The generic broker is intentionally still:

```text
remote_dispatch=false
side_effects=false
```

Its socket/service were started for acceptance but were not made a persistent enabled production dependency at the acceptance checkpoint.

Pinned generic runtime candidate used for live acceptance:

```text
4f201166f77cd104eb53625d0794e75c895ce16b
```

## Frozen constraints

The integration must preserve all of these:

- Participant input never selects an Orchestrator operation, route, endpoint, credential, service, host, or backend.
- `water-ants` remains bound to the fixed semantic operation `publication.publish`.
- Participant identity is derived locally from AF_UNIX `SO_PEERCRED` and mapped to the stable Civic Participant ID.
- Usermin/Unix identity is not itself permanent Civic identity.
- Custom Command access remains curated/default-deny and separate from `civic-participants` group membership.
- The privileged broker never opens a Participant-supplied pathname; Participant code reads the upload and sends bounded bytes.
- Explicit acknowledgement remains a usability/consequence barrier, not authorization.
- The protected U-003 adapter credential remains server-side and unavailable to the Participant.
- No generic `shell.exec`, arbitrary HTTP proxy, arbitrary operation selector, arbitrary route selector, privileged path-open, or Kubo RPC surface may be introduced.
- The existing accepted U-003 publication broker/path must not be casually replaced or broken.
- Kubo/IPFS publication remains disabled for this gate.
- The next acceptance must continue to prove `side_effects=false`.

## First task for the new Assistant

Read, in order:

1. `ROADMAP.md`
2. `docs/PHASE3_USERMIN_ADAPTER_BOUNDARY.md`
3. `docs/KANE_DEPLOYMENT_FACTS.md`
4. this handoff

Then produce a **design-only comparison** for how the generic `water-ants` broker should reach the already accepted U-003 authenticated publication transport.

At minimum compare:

1. reusing the accepted U-003 publisher/transport component inside the generic broker; versus
2. a bounded local delegation from the generic broker to the existing publication broker.

Evaluate identity preservation, duplicate policy/validation, credential ownership, failure semantics, audit/workflow continuity, deployment complexity, and whether either option accidentally creates a generic remote dispatcher.

Do not implement either option until the architecture is approved.

## Acceptance target for the remaining U-004 gate

The next live acceptance should prove:

```text
real Usermin Participant
  -> water-ants
  -> generic broker
  -> stable Participant identity
  -> fixed publication.publish binding
  -> accepted authenticated U-003 Orchestrator transport
  -> existing validation-only publication backend
```

with:

```text
same Participant identity
same bounded artifact bytes/hash
same Orchestrator workflow evidence
remote dispatch performed only by trusted server-side code
Kubo disabled
side_effects=false
```

No additional Usermin source archaeology is required unless new evidence exposes an actual defect.
