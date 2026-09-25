# RAG / Email and Ceremony Capabilities

Status: capability inventory extension

This document records capability-shaped requirements that emerged after Kane Fabric Civic Authority Reference v1 was completed and the future RAG/LLM Diagnostics layer was reconsidered as an operational actor in human-facing workflows.

It does not define deployment topology, mail-server configuration, model selection, licensing, blockchain representation, or production implementation.

The governing boundary remains:

```text
Kane Fabric authority
    !=
RAG / LLM advisory computation
```

The RAG/LLM may coordinate, explain, retrieve, compare, classify, and preserve diagnostics. It does not acquire Civic standing, governance weight, operator authority, Signing Node authority, or authority to accept an epoch.

## 1. RAG request opportunity

Represents one bounded opportunity for an authorized requester to submit one analytical request to the RAG service.

```text
holder:
    authorized requester or participant

purpose:
    submit one bounded RAG/Diagnostics request

subject:
    one request/case context

exercise:
    acceptance of one canonical request object

possible transport:
    RFC 822 email
    later replaceable clients

result:
    request becomes eligible for processing

authority effect:
    none
```

The transport is not the capability. For an email implementation, the exact message is a transport/evidence object; acceptance of the canonical request is the capability exercise.

## 2. RAG advisory execution

Represents one bounded computational opportunity to process one accepted request against one identified RAG corpus/context and produce one provenance-bearing advisory result.

```text
holder:
    authorized RAG execution service

purpose:
    process one accepted request

inputs:
    exact request identity
    exact corpus identity
    exact retrieval/configuration identity
    permitted source/evidence set

exercise:
    production of one retained advisory result

authority effect:
    none
```

A valid execution does not make the answer legally correct, factually true, or Civic authority. A re-run with a different corpus, model, or retrieval profile is a different execution and must remain distinguishable.

## 3. Civic Ceremony Clerk session

Represents one bounded coordination session in which a non-authoritative RAG/LLM Clerk assists humans and devices through one exact candidate Civic transition.

The Clerk may retrieve and explain governing sources, enumerate required steps, identify missing evidence, present the exact transition subject, track outstanding actions, explain deterministic verification failures, compare equivalent treatment, and retain a provenance-bearing Diagnostics transcript.

The Clerk may not vote, choose a participant governance decision, create standing, admit a participant, select an operator, authorize a Signing Node, alter thresholds, substitute evidence, waive a required proof, select accepted Civic authority state, or sign as a participant or Signing Node.

```text
subject:
    one exact candidate Civic transition

purpose:
    coordinate and explain the ceremony

bounded by:
    exact predecessor authority state
    exact candidate transition subject
    exact governing profile
    exact governance policy
    exact RAG corpus/advisory context

exercise:
    complete one Clerk coordination/advisory session

result:
    Diagnostics/advisory record

authority effect:
    none
```

The Clerk is deliberately not a Civic Participant. Its usefulness comes from occupying a procedural role that should not become a privileged human office.

## 4. Successor epoch-key enrollment opportunity

Represents one proposed successor participant's bounded opportunity to demonstrate possession of the private key corresponding to the public key proposed for that participant in one exact successor epoch.

```text
holder:
    one proposed successor participant

purpose:
    enroll one successor epoch credential

context:
    exact HOA root
    exact candidate successor epoch
    exact predecessor authority state
    exact candidate transition subject

quantity:
    one successor-key enrollment opportunity

exercise:
    valid proof of possession produced with
    the proposed successor private key

authority effect:
    does not itself admit participant
    does not itself approve transition
```

Successor-key enrollment is distinct from a governance decision. A participant may enroll a successor key and vote reject, may enroll a key without belonging to the governance electorate, or may belong to the predecessor electorate while not belonging to the proposed successor set.

A future canonical enrollment proof should bind at least participant identity, HOA root, successor epoch sequence, predecessor manifest identity, new participant key ID/public key, exact candidate transition subject identity, and a signature made by the NEW private key.

The proof establishes only that the holder of the proposed successor credential possesses the corresponding private key for this exact candidate transition. It does not establish standing, governance approval, admission, or accepted authority.

## 5. Relationship among the capabilities

```text
RAG request opportunity
        |
        v
RAG advisory execution
        |
        v
Ceremony Clerk session
        |
        +--> successor epoch-key enrollment opportunities
        |
        +--> governance decision opportunities
        |
        v
deterministic Civic verification
        |
        v
accepted or rejected authority transition
```

The RAG/LLM coordinates the process. It does not become the holder of participant governance or key-enrollment capabilities.

## 6. Email as replaceable human transport

Email is a strong initial transport because it naturally produces durable request/response artifacts and supports asynchronous operation.

```text
email address        != Civic identity
email authentication != Civic standing
mail server          != Civic authority
```

The capability layer must remain usable with another future client. A web application, local application, command-line client, or other interface may later produce the same canonical request/action objects.

## 7. Deployment independence

No capability in this document is defined by a physical machine. Public mail/DNS/DANE services, confidential SQL/vector/corpus services, LLM inference, and Civic Signing Node authority may be placed on separate systems without altering capability meaning.

An LLM runtime sharing physical infrastructure with a Civic Signing Node must remain logically unable to exercise Signing Node authority merely because it can communicate with the host.

## 8. Grant-oriented implementation handoff

The first operated implementation is expected to be documented and demonstrated according to this priority:

```text
1. Impress
2. Function
3. Inspire
4. Expand
```

These are presentation and adoption objectives for the implementation project, not capability semantics.

Security, reliability, recovery, provenance, access control, licensing compliance, and failure behavior remain engineering obligations and conformance concerns. They should be documented rigorously without being treated as promotional capability claims.

A future implementation repository should present each major subsystem in two layers:

```text
civic capability demonstrated
        +
technical mechanism implementing it
```

This repository records the former. The implementation project records the latter.

## 9. No implementation authorization

This document does not authorize mail-server changes, RAG deployment, LLM model selection, vector database selection, SQL schema design, Ceremony Clerk code, production key generation, production Signing Node activation, blockchain representation, IPFS publication, or creation of a new implementation repository.

Implementation should begin only after the capability semantics needed by the first bounded workflow are accepted.
