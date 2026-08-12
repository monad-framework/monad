# TECH-INGEST-0003: Local Reference Resolution

**Status:** approved  
**Version:** 1.0.0  
**Owner:** Monad Core  
**Related requirements:** FR-002, FR-003, FR-004, QR-001, QR-003  
**Governing ADRs:** ADR-0003, ADR-0004

## Purpose

Defines deterministic resolution of local reference candidates extracted from supported canonical artifacts. It emits typed relation candidates for semantic graph construction while preserving unresolved/ambiguous references explicitly.

## Reference classes in MVP

- explicit governed artifact identifiers such as ADR, specification, PI/WC/WP, Epic/Feature/Story identifiers;
- repository-relative Markdown/file links to configured canonical sources;
- same-document anchors where needed for provenance/explanation;
- external URLs as external/unresolved reference records, not fetched semantic truth.

## Normative behavior

1. Resolution operates over the complete discovered/parsed MVP source index, never first-match filesystem traversal.
2. Governed-ID references resolve by exact namespace + identifier. Missing IDs remain unresolved; duplicate target IDs produce ambiguity/collision diagnostics.
3. File references resolve lexically from the referring source path, normalize `.` segments, reject root escape, and match canonical configured source paths.
4. References to excluded/noncanonical files may be recorded as noncanonical targets but MUST NOT silently promote those files into canonical semantic sources.
5. External URLs MUST NOT be fetched during resolution. They remain typed external reference records with source provenance.
6. Every relation candidate records referring source/document, source range when available, raw reference text, normalized target key, resolution state, relation-hint/rule identifier, and target identity when resolved.
7. Resolution states are at least `resolved`, `unresolved`, `ambiguous`, `external`, and `noncanonical`.
8. Candidate/result ordering MUST be deterministic by referring identity, source range, relation/rule key, and normalized target key.
9. Absence of a resolvable target MUST NOT be rewritten as a negative semantic claim. Later validation determines whether unresolved references are allowed or errors for that artifact contract.

## Security

Resolution MUST reject path traversal outside repository root and MUST NOT dereference network locations or execute target content.

## Verification

Fixtures cover valid/missing/duplicate governed IDs, relative paths, anchors, excluded targets, `..` traversal, external URLs, duplicate filenames in different directories, case collisions, and randomized input ordering.
