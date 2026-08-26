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

**Decision:** REJECTED

## Target

- Artifact: `engineering/work-packets/WP-MVP-0004.md`
- State at review start: VERIFYING
- Governed execution: `EXEC-0009`
- Implementation merge: PR #217
- Post-merge EOSV merge: PR #224
- Review baseline: `8923f63e39d26937c82d3e9837431c7cdd89b1ee`

## Deterministic Verification

**Result:** PASS for the existing repository suite; a focused EOSR adversarial conformance probe FAILS as expected and exposes a missing canonical-artifact contract case.

Before lifecycle mutation, the merged baseline independently passed:

- `cargo fmt --all -- --check`;
- `cargo clippy --workspace --all-targets --all-features -- -D warnings`;
- `cargo test --workspace --all-targets --all-features`;
- `./scripts/eos verify --strict`;
- `./scripts/eos state status`;
- `python3 scripts/sync-machine-docs.py --check`.

A temporary uncommitted regression probe used the repository's real review-artifact shape: YAML front matter with `artifact_id: "REV-WP-MVP-0003"` and `status: "In Review"`, followed by H1 `# WP-MVP-0003 — Engineering Review`. The current parser returns explicit document identity `WP-MVP-0003`, not `REV-WP-MVP-0003`; the expected contract probe therefore fails. The probe was removed before the governed review transaction.

## Scope Conformance

PASS.

The merged implementation remains within the authorized Rust semantic-core boundary. Product semantics are confined to `crates/monad-core/src/markdown.rs` plus its module export. There is no network access, repository-code execution, CLI-owned duplicate semantic rule, plugin/runtime expansion, or unrelated refactor.

## Requirements / Specification Conformance

REJECTED because of one blocking root defect, `EOSR-WP-MVP-0004-F001`.

FR-002 requires canonical Markdown ingestion to preserve sections, metadata, stable identifiers, and references, while malformed input cannot silently become valid semantic state. TECH-INGEST-0001 likewise requires recognized metadata fields expressed by the artifact contract plus explicit governed identifiers and statuses where present. Monad's canonical repository configuration includes `engineering/**/*.md`, and governed review/change artifacts in that tree use YAML front matter for their canonical artifact identity and lifecycle metadata.

The current parser does not parse YAML front matter as Markdown artifact metadata. It instead promotes an approved governed identifier found in an H1 heading to explicit document identity. This is incorrect for canonical review artifacts whose H1 names the reviewed target while front matter identifies the review artifact itself.

## Architecture Conformance

PARTIAL / BLOCKED BY F001.

The implementation correctly lives in `monad-core`, remains deterministic/offline, and preserves the ADR-0004 safe-ingestion boundary. However ADR-0003 requires a Document ID to use the explicit governed identifier when the artifact contract defines one. Ignoring the canonical front-matter `artifact_id` and substituting the H1 target ID violates that identity rule.

This also interacts directly with DATA-SOURCE-0001: duplicate explicit governed identifiers are fatal and must not be resolved by traversal order. Under the current parser, an actual Work Packet `WP-MVP-0003` and its canonical review `REV-WP-MVP-0003` are both assigned explicit identifier `WP-MVP-0003`, manufacturing a false fatal collision.

## Acceptance Criteria Evidence

- US-011 section/heading/metadata structure and source ranges are extracted deterministically — **FAIL / PARTIAL**. Heading/source-range behavior is well covered, but canonical YAML front-matter metadata is omitted.
- US-012 governed identifiers/status metadata are extracted according to artifact contracts — **FAIL**. Canonical `artifact_id` and `status` front-matter fields are not extracted; H1 target IDs can be promoted as document identity instead.
- US-013 links and identifier references are emitted as unresolved candidates with provenance — **PASS**. Link/title parsing, approved identifier namespaces, lexical boundaries, and exact spans have focused coverage.
- US-014 malformed/ambiguous governed constructs produce source-located diagnostics without silent valid promotion — **FAIL / PARTIAL** for canonical front-matter identity/status fields because they are not recognized as governed metadata at all.
- Code fences containing fake IDs/links are not treated as ordinary governed references — **PASS**.
- HTML/scripts/macros are never executed — **PASS**.
- Repeat-run normalized output is equivalent/byte-stable where declared canonical — **PASS** for currently modeled constructs.

