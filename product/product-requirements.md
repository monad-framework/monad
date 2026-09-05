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

Given governed engineering intent, a planning subject, or a valid authorized Work Packet, Monad MUST produce a bounded context package containing applicable scope, governing artifacts with their authority/status, lifecycle state, constraints/prohibitions, relevant graph neighborhood, dependencies, unresolved decisions, relevant evidence, acceptance criteria, and validation commands while excluding unrelated content by default. The context package MUST preserve enough provenance and classification to distinguish canonical, derived, proposed, stale, contradictory, and merely informative material. When that context is used for governed execution, its authoritative inputs MUST be incorporated by identity into the bound Execution Envelope rather than treated as independent execution authority.

**Acceptance:** context-package membership and source basis are deterministic/explainable where deterministic semantics apply; excluded secret paths remain excluded; planning context may exist before execution authorization, but missing authority blocks an implementation-ready executable package; material governing-context drift after a run is bound is detectable by the execution-governance boundary.

### FR-008 — Expose a coherent CLI

Monad MUST expose a coherent local CLI for repository inspection, validation, graph/query, explanation, context generation, diagnostics, and later approved execution/automation capabilities with human-readable and structured output where automation requires it.

### FR-009 — Preserve reproducibility evidence

Monad MUST record enough version/input/configuration identity to reproduce semantic output and diagnose divergence.

### FR-010 — Integrate without replacing native tools

Where validation or execution delegates to a native tool, Monad MUST expose the invocation/evidence and preserve the native result rather than reinterpreting a failure as success. A consequential native-tool invocation that claims governed execution MUST be requested through the applicable capability/policy-mediated execution boundary rather than bypassing it.

**Acceptance:** denied or unavailable authority prevents the governed effect before invocation; native results remain attributable to the requesting run/operation and are preserved as evidence without semantic rewriting.

### FR-011 — Measure workspace intelligence

Monad MUST provide an explainable 0–100 workspace-intelligence score with explicit maturity tiers derived from governed evidence across memory/knowledge, agent intelligence, execution/automation, health, and governance dimensions.

**Acceptance:** score inputs, weights, tier thresholds, historical changes, and missing evidence are inspectable and reproducible.

### FR-012 — Unify memory, intelligence, and execution

Monad MUST support a unified workspace-intelligence model in which governed memory informs bounded human and agent reasoning; reasoning MAY proactively identify next useful engineering actions, propose adaptive pathways, surface ambiguity, request clarification, recommend decisions, or request execution through the governed execution boundary; and authorized execution produces provenance-rich memory/evidence. Reasoning output remains non-binding until the applicable native decision, approval, authority, policy, and lifecycle requirements are satisfied.

### FR-013 — Maintain anti-hallucination engineering memory

Agent-facing memory MUST distinguish canonical fact, derived fact, proposal, decision, approval, evidence/observation, uncertain inference, stale knowledge, and contradiction; multiple agents may contribute evidence but cannot silently promote probabilistic output to canonical truth. Verification, review, operational, and execution evidence MAY change future recommendations or planning inputs while retaining its actual provenance and authority classification rather than silently rewriting governing engineering meaning.

### FR-014 — Orchestrate dependency-aware agent work

Monad MUST be able to propose, sequence, and dispatch bounded developer-agent work through an explicit dependency graph, with concurrency, cancellation, resource limits, authorization, and evidence capture. AI-driven planning MAY identify dependency-aware next actions and parallelizable work, but emergent work outside authorized scope MUST route to EOSP or EOSC rather than being silently absorbed into execution. Each governed executable unit MUST be bound to explicit execution authority and capabilities; delegation or subagent creation MUST NOT broaden those grants. Autonomous orchestration MUST begin behind an explicit experimental capability gate.

### FR-015 — Enforce progressive autonomy

Agents MUST operate under named autonomy profiles supporting at least AI-assisted, AI-driven, and bounded AI-autonomous operation, beginning without unrestricted execution authority. Promotion to stronger execution authority MUST require objective evidence relevant to the class of work being delegated, explicit policy, bounded scope, observable behavior, and reversible human approval or delegation. Autonomy MUST be revocable and MUST constrain capabilities, resource boundaries, approval thresholds, and escalation rules applied at the governed execution boundary rather than acting as an executor-controlled preference. Trust earned for one materially distinct class of work MUST NOT automatically authorize another. Operators remain decision stewards for unresolved authority, risk, architecture, security, irreversible, and release decisions.

### FR-016 — Support cross-harness review

Monad MUST support governed independent review by multiple configured agent/model/human review participants, preserve reviewer provenance, surface disagreement, and prevent reviewer consensus or any individual executor's self-report from overriding canonical human/governance authority or verification-controlled completion. Required independence MUST be evaluated according to policy and MUST NOT be satisfied merely by invoking the same executor, model, provider, harness, or materially identical review context a second time.

