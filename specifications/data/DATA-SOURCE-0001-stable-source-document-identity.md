# DATA-SOURCE-0001: Stable Source and Document Identity

**Status:** approved  
**Version:** 1.0.0  
**Owner:** Monad Core  
**Related requirements:** FR-002, FR-003, FR-009, QR-001  
**Governing ADR:** ADR-0003

## Purpose

Defines the canonical identity/provenance fields emitted before semantic graph construction.

## Canonical model

Each source record MUST contain:

- `source_id` — deterministic identity derived from source kind + canonical repository-relative path;
- `canonical_path` — root-relative `/`-separated path;
- `source_kind` — declared/supported parser kind;
- `content_sha256` — lowercase SHA-256 of exact consumed bytes;
- `byte_length`;
- `parser_contract` — parser/specification identity/version used to interpret bytes;
- discovery provenance sufficient to explain selection.

A parsed document additionally contains `document_id`, `document_kind`, and explicit governed identifier when present.

## Normative rules

1. Source IDs MUST be identical across clean clones with equivalent canonical paths/kinds.
2. Content edits MUST change `content_sha256` but MUST NOT change Source ID solely because bytes changed.
3. A path move changes Source ID. If the document has an explicit governed ID, its Document ID survives the move while source provenance changes.
4. Explicit governed identifiers MUST be unique in their namespace for a valid semantic compilation.
5. Duplicate governed IDs MUST produce a fatal identity-collision diagnostic naming all known source locations; traversal order MUST NOT select a winner.
6. Path case is preserved in identity. Discovery MUST diagnose cross-platform case-collision risk where two configured canonical paths differ only by case.
7. IDs MUST NOT include absolute clone path, timestamps, random data, inode/device numbers, Git branch name, or network identity.
8. Machine serialization MUST preserve original identity components/provenance and use deterministic field/order conventions.

## Security/data

Paths and source bytes are repository-local engineering data. Diagnostics SHOULD use repository-relative paths and MUST NOT leak unrelated absolute host paths when a relative location is sufficient.

## Verification

Property/golden tests cover clone relocation, content edit, path move, explicit-ID move, duplicate ID, case collision, symlink alias, empty file, and stable serialized records.
