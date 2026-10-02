# Kane Publication Deployment Acceptance Record

## Purpose

This is the evidence record for the first Kane deployment performed under `DEPLOYMENT_ACCEPTANCE_PROTOCOL.md`.

It deliberately separates observed facts, accepted layers, unresolved drift, and later gates. A partially accepted deployment is not described as complete.

## Repository baseline

Current repository baseline at this audit checkpoint:

```text
e1b3f8a7ff9d1f5d4689989102c0e5621453f200
```

The repository baseline includes:

- authenticated CT105 adapter ingress;
- authenticated publication-service client primitive;
- P4-006 budget implementation;
- restart-safe reference CT105/CT106 service units;
- explicit CT106 Kane placement;
- explicit exclusion of `proxmox1 / CT102 / ipfs1`;
- authenticated workflow-evidence reads;
- CI coverage on Python 3.11, 3.12, and 3.13.

At that commit, 144 tests pass on all three Python versions.

## Stack identity

```text
srv-b
  CT105 civic-orchestrator
  10.20.0.15/24
  gateway 10.20.0.1

srv-b wg0
  10.110.0.12/32

proxmox1
  relay 10.110.0.21:8046

proxmox1
  CT106 publication1.internal.diagnostics.kane-il.us
  192.168.1.106:8046
```

Hard exclusion:

```text
proxmox1 / CT102 / ipfs1.diagnostics.kane-il.us
NOT PART OF THIS STACK
```

## srv-b host/network acceptance — 2026-10-02

### Observed runtime state

Accepted observations:

- physical host: `srv-b`;
- `vmbr0 = 10.0.0.12/24`;
- `vmbr1 = 10.20.0.1/24`;
- `wg0 = 10.110.0.12/32`;
- CT105 = `10.20.0.15/24`, gateway `10.20.0.1`;
- `net.ipv4.ip_forward = 1`;
- route `10.110.0.0/22 dev wg0`;
- WireGuard peer is live;
- live NAT includes `10.20.0.0/24 -> wg0 MASQUERADE`;
- live forwarding policy preserves the established SMTP isolation and LAN boundary;
- CT105 reaches `http://10.110.0.21:8046/healthz`;
- returned publication-service health remains validation-only with Kubo/swarm disabled.

### Reboot-persistent state

Persistence is proved, not inferred:

- `net.ipv4.ip_forward=1` is present in persistent sysctl configuration;
- `/etc/iptables/rules.v4` contains the required NAT and forwarding rules;
- `iptables-persistent 1.0.20` is installed;
- `netfilter-persistent 1.0.20` is installed;
- `netfilter-persistent.service` is enabled and active;
- IPv4 and IPv6 netfilter persistence plugins are installed;
- boot links for netfilter/iptables persistence exist;
- `wg-quick@wg0.service` is enabled and active;
- protected `/etc/wireguard/wg0.conf` exists;
- its non-secret configuration records `Address=10.110.0.12/32`, peer endpoint, `AllowedIPs=10.110.0.0/22`, and persistent keepalive.

**srv-b network path status: ACCEPTED for the current publication deployment.**

No routing, NAT, firewall, bridge, or WireGuard write is justified by this audit.

## CT105 application state — 2026-10-02

Observed:

- service active;
- PID observed as `12520`;
- zero service restarts at the audit checkpoint;
- listener is `127.0.0.1:8045` only;
- effective drop-ins include `20-publication-client.conf` and `30-authenticated-publication.conf`;
- `30-authenticated-publication.conf` loads both protected systemd credentials and supplies the publication route, budget policy, publication credential name, and adapter credential name;
- credential source files are root-owned mode 0600;
- budget policy is root-owned and service-readable;
- deployed source revision at the checkpoint is `5b04f3a03dc7dbecd225bb0cc898a1d4707aa9b6`;
- generated `build/` and `src/civic_orchestrator.egg-info/` are untracked in the source checkout.

Unresolved:

- CT105 deployed source is behind current repository baseline;
- therefore the authenticated workflow-evidence GET correction is not yet deployed;
- checked-in restart-safe CT105 unit and live base+drop-in composition have not yet been reconciled;
- current P4-006 policy values are validation-stage values (`max_publications=1`, `max_publication_bytes=262144`) and are not yet recorded as accepted production allocation.

**CT105 application status: DEPLOYED/PARTIALLY ACCEPTED; remediation and final acceptance pending.**

## proxmox1 / CT106 re-audit — 2026-10-02

### proxmox1 host and relay

Observed:

- physical host: `proxmox1`;
- Proxmox VE 9.2.2, running kernel 7.0.2-2-pve;
- `wg0 = 10.110.0.21/32`, live WireGuard peer, route `10.110.0.0/22 dev wg0`;
- `vmbr1 = 192.168.1.1/16`;
- CT106 is `publication1.internal.diagnostics.kane-il.us`, `192.168.1.106/16`, on `vmbr1`;
- CT102 is independently identified as `ipfs1.diagnostics.kane-il.us` and is stopped;
- relay socket is enabled and active on `10.110.0.21:8046`;
- relay service is active and targets `192.168.1.106:8046`;
- actual host listener exists on `10.110.0.21:8046`;
- host NAT contains `192.168.0.0/16 -> vmbr0 MASQUERADE`;
- that NAT rule is persisted by the `vmbr1` `post-up` / `post-down` configuration in `/etc/network/interfaces`;
- no `netfilter-persistent` service is installed on this host;
- `wg-quick@wg0.service` is enabled and active and the protected WireGuard configuration exists.

