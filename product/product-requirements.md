# Product Requirements

**Status:** Expanded product baseline  
**Release focus:** MVP Release 1 plus governed post-MVP capability expansion

## Objective

Deliver a local-first Monad implementation that compiles canonical engineering knowledge into a deterministic semantic model and evolves that model into a governed engineering operating system for human and bounded-agent inspection, validation, query/explanation, execution planning, automation, observability, deployment, and ecosystem integration.

MVP Release 1 remains the first release gate. Post-MVP requirements are commitments to the product direction, not authorization to bypass the current rolling-wave backlog, Work Packet, ADR, specification, security, or evidence gates.

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

Monad MUST evaluate approved rules for identity uniqueness, required metadata, reference resolution, authority/status consistency, machine-projection freshness, policy, and other governed invariants.

**Acceptance:** findings have stable code, severity, source/entity, explanation, and remediation context; valid repositories pass deterministically.

### FR-005 — Query semantic relationships

Monad MUST support bounded graph queries including references, dependents, governing artifacts, unresolved entities, and traceability gaps.

**Acceptance:** query results are stable for unchanged input and include provenance sufficient to inspect the canonical basis.

### FR-006 — Explain engineering meaning

Monad MUST explain why a supported artifact/entity exists or what governs/depends on it by traversing explicit graph relationships rather than inventing undocumented causal claims.

**Acceptance:** explanations enumerate the relationship/evidence path and distinguish missing knowledge from negative answers.

### FR-007 — Produce bounded agent context

Given a valid authorized Work Packet, Monad MUST produce a context package containing applicable scope, governing artifacts, constraints/prohibitions, relevant graph neighborhood, acceptance criteria, and validation commands while excluding unrelated content by default.

**Acceptance:** context-package membership is deterministic/explainable; excluded secret paths remain excluded; missing authority blocks an implementation-ready package.

### FR-008 — Expose a coherent CLI

Monad MUST expose a coherent local CLI for repository inspection, validation, graph/query, explanation, context generation, diagnostics, and later approved execution/automation capabilities with human-readable and structured output where automation requires it.

### FR-009 — Preserve reproducibility evidence

Monad MUST record enough version/input/configuration identity to reproduce semantic output and diagnose divergence.

### FR-010 — Integrate without replacing native tools

Where validation or execution delegates to a native tool, Monad MUST expose the invocation/evidence and preserve the native result rather than reinterpreting a failure as success.

### FR-011 — Measure workspace intelligence

Monad MUST provide an explainable 0–100 workspace-intelligence score with explicit maturity tiers derived from governed evidence across memory/knowledge, agent intelligence, execution/automation, health, and governance dimensions.

**Acceptance:** score inputs, weights, tier thresholds, historical changes, and missing evidence are inspectable and reproducible.

### FR-012 — Unify memory, intelligence, and execution

Monad MUST support a unified workspace-intelligence model in which governed memory informs bounded agent reasoning, reasoning may propose or trigger authorized execution, and execution produces provenance-rich memory/evidence.

### FR-013 — Maintain anti-hallucination engineering memory

Agent-facing memory MUST distinguish canonical fact, derived fact, proposal, uncertain inference, stale knowledge, and contradiction; multiple agents may contribute evidence but cannot silently promote probabilistic output to canonical truth.

### FR-014 — Orchestrate dependency-aware agent work

Monad MUST be able to dispatch bounded developer-agent work through an explicit dependency graph, with concurrency, cancellation, resource limits, authorization, and evidence capture. Autonomous orchestration MUST begin behind an explicit experimental capability gate.

### FR-015 — Enforce progressive autonomy

Agents MUST operate under named autonomy levels beginning with advisory behavior. Promotion to stronger execution authority MUST require objective reliability evidence, explicit policy, and reversible human approval. Operators remain decision stewards for unresolved authority, risk, architecture, and release decisions.

### FR-016 — Support cross-harness review

Monad MUST support independent parallel review by multiple configured agent/model harnesses, preserve reviewer provenance, surface disagreement, and prevent reviewer consensus from overriding canonical human/governance authority.

### FR-017 — Route AI work by capability, cost, and policy

Monad MUST support multiple AI providers and local models through a provider-neutral contract and route work using declared capability, complexity, privacy, cost, latency, and policy constraints.

### FR-018 — Provide a governed automation and integration layer

Monad MUST provide a resource model, adapter contract, and reactive workflow model for external systems. The ecosystem MUST be able to grow to a broad catalog of pre-built integrations without embedding third-party semantics into the core.

