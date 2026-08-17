# Codex Execution Contract v2 — WP-MVP-0004

Execution: EXEC-0008
Generated: 2026-08-17T04:13:58Z
Branch: `wp/mvp-0004`
Worktree: `/data/MONAD/.monad-worktrees/wp-mvp-0004`
Baseline: `2566352812c212dc9b453b6ac3d45aac2b2bf1ad`
Governing hash: `4933e2428d0dfaaa2ab315a885b60260e18a9c9896bf99453be4a3c2f2a94816`
Contract hash: `a0474aed894a73342c878a5792fe460258360a28d2df80fe0dd5b52a0e179452`

## Authority

This contract authorizes bounded implementation only. It does not authorize changes to product/architecture/specification policy unless the work packet explicitly lists the exact governed path with `allowed-governed-path`.

## Concurrency / Freshness

Before finalizing work, verify this contract with `./scripts/eos contract verify EXEC-0008`. If governing inputs drift, stop: the execution contract is invalid.

## Execution Scope

- allowed-path: `*`
- allowed-path: `**/*`

## Work Packet

# WP-MVP-0004 — Markdown engineering artifact parser

**Status:** IN_PROGRESS
**Epic:** EPIC-003  
**Feature:** F-003-02  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0002  
**Product Goal:** PG-001

## Objective

Parse canonical Markdown artifacts into deterministic provenance-rich structural records and reference candidates without LLM inference or executable semantics.

## Governing authority

- FR-002; QR-001, QR-003
- ADR-0003, ADR-0004
- DATA-SOURCE-0001
- TECH-INGEST-0001
- ADR-0005

## Dependencies

- WP-MVP-0003 is CLOSED and provides stable source/document identity.
- ADR-0005 is Accepted and establishes the authorized MVP implementation topology.
- WC-MVP-0002 is ACTIVE and provides the current Parsing and Reference Resolution cycle context.

## Acceptance criteria

- [ ] US-011 section/heading/metadata structure and source ranges are extracted deterministically.
- [ ] US-012 governed identifiers/status metadata are extracted according to artifact contracts.
- [ ] US-013 links and identifier references are emitted as unresolved candidates with provenance.
- [ ] US-014 malformed/ambiguous governed constructs produce source-located diagnostics; partial recovery is not silently valid semantic state.
- [ ] code fences containing fake IDs/links are not treated as ordinary governed references.
- [ ] HTML/scripts/macros are never executed.
- [ ] repeat-run normalized output is equivalent/byte-stable where declared canonical.

## Out of scope

semantic graph construction, reference resolution, natural-language inference, arbitrary MDX execution, remote includes.

## Validation

Parser golden corpus covering headings, metadata, links, code fences, comments, Unicode, malformed constructs, empty documents, and security fixtures; machine-document freshness check.


## Governing Input Fingerprints

- `engineering/increments/PI-MVP-001-SEMANTIC-FOUNDATION.md` — `bece83dc3997145b356fec00b224ea72ba8791cba0b03ab2563716fc252a34df`
- `engineering/work-cycles/WC-MVP-0002.md` — `d6d06775832ece5a13c21668dc89da43c3682c19106e371866a2cf8eb10bb06e`
- `engineering/work-packets/WP-MVP-0003.md` — `853872eb65818c12c2a3eb7fb2e27728f5dc5f80e8bd56fca8db5ae37d341292`
- `engineering/work-packets/WP-MVP-0004.md` — `5fd2889a06ad028549513e7865bd99a3780d104b887d410ce002c7d4182c7fb8`

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

Write JSON matching the contract to `.eos-result-EXEC-0008.json` in the worktree, then ingest it from the main repository:

`./scripts/eos execution ingest EXEC-0008 <path-to-result.json>`

The result is a claim. EOS independently compares it with the real Git diff and contract fingerprint.

