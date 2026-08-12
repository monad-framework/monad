# Monad Artifact System

**Status:** Draft catalog baseline  
**Owner:** Engineering Owner

## Purpose

`artifact-system/` is the comprehensive catalog and design space for artifact types that a mature Monad engineering system may create, govern, compile, validate, project, or consume.

It is **not** a declaration that every file is currently authoritative, required for MVP, or accepted. The directory intentionally contains forward-looking artifact contracts so the project can reason about the complete engineering lifecycle without prematurely activating every mechanism.

## Canonicality

Human-readable source is canonical. Machine representations under `machine/` are deterministic projections and never outrank their canonical source.

Within this directory:

- **Draft** documents describe a proposed artifact contract or policy;
- **Approved** documents govern their stated scope;
- **Implemented** means the approved contract is enforced or produced by Monad;
- **Deprecated/Superseded/Retired** follow `governance/document-lifecycle.md`.

A path or filename alone confers no authority.

## Required content standard

Every Markdown file in `artifact-system/` must contain enough information for a human or agent to understand:

1. purpose and problem addressed;
2. scope and explicit exclusions;
3. relationship to higher-authority artifacts;
4. required structure/data where the artifact is instantiated;
5. lifecycle and ownership;
6. invariants or normative rules where applicable;
7. traceability/provenance expectations;
8. security, privacy, reliability, or compatibility implications where relevant;
9. verification/acceptance method; and
10. known open questions or activation criteria.

Empty placeholders are prohibited after stabilization.

## Activation model

Artifact types are activated just in time. An artifact family becomes operational when one or more of the following is true:

- an accepted decision requires it;
- an approved specification relies on it;
- MVP/release evidence requires it;
- recurring engineering work needs a stable contract;
- risk or scale makes an informal representation unsafe.

Activation creates or identifies the canonical repository location, identifier scheme, schema/template, owner, validation rule, and GitHub projection if applicable.

## MVP criticality

The full catalog is larger than MVP. Stabilization populates every catalog document, but MVP implementation prioritizes:

- foundational authority and terminology;
- specifications and decisions;
- semantic graph and KIR contracts;
- repository/configuration model;
- CLI and diagnostics;
- AI/agent context boundaries;
- testing, CI, security, traceability, Work Packets, and release evidence.

Commercial, enterprise, registry, remote-execution, and ecosystem-scale artifacts remain Draft unless activated by an explicit decision.

## Relationship to the machine layer

Every non-excluded canonical artifact may be represented in the deterministic machine layer. The machine projection records source identity, hash, sections, identifiers, references, metadata, and graph relations. It must not infer approval status that is absent from canonical source.

## Change rule

Meaning-changing updates to an Approved artifact contract follow change control. Draft catalog refinement may proceed normally but must preserve identifiers and document any incompatibility with already-instantiated artifacts.