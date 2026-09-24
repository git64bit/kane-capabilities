# Kane Fabric Use-Case Inventory

Status: Milestone 0A — final Kane Fabric sweep

This document inventories capability-shaped requirements that emerged from the completed Kane Fabric Civic Authority Reference v1.

It does not add implementation, change the Capability Model, select a blockchain, or claim that every cryptographic object in Kane Fabric should become a capability.

## Source baseline

The sweep is anchored to:

```text
Kane Fabric Civic Authority Reference v1
accepted code head:
0234b8e09fc0ce092d6b4f47a579d4253a19b812
```

The principal Kane Fabric contracts considered were:

- `docs/KANE_FABRIC_CIVIC_AUTHORITY_REFERENCE_V1.md`
- `docs/CIVIC_GOVERNANCE_POLICY_PROOF_CONTRACT.md`
- `docs/CIVIC_ACCEPTED_OPERATOR_SELECTION_RECORD.md`
- `docs/CIVIC_ACCEPTED_PARTICIPANT_ISSUANCE_RECORD.md`
- the accepted participant-standing contract introduced at commit `0eb65e13bf43c6c16880fee983ad033762a881ca`
- `docs/CIVIC_PARTICIPATION_RENEWAL.md`
- `docs/CIVIC_OPERATOR_PEER_SCRUTINY.md`
- `docs/CIVIC_HISTORY_HEAD_SEMANTICS.md`
- `docs/CIVIC_EPOCH_MANIFEST_FORMAT.md`
- `docs/CIVIC_SIGNING_NODE_FUTURE_SERVICE_BOUNDARIES.md`
- `docs/CIVIC_SIGNING_NODE_CONFORMANCE_DEPLOYMENT_BOUNDARY.md`

## Admission rule

A Kane Fabric object or workflow is a capability candidate only when the completed architecture exposes a bounded right, opportunity, or responsibility whose exercise or non-exercise is meaningful.

The following are not sufficient by themselves:

- cryptographic signatures;
- content hashes;
- current standing;
- possession of a key;
- membership in an epoch;
- storage of evidence;
- inclusion in accepted history.

A capability must represent an exercisable bounded opportunity rather than merely authenticated state.

## Inventory classifications

This inventory uses three classifications:

- **MATCH** — Kane Fabric already exposes a sufficiently clear capability-shaped requirement.
- **HOLD** — the architecture suggests a possible capability, but Kane Fabric deliberately left material semantics undefined.
- **NOT A CAPABILITY** — the object is authority state, evidence, identity, provenance, or storage rather than an exercisable bounded opportunity.

No classification in this document authorizes implementation.

---

## MATCH 1 — Governance decision opportunity

### Kane Fabric source

The governance policy/proof contract defines an exact electorate for an exact transition subject and exact governance policy.

For one exact transition subject and policy:

```text
one electorate participant
    -> at most one non-null governance decision
```

The permitted non-null decisions are:

```text
approve
reject
abstain
```

Repeated signing cannot create additional decision weight.

The electorate and its weight are reconstructed from verified standing and the exact source-derived governance policy.

### Capability shape

This naturally exposes a capability of the form:

```text
holder:
    one verified electorate participant

purpose:
    contribute one governance decision
    to one exact transition subject
    under one exact governance policy

quantity:
    one decision opportunity

exercise:
    one valid non-null governance proof

terminal result:
    exercised after one valid decision
```

### Important boundary

**Decision quantity is not vote weight.**

Kane Fabric permits source-derived explicit weights. A participant with weight 25 does not therefore receive 25 independently exercisable or transferable capability units.

The capability represents one decision opportunity.

The exact governance policy supplies the weight applied to that decision.

This preserves:

```text
one participant decision
    !=
one unit of governance weight
```

### Unresolved capability detail

Kane Fabric v1 binds the decision to an exact transition subject and effective time, but it does not define a universal voting/open-close time window.

Therefore this use case reveals a possible future pressure on the Capability Model:

```text
validity may be bounded by an exact subject/event lifecycle
and not only by a wall-clock interval
```

Milestone 0A records this observation but does not modify the model.

---

## MATCH 2 — Bounded operator issuance/validation action

### Kane Fabric source

Kane Fabric defines the operator as a participant performing a bounded procedural role.

