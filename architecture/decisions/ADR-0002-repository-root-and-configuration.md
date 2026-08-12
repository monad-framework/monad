# ADR-0002: Canonical Repository Root and Configuration

**Status:** Accepted  
**Date:** 2026-08-12  
**Decision scope:** MVP repository discovery and semantic configuration  
**Related:** FR-001, QR-001, QR-003, QR-006

## Context

Monad must be able to start from an arbitrary path inside a repository and determine, without executing project code or consulting remote state, which Monad repository it is operating on and which semantic configuration governs the run. The repository currently contains transitional `.monad/manifest.yaml` metadata, while the target architecture has long treated a root `monad.toml` as the intended human-authored configuration surface.

If root identity can be inferred from Git alone, environment-dependent state, or multiple competing configuration files, the same working tree can compile differently across machines. That violates the local-first and reproducibility principles.

## Decision

1. `monad.toml` at the repository root is the canonical human-authored Monad repository configuration and the primary Monad-root marker.
2. Root discovery starts at the explicitly supplied path, or the current working directory when none is supplied, resolves it to an absolute lexical starting point, and walks ancestors toward the filesystem root. The nearest ancestor containing a valid `monad.toml` is the selected Monad root.
3. A Git repository without `monad.toml` is not automatically a Monad repository.
4. Nested Monad repositories are valid boundaries: nearest-root selection prevents an invocation inside a nested repository from silently binding to an outer repository.
5. MVP semantic configuration precedence is: built-in documented defaults < root `monad.toml` < explicit command-line overrides. Environment variables may provide operational inputs or secrets but MUST NOT silently alter semantic configuration.
6. Unknown keys, duplicate keys, unsupported schema versions, invalid types, and values that violate the configuration schema produce diagnostics. Monad does not silently repair or ignore semantically meaningful invalid configuration.
7. The effective configuration is explainable: structured output must identify each effective value and whether it came from a default, `monad.toml`, or explicit CLI override.
8. `.monad/` is reserved for compatibility, generated, cached, or local operating state unless a future accepted decision says otherwise. `.monad/manifest.yaml` is a legacy bootstrap record and is not a competing canonical configuration source.
9. A future `monad.lock` may record resolved deterministic state, but lock semantics are outside this ADR and require their own specification before use as authority.

## Initial canonical configuration

The stabilization branch introduces a minimal `monad.toml` describing repository identity and canonical artifact roots. It is intentionally small; new semantic keys require specification rather than ad-hoc growth.

## Consequences

### Positive

- one obvious root marker and configuration source;
- deterministic root selection in nested directory scenarios;
- reproducible configuration that does not depend on ambient shell state;
- direct dogfooding by this repository;
- `.monad/` remains available for rebuildable/internal state without creating two editable truths.

### Negative

- existing bootstrap-only repositories using `.monad/manifest.yaml` need migration;
- configuration additions require schema/version discipline;
- environment-driven convenience is intentionally constrained for semantic settings.

## Compatibility and migration

For stabilization tooling only, `.monad/manifest.yaml` may remain readable as legacy metadata. MVP runtime behavior MUST NOT treat it as equivalent to `monad.toml`. A missing `monad.toml` should produce a repository-not-found or migration diagnostic rather than silently promoting the legacy manifest.

## Verification

Conformance fixtures must cover: invocation at root and descendants, nested Monad repositories, no marker, malformed TOML, unknown schema version, duplicate/unknown keys, CLI override provenance, and repeated runs producing equivalent effective configuration.
