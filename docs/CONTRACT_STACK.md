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
- identity;
- authorization;
- operation;
- workflow;
- audit;
- receipt;
- service capability.

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

## Scripting and mature engines

General-purpose scripting is permitted behind service adapters when required by an implementation, but is not exposed as a Civic operation.

The project may later evaluate workflow/orchestration engines. Selection must not force external clients to understand the chosen engine.

The initial implementation deliberately avoids making Rundeck, Temporal, Kubernetes, a message broker, or another orchestration product a platform dependency before the workflow requirements prove the need.
