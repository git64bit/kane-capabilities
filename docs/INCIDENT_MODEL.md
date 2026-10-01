# Operational Incident and Abuse-Signal Model

## Purpose

Civic Infrastructure needs a bounded way to notice, preserve, expose, and resolve operational failures without turning raw logs or isolated errors into automatic accusations or enforcement.

The model is inspired by the useful property of systems such as Web2Pi that convert important core failures into stateful tickets, while preserving Civic Infrastructure's contract-first and evidence-first boundaries.

## Four separate concepts

### Audit evidence

Audit answers:

> What happened?

Audit records are evidence of observed or orchestrated events. They are not mutable ticket state and do not themselves imply fault, abuse, or an enforcement decision.

### Signal

A signal answers:

> Did something occur that may deserve attention?

Examples may later include:

- repeated failed privilege escalation attempts reported by the operating system;
- mail or Hubzilla delivery failures;
- repeated malformed or unauthorized Civic operation requests;
- backend health failures;
- publication verification failures;
- signing or edge-management faults.

A signal is not automatically an incident and is not proof of abuse.

### Incident

An incident answers:

> Has an operator or policy accepted this condition for investigation or resolution?

Incidents are mutable operational workflow objects. Initial states are:

- `open`
- `acknowledged`
- `resolved`

The initial bounded operations are:

- `incident.report`
- `incident.get`
- `incident.acknowledge`
- `incident.resolve`

During Phase 1 all remain stubs and produce no production side effects.

### Policy response

Policy response answers:

> What, if anything, should the system do about the condition?

Examples could eventually include retry, throttling, quarantine, escalation, notification, or access restriction.

Policy response is deliberately outside the initial incident contract. Detection and evidence must remain separable from enforcement.

## Classification dimensions

The v1 incident contract keeps independent dimensions rather than collapsing meaning into one severity value.

### Domain

Initial values:

- `core`
- `transport`
- `publication`
- `repository`
- `geography`
- `rag`
- `inference`
- `signing`
- `edge`
- `participant`
- `security`

### Severity

Initial values:

- `info`
- `warning`
- `degraded`
- `failure`
- `critical`

### Visibility

Initial values:

- `local`
- `operator`
- `participant`
- `public`

### Source

The source identifies the reporting component or adapter, for example an orchestrator, systemd/sudo adapter, Hubzilla adapter, SMTP transport, Gitea, publication service, or another bounded service.

The source field identifies origin; it does not determine severity or guilt.

## Abuse-prevention boundary

The incident facility may later help operators recognize patterns associated with abuse, but it must not encode the conclusion that a participant is abusive merely because a signal exists.

For example:

```text
failed sudo attempts
  -> signal(s)
  -> optional aggregation/policy evaluation
  -> incident when investigation is warranted
  -> independently authorized response, if any
```

The same separation applies to delivery failures, invalid requests, authentication failures, or repeated service errors.

## Phase 1 boundary

Phase 1 introduces only:

- the `incident.*` operation namespace;
- the `incident-v1` record schema;
- four registry stubs;
- roadmap and demonstrator integration.

Phase 1 does not introduce:

- log ingestion;
- automatic incident creation;
- automatic notifications;
- rate limiting;
- banning/blocking;
- privilege changes;
- participant sanctions;
- a help-desk UI;
- Web2Pi coupling.

## Future demonstrator use

A later controlled-failure demonstration may show:

```text
Civic operation
  -> failure/audit evidence
  -> signal
  -> incident opened
  -> operator acknowledgement
  -> corrective action
  -> incident resolution
```

The demonstrator must use the same incident contracts as production and must not receive a demo-only enforcement path.
