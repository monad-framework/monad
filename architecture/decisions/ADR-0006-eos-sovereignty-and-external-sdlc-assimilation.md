# ADR-0006: EOS Sovereignty and External SDLC Assimilation

- **Status:** Accepted
- **Date:** 2026-08-13
- **Decision owners:** Architecture Owner, Engineering Owner
- **Reviewers:** Product Owner, Security Owner, Operations Owner as affected
- **Related:** ADR-0001, ADR-0005, `governance/authority.md`, `governance/canonical-state-model.md`, `governance/planning-engine.md`, `governance/policy-engine.md`, `governance/execution-engine.md`
- **Supersedes:** none
- **Superseded by:** none
- **Acceptance evidence:** `engineering/reviews/DECISION-0001-2026-08-13-adr-0006-acceptance.md`

## Decision summary

Monad SHALL assimilate useful concepts and mechanisms from external software-delivery frameworks, including AI-SDLC, into Monad-native semantics while preserving EOS as the sole repository lifecycle/control plane and Monad canonical artifacts as the authoritative engineering knowledge source. External frameworks MAY be used as design inputs, compatibility targets, import/export formats, or adapters, but they MUST NOT introduce a competing authoritative lifecycle state, dependency graph, task hierarchy, evidence store, approval system, or execution authority inside Monad.

The initial assimilation program SHALL prioritize decision closure and Definition-of-Ready enforcement, then harness abstraction, independent review, bounded orchestration, proof of execution, emergent-work capture, exploration profiles, operator surfaces, conformance, and later interoperability. Product-runtime implementation governed by existing MVP ADRs and Work Packets remains independently scoped and is not reopened by this decision.

## Context

Monad has matured from a documentation-oriented foundation into an Engineering Knowledge Compilation Platform with a repository-native Engineering Operating System. EOS already provides lifecycle state, planning, policy gates, semantic traceability, bounded execution, verification evidence, review, change control, release lifecycle, and maintenance concerns. The current canonical-state model intentionally establishes one current operational state and treats GitHub and legacy registries as projections rather than competing authorities.

The `ai-sdlc-framework/ai-sdlc` project contains several complementary mechanisms that are strategically valuable to Monad: deterministic-first Definition-of-Ready evaluation, decision routing, dependency-aware autonomous dispatch, cross-harness review, declarative quality/autonomy policies, typed agent handoffs, proof-of-execution patterns, emergent-issue capture, exploration workstreams, operator TUI concepts, cost/compliance surfaces, and language-agnostic conformance.

A wholesale merge, subtree, submodule, or parallel installation would create overlapping concepts and potentially two control planes. In particular, `.ai-sdlc/`-style control state, an external task model, a separate dependency graph, or an external attestation authority would conflict with Monad's canonical-state, authority, Work Packet, semantic-graph, and evidence models.

The decision is required before further autonomous-execution investment because the architecture must determine whether these capabilities become native EOS behavior, remain external, or are deferred.

## Decision drivers

1. **Single authority:** no competing source of lifecycle or engineering truth.
2. **Semantic coherence:** imported concepts must map to Monad's domain model and graph.
3. **Determinism first:** structural and graph checks precede probabilistic evaluation.
4. **Human sovereignty:** consequential decisions remain with explicitly accountable authority.
5. **Bounded autonomy:** automation executes only within authorized scope and evidence-backed policy.
6. **Replaceable harnesses:** Codex, Claude Code, and future executors/reviewers are adapters to roles rather than architectural owners.
7. **Auditability:** execution, review, approval, and evidence remain reconstructable and attributable.
8. **Incremental adoption:** the MVP product kernel must continue without a disruptive EOS rewrite.
9. **Interoperability:** future AI-SDLC compatibility should be possible without making it canonical.
10. **Licensing clarity:** conceptual assimilation is preferred; direct code/document reuse requires explicit provenance and license review.

## Options considered

### Option A — Merge or embed AI-SDLC as a subsystem

Import substantial AI-SDLC code/configuration and operate it inside the Monad repository.

**Advantages**

- fastest access to already-implemented orchestration features;
- lower short-term design effort;
- possible direct compatibility with AI-SDLC tooling.

**Disadvantages**

- creates overlapping task, policy, dependency, execution, and evidence models;
- risks two operational authorities;
- introduces runtime/tooling assumptions that are not native to Monad;
- increases coupling to AI-SDLC's release cadence and design choices;
- makes later removal costly;
- complicates provenance and Apache-2.0 reuse obligations if code or substantial documentation is copied.

### Option B — Selective Monad-native assimilation with optional compatibility bridge

Treat AI-SDLC as a design donor. Classify each capability as Adopt, Adapt, Interoperate, Defer, or Reject; implement selected mechanisms through Monad's existing domain, EOS layers, canonical state, semantic graph, policies, evidence, and authority model. Build an AI-SDLC adapter only after native semantics stabilize.

**Advantages**

- preserves one control plane and one authority model;
- leverages Monad's richer semantic graph and provenance model;
- permits stronger readiness and impact analysis than issue-text-only systems;
- keeps harnesses and external frameworks replaceable;
- allows incremental implementation and rollback;
- minimizes licensing entanglement by preferring independent implementation of concepts.

