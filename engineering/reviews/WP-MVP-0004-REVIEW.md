---
artifact_id: "REV-WP-MVP-0004"
title: "WP-MVP-0004 Engineering Review"
type: "review"
version: "0.1.0"
status: "In Review"
authority: "review-authoritative"
created: "2026-08-26"
updated: "2026-08-26"
---


# WP-MVP-0004 — Engineering Review

**Decision:** ACCEPTED

## Target

- Artifact: `engineering/work-packets/WP-MVP-0004.md`
- State at final review start: IN_REVIEW
- Governed execution: `EXEC-0009`
- Initial implementation merge: PR #217
- Initial rejected EOSR merge: PR #230
- F001 correction merge: PR #231
- Post-correction EOSV merge: PR #232
- Final review baseline: `385fd7bb8631e25d4c2cdae0c2a81f8406ba734b`

## Deterministic Verification

**Result:** PASS.

The canonical merged state was freshly revalidated before this review using formatting checks, Clippy with warnings denied, and the complete workspace test suite. `monad-core` has 56 passing tests. Focused independent reruns also pass for canonical front-matter authority, prevention of the review/Work-Packet false duplicate, and malformed/duplicate/conflicting explicit identity behavior. EOS strict verification, canonical-state consistency, trace integrity, and machine-document synchronization pass.

Current post-correction EOSV evidence is `EVID-0229` through `EVID-0231`, captured after PR #231 was merged and integrated through PR #232.

## Scope Conformance

PASS.

The product correction is confined to `crates/monad-core/src/markdown.rs`; the remaining correction/EOSV changes are governed evidence, trace, and machine projections. The parser remains deterministic, local, non-executing, and free of network behavior. No CLI-owned semantic rule, graph construction, reference resolution, LLM inference, arbitrary MDX execution, remote include, plugin/runtime expansion, or unrelated product refactor was introduced.

## Requirements / Specification Conformance

PASS.

The implementation now satisfies FR-002, QR-001, QR-003, ADR-0003, ADR-0004, DATA-SOURCE-0001, TECH-INGEST-0001, and ADR-0005 for this packet:

- canonical Markdown structural and metadata extraction is deterministic and source-located;
- canonical top-of-document YAML `artifact_id` is authoritative explicit document identity;
- H1 governed identifiers are identity fallback only when no authoritative explicit identity is declared;
- canonical front-matter `status` is preserved as metadata;
- malformed, duplicate, and conflicting explicit identities produce diagnostics and cannot silently fall back to H1 identity;
- links and governed identifier references remain unresolved provenance-rich candidates;
- code fences, inline code, HTML comments, scripts, macros, and executable-looking content remain inert;
- normalized output remains deterministic and parser semantics are versioned through Markdown parser contract v2.

## Architecture Conformance

PASS.

Markdown semantic extraction remains in `monad-core`, consistent with ADR-0005. The correction composes with ADR-0003 document identity rather than duplicating identity derivation. It preserves ADR-0004 safe-ingestion constraints: repository content is treated as data, no network fetch is performed, and no repository code or embedded construct is executed.

## Acceptance Criteria Evidence

PASS for all seven WP-MVP-0004 acceptance criteria.

- US-011: section/heading/metadata structure and exact source ranges are extracted deterministically — PASS, including canonical front matter.
- US-012: governed identifiers and status metadata follow artifact contracts — PASS. `artifact_id` is authoritative; H1 is fallback only; malformed/duplicate/conflicting explicit identity blocks silent fallback.
- US-013: links and identifier references are emitted as unresolved candidates with provenance — PASS, including the reviewed Work Packet ID in a review H1 remaining a reference rather than review identity.
- US-014: malformed/ambiguous governed constructs produce source-located diagnostics without silently valid semantic promotion — PASS, including malformed and unclosed governed front matter.
- Fake IDs/links inside code fences are not ordinary governed references — PASS.
- HTML/scripts/macros are never executed — PASS.
- Repeat-run normalized output is equivalent/byte-stable where declared canonical — PASS.

The Work Packet checklist remains unreconciled here by design; acceptance review and checklist/closure are separate governed transactions.

## Test / Validation Evidence

PASS.

Coverage includes headings, bold metadata, canonical YAML front matter, links, optional link titles, Unicode, malformed constructs, invalid UTF-8 spans, empty documents, code fences, HTML comments, multiline inline code, namespace filtering, explicit-ID conflicts, deterministic serialization, executable-looking inert content, and repeatability.

The five F001-focused regressions all pass, including the exact canonical review shape that previously failed. A review with `artifact_id: REV-WP-MVP-0003` and H1 target `WP-MVP-0003` now retains review identity `REV-WP-MVP-0003`, preserves status, treats the H1 target as a reference candidate, and does not collide with the actual `WP-MVP-0003` Work Packet.

## Security / Reliability Findings

No blocking security or reliability finding remains.

The parser does not execute HTML, scripts, macros, code fences, inline code, links, remote includes, or repository commands. F001's reliability impact—manufacturing a false fatal duplicate identity and dropping authoritative lifecycle metadata—is resolved by explicit front-matter authority plus fail-closed malformed-identity behavior.

## Traceability Findings

PASS.

The accepted result is traceable through FR-002; QR-001 and QR-003; ADR-0003, ADR-0004, and ADR-0005; DATA-SOURCE-0001; TECH-INGEST-0001; WP-MVP-0004; EXEC-0006 through EXEC-0009; implementation PR #217; rejected review PR #230; corrective PR #231; post-correction EOSV PR #232; and current evidence EVID-0229 through EVID-0231.

## Blocking Findings

None.

`EOSR-WP-MVP-0004-F001` is **RESOLVED**. The exact previously failing review-artifact identity scenario is covered by a permanent regression and passes on canonical `main`.

## Non-Blocking Findings

The earlier maintainability observation remains: the governed-identifier namespace allowlist must be intentionally extended with regression coverage when future canonical namespaces are introduced. This is not a defect in the present authorized scope.

## Decision

**ACCEPTED.** WP-MVP-0004 satisfies its authorized scope and all acceptance criteria after the bounded F001 correction. It may proceed to the separate governed checklist-reconciliation and closure transaction. This review does not itself close the Work Packet.
