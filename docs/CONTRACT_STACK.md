# Contract and Protocol Stack

## Decision

Kane Capabilities does **not** define a new wire protocol.

JSON may be used as a representation, but JSON alone is not a protocol.

The initial stack reuses mature open standards:

```text
Civic operation semantics     project-defined
Workflow semantics            project-defined, deliberately small
Events                        CloudEvents 1.0
API description               OpenAPI 3.1
Payload contracts             JSON Schema 2020-12
Representation                JSON by default
Transport                     HTTP/HTTPS
Trust                         deployment-specific authenticated TLS/signatures
```

## Why this split exists

The project should invent only the semantics that do not already exist elsewhere: what a Civic operation means, who may request it, which state transition it represents, and what evidence/result it produces.

It should not invent replacements for HTTP, schema languages, API description, or event envelopes.

## Synchronous calls

Operations that naturally return promptly use HTTP request/response semantics described by OpenAPI.

The API must expose bounded operation resources, not generic remote execution.

## Asynchronous events

Facts such as the following are events rather than commands:

- workflow accepted;
- workflow rejected;
- candidate ready for review;
- publication completed;
- publication failed;
- firmware signature issued;
- edge update acknowledged;
- receipt issued.

These use CloudEvents envelopes. Civic-specific content belongs in the event data contract.

## Schemas

Every durable message type must have:

- a stable schema identifier;
- explicit version;
- validation rules;
- compatibility policy;
- examples used by tests.

Initial schema families:

- request;
- result;
- failure;
- caller identity and authentication provenance;
- extensible client identity;
- authorization;
- operation;
- workflow;
- audit;
- receipt;
- service capability;
- Custom Command registry for the bounded participant interaction-adapter surface.

The Custom Command registry is an adapter contract rather than an Orchestrator operation namespace. It uses opaque two-token codenames and binds commands to fixed semantic operations only after those operations exist. A declared command with a pending binding is not callable.

Authority: `CUSTOM_COMMAND_ARCHITECTURE.md`; `../contracts/custom-command-registry-v1.yaml`.

## Workflow definitions

Workflow definitions are declarative and must refer to named Civic capabilities rather than shell commands.

Initial vocabulary should remain intentionally small. Candidate primitives include:

- `authorize`
- `call`
- `verify`
- `transition`
- `wait`
- `approve`
- `reject`
- `emit`
- `record`

A workflow definition language is an internal orchestration contract, not a new network protocol.

The Phase 1H runtime validates the operation registry and stub workflow definition against JSON Schema at startup. The stub workflow's authorization policy and accepted namespaces are runtime inputs; they are not decorative documentation.

All JSON Schema cross-references use absolute Civic schema URNs. Runtime validation uses the modern `referencing` registry used by `jsonschema`, not the deprecated `RefResolver` compatibility API. Date/time formats are checked with a JSON Schema format checker.

## Scripting and mature engines

General-purpose scripting is permitted behind service adapters when required by an implementation, but is not exposed as a Civic operation.

The project may later evaluate workflow/orchestration engines. Selection must not force external clients to understand the chosen engine.

The initial implementation deliberately avoids making Rundeck, Temporal, Kubernetes, a message broker, or another orchestration product a platform dependency before the workflow requirements prove the need.


## Caller and client identity

The request contract separates the authenticated civic subject from the software client carrying the request.

```text
caller.subject
caller.authority
caller.authenticated_by

client.id
client.kind
```

`client.id` is intentionally not a fixed enum of known applications. New software that legitimately belongs to the same orchestrator domain can identify itself without revising the v1 schema merely to add another program name.

`caller.authenticated_by` is an assertion carried by the trusted adapter boundary. Phase 1 validates that the field is present and records it as provenance; Phase 1 does **not** independently authenticate the subject or cryptographically bind a client to its declared `client.id`.

The current HTTP ingress adds the repository-side authenticated-adapter primitive that Phase 1 intentionally lacked. An adapter bearer credential resolves server-side to a fixed `client.id`, fixed `client.kind`, fixed `caller.authenticated_by`, fixed caller authority, and allowed subject namespace. Requests that contradict that transport binding are rejected before workflow creation. This repository implementation does not by itself establish production acceptance: the real adapter path, protected credential provisioning, and deployment route must still be installed and accepted.

Client extensibility does not imply admission to CT105. Admission remains governed by `ORCHESTRATOR_SCOPE.md`.

## Replay and idempotency

`request_id` identifies a logical request. An optional `idempotency_key` identifies a retry family.

For the Phase 1H stub runtime:

- an exact semantic replay returns the original workflow/receipt result;
- reusing an idempotency key for different semantics returns `409 conflict`;
- reusing a request ID for different semantics returns `409 conflict`;
- replay does not create another workflow, audit trail, or receipt.

The semantic fingerprint covers operation, caller, client, and input. Transport time and retry request ID do not change the requested civic action.

## Effect scope

Operation descriptors classify intended effect scope as:

- `none` — read/compute behavior with no orchestrator or external state mutation;
- `orchestrator-state` — mutation limited to orchestrator-owned workflow/incident/release state;
- `external-bounded` — a bounded request that, when implemented, may change state in another authority/service.

Phase 1H remains stub-only, so actual side effects remain false regardless of intended future effect scope.


## Schema catalog

`schemas/catalog-v1.json` publishes the mapping from each absolute Civic schema URN to its repository-relative JSON Schema file.

An independent validator may load the catalog, register each listed schema by its `$id`, and then validate the public contracts without relying on the Python runtime's private loading behavior.

The catalog is transport metadata only; it does not add Civic semantics.


## Rejection diagnostics

Rejected requests, replay attempts, conflicts, and HTTP-level parsing failures leave a minimal local diagnostic record in CT105.

These records are operational diagnostics, not Civic workflow receipts and not proof of abuse. They exist so failures do not disappear merely because no normal workflow was accepted.
