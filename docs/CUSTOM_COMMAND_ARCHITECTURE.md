# Custom Command Architecture

## Status

Initial contract baseline for the Civic Infrastructure Usermin Custom Command surface.

This document freezes the command registry model and the first participant utility inventory. The repository now contains the first generic local command stub for `water-ants` / Publish File. It does not change the production Usermin mapping, enable a new Orchestrator operation, or enable any new external side effect.

The first command to advance from the declared inventory into a callable stub is:

```text
water-ants
display name: Publish File
```

## Purpose

Usermin Custom Commands are a small participant-facing control surface over bounded Civic capabilities.

They are not:

- a general shell;
- a remote administration framework;
- an alternate Orchestrator API;
- an application server;
- a backend-routing interface;
- a replacement for Usermin file management, Hubzilla, mail, IPFS, or an Attestation Device.

The durable relationship is:

```text
Participant
    |
    v
Usermin Custom Command
    |
    v
participant helper
    |
    | authenticated local IPC
    v
Civic participant broker
    |
    | kernel-derived participant identity
    v
bounded command registry
    |
    | fixed command -> fixed semantic binding
    v
Civic Orchestrator or other explicitly admitted Civic interface
    |
    v
bounded service/resource
```

The participant chooses a command and supplies only that command's bounded inputs. The participant does not choose caller identity, backend operation, service, host, container, network route, credential, or arbitrary execution primitive.

## Command identity

Custom Commands use opaque non-serialized codenames.

The v1 syntax is:

```text
^[a-z]{1,5}-[a-z]{1,5}$
```

Therefore a command identifier consists of:

- one lowercase alphabetic token of 1 through 5 characters;
- one hyphen;
- a second lowercase alphabetic token of 1 through 5 characters.

Examples:

```text
water-ants
navy-roots
next-penny
```

Every codename in one registry version must be unique. Registry validation must reject duplicate codenames even when the duplicate command objects differ in other fields.

The codename:

- is the canonical command identifier;
- does not encode sequence or priority;
- does not encode authority;
- does not encode implementation technology;
- does not encode deployment location;
- does not encode lifecycle state;
- is never reassigned to another semantic command after publication.

A serial number or display index may be added later for documentation or presentation. It does not replace the codename and must not become protocol identity.

## Registry lifecycle

The command lifecycle is independent of command identity.

### declared

The command name and intended semantic boundary are reserved in the registry.

It is not callable.

### stub

The adapter/broker can recognize and validate the command contract, but the command performs no external Civic side effect.

A stub may return deterministic validation/evidence describing what would be requested.

### validation

The real bounded route may be exercised through the trusted adapter and Orchestrator path, while the relevant external side effect remains disabled.

### available

The bounded production operation is enabled under its accepted authority, resource, budget, workflow, and safety gates.

### disabled

The command remains a known contract but is deliberately unavailable by policy or deployment configuration.

### retired

The command is no longer accepted for new invocation.

Its codename remains permanently reserved so historical evidence cannot acquire a different meaning.

No lifecycle transition is implied by a registry edit alone. Deployment acceptance remains explicit.

## Binding rule

A Custom Command is not an Orchestrator operation.

A command may eventually map to one or more bounded Civic operations, but the mapping is trusted registry state and is never participant-selected.

A v1 binding has one of two states:

```text
bound
pending
```

`bound` means an accepted semantic operation already exists and the registry names it exactly.

`pending` means the participant utility is intentionally inventoried before its backend semantic operation has been frozen. A pending command is not callable. The registry must not invent a provisional Orchestrator operation merely to make the command look complete.

The first binding is:

```text
water-ants
    -> publication.publish
```

All other initial commands remain pending until their own semantic contracts are accepted.

## Identity and authority

Participant identity does not come from command input.

For the Usermin reference path:

```text
authenticated Usermin session
    -> Unix process UID/GID
    -> AF_UNIX peer
    -> SO_PEERCRED
    -> stable Civic participant mapping
```

