# WP-MVP-0002 — Deterministic workspace discovery

**Status:** AUTHORIZED
**Epic:** EPIC-002  
**Feature:** F-002-02  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0001  
**Product Goal:** PG-001

## Objective

Enumerate the configured canonical workspace deterministically and safely, with stable ordering, containment checks, exclusions, and discovery provenance.

## Governing authority

- FR-001; QR-001, QR-003
- ADR-0002, ADR-0004
- IFC-WORKSPACE-0001
- TECH-WORKSPACE-0001
- ADR-0005

## Dependencies

- WP-MVP-0001 is CLOSED and provides the required valid root/effective configuration boundary.
- ADR-0005 is Accepted and establishes the authorized MVP implementation topology.

## In scope

configured include/exclude matching; canonical relative paths; stable candidate ordering; overlapping-pattern de-duplication; symlink containment/cycle handling; unsupported-source diagnostics; discovery provenance; fixtures.

## Out of scope

parsing document content; source/document ID allocation beyond the canonical-path inputs needed by WP-MVP-0003; graph construction; package-manager/native-tool discovery requiring execution; network access.

## Acceptance criteria

- [ ] US-005 supported configured workspace candidates are discovered.
- [ ] US-006 ordering is stable under randomized filesystem enumeration.
- [ ] US-007 unsupported/unsafe structures produce actionable diagnostics.
- [ ] exclusions prevent `.git/`, `.eos/`, `machine/`, and configured build output from canonical ingestion by default.
- [ ] overlapping patterns produce one canonical candidate.
- [ ] external/cyclic symlinks cannot escape root or create duplicate semantic sources.
- [ ] no repository code/network executes.

## Implementation boundary

Under accepted ADR-0005, changes belong in the workspace/discovery module and its focused fixtures/tests in `monad-core`; CLI changes are limited to exposing already-defined discovery results/diagnostics.

## Validation

Focused unit/property/golden discovery tests, randomized-order test harness, symlink/security fixtures where the platform supports them, and machine-document freshness check.
