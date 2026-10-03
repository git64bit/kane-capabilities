# Kane Deployment Facts

## Purpose

This file records **confirmed live deployment facts** that future work may rely on without rediscovering them.

It is intentionally narrow. A fact belongs here only after it has been observed on the live system or explicitly confirmed by the operator. Architectural intent belongs in the architecture and placement documents instead.

Do not infer an unrecorded host, CT number, address, route, or service placement from a component name.

## Interaction node: `witness-hubzilla`

**Confirmed 2026-10-02 from a root shell inside the container.**

The current Kane deployment co-locates these two Civic interaction surfaces in the container whose hostname is:

```text
witness-hubzilla
```

The container hosts:

- Witness / Hubzilla;
- Portal / Usermin.

This is a deployment fact, not a requirement that future or independent deployments co-locate them.

Observed service/runtime facts:

```text
hostname: witness-hubzilla
Python:   3.12.3

usermin.service:
  LoadState=loaded
  ActiveState=active
  SubState=running

civic-participants:
  gid 1004
  member sase25sep26a
```

The same container also matches the earlier production Usermin discovery recorded in `PHASE3_USERMIN_ADAPTER_BOUNDARY.md`, including Linux AF_UNIX / `SO_PEERCRED`, systemd, Python 3.12, and the `civic-participants` participant boundary.

At the 2026-10-02 pre-deployment check, the Usermin publication broker systemd units had **not yet been installed**:

```text
civic-usermin-broker.socket:
  LoadState=not-found
  ActiveState=inactive

civic-usermin-broker.service:
  LoadState=not-found
  ActiveState=inactive
  SubState=dead
```

No separate Portal/Usermin container has been established in this repository. Do not tell an operator to leave `witness-hubzilla` merely because the task concerns Usermin/Portal.

The physical host for `witness-hubzilla` is `annales`, confirmed by the operator on 2026-10-02. The container/VM numeric identifier is not recorded here. Do not invent it.

## Publication node: `publication1`

The current publication-service container is separately documented as `publication1` / CT106 in the publication deployment records.

During 2026-10-02 cleanup, the temporary unpublished authentication experiment was removed:

- `20-auth.conf` absent;
- temporary `publication-service.json` credential absent;
- accepted `10-listen.conf` retained;
- service remained active with PID 293 and `NRestarts=0` at the time of verification.

These facts do not establish the final IPFS network topology.


### Usermin broker deployment progress — 2026-10-02

Confirmed inside `witness-hubzilla`:

```text
civic-usermin-broker service account:
  uid=999
  gid=988
  home=/nonexistent
  shell=/usr/sbin/nologin

created directories:
  /opt/civic-usermin-broker   root:root 0755
  /etc/civic-orchestrator     root:root 0755
```

No Usermin broker systemd unit, socket activation, Orchestrator route, or network change was made by this step.


### Usermin broker Python prerequisite — 2026-10-02

On `witness-hubzilla`, creating `/opt/civic-usermin-broker/venv` with Python 3.12.3 failed because `ensurepip` is unavailable. The host requires the Debian/Ubuntu `python3.12-venv` package before the broker virtual environment can be completed.

The failed attempt created only a partial `/opt/civic-usermin-broker/venv` directory; no Civic package, systemd unit, or service was installed or activated.


### Usermin broker Python venv prerequisite installed — 2026-10-02

Confirmed on `witness-hubzilla`:

```text
python3.12-venv      installed
python3-pip-whl      installed as dependency
python3-setuptools-whl installed as dependency
```

No packages were upgraded. The install reported 35 packages not upgraded. No Civic service was installed or activated by this package step.

The earlier `/opt/civic-usermin-broker/venv` remains a partial venv created before `python3.12-venv` was available and must be replaced before use.


### Usermin broker virtual environment ready — 2026-10-02

Confirmed on `witness-hubzilla` after installing `python3.12-venv`:

```text
/opt/civic-usermin-broker/venv
  Python 3.12.3
  pip 24.0
```

The earlier partial venv was removed and recreated cleanly. No Civic package, systemd unit, socket, Orchestrator route, or credential was installed by this step.


### Usermin broker pinned source reachable — 2026-10-02

Confirmed from inside `witness-hubzilla` that the exact repository revision below is reachable from GitHub/codeload over HTTPS:

```text
3ea891a0e0e5d361ac8380f8b0dd41e7d5a42ab1
HTTP status: 200
content type: application/x-gzip
```

