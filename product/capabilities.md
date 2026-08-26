# Product Capabilities

**Status:** Expanded product baseline

## Core semantic capabilities

### C-01 — Repository and workspace discovery

Identify repository/workspace roots, configuration, packages/modules, canonical artifact locations, toolchains, and supported inputs deterministically.

### C-02 — Canonical knowledge ingestion

Read supported human-authored artifacts, preserve source provenance, normalize metadata/identifiers/references, and reject or diagnose malformed input.

### C-03 — Semantic graph compilation

Construct stable engineering entities and typed relationships spanning requirements, decisions, specifications, components, dependencies, work, tests, evidence, releases, and provenance.

### C-04 — KIR and canonical interchange

Lower validated semantic knowledge into canonical machine representations suitable for deterministic downstream consumption, caching, diff, and compatibility.

### C-05 — Diagnostics and conformance

Evaluate structural/semantic invariants, policies, and specification conformance and return stable actionable diagnostics.

### C-06 — Query, traversal, and explanation

Query graph state, traverse relationships, explain why/what-governs/what-depends, and retain the evidence path supporting the answer.

### C-07 — Change impact and incrementality

Relate repository changes to semantic entities and derive minimal invalidation, validation, and execution scope.

### C-08 — Native tool orchestration

Plan and invoke native compilers, formatters, linters, tests, build tools, infrastructure tools, and other adapters through explicit capability contracts.

### C-09 — AI/agent context and governance

Select minimal authorized context, express scope/prohibitions/acceptance, record provenance, and support bounded AI collaboration without granting unbounded authority.

### C-10 — Policy and governance

Represent/evaluate engineering rules, ownership, architectural constraints, readiness/done gates, exceptions, autonomy strategies, and acceptance gates against semantic state.

### C-11 — Documentation and projection

Generate or validate machine companions, publication views, status, GitHub projections, dashboards, and other derived artifacts from canonical knowledge.

### C-12 — Extensibility and ecosystem

Support adapters, plugins, registries, SDKs, packs, and multi-repository evolution through stable contracts.

### C-13 — Release and provenance

Create traceable release evidence linking source, resolved inputs, semantic state, tests, artifacts, compatibility, signatures, attestations, and approval evidence.

## Living workspace intelligence

### C-14 — Workspace intelligence scoring

Compute an explainable 0–100 workspace-intelligence score and maturity tier from governed evidence across knowledge/memory, agent intelligence, automation/execution, health, and governance.

### C-15 — Unified memory–intelligence–execution loop

Maintain a governed feedback loop in which canonical memory informs bounded reasoning, authorized reasoning triggers execution, and execution creates provenance-rich memory/evidence.

### C-16 — Anti-hallucination memory and knowledge health

Distinguish canonical, derived, proposed, uncertain, stale, contradictory, and superseded knowledge; identify zombie/stale nodes and degrading relationships; and expose health indicators without inventing completeness.

### C-17 — Multi-vector memory and intelligent caching

Support multiple vector spaces for code, data, and engineering/business semantics plus semantic/result-aware caches with isolation, provenance, invalidation, and privacy rules.

## Governed agent execution

### C-18 — Autonomous dependency-aware orchestration

Dispatch bounded agent work through dependency graphs with explicit authority, concurrency, cancellation, budgets, evidence capture, and experimental autonomy gates.

### C-19 — Progressive autonomy and operator stewardship

Support named autonomy levels from advisory to stronger policy-governed execution, evidence-based promotion/demotion, and explicit human decision stewardship for unresolved authority/risk.

### C-20 — Cross-harness verification

Run independent parallel reviewers, preserve reviewer provenance, surface disagreements, and require governed disposition rather than treating model consensus as authority.

### C-21 — Cost/capability-aware AI routing

Route AI work across multiple hosted or local providers according to capability, complexity, policy, privacy, cost, and latency.

### C-22 — Agent resilience controls

Provide retry/idempotency, exponential backoff, timeout/cancellation, circuit breakers, execution budgets, and failure isolation for agent/provider workflows.

## Automation, integrations, and resources

### C-23 — Integration adapter framework

