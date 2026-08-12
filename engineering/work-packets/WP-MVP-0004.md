# WP-MVP-0004 — Markdown engineering artifact parser

**Status:** Refined — blocked from Ready by WP-MVP-0003 and ADR-0005  
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
- proposed ADR-0005

## Dependencies

WP-MVP-0003 provides stable source/document identity. ADR-0005 establishes implementation topology.

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
