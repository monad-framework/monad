# Codex Execution Contract v2 — WP-MVP-0003

Execution: EXEC-0005
Generated: 2026-08-16T19:48:36Z
Branch: `wp/mvp-0003`
Worktree: `/data/MONAD/.monad-worktrees/wp-mvp-0003`
Baseline: `d7cdaa7f97bdd443052284c73a18fc7bd14d3586`
Governing hash: `e07d122864570be67a476a8a970683b43fa548517e211bd006e4688efd5bfae5`
Contract hash: `315ad5b045c99272f0d78717ed4fe98d65d1a8029cf7d7f59da38aee4bb63a2d`

## Authority

This contract authorizes bounded implementation only. It does not authorize changes to product/architecture/specification policy unless the work packet explicitly lists the exact governed path with `allowed-governed-path`.

## Concurrency / Freshness

Before finalizing work, verify this contract with `./scripts/eos contract verify EXEC-0005`. If governing inputs drift, stop: the execution contract is invalid.

## Execution Scope

- allowed-path: `*`
- allowed-path: `**/*`

## Work Packet

# WP-MVP-0003 — Stable source and document identity

**Status:** IN_PROGRESS
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


## Governing Input Fingerprints

- `engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md` — `bece83dc3997145b356fec00b224ea72ba8791cba0b03ab2563716fc252a34df`
- `engineering/work-cycles/WC-MVP-0001.md` — `42f4366d3b4e15c8ad60299e2a518ba028fd0c18d66a3b66ab544b8939a10a96`
- `engineering/work-packets/WP-MVP-0001.md` — `4a47380500b943435851542f9727b603b257fb903d9269e10cd6d57522f97aa4`
- `engineering/work-packets/WP-MVP-0002.md` — `72e50275688b966af5d0dd145452a3ce7b1985c1871c3cd30789040f180b2f6c`
- `engineering/work-packets/WP-MVP-0003.md` — `354f749bf713aefb71698f9b6329a44e42a7b417df97e0e8e8ee60651131a4a1`

## Required Operating Procedure

1. Work only inside the assigned worktree and branch.
2. Do not edit `.eos/` or Git internals.
3. Do not expand product/architecture/specification scope to make implementation easier.
4. Preserve stable IDs and traceability references.
5. Run repository-prescribed validation and WP-specific validation.
6. Compare actual Git changes against execution scope.
7. Produce the structured JSON completion result described below.
8. Stop and report BLOCKED if a governing decision must change.

## Required Completion Result

Write JSON matching the contract to `.eos-result-EXEC-0005.json` in the worktree, then ingest it from the main repository:

`./scripts/eos execution ingest EXEC-0005 <path-to-result.json>`

The result is a claim. EOS independently compares it with the real Git diff and contract fingerprint.

