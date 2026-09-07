# Codex Execution Contract v2 — WP-MVP-0005

Execution: EXEC-0010
Generated: 2026-09-07T15:14:39Z
Branch: `wp/mvp-0005`
Worktree: `/home/runner/work/monad/.monad-worktrees/wp-mvp-0005`
Baseline: `12750d1ace8df46587be3d816ef8d4e09b31eda1`
Governing hash: `d3284e11b0364f97e82aaf5049db30e85a32dc9fda4ffe1c8e2d47a20c064db1`
Contract hash: `2879de4abf9e0d8d3ea731b154adf3ceccbc441c19e8d193310f2ee8756c0fb5`

## Authority

This contract authorizes bounded implementation only. It does not authorize changes to product/architecture/specification policy unless the work packet explicitly lists the exact governed path with `allowed-governed-path`.

## Concurrency / Freshness

Before finalizing work, verify this contract with `./scripts/eos contract verify EXEC-0010`. If governing inputs drift, stop: the execution contract is invalid.

## Execution Scope

- allowed-path: `*`
- allowed-path: `**/*`

## Work Packet

# WP-MVP-0005 — Structured Monad configuration parser

**Status:** IN_PROGRESS
**Epic:** EPIC-003  
**Feature:** F-003-03  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0002  
**Product Goal:** PG-001

## Objective

Represent canonical `monad.toml` as a provenance-rich semantic input after bootstrap validation, without creating a competing configuration authority.

## Governing authority

- FR-001, FR-002; QR-001, QR-003
- ADR-0002, ADR-0003, ADR-0004
- IFC-WORKSPACE-0001
- DATA-SOURCE-0001
- TECH-INGEST-0002
- ADR-0005

## Dependencies

- WP-MVP-0001 is CLOSED and supplies valid effective configuration and precedence semantics.
- WP-MVP-0003 is CLOSED and supplies stable source/document identity and provenance.
- ADR-0005 is Accepted and authorizes the MVP Rust implementation topology and `monad-core` semantic boundary.
- WC-MVP-0002 is ACTIVE and supplies the current parsing/reference-resolution execution context.

These historical prerequisite blockers are satisfied. This packet does not reimplement configuration precedence. Prerequisite completion alone did not make the packet Ready, authorized, or started; those lifecycle transitions require separate governed EOS gates.

## Acceptance criteria

- [ ] US-015 valid `monad.toml` becomes a deterministic semantic document record.
- [ ] US-016 schema/parse errors remain diagnostics and block a valid semantic config document.
- [ ] US-017 normalized semantic representation is deterministic and retains source/effective-value provenance distinctions.
- [ ] `.monad/manifest.yaml` cannot override or become a competing semantic config source.
- [ ] no environment interpolation, command substitution, network lookup, or include execution occurs.

## Implementation boundary

Under ADR-0005, semantic config adaptation belongs in the ingestion/config modules of `monad-core`; bootstrap loader semantics from WP-MVP-0001 are reused rather than duplicated.

## Validation

Golden config corpus for canonical repository config, malformed/unknown/unsupported keys, override provenance, deterministic representation, and legacy-manifest non-authority.

## Authorization disposition

The prior dependency block is cleared by canonical closure/acceptance evidence for WP-MVP-0001 and WP-MVP-0003 plus the Accepted ADR-0005. This packet was adopted into canonical EOS lifecycle control, passed `WP_READY` (`DRAFT → READY`), and has now passed the separate `WP_AUTHORIZE` gate (`READY → AUTHORIZED`). The next permitted lifecycle action is the separate EOSE start transition. Execution preparation, start, product mutation, and implementation remain prohibited until that governed start transition passes and is recorded.


## Governing Input Fingerprints

- `engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md` — `bece83dc3997145b356fec00b224ea72ba8791cba0b03ab2563716fc252a34df`
- `engineering/work-cycles/WC-MVP-0002.md` — `d6d06775832ece5a13c21668dc89da43c3682c19106e371866a2cf8eb10bb06e`
- `engineering/work-packets/WP-MVP-0001.md` — `4a47380500b943435851542f9727b603b257fb903d9269e10cd6d57522f97aa4`
- `engineering/work-packets/WP-MVP-0003.md` — `853872eb65818c12c2a3eb7fb2e27728f5dc5f80e8bd56fca8db5ae37d341292`
- `engineering/work-packets/WP-MVP-0005.md` — `26ce2d5e617fd4d0e6ddad922627838addc84a3cdeeaddfbcaa564919ddba6bc`

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

Write JSON matching the contract to `.eos-result-EXEC-0010.json` in the worktree, then ingest it from the main repository:

`./scripts/eos execution ingest EXEC-0010 <path-to-result.json>`

The result is a claim. EOS independently compares it with the real Git diff and contract fingerprint.

