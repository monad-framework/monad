# Product Requirements

**Status:** Proposed MVP baseline  
**Release focus:** MVP Release 1

## Objective

Deliver the smallest local-first Monad implementation that compiles canonical engineering knowledge into a deterministic semantic model and makes that model useful for repository inspection, validation, query/explanation, and bounded AI-agent context.

## Functional requirements

### FR-001 — Discover a Monad repository

Monad MUST identify the repository/workspace root, effective configuration, supported canonical artifacts, and relevant toolchain/workspace structure.

**Acceptance:** repeated discovery of an unchanged reference repository yields equivalent identities/order; unsupported or malformed configuration produces actionable diagnostics.

### FR-002 — Ingest canonical engineering artifacts

Monad MUST parse supported canonical Markdown and structured configuration without requiring an LLM.

**Acceptance:** source path/hash, sections, metadata, stable identifiers, and references are preserved; malformed input cannot silently become valid semantic state.

### FR-003 — Construct the Monad Semantic Graph

Monad MUST represent supported engineering entities and typed relationships with deterministic identity and provenance.

**Acceptance:** equivalent input yields equivalent canonical graph; every derived node/edge can identify its source/rule; unresolved relationships remain explicit.

### FR-004 — Validate structural and semantic invariants

Monad MUST evaluate MVP rules for identity uniqueness, required metadata, reference resolution, authority/status consistency, machine-projection freshness, and other approved invariants.

**Acceptance:** findings have stable code, severity, source/entity, explanation, and remediation context; valid repositories pass deterministically.

### FR-005 — Query semantic relationships

Monad MUST support bounded graph queries needed by MVP, including references, dependents, governing artifacts, unresolved entities, and traceability gaps.

**Acceptance:** query results are stable for unchanged input and include provenance sufficient to inspect the canonical basis.

### FR-006 — Explain engineering meaning

Monad MUST explain why a supported artifact/entity exists or what governs/depends on it by traversing explicit graph relationships rather than inventing undocumented causal claims.

**Acceptance:** explanations enumerate the relationship/evidence path and distinguish missing knowledge from negative answers.

### FR-007 — Produce bounded agent context

Given a valid authorized Work Packet, Monad MUST produce a context package containing applicable scope, governing artifacts, constraints/prohibitions, relevant graph neighborhood, acceptance criteria, and validation commands while excluding unrelated content by default.

**Acceptance:** context-package membership is deterministic/explainable; excluded secret paths remain excluded; missing authority blocks an implementation-ready package.

### FR-008 — Expose an MVP CLI

Monad MUST expose a coherent local CLI for repository inspection, validation, graph/query, explanation, and context generation with human-readable and structured output where automation requires it.

**Acceptance:** commands use documented exit semantics, no-color/CI-safe behavior, stable machine schemas where declared, and actionable diagnostics.

### FR-009 — Preserve reproducibility evidence

Monad MUST record enough version/input/configuration identity to reproduce semantic output and diagnose divergence.

**Acceptance:** clean-clone conformance fixtures reproduce expected semantic snapshots and diagnostics across supported environments.

### FR-010 — Integrate without replacing native tools

Where MVP validation delegates to a native tool, Monad MUST expose the invocation/evidence and preserve the native result rather than reinterpreting a failure as success.

## Quality requirements

### QR-001 Determinism

Ordering, identity, canonical serialization, and diagnostics must not depend on filesystem enumeration order, wall-clock time, randomized IDs, or LLM output.

### QR-002 Performance

Reference budgets for startup, parse/graph build, query latency, and memory must be measured before release; regressions above approved thresholds fail the performance gate.

### QR-003 Security

The system follows least privilege/context, defends against path traversal/symlink and untrusted-input hazards, avoids executing repository content during inspection unless explicitly authorized, and produces no secret-bearing diagnostics/context by default.

### QR-004 Reliability

Partial/corrupt caches or generated state must be detectable and recoverable by rebuilding from canonical inputs.

### QR-005 Compatibility

MVP does not promise a stable public KIR/plugin API until versioning contracts are approved; any declared stable CLI/schema surface follows compatibility policy.

### QR-006 Operability

`doctor`/diagnostic paths must make configuration/toolchain/environment failures distinguishable from semantic repository failures.

### QR-007 Maintainability

Compiler/graph/query/context concerns have explicit boundaries and conformance fixtures so implementations can evolve without changing semantics accidentally.

## Release gate

MVP release requires all Must requirements to trace to approved specification rules and passing evidence; no unaccepted critical/high security or correctness risk; deterministic clean-clone demonstration; installation/usage docs; and Product Owner acceptance against `MVP-RELEASE-1.md`.