GitHub Actions for that exact revision completed successfully before installation was attempted.


### Usermin broker code installed — 2026-10-02

Confirmed on `witness-hubzilla`:

```text
venv: /opt/civic-usermin-broker/venv
source revision: 3ea891a0e0e5d361ac8380f8b0dd41e7d5a42ab1
package: civic-orchestrator 0.1.0
```

The package and its Python dependencies installed successfully from the exact pinned GitHub revision. These modules imported successfully from the production venv:

```text
civic_orchestrator
civic_orchestrator.usermin_adapter
civic_orchestrator.usermin_broker
civic_orchestrator.usermin_remote
civic_orchestrator.usermin_upload
```

No systemd unit, broker socket, participant registry, Orchestrator route, or credential was installed or activated by this step.


### Usermin participant Unix identity confirmed — 2026-10-02

Confirmed on `witness-hubzilla` immediately before participant-registry provisioning:

```text
username: sase25sep26a
uid:      1002
gid:      1003
home:     /home/sase25sep26a
shell:    /bin/bash
groups:
  1003 sase25sep26a
  1004 civic-participants
```

These Unix identifiers are deployment locators only. The publication registry must assign a separate stable Civic `participant_id` and must not derive permanent publication identity from the username or UID.


### Stable Usermin participant identity provisioned — 2026-10-02

Confirmed on `witness-hubzilla`:

```text
username:       sase25sep26a
uid:            1002
participant_id: participant:f58aeb92-f8fd-49f4-b314-d77c2b3e8536
registry:       /etc/civic-orchestrator/participants-v1.json
```

The participant ID is a stable Civic provenance identifier and is not derived from the Unix username or UID.

Initial registry creation produced `root:root 0600`. Because the production broker service runs as the non-root `civic-usermin-broker` account, deployment must grant that service read access while retaining root ownership and prohibiting group/world write; the intended live mode is therefore `root:civic-usermin-broker 0640`.


### Usermin participant registry permissions confirmed — 2026-10-02

Confirmed on `witness-hubzilla` after correcting the initial root-only mode:

```text
/etc/civic-orchestrator/participants-v1.json
owner: root
group: civic-usermin-broker
mode:  0640
```

The non-root `civic-usermin-broker` account successfully read the registry. The active mapping at that point was:

```text
sase25sep26a / uid 1002
  -> participant:f58aeb92-f8fd-49f4-b314-d77c2b3e8536
```


### Usermin broker socket unit installed — 2026-10-02

Confirmed on `witness-hubzilla`:

```text
/etc/systemd/system/civic-usermin-broker.socket
```

The unit matches the repository deployment asset and has not yet been enabled or started.

A standalone `systemd-analyze verify` reported that the matching `civic-usermin-broker.service` was not loaded, so the socket could not yet be validated as a startable pair. This is expected until the service unit is installed.


### Usermin broker service unit installed and pair verified — 2026-10-02

Confirmed on `witness-hubzilla`:

```text
/etc/systemd/system/civic-usermin-broker.socket
/etc/systemd/system/civic-usermin-broker.service
```

`systemd-analyze verify` completed with no output when both units were checked together, indicating the pair is syntactically and structurally valid. Neither unit had yet been enabled or started at this point.


### Usermin U-002 production acceptance — 2026-10-02

U-002 was accepted on the real production Portal/Usermin host `witness-hubzilla`.

Observed acceptance evidence:

```text
civic-usermin-broker.socket:
  ActiveState=active
  SubState=listening

/run/civic-orchestrator/usermin.sock:
  owner=civic-usermin-broker
  group=civic-participants
  mode=0660

participant:
  sase25sep26a
  uid=1002
  participant_id=participant:f58aeb92-f8fd-49f4-b314-d77c2b3e8536

artifact:
  size_bytes=33
  sha256=f93c8e21400f06755c4965593a81b24d6dcc6ca6b4abab17e71896133149156e
  media_type=application/octet-stream

broker result:
  status=validated
  remote_dispatch=false

civic-usermin-broker.service:
  ActiveState=active
  SubState=running
  MainPID=716923
  NRestarts=0
```

This acceptance proves the deployed participant-byte -> AF_UNIX -> `SO_PEERCRED` -> stable participant-ID path with no remote Orchestrator dispatch and no publication side effect.


