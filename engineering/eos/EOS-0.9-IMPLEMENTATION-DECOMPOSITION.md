# EOS 0.9 — Implementation Decomposition

**Status:** Proposed implementation plan
**Date:** 2026-08-13
**Governing proposal:** ADR-0006
**Change request:** CR-0001
**Design:** `engineering/eos/EOS-0.9-DECISION-READINESS-DESIGN.md`
**Planning rule:** Logical packet names below are provisional; canonical IDs are allocated only after state reconciliation and explicit CR approval.

## Objective

Implement EOS 0.9 as a sequence of bounded, independently verifiable changes that turn planning/readiness from a mostly document-completeness gate into an explainable decision-, dependency-, authority-, and evidence-aware execution boundary.

No packet may broaden the Monad product-runtime MVP scope.

## Pre-implementation gate

Before any implementation packet is authorized:

- [ ] ADR-0006 is explicitly Accepted by human authority.
- [ ] `eosp/start-pi-mvp-001` is integrated or otherwise reconciled into the canonical baseline.
- [ ] this branch is rebased/merged onto that baseline.
- [ ] `./scripts/eos state status` passes.
- [ ] `./scripts/eos verify --strict` passes.
- [ ] CR-0001 is approved through EOS.
- [ ] the EOS 0.9 planning horizon is created through EOS transactions.
- [ ] each implementation packet has explicit allowed/forbidden paths and validation requirements.

## Dependency graph

```text
P0 canonical-state mutation concurrency guard
 |
 +--> P1 decision/approval/dependency domain contract
       |
       +--> P2 canonical operational-state promotion
             |
             +--> P3 lifecycle + CLI operations
                   |
                   +--> P4 deterministic readiness predicates
                         |
                         +--> P5 readiness explainability/operator surface
                               |
                               +--> P7 integration/release review

P2 --------------------+
                       +--> P6 migration/conformance/regression
P3 --------------------+
P4 --------------------+
P5 --------------------+
```

P6 evolves alongside implementation and becomes a hard dependency of final integration.

## P0 — Canonical-State Mutation Concurrency Guard

### Purpose

Prevent two independently advancing branches from silently creating incompatible descendants of the sole canonical operational state.

### Required behavior

- capture the canonical-state revision/fingerprint at the branch/control-operation baseline;
- before an ordinary state mutation, detect whether the authoritative integration baseline has advanced incompatibly;
- fail closed rather than auto-merging operational authority;
- provide an actionable reconciliation message;
- preserve an explicit escape path only through governed reconciliation, never silent projection-wins behavior.

### Minimum acceptance

- stale branch mutation is rejected deterministically;
- clean current-baseline mutation remains allowed;
- read-only commands remain usable when safe;
- no automatic Git/GitHub state adoption occurs;
- fixture covers two branches derived from the same canonical revision.

### Why first

The current parallel workstreams exposed this gap in real operation. EOS 0.9 should not add more first-class state without first making stale-state mutation detectable.

## P1 — Decision, Approval, and Dependency Domain Contract

### Purpose

Correct and stabilize the semantic contracts that readiness will consume.

### Scope

- Decision lifecycle and conditional outcome requirements;
- Approval validity/disposition semantics;
- Dependency kinds and blocking semantics;
- authority/provenance expectations;
- state-machine definitions;
- schema/domain-model versioning.

### Decision invariant

An unresolved Decision is a valid object. A decided Decision has a non-empty outcome and rationale sufficient for audit.

### Approval invariant

Only a current Approval whose disposition and authority satisfy policy can discharge an approval requirement.

### Dependency invariant

A relationship becomes a readiness blocker only when its typed semantics and lifecycle say it is blocking; references and optional dependencies must not accidentally halt work.

### Minimum acceptance

Positive and negative fixtures cover every lifecycle transition and conditional field rule.

## P2 — Canonical Operational-State Promotion

### Purpose

Make DEC/APR/DEP operational participants without creating another state authority.

### Scope

- canonical-state schema support;
- state-model registration;
- transaction load/validate/mutate/project support;
- event representation;
- projection generation;
- migration from existing state with zero semantic change to current PI/WC/WP/CR/MNT/REL records.

### Migration requirements

- old canonical state validates/migrates predictably;
- failed migration leaves prior state authoritative;
- migration is deterministic and repeatable;
- projection drift fails closed;
- history is appended, not rewritten.

### Minimum acceptance

A migrated copy of the current repository state is semantically equivalent for all pre-existing entities, with only the expected schema/revision changes.

## P3 — Decision/Approval/Dependency Lifecycle and CLI

### Purpose

Give operators deterministic ways to create, inspect, transition, and relate the new operational entities.

### Candidate command surface

```text
eos decision create|list|show|open|decide|defer|supersede|revoke
eos approval request|list|show|grant|deny|revoke|expire
eos dependency create|list|show|satisfy|block|waive|retire
```

Exact command names remain implementation details until packet authorization.

### Requirements

- every mutation uses canonical transactions;
- actor/reason/authority/provenance are recorded;
- invalid transitions fail before write;
- tab completion discovers current IDs;
- read commands do not mutate projections.

## P4 — Deterministic Readiness Predicate Engine

### Purpose

Bring machine-enforced readiness into alignment with `engineering/definition-of-ready.md`.

