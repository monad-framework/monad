# TECH-INGEST-0002: Structured Monad Configuration Parsing

**Status:** approved  
**Version:** 1.0.0  
**Owner:** Monad Core  
**Related requirements:** FR-001, FR-002, QR-001, QR-003  
**Governing ADRs:** ADR-0002, ADR-0004

## Purpose

Defines semantic ingestion of `monad.toml` as a structured engineering source after bootstrap configuration resolution. It intentionally distinguishes the narrow bootstrap loader needed to establish the repository from the semantic document representation used by later graph/query/provenance features.

## Normative behavior

1. Input is the exact root `monad.toml` bytes plus the effective validated configuration established under IFC-WORKSPACE-0001.
2. The parser MUST preserve source identity, SHA-256 provenance, schema version, project identity, artifact-root definitions, ingestion controls, exclusions, and source ranges where the TOML parser exposes them reliably.
3. Semantic representation MUST use normalized types and deterministic key ordering without discarding the original source provenance.
4. Unknown/invalid semantic keys are configuration diagnostics; they MUST NOT appear as valid semantic configuration facts.
5. The semantic representation MUST distinguish explicit source values from defaults and CLI overrides. CLI overrides are effective-run provenance, not edits to the canonical `monad.toml` document.
6. `.monad/manifest.yaml` is not a second input to this parser and MUST NOT override `monad.toml`.
7. Parsing performs no environment interpolation, command substitution, file include, network lookup, or executable extension.

## Failure behavior

When bootstrap validation fails, no valid semantic configuration document is emitted. Diagnostics may still reference parse/source locations. Unsupported schema versions are explicit errors.

## Verification

Golden fixtures cover the canonical repository config, defaults, explicit overrides, unknown/duplicate keys, unsupported versions, malformed TOML, provenance, and deterministic machine serialization.
