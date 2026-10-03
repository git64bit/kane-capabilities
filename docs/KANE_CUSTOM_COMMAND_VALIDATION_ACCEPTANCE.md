# Kane Custom Command Local Validation Acceptance

## Status

**PAUSED BEFORE FIRST PRODUCTION WRITE — CURATED ACCESS RESOLVER REQUIRED**

Read-only Steps 0 through 2 were completed on 2026-10-03 and matched the expected live state. No generic Custom Command file, package, venv, socket, service, or Participant-home test artifact was written.

The former deployment candidate `925c2ed7c366124dfde5d8078c7ec2a06bdd2162` is superseded for live validation because it does not enforce the newly frozen per-Participant Custom Command access policy.

Do **not** execute Step 3 or later until:

1. runtime access-policy loading is implemented;
2. stable `participant_id` is resolved before discovery/invocation;
3. default-deny discovery and invocation are enforced;
4. `water-ants` is explicitly granted to the test Participant;
5. the revised candidate passes CI and this runbook is repinned.

This runbook validates the parallel generic Custom Command path on the current Kane Portal/Usermin host without changing the accepted publication-specific Usermin route.

## Scope

This runbook applies only inside the existing Kane interaction container:

```text
physical host: annales
container hostname: witness-hubzilla
role: Witness / Hubzilla + Portal / Usermin
```

The procedure contains no command for another physical host.

Do not modify:

- CT105;
- CT106;
- WireGuard;
- NAT/firewall/routing;
- the existing `civic-usermin-broker` service or its U-003 overlay;
- the existing `/run/civic-orchestrator/usermin.sock`;
- the visible Usermin Custom Command configuration.

The new validation path is:

```text
participant
  -> /usr/local/bin/civic-custom-command
  -> /run/civic-orchestrator/custom-command.sock
  -> civic-custom-command-broker.service
  -> SO_PEERCRED
  -> stable participant mapping
  -> Custom Command registry
  -> water-ants local stub
```

Expected result:

```text
status=stub
command=water-ants
operation=publication.publish
remote_dispatch=false
side_effects=false
```

## Safety invariants

The generic broker is deliberately isolated from the accepted publication broker.

Existing accepted environment:

```text
/opt/civic-usermin-broker/venv
/run/civic-orchestrator/usermin.sock
```

New validation environment:

```text
/opt/civic-custom-command-broker/venv
/run/civic-orchestrator/custom-command.sock
```

The new service has no Orchestrator URL, adapter credential, AF_INET/AF_INET6 permission, or remote publisher.

The existing publication broker process must not be restarted by this procedure.

## Step 0 — establish the correct container

Run inside the intended container before any write:

```sh
hostname
cat /etc/machine-id
systemctl is-active usermin.service
getent group civic-participants
getent passwd sase25sep26a
```

Required facts:

- hostname is exactly `witness-hubzilla`;
- Usermin is active;
- `sase25sep26a` exists;
- `sase25sep26a` is in `civic-participants`.

If any fact differs, stop.

## Step 1 — capture the accepted publication-broker baseline

Read only:

```sh
systemctl show civic-usermin-broker.service \
  -p MainPID -p NRestarts -p ActiveState -p SubState -p ExecStart

systemctl show civic-usermin-broker.socket \
  -p ActiveState -p SubState -p Listen

systemctl cat civic-usermin-broker.service
stat -Lc '%n %U:%G %a %s' /run/civic-orchestrator/usermin.sock
/opt/civic-usermin-broker/venv/bin/python -c \
  'import civic_orchestrator; print(civic_orchestrator.__version__)'
```

Record the existing publication broker `MainPID` and `NRestarts`. They must remain unchanged through this acceptance.

## Step 2 — confirm the generic path is not already deployed

Read only:

```sh
systemctl show civic-custom-command-broker.socket \
  -p LoadState -p ActiveState -p SubState 2>/dev/null || true

systemctl show civic-custom-command-broker.service \
  -p LoadState -p ActiveState -p SubState 2>/dev/null || true

test -e /run/civic-orchestrator/custom-command.sock && \
  stat -Lc '%n %U:%G %a %s' /run/civic-orchestrator/custom-command.sock || true

test -e /opt/civic-custom-command-broker/venv/bin/python && \
  /opt/civic-custom-command-broker/venv/bin/python --version || true
```

Unexpected pre-existing state is drift. Stop and classify it before writing.

## Step 3 — stage the exact repository archive

**BLOCKED. Do not execute this step while the Status above is PAUSED.**

Set shell variables; this changes no persistent state:

```sh
REV='925c2ed7c366124dfde5d8078c7ec2a06bdd2162'
ARCHIVE="/tmp/kane-capabilities-${REV}.tar.gz"
SRC="/tmp/kane-capabilities-${REV}"
```

Confirm neither staging target already exists:

```sh
test ! -e "$ARCHIVE"; echo "archive target clear: $?"
test ! -e "$SRC"; echo "source target clear: $?"
```

### Write 3A — download the pinned archive

One write:

```sh
curl -fL \
  "https://github.com/git64bit/kane-capabilities/archive/${REV}.tar.gz" \
  -o "$ARCHIVE"
```

Verify:

```sh
ls -l "$ARCHIVE"
tar -tzf "$ARCHIVE" | head -20
```

### Write 3B — extract the pinned archive

One write:

```sh
tar -xzf "$ARCHIVE" -C /tmp
```

Verify:

```sh
test -f "$SRC/pyproject.toml" && echo SOURCE_OK
test -f "$SRC/contracts/custom-command-registry-v1.yaml" && echo REGISTRY_OK
test -f "$SRC/contracts/custom-command-help-v1.yaml" && echo HELP_OK
test -f "$SRC/deploy/usermin/civic-custom-command-broker.service" && echo SERVICE_OK
```

All four markers are required.

## Step 4 — create the isolated Python environment

Precondition:

```sh
test ! -e /opt/civic-custom-command-broker/venv
```

### Write 4A — create the venv

One write:

```sh
python3.12 -m venv /opt/civic-custom-command-broker/venv
```

Verify:

```sh
/opt/civic-custom-command-broker/venv/bin/python --version
/opt/civic-custom-command-broker/venv/bin/pip --version
```

### Write 4B — install only the pinned package into the isolated venv

One write:

```sh
/opt/civic-custom-command-broker/venv/bin/pip install "$SRC"
```

Verify imports:

```sh
/opt/civic-custom-command-broker/venv/bin/python - <<'PY'
import civic_orchestrator
import civic_orchestrator.custom_commands
import civic_orchestrator.custom_command_broker
import civic_orchestrator.usermin_command
print("CUSTOM_COMMAND_IMPORTS_OK")
PY
```

The existing `/opt/civic-usermin-broker/venv` must not be modified.

## Step 5 — install the public command contracts

These files are non-secret, root-owned deployment contracts. Install them one at a time.

### Write 5A — command registry

```sh
install -o root -g root -m 0644 \
  "$SRC/contracts/custom-command-registry-v1.yaml" \
  /etc/civic-orchestrator/custom-command-registry-v1.yaml
```

Verify:

```sh
cmp -s \
  "$SRC/contracts/custom-command-registry-v1.yaml" \
  /etc/civic-orchestrator/custom-command-registry-v1.yaml && echo REGISTRY_MATCH
```

### Write 5B — command registry schema

```sh
install -o root -g root -m 0644 \
  "$SRC/schemas/custom-command-registry-v1.schema.json" \
  /etc/civic-orchestrator/custom-command-registry-v1.schema.json
```

Verify with `cmp`.

### Write 5C — help catalog

