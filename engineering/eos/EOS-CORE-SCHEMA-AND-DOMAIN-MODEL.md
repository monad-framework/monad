# EOS Core Schema and Canonical Domain Model

**Status:** Implemented  
**Schema version:** 2.0.0  
**Domain-model version:** 1.0.0

## Purpose

Establish a stable, machine-readable semantic foundation for the Engineering Operating System. Every first-class EOS entity now shares one canonical contract for identity, lifecycle, versioning, timestamps, relationships, authority, and provenance.

## Canonical entities

Project, Artifact, Requirement, Capability, ADR, Specification, Risk, PI, WC, WP, Review, ChangeRequest, Release, MaintenanceItem, Evidence, Decision, Approval, Dependency, and TraceEdge.

## Common invariant

Every canonical entity MUST carry: `id`, `entity_type`, `schema_version`, `version`, `lifecycle_state`, `created_at`, `updated_at`, `relationships`, `authority_level`, and `provenance`. IDs are immutable and MUST NOT be reused. Entity version and schema version are independent.

## Authority levels

- `L0_INFORMATIVE` — descriptive or derived only.
- `L1_ADVISORY` — analysis/recommendation; non-binding.
- `L2_NORMATIVE` — approved rule or contract.
- `L3_BINDING` — active approval/authorization/control effect.
- `L4_HUMAN_SOVEREIGN` — human-only authority for mission, material risk, irreversible actions, and governance override.

## Provenance

Every entity records origin, creator, source references, and generation method. Optional commit and SHA-256 fields provide cryptographic linkage. Derived projections MUST preserve source references and cannot silently elevate authority.

## Compatibility boundary

The existing EOS CLI validates current TSV registries with a small operational schema engine. Those legacy operational schemas remain in place. The new canonical schemas live under `.eos/schemas/core/` and are normative for the domain model, preventing this tranche from breaking current PI/WC/WP/CR/REL/MNT operations. Future migration may project canonical entities into richer registries without changing their IDs.

## Canonical source

`.eos/domain-model.json` is the registry of entity kinds, ID patterns, lifecycle states, schema locations, and compatibility metadata. `.eos/schemas/core/base-entity.schema.json` defines the common contract. Each first-class entity has its own Draft 2020-12 JSON Schema.
