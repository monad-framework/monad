# WP-MVP-0006 — Local reference resolution

**Status:** Refined — blocked from Ready by WP-MVP-0004/WP-MVP-0005 and ADR-0005  
**Epic:** EPIC-003  
**Feature:** F-003-04  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0002  
**Product Goal:** PG-001

## Objective

Resolve local governed identifiers and canonical file references deterministically into provenance-rich typed relation candidates while preserving missing, ambiguous, external, and noncanonical targets explicitly.

## Governing authority

- FR-002, FR-003, FR-004; QR-001, QR-003
- ADR-0003, ADR-0004
- DATA-SOURCE-0001
- TECH-INGEST-0001/0002/0003
- proposed ADR-0005

## Dependencies

WP-MVP-0004 and WP-MVP-0005 provide parsed reference candidates; WP-MVP-0003 provides stable identity. Full source index must be available before deterministic resolution.

## Acceptance criteria

- [ ] US-018 local governed-ID and canonical file references resolve against the complete source index.
- [ ] US-019 unresolved, ambiguous, external, and noncanonical references remain explicit; no traversal-order winner is invented.
- [ ] US-020 resolved references emit typed relation candidates carrying rule and source provenance.
- [ ] `..`/root-escape references are rejected/diagnosed.
- [ ] external URLs are never fetched during resolution.
- [ ] ordering is deterministic under randomized parse/input ordering.

## Out of scope

semantic graph materialization, network resolution, semantic inference from prose, package-manager/module resolution, native tool execution.

## Validation

Golden/property reference corpus covering valid/missing/duplicate IDs, relative paths, anchors, excluded targets, traversal attempts, external URLs, duplicate filenames, case ambiguity, and randomized input ordering.
