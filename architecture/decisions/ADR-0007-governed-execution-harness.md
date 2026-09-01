# ADR-0007: Governed Execution Harness Architecture

- **Status:** proposed
- **Date:** 2026-09-01
- **Decision owners:** Architecture Owner, Engineering Owner
- **Reviewers:** Security Owner, Operations Owner, Product Owner, Verification Owner as affected
- **Related:** ADR-0001, ADR-0005, ADR-0006, `governance/authority.md`, `governance/policy-engine.md`, `governance/execution-engine.md`, `governance/canonical-state-model.md`, `engineering/definition-of-ready.md`
- **Supersedes:** none
- **Superseded by:** none

## Decision summary

Monad SHALL establish a first-class **Governed Execution Harness** as the stable governance and execution boundary between Monad's authoritative engineering knowledge/EOS control plane and replaceable AI agent harnesses, models, tools, and execution environments.

The governing architectural rule is:

> **Monad governs agent execution but does not prescribe agent cognition.**

Monad SHALL own compilation of governed work into a versioned Execution Envelope; authority, policy, and capability resolution; mediated tool/effect execution; execution state and checkpoints; approval/escalation control; evidence and provenance capture; and verification-controlled completion. External agent harnesses such as Codex, Claude Code, and future executors SHALL remain replaceable adapters that may choose their own planning, reasoning, delegation, prompting, and model strategies within the envelope and SHALL NOT become authoritative lifecycle, policy, evidence, or completion authorities.

A lightweight Monad reference agent MAY later be provided for dogfooding, conformance, and portability testing, but it SHALL implement the same adapter contract as external harnesses and SHALL NOT define the core architecture.

## Context

ADR-0006 preserves EOS as the sole repository lifecycle/control plane while explicitly prioritizing harness/execution-role abstraction as an early Monad-native assimilation target. That decision also requires replaceable harnesses, bounded autonomy, human sovereignty, deterministic checks before probabilistic evaluation, and reconstructable execution evidence.

Current AI coding systems combine several concerns that should not share one architectural owner: model inference, planning/reasoning loops, context assembly, tool invocation, permissions, workspace interaction, retries, review, and completion judgment. If Monad adopts one vendor harness or one agent-loop design as its native control plane, rapidly changing implementation assumptions become coupled to stable engineering-governance semantics.

Conversely, treating AI execution as only a prompt or shell-command integration would leave Monad's strongest existing concepts—authority, policy, capabilities, semantic dependencies, evidence, provenance, verification, and EOS lifecycle state—outside the actual execution boundary. That would make governed knowledge AI-readable but not reliably AI-executable.

An explicit decision is therefore required before introducing broader autonomous execution, cross-harness review, worker pools, or a native reference agent.

## Decision drivers

1. **Single authority:** EOS and canonical Monad artifacts remain the sole authoritative engineering control plane.
2. **Governed effects:** consequential actions must pass explicit authority, policy, and capability checks.
3. **Harness portability:** Codex, Claude Code, future agents, and a Monad reference agent must be substitutable without rewriting governance semantics.
4. **Cognition neutrality:** Monad must not encode a particular agent planning/reasoning technique into its governing contracts.
5. **Least privilege:** every execution receives only the capabilities and tools required for authorized work.
6. **Auditability:** consequential operations and outcomes must be attributable to actor, execution, governing state, and evidence.
7. **Verification authority:** completion must be determined from explicit verification obligations rather than model self-report.
8. **Local-first operation:** the core must remain usable without requiring a cloud control plane.
9. **Backend neutrality:** execution environments and model providers must remain replaceable behind contracts.
10. **Fail-closed governance:** unresolved governing authority or capability must not silently broaden execution rights.
11. **Recoverability:** long-running work needs explicit cancellation, checkpoint, retry, resume, and escalation semantics.
12. **Incremental adoption:** existing bounded EOSE execution must remain viable while the new boundary is introduced.

## Options considered

### Option A — Build a monolithic Monad coding agent

Monad would own the model loop, planning strategy, prompting, context handling, tools, permissions, verification, and user interaction as one integrated AI agent product.

**Advantages**

- maximum short-term control over user experience;
- fewer adapter boundaries initially;
- easier optimization around one execution strategy.

**Disadvantages**

- couples Monad to rapidly changing model and agent-loop assumptions;
- duplicates mature external harness capabilities;
- makes model/harness substitution expensive;
- risks shifting Monad from governed engineering substrate toward a vendor-specific coding-agent product;
- encourages cognition implementation details to leak into governance semantics.

### Option B — Governed Execution Harness with pluggable agent adapters

Monad owns the stable governance/execution boundary and exposes a versioned adapter contract to external or native agent harnesses. The agent receives a governed Execution Envelope and requests operations through mediated interfaces. Monad captures results/evidence and determines lifecycle transitions through verification and authority rules.

