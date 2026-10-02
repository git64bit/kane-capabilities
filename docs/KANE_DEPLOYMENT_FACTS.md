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

The physical host and container/VM numeric identifier for `witness-hubzilla` are not recorded here. Do not invent them.

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
