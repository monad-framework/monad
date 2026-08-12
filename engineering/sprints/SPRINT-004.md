# SPRINT-004 — Monad Semantic Graph

**Status:** Forecast  
**Dates:** 2026-09-07 through 2026-09-13  
**Product Increment:** PI-002 — Semantic Kernel

## Sprint Goal

Compile stable semantic inputs into the first deterministic Monad Semantic Graph with an explicit ontology, typed entities/relationships, provenance, invariants, canonical snapshot, and traversal support.

## Forecast PBIs

EN-005-01 through EN-005-07, EN-007-04, EN-014-02.

## Forecast Work Packets

WP-MSG-0001 — ontology/taxonomy; WP-MSG-0002 — construction/invariants/snapshot/traversal.

## Acceptance scenario

Reference artifacts representing requirements, decisions, specifications, components/dependencies, tests, work, and evidence compile into the expected typed graph. Repeated compilation produces the same semantic graph and canonical serialization; sampled edges explain their provenance.

## Key invariants

- unique stable node identity;
- permitted edge endpoint/type combinations;
- deterministic ordering independent of traversal/concurrency;
- required provenance on derived relationships;
- unresolved required references do not become invented edges;
- invalid graph state cannot be serialized as accepted output.

## Review evidence

Golden graphs, property tests, invalid-graph fixtures, deterministic hashes, provenance/explanation samples, and traversal/index conformance.

## Exit condition

KIR lowering in SPRINT-005 can consume a stable versioned graph boundary without reparsing source artifacts.
