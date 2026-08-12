# Product Capabilities

**Status:** Proposed foundation baseline

Capabilities describe durable product abilities independent of one implementation language or interface. MVP Release 1 composes the first fourteen capabilities into one end-to-end semantic engineering loop.

## C-01 — Workspace intelligence

Discover repository roots, components, packages, configuration sources, artifact roots, toolchains, and supported project topology.

**MVP maturity:** deterministic discovery and inspection for the reference repositories, with clear diagnostics for ambiguity and unsupported structure.

## C-02 — Engineering artifact ingestion

Discover and read canonical engineering artifacts through explicit adapters and conventions without requiring all repositories to adopt a Monad-native format.

**MVP maturity:** source/configuration metadata plus core documentation/governance/specification/test artifact classes needed by acceptance scenarios.

## C-03 — Semantic identity and normalization

Assign stable identities, canonicalize supported representations, resolve aliases, preserve source coordinates, and detect collisions.

**MVP maturity:** deterministic identity for documents and core semantic entities across clean recompilation.

## C-04 — Monad Semantic Graph

Represent engineering entities and relationships with typed ontology, provenance, invariants, deterministic construction, and traversal.

**MVP maturity:** one versioned graph schema sufficient for requirements/decisions/specifications/components/dependencies/tests/work/evidence in the reference scenarios.

## C-05 — Kernel Intermediate Representation

Expose a canonical machine-oriented representation that downstream systems can validate, serialize, migrate, and consume without reparsing arbitrary source artifacts.

**MVP maturity:** charter, schema, canonical serialization, graph-to-KIR lowering, versioning, compatibility contract, and conformance fixtures.

## C-06 — Diagnostics and validation

Detect invalid configuration, unresolved or contradictory knowledge, graph invariant failures, stale generated projections, and tool/execution failures through structured diagnostics.

**MVP maturity:** stable diagnostic registry and deterministic negative/boundary acceptance coverage.

## C-07 — Query and explanation

Inspect semantic entities, traverse relationships, explain provenance and why relationships exist, and expose structured query output.

**MVP maturity:** entity lookup, relationship traversal, provenance explanation, selected coverage/gap queries, and machine-readable results.

## C-08 — Change impact and incrementality

Ingest Git/repository changes, calculate conservative affected sets, explain impact paths, and minimize recomputation without losing correctness.

**MVP maturity:** affected-set calculation and first incremental graph/validation path proven against a change corpus.

## C-09 — Execution planning

Turn authorized goals and affected knowledge into explicit dependency-ordered tasks with declared inputs, outputs, environment, cacheability, and verification expectations.

**MVP maturity:** serializable local execution-plan schema and deterministic plan construction for supported native-tool adapters.

## C-10 — Native tool orchestration

Invoke existing ecosystem tools in controlled subprocesses, preserve their evidence, and propagate failure/cancellation/retry semantics without reimplementing their mechanics.

**MVP maturity:** real tool adapters for the reference polyglot scenario, including plan inspection and evidence capture.

## C-11 — AI and agent context engineering

Select minimal task-relevant semantic context, package governing artifacts and acceptance criteria, enforce explicit capability/exclusion boundaries, and retain provenance.

**MVP maturity:** deterministic context packages suitable for bounded Codex tasks and review by a human maintainer.

## C-12 — Policy and authority

Represent and evaluate selected repository, governance, security, and work-authorization rules that affect whether a plan or agent action is permitted.

**MVP maturity:** enough authority awareness to distinguish canonical/generated sources and require explicit work/approval boundaries for the MVP engineering workflow.

## C-13 — Publication and project projection

Project canonical engineering knowledge into generated documentation, indexes, GitHub issues/project views, wiki pages, and other disposable human-facing views without creating a competing source of truth.

**MVP maturity:** synchronized machine documentation plus repository-controlled projection contracts for GitHub and docs.

## C-14 — Release and provenance

Package Monad, version public contracts, produce release evidence, retain source/toolchain/validation provenance, and support installation/upgrade/rollback.

**MVP maturity:** reproducible Release 1 package and release-readiness evidence.

## Post-MVP capabilities

### C-15 — Plugin and adapter ecosystem

Third-party extension manifests, capabilities, permissions, lifecycle, SDKs, compatibility, signing, and registry publication.

### C-16 — Remote cache and execution

Content-addressed remote cache, remote task execution, trust boundaries, scheduling, and result verification.

### C-17 — Team and hosted collaboration

Shared knowledge indexes, identity, authorization, synchronized team state, hosted control-plane services, and collaboration workflows.

### C-18 — Enterprise and commercial operations

Organization-wide governance, fleet insights, support/SLA controls, commercial packaging, and sustainable hosted services.

## Capability dependency model

```text
C-01 Workspace
      ↓
C-02 Artifact ingestion
      ↓
C-03 Identity/normalization
      ↓
C-04 Semantic Graph ───────────────┐
      ↓                            │
C-05 KIR                          │
      ↓                            │
C-06 Validation                   │
      ├──→ C-07 Query/explain     │
      ├──→ C-08 Impact/incrementality
      │          ↓                 │
      │       C-09 Planning        │
      │          ↓                 │
      │       C-10 Native execution
      │                            │
      └──→ C-11 Agent context ←────┘
                 ↑
          C-12 Policy/authority

C-13 Publication/project projection consumes the semantic model.
C-14 Release/provenance consumes execution and verification evidence.
```

## Maturity model

- **M0 — Named:** capability intent exists but behavior is unproven.
- **M1 — Bounded:** one supported end-to-end path with explicit limitations.
- **M2 — Reliable:** correctness, failure handling, recovery, and ownership are demonstrated against representative evidence.
- **M3 — Scalable:** performance, capacity, ecosystem variation, and operational repeatability are demonstrated.
- **M4 — Extensible:** controlled third-party or organizational variation is supported by stable contracts.

Release 1 targets M2 for the semantic kernel and primary local workflow, with M1 acceptable for secondary adapters and project/publication projections that are not on the critical correctness path.
