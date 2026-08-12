# WP-MVP-0001 — Repository identity and effective configuration

**Status:** Ready — not Authorized  
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
- `architecture/decisions/ADR-0005-mvp-core-implementation-topology.md`
- `specifications/interfaces/IFC-WORKSPACE-0001-repository-root-and-effective-configuration.md`

## Dependencies

All semantic and implementation-topology dependencies required for this packet are resolved. ADR-0005 is Accepted. This packet is Ready but remains inactive until explicit EOS authorization.

## In scope

- initial Cargo workspace scaffolding required by ADR-0005;
- `crates/monad-core` workspace/config modules;
- minimal `crates/monad-cli` bootstrap wiring required to exercise the boundary;
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
- remote config, plugins, package-manager execution, or network access;
- EOS implementation under `tools/eos`/`scripts/eos`.

## Authorized implementation boundary after EOS authorization

Product changes are limited to:

- root `Cargo.toml`, `Cargo.lock`, and toolchain/config files needed for the accepted Rust workspace;
- `crates/monad-core/**` for workspace/config semantics and focused fixtures/tests;
- `crates/monad-cli/**` only for minimal argument/bootstrap presentation needed to invoke the core boundary;
- narrowly related documentation/evidence required by the Definition of Done.

No additional crate, service, plugin boundary, hosted dependency, or unrelated refactor is authorized by this packet.

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

## Required validation commands

The implementing branch MUST make the following commands pass from repository root:

```bash
cargo fmt --all -- --check
cargo clippy --workspace --all-targets --all-features -- -D warnings
cargo test --workspace --all-targets --all-features
python3 scripts/sync-machine-docs.py --check
./scripts/eos verify --strict
```

Focused tests/fixtures MUST additionally cover root discovery, nested roots, precedence/provenance, malformed TOML, unsupported schema version, unknown semantic keys, missing root, deterministic structured output, and the no-execution/no-network boundary.

## Ready disposition

This packet satisfies its current Definition-of-Ready boundary: governing ADR/specification authority is explicit, implementation scope is bounded, acceptance behavior is testable, and exact validation commands are defined.

**Do not begin implementation until `./scripts/eos authorize WP-MVP-0001` succeeds after PR #158 is merged and the post-merge repository ruleset has been applied/verified.**
