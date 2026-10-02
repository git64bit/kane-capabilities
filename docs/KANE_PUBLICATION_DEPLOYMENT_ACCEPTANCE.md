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

## CT106 known state before re-audit

The following observations were established earlier and must be independently re-checked before any CT106 write:

- service active under the old loaded Python process;
- listener `192.168.1.106:8046`;
- reviewed H4-capable script installed on disk;
- previous script retained as `publication_service.py.pre-h4`;
- no H4 credential directory/file;
- no H4 systemd drop-in;
- Kubo/IPFS services inactive.

Critical restart drift to verify:

> The reviewed publication script defaults to loopback, while the existing live unit was previously observed without an explicit `--listen`. If still true, an unplanned restart could change the listener from `192.168.1.106:8046` to loopback.

CT106 is therefore not accepted until its current state and persistence are re-audited on `proxmox1`.

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
