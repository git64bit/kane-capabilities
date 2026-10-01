# CT105 Phase 2 Publication Acceptance

## Status

**ACCEPTED** on 2026-10-01.

The Civic Orchestrator on `srv-b / CT105 / civic-orchestrator` has entered Phase 2 with exactly one available bounded external operation:

```text
publication.publish
```

The publication backend remains intentionally validation-only. Kubo publication and swarm participation are not enabled.

## Accepted repository state

Observed deployed commit:

```text
1a78d2c41d798ad867c0fa7506202e34a811c442
```

The production regression suite passed:

```text
Ran 66 tests
OK
```

The operation registry advertises:

```text
publication.publish       available
all other operations      stub
```

## Service state

Observed:

```text
civic-orchestrator.service
Description: Civic Orchestrator Phase 2
Loaded:      loaded and enabled
Active:      active (running)
Runtime:     /opt/civic-orchestrator/venv/bin/python
State:       /var/lib/civic-orchestrator/state/orchestrator.sqlite3
```

Deployment-specific publication client configuration:

```text
--publication-base-url http://10.110.0.21:8046
```

## Listener boundary

Observed:

```text
127.0.0.1:8045
```

The Orchestrator remains loopback-only. No participant-facing Orchestrator ingress is accepted by this gate.

## Health

Observed:

```json
{"phase":"2","side_effects":true,"status":"ok"}
```

Here `side_effects=true` means the active registry now contains an available operation whose effect scope permits external effects. It does not assert that any specific workflow produced an external side effect.

## Real validation-only workflow

A real `publication.publish` operation was submitted through the running Phase 2 Orchestrator.

Observed result:

```text
status          failed
failure_class   service-unavailable
retryable       true
side_effects    false
```

Backend message:

```text
publication bytes validated; Kubo publication is not enabled yet
```

Accepted workflow:

```text
wf:ef51aada-bebc-41c8-b3f3-03adf4597c39
```

The persisted evidence showed:

```text
authorization policy      publication-policy-v1
workflow state            failed
workflow side_effects     false
receipt outcome           failed
receipt side_effects      false
final audit event         civic.operation.failed
```

This proves that the Orchestrator accepted, authorized, routed, and recorded the bounded external workflow while preserving the backend's validation-only failure as a no-side-effect outcome.

## Publication backend state

Observed health:

```json
{"kubo_enabled":false,"phase":"validation-only","service":"civic-publication","status":"ok","swarm_enabled":false}
```

Result: **PASS**

No CID was produced. No pin was created. No Kubo publication occurred.

## Trust boundary not yet accepted

The validation request used a synthetic local operator assertion:

```text
subject          operator:phase2-validation
authenticated_by local-operator-validation
client           phase2-validation-client
```

This is test provenance only. It is not participant authentication.

The raw HTTP request envelope still contains adapter-supplied caller and client assertions. Participant-facing ingress must not expose that boundary until a trusted adapter derives caller identity from the authenticated interaction context and fixes the client identity.

## Acceptance conclusion

Phase 2 now proves:

- one real bounded external operation is enabled;
- the production Orchestrator reaches the publication service over the intended private route;
- the publication service contract is exercised end to end;
- workflow, authorization, audit, receipt, and failure evidence persist correctly;
- validation-only backend failure remains `side_effects=false`;
- the Orchestrator listener remains loopback-only;
- Kubo remains disabled;
- participant-facing ingress remains intentionally absent.

## Next gate

Establish a trusted interaction-adapter boundary before exposing any participant route.

For Usermin, the adapter must derive the participant identity from the authenticated Unix/Usermin execution context, use a fixed controlled client identity, and prevent participants from supplying arbitrary caller, client, or authentication-provenance assertions.

A raw TCP relay from the WireGuard mesh to the Orchestrator API is not sufficient for this gate.
