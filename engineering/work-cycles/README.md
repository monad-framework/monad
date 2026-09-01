# Work Cycles / Sprints

A Work Cycle is a short, fixed execution and learning window. It limits work in progress, creates a frequent integration point, and provides evidence for reforecasting. A cycle is not successful merely because every planned task was started.

For Monad's current roadmap, **Work Cycle == Sprint**. There is no second competing Sprint cadence.

## Namespaces and schedules

- `WC-MVP-*` — MVP Release 1; see `MVP-SPRINT-SCHEDULE.md`.
- `WC-EXP-*` — CR-0002 post-MVP expansion; see `EXPANDED-SPRINT-SCHEDULE.md`.

A forecast Work Cycle does not authorize its Work Packets. Parent increment state, Ready gates, authorization, execution, verification, and closure remain distinct.

## Cycle protocol

### Plan

Confirm the Increment/Product Goal objective, available capacity, carryover reason, autonomy assumptions, and top risks. Pull only Ready packets. Sequence the smallest path to integrated evidence and identify who can unblock external decisions.

### Execute

Keep active ownership and status visible. Integrate continuously, review early, and swarm on blockers or nearly complete packets before starting more work. Update acceptance/audit evidence as it is produced. Multi-agent parallelism does not justify exceeding dependency, review, or least-authority constraints.

### Review

Demonstrate completed outcomes and risk reduction in a representative context. Record accepted packets, unmet evidence, defects, product/architecture/security/privacy findings, performance claims, autonomy changes, and milestone/Product Goal implications. Do not count partial work or merged code alone as delivered value.

### Improve

Inspect flow time, blocked time, rework, escaped defects, review latency, automation/provider failures, cost, security/privacy findings, and unplanned work. Select at most one or two concrete process/system experiments for the next cycle and assign owners.

## Suggested limits

Use no more concurrent Work Packets than demonstrated review/execution capacity supports and aim for fewer. Only one Work Packet may be authorized at a time where EOS WIP policy says so. Packets blocked beyond the configured escalation threshold require explicit escalation or replanning. A packet spanning multiple cycles is split unless its indivisibility is documented and approved.

## Cycle record

Each activated Work Cycle receives a canonical record with objective, Increment/Product Goal, capacity, selected packets, risk focus, completed evidence, metrics, decisions, carryover, and improvement experiment. Forecast schedule rows are planning projections, not substitutes for activated cycle records.
