# CT105 Phase 1 Systemd Acceptance

## Status

**ACCEPTED** on 2026-10-01.

The Civic Orchestrator Phase 1 stub is installed as a persistent systemd service on CT105 `civic-orchestrator`.

## Service state

Observed:

```text
civic-orchestrator.service
Loaded:  loaded and enabled
Active:  active (running)
Runtime: /opt/civic-orchestrator/venv/bin/python
Module:  civic_orchestrator.server
State:   /var/lib/civic-orchestrator/state/orchestrator.sqlite3
```

## Listener boundary

Observed:

```text
LISTEN ... 127.0.0.1:8045 ... users:(("python",...))
```

This is the intended Phase 1 boundary.

The `0.0.0.0:*` field displayed by `ss` is the wildcard remote-peer field for the listening socket. The local bind remains `127.0.0.1:8045`.

No service-network or public listener is enabled.

## Health

Observed:

```json
{"phase":1,"side_effects":false,"status":"ok"}
```

Result: **PASS**

## Acceptance conclusion

The persistent Phase 1 runtime now proves:

- systemd startup;
- dedicated unprivileged service account;
- hardened unit;
- loopback-only HTTP listener;
- local SQLite workflow/audit/receipt state;
- no production backend adapter;
- no production network exposure;
- `side_effects=false`.

## Next gate

Add read-only local workflow evidence retrieval for the D-001 Demonstrator.

The next implementation may expose already-recorded local workflow/audit/receipt evidence, but must not introduce any production backend call or external side effect.
