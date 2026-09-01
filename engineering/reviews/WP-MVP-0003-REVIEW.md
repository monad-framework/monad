---
artifact_id: "REV-WP-MVP-0003"
title: "WP-MVP-0003 Engineering Review"
type: "review"
version: "0.1.0"
status: "In Review"
authority: "review-authoritative"
created: "2026-08-17"
updated: "2026-08-17"
---

# WP-MVP-0003 — Engineering Review

**Decision:** ACCEPTED

## Target

- Artifact: `engineering/work-packets/WP-MVP-0003.md`
- State at review start: VERIFYING
- Governed execution: `EXEC-0005`
- Implementation merge: PR #204
- EOSV verification merge: PR #205
- Review baseline: `d7a420ce6b78836e2ada408dca50282c88de518f`

## Deterministic Verification

**Result:** PASS before review.

The merged implementation was freshly revalidated with Rust 1.95.0 using formatting checks, Clippy with warnings denied, and the complete workspace test suite. EOS strict verification, canonical-state consistency, and machine-document synchronization also pass. WP-MVP-0003 enters EOSR with current EVID-0082–EVID-0084 bound to EXEC-0005; EOS integrity and execution acceptance are PASS and the optional repository validator is SKIPPED by configuration.

## Scope Conformance

PASS.

Product changes are limited to the Rust workspace dependency/lock metadata, `crates/monad-core` identity/discovery implementation, the module export, and generated machine projections. The implementation introduces no CLI-specific identity rules, service/plugin boundary, network behavior, repository-code execution, or unrelated product refactor. The minimal discovery extension for case-collision diagnostics is directly required by ADR-0003 and WP-MVP-0003 acceptance coverage.

## Requirements / Specification Conformance

PASS.

The implementation conforms to the identity/provenance rules established by ADR-0003 and DATA-SOURCE-0001:

- Source IDs are versioned/domain-separated SHA-256 identities over unambiguous length-framed canonical repository-relative path and source-kind inputs only.
- Source content is excluded from Source ID derivation, so ordinary byte edits preserve source identity at a stable path.
- `SourceRecord` retains the original canonical path and source kind alongside exact-byte lowercase SHA-256, byte length, parser contract, and deterministic discovery provenance; the digest representation therefore does not lose authoritative identity components.
- Path-derived Document IDs depend on Source ID plus document kind, so a source move changes a path-only document identity.
- Explicit governed Document IDs depend on document kind plus governed namespace/value, not source path, so they survive source moves.
- Duplicate governed identifiers are grouped by explicit namespace/value, produce deterministic diagnostics naming all unique conflicting repository-relative locations in sorted order, and do not select a traversal-order winner.
- Path case is preserved in Source IDs. Discovery separately emits deterministic `CaseCollisionRisk` diagnostics for canonical paths differing only by case.
- Symlink aliases remain governed by deterministic discovery containment/de-duplication and therefore do not create additional semantic source identities.
- Exact consumed bytes, including empty and binary content, are hashed without text normalization.

## Architecture Conformance

PASS.

Identity/provenance types and algorithms live in `monad-core` as required by ADR-0005. Discovery remains the canonical source of repository-relative path, source kind, and discovery provenance. No identity behavior is duplicated in the CLI. The only new runtime dependency is the established `sha2` crate, locked through Cargo, which is appropriate for the required SHA-256 behavior.

## Acceptance Criteria Evidence

PASS for all seven WP-MVP-0003 criteria.

- US-008: stable Source IDs are equal across equivalent clean clones — PASS. The derivation has no clone-root input and equivalent canonical path/kind inputs produce identical IDs.
- US-009: SHA-256/source/parser provenance is recorded and changes when consumed bytes change — PASS. Exact-byte content vectors, byte lengths, parser contract, and discovery provenance are represented in `SourceRecord`.
- US-010: duplicate governed identifiers produce collision diagnostics naming all sources — PASS. Namespace-aware BTreeMap grouping plus sorted/de-duplicated repository-relative locations makes output traversal-order independent.
- Content edits do not change Source ID solely because content changed — PASS. Content is absent from Source ID framing; tests verify equal IDs with differing bytes and differing content digests.
- Explicit governed Document IDs survive source-path moves; path-only identities do not — PASS. Tests cover both move behaviors.
- Absolute host path, time, random IDs, inode/device data, and Git branch do not affect identity — PASS. Those values are absent from the derivation inputs and serialized source model.
- Case-collision and symlink-alias fixtures are deterministic — PASS. Discovery preserves distinct case-sensitive canonical paths while emitting a sorted collision-risk diagnostic, and symlink alias fixtures yield one canonical source/identity.

## Test / Validation Evidence

PASS.

The workspace suite contains 29 passing tests after WP-MVP-0003. Identity coverage includes exact SHA-256 vectors for ordinary, empty, and binary bytes; versioned Source-ID golden vectors; source-kind separation; Unicode/spaces/punctuation framing; content-edit stability; path-only and explicit-ID moves; duplicate governed-ID ordering and namespace isolation; deterministic serialization; case-collision behavior; and symlink alias de-duplication. The merged implementation also passes formatting, Clippy with `-D warnings`, repository PR integrity checks, machine-document synchronization, governed EXEC-0005 checking, and first-class EOSV.

## Security / Reliability Findings

No blocking security or reliability finding was identified.

SHA-256 uses the maintained Rust `sha2` implementation rather than bespoke cryptography. Identity inputs exclude nondeterministic host/process metadata. Collision and case-risk diagnostics use repository-relative paths and deterministic ordering. Discovery root-containment and symlink-cycle protections remain intact.

## API Boundary Observation

Non-blocking: low-level public derivation helpers accept canonical path/document strings as caller preconditions rather than introducing validated newtypes for every component. The integrated construction path (`SourceRecord::from_discovered`) receives canonical paths from deterministic discovery, so the governed MVP path satisfies the invariant. If these helpers later become a broader external compatibility surface, typed validation can be considered without changing this packet's accepted semantics.

## Traceability Findings

PASS.

The implementation is traceable to FR-002, FR-003, FR-009; QR-001 and QR-005; ADR-0003; DATA-SOURCE-0001; TECH-WORKSPACE-0001; ADR-0005; WP-MVP-0003; EXEC-0005; implementation PR #204; and current EOSV evidence EVID-0082–EVID-0084.

## Blocking Findings

None.

## Non-Blocking Findings

No packet-specific defect requires correction before closure. The API-boundary observation above is future hardening, not an acceptance failure. Separate EOS issues #175, #176, #178, and #181 remain outside this Work Packet.

## Decision

**ACCEPTED.** WP-MVP-0003 satisfies its authorized scope and acceptance criteria and may proceed to the separate governed checklist-reconciliation and closure transaction.