**Disadvantages**

- requires deliberate design and implementation work;
- reaches feature parity more slowly than embedding an existing system;
- requires conformance tests to prevent conceptual drift.

### Option C — Continue current EOS development without explicit assimilation

Keep AI-SDLC as informal inspiration only.

**Advantages**

- no near-term architecture work;
- lowest immediate change risk.

**Disadvantages**

- likely duplicates already-solved design work inconsistently;
- risks ad hoc feature copying without a coherent authority boundary;
- delays high-value readiness, review-independence, and orchestration mechanisms;
- makes later interoperability harder.

## Decision

Choose **Option B — Selective Monad-native assimilation with optional compatibility bridge**.

EOS remains the sole repository lifecycle/control plane. Canonical Monad artifacts and the canonical EOS operational state remain authoritative according to existing governance. AI-SDLC terminology MAY appear in source-attribution, research, migration, or compatibility documentation, but native implementation surfaces SHALL use Monad concepts unless an external protocol requires otherwise.

The assimilation order is:

1. Decision and Readiness Engine.
2. Harness/execution-role abstraction.
3. Independent cross-harness review.
4. Dispatch frontier and worker pool.
5. Deterministic failure/recovery playbook.
6. Proof-of-execution and stronger provenance.
7. Emergent-work capture and exploration profiles.
8. Operator TUI and analytics.
9. Conformance/certification suite.
10. Cost, compliance, zero-trust contribution, and advanced autonomy.
11. Optional AI-SDLC import/export/compatibility adapter.

The current MVP product topology established by ADR-0005 remains in force. Assimilation work SHALL NOT silently broaden or rewrite existing product Work Packet scope.

## Consequences

### Positive

- Monad gains a coherent path to substantially stronger AI-assisted delivery without architectural duplication.
- Decision closure becomes a first-class prerequisite to execution rather than an informal prompt convention.
- The semantic graph can make readiness authority-, lifecycle-, dependency-, freshness-, and evidence-aware.
- Execution becomes portable across Codex, Claude Code, and future harnesses.
- Independent review can be enforced mechanically rather than by convention.
- Autonomous orchestration can be introduced only after the prerequisites that make it safe are measurable.

### Negative

- EOS schema and canonical-state evolution will be required before Decision, Approval, and richer Dependency entities become operationally first-class.
- Some AI-SDLC features will need reimplementation instead of direct reuse.
- The program adds governance and test surface before autonomous throughput increases.
- Interoperability is deferred until native semantics stabilize.

### Neutral or follow-on

- Existing `./scripts/eos codex` behavior may remain as a compatibility/convenience command while a generic execution role/harness interface is introduced later.
- GitHub Issues/Projects remain collaboration projections.
- Direct reuse of AI-SDLC code or substantial textual material requires a deliberate license/provenance review; this ADR authorizes conceptual assimilation, not unreviewed copying.

## Security, privacy, and operations

No new runtime privilege is authorized by this ADR. Later autonomy work must preserve least privilege, bounded file/system/network access, explicit authority, immutable or tamper-evident audit evidence, and fail-closed behavior for governing-state drift.

The future harness abstraction must record sufficient executor/reviewer identity and configuration to support accountability. Independent review policy must be able to prohibit insufficiently independent reviewer/implementer combinations. Raw model transcripts must not become mandatory committed artifacts because they may contain sensitive repository context; cryptographic/provenance evidence should be retained separately from configurable transcript storage.

## Migration and rollback

Migration is staged and additive. Each capability enters through a separately governed EOS tranche. Existing product Work Packets continue under current contracts.

Rollback is performed by reverting an unaccepted or failed tranche while retaining prior canonical state and evidence. No tranche may require a one-way migration until its compatibility, backup, projection, verification, and recovery strategy is documented and reviewed.

## Validation

The decision is validated when:

- the capability assimilation matrix maps external concepts to existing or planned Monad-native owners;
- EOS 0.9 can strengthen readiness without introducing a second current-state store;
- execution remains compatible with existing bounded EOSE behavior;
- independent review can be represented using native Review/Evidence/Approval semantics;
- future orchestration can derive a dispatch frontier from canonical lifecycle, dependency, decision, risk, and evidence state;
- `./scripts/eos verify --strict` remains authoritative for EOS integrity throughout adoption.

Reconsider this ADR if selective assimilation proves unable to provide required interoperability without duplicating authority, or if evidence shows an external framework can be embedded while preserving Monad's single canonical state and governance invariants more safely and cheaply.

## References

- `https://github.com/ai-sdlc-framework/ai-sdlc`
- AI-SDLC `VISION.md`, Definition-of-Ready RFC, Autonomous Pipeline Orchestrator RFC, Decision Catalog RFC, cross-harness review runbook, proof-of-execution RFC, emergent-issue capture RFC, exploration-workstream RFC, conformance package, and progressive-autonomy specification; inspected 2026-08-12 through 2026-08-13.
- `governance/authority.md`
- `governance/canonical-state-model.md`
- `governance/decision-process.md`
- `governance/planning-engine.md`
- `governance/policy-engine.md`
- `governance/execution-engine.md`
- `engineering/definition-of-ready.md`
