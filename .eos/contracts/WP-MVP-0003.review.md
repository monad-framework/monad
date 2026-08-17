# ChatGPT Review Contract — WP-MVP-0003

Review the target against all applicable accepted higher-authority artifacts.

## Target

# WP-MVP-0003 — Stable source and document identity

**Status:** IN_REVIEW
**Epic:** EPIC-003  
**Feature:** F-003-01  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0001  
**Product Goal:** PG-001

## Objective

Create clone-independent source/document identities and content provenance that downstream parsers, graph construction, diagnostics, KIR, queries, and agent context can rely on.

## Governing authority

- FR-002, FR-003, FR-009; QR-001, QR-005
- ADR-0003
- DATA-SOURCE-0001
- TECH-WORKSPACE-0001
- ADR-0005

## Dependencies

- WP-MVP-0001 is CLOSED and provides stable repository root/effective configuration semantics.
- WP-MVP-0002 is CLOSED and provides stable canonical discovery output.
- ADR-0005 is Accepted and establishes the authorized MVP implementation topology.

## Acceptance criteria

- [ ] US-008 stable Source IDs are equal across equivalent clean clones.
- [ ] US-009 SHA-256/source/parser provenance is recorded and changes when consumed bytes change.
- [ ] US-010 duplicate governed identifiers produce collision diagnostics naming all sources.
- [ ] content edits do not change Source ID solely because content changed.
- [ ] explicit governed Document IDs survive source-path moves; path-only Source IDs do not.
- [ ] absolute host path, time, random IDs, inode/device data, and Git branch do not affect identity.
- [ ] case-collision and symlink-alias fixtures are deterministic.

## Implementation boundary

Under ADR-0005, identity/provenance types and algorithms live in `monad-core`; no CLI-specific identity rules are permitted. Hashing/serialization dependencies must be locked and covered by golden vectors.

## Validation

Property tests plus golden identity vectors covering clone relocation, edits, moves, duplicates, case ambiguity, aliases, empty sources, and deterministic machine serialization.


## Required Review Dimensions

- scope conformance;
- requirements and specification conformance;
- architecture conformance;
- acceptance criteria;
- deterministic validation evidence;
- security/reliability risk;
- traceability completeness;
- unresolved findings;
- recommendation: ACCEPTED / ACCEPTED_WITH_FOLLOW_UP / REJECTED / BLOCKED.

Do not impersonate final human authorization where the governance model reserves
that decision to the human.