### Usermin-to-CT105 route probe — 2026-10-02

Confirmed from `witness-hubzilla`:

```text
ip route get 10.20.0.15
  via 10.56.172.1 dev eth0
  source 10.56.172.200

TCP connect to 10.20.0.15:8045
  result: TimeoutError
```

This confirms that a network route toward CT105's deployment address exists from `witness-hubzilla`, but the Civic Orchestrator is not reachable there on port 8045. This is consistent with the accepted CT105 invariant that the Orchestrator listener remains bound to `127.0.0.1:8045`.

U-003 therefore still requires an explicit authenticated ingress/transport path; direct participant-host access to the raw CT105 listener is not available.


### Usermin to srv-b Civic fabric reachability — 2026-10-02

Confirmed from the production participant account on `witness-hubzilla`:

```text
witness-hubzilla wg0: 10.110.0.19/22

route to srv-b:
  destination 10.110.0.12
  dev wg0
  source 10.110.0.19

ICMP:
  2/2 replies from 10.110.0.12
  0% packet loss
```

This confirms that `witness-hubzilla` and `srv-b` already share the established witness/CPE WireGuard fabric `10.110.0.0/22`. U-003 does not require routing between the separate diagnostics `10.0.0.0/24` WireGuard fabric and the witness/CPE fabric.


### CT105 U-003 private ingress units verified — 2026-10-02

Confirmed inside `srv-b` CT105 `civic-orchestrator`:

```text
/etc/systemd/system/civic-orchestrator-ingress.socket
/etc/systemd/system/civic-orchestrator-ingress.service
```

`systemd-analyze verify` completed with no output when both units were checked together.

The intended relay boundary is:

```text
10.20.0.15:8045
    -> systemd-socket-proxyd
    -> 127.0.0.1:8045
```

The units had not yet been started at this checkpoint.


### CT105 U-003 private ingress activated and verified — 2026-10-02

Confirmed inside `srv-b` CT105 `civic-orchestrator`:

```text
civic-orchestrator-ingress.socket:
  ActiveState=active
  SubState=listening

listener:
  10.20.0.15:8045
  owner process: systemd socket activation

GET http://10.20.0.15:8045/healthz:
  {"available_operations":1,"side_effects":true,"status":"ok"}
```

This proves the CT105 private ingress relay reaches the existing loopback-only Orchestrator service. The Orchestrator itself remains bound to `127.0.0.1:8045`.


### U-003 host-boundary correction — 2026-10-02

The temporary repository proposal for a `systemd-socket-proxyd` application relay on the physical `srv-b` Proxmox host was rejected before live deployment and removed from the repository.

No Civic relay daemon was installed on `srv-b`.

The accepted boundary is:

```text
witness-hubzilla / 10.110.0.19
    -> existing WireGuard fabric
srv-b / 10.110.0.12
    -> narrowly scoped host routing/firewall/NAT only
CT105 / 10.20.0.15:8045
    -> CT-local ingress relay
127.0.0.1:8045 Civic Orchestrator
```

The virtualization host remains network/hypervisor substrate rather than an application host.


### srv-b U-003 network-policy baseline — 2026-10-02

Confirmed on physical Proxmox host `srv-b` before adding the Usermin U-003 route:

```text
net.ipv4.ip_forward = 1

FORWARD policy = ACCEPT

existing WireGuard -> vmbr1 DNAT pattern:
  10.110.0.1 -> 10.110.0.12:8300
      DNAT -> 10.20.0.14:3000

  10.110.0.1 -> 10.110.0.12:8770
      DNAT -> 10.20.0.10:8770

POSTROUTING:
  10.20.0.0/24 -> wg0 MASQUERADE

persistence mechanism:
  iptables-persistent / netfilter-persistent
  /etc/iptables/rules.v4
```

The host already implements WireGuard-to-private-service-network routing/NAT as infrastructure policy. U-003 can therefore use the same established mechanism without adding a Civic application daemon to the Proxmox host.


### srv-b temporary U-003 DNAT installed — 2026-10-02

Confirmed on physical Proxmox host `srv-b`:

```text
-A PREROUTING
  -s 10.110.0.19/32
  -d 10.110.0.12/32
  -i wg0
  -p tcp
  --dport 8045
  -j DNAT
  --to-destination 10.20.0.15:8045
```

This rule is live only and has not yet been persisted to `/etc/iptables/rules.v4`.

Purpose:

```text
witness-hubzilla 10.110.0.19
    -> srv-b 10.110.0.12:8045
    -> DNAT
    -> CT105 10.20.0.15:8045
    -> CT105 ingress relay
    -> Orchestrator 127.0.0.1:8045
```


### U-003 Civic fabric path verified from participant shell — 2026-10-02

Confirmed from the ordinary participant shell:

```text
account: sase25sep26a
host: witness-hubzilla
source WireGuard identity: 10.110.0.19
destination: http://10.110.0.12:8045/healthz
HTTP status: 200

response:
{"available_operations":1,"side_effects":true,"status":"ok"}
```

This was not an operator/root connectivity test. It proves that a participant process can traverse the existing Civic WireGuard fabric and the temporary `srv-b` DNAT path to the CT105 private ingress, which then reaches the loopback-only Orchestrator.

Because participant Terminal access is part of the accepted Usermin design, U-003 must now prove that this same participant cannot submit an Orchestrator operation without the broker-held protected adapter credential.


### U-003 participant bypass rejection accepted — 2026-10-02

Confirmed from the ordinary participant shell `sase25sep26a@witness-hubzilla` against the live Civic ingress:

```text
POST http://10.110.0.12:8045/v1/operations
Authorization header: absent

HTTP/1.0 401 Unauthorized

{
  "contract_version": 1,
  "failure_class": "unauthorized",
  "message": "adapter credential is required",
  "operation": "audit.invalid_request",
  "request_id": "invalid:request",
  "retryable": false,
  "side_effects": false
}
```

This proves the accepted Terminal coexistence invariant: an ordinary participant can reach the Civic network ingress but cannot bypass the Usermin broker and directly exercise an Orchestrator operation without the protected adapter credential.


### U-003 srv-b route persisted — 2026-10-02

Confirmed on physical Proxmox host `srv-b`:

```text
/etc/iptables/rules.v4:
  -A PREROUTING -s 10.110.0.19/32 -d 10.110.0.12/32 -i wg0 -p tcp -m tcp --dport 8045 -j DNAT --to-destination 10.20.0.15:8045

netfilter-persistent:
  enabled
```

The identical DNAT rule was already live before persistence, so no firewall reload was required.

This makes the accepted Usermin-to-CT105 Civic fabric route reboot-persistent using the existing `srv-b` network-control mechanism, with no Civic application daemon installed on the Proxmox host.


### CT105 U-003 credential state confirmed — 2026-10-02

Confirmed inside `srv-b` CT105 `civic-orchestrator`:

```text
civic-orchestrator.service:
  ActiveState=active
  SubState=running
  MainPID=12520
  NRestarts=0

drop-ins:
  20-publication-client.conf
  30-authenticated-publication.conf

/etc/civic-orchestrator/credentials/usermin-adapter.json:
  owner=root
  group=root
  mode=0600
  size=279 bytes
  version=1
  token length=64

binding:
  authenticated_by=adapter:usermin-broker
  caller_authority=portal-participant-registry
  client_id=usermin-broker
  client_kind=service
  subject_prefix=participant:
```

The participant-shell negative test already returned `401 adapter credential is required`, which proves the running Orchestrator is enforcing the configured adapter authentication boundary.

At this checkpoint `civic-orchestrator-ingress.socket` was active but not enabled for boot persistence.


### CT105 U-003 ingress persistence accepted — 2026-10-02

Confirmed inside `srv-b` CT105 `civic-orchestrator`:

```text
civic-orchestrator-ingress.socket:
  enabled
  ActiveState=active
  SubState=listening
```

The CT105 private ingress is now reboot-persistent and remains active without restarting the Civic Orchestrator.


### U-003 network path clean and persistent — 2026-10-02

Confirmed on physical Proxmox host `srv-b`:

```text
live DNAT rule count for 10.110.0.19 -> 10.110.0.12:8045 = 1
persistent /etc/iptables/rules.v4 entries for that route = 1
```

The live and reboot-persistent states now match exactly:

```text
10.110.0.19 -> 10.110.0.12:8045
    DNAT -> 10.20.0.15:8045
```

No duplicate live rule exists.


### U-003 broker credential provisioned — 2026-10-02

Confirmed inside `annales` LXD container `witness-hubzilla`:

```text
/etc/civic-orchestrator/credentials/usermin-adapter.json
  owner=root
  group=root
  mode=0600
  size=279 bytes

one-shot credential receiver:
  bound temporarily to 10.110.0.19:48045
  accepted the transfer from CT105
  validated credential version/binding
  installed the credential
  exited after the single transfer
```

The credential was transferred directly from CT105 over the existing WireGuard fabric without printing the bearer token, committing it to Git, or creating a persistent administrative transport service.


### witness-hubzilla broker U-003 readiness — 2026-10-02

Confirmed on witness-hubzilla: the installed broker CLI supports `--orchestrator-base-url` and `--adapter-credential-name`, and `civic_orchestrator.usermin_remote` is installed. The live service remains configured for U-002 local-only operation. `/etc/civic-orchestrator/usermin-broker.env` and `/etc/systemd/system/civic-usermin-broker.service.d/30-remote.conf` were absent at this checkpoint. No broker package upgrade is required before enabling U-003 remote dispatch.


### witness-hubzilla U-003 broker overlay verified — 2026-10-02

Confirmed on `witness-hubzilla` before broker restart:

```text
/etc/civic-orchestrator/usermin-broker.env:
  CIVIC_ORCHESTRATOR_BASE_URL=http://10.110.0.12:8045
  owner=root
  mode=0600

/etc/systemd/system/civic-usermin-broker.service.d/30-remote.conf:
  EnvironmentFile=/etc/civic-orchestrator/usermin-broker.env
  LoadCredential=usermin-adapter.json:/etc/civic-orchestrator/credentials/usermin-adapter.json
  ExecStart includes --orchestrator-base-url and --adapter-credential-name
  RestrictAddressFamilies=AF_UNIX AF_INET AF_INET6

credential source:
  /etc/civic-orchestrator/credentials/usermin-adapter.json
  root:root 0600
  279 bytes

systemd-analyze verify:
  clean (no output)
```

The broker had not yet been restarted at this checkpoint.


### witness-hubzilla U-003 broker restart accepted — 2026-10-02

Confirmed after applying the U-003 remote-dispatch overlay:

```text
civic-usermin-broker.service
  MainPID=725079
  Result=success
  NRestarts=0
  ActiveState=active
  SubState=running
```

Journal for the restart window showed a clean stop and start with no credential, network, or startup errors. The broker is now running with the U-003 Orchestrator endpoint and systemd-loaded adapter credential.


### U-003 authenticated participant dispatch reached Orchestrator — 2026-10-02

Confirmed from ordinary participant shell `sase25sep26a@witness-hubzilla` using `civic_orchestrator.usermin_upload`:

```text
participant file:
  /home/sase25sep26a/u003-test.txt
  owner=sase25sep26a
  mode=0644
  size=41 bytes

broker result:
  remote_dispatch=true
  status=rejected
  orchestrator_http_status=502
  failure_class=internal
  retryable=true
  side_effects=true
  message="publication service failure returned a different workflow_id"
```

This proves the U-003 authenticated path through the local broker, protected adapter credential, Civic network route, CT105 ingress, and Orchestrator. The remaining failure is downstream in the Orchestrator-to-publication-service workflow contract, not in Usermin transport or broker authentication.


### CT105 publication-client credential state confirmed — 2026-10-02

Confirmed inside `srv-b` CT105 `civic-orchestrator` after the first authenticated Usermin dispatch reached the publication boundary:

```text
30-authenticated-publication.conf:
  LoadCredential=usermin-adapter.json
  LoadCredential=publication-service.json
  publication-base-url=http://10.110.0.21:8046
  publication-credential-name=publication-service.json

/etc/civic-orchestrator/credentials/publication-service.json:
  owner=root
  group=root
  mode=0600
  size=89 bytes
  version=1
  token_length=64

GET http://10.110.0.21:8046/healthz:
  {"kubo_enabled":false,"phase":"validation-only","service":"civic-publication","status":"ok","swarm_enabled":false}
```

Therefore CT105 has the expected publication-service credential source and can reach CT106. The remaining failure must be resolved at the CT106 authentication state or credential match, not at Usermin transport.


### CT106 publication authentication defect identified — 2026-10-02

Confirmed inside `proxmox1` CT106 `publication1`:

```text
civic-publication.service:
  ActiveState=active
  SubState=running
  MainPID=293
  NRestarts=0
  effective drop-ins:
    10-listen.conf only

effective ExecStart:
  /usr/bin/python3 /opt/civic-publication/publication_service.py
    --listen 192.168.1.106
    --port 8046

/etc/civic-publication/credentials/publication-service.json:
  ABSENT

effective service contains no:
  LoadCredential=publication-service.json:...
  --credential-name publication-service.json
```

