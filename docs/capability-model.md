# Capability Model

Status: Milestone 0 draft

This document defines the minimum abstract capability model for Kane Fabric. It intentionally avoids blockchain-specific, storage-specific, and application-specific behavior.

## 1. Definition

A Kane Capability is a finite, cryptographically controlled representation of a bounded right, opportunity, or responsibility.

A capability is not inherently monetary and does not imply exchange value.

## 2. Minimum fields

A capability contains, at minimum:

- **issuer** — authority that creates or authorizes the capability.
- **holder** — participant or cryptographic principal permitted to exercise it.
- **purpose** — bounded meaning of the capability.
- **validity interval** — earliest and latest time at which exercise is valid.
- **quantity** — finite amount authorized under the capability.
- **state** — current lifecycle state.
- **evidence reference** — optional reference binding exercise to external evidence.
- **signatures** — cryptographic signatures required by the capability rules.

No additional fields are part of Milestone 0 unless required to make these semantics unambiguous.

## 3. Lifecycle

The minimum lifecycle is:

```text
AUTHORIZED
    |
  ISSUED
    |
  ACTIVE
   /   \
EXERCISED EXPIRED
```

### AUTHORIZED

The issuer has approved creation of a finite quantity of capability units.

### ISSUED

An authorized capability unit has been assigned to a holder.

### ACTIVE

The capability is within its validity interval and may be exercised according to its purpose.

### EXERCISED

The holder validly used the capability. An exercised capability cannot be exercised again.

### EXPIRED

The validity interval ended before exercise. An expired capability cannot later become exercised.

## 4. Conservation invariant

For a bounded authorization, the system must be able to account for the entire authorized quantity.

```text
AUTHORIZED = UNISSUED + ACTIVE + EXERCISED + EXPIRED
```

No valid state transition may create capability quantity beyond the authorized amount.

No valid state transition may cause an authorized unit to disappear from accounting.

## 5. Evidence binding

A capability may reference external evidence.

The evidence reference binds the exercise to an exact external object or record, but the external evidence system does not determine the capability state.

Milestone 0 does not define the representation of the evidence reference.

## 6. Cryptographic control

Capability state transitions must ultimately be attributable to the required cryptographic principals.

Milestone 0 records the requirement for signatures but does not yet define:

- signature algorithms;
- key formats;
- canonical serialization;
- multisignature rules;
- signing-node behavior.

## 7. Deferred questions

The following are deliberately outside Milestone 0:

- transferability;
- revocation;
- invalidation;
- return or surrender;
- delegation;
- partial exercise;
- replacement;
- recovery;
- privacy;
- public-chain representation;
- Pi or Stellar adapters;
- IPFS publishing or pinning;
- Annales integration;
- application-specific semantics such as voting or witness attestation.

These questions should be introduced only when the minimum model requires them.
