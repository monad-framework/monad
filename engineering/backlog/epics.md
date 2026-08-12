# Epic Registry

**Status:** Proposed backlog baseline  
**Product Goal:** MVP Release 1 — deterministic semantic engineering loop

Epics are outcome-oriented backlog containers. Their presence does not authorize implementation. Priority expresses current ordering pressure and may change through refinement.

| ID | Epic | Horizon | Priority | Outcome |
| --- | --- | --- | --- | --- |
| EPIC-001 | Foundation, Governance & Product Identity | MVP | P0 | Stabilize the product thesis, authority, artifact lifecycle, Scrum/EOS integration, and repository governance. |
| EPIC-002 | Canonical Knowledge & Machine Projection | MVP | P0 | Keep human-readable canonical artifacts and deterministic machine companions/manifest/graph/corpus synchronized. |
| EPIC-003 | Workspace & Configuration Intelligence | MVP | P0 | Discover workspace identity, configuration, components, packages, artifact roots, and toolchains deterministically. |
| EPIC-004 | Semantic Identity & Provenance | MVP | P0 | Provide stable identities, normalization, source coordinates, lineage, aliases, hashing, and provenance. |
| EPIC-005 | Engineering Semantic Graph | MVP | P0 | Compile typed engineering entities and relationships into a deterministic, invariant-checked semantic graph. |
| EPIC-006 | Kernel Intermediate Representation | MVP | P0 | Define and implement versioned KIR, canonical serialization, lowering, compatibility, and conformance. |
| EPIC-007 | Diagnostics, Validation & Consistency | MVP | P0 | Make invalid, stale, contradictory, unsupported, and failed states explicit through structured diagnostics. |
| EPIC-008 | Query, Explanation & Navigation | MVP | P1 | Let humans and automation inspect, query, traverse, and explain engineering knowledge and provenance. |
| EPIC-009 | Change Impact & Incrementality | MVP | P1 | Compute conservative semantic blast radius and minimize recomputation without losing correctness. |
| EPIC-010 | Execution Planning & Native Tool Orchestration | MVP | P1 | Derive explicit execution plans and safely coordinate native tools with evidence and cache semantics. |
| EPIC-011 | CLI & Developer Experience | MVP | P1 | Deliver a coherent local CLI and progressive developer workflow for inspection through execution. |
| EPIC-012 | AI & Agent Context Engineering | MVP | P1 | Generate bounded, attributable context and task contracts for Codex/other agents under explicit authority. |
| EPIC-013 | Policy, Security & Trust | MVP | P0 | Protect repository ingestion, secrets, execution, agents, supply chain, and authority boundaries. |
| EPIC-014 | Testing, Conformance & Reproducibility | MVP | P0 | Prove deterministic semantics, compatibility, integration, performance, security, and clean-machine reproducibility. |
| EPIC-015 | Documentation, Publication & GitHub Projection | MVP | P1 | Project canonical knowledge into docs, search, GitHub Issues/Projects/Wiki, and other disposable views. |
| EPIC-016 | Packaging, Release & Dogfooding | MVP | P1 | Package, version, release, dogfood, attest, document, and support MVP Release 1. |
| EPIC-017 | Plugins, Adapters & Registry | Post-MVP | P2 | Provide stable extension manifests, SDKs, capabilities, permissions, signing, and registry distribution. |
| EPIC-018 | Remote, Team & Hosted Capabilities | Future | P3 | Add shared indexes, remote cache/execution, hosted control plane, and team collaboration. |
| EPIC-019 | Enterprise & Commercial Ecosystem | Future | P3 | Add enterprise governance, fleet insights, commercial packaging, support/SLA, and sustainability. |

## Ordering principles

MVP P0 work protects the correctness/authority foundation or sits on the semantic-kernel critical path. MVP P1 work completes the user-visible/executable Release 1 loop. Post-MVP and Future epics remain visible to prevent accidental architecture dead-ends but are not scheduled into Release 1 unless an approved change request demonstrates necessity.

## Traceability

Every Feature belongs to exactly one primary Epic for planning. Cross-epic dependencies are represented explicitly in Features, Stories, Work Packets, and the semantic graph rather than by duplicating backlog items.