The command payload must never contain editable values that can widen:

- participant identity;
- caller subject;
- authentication provenance;
- client identity;
- authority class;
- operation binding;
- service destination.

A future owner-operator or authority-facing command catalog may reuse this architecture with a different accepted authority profile. It must not silently widen the participant catalog.

## Inputs

Each registry entry declares an input profile.

Initial input modes are:

- `none`;
- `upload-bytes`;
- `select-known-object`;
- `typed-fields`;
- `mixed`.

An input mode describes the shape of participant input, not how the backend is implemented.

For byte-bearing commands, the participant process opens and reads participant-accessible bytes under the participant's own Unix credentials. A privileged broker must not open an arbitrary participant-supplied pathname.

The command protocol must not carry arbitrary filesystem paths for privileged resolution.

## Civic objects, resources, and evidence

A command descriptor inventories:

- accepted or referenced Civic object classes;
- object classes it may create;
- resource classes it may require;
- intended effect scope;
- expected evidence classes.

These are architectural inventory fields.

They do not grant authority by themselves.

Possession of an object never automatically grants the authority associated with that object's type.

Examples:

```text
possession of firmware bytes
    != authorized firmware release

possession of a public key
    != authorized Civic signer

possession of an attestation record
    != accepted Civic history

knowledge of a CID
    != participant authority over that publication
```

## Initial participant utility inventory

The initial inventory is intentionally broader than the first implementation so the adapter architecture is not designed around one publication command.

| Codename | Display name | Family | Initial binding |
|---|---|---|---|
| `water-ants` | Publish File | publication | `publication.publish` |
| `navy-roots` | My Publications | publication | pending |
| `next-penny` | Bind Logical File Name | logical-file-namespace | pending |
| `amber-crow` | Browse Logical File Namespace | logical-file-namespace | pending |
| `quiet-moss` | Rebind Logical File Name | logical-file-namespace | pending |
| `stone-wren` | Unbind Logical File Name | logical-file-namespace | pending |
| `coral-fern` | Request Pin | publication-retention | pending |
| `ivory-moth` | Request Unpin | publication-retention | pending |
| `river-owls` | Inspect Pin State | publication-retention | pending |
| `cedar-lark` | My Attestation Timeline | attestation | pending |
| `plain-fox` | Register Attestation Record | attestation | pending |
| `flint-deer` | Verify Historical Resource | attestation | pending |
| `maple-wasp` | My Attestation Device | edge-continuity | pending |
| `cloud-reed` | Synchronize Attestation State | edge-continuity | pending |
| `birch-kite` | Continuity Check | edge-continuity | pending |
| `green-lamb` | Resolve Historical Resource | edge-continuity | pending |
| `silk-heron` | Register Witness Image Evidence | witness | pending |
| `crown-ruby` | Inspect Nomadic Continuity | witness | pending |
| `olive-mint` | Publish Public Verification Material | verification-material | pending |
| `dawn-cedar` | Inspect Public-Key and Signature History | verification-material | pending |
| `pearl-moss` | Place Public Verification Material on Edge | verification-material | pending |
| `metal-robin` | Request Authorized Signature | signing | pending |
| `lilac-shore` | Show Authorized Firmware | firmware | pending |
| `rust-moon` | Request Authorized Edge Update | firmware | pending |
| `north-bell` | Inspect Update and Rollback State | firmware | pending |
| `final-wave` | Pre-Departure Continuity Audit | departure-continuity | pending |

Registration does not imply that every utility must eventually be presented as a separate Usermin button. It reserves the participant-facing semantic surface and prevents later implementation from inventing incompatible shortcuts.

## Publish File first target

`water-ants` is the first command to advance from `declared` to `stub`.

Its participant-facing semantics remain:

```text
Choose file
Publish
```

It does not accept:

