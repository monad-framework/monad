# ADR-0003: Stable Source and Document Identity

**Status:** Accepted  
**Date:** 2026-08-12  
**Decision scope:** canonical source/document identity and provenance  
**Related:** FR-002, FR-003, FR-009, QR-001, QR-005

## Context

Monad's semantic graph, diagnostics, references, KIR, cache keys, and agent context all depend on stable identity. Content hashes alone are not identity because an ordinary edit would create a new semantic entity. Absolute filesystem paths are not identity because clones live at different locations. Human identifiers such as `ADR-0001` are valuable but not every source has one and they can collide if governance fails.

## Decision

1. Every ingested source has a **Source ID** derived from its canonical repository-relative path and source kind. Absolute clone location, filesystem enumeration order, timestamps, inode numbers, and random values are excluded.
2. Canonical paths use `/` separators, contain no leading slash, `.` or `..` segments, and are interpreted relative to the selected Monad root.
3. Source identity preserves path case. Discovery MUST separately diagnose path sets that are unsafe or ambiguous across supported case-insensitive filesystems rather than silently case-folding identity.
4. A **Document ID** uses an explicit governed identifier when the artifact contract defines one (for example `ADR-0001`, `WP-MVP-0001`, or a specification ID). Otherwise it derives from Source ID plus the document kind.
5. Stable governed identifiers are unique within their identifier namespace. Duplicate explicit IDs are fatal semantic diagnostics for the affected compilation; Monad does not pick a winner based on traversal order.
6. Content identity is separate provenance. Each source records a SHA-256 digest of the exact bytes consumed plus canonical path, source kind, and parser/schema version sufficient to explain the semantic result.
7. Renaming a path changes Source ID unless the document has an explicit stable governed identifier. For explicitly identified artifacts, the governed Document ID survives a location move while provenance records the changed source path.
8. Symlink aliases do not create additional source identities. Discovery resolves containment and ingests at most the canonical configured repository path; aliases/cycles are diagnosed or de-duplicated deterministically.
9. Identity encodings used in machine schemas must be reversible or carry the original canonical components; lossy slugification is not authoritative identity.

## Consequences

- ordinary content edits retain source/document identity where path/explicit ID is stable;
- repository clones produce equivalent identities;
- governed artifact moves retain logical identity when an explicit ID exists;
- path-only sources intentionally receive new Source IDs when moved;
- duplicate IDs become visible defects rather than order-dependent behavior.

## Verification

Golden/property tests must cover unchanged clones, content edits, renames, explicit-ID moves, duplicate identifiers, path separator normalization, case-collision diagnostics, symlink aliases/cycles, and SHA-256 provenance changes.