### FR-017 — Route AI work by capability, cost, and policy

Monad MUST support multiple AI providers and local models through a provider-neutral contract and route work using declared capability, complexity, privacy, cost, latency, and policy constraints. Routing MAY select a model, provider, or agent harness but MUST NOT modify the governing Execution Envelope or broaden granted authority as a side effect of selection.

### FR-018 — Provide a governed automation and integration layer

Monad MUST provide a resource model, adapter contract, and reactive workflow model for external systems. The ecosystem MUST be able to grow to a broad catalog of pre-built integrations without embedding third-party semantics into the core.

### FR-019 — Automate verified pull-request lifecycle operations

Monad MUST be able to create pull requests from verified completed work under explicit policy, isolated worktrees/branches, rebase-first integration rules where configured, and complete evidence linkage. Automatic PR creation MUST NOT imply automatic merge authority.

### FR-020 — Produce signed change attestations

Monad MUST support DSSE-compatible signed attestations for governed changes and release evidence, including policy that can require valid attestations before protected-branch integration.

### FR-021 — Support cryptographic agility and strong identity

Monad MUST support versioned cryptographic profiles capable of Ed25519, P-256, secp256k1, and post-quantum ML-DSA where appropriate; multi-party approval/signature policies; key rotation; and WebAuthn/passkey-backed identity for hosted or privileged control surfaces. No single algorithm becomes permanent semantic authority.

### FR-022 — Defend agent and prompt boundaries

Monad MUST detect or contain prompt-injection attempts, mask secrets in logs/context/output, sandbox agent capabilities, enforce least authority, and prohibit unapproved tool/resource escalation. Untrusted executor input or private reasoning MUST NOT be able to expand an Execution Envelope, create capabilities, suppress mandatory policy checks, or convert a denied operation into an authorized effect.

### FR-023 — Provide declarative governance, change control, and audit

Monad MUST support declarative quality/autonomy/compliance policies, formal governed resources, Definition-of-Ready and Definition-of-Done gates, adaptive-pathway governance, change submission/review/approval/rollback, and a complete tamper-evident audit trail linking governed intent, compiled-context identity, proposed pathway and material rationale, material questions, humans, agents, decisions, approvals/denials, authorization, execution envelopes, capability/policy decisions, operations/effects, executions, evidence, verification, review, resulting artifacts, and acceptance. AI recommendations or pathway proposals MUST NOT create authority or bypass native EOS decision/change semantics.

### FR-024 — Provide operational health and execution observability

Monad MUST expose knowledge-graph health, stale/zombie/decaying relationships, agent execution history, proposed adaptive-pathway identity/rationale where persisted, compiled-context identity, autonomy profile, bound Execution Envelope identity, capability/policy decisions, mediated operation/effect history, material clarifications/decisions, checkpoints/escalations, governing-input drift, replanning events, input context, output diff, verification/review results, provider/harness identity where relevant, duration, token/cost data where available, and OpenTelemetry-compatible logs/metrics/traces.

### FR-025 — Support privacy-governed hosted analytics

Where a hosted/public surface is enabled, Monad MAY provide opt-in visitor/session analytics including traffic source, coarse geography, device class, and usage behavior. Analytics MUST be separable from the local core and governed by privacy/data-retention policy.

### FR-026 — Support deployable shared experiences

Approved hosted surfaces MUST support automated deployment, shareable endpoints, custom domains, access controls, and optional gallery/registry publication without making hosting mandatory for core operation.

### FR-027 — Clone and restore complete workspace state

Monad MUST support provenance-preserving cloning/templates of a complete governed workspace configuration and one-step restoration of prior versioned states where the underlying canonical source permits it.

### FR-028 — Support enterprise deployment modes

Monad MUST support a path to air-gapped/no-exfiltration operation, on-premises deployment, and optional AWS/GCP/Azure deployment without making any cloud provider mandatory.

### FR-029 — Provide reproducible environment profiles

Monad MUST support container and Nix-based environment profiles where required to reproduce builds, validation, agent execution, and release evidence. Governed execution MUST be able to bind or reference the applicable environment identity in its Execution Envelope and evidence when reproducibility policy requires it.

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

### FR-037 — Compile governed Execution Envelopes

Before a governed run begins, Monad MUST compile the bounded work intent and applicable canonical engineering knowledge into a versioned, immutable, content-addressed Execution Envelope that identifies the governing state, actor/executor, authority, capabilities/prohibitions, tools/environment constraints, acceptance criteria, verification obligations, approval/escalation rules, evidence obligations, and applicable resource limits.

