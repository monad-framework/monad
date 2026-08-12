# WP-MVP-0001 — Repository identity and effective configuration

**Status:** Refined — blocked from Ready by ADR-0005  
**Epic:** EPIC-002  
**Feature:** F-002-01  
**Program Increment:** PI-MVP-001  
**Work Cycle:** WC-MVP-0001  
**Product Goal:** PG-001

## Objective

Implement the deterministic bootstrap boundary that locates a Monad repository, validates `monad.toml`, produces effective configuration with provenance, and emits actionable failures without executing repository code.

## Governing authority

- `product/MVP-RELEASE-1.md`
- `product/product-requirements.md` — FR-001; QR-001, QR-003, QR-006
- `architecture/decisions/ADR-0002-repository-root-and-configuration.md`
- `architecture/decisions/ADR-0004-safe-deterministic-ingestion-boundary.md`
- `specifications/interfaces/IFC-WORKSPACE-0001-repository-root-and-effective-configuration.md`
- Proposed implementation topology: `architecture/decisions/ADR-0005-mvp-core-implementation-topology.md`

## Dependencies

Semantic dependencies are resolved. Implementation authorization is blocked only until ADR-0005 is accepted or replaced by another accepted implementation-topology decision.

## In scope

- root discovery from explicit/current path;
- nearest `monad.toml` semantics and nested root behavior;
- schema-v1 TOML validation;
- defaults/file/CLI precedence and provenance;
- effective configuration model and explanation-ready structured representation;
- stable diagnostics for missing root and invalid configuration;
- unit/golden/conformance fixtures for IFC-WORKSPACE-0001.

## Out of scope

- `monad.lock` semantics;
- general artifact discovery (WP-MVP-0002);
- semantic ingestion of configuration into the graph pipeline (WP-MVP-0005);
- environment variables changing semantic configuration;
- remote config, plugins, package-manager execution, or network access.

## Implementation boundary

If ADR-0005 is accepted, authorized product changes are limited to initial Cargo workspace scaffolding plus workspace/config modules in `crates/monad-core`, minimal CLI/bootstrap wiring in `crates/monad-cli`, root `Cargo.toml`/lock/toolchain files as needed, and focused tests/fixtures. EOS implementation under `tools/eos` is not in scope.

## Acceptance criteria

- [ ] US-002: invocation at root/descendant detects the nearest valid Monad root.
- [ ] US-003: schema-v1 configuration resolves with documented precedence.
- [ ] US-004: effective configuration is explainable with value provenance.
- [ ] no `monad.toml` yields a stable repository-not-found diagnostic.
- [ ] malformed/unsupported/unknown semantic config cannot become valid state silently.
- [ ] environment differences do not change semantic configuration in conformance tests.
- [ ] nested Monad-root fixtures bind to the nearest root.
- [ ] repository code/network is never executed during bootstrap.
- [ ] repeated structured output for identical inputs is byte-equivalent where declared canonical.

## Validation commands

Exact language commands become binding with ADR-0005. Minimum evidence MUST include targeted unit tests, root/config golden fixtures, malformed-input tests, and `python3 scripts/sync-machine-docs.py --check` for canonical-document changes.

## Authorization gate

Do not run `./scripts/eos authorize WP-MVP-0001` until ADR-0005 is Accepted and this packet's implementation boundary is updated from conditional to authoritative.
