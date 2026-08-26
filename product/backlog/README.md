# Monad Product Backlog

**Status:** Active rolling-wave plan

The Product Backlog is the ordered product/value view of work. It complements—not replaces—engineering authority.

```text
Product Goal
  → Epic
    → Feature
      → Story / Enabler / Bug / Spike
        → Task

Engineering authority
  → ADR / Specification
    → Increment
      → Work Cycle (Sprint)
        → Work Packet
          → Execution / implementation / tests / evidence / PR
```

For Monad, **Work Cycle and Sprint are the same execution window** unless a future governance change explicitly replaces that rule. This avoids running two competing cadences.

## Canonical backlog layers

- `MVP-BACKLOG.md` — PG-001 / MVP Release 1: EPIC-001 through EPIC-014, WP-MVP-0001 through WP-MVP-0033, US-001 through US-105 plus EN-001 through EN-003.
- `EXPANDED-BACKLOG.md` — approved post-MVP expansion under CR-0002: PG-002 through PG-004, EPIC-015 through EPIC-024, WP-EXP-0001 through WP-EXP-0040, US-106 through US-237.

MVP remains first in execution order. The expanded backlog does not silently widen an active MVP Work Packet or Work Cycle.

## Refinement horizon

- All planned Epics: defined and sequenced at outcome level.
- All forecast Features: assigned to a forecast Increment and Work Cycle/Sprint.
- Stories/Enablers: stable planning identifiers with acceptance intent.
- Near-term Work Packets: decomposed into ready-candidate Tasks/tests/evidence.
- Later Tasks: refined only when dependencies, ADRs/specifications, security/privacy analysis, and evidence make them meaningful.

For the expanded roadmap, forecast Work Packet identities are cataloged by Program Increment under `engineering/work-packets/WP-EXP-PI-*-FORECAST.md`. A forecast entry is split into its own detailed Work Packet file when rolling-wave refinement reaches it. Forecast status is never Ready/Authorized by implication.

## Task rule

Formal implementation Tasks are intentionally not pre-generated for the entire roadmap. Before a Work Packet becomes Ready, it must have enough bounded task/test/evidence decomposition to execute without guessing. This prevents stale speculative task inventories from masquerading as engineering authority.

## Projection rule

GitHub Issues/Projects may project this backlog for collaboration. Git files remain canonical for governing requirements, specifications, ADRs, Work Packets, Program Increments, Work Cycles, Product Goals, milestones, and release evidence. Projection drift must be reconciled; it never silently changes canonical status.