- a logical namespace path;
- title or descriptive label;
- retention or pin duration;
- version/supersession intent;
- destination edge;
- Kubo/IPFS parameters;
- Orchestrator operation name;
- service endpoint;
- participant identity.

The first stub implementation must exercise:

```text
real Usermin identity
    -> participant helper
    -> generic Custom Command framing
    -> AF_UNIX broker
    -> SO_PEERCRED participant derivation
    -> command registry lookup for water-ants
    -> fixed publication.publish binding
    -> authenticated Orchestrator transport
    -> validation/no-side-effect result
```

External IPFS/Kubo publication remains governed by the independent Phase 4 publication safety gates.

## Participant backplanes

The Custom Command layer coordinates bounded operations across distinct Civic Infrastructure backplanes without merging their authority.

### Usermin /home

Quota-bounded participant working storage.

Ordinary participant files of any type may exist there.

Publication eligibility is a separate boundary.

### Virtual Email Boxes

Separate email infrastructure on a different host/network plane.

Participants are encouraged to forward mail they want to retain to their own ordinary email account.

Custom Commands do not become another mailbox implementation.

### Witness / Hubzilla

Social, discussion, image, and witness context.

The Civic deployment permits visible image uploads rather than arbitrary PDF/archive/general-binary storage.

Hubzilla Nomadic Identity remains Hubzilla functionality rather than a Custom Command reimplementation.

### IPFS publication

Content-addressed publication for approved inspectable publication classes.

Usermin's ability to store a file does not make that file eligible for IPFS publication.

Compressed/archive containers are outside the intended publication class. Exact accepted PDF/text/image validation belongs to the publication contract and safety gates.

### Attestation Device

A participant-controlled continuity, attestation, resolution, and verification endpoint.

It is not bulk backup storage.

It retains enough authenticated state to locate, relate, and verify historical resources across surviving backplanes and owner-operator domains.

The device role is platform-neutral. ESP32-S3 is a reference implementation only.

Historical continuity must not require a continued Kane Portal login, a Kane hostname, or access to one Kane private network.

## Prohibited generic behaviors

The Custom Command framework must fail closed rather than expose a generic escape hatch.

Prohibited categories include:

- arbitrary shell execution;
- arbitrary SSH;
- arbitrary HTTP proxy or URL fetch;
- arbitrary SQL;
- direct Kubo/IPFS RPC;
- arbitrary service/container/network destination selection;
- participant-selected Orchestrator operation names;
- arbitrary signing;
- participant submission of private signing-key material;
- privileged opening of participant-supplied paths;
- cross-participant mutation;
- reimplementation of Hubzilla clone/nomadic identity;
- reimplementation of email storage;
- reimplementation of IPFS storage.

When a desired utility appears to require one of these mechanisms, implementation stops until a bounded semantic operation, authority model, resource model, and evidence contract are defined.

## Initial acceptance sequence

The first implementation sequence after this contract is accepted is:

```text
1. registry/schema validation
2. generic bounded Custom Command local frame
3. broker command-registry lookup
4. water-ants stub implementation
5. real Usermin Publish File mapping to water-ants
6. validation-only end-to-end acceptance
7. only then evaluate the independent Phase 4 side-effect gate
```

No other initial utility advances beyond `declared` merely because it exists in the registry.

### Repository stub checkpoint

`water-ants` is now the only initial command with lifecycle `stub`.

The generic local stub path is deliberately parallel to the accepted production publication helper. It introduces a versioned local frame carrying only:

```text
protocol_version
codename
arguments
bounded byte payload
```

The frame carries no username, participant ID, caller/client identity, Orchestrator operation name, route, credential, host, service, or container selection.

The broker derives the Unix peer identity through `SO_PEERCRED`, the trusted registry fixes `water-ants -> publication.publish`, and the stub returns deterministic artifact evidence with:

```text
remote_dispatch = false
side_effects = false
```

The existing production Usermin publication mapping remains unchanged until a later explicit deployment step.
