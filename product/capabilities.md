# Product Capabilities

**Status:** Proposed stabilization baseline

## C-01 — Repository and workspace discovery

Identify repository/workspace roots, configuration, packages/modules, canonical artifact locations, toolchains, and supported inputs deterministically.

## C-02 — Canonical knowledge ingestion

Read supported human-authored artifacts, preserve source provenance, normalize metadata/identifiers/references, and reject or diagnose malformed input.

## C-03 — Semantic graph compilation

Construct stable engineering entities and typed relationships spanning requirements, decisions, specifications, components, dependencies, work, tests, evidence, releases, and provenance.

## C-04 — KIR and canonical interchange

Lower validated semantic knowledge into canonical machine representations suitable for deterministic downstream consumption, caching, diff, and compatibility.

## C-05 — Diagnostics and conformance

Evaluate structural/semantic invariants, policies, and specification conformance and return stable actionable diagnostics.

## C-06 — Query, traversal, and explanation

Query graph state, traverse relationships, explain why/what-governs/what-depends, and retain the evidence path supporting the answer.

## C-07 — Change impact and incrementality

Relate repository changes to semantic entities and eventually derive minimal invalidation/execution scope.

## C-08 — Native tool orchestration

Plan and invoke native compilers, formatters, linters, tests, build tools, infrastructure tools, and other adapters through explicit capability contracts.

## C-09 — AI/agent context and governance

Select minimal authorized context, express scope/prohibitions/acceptance, record provenance, and support ChatGPT/Codex collaboration without granting unbounded authority.

## C-10 — Policy and governance

Represent/evaluate engineering rules, ownership, architectural constraints, exceptions, and acceptance gates against semantic state.

## C-11 — Documentation and projection

Generate or validate machine companions, publication views, status, GitHub projections, and later other derived artifacts from canonical knowledge.

## C-12 — Extensibility and ecosystem

Support adapters, plugins, registries, SDKs, and multi-repository evolution through stable contracts when scale requires them.

## C-13 — Release and provenance

Create traceable release evidence linking source, resolved inputs, semantic state, tests, artifacts, compatibility, and signatures/attestations where applicable.

## MVP capability boundary

MVP directly requires C-01, C-02, C-03, foundations of C-04, C-05, C-06, bounded C-09, and enough C-11/C-13 to prove deterministic provenance. C-07/C-08 begin only to the extent needed to demonstrate impact/validation; C-10/C-12 are architected but not broadly implemented.