# Goals

**Status:** Proposed stabilization baseline

## G-001 — Compile engineering knowledge

Transform supported canonical engineering artifacts into stable machine-readable semantic structures with source provenance.

## G-002 — Build a trustworthy semantic graph

Represent engineering entities and typed relationships so important dependencies, authority, evidence, ownership, and provenance are queryable.

## G-003 — Explain engineering state

Answer useful `what`, `why`, `governed-by`, `depends-on`, `verified-by`, and `affected-by` questions without requiring users to reconstruct the repository manually.

## G-004 — Make validation semantic

Detect missing, stale, contradictory, invalid, or non-conforming engineering knowledge with actionable diagnostics.

## G-005 — Coordinate native tools incrementally

Derive minimal execution plans from semantic change and dependency state while leaving language/build/test tools authoritative for their own mechanics.

## G-006 — Govern AI-assisted engineering

Produce minimal, authorized, provenance-rich context packages and evidence expectations for ChatGPT, Codex, and future agents.

## G-007 — Remain local-first and reproducible

Make the core repository-understanding/validation loop fully useful without mandatory SaaS connectivity and reproduce equivalent outputs from equivalent inputs.

## G-008 — Keep project knowledge alive

Enable documentation, GitHub projections, status, traceability, and release evidence to derive from canonical engineering reality rather than drift independently.

## G-009 — Scale through stable contracts

Design clear internal boundaries, schemas, adapters, and extension points so additional repositories, languages, plugins, registries, and hosted services can emerge without destabilizing the core.

## G-010 — Dogfood Monad

Use Monad increasingly to understand, validate, plan, and coordinate its own development as the relevant capabilities become trustworthy.

## Prioritization rule

MVP work prioritizes G-001 through G-007. Later goals may shape architecture but may not inflate MVP unless they remove a release-blocking risk.