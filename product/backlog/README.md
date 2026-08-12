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
          → Implementation / tests / evidence / PR
```

For MVP, **Work Cycle and Sprint are the same one-week execution window**. This avoids running two competing cadences.

## Refinement horizon

- All MVP Epics: defined and sequenced.
- All MVP Features: defined and assigned to a forecast Sprint/Increment.
- Stories/Enablers: defined across the MVP with acceptance intent.
- Next three Sprints: decomposed into ready-candidate Work Packets/tasks.
- Later tasks: refined when dependencies/evidence make them meaningful.

GitHub Issues/Projects project this backlog for collaboration. Git files remain canonical for governing specifications, ADRs, Work Packets, and release evidence.