**Acceptance:** equivalent governed inputs produce an equivalent canonical envelope identity; a material change to governing authority, policy, constraints, acceptance, or other envelope-defining input changes the envelope identity; a bound envelope cannot be silently mutated in place.

### FR-038 — Mediate governed execution through a fail-closed harness

Any consequential agent, automation, or tool effect that claims Monad-governed execution MUST be requested through the Governed Execution Harness or a semantically conforming boundary that evaluates the bound Execution Envelope, current policy/authority state, and explicit capabilities before allowing the effect.

**Acceptance:** missing, stale, ambiguous, denied, expired, or incompatible authority/capability state cannot be interpreted as permission; denied operations produce attributable diagnostics/evidence and no governed effect; successful effects remain attributable to the requesting run and operation.

### FR-039 — Support replaceable agent harnesses through a stable adapter contract

Monad MUST provide a versioned agent/executor harness adapter contract that permits materially different model-driven, scripted, or human-driven executors to consume the same governed execution semantics without becoming authoritative for policy, capability grants, evidence validity, verification, or EOS lifecycle state.

**Acceptance:** adapter compatibility is negotiated before a run is bound; an adapter unable to represent a mandatory envelope obligation fails explicitly rather than weakening governance; switching compatible adapters does not require changing canonical Monad authority semantics.

### FR-040 — Verify completion independently of executor claims

Executor-reported success or completion MUST be treated as a candidate terminal request, not authoritative completion. Monad MUST evaluate the bound acceptance criteria, verification obligations, required evidence, and approval gates before a governed run can become verified/complete or drive an authoritative EOS completion transition.

**Acceptance:** an executor cannot mark governed work complete solely by self-report; failed or missing verification prevents authoritative completion; verification results identify the obligations and evidence evaluated.

### FR-041 — Recover execution without losing governing identity

Monad MUST support bounded checkpoint, cancellation, resume/recovery, and governing-state drift handling for long-running or interruptible governed execution. Recovery MUST preserve or explicitly replace the bound Execution Envelope and MUST NOT silently resume under materially changed authority, policy, constraints, or acceptance obligations.

**Acceptance:** resumable state identifies the run, envelope, adapter/executor compatibility state where required, and relevant evidence; material governing drift causes suspension/recompilation, escalation, cancellation, or another explicit governed outcome rather than silent continuation.

### FR-042 — Evaluate harness and model combinations under governed conformance

Monad MUST support a verification/evaluation capability that can execute equivalent governed task fixtures against different compatible agent-harness/model combinations and measure requirement satisfaction, policy compliance, unauthorized-operation attempts, evidence/provenance completeness, verification outcome, reproducibility characteristics, cost/latency where available, and human intervention.

**Acceptance:** evaluation uses versioned fixtures and governed envelopes; results preserve the tested adapter/model/configuration identity; model or harness ranking cannot override canonical authority and does not itself grant production execution rights.

### FR-043 — Provide Adaptive AI-Driven Engineering Workflow Planning

Monad MUST produce an inspectable proposed engineering pathway from governed intent, repository context, lifecycle state, authority, policy, risk, complexity, uncertainty, reversibility, dependencies, unresolved decisions, available evidence, and the applicable autonomy profile. The pathway MAY adapt the breadth, ordering, and rigor of optional engineering activities, but MUST identify material questions and decision points, required authority/approval boundaries, expected verification and review obligations, and sufficient structured rationale for material changes in rigor. It MUST operate inside EOS and MUST NOT create a competing lifecycle, bypass mandatory EOS gates, silently broaden authorized scope, or infer authority from an AI recommendation.

When a proposed pathway reaches governed execution, the existing execution-governance requirements beginning with FR-037 continue to govern Execution Envelope compilation, mediated execution, executor compatibility, independent completion verification, and recovery.

**Acceptance:** a low-risk reversible change can receive a lightweight pathway without bypassing mandatory gates; material ambiguity produces an explicit clarification/decision route instead of an inferred consequential answer; security-sensitive or otherwise high-consequence work can increase required rigor and authority; material governing-input drift causes pathway reevaluation, replanning, suspension, or change control as applicable; a governed human denial is respected as an input to replanning rather than triggering repeated pressure for the rejected outcome; and material pathway changes are traceable to the governing evidence, decision, risk, policy, or context change that caused them.

**Identifier allocation note:** CR-0003, ADR-0008, EOS-AI-0001, and their acceptance records anticipated this concern as `FR-037` before the live requirement allocation was re-verified. The current product baseline already assigns `FR-037` through `FR-042` to governed execution-harness requirements. `FR-043` therefore realizes the same adaptive-workflow requirement without changing its approved semantic scope.

## Quality requirements

### QR-001 — Determinism