This explains the authenticated Usermin dispatch failure. The CT106 publication service has no bearer credential configured, so its current implementation returns a pre-request authentication/service failure using `workflow_id=wf:invalid`. CT105 then correctly rejects that response because it cannot correlate `wf:invalid` to the real workflow.

The Usermin U-003 broker/network/authentication path is therefore proven; the remaining blocker is the previously pending CT106 publication-service authentication gate.


### CT106 one-shot publication credential receiver ready — 2026-10-02

Confirmed inside `proxmox1` CT106 `publication1`:

```text
temporary receiver:
  192.168.1.106:48046
  process=python3
  state=LISTEN
  log state=READY
```

The receiver exists only inside CT106 and is intended to accept a single publication-service credential transfer, validate it, install it root-owned mode 0600, and exit. The publication service itself has not yet been reconfigured or restarted.


### proxmox1 H4 credential-transfer network baseline — 2026-10-02

Confirmed read-only on physical Proxmox host `proxmox1` before temporary CT106 credential transfer:

```text
net.ipv4.ip_forward = 1
FORWARD policy = ACCEPT
PREROUTING policy = ACCEPT
POSTROUTING policy = ACCEPT

POSTROUTING:
  -s 192.168.0.0/16 -o vmbr0 -j MASQUERADE

PREROUTING:
  no rules present at this checkpoint
```

The attempted combined `ip -brief addr show wg0 vmbr1` command was rejected by `ip` syntax and made no change.


### proxmox1 H4 transfer interfaces confirmed — 2026-10-02

Confirmed on physical host `proxmox1`:

```text
wg0   10.110.0.21/32
vmbr1 192.168.1.1/16
```

These addresses match the accepted publication-stack topology. The temporary CT106 credential-transfer DNAT can therefore target `10.110.0.21:48046 -> 192.168.1.106:48046`.


### proxmox1 temporary H4 credential-transfer DNAT active — 2026-10-02

Confirmed on physical host `proxmox1`:

```text
-A PREROUTING
  -s 10.110.0.12/32
  -d 10.110.0.21/32
  -i wg0
  -p tcp
  --dport 48046
  -j DNAT
  --to-destination 192.168.1.106:48046
```

The rule is live only and is not persisted. It exists solely for the one-shot transfer of the existing CT105 publication-service credential into CT106.


### CT106 publication credential installed — 2026-10-02

Confirmed inside `proxmox1` CT106 `publication1`:

```text
/etc/civic-publication/credentials/publication-service.json
  owner=root
  group=root
  mode=0600
  size=89 bytes

one-shot receiver:
  state=INSTALLED
  receiver process exited after the single transfer
  listener 192.168.1.106:48046 no longer present
```

The bearer token was not printed or committed. The temporary network aperture on `proxmox1` remains to be removed before configuring the publication service.


### proxmox1 temporary H4 transfer DNAT removed — 2026-10-02

Confirmed on physical host `proxmox1` after CT106 received the publication credential:

```text
temporary PREROUTING rule for TCP/48046:
  removed

verification:
  no PREROUTING entry matching 48046 remains
```

The one-time credential-transfer aperture is closed before any publication-service configuration or restart.


### CT106 publication authentication overlay staged — 2026-10-02

Confirmed inside `proxmox1` CT106 `publication1`:

```text
/etc/systemd/system/civic-publication.service.d/20-authentication.conf:
  owner=root
  group=root
  mode=0644
  size=285 bytes

systemd-analyze verify:
  clean (no output)

running service before daemon-reload:
  MainPID=293
  NRestarts=0
  ActiveState=active
  SubState=running
```

The authentication overlay is staged on disk and has not yet changed the running publication service.


### CT106 authentication overlay did not enter effective unit — 2026-10-02

After `systemctl daemon-reload` inside CT106:

```text
DropInPaths:
  10-listen.conf
  20-authentication.conf

running service:
  MainPID=293
  NRestarts=0
  ActiveState=active
  SubState=running
```

However, `systemctl cat civic-publication.service` showed only the path header for `20-authentication.conf` and no effective contents from that file. The effective ExecStart remained the unauthenticated `10-listen.conf` command, with no visible `LoadCredential` or `--credential-name`.