**proxmox1 relay/network persistence status: PROVISIONALLY ACCEPTED for the current publication path.**

No routing, NAT, bridge, firewall, or WireGuard change is justified by the evidence collected so far.

### CT106 application state

Observed:

- service is active;
- PID `1167`;
- zero service restarts at the audit checkpoint;
- effective service has no drop-ins;
- effective `ExecStart` is only:
  `/usr/bin/python3 /opt/civic-publication/publication_service.py`;
- live listener is `192.168.1.106:8046`;
- current on-disk script SHA-256:
  `43e3ec41d243bd859dff290ae646dcf5a12c72065ffc56e5a4e373ab1a95fdcc`;
- retained pre-H4 script SHA-256:
  `9a349b949ec9eae260b88213eacca13c3d852a43441a0501b1728ea79a12c835`;
- retained pre-H4 script hard-codes `HOST = "192.168.1.106"`, `PORT = 8046`;
- current on-disk script defines:
  `DEFAULT_HOST = "127.0.0.1"`,
  `DEFAULT_PORT = 8046`,
  and `MAX_ARTIFACT_BYTES = 262144`;
- current script accepts `--listen`, `--port`, and `--credential-name`;
- effective systemd unit supplies none of those arguments.

### Remaining CT106 pre-write audit

Additional observations:

- CT106 runs systemd 257 (257.8-1~deb13u2), which supports systemd credentials;
- `/etc/civic-publication` is absent;
- `/etc/civic-publication/credentials` is absent;
- `publication-service.json` is absent;
- `/etc/systemd/system/civic-publication.service.d` is absent;
- both `ipfs.service` and `kubo.service` are inactive;
- no listeners were observed on TCP 4001, 5001, or 8080.

These facts close the CT106 read-only pre-write audit. The first repair must establish restart-safe service configuration without restarting the service and without enabling authentication or Kubo in the same write.

### Confirmed restart drift

The restart defect is now proved directly from production:

1. PID 1167 is an older loaded implementation whose server is currently bound to `192.168.1.106:8046`.
2. The effective systemd unit supplies no explicit listen address.
3. The replacement file already present at the same path defaults to `127.0.0.1`.
4. Therefore a restart under the current unit would execute the replacement file with its loopback default and would no longer satisfy the relay target `192.168.1.106:8046`.

This is **restart drift**, not current runtime failure.

**CT106 application status: RUNNING BUT NOT RESTART-SAFE; production acceptance is blocked until this drift is repaired and verified.**

No intentional CT106 restart is permitted before the unit is made restart-safe.

### CT106 restart-safety repair in progress

First production writes completed and verified:

1. created `/etc/systemd/system/civic-publication.service.d` as `root:root`, mode `0755`;
2. created `10-listen.conf` as `root:root`, mode `0644`, containing only the explicit restart-safe ExecStart override:
   `/usr/bin/python3 /opt/civic-publication/publication_service.py --listen 192.168.1.106 --port 8046`;
3. static `systemd-analyze verify` completed without reported errors;
4. running PID remained `1167`, `NRestarts=0`, service active/running;
5. live listener remained `192.168.1.106:8046`.

The systemd manager was then reloaded as a separate bounded write. Verification after `daemon-reload` showed:

- effective unit includes `10-listen.conf`;
- manager `ExecStart` is `/usr/bin/python3 /opt/civic-publication/publication_service.py --listen 192.168.1.106 --port 8046`;
- `DropInPaths` contains only the expected restart-safety drop-in;
- PID remained `1167`;
- `NRestarts=0`;
- service remained active/running;
- live listener remained `192.168.1.106:8046`.

**CT106 bind restart drift is repaired in systemd manager state.**

### Controlled restart acceptance

A controlled restart was performed from inside CT106 after the explicit bind override had been loaded.

Post-restart evidence:

- new PID: `293`;
- `NRestarts=0`;
- service active/running;
- effective ExecStart includes `--listen 192.168.1.106 --port 8046`;
- actual listener is `192.168.1.106:8046`;
- `GET /healthz` returns validation-only status with `kubo_enabled=false` and `swarm_enabled=false`;
- both `ipfs.service` and `kubo.service` remain inactive.

**CT106 bind restart-safety gate: ACCEPTED.**

H4 credential provisioning and authenticated validation-only acceptance remain pending.

## Remaining acceptance order

1. finish read-only `proxmox1` and CT106 audit;
2. classify all CT106 runtime/restart/repository drift;
3. repair restart safety before any intentional CT106 restart;
4. provision and accept H4 credential without enabling Kubo;
5. update and accept CT105 at the current repository revision;
6. reconcile the P4-006 Kane deployment policy values;
7. deploy and accept Usermin U-002;
8. complete U-003 broker-to-CT105 authenticated transport;
9. complete U-004 validation-only end-to-end evidence;
10. perform a separate Phase 4 first-side-effect gate before any Kubo publication.

No step in this sequence authorizes CT102/IPFS1 or Kubo side effects.
