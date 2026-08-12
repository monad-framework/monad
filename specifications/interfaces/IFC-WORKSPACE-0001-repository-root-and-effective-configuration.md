# IFC-WORKSPACE-0001: Repository Root and Effective Configuration

**Status:** approved  
**Version:** 1.0.0  
**Owner:** Monad Core  
**Related requirements:** FR-001, QR-001, QR-003, QR-006  
**Governing ADR:** ADR-0002

## Purpose and scope

This specification defines how the MVP identifies a Monad repository, parses `monad.toml`, applies deterministic overrides, and explains effective configuration. It does not define future lockfile semantics, remote configuration, plugin configuration, or hosted policy distribution.

## Definitions

- **Invocation path:** explicit `--root`/path input, otherwise current working directory.
- **Monad root:** nearest ancestor containing a valid root `monad.toml`.
- **Semantic configuration:** values capable of changing discovered inputs or compiled semantic output.
- **Effective configuration:** validated defaults plus file values plus explicit CLI overrides, with provenance.

## Normative behavior

1. Root discovery MUST walk from invocation path toward the filesystem root and select the nearest ancestor containing `monad.toml`.
2. Discovery MUST NOT infer Monad membership solely from `.git`, `.monad`, `.eos`, package-manager files, or source-language manifests.
3. If no `monad.toml` exists in the ancestor chain, discovery MUST return a stable repository-not-found diagnostic and non-success result.
4. `schema_version` MUST be present and supported. MVP supports integer version `1`.
5. `[project].id` MUST be a non-empty stable identifier matching `^[a-z0-9][a-z0-9._-]*$`; `[project].name` MUST be non-empty.
6. Artifact include patterns and exclude paths MUST be repository-relative and MUST NOT escape root.
7. Unknown semantic keys MUST produce a diagnostic. Implementations MUST NOT silently ignore a key merely because they cannot act on it.
8. Semantic precedence is defaults < `monad.toml` < explicit CLI override. Environment variables MUST NOT alter semantic values in MVP.
9. Effective-configuration output MUST provide normalized value plus provenance source (`default`, `monad.toml:<location>`, or `cli`).
10. Ordering of maps, diagnostics, and emitted effective-configuration records MUST be canonical and independent of parser/hash-map/filesystem order.
11. Sensitive operational values, if later admitted, MUST be redacted from diagnostics and explanation output by default.

## Failure behavior

Malformed TOML, duplicate keys, unsupported schema version, invalid path patterns, invalid project identity, and contradictory settings are errors. A parser MAY report multiple independent findings in one run, but MUST NOT publish an effective semantic configuration when a fatal configuration error exists.

## Compatibility

Adding an optional key with deterministic default is backward compatible within schema version 1 only when it cannot reinterpret an existing key. Renaming/removing keys or changing semantics requires schema/version impact and migration guidance.

## Verification

Required fixtures: root invocation, descendant invocation, nested roots, missing marker, malformed TOML, schema mismatch, invalid project ID, unknown key, invalid escaping path, CLI override, environment non-interference, and stable structured output. Repeated runs over identical inputs MUST be byte-equivalent for declared canonical structured output.
