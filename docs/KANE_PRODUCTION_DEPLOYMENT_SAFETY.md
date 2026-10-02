# Kane Production Deployment Safety

## Scope

This file records operational invariants for the Kane reference deployment. It does not change the portable Civic contracts.

## Node identity

The current publication path is:

```text
srv-b / CT105 / civic-orchestrator / 10.20.0.15
        |
        | publication route http://10.110.0.21:8046
        v
proxmox1 / civic-publication-relay.socket
        |
        | systemd-socket-proxyd
        v
proxmox1 / CT106 / publication1.internal.diagnostics.kane-il.us
192.168.1.106:8046
```

`proxmox1 / CT102 / ipfs1.diagnostics.kane-il.us` is **not part of this stack**. It must not be started, modified, used as a credential source, or treated as a publication/pinning node for this deployment.

## Production-write discipline

Production changes use these rules:

1. identify the physical host, CT number, and service role before every write;
2. inspect the effective live unit and current listener before replacing code or unit files;
3. never replace a running service binary with a version whose restart defaults differ from the live unit unless the unit is first made restart-safe;
4. perform one state-changing action at a time and verify that exact action before the next write;
5. keep service restart as a separate explicit action after code, configuration, credentials, and `systemd-analyze verify` have already passed;
6. do not combine cross-host credential transfer, unit creation, restart, and rollback in one shell pipeline;
7. do not assume root SSH or another administrative transport exists merely because network reachability exists; verify the administrative authentication path first;
8. verify credential copies by cryptographic digest without printing credential contents;
9. do not alter Proxmox forwarding, bridges, WireGuard, NAT, firewall policy, or relay units as part of an application deployment unless a separate network change has been explicitly diagnosed and accepted;
10. Kubo/IPFS side effects remain disabled until the Phase 4 acceptance gate is explicitly completed.

## Restart-safety invariant

The publication implementation defaults to loopback. The Kane CT106 service therefore **must** carry an explicit:

```text
--listen 192.168.1.106 --port 8046
```

before the reviewed publication script is allowed to become the next process after a restart.

The authenticated CT106 service additionally requires the systemd credential `publication-service.json` and:

```text
--credential-name publication-service.json
```

The CT105 service must remain explicitly loopback-only on `127.0.0.1:8045`.

## Repository/live-state rule

Checked-in deployment assets define the intended restart-safe target state. A live node is not assumed to match them. Deployment acceptance always compares:

- checked-in unit;
- effective live unit and drop-ins;
- actual process command line;
- actual listener;
- credential/policy metadata;
- deployed source/package revision.

A repository update is not production acceptance, and a running old process does not prove that the files on disk are restart-safe.


## Mandatory deployment procedure

All Kane production deployments follow `DEPLOYMENT_ACCEPTANCE_PROTOCOL.md`.

In particular, operational instructions are scoped to exactly one physical host per execution step. A response or runbook step must never present executable command blocks for two different production hosts. Host transitions are explicit, separate steps after the preceding host's evidence has been reviewed.

The publication stack's first deployment is the reference implementation of this procedure. Its accumulated acceptance record is maintained in `KANE_PUBLICATION_DEPLOYMENT_ACCEPTANCE.md`.