```sh
install -o root -g root -m 0644 \
  "$SRC/contracts/custom-command-help-v1.yaml" \
  /etc/civic-orchestrator/custom-command-help-v1.yaml
```

Verify with `cmp`.

### Write 5D — help schema

```sh
install -o root -g root -m 0644 \
  "$SRC/schemas/custom-command-help-v1.schema.json" \
  /etc/civic-orchestrator/custom-command-help-v1.schema.json
```

Verify with `cmp`.

## Step 6 — validate contracts before installing systemd units

Read only:

```sh
/opt/civic-custom-command-broker/venv/bin/python - <<'PY'
from pathlib import Path
from civic_orchestrator.custom_commands import CustomCommandRegistry

registry = CustomCommandRegistry.load(
    Path("/etc/civic-orchestrator/custom-command-registry-v1.yaml"),
    Path("/etc/civic-orchestrator/custom-command-registry-v1.schema.json"),
    Path("/etc/civic-orchestrator/custom-command-help-v1.yaml"),
    Path("/etc/civic-orchestrator/custom-command-help-v1.schema.json"),
)
print("commands", len(registry.value["commands"]))
print("water-ants", registry.lookup("water-ants")["lifecycle"])
print("binding", registry.lookup("water-ants")["binding"])
print("confirmation", registry.help_for("water-ants")["confirmation"])
PY
```

Required:

```text
commands 26
water-ants stub
binding ... publication.publish
confirmation explicit
```

## Step 7 — install the participant helper wrapper

### Write 7A

```sh
install -o root -g root -m 0755 \
  "$SRC/deploy/usermin/civic-custom-command" \
  /usr/local/bin/civic-custom-command
```

Verify without broker access:

```sh
runuser -u sase25sep26a -- \
  /usr/local/bin/civic-custom-command list

runuser -u sase25sep26a -- \
  /usr/local/bin/civic-custom-command help water-ants
```

Expected discovery shows `Publish File (water-ants) [stub]`.

Help must visibly include significant effects, consequences, incident guidance, and explicit acknowledgement.

## Step 8 — install the parallel systemd socket and service

### Write 8A — socket unit

```sh
install -o root -g root -m 0644 \
  "$SRC/deploy/usermin/civic-custom-command-broker.socket" \
  /etc/systemd/system/civic-custom-command-broker.socket
```

Verify with `cmp`.

### Write 8B — service unit

```sh
install -o root -g root -m 0644 \
  "$SRC/deploy/usermin/civic-custom-command-broker.service" \
  /etc/systemd/system/civic-custom-command-broker.service
```

Verify with `cmp`.

## Step 9 — static systemd validation before manager reload

Read only:

```sh
systemd-analyze verify \
  /etc/systemd/system/civic-custom-command-broker.socket \
  /etc/systemd/system/civic-custom-command-broker.service
```

Required: no output and exit status 0.

Inspect the service file:

```sh
grep -E 'ExecStart|RestrictAddressFamilies|LoadCredential|orchestrator' \
  /etc/systemd/system/civic-custom-command-broker.service
```

Required properties:

- isolated venv path;
- `RestrictAddressFamilies=AF_UNIX`;
- no `LoadCredential`;
- no Orchestrator URL.

## Step 10 — reload systemd manager state

### Write 10A

```sh
systemctl daemon-reload
```

Verify, without starting either new unit:

```sh
systemctl show civic-custom-command-broker.socket \
  -p LoadState -p ActiveState -p SubState

systemctl show civic-custom-command-broker.service \
  -p LoadState -p ActiveState -p SubState -p ExecStart
```

Expected before activation:

```text
LoadState=loaded
ActiveState=inactive
```

## Step 11 — start only the new validation socket

### Write 11A

```sh
systemctl start civic-custom-command-broker.socket
```

Do **not** enable it yet.

Verify:

```sh
systemctl show civic-custom-command-broker.socket \
  -p ActiveState -p SubState -p Listen

stat -Lc '%n %U:%G %a %s' \
  /run/civic-orchestrator/custom-command.sock
```

