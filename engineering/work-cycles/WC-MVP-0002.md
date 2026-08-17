# WC-MVP-0002 — Parsing and Reference Resolution

**Status:** AUTHORIZED
**Program Increment:** PI-MVP-001  
**Forecast:** 2026-08-24 through 2026-08-30  
**Sprint Goal:** Parse canonical repository inputs into deterministic provenance-rich records and resolve local references without execution, network access, or semantic inference.

## Objective

Establish the deterministic ingestion boundary above workspace discovery and stable identity: parse canonical Markdown engineering artifacts and canonical Monad configuration into provenance-rich structural records and reference candidates, then resolve local governed identifiers and canonical file references against the complete source index.

## Included Work Packets

- `WP-MVP-0004` — Markdown engineering artifact parser.
- `WP-MVP-0005` — Structured Monad configuration parser.
- `WP-MVP-0006` — Local reference resolution.

Only one Work Packet is authorized at a time unless an explicit EOS WIP exception is approved.

## Governing Authority

- `product/PRODUCT-GOAL.md`
- `product/MVP-RELEASE-1.md`
- `architecture/decisions/ADR-0002-repository-root-and-configuration.md`
- `architecture/decisions/ADR-0003-stable-source-and-document-identity.md`
- `architecture/decisions/ADR-0004-safe-deterministic-ingestion-boundary.md`
- `architecture/decisions/ADR-0005-mvp-core-implementation-topology.md`
- `specifications/interfaces/IFC-WORKSPACE-0001-repository-root-and-effective-configuration.md`
- `specifications/data/DATA-SOURCE-0001-stable-source-and-document-identity.md`
- `specifications/technical/TECH-INGEST-0001-markdown-engineering-artifact-parsing.md`
- `specifications/technical/TECH-INGEST-0002-structured-monad-configuration-parsing.md`
- `specifications/technical/TECH-INGEST-0003-local-reference-resolution.md`

## Entry Criteria

- `PI-MVP-001` is ACTIVE.
- `WC-MVP-0001` is CLOSED with an accepted Work Cycle Review.
- `WP-MVP-0001` through `WP-MVP-0003` are CLOSED with accepted evidence.
- `ADR-0005` is Accepted and the MVP implementation topology is authoritative.
- The stable repository/configuration, workspace-discovery, and source/document-identity contracts needed by this cycle are implemented and verified.

## Execution Policy

- Work Cycle status does not authorize child Work Packets automatically.
- EOS must authorize each Work Packet independently before EOSE execution.
- Parser and resolver behavior must remain deterministic, provenance-rich, non-executing, and network-independent.
- Markdown parsing must not execute HTML, scripts, macros, MDX, remote includes, or repository code.
- Configuration parsing must reuse canonical bootstrap/effective-configuration semantics rather than introduce a competing authority.
- Reference resolution must preserve missing, ambiguous, external, excluded, and noncanonical targets explicitly rather than inventing traversal-order winners.
- Semantic graph materialization and natural-language semantic inference remain outside this Work Cycle.

## Exit Criteria

- `WP-MVP-0004` through `WP-MVP-0006` are CLOSED with accepted evidence, or unfinished packets are explicitly replanned under EOSP without weakening quality gates.
- Markdown and structured-configuration parsing is deterministic and source-located across positive, negative, malformed, security, Unicode, and reproducibility fixtures.
- Local governed-ID and canonical-file reference resolution is deterministic against the complete source index and preserves unresolved/ambiguous/external/noncanonical states explicitly.
- No parser/resolver path executes repository code, scripts, macros, includes, network fetches, or environment/command interpolation.
- Work Cycle Review records the Sprint Goal disposition.
- Retrospective records at least one actionable process/system improvement or explicitly records that no change is warranted based on evidence.

## Review Evidence

Closure evidence belongs in `engineering/reviews/WC-MVP-0002-REVIEW.md` and first-class EOSV evidence records. Scheduling alone is never closure evidence.