## Test / Validation Evidence

The existing suite is strong and all current tests pass. It covers headings, bold metadata, links, Unicode, malformed constructs, UTF-8 diagnostics, code fences, HTML comments, multiline inline code, explicit-ID conflicts, link titles, identifier namespace filtering, and repeatability.

The EOSR probe demonstrates the missing test class: a real canonical governed artifact with YAML front matter whose `artifact_id` differs intentionally from the H1 target/reference identifier. The current suite does not cover that artifact contract shape.

## Security / Reliability Findings

No execution/network security regression was found. The parser remains side-effect free and inert with respect to code fences, HTML/scripts, macros, links, and executable-looking content.

F001 is nevertheless reliability-critical because it can create false fatal identity collisions from valid repository state and can discard authoritative lifecycle metadata during canonical ingestion.

## Traceability Findings

PASS for existing execution/evidence traceability; BLOCKED for semantic acceptance by F001.

Relevant authority/evidence:

- FR-002; QR-001; QR-003;
- ADR-0003; ADR-0004; ADR-0005;
- DATA-SOURCE-0001;
- TECH-INGEST-0001;
- WP-MVP-0004;
- EXEC-0006 through EXEC-0009, all CLOSED;
- PR #217 implementation;
- PR #224 post-merge EOSV;
- current WP-MVP-0004 evidence EVID-0202 through EVID-0204 before this review-state transaction.

## Blocking Findings

### EOSR-WP-MVP-0004-F001 — Canonical YAML front matter is not authoritative for Markdown document identity/metadata

**Severity:** P1 / blocking acceptance

**Observed behavior:** a canonical review artifact with `artifact_id: "REV-WP-MVP-0003"` and H1 `# WP-MVP-0003 — Engineering Review` is parsed with explicit governed identifier `WP-MVP-0003`; front-matter status is omitted.

**Impact:** valid canonical review artifacts can collide with the Work Packets they review, and authoritative artifact identity/status metadata is lost. This violates FR-002, TECH-INGEST-0001, ADR-0003, and DATA-SOURCE-0001.

**Required bounded correction:**

1. recognize the repository's canonical top-of-document YAML front-matter metadata contract deterministically, at minimum `artifact_id` and `status`, with exact source ranges;
2. make a valid front-matter `artifact_id` authoritative explicit document identity for governed artifacts;
3. treat H1 governed IDs as identity fallback only when no authoritative explicit identity field is declared; an H1 target/reference must not conflict with a valid front-matter artifact ID;
4. if explicit front-matter identity is malformed, duplicated, or conflicts with another authoritative explicit-ID field, emit a source-located diagnostic and do not silently fall back to H1 identity;
5. preserve front-matter status as recognized metadata;
6. add focused regressions using review-style canonical artifacts and prove the review plus reviewed Work Packet do not produce a false duplicate-ID diagnostic;
7. preserve all existing code-fence/comment/execution/network safety and deterministic ordering/span behavior;
8. bump the Markdown parser contract version if required by the parser-version compatibility rule for changed canonical extraction semantics;
9. rerun full Rust validation, first-class EOSV evidence, and EOSR after the correction is integrated.

## Non-Blocking Findings

The existing EXEC-0009 note remains valid: the approved governed-identifier namespace allowlist will require intentional extension and regression coverage when new canonical namespaces are introduced. This is maintainability guidance, not a separate blocker for the present packet.

## Decision

**REJECTED.** WP-MVP-0004 must remain `IN_REVIEW` while `EOSR-WP-MVP-0004-F001` is corrected through bounded product work. Closure is not authorized. After the correction merges and evidence is refreshed, perform a fresh independent EOSR review before checklist reconciliation or `WP_CLOSE`.
