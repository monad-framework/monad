# Architecture Overview

**Status:** Proposed foundation baseline

## Architectural thesis

Monad is a local-first engineering knowledge compiler and orchestration runtime. Its deterministic core converts canonical repository artifacts into an explicit semantic model; downstream capabilities query, validate, explain, plan, publish, and execute from that model instead of independently reparsing unrelated files and reconstructing meaning.

## Primary pipeline

```text
Canonical repository knowledge
        ↓
Workspace discovery + artifact adapters
        ↓
Semantic extraction + normalization
        ↓
Stable identity + provenance resolution
        ↓
Monad Semantic Graph (MSG)
        ↓
Kernel Intermediate Representation (KIR)
        ↓
┌─────────────┬───────────────┬──────────────┬──────────────┐
│ Validation  │ Query/explain │ Change impact│ Agent context │
└─────────────┴───────────────┴──────────────┴──────────────┘
                         ↓
                  Execution planner
                         ↓
                 Native tool adapters
                         ↓
                Local execution runtime
                         ↓
        diagnostics + evidence + artifacts
                         ↓
               canonical knowledge update
```

The pipeline may execute incrementally, but incremental results must be semantically equivalent to a correct full rebuild under the same declared inputs.

## Five architectural planes

### 1. Knowledge Plane

Owns the model of what the engineering system *means*.

Responsibilities include workspace/artifact discovery, semantic extraction, identity, provenance, ontology, graph construction, KIR, indexes, query semantics, and machine-readable knowledge representations.

It does not execute consequential development commands or grant authority to agents.

### 2. Control Plane

Owns what work *should happen* and whether it is allowed.

Responsibilities include configuration resolution, policy/authority evaluation, affected-set calculation, execution-plan construction, capability boundaries, work authorization, cache-validity decisions, and compatibility gates.

It consumes the Knowledge Plane and produces explicit decisions/plans rather than side effects.

### 3. Execution Plane

Owns controlled side effects.

Responsibilities include native-tool adapters, subprocess isolation, dependency-ordered execution, concurrency, cancellation, retry, output capture, cache interaction, and artifact materialization.

The Execution Plane executes only explicit approved plans/capabilities; it does not invent semantic intent.

### 4. Observation Plane

Owns evidence about what happened.

Responsibilities include structured diagnostics, logs, traces, metrics, execution records, provenance, performance evidence, debug bundles, conformance results, and release evidence.

Observation must not become an uncontrolled secondary store for repository secrets or sensitive payloads.

### 5. Interaction Plane

Owns how humans, automation, and AI systems access Monad.

Responsibilities include CLI, future TUI/IDE integration, machine output, agent context packages, GitHub projection, documentation/publication, and APIs.

The Interaction Plane presents or invokes underlying semantics; it is not itself the source of truth.

## Core domain boundaries

### Workspace

Represents the repository or repository set being inspected, including configuration, component/package discovery, toolchains, canonical artifact roots, Git state, and local Monad state.

### Artifact

Represents a canonical or generated engineering record with identity, classification, source location, hash, ownership/authority metadata where known, and adapter provenance.

### Semantic Entity and Relationship

Represent meaning extracted or declared from artifacts. Every derived object carries provenance sufficient for explanation and invalidation.

### Semantic Graph

The canonical relational model used for dependency, governance, traceability, impact, coverage, and context queries.

### KIR

A versioned canonical machine representation suitable for deterministic downstream consumption without reparsing arbitrary human formats.

### Diagnostic

A structured finding with stable identity, severity, affected location/entity, cause context, remediation, and provenance.

### Execution Plan

A serializable DAG of authorized tasks with declared dependencies, inputs, outputs, environment, cacheability, and verification expectations.

### Evidence

A durable, attributable record proving or contradicting an engineering claim, execution outcome, validation condition, or release gate.

## Local-first deployment shape

MVP Release 1 favors one cohesive local executable/process boundary with clean internal modules rather than prematurely distributed services. The filesystem, Git repository, configuration, and installed native toolchains are the primary local dependencies.

Potential internal modules include:

```text
workspace
artifacts/adapters
identity
provenance
semantic-graph
kir
diagnostics
query
impact
policy
planner
execution
cache
context
cli
observability
```

The language/runtime for the mature core requires an accepted ADR. Architectural modules should not be conflated with repositories or services before evidence justifies separation.

## Deterministic boundary

The following belong inside the deterministic boundary for Release 1:

- workspace and artifact discovery;
- parsing of supported deterministic formats;
- normalization and canonicalization;
- stable identity and hashing;
- graph construction and invariants;
- KIR lowering/serialization;
- deterministic diagnostics;
- query semantics;
- affected-set calculation;
- execution-plan derivation from explicit rules;
- cache-validity decisions;
- conformance and reproducibility checks.

LLM inference is outside this boundary. AI-generated suggestions may become canonical only after normal review/authority processes.

## Security model at the architecture level

Repository content is untrusted input. Paths, symlinks, configuration, templates, code blocks, plugins, command declarations, and external tool output may attempt to influence execution or context generation.

The architecture therefore separates **knowledge acquisition** from **execution authority**. Reading a file that says “run this command” does not authorize execution. A command reaches the Execution Plane only through supported adapters, explicit planning rules, policy checks, and user/work authorization appropriate to consequence.

Agent context similarly follows explicit inclusion and exclusion rules. The fact that a secret or unrelated file is graph-reachable does not authorize disclosure.

## Consistency and incrementality

A full semantic compilation defines correctness. Incremental computation maintains indexes from observed changes and invalidates dependent semantic nodes, queries, plans, and cache entries according to explicit dependency rules.

When Monad cannot prove that an incremental result is complete, it expands invalidation or falls back to a broader recomputation. Performance uncertainty must not become silent correctness risk.

## Failure model

Failures are classified rather than flattened:

- invalid repository/configuration;
- unsupported artifact/format;
- parse/extraction failure;
- identity collision;
- unresolved required relationship;
- graph invariant violation;
- policy/authority denial;
- plan construction uncertainty;
- unavailable native tool;
- native-tool failure;
- cancellation/timeout;
- cache corruption/invalidity;
- internal defect.

Unknown semantic or execution state is represented explicitly and enters reconciliation or conservative fallback.

## Architecture evolution

### Phase A — Semantic kernel

Workspace → artifacts → identity/provenance → graph → KIR → validation/query.

### Phase B — Executable knowledge

Change impact → incrementality → planning → cache → native execution → evidence.

### Phase C — Human/AI operating system

Agent context/capabilities, work-packet integration, policy, GitHub/project projections, documentation/publication, self-hosting workflows.

### Phase D — Distributed ecosystem

Plugins, registry, remote cache/execution, team indexes, hosted control plane, enterprise governance.

## Architecture quality test

A proposed component, service, repository, protocol, or dependency is justified only when its responsibility is clear, its authority/data boundaries are explicit, its failure modes are understood, and it strengthens the knowledge → control → execution → evidence loop. Complexity without a user/engineering outcome is rejected or deferred.
