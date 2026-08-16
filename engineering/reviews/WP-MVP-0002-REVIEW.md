---
artifact_id: "REV-WP-MVP-0002"
title: "WP-MVP-0002 Engineering Review"
type: "review"
version: "0.1.0"
status: "In Review"
authority: "review-authoritative"
created: "2026-08-16"
updated: "2026-08-16"
---

# WP-MVP-0002 — Engineering Review

**Decision:** REJECTED

## Target

- Artifact: `engineering/work-packets/WP-MVP-0002.md`
- State at review start: VERIFYING
- Governed execution: `EXEC-0004`
- Implementation merge: PR #190
- EOSV verification merge: PR #196
- Review baseline: `cb80c2f4599768f144d1cf94e7b95607b30098ff`

## Deterministic Verification

**Result:** PASS before review.

WP-MVP-0002 entered EOSR with current EXEC-0004-bound EOSV evidence, zero current stale evidence, canonical-state consistency, synchronized machine projections, and all required PR checks green. MNT-0002 / issue #191 is CLOSED and no longer blocks product review.

## Scope Conformance

PASS.

The agent-authored product implementation is confined to `crates/monad-core/src/discovery.rs`, the `monad-core` module export, and generated machine projections. The implementation introduces no service/plugin boundary, network dependency, repository-code execution path, or unrelated product refactor.

## Requirements / Specification Conformance

**REJECTED due to one blocking failure-recovery defect.**

The implementation otherwise conforms to the central TECH-WORKSPACE-0001 behaviors: configured include/exclude selection, default `.git`/`.eos`/`machine`/`target` exclusions, canonical repository-relative paths, stable ordering, overlapping-pattern de-duplication with provenance, root-containment enforcement, symlink diagnostics, supported Markdown/YAML classification, unsupported-source diagnostics, and deterministic equivalent-clone output.

However, `Walker::walk_directory()` currently collects directory entries with:

```rust
let mut entries = entries.filter_map(Result::ok).collect::<Vec<_>>();
```

Any per-entry error yielded by `std::fs::ReadDir` is therefore silently discarded. TECH-WORKSPACE-0001 requires unreadable files/inputs to produce diagnostics, and US-007 requires unsupported/unsafe structures to produce actionable diagnostics. A transient or permission-related enumeration failure can currently omit an otherwise configured candidate without any diagnostic, creating silent incompleteness and potentially filesystem-timing-dependent discovery output.

## Architecture Conformance

PASS subject to the blocking failure-recovery correction.

Discovery remains local and deterministic in `monad-core`, does not execute repository code, does not invoke package managers/plugins, performs no network access, and enforces root containment consistent with ADR-0002, ADR-0004, and ADR-0005.

## Acceptance Criteria Evidence

PASS for six criteria; US-007 is not fully satisfied.

- US-005: supported configured candidates are discovered — PASS.
- US-006: ordering is stable across differing filesystem creation/enumeration order — PASS.
- US-007: unsupported/unsafe structures produce actionable diagnostics — **FAIL for per-entry directory enumeration errors**.
- Default/configured exclusions prevent canonical ingestion — PASS.
- Overlapping patterns produce one canonical candidate with merged provenance — PASS.
- External/cyclic symlinks cannot escape root or create duplicate semantic sources — PASS.
- Repository code/network is never executed — PASS.

## Test / Validation Evidence

PASS for the implemented test set, but the test set does not cover the blocking `ReadDir` item-error path.

Existing verification includes formatting, Clippy with warnings denied, all workspace tests, machine-document synchronization, governed EOSE execution/result checking, current EOSV evidence, and repository PR CI.

## Security / Reliability Findings

One blocking reliability finding:

**EOSR-WP-MVP-0002-F001 — Silent `ReadDir` item errors.**

Severity: blocking conformance / reliability.

Required correction:

1. replace silent `filter_map(Result::ok)` handling with explicit per-entry error handling;
2. emit a deterministic `UnreadableSource` discovery diagnostic for enumeration errors, anchored to the containing repository-relative directory (or another stable location available at that failure boundary);
3. retain stable ordering of all successfully enumerated entries and diagnostics;
4. add focused regression coverage for the error-handling helper/path without weakening existing deterministic discovery tests;
5. rerun full Rust validation and refresh EOSV evidence after the product/test correction.

## Traceability Findings

PASS except for EOSR-WP-MVP-0002-F001.

The implementation is traceable to FR-001; QR-001 and QR-003; ADR-0002, ADR-0004, ADR-0005; IFC-WORKSPACE-0001; TECH-WORKSPACE-0001; WP-MVP-0002; EXEC-0004; and current EOSV evidence.

## Blocking Findings

1. **EOSR-WP-MVP-0002-F001 — `ReadDir` item failures are silently dropped instead of diagnosed.**

No other blocking finding was identified in this review pass.

## Non-Blocking Findings

None specific to WP-MVP-0002 at this review stage. Separate EOS issues #175, #176, #178, and #181 remain outside this packet.

## Decision

**REJECTED** pending correction and re-verification of EOSR-WP-MVP-0002-F001.