Provide versioned resource and adapter contracts for external systems and a scalable integration catalog without embedding third-party semantics in the core.

### C-24 — Intelligent automation workflows

Support reactive/event-driven workflows that can adapt within explicit policy and generate durable evidence/memory from their outcomes.

### C-25 — Verified pull-request automation

Create PRs from verified bounded work using isolated worktrees/branches, configurable rebase-first policy, and complete Work Packet/execution/evidence traceability.

## Security, identity, governance, and audit

### C-26 — Signed attestations and cryptographic agility

Produce DSSE-compatible change/release attestations and support rotating cryptographic profiles including conventional and post-quantum signatures.

### C-27 — Multi-party trust and key lifecycle

Support multi-party approval/signature policies, key rotation/revocation, migration, and quantum-transition planning.

### C-28 — RBAC and passkey identity

Provide RBAC, passkey/WebAuthn-backed identity, session/access policy, and password-protected shared surfaces where deployment mode requires them.

### C-29 — Agent and prompt security

Detect/contain prompt-injection attempts, mask secrets, sandbox capabilities, apply least authority, and prevent unapproved tool/resource escalation.

### C-30 — Change control and immutable audit

Provide formal change submission/review/approval/rollback/restore and tamper-evident audit records linking people, agents, decisions, policies, executions, evidence, and artifacts.

## Observation and operations

### C-31 — OpenTelemetry and health observation

Expose correlated structured logs, metrics, traces, graph-health indicators, stale/decay signals, and operational health through OpenTelemetry-compatible boundaries.

### C-32 — Agent execution analytics

Record execution inputs, selected context, output diffs, verification, duration, token/cost data, failures, and resulting evidence.

### C-33 — Privacy-governed hosted analytics

For optional hosted/public surfaces, provide opt-in traffic/source/geography/device/usage analytics isolated from the local semantic core.

## Deployment and workspace lifecycle

### C-34 — Instant/shared deployment

Support automated deployment of approved surfaces with shareable endpoints, custom domains, access controls, and optional gallery/registry publication.

### C-35 — Workspace cloning and restoration

Clone/templates of complete governed workspace state with provenance and restore prior versioned states through canonical version control.

### C-36 — Enterprise deployment modes

Support air-gapped/no-exfiltration, on-premises, and optional AWS/GCP/Azure deployment profiles.

### C-37 — Reproducible environments

Support Docker/container and Nix environment profiles for repeatable validation, execution, and release evidence.

### C-38 — Governed file and media handling

Provide content-addressed file/media ingestion, storage/reference, provenance, classification, retention, access controls, and AI-processing policy.

## Developer and ecosystem surfaces

### C-39 — MCP server

Expose bounded semantic query/context/validation capabilities through a governed Model Context Protocol server.

### C-40 — LSP and IDE integration

Expose diagnostics, navigation, semantic relationships, explanations, and bounded actions through LSP/IDE integration surfaces.

### C-41 — Plugin SDK, registry, and packs

Provide versioned plugin SDK, registry/discovery, curated packs, compatibility, provenance, signature, and permission contracts.

### C-42 — Pluggable graph/vector storage

Support local-first storage plus adapters for external graph/vector systems when scale/deployment evidence requires them.

### C-43 — External runtime compatibility profiles

Permit isolated adapter-defined compatibility with external bytecode/runtime ecosystems, including an optional EVM bytecode profile, without redefining Monad semantic truth.

## Performance and scale

### C-44 — Deterministic parallel execution

Schedule independent internal work in parallel using dependency/conflict analysis while preserving deterministic evidence/state ordering.

### C-45 — High-throughput and fast-finalization benchmark profiles

Maintain declared benchmark profiles including a long-range target of at least 10,000 lightweight internal scheduler/graph operations per second and eligible local governed-state transitions at or below 400 ms p95 once inputs are available.

## Capability boundary

MVP Release 1 directly requires C-01 through foundations of C-13 as defined by `MVP-RELEASE-1.md`. C-14 through C-45 form the governed post-MVP capability roadmap. Their presence in the product baseline does not authorize implementation or expand MVP scope automatically.
