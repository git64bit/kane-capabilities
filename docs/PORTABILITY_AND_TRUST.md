# Portability and Non-Monetary Trust

## Purpose

Kane County is the reference deployment. Civic Infrastructure is the portable system.

A conforming implementation in another jurisdiction, such as Orange County, California, must be able to implement the public contracts without inheriting Kane County hostnames, private keys, accounts, filesystem paths, operator state, private databases, or deployment-specific service identities.

## Portability principle

> No Civic Infrastructure contract may require Kane County-specific infrastructure, private hostnames, accounts, keys, filesystem paths, or operator state.

Kane-specific source adapters, jurisdiction identifiers, data-source mappings, and operator policy are deployment inputs. They are not universal protocol requirements.

A second operator must be able to replace:

- jurisdiction identifiers and geographic sources;
- operator accounts and trust roots;
- hostnames and service locations;
- signing keys;
- participant organizations;
- source adapters;
- deployment topology where the public contracts permit it.

while preserving:

- orchestrator operation semantics;
- workflow semantics;
- API and event contracts;
- publication and receipt formats;
- browser application architecture;
- capability namespaces;
- conformance tests;
- edge and signing boundaries.

## Independent-operator test

Every durable architectural decision should survive this question:

> Can an independent operator in another county understand, deploy, and operate this from the public contracts without access to Kane County's private infrastructure?

If not, an implementation detail has probably escaped into a public contract.

## Conventional-infrastructure preference

When two implementations satisfy the same Civic requirement, prefer the one that is:

- more widely understood;
- easier to inspect;
- easier to reproduce;
- easier to replace;
- supported by mature open standards;
- less dependent on specialized operators or proprietary ecosystems.

This does not prohibit novel Civic semantics. It limits novelty to the portion of the problem that actually requires it.

## Cryptography boundary

Cryptography is evidence and authorization infrastructure.

Appropriate uses include:

- TLS;
- hashes and content identity;
- digital signatures;
- certificate authorities;
- signed manifests;
- firmware signing;
- receipts and attestations;
- verifiable authorization records.

Cryptography must answer questions such as:

- Who authorized this?
- Were these exact bytes approved?
- Has this artifact changed?
- Which authority signed it?
- Which publication generation is this?
- Can the result be independently verified?

## Non-monetary trust principle

> Cryptographic identities, capabilities, receipts, attestations, signatures, and content identities are evidence and authorization mechanisms. They confer no monetary value, ownership interest, transferable economic claim, or governance weight merely by existing.

Civic Infrastructure does not introduce a utility token, cryptocurrency, mining reward, exchange value, or market mechanism as a prerequisite for participation.

If a future deployment requires an economic instrument for an unrelated purpose, that system must remain explicitly separate from the Civic trust model.

## Blockchain admission rule

A blockchain or distributed-ledger component may not enter the required architecture unless a concrete Civic requirement cannot be satisfied adequately by simpler mechanisms such as:

- signed records;
- append-only logs;
- Git history;
- content-addressed storage;
- WORM storage;
- independent witnesses;
- replication;
- public verification.

The burden of proof is on introducing the blockchain, not on retaining conventional infrastructure.

## Appliance direction

The long-term architecture should remain compatible with a network-bootstrapped Civic Infrastructure appliance.

Conceptually:

```text
boot
  -> establish network
  -> discover operator/jurisdiction configuration
  -> obtain public contracts
  -> verify trust roots
  -> configure local services
  -> obtain jurisdiction adapters
  -> verify conformance
  -> join the deployment
```

The appliance goal reinforces the preference for standard Linux services, standard network protocols, explicit schemas, standard PKI/signatures, replaceable service adapters, and reproducible configuration.

The appliance must not depend on Kane County's physical hosts or private implementation state.