**Advantages**

- preserves Monad's differentiated governance role;
- makes harnesses and models replaceable;
- compiles governed engineering knowledge into executable constraints;
- centralizes authority, policy, capability, evidence, and verification enforcement;
- permits specialized agent harnesses to evolve independently;
- supports both AI and non-AI executors behind the same governed effect boundary.

**Disadvantages**

- requires explicit protocol/schema design;
- adds adapter and compatibility testing;
- may limit harness-specific optimizations unless extension points are carefully designed;
- introduces execution-state and evidence overhead.

### Option C — Keep harness integration external and prompt-based

Monad would export context or instructions to external agents but would not introduce a first-class execution harness boundary.

**Advantages**

- least near-term implementation work;
- no new protocol surface.

**Disadvantages**

- governance becomes advisory rather than enforceable at the action boundary;
- permissions and completion semantics remain fragmented across tools;
- weak provenance and reconstruction of agent effects;
- no stable basis for cross-harness execution, evaluation, or controlled autonomy;
- duplicates policy/context assembly in each integration.

## Decision

Choose **Option B — Governed Execution Harness with pluggable agent adapters**.

The Governed Execution Harness is a Monad subsystem, not a new lifecycle authority. EOS remains authoritative for work state and transition eligibility. The harness consumes governed state, executes authorized work, emits evidence/provenance, and requests or triggers EOS transitions only through established governance rules.

### Required harness responsibilities

The first-class harness boundary SHALL include the following logical responsibilities. Implementations MAY combine them physically while preserving their contracts and invariants.

1. **Context Compiler** — resolves the minimum authoritative engineering context required for the work.
2. **Authority Resolver** — determines governing sources and accountable decision authority.
3. **Policy Engine Integration** — evaluates execution and transition policy against canonical state.
4. **Capability Broker** — derives least-privilege capabilities for the actor/executor.
5. **Execution Envelope Compiler** — produces a versioned, immutable description of governed work inputs and obligations.
6. **Tool Gateway** — mediates governed tool/effect requests and enforces capabilities/policy before execution.
7. **Execution State and Checkpoint Manager** — tracks run identity, state, cancellation, retry, checkpoint, and resume semantics without replacing EOS canonical lifecycle state.
8. **Approval and Escalation Controller** — stops or routes work when explicit authority, uncertainty, risk, or policy requires human or designated review.
9. **Evidence and Provenance Recorder** — records sufficient inputs, requested operations, outcomes, verification evidence, and identities for reconstruction and audit.
10. **Verification Controller** — evaluates explicit verification obligations and determines whether execution evidence is sufficient to claim completion.

### Execution Envelope

Each governed execution SHALL be derived from a versioned **Execution Envelope**. The envelope is a compiled artifact, not a second source of truth. It references or snapshots the governing state necessary to make one execution deterministic and auditable.

The envelope SHALL support, at minimum:

- envelope schema/version;
- execution/run identity;
- intent and governed work subject;
- governing requirements, specifications, ADRs, decisions, and policies;
- architectural and operational constraints;
- relevant evidence and unresolved claims/decisions;
- actor/executor identity and role;
- granted capabilities and explicit prohibitions;
- permitted tools/interfaces and execution environment constraints;
- acceptance criteria and verification obligations;
- approval gates and escalation conditions;
- budgets/limits where applicable;
- provenance/evidence obligations;
- completion criteria;
- hashes or equivalent identifiers sufficient to detect governing-state drift.

The exact serialized schema is deferred to a technical specification and schema tranche.

### Agent Harness Adapter boundary

An agent adapter SHALL be able to:

- receive a versioned Execution Envelope or a capability-limited projection of it;
- initialize/resume a governed execution session;
- request approved operations/tools through the Tool Gateway;
- receive operation results and diagnostics;
- emit candidate outputs, progress state, questions, and escalation requests;
- submit evidence or references to evidence produced by governed operations;
- request verification;
- terminate, cancel, or yield control according to protocol.

An adapter SHALL NOT be allowed to:

- broaden its own capabilities;
- redefine authoritative requirements/policies;
- directly mark EOS work accepted/complete;
- bypass the Tool Gateway for governed effects while claiming a governed execution;
- silently replace governing context after the envelope has been compiled;
- make its private planning/reasoning representation part of Monad's normative contract.

### Cognition-neutral contract

Monad SHALL constrain externally observable intent, capabilities, operations, effects, evidence, verification, and lifecycle transitions. Monad SHALL NOT require a specific internal agent planning, reasoning, reflection, delegation, or prompting strategy unless a future separately governed feature explicitly requires one for conformance.

This keeps governance stable while models and harnesses improve.

### Reference agent