Ordering, identity, canonical serialization, Execution Envelope compilation, diagnostics, policy/capability decisions, and reproducible execution records must not depend on filesystem enumeration order, wall-clock time, randomized IDs, or ungoverned LLM output where deterministic semantics are required.

### QR-002 — Performance

Reference budgets for startup, parse/graph build, query latency, context generation, execution scheduling, state finalization, and memory must be measured on declared reference profiles; regressions above approved thresholds fail the applicable performance gate.

### QR-003 — Security

The system follows least privilege/context, defends against path traversal/symlink and untrusted-input hazards, avoids executing repository content during inspection unless explicitly authorized, produces no secret-bearing diagnostics/context by default, and fails closed when a consequential governed effect lacks sufficient authority, policy, or capability evidence.

### QR-004 — Reliability

Partial/corrupt caches or generated state must be detectable and recoverable by rebuilding from canonical inputs. Remote calls and agent orchestration use bounded retries, exponential backoff where safe, idempotency semantics, checkpoints where appropriate, and circuit breakers to prevent cascading failure. Recovery must not silently change governing execution semantics.

### QR-005 — Compatibility

Stable KIR/configuration/CLI/plugin/registry/MCP/LSP/adapter surfaces MUST use explicit versioning and compatibility policies before external stability is promised.

### QR-006 — Operability

Doctor/diagnostic paths must distinguish configuration/toolchain/environment, semantic-repository, provider, integration, policy, security, and deployment failures.

### QR-007 — Maintainability

Compiler/graph/query/context/policy/execution/observation/integration concerns have explicit boundaries and conformance fixtures so implementations can evolve without changing semantics accidentally. Governed execution semantics must remain separable from replaceable model reasoning, prompting strategy, and agent-harness internals.

### QR-008 — Progressive trust

Agent trust is earned from evidence relevant to the class of work being delegated, remains explicitly scoped, and can be demoted or revoked. Success in one materially different domain does not automatically grant authority in another. No agent begins with hard-mandatory or unrestricted authority.

### QR-009 — Cryptographic agility

Attestation and identity mechanisms must permit algorithm/version rotation, post-quantum migration, multi-party policies, and revocation without rewriting semantic history.

### QR-010 — Auditability

Consequential governed intent, compiled-context identity, adaptive pathway/rationale, material questions, human/agent actions, decisions, approvals/denials, authorizations, state transitions, Execution Envelopes, capability/policy evaluations, operations/effects, checkpoints/escalations, replanning, attestations, evidence, verification, review, and acceptance results must be reconstructable from durable evidence and tamper-evident logs without requiring private model chain-of-thought.

### QR-011 — Prompt and secret safety

Untrusted instructions must not silently expand capability. Secret material must be minimized, detected/masked where feasible, and excluded from shared caches and agent context unless explicitly authorized.

### QR-012 — Observability

Operational components must expose structured logs, metrics, and traces through OpenTelemetry-compatible boundaries where applicable, with correlation to Work Packets/executions/evidence.

### QR-013 — Portability

The local core remains usable offline. Optional deployment surfaces support major developer platforms, containers, Nix, air-gapped/on-prem operation, and multiple clouds through explicit compatibility profiles.

### QR-014 — Provider and harness independence

No single AI provider, model family, agent harness, hosted graph database, cloud vendor, or automation vendor is required for canonical core operation or authoritative governed-execution semantics.

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

### QR-021 — Fail-closed execution governance

Governed execution must deny, suspend, or explicitly escalate when mandatory authority, policy, capability, compatibility, approval, or governing-state validity cannot be established. Absence or ambiguity must never be treated as implicit permission.

### QR-022 — Cognition independence

Normative Monad execution contracts must govern observable intent, authority, operations, effects, evidence, verification, and state transitions without depending on a particular private reasoning representation, prompting technique, planner/executor pattern, reflection loop, or chain-of-thought disclosure.

### QR-023 — Governed execution reproducibility

Given equivalent canonical governed inputs and declared deterministic configuration, Monad must reproduce equivalent Execution Envelope identity and governance decisions. Nondeterministic executor/model outputs must be attributable and captured as results/evidence rather than falsely normalized into deterministic semantic truth.

## Release gates

### MVP Release 1

MVP Release 1 remains governed by `MVP-RELEASE-1.md`. New post-MVP capabilities do not expand the MVP merely because they are now planned.

### Post-MVP expansion

A post-MVP capability may enter execution only when its Epic/Feature/Work Packet is refined, governing ADR/specification authority is explicit, threat/privacy implications are dispositioned, exact validation/evidence requirements exist, and parent lifecycle gates authorize execution.

FR-037 through FR-042 and their associated quality requirements are post-MVP governed execution commitments. Their inclusion in this baseline does not authorize production activation of the Governed Execution Harness; activation remains subject to the same lifecycle, security, verification, and evidence gates.