Required:

```text
ActiveState=active
SubState=listening
owner=civic-usermin-broker
group=civic-participants
mode=0660
```

The service may remain inactive until first use.

## Step 12 — create one bounded Participant test file

This is the only Participant-file write in the acceptance.

### Write 12A

```sh
runuser -u sase25sep26a -- sh -c \
  'umask 077; printf "%s\n" "water-ants local validation" > "$HOME/custom-command-validation.txt"'
```

Verify:

```sh
stat -Lc '%n %U:%G %a %s' \
  /home/sase25sep26a/custom-command-validation.txt

sha256sum /home/sase25sep26a/custom-command-validation.txt
```

## Step 13 — prove acknowledgement blocks accidental invocation

Run as the Participant without `--confirm`:

```sh
runuser -u sase25sep26a -- \
  /usr/local/bin/civic-custom-command \
  run water-ants \
  --file /home/sase25sep26a/custom-command-validation.txt
```

Required result is rejection containing:

```text
explicit participant confirmation is required: water-ants
remote_dispatch=false
side_effects=false
```

This rejection occurs in the participant helper before the generic invocation is sent.

## Step 14 — execute the confirmed local stub

Run as the Participant:

```sh
runuser -u sase25sep26a -- \
  /usr/local/bin/civic-custom-command \
  run water-ants \
  --file /home/sase25sep26a/custom-command-validation.txt \
  --confirm
```

Required result:

```text
status=stub
command=water-ants
operation=publication.publish
participant_id=participant:f58aeb92-f8fd-49f4-b314-d77c2b3e8536
remote_dispatch=false
side_effects=false
artifact.size_bytes=<test file size>
artifact.sha256=<matches sha256sum>
```

This invocation should socket-activate `civic-custom-command-broker.service`.

## Step 15 — inspect the activated generic broker

Read only:

```sh
systemctl show civic-custom-command-broker.service \
  -p MainPID -p NRestarts -p ActiveState -p SubState -p ExecStart

systemctl cat civic-custom-command-broker.service

ss -lxnp | grep -F /run/civic-orchestrator/custom-command.sock || true
```

Required:

- service active/running;
- `NRestarts=0`;
- effective command uses `/opt/civic-custom-command-broker/venv`;
- no credential or remote endpoint;
- generic socket remains AF_UNIX.

## Step 16 — prove the accepted publication broker was untouched

Read only:

```sh
systemctl show civic-usermin-broker.service \
  -p MainPID -p NRestarts -p ActiveState -p SubState -p ExecStart

systemctl show civic-usermin-broker.socket \
  -p ActiveState -p SubState -p Listen

stat -Lc '%n %U:%G %a %s' /run/civic-orchestrator/usermin.sock
```

Compare `MainPID` and `NRestarts` with Step 1.

Required:

- same publication broker PID;
- same restart count;
- existing publication socket still active;
- no Usermin configuration was changed.

## Step 17 — acceptance boundary

If all evidence matches, this establishes only:

```text
generic local frame                  accepted on real host
generic contract/help loading        accepted on real host
SO_PEERCRED participant binding      accepted on real host
water-ants registry binding          accepted on real host
help discovery                       accepted on real host
explicit acknowledgement barrier     accepted on real host
remote_dispatch=false                proven
side_effects=false                   proven
```

It does **not** establish:

- U-004;
- generic broker remote Orchestrator dispatch;
- IPFS publication;
- Usermin UI mapping to `water-ants`;
- enablement/persistence of the generic socket;
- any second Custom Command.

Do not update `KANE_DEPLOYMENT_FACTS.md` to ACCEPTED until the live outputs from Steps 0–16 have been reviewed.

## Deferred cleanup

The Participant test file may be removed later as a separate verified write. The generic socket should remain un-enabled until a persistence decision is made after acceptance.