A Monad reference agent MAY be implemented after the adapter and envelope contracts are stable enough to test. It exists to:

- dogfood the adapter contract;
- prove that Monad is not dependent on an external proprietary harness;
- provide deterministic/conformance fixtures where feasible;
- exercise local-first execution;
- support evaluation across model/harness combinations.

It SHALL NOT receive privileged governance APIs unavailable to conforming external adapters unless those privileges are separately specified as an explicit trusted-system role.

### Evaluation harness

Evaluation is related but distinct from governed execution. Monad SHOULD provide a separate evaluation/conformance harness capable of replaying controlled tasks against multiple model/harness combinations and scoring correctness, requirement satisfaction, policy compliance, unauthorized actions, provenance completeness, architectural drift, cost/resource use, human intervention, and reproducibility.

Evaluation results MAY inform policy and harness selection but SHALL NOT create a second production execution authority.

## Consequences

### Positive

- Governed engineering knowledge becomes executable rather than merely available as model context.
- External harness innovation can be adopted without transferring lifecycle authority to external products.
- Agent/model substitution becomes a contract compatibility problem rather than an architecture rewrite.
- Least privilege, provenance, evidence, and verification become common behavior across executors.
- Human approval/escalation can be represented explicitly rather than through ad hoc confirmation dialogs.
- The same boundary can govern human, scripted, and AI executors where appropriate.
- Cross-harness independent review and comparative evaluation gain a stable foundation.

### Negative

- Monad must design and version new envelope, adapter, execution-state, and evidence contracts.
- Every supported external harness requires an adapter and conformance maintenance.
- Full mediation may be impossible for effects performed outside Monad-controlled environments; such effects must be marked external/unverified rather than silently treated as governed.
- Rich context compilation and evidence retention can increase latency, storage, and operational complexity.

### Neutral or follow-on

- Existing `./scripts/eos codex` behavior may continue temporarily but should converge on the generic adapter boundary.
- A Claude Code adapter, Codex adapter, or other adapter is an implementation choice, not an architectural dependency.
- Multi-agent delegation remains deferred; when introduced, child executions must inherit or narrow—not broaden—the parent authority/capability envelope.
- Requirements, threat model, schema catalog, traceability, and implementation Work Packets require follow-on amendments before production activation.

## Security, privacy, and operations

The harness creates a critical trust boundary because model-generated requests may cause external effects. Governed effects MUST be authorized independently of model assertions. Capability decisions MUST default to denial when governing state is absent, invalid, stale beyond policy, or contradictory in a way that prevents safe resolution.

Sensitive context SHOULD be minimized before projection to external model providers. Provider/network permissions, transcript retention, secret exposure, filesystem scope, process execution, and external-service access require explicit policy. Raw private model reasoning is neither required nor sufficient audit evidence; auditability is based on governed inputs, observable requests/actions, outcomes, approvals, evidence, and verification.

Execution cancellation, timeout, resource budget, checkpoint integrity, stale-envelope detection, tool failure, partial-effect recovery, and incident reconstruction must be testable operational behaviors.

## Migration and rollback

Migration is additive and staged:

1. define envelope and adapter contracts without changing current execution behavior;
2. implement envelope compilation and dry-run inspection;
3. route one existing bounded executor through the adapter/gateway boundary;
4. add evidence/verification integration;
5. introduce additional external adapters;
6. add the reference agent and evaluation harness only after contract conformance is demonstrated.

Existing direct executor commands remain available during compatibility migration unless separately deprecated. Rollback removes the new routing path and returns to the prior bounded EOSE behavior; canonical EOS state and already-recorded evidence remain intact.

No migration stage may make an external harness the sole owner of canonical execution state.

## Validation

This decision is validated when all of the following are demonstrated:

- a versioned Execution Envelope can be compiled deterministically from a fixed governed repository state;
- at least two materially different executor/harness implementations can consume the same governed contract without governance-semantic changes;
- prohibited or ungranted tool operations fail closed;
- governing-state drift is detected before consequential execution or completion;
- consequential effects are attributable to execution, actor, envelope, operation, and resulting evidence;
- verification, not executor self-report, controls the governed completion claim;
- cancellation/checkpoint/resume semantics preserve auditability;
- existing EOS strict verification remains authoritative;
- the core remains usable in a local-first configuration without mandatory cloud orchestration.

Reconsider this ADR if the adapter boundary proves unable to preserve key harness capabilities without unsafe bypasses, or if evidence shows the abstraction materially reduces correctness/reliability compared with a more specialized architecture without delivering meaningful portability or governance value.

## References

- ADR-0006: EOS Sovereignty and External SDLC Assimilation
- `governance/authority.md`
- `governance/canonical-state-model.md`
- `governance/policy-engine.md`
- `governance/execution-engine.md`
- `engineering/definition-of-ready.md`
