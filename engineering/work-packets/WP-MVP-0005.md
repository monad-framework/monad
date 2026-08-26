# WP-MVP-0005 — Structured Monad configuration parser

**Status:** AUTHORIZED
**Epic:** EPIC-003  
**Feature:** F-003-03  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0002  
**Product Goal:** PG-001

## Objective

Represent canonical `monad.toml` as a provenance-rich semantic input after bootstrap validation, without creating a competing configuration authority.

## Governing authority

- FR-001, FR-002; QR-001, QR-003
- ADR-0002, ADR-0003, ADR-0004
- IFC-WORKSPACE-0001
- DATA-SOURCE-0001
- TECH-INGEST-0002
- ADR-0005

## Dependencies

- WP-MVP-0001 is CLOSED and supplies valid effective configuration and precedence semantics.
- WP-MVP-0003 is CLOSED and supplies stable source/document identity and provenance.
- ADR-0005 is Accepted and authorizes the MVP Rust implementation topology and `monad-core` semantic boundary.
- WC-MVP-0002 is ACTIVE and supplies the current parsing/reference-resolution execution context.

These historical prerequisite blockers are satisfied. This packet does not reimplement configuration precedence. Prerequisite completion alone did not make the packet Ready, authorized, or started; those lifecycle transitions require separate governed EOS gates.

## Acceptance criteria

- [ ] US-015 valid `monad.toml` becomes a deterministic semantic document record.
- [ ] US-016 schema/parse errors remain diagnostics and block a valid semantic config document.
- [ ] US-017 normalized semantic representation is deterministic and retains source/effective-value provenance distinctions.
- [ ] `.monad/manifest.yaml` cannot override or become a competing semantic config source.
- [ ] no environment interpolation, command substitution, network lookup, or include execution occurs.

## Implementation boundary

Under ADR-0005, semantic config adaptation belongs in the ingestion/config modules of `monad-core`; bootstrap loader semantics from WP-MVP-0001 are reused rather than duplicated.

## Validation

Golden config corpus for canonical repository config, malformed/unknown/unsupported keys, override provenance, deterministic representation, and legacy-manifest non-authority.

## Authorization disposition

The prior dependency block is cleared by canonical closure/acceptance evidence for WP-MVP-0001 and WP-MVP-0003 plus the Accepted ADR-0005. This packet was adopted into canonical EOS lifecycle control, passed `WP_READY` (`DRAFT → READY`), and has now passed the separate `WP_AUTHORIZE` gate (`READY → AUTHORIZED`). The next permitted lifecycle action is the separate EOSE start transition. Execution preparation, start, product mutation, and implementation remain prohibited until that governed start transition passes and is recorded.