### FR-019 — Automate verified pull-request lifecycle operations

Monad MUST be able to create pull requests from verified completed work under explicit policy, isolated worktrees/branches, rebase-first integration rules where configured, and complete evidence linkage. Automatic PR creation MUST NOT imply automatic merge authority.

### FR-020 — Produce signed change attestations

Monad MUST support DSSE-compatible signed attestations for governed changes and release evidence, including policy that can require valid attestations before protected-branch integration.

### FR-021 — Support cryptographic agility and strong identity

Monad MUST support versioned cryptographic profiles capable of Ed25519, P-256, secp256k1, and post-quantum ML-DSA where appropriate; multi-party approval/signature policies; key rotation; and WebAuthn/passkey-backed identity for hosted or privileged control surfaces. No single algorithm becomes permanent semantic authority.

### FR-022 — Defend agent and prompt boundaries

Monad MUST detect or contain prompt-injection attempts, mask secrets in logs/context/output, sandbox agent capabilities, enforce least authority, and prohibit unapproved tool/resource escalation.

### FR-023 — Provide declarative governance, change control, and audit

Monad MUST support declarative quality/autonomy/compliance policies, formal governed resources, Definition-of-Ready and Definition-of-Done gates, change submission/review/approval/rollback, and a complete tamper-evident audit trail linking humans, agents, decisions, executions, evidence, and resulting artifacts.

### FR-024 — Provide operational health and execution observability

Monad MUST expose knowledge-graph health, stale/zombie/decaying relationships, agent execution history, input context, output diff, verification results, duration, token/cost data where available, and OpenTelemetry-compatible logs/metrics/traces.

### FR-025 — Support privacy-governed hosted analytics

Where a hosted/public surface is enabled, Monad MAY provide opt-in visitor/session analytics including traffic source, coarse geography, device class, and usage behavior. Analytics MUST be separable from the local core and governed by privacy/data-retention policy.

### FR-026 — Support deployable shared experiences

Approved hosted surfaces MUST support automated deployment, shareable endpoints, custom domains, access controls, and optional gallery/registry publication without making hosting mandatory for core operation.

### FR-027 — Clone and restore complete workspace state

Monad MUST support provenance-preserving cloning/templates of a complete governed workspace configuration and one-step restoration of prior versioned states where the underlying canonical source permits it.

### FR-028 — Support enterprise deployment modes

Monad MUST support a path to air-gapped/no-exfiltration operation, on-premises deployment, and optional AWS/GCP/Azure deployment without making any cloud provider mandatory.

### FR-029 — Provide reproducible environment profiles

Monad MUST support container and Nix-based environment profiles where required to reproduce builds, validation, agent execution, and release evidence.

### FR-030 — Manage governed files and media

Monad MUST support content-addressed upload/storage/reference of documents and media needed by engineering workflows, with provenance, classification, retention, access policy, and explicit controls over AI processing.

### FR-031 — Provide MCP and IDE integration surfaces

Monad MUST provide an MCP server and an LSP/IDE integration path so external clients can query, navigate, validate, explain, and request bounded context without redefining semantic authority.

### FR-032 — Provide an extensible plugin ecosystem

Monad MUST establish versioned plugin SDK, registry, and curated pack contracts. Plugins remain explicit capabilities with provenance, compatibility, permission, and signature policy.

### FR-033 — Support pluggable graph/vector storage

The architecture MUST permit local-first defaults plus versioned adapters for graph/vector backends such as Neo4j, Neptune, JanusGraph, pgvector, Pinecone, and Weaviate when scale or deployment requirements justify them.

### FR-034 — Support multi-vector memory and semantic/result-aware caching

Monad MUST be able to represent multiple vector spaces for code, data, and business/engineering semantics and cache embeddings/completions/results with explicit tenant/workspace isolation, provenance, invalidation, and privacy boundaries.

### FR-035 — Support optional external runtime compatibility profiles

The adapter architecture MUST permit optional compatibility profiles for external bytecode/runtime ecosystems. An EVM bytecode-compatibility profile MAY be implemented as an isolated adapter, but it MUST NOT contaminate or redefine Monad core semantics.

### FR-036 — Support deterministic parallel execution and scale benchmarks

Monad MUST support dependency/conflict-aware parallel execution of independent internal work and define benchmark profiles for throughput and state finalization. A long-range benchmark target is at least 10,000 lightweight scheduler/graph operations per second on declared reference hardware, and eligible local control-state transitions SHOULD finalize within 400 ms p95 once their inputs are available. External tool/network latency is excluded from these internal targets.

