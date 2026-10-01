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

## Authorization evidence acceptance

On the persistent CT105 state store, a registered `publication.publish` request produced:

```text
workflow.state              = not-implemented
authorization decisions     = 1
decision                    = allow
policy                      = stub-policy
first audit event           = civic.authorization.allowed
audit events                = 3
receipts                    = 1
side_effects                = false
```

The authorization decision was persisted separately from the audit events and was returned through the read-only workflow evidence endpoint.

The schema change was additive and initialized successfully against the existing persistent SQLite database.

Result: **PASS**

## Service-selection evidence acceptance

On the persistent CT105 state store, a registered `publication.publish` request produced the ordered audit sequence:

```text
civic.authorization.allowed
civic.operation.accepted
civic.service.selected
civic.operation.not-implemented
```

The `civic.service.selected` event preserved:

```text
service_capability = publication.publish
implementation     = stub
side_effects       = false
```

The workflow retained one authorization decision, four audit events, one receipt, and `side_effects=false`.

Result: **PASS**

## Interface-equivalence acceptance

The Phase 1 development acceptance harness submitted the same bounded `publication.publish` operation using the interface identities:

```text
usermin
hubzilla
kane-fabric
```

Observed semantic result for all three:

```text
operation                  = publication.publish
status                     = not-implemented
implementation             = stub
service_capability         = publication.publish
authorization_decision     = allow
authorization_policy       = stub-policy
audit event sequence       = identical
receipt_outcome            = not-implemented
receipt_side_effects       = false
side_effects               = false
```

Request IDs, workflow IDs, receipt IDs, caller subjects, timestamps, and recorded interface identity remained request-specific as intended.

This gate proves contract-level interface equivalence only. It does not claim that production Usermin, Hubzilla, or Kane Fabric adapters have been implemented.

Result: **PASS**

## Workflow-transition acceptance

The persistent CT105 state store was exercised directly against the bounded transition graph.

Observed:

```text
initial state                         = validated
validated -> completed               = rejected
state after rejected transition      = validated
validated -> authorized              = accepted
authorized -> accepted               = accepted
accepted -> not-implemented          = accepted
final state                           = not-implemented
side_effects                          = false
```

The rejected transition did not mutate stored workflow state.

Result: **PASS**

## Acceptance conclusion

The Phase 1 runtime has now proven:

- schema validation;
- bounded operation registry;
- fail-closed unknown operation handling;
- schema-level rejection of prohibited generic capabilities;
- workflow ID issuance;
- explicit authorization-decision persistence;
- authorization audit evidence;
- explicit service-capability selection evidence;
- interface-independent Civic operation semantics across Usermin, Hubzilla, and Kane Fabric development identities;
- receipt issuance;
- local SQLite state;
- bounded workflow-transition validation with fail-closed rejection;
- threaded request safety;
- loopback HTTP operation;
- no production backend invocation;
- `side_effects=false`.

No production service adapter is enabled.

## Phase 1 closure

**Phase 1 is COMPLETE.**

The contract-bearing CT105 stub runtime now satisfies the Phase 1 architecture and acceptance requirements without enabling a production backend adapter or external service-network listener.

The next roadmap phase is Phase 2: service and trust node architecture. Phase 2 begins with architecture/inventory work, not broad backend integration.
