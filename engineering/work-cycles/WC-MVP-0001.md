# WC-MVP-0001 — Workspace, Discovery, and Identity

**Status:** AUTHORIZED
**Program Increment:** PI-MVP-001  
**Forecast:** 2026-08-17 through 2026-08-23  
**Sprint Goal:** Discover repository/workspace knowledge with stable identity.

## Objective

Establish the deterministic repository bootstrap boundary for Monad MVP Release 1: identify a Monad repository, resolve effective configuration, discover supported canonical workspace inputs safely, and assign stable source/document identity with provenance.

## Included Work Packets

- `WP-MVP-0001` — Repository identity and effective configuration — **Ready**.
- `WP-MVP-0002` — Deterministic workspace discovery — Refined; becomes Ready only after its dependency and governing-contract gates pass.
- `WP-MVP-0003` — Stable source/document identity — Refined; becomes Ready only after its dependency and governing-contract gates pass.

Only one Work Packet is authorized at a time unless an explicit EOS WIP exception is approved.

## Governing Authority

- `product/PRODUCT-GOAL.md`
- `product/MVP-RELEASE-1.md`
- `architecture/decisions/ADR-0002-repository-root-and-configuration.md`
- `architecture/decisions/ADR-0003-stable-source-and-document-identity.md`
- `architecture/decisions/ADR-0004-safe-deterministic-ingestion-boundary.md`
- `architecture/decisions/ADR-0005-mvp-core-implementation-topology.md`
- `specifications/interfaces/IFC-WORKSPACE-0001-repository-root-and-effective-configuration.md`
- `specifications/technical/TECH-WORKSPACE-0001-deterministic-workspace-discovery.md`
- `specifications/data/DATA-SOURCE-0001-stable-source-and-document-identity.md`

## Entry Criteria

- Foundation stabilization M-000 is complete.
- PI-MVP-001 is authorized under the accepted stabilization baseline.
- ADR-0005 is Accepted.
- `WP-MVP-0001` passes its Ready gate with exact Rust/Cargo validation commands.
- Main-branch governance/ruleset setup is active or has an explicitly recorded Project Authority disposition.

## Execution Policy

- Work Cycle status does not authorize child Work Packets automatically.
- EOS must authorize each Work Packet independently before EOSE execution.
- Canonical engineering artifacts remain authoritative over GitHub projections and `.eos/` control state.
- No network access, repository-code execution, or post-MVP generalization is introduced through the workspace bootstrap boundary unless separately authorized.

## Exit Criteria

- WP-MVP-0001 through WP-MVP-0003 are closed with accepted evidence, or unfinished packets are explicitly replanned under EOSP without weakening quality gates.
- Deterministic root/config/discovery/identity behavior is demonstrated against positive, negative, boundary, and reproducibility fixtures.
- Work Cycle Review records the Sprint Goal disposition.
- Retrospective records at least one actionable process/system improvement or explicitly records that no change is warranted based on evidence.

## Review Evidence

Closure evidence belongs in `engineering/reviews/WC-MVP-0001-REVIEW.md` and first-class EOSV evidence records. Scheduling alone is never closure evidence.