## Quality requirements

### QR-001 — Determinism

Ordering, identity, canonical serialization, diagnostics, policy decisions, and reproducible execution records must not depend on filesystem enumeration order, wall-clock time, randomized IDs, or ungoverned LLM output.

### QR-002 — Performance

Reference budgets for startup, parse/graph build, query latency, context generation, execution scheduling, state finalization, and memory must be measured on declared reference profiles; regressions above approved thresholds fail the applicable performance gate.

### QR-003 — Security

The system follows least privilege/context, defends against path traversal/symlink and untrusted-input hazards, avoids executing repository content during inspection unless explicitly authorized, and produces no secret-bearing diagnostics/context by default.

### QR-004 — Reliability

Partial/corrupt caches or generated state must be detectable and recoverable by rebuilding from canonical inputs. Remote calls and agent orchestration use bounded retries, exponential backoff where safe, idempotency semantics, and circuit breakers to prevent cascading failure.

### QR-005 — Compatibility

Stable KIR/configuration/CLI/plugin/registry/MCP/LSP/adapter surfaces MUST use explicit versioning and compatibility policies before external stability is promised.

### QR-006 — Operability

Doctor/diagnostic paths must distinguish configuration/toolchain/environment, semantic-repository, provider, integration, policy, security, and deployment failures.

### QR-007 — Maintainability

Compiler/graph/query/context/policy/execution/observation/integration concerns have explicit boundaries and conformance fixtures so implementations can evolve without changing semantics accidentally.

### QR-008 — Progressive trust

Agent trust is earned from evidence and can be demoted. No agent begins with hard-mandatory or unrestricted authority.

### QR-009 — Cryptographic agility

Attestation and identity mechanisms must permit algorithm/version rotation, post-quantum migration, multi-party policies, and revocation without rewriting semantic history.

### QR-010 — Auditability

Consequential human/agent actions, decisions, state transitions, policy evaluations, attestations, and execution results must be reconstructable from durable evidence and tamper-evident logs.

### QR-011 — Prompt and secret safety

Untrusted instructions must not silently expand capability. Secret material must be minimized, detected/masked where feasible, and excluded from shared caches and agent context unless explicitly authorized.

### QR-012 — Observability

Operational components must expose structured logs, metrics, and traces through OpenTelemetry-compatible boundaries where applicable, with correlation to Work Packets/executions/evidence.

### QR-013 — Portability

The local core remains usable offline. Optional deployment surfaces support major developer platforms, containers, Nix, air-gapped/on-prem operation, and multiple clouds through explicit compatibility profiles.

### QR-014 — Provider independence

No single AI provider, hosted graph database, cloud vendor, or automation vendor is required for canonical core operation.

### QR-015 — High-throughput scalability

Parallel internal execution, graph operations, caching, and observation paths must scale by measured evidence. The 10,000-operations/second target in FR-036 is a stretch benchmark, not permission to weaken determinism, safety, or external-tool authority.

### QR-016 — Local state finalization

Eligible local governed state transitions should meet the 400 ms p95 target from FR-036 on declared reference profiles; slower transitions must remain correct, observable, and explicitly reported rather than falsely finalized.

### QR-017 — Resilience

External providers/integrations use bounded retry, exponential backoff, circuit breakers, timeout/cancellation, and failure isolation appropriate to idempotency and side-effect risk.

### QR-018 — Modular-first evolution

Monad modularizes stable contracts before repository/service splitting. Ecosystem repositories and distributed services are introduced only when ownership, deployment, scaling, or compatibility evidence justifies them.

### QR-019 — Privacy and tenant isolation

Hosted analytics, vector memory, caches, files, integrations, and agent records must maintain explicit workspace/tenant boundaries, retention rules, and data-classification policy.

### QR-020 — Accessibility of evidence

Dashboards, scores, automation, and AI summaries cannot become the sole source of truth; users must be able to reach the underlying governed evidence and explanations.

## Release gates

### MVP Release 1

MVP Release 1 remains governed by `MVP-RELEASE-1.md`. New post-MVP capabilities do not expand the MVP merely because they are now planned.

### Post-MVP expansion

A post-MVP capability may enter execution only when its Epic/Feature/Work Packet is refined, governing ADR/specification authority is explicit, threat/privacy implications are dispositioned, exact validation/evidence requirements exist, and parent lifecycle gates authorize execution.
