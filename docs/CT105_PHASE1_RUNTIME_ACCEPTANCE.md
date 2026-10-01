# CT105 Phase 1 Runtime Acceptance

## Status

**ACCEPTED** on 2026-10-01.

The Civic Orchestrator Phase 1 stub runtime passed unit and loopback HTTP acceptance on CT105 `civic-orchestrator`.

## Unit-test gate

Observed:

```text
Ran 6 tests in 1.747s

OK
```

The sixth test specifically exercised threaded submissions against SQLite after a runtime defect was found during the first HTTP trial.

## Runtime defect found and corrected

The first HTTP test exposed:

```text
sqlite3.ProgrammingError:
SQLite objects created in a thread can only be used in that same thread
```

Cause:

- `ThreadingHTTPServer` handled the request in a worker thread;
- the SQLite connection had been created once in the main thread;
- request processing attempted to reuse that connection.

Correction:

- the state layer now opens short-lived SQLite connections per state operation;
- WAL mode and foreign-key enforcement are set on each connection;
- a concurrent threaded regression test was added.

The corrected runtime passed the six-test suite.

## Loopback HTTP acceptance

Runtime boundary:

```text
listen: 127.0.0.1
port:   8045
phase:  1
```

### Health

Observed:

```json
{"phase":1,"side_effects":false,"status":"ok"}
```

Result: **PASS**

### Known bounded operation

Submitted:

```text
publication.publish
```

Observed result:

- contract version 1;
- workflow ID issued;
- receipt ID issued;
- implementation `stub`;
- service capability `publication.publish`;
- status `not-implemented`;
- `side_effects=false`.

Result: **PASS**

### Unknown bounded-namespace operation

Submitted:

```text
publication.unknown
```

Observed:

```text
failure_class = unknown-operation
retryable     = false
side_effects  = false
```

Result: **PASS**

### Prohibited generic operation

Submitted:

```text
shell.exec
```

Observed:

```text
failure_class = invalid-contract
operation     = audit.invalid_request
retryable     = false
side_effects  = false
```

This is intentional.

The request is rejected by the request schema before operation-registry lookup because `shell` is not an allowed Civic capability namespace. The public contract therefore cannot represent `shell.exec` as a valid Civic operation.

Result: **PASS**

## Acceptance conclusion

The Phase 1 runtime has now proven:

- schema validation;
- bounded operation registry;
- fail-closed unknown operation handling;
- schema-level rejection of prohibited generic capabilities;
- workflow ID issuance;
- receipt issuance;
- local SQLite state;
- threaded request safety;
- loopback HTTP operation;
- no production backend invocation;
- `side_effects=false`.

No production service adapter is enabled.

## Next gate

Install and enable the hardened systemd unit while keeping the service bound to `127.0.0.1:8045`.

No inbound CT105 service-network exposure is permitted yet.
