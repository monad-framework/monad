# Product Constraints

**Status:** Proposed stabilization baseline

## PC-001 — Local-first core

Repository discovery, semantic compilation, validation, query/explain, and MVP context generation must operate without mandatory hosted services.

## PC-002 — Deterministic semantic core

Equivalent supported inputs/configuration/Monad version must produce equivalent canonical semantic identity and output. Probabilistic AI output cannot define core graph truth.

## PC-003 — Human-readable canonical source

MVP assumes human-readable Git artifacts are canonical. Machine companions are generated derivatives with source hashes/provenance.

## PC-004 — Git-native history

Monad does not replace Git history/branching/PR review. It may enrich and validate them.

## PC-005 — Native-tool authority

Language compilers, package managers, test runners, formatters, and other domain tools remain authoritative for their native semantics unless an accepted adapter contract says otherwise.

## PC-006 — Bounded AI authority

Agents must receive explicit scope and may not silently accept architecture, specifications, risk, or releases.

## PC-007 — Explainability

Consequential diagnostics, graph relationships, context selections, and policy/execution decisions must retain enough provenance to explain their basis.

## PC-008 — Security and secret minimization

Repository ingestion and context generation must honor exclusions, data classification, and least-context principles; secrets are never considered ordinary engineering context.

## PC-009 — Polyglot evolution

The architecture must not hard-code one implementation language/toolchain as the product model. MVP implementation may choose a narrow stack while interfaces remain explicit.

## PC-010 — Bootstrap resource discipline

The project should prefer best-of-breed open-source dependencies and avoid unnecessary paid infrastructure/API requirements for the local core.

## PC-011 — Backward-compatible evolution

Public schemas, KIR, configuration, CLI structured output, plugin APIs, and registry protocols must establish explicit versioning before external stability is promised.

## PC-012 — No false completeness

Unsupported constructs, incomplete graph knowledge, and uncertain relationships must be visible rather than guessed into a complete-looking model.