# Monad Product Backlog

**Status:** Active rolling-wave plan

The Product Backlog is the ordered product/value view of work. It complements—not replaces—engineering authority. The canonical relationship between product planning and governed execution is defined in `../PROGRAM-HIERARCHY.md`.

```text
Product planning
Product Goal
  → Initiative
    → Epic
      → Feature
        → Story / Enabler / Bug / Spike
          → Task

Governed execution
Program Increment
  → Work Cycle
    → Work Packet
      → Execution / implementation / tests / evidence / review / verification

Engineering authority
Requirement / ADR / Specification / Policy
  → governs or constrains the applicable product and execution objects
```

For Monad, **Work Cycle and Sprint are the same execution window** unless a future governance change explicitly replaces that rule. `Work Cycle` is the canonical term and field; `Sprint` is a GitHub/planning compatibility label only and must not create a second cadence.

A Feature and a Work Packet are linked but distinct. A Feature expresses the planned product/value outcome. A Work Packet is the smallest authorized governed execution unit. The current MVP and expanded forecasts generally pair one Feature with one Work Packet, but that one-to-one mapping is a planning convention rather than an ontology identity.

## Canonical backlog layers

- `MVP-BACKLOG.md` — PG-001 / MVP Release 1: INIT-001 through INIT-006, EPIC-001 through EPIC-014, WP-MVP-0001 through WP-MVP-0033, US-001 through US-105 plus EN-001 through EN-003.
- `EXPANDED-BACKLOG.md` — approved post-MVP expansion under CR-0002: PG-002 through PG-004, EPIC-015 through EPIC-024, WP-EXP-0001 through WP-EXP-0040, US-106 through US-237. A post-MVP Initiative mapping has not yet been canonically assigned and must be introduced through governed rolling-wave planning before those Epics approach active execution.

MVP remains first in execution order. The expanded backlog does not silently widen an active MVP Work Packet or Work Cycle.

## Refinement horizon

- Current Product Goal Initiatives: defined as finite outcome groupings.
- All planned Epics: defined and sequenced at outcome level.
- All forecast Features: assigned to a forecast Increment and Work Cycle/Sprint.
- Stories/Enablers: stable planning identifiers with acceptance intent.
- Near-term Work Packets: decomposed into ready-candidate Tasks/tests/evidence.
- Later Tasks: refined only when dependencies, ADRs/specifications, security/privacy analysis, and evidence make them meaningful.

For the expanded roadmap, forecast Work Packet identities are cataloged by Program Increment under `engineering/work-packets/WP-EXP-PI-*-FORECAST.md`. A forecast entry is split into its own detailed Work Packet file when rolling-wave refinement reaches it. Forecast status is never Ready/Authorized by implication.

## Task rule

Formal implementation Tasks are intentionally not pre-generated for the entire roadmap. Before a Work Packet becomes Ready, it must have enough bounded task/test/evidence decomposition to execute without guessing. This prevents stale speculative task inventories from masquerading as engineering authority.

A formal Task should retain both its product parent (`Story` or `Enabler`) and its execution parent/context (`Work Packet`) where applicable. The Work Packet remains the governance boundary.

## Projection rule

GitHub Issues/Projects may project this backlog for collaboration. Git files remain canonical for governing requirements, specifications, ADRs, Work Packets, Program Increments, Work Cycles, Product Goals, milestones, and release evidence. Projection drift must be reconciled; it never silently changes canonical status.
