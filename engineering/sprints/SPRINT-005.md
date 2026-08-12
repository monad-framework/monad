# SPRINT-005 — Kernel Intermediate Representation

**Status:** Forecast  
**Dates:** 2026-09-14 through 2026-09-20  
**Product Increment:** PI-002 — Semantic Kernel

## Sprint Goal

Establish KIR as a versioned, canonical machine boundary derived from MSG so downstream validation, query, interoperability, execution planning, and future plugins do not need to reinterpret arbitrary source documents.

## Forecast PBIs

EN-006-01 through EN-006-06.

## Forecast Work Packets

WP-KIR-0001 — charter/schema/serialization/lowering; WP-KIR-0002 — validation/conformance/versioning/compatibility/migrations.

## Acceptance scenario

A known MSG fixture lowers into schema-valid KIR with deterministic canonical serialization. Equivalent graph semantics produce equivalent KIR; invalid or unsupported graph semantics fail with structured diagnostics. Version/compatibility metadata is explicit.

## Review evidence

JSON/schema or selected representation contract, canonicalization vectors, graph→KIR golden fixtures, validation tests, compatibility matrix, migration examples, and independent consumer fixture.

## Exit condition

SPRINT-006 query/impact capabilities can consume stable graph/KIR contracts and machine representations without relying on internal implementation layout.
