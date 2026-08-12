# Monad Product Backlog

**Status:** Proposed operating baseline  
**Product Goal:** Deliver MVP Release 1: a local-first deterministic semantic engineering loop from repository knowledge to graph/KIR, explanation, change impact, bounded agent context, execution plan, native tools, and reproducible evidence.

## Backlog hierarchy

```text
Product Goal
  ↓
Epic
  ↓
Feature
  ↓
Product Backlog Item
  ├─ User Story
  ├─ Enabler
  ├─ Bug
  ├─ Spike
  ├─ Debt
  └─ Risk/Decision work when delivery-relevant
       ↓
Sprint selection
       ↓
Work Packet
       ↓
Task / Codex execution unit
       ↓
PR + evidence
```

The Product Backlog describes value and delivery. Work Packets remain the smallest formally governed engineering authorization. GitHub Issues/Projects are projections of this model.

## Canonical files

- `epics.md` — complete foreseeable Epic map.
- `features.md` — complete foreseeable Feature map and forecast target.
- `stories.md` — MVP Product Backlog Items and refinement state.
- `tasks.md` — current and near-term executable task decomposition.
- `backlog.md` — ordered current Product Backlog and dependency-critical sequence.
- `../sprints/` — Sprint Goals and selected/forecast work.
- `../increments/` — Product Increment outcomes and exit gates.
- `../work-packets/` — formal engineering authorization and acceptance.

## Backlog item types

### User Story

A user- or operator-observable capability stated from an actor/outcome perspective. Technical implementation may be large internally, but the Story must still demonstrate value at a boundary.

### Enabler

Architecture, semantic model, tooling, quality, security, or infrastructure work that enables product behavior and has objective engineering acceptance. Do not force an artificial “As a user” sentence onto internal contracts.

### Spike

Time-boxed investigation whose result is evidence, a decision, or a recommendation—not production code by default.

### Bug

Observed behavior that contradicts an accepted requirement, specification, invariant, or user expectation.

### Task

A small execution step underneath a Story/Enabler/Work Packet. Tasks should normally be independently verifiable and small enough for one focused Codex/human execution unit.

### Debt

Known maintainability, architecture, dependency, test, or operational deficiency with explicit consequence and repayment trigger.

## Priority

- **P0:** existential correctness/security/authority need or hard critical-path blocker.
- **P1:** required to complete the MVP user outcome.
- **P2:** useful post-MVP capability or material optimization not required for Release 1.
- **P3:** future option kept visible to avoid architectural dead ends.

## Estimation

Stories/Enablers use Fibonacci comparative points: `1, 2, 3, 5, 8, 13`. Items larger than 8 should normally be split before Sprint commitment; 13 is a decomposition warning, not a target size. Points are not hours and are not converted into individual productivity measures.

## Rolling-wave refinement

- Entire foreseeable product: Epics visible.
- MVP and next horizons: Features visible and dependency-ordered.
- MVP: Stories/Enablers enumerated with acceptance anchors.
- Next 2–3 Sprints: refined enough to estimate and pass Definition of Ready.
- Current Sprint: Work Packets and Tasks fully decomposed with validation commands/evidence expectations.

This preserves long-range visibility without pretending the implementation details of later Sprints are already known.

## Ordering model

Backlog ordering considers, in order:

1. critical safety/security/correctness/authority risk;
2. assumptions or decisions that can invalidate downstream architecture;
3. dependency critical path to an integrated MVP scenario;
4. direct product value and learning value;
5. enablement of subsequent work;
6. effort, reversibility, and opportunity cost.

The Product Owner can override algorithmic or suggested ordering. The reason for a material override should be visible when it changes the Release 1 critical path.

## Definition of Ready

A PBI may be selected when its outcome is clear, dependencies are sufficiently known, acceptance is objective, governing authority is identified, risk is understood enough for the Sprint, and the implementing team/agent will not have to invent product or architecture meaning.

A Work Packet adds stricter engineering scope, authorized paths/concerns, prohibited changes, tests, validation commands, and completion evidence.

## Definition of Done

Done means integrated behavior and evidence—not “code written.” Applicable tests, static checks, documentation, machine projection, security/compatibility impact, diagnostics, traceability, review findings, and generated artifacts must satisfy the repository Definition of Done.

## GitHub projection

GitHub Issue hierarchy should follow:

```text
Epic Issue
  └─ Feature Issue
      └─ Story / Enabler Issue
          └─ Task Issue only when a separately tracked task is useful
```

Sprint is represented by a Project iteration field where available; repository Milestones represent major delivery/release outcomes rather than duplicating one-week Sprints. Issue state is a collaboration view and must not silently replace canonical status in Git.
