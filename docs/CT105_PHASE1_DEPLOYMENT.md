# CT105 Phase 1 Stub Deployment

## Purpose

Deploy the contract-bearing Civic Orchestrator stub on CT105 without enabling any production backend capability.

## Runtime boundary

The Phase 1 service:

- binds only to `127.0.0.1:8045`;
- has no backend service adapters;
- performs no production network calls;
- records only local workflow/audit/receipt state;
- returns `side_effects=false`;
- runs as the unprivileged `civic-orchestrator` service account.

## Filesystem

Expected layout:

```text
/opt/civic-orchestrator/
  current/        repository checkout
  venv/           Python virtual environment

/var/lib/civic-orchestrator/
  state/
  audit/
  receipts/
  work/
  config/
  keys/
```

Only `state/` is used by the first runtime. The remaining directories reserve the authority boundaries for later phases.

## Initial acceptance

Before enabling the systemd service:

1. install the package into the dedicated virtualenv;
2. run `python -m unittest discover -s tests -v`;
3. start the server manually on loopback;
4. verify `GET /healthz`;
5. verify `GET /v1/capabilities`;
6. submit one known operation and confirm `status=not-implemented` and `side_effects=false`;
7. submit one prohibited/invalid operation and confirm fail-closed behavior.

Only after those pass should the systemd unit be enabled.

## Network

Do not open CT105 inbound firewall access during this gate.

Loopback-only binding is deliberate. Usermin, Hubzilla, Kane Fabric, Gitea, and Wiregate adapters are later gates.

## Service unit

Repository authority:

`deploy/civic-orchestrator.service`

Install to:

`/etc/systemd/system/civic-orchestrator.service`

Do not modify the unit to expose `0.0.0.0` during Phase 1.