No restart was performed. CT106 is therefore not yet restart-ready for authenticated publication.


### CT106 authenticated unit manager state verified — 2026-10-02

Confirmed inside `publication1` after daemon-reload:

```text
effective ExecStart:
  /usr/bin/python3 /opt/civic-publication/publication_service.py
    --listen 192.168.1.106
    --port 8046
    --credential-name publication-service.json

DropInPaths:
  10-listen.conf
  20-authentication.conf

LoadCredential:
  present in systemd manager state
  displayed by systemctl as [unprintable]
```

The service had not yet been restarted at this checkpoint. The authenticated CT106 unit is ready for a controlled restart.


### CT106 authenticated validation-only service accepted — 2026-10-02

Confirmed after controlled restart inside `publication1`:

```text
civic-publication.service:
  MainPID=429
  Result=success
  NRestarts=0
  ActiveState=active
  SubState=running

listener:
  192.168.1.106:8046

GET /healthz:
  {"kubo_enabled":false,"phase":"validation-only","service":"civic-publication","status":"ok","swarm_enabled":false}
```

The CT106 publication service is now running with its protected publication-service credential while remaining explicitly validation-only; Kubo and swarm are still disabled.


### First authenticated Usermin workflow persisted in recovery state — 2026-10-02

CT105 read-only state for workflow `wf:e1a11128-ca42-423d-bfab-879831967cb2`:

```text
request_id=req:usermin:a7b7e2231db04a01b07936f1b1777454
operation=publication.publish
state=waiting
side_effects=1
side_effects_certainty=unknown

publication budget hold:
  participant_id=participant:f58aeb92-f8fd-49f4-b314-d77c2b3e8536
  size_bytes=41
  hold_state=uncertain
```

Audit sequence confirms:
1. civic.authorization.allowed
2. civic.operation.accepted
3. civic.service.selected
4. civic.operation.waiting due to the then-unconfigured CT106 publication authentication boundary.

This workflow must be resumed or explicitly reconciled; a second independent participant publication must not be used to bypass the conservative budget hold.


### Explicit publication reconciliation primitive verified — 2026-10-03

The repository now contains an operator-only no-effect reconciliation path for a waiting publication workflow whose prior dispatch was conservatively recorded as uncertain.

Safety conditions require:

- operation is `publication.publish`;
- workflow state is `waiting`;
- prior `side_effects=true`;
- prior `side_effects_certainty=unknown`;
- budget hold is `uncertain`;
- no publication record exists for the workflow.

Successful reconciliation leaves the workflow waiting, records `side_effects=false` with certainty `known`, changes the existing hold to `reserved`, and appends `civic.operation.reconciled` audit evidence.

GitHub Actions run 37135078489 passed the complete unit suite on Python 3.11, 3.12, and 3.13.


### First Usermin workflow explicitly reconciled — 2026-10-03

Workflow `wf:e1a11128-ca42-423d-bfab-879831967cb2` was explicitly reconciled after direct operator evidence proved the original failed CT106 dispatch could not have produced a publication side effect.

Verified post-reconciliation state:

```text
workflow:
  state=waiting
  side_effects=0
  side_effects_certainty=known

publication budget hold:
  size_bytes=41
  hold_state=reserved

latest audit event:
  sequence=5
  event_type=civic.operation.reconciled
  actor=operator:publication-recovery
  resolution=no-external-side-effect
```

The original reservation is preserved; no second publication workflow or budget slot was created.


### U-003 authenticated transport accepted — 2026-10-03

The reconciled workflow `wf:e1a11128-ca42-423d-bfab-879831967cb2` was resumed with the original semantic request and original request ID after CT106 authentication was provisioned.

Observed result:

```text
HTTP 503
failure_class=backend-unavailable
service_failure_class=service-unavailable
message="publication bytes validated; Kubo publication is not enabled yet"
retryable=true
side_effects=false
side_effects_certainty=known
workflow_state=waiting
workflow_id=wf:e1a11128-ca42-423d-bfab-879831967cb2
SAME_WORKFLOW=True
```

This is the intended validation-only backend result. It proves the authenticated chain from participant broker through CT105 and onward to authenticated CT106 while preserving the same workflow and producing no Kubo side effect.

**U-003 production status: ACCEPTED.**

U-004 remains pending and requires the real Usermin Custom Command surface.