For the Kane SASE participation process, the operator may attest the narrow fact that a participant voluntarily initiated or renewed participation through the required SASE procedure and that a bounded participation interval resulted.

The peer-scrutiny architecture explicitly anticipates bounded future records for:

- SASE receipt/validation event;
- issuance action;
- operator provenance;
- correction or supersession.

### Capability shape

The operator role itself is **not** the capability.

A capability candidate arises when a particular bounded issuance/validation task exists:

```text
holder:
    current authorized operator

purpose:
    perform one identified validation/issuance act

subject:
    one participant + one renewal/admission event

exercise:
    produce the required attributable validation/issuance record

evidence:
    exact evidence identities required by the governing profile
```

This is useful because it distinguishes:

```text
being the operator
    from
being authorized to complete this bounded act
```

### Current limitation

Kane Fabric deliberately did not freeze a universal SASE workflow or universal issuance ceremony.

The use case is therefore a semantic match, but its exact capability serialization must wait for a real workflow that identifies the action boundary precisely.

---

## MATCH 3 — Contemporaneous witness attestation opportunity

### Kane Fabric source

Kane Fabric v1 already reserves an independent:

```text
witness
```

history stream.

The history-head contract freezes the append-only linkage semantics for that stream while deliberately leaving substantive witness-record schemas undefined.

Several Kane Fabric architecture documents also preserve a future participant-device Witness Attestation role in which the participant appliance authors the witnessed record and references the civic context under which it was operating.

### Capability shape

This is a strong match for a finite capability:

```text
holder:
    participant / witness principal

purpose:
    attest to one identified real-world event or opportunity

validity:
    contemporaneous event window

quantity:
    bounded attestation opportunity

exercise:
    produce one attributable witness record
    optionally bound to exact external evidence

expiration:
    the contemporaneous opportunity closes
```

A later historical statement may still be evidence.

It must not acquire the same status as a capability exercised during the contemporaneous opportunity.

### Current limitation

Kane Fabric intentionally did not freeze:

- witness-record schema;
- event-window semantics;
- physical-presence/challenge mechanisms;
- witness eligibility rules;
- duplicate/conflicting attestation rules.

Those details remain future work. The capability match itself is nevertheless clear.

---

## HOLD 1 — Participation renewal opportunity

Kane Fabric defines six-month bounded participation and requires a fresh SASE for renewal.

That produces strong temporal semantics:

```text
accepted SASE
    -> bounded active interval
    -> expiration without renewal
```

However, current standing is authority state, not automatically an exercisable capability.

Kane Fabric does not yet define enough about:

- earliest permitted renewal;
- duplicate SASE handling;
- overlapping renewal attempts;
- whether renewal is one opportunity per interval or simply a newly observed act;
- whether a rejected/invalid renewal consumes anything.

Therefore Milestone 0A does **not** promote SASE renewal itself to a capability.

A later concrete renewal workflow may do so.

---

## HOLD 2 — Peer confirmation/challenge

Kane Fabric peer scrubbing anticipates participant:

- confirmations;
- corroborations;
- challenges;
- contradiction reports.

Exact confirmation/challenge record formats remain future design work.

Nothing in v1 establishes a finite number of such observations or a one-time exercise rule.

Therefore these are provenance-bearing observations, not yet finite capabilities.

If a future procedure creates a bounded response opportunity, that procedure may produce a capability use case.

---

## HOLD 3 — IPFS pinning / retention commitment

Kane Fabric explicitly identifies participant-edge pinning of user-owned CIDs as a future wish-list capability.

The mechanism is deliberately undefined and IPFS is not part of baseline Civic authority.

A future bounded request such as:

```text
retain CID X
for retention class Y
under commitment Z
```

could become capability-shaped.

Milestone 0A does not admit it because Kane Fabric v1 does not define:

- pin-request semantics;
- retention duration;
- acknowledgement;
- replication count;
- failure behavior;
- release/expiration behavior.

CID identity alone is not a capability.

---

## NOT A CAPABILITY — participant standing

Standing answers whether a participant qualifies under an exact governing profile at an evaluation time.

Standing may authorize or constrain later capabilities.

It is not itself a one-time exercisable opportunity.

```text
standing
    -> eligibility/context

capability
    -> bounded exercise derived from eligibility/context
```

---

## NOT A CAPABILITY — participant issuance

An accepted participant-issuance record binds:

- participant identity;
- participant epoch key;
- standing record;
- operator provenance;
- accepted history.

It is authenticated authority state.

It is not the exercise of a finite resource.

---

## NOT A CAPABILITY — Epoch Manifest / authority epoch

The Epoch Manifest is the current authenticated authority snapshot.

It determines context from which capabilities may later be derived.

The manifest itself is not a token, balance, entitlement, or exercise opportunity.

---

## NOT A CAPABILITY — participant or Signing Node keys

A key proves or enables cryptographic attribution under the applicable authority context.

Possession of a key does not independently create:

- standing;
- governance weight;
- operator authority;
- a vote;
- an attestation opportunity;
- current Civic authority.

Keys may control capability exercise, but keys are not capabilities.

---

## NOT A CAPABILITY — Signing Node authority

The current Signing Node authorization is an authority relationship in the accepted epoch.

The node deliberately has no generic arbitrary-current-byte signing authority.

A future bounded operation invoked through the node may be capability-controlled.

The node's current authority binding itself should remain Kane Fabric authority state.

---

## NOT A CAPABILITY — evidence hashes, CIDs, and object-store entries

SHA-256 identities and future CIDs identify exact content.

They do not create a right to act.

Evidence may be attached to a capability exercise, but evidence identity is not the capability.

---

## NOT A CAPABILITY — accepted/witness/diagnostics/knowledge history records

A history record is an immutable attributable record.

A capability exercise may produce a history record.

The record is the consequence/evidence of exercise, not the capability itself.

---

## NOT A CAPABILITY — participant replicas and recovery

A participant-held replica can preserve enough authenticated state for continuity/recovery.

Supplying a replica does not grant governance authority, operator status, or Signing Node authority.

Recovery therefore remains an authority-state continuity mechanism rather than a finite capability.

---

## NOT A CAPABILITY — accepted-state selector

The local selector chooses which completely verified authority state is currently selected by a Signing Node implementation.

It is operational metadata governed by Kane Fabric transaction semantics.

It is not civic authority and should not be tokenized.

---

## Cross-cutting observations

### 1. Kane Fabric remains the source of capability meaning

Any future capability must be derived from verified Kane Fabric state and exact source-bound policy.

A blockchain must not decide:

- who has standing;
- who belongs to an electorate;
- what vote weight applies;
- who is operator;
- whether a Signing Node is current;
- what governing source controls.

At most, an external ledger can make capability issuance/exercise/expiration independently inspectable.

### 2. Capability exercise should bind exact context

The three admitted matches all naturally need context stronger than a human label.

Likely context includes some subset of:

```text
hoa_root_id
epoch_sequence
holder participant identity/key
purpose
exact subject identity
exact policy identity
validity/event context
evidence identity
exercise record identity
```

This is an inventory observation only. It is not a Milestone 0 schema change.

### 3. Expiration must preserve history

Kane Fabric consistently preserves prior state after currentness ends.

The capability system should preserve the same distinction:

```text
expired
    != deleted

exercised
    != erased

superseded context
    != nonexistent history
```

### 4. External ledger state must remain subordinate

A public chain may prove that a capability representation was issued or exercised on that chain.

It must not convert an otherwise invalid Kane Fabric act into valid Civic authority.

Conceptually:

```text
verified Kane Fabric authority/context
    -> capability authorization
    -> optional external-ledger representation
```

not:

```text
external token exists
    -> therefore Civic authority exists
```

### 5. No chain selection follows from this inventory

Nothing in this sweep selects:

- Pi;
- Stellar;
- another public chain;
- a Kane-local ledger;
- a smart-contract platform.

The use cases are intentionally chain-independent.

---

## Milestone 0A result

The completed Kane Fabric did produce capability-shaped requirements without being designed around a token system.

The strongest current inventory is:

```text
1. governance decision opportunity
2. bounded operator issuance/validation action
3. contemporaneous witness attestation opportunity
```

The following remain on hold:

```text
participation renewal opportunity
peer confirmation/challenge
IPFS pinning/retention commitment
```

Everything else reviewed in this sweep remains authority state, identity, provenance, evidence, storage, or recovery rather than a capability.

No implementation work follows automatically from this inventory.

The next development step should occur only when one admitted use case requires a concrete capability representation that Kane Fabric itself does not already provide adequately.
