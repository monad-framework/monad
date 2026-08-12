# TECH-INGEST-0001: Markdown Engineering Artifact Parsing

**Status:** approved  
**Version:** 1.0.0  
**Owner:** Monad Core  
**Related requirements:** FR-002, QR-001, QR-003  
**Governing ADRs:** ADR-0003, ADR-0004

## Purpose

Defines the MVP parser contract for canonical Markdown engineering artifacts. The parser extracts deterministic structural facts and reference candidates; it does not infer undocumented semantics with an LLM.

## Input

A UTF-8 source record satisfying DATA-SOURCE-0001 and classified as Markdown.

## Output

The normalized document record MUST preserve:

- source/document identity and content provenance;
- ordered heading/section structure with source ranges;
- recognized metadata fields expressed by the artifact contract;
- explicit governed identifiers and statuses where present;
- Markdown links and repository/artifact identifier reference candidates;
- diagnostics with source ranges for malformed/ambiguous governed constructs.

## Normative behavior

1. Parsing MUST be side-effect free, offline, and deterministic.
2. CommonMark/GFM-compatible syntax MAY be accepted, but the exact parser dialect/version used for canonical extraction MUST be recorded as parser contract metadata.
3. Heading hierarchy and textual source ranges MUST be preserved sufficiently for diagnostics/explanation.
4. Code-fence contents MUST NOT be scanned as ordinary governed identifiers or links unless an artifact-specific rule explicitly opts in.
5. HTML/comments MAY carry metadata only when an approved artifact contract defines it; arbitrary executable HTML/script semantics are ignored as text/structure.
6. A syntactically valid Markdown document can still be semantically invalid; the parser MUST separate parse findings from later semantic validation.
7. Recoverable malformed constructs MAY yield partial structure for diagnostics, but invalid recovered fields MUST NOT be represented as accepted semantic facts.
8. Link/reference extraction emits candidates only. Resolution is governed by TECH-INGEST-0003.
9. Output ordering follows source order for source-ordered constructs and canonical key order for map-like machine fields.

## Security

The parser MUST NOT execute embedded HTML, scripts, code fences, include directives, shell substitutions, links, or macros.

## Verification

Fixtures include nested headings, repeated headings, metadata, fenced code containing fake IDs, relative links, artifact IDs, HTML comments, malformed links/metadata, Unicode, empty files, and repeat-run byte-equivalent normalized output.
