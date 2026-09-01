# Codex Execution Contract v2 — WP-MVP-0002

Execution: EXEC-0004
Generated: 2026-08-16T16:05:00Z
Branch: `wp/mvp-0002`
Worktree: `/home/runner/work/monad/.monad-worktrees/wp-mvp-0002`
Baseline: `5dc6ad47759dbd7e315d23627feef5086eb64099`
Governing hash: `8ff12f33ec701fde9ae35c6a71b128ea4799a50118331652106a12a9f2b52142`
Contract hash: `bc8a277c3599ee885d7d02134de5e5882adf84f2e16d8e2fd578811949f746fd`

## Authority

This contract authorizes bounded implementation only. It does not authorize changes to product/architecture/specification policy unless the work packet explicitly lists the exact governed path with `allowed-governed-path`.

## Concurrency / Freshness

Before finalizing work, verify this contract with `./scripts/eos contract verify EXEC-0004`. If governing inputs drift, stop: the execution contract is invalid.

## Execution Scope

- allowed-path: `*`
- allowed-path: `**/*`

## Work Packet

# WP-MVP-0002 — Deterministic workspace discovery

**Status:** IN_PROGRESS
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


## Governing Input Fingerprints

- `engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md` — `bece83dc3997145b356fec00b224ea72ba8791cba0b03ab2563716fc252a34df`
- `engineering/work-cycles/WC-MVP-0001.md` — `42f4366d3b4e15c8ad60299e2a518ba028fd0c18d66a3b66ab544b8939a10a96`
- `engineering/work-packets/WP-MVP-0001.md` — `4a47380500b943435851542f9727b603b257fb903d9269e10cd6d57522f97aa4`
- `engineering/work-packets/WP-MVP-0002.md` — `75aa7cc03ee92053e66aba6b79da99613cc4024e50a691270c3ecedb802286ff`

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

Write JSON matching the contract to `.eos-result-EXEC-0004.json` in the worktree, then ingest it from the main repository:

`./scripts/eos execution ingest EXEC-0004 <path-to-result.json>`

The result is a claim. EOS independently compares it with the real Git diff and contract fingerprint.