### Predicate families

#### Structure

- required fields/sections present;
- no unauthorized unresolved markers;
- valid parent/identity metadata.

#### Governing references

- references resolve;
- governing artifacts are current enough for the requested transition;
- superseded/stale authority fails where policy requires current authority.

#### Dependency closure

- graph valid and acyclic;
- required blocking predecessors satisfy policy;
- unrelated unresolved work is ignored.

#### Decision/approval closure

- governing blocking decisions are resolved;
- required approvals are current and sufficient;
- authority level is adequate.

#### Scope

- bounded implementation surface;
- explicit exclusions;
- oversize signal requires decomposition or governed exception.

#### Acceptance/verification

- acceptance criteria are testable enough for delivery profile;
- validation/evidence expectations are declared;
- required security/operations checks are present when thresholds apply.

### Evaluation rule

Deterministic checks always run before any semantic/model-assisted evaluator.

A model-assisted result may contribute attributed evidence but cannot silently override a deterministic failure or create binding authority.

## P5 — Readiness Explainability and Operator Surface

### Purpose

Turn a gate failure into a concrete next action rather than a generic rejection.

### Result contract

Every predicate result should expose:

```text
gate/predicate
PASS | FAIL | NOT_APPLICABLE
reason
source/evidence
blocking entity
required authority when applicable
smallest corrective action when determinable
```

### Candidate UX

Preserve and enrich:

```text
eos gate check
eos gate explain
```

Optionally add:

```text
eos readiness check <target>
eos readiness explain <target>
```

if that improves discoverability without duplicating policy authority.

### Minimum acceptance

Identical canonical input produces byte/logically stable deterministic explanations.

## P6 — Migration, Conformance, and Regression Contract

### Purpose

Prove EOS 0.9 is safe, deterministic, backward-compatible where promised, and hostile to malformed state.

### Required fixture classes

- Decision open/decided conditional-field cases;
- Approval valid/invalid/expired/revoked cases;
- Dependency satisfied/blocked/optional/cyclic cases;
- unrelated unresolved decision does not block a packet;
- governing unresolved decision does block its affected packet;
- stale governing artifact behavior;
- current MVP state migration;
- stale-branch mutation rejection;
- projection-drift rejection;
- event/projection/canonical convergence;
- repeatability/idempotence;
- deterministic readiness explanation.

### Existing validations retained

- machine-document synchronization;
- trace projection integrity;
- repository integrity;
- `./scripts/eos state status`;
- `./scripts/eos verify --strict`.

## P7 — Integration, Documentation, and EOS 0.9 Release Review

### Purpose

Integrate the completed tranche only after contract, migration, policy, tooling, and regression evidence agree.

### Required work

- version EOS tool/schema/state-machine contracts intentionally;
- update governance/operator documentation;
- update shell completion;
- update machine projections;
- produce EOS 0.9 verification evidence;
- conduct independent review;
- record residual risks;
- prepare release/integration decision.

### Exit criteria

- all authorized EOS 0.9 packets closed;
- no unresolved blocking findings;
- canonical state and projections converge;
- migration evidence accepted;
- strict verification passes from a clean checkout/worktree;
- product MVP state remains historically and semantically coherent;
- human integration authority explicitly approves merge/release.

## Proposed planning shape after reconciliation

The recommended planning hierarchy is a dedicated EOS evolution horizon rather than placing EOS implementation inside `PI-MVP-001`.

Conceptually:

```text
PI-EOS-001 — EOS 0.9 Decision & Readiness
  Work Cycle — State and domain foundation
    P0 Canonical-state mutation concurrency guard
    P1 DEC/APR/DEP domain contract
    P2 Canonical operational-state promotion

  Work Cycle — Readiness behavior
    P3 Lifecycle + CLI operations
    P4 Deterministic readiness predicates
    P5 Explainability/operator surface

  Work Cycle — Qualification
    P6 Migration/conformance/regression
    P7 Integration/release review
```

`PI-EOS-001` is a proposed identifier because `eos plan` supports namespaced Program Increment IDs. Work Cycle and Work Packet identifiers must be allocated by the actual EOS creation commands at planning time rather than invented in this document.

## Parallelism

After P2 is stable:

- CLI work and fixture expansion may proceed partly in parallel;
- predicate fixture development can begin before all predicates are implemented;
- documentation can evolve continuously.

However:

- P4 cannot be considered complete before P1-P3 semantics stabilize;
- P5 depends on P4 result semantics;
- P7 depends on all implementation plus P6 qualification.

## Explicit non-goals

EOS 0.9 does not implement:

- multi-harness execution abstraction;
- cross-harness independent reviewer policy;
- autonomous dispatch frontier/worker pool;
- deterministic failure playbook;
- transcript/Merkle proof-of-execution;
- emergent finding capture;
- exploration readiness profile;
- TUI;
- cost/compliance governance;
- AI-SDLC import/export adapter.

Those remain later tranches in the assimilation program.

## Next authority sequence

Once the competing canonical-state branch is integrated:

1. reconcile/rebase this branch;
2. run state/strict verification;
3. human accepts ADR-0006;
4. human approves CR-0001 through EOS;
5. create the EOS evolution PI/work cycles/work packets through EOS;
6. make P0 the first authorized implementation packet.

