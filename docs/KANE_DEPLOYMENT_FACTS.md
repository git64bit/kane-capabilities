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
