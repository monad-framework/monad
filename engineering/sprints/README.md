# Sprints

Monad uses one-week Sprints from Monday through Sunday once Foundation Stabilization closes. Sprints are inspection/adaptation windows, not mini-waterfall phases. The forecast through MVP Release 1 exists to expose sequencing and dependencies; actual Sprint commitment occurs during Sprint Planning.

## Cadence

- **Planning:** Monday — Product Goal context, Sprint Goal, Ready PBI selection, capacity/dependency check.
- **Execution:** continuous implementation, review, integration, and daily state inspection.
- **Refinement:** throughout the Sprint; next two Sprints receive the deepest refinement.
- **Review:** demonstrate integrated outcome and acceptance evidence before Sprint closure.
- **Retrospective:** record process/system improvements and update operating agreements/backlog where evidence justifies change.

## Forecast

| Sprint | Dates | Product Increment | Goal |
| --- | --- | --- | --- |
| SPRINT-001 | Aug 17–23, 2026 | PI-001 | Accept stabilized foundation and make first implementation packets Ready. |
| SPRINT-002 | Aug 24–30 | PI-002 | Discover workspace, repository identity, configuration, components and tools deterministically. |
| SPRINT-003 | Aug 31–Sep 6 | PI-002 | Establish stable semantic identity, canonicalization, hashing, source coordinates and provenance. |
| SPRINT-004 | Sep 7–13 | PI-002 | Build deterministic Monad Semantic Graph with ontology and invariants. |
| SPRINT-005 | Sep 14–20 | PI-002 | Establish KIR schema, lowering, serialization and conformance. |
| SPRINT-006 | Sep 21–27 | PI-002 | Query/explain the graph and compute the first conservative affected set. |
| SPRINT-007 | Sep 28–Oct 4 | PI-003 | Harden diagnostics, impact paths and conservative uncertainty behavior. |
| SPRINT-008 | Oct 5–11 | PI-003 | Add incrementality, fingerprints, policy first slice and execution-plan construction. |
| SPRINT-009 | Oct 12–18 | PI-003 | Execute native tools locally with failure semantics, cache and evidence. |
| SPRINT-010 | Oct 19–25 | PI-003 | Integrate Release 1 CLI and bounded AI-agent context workflow. |
| SPRINT-011 | Oct 26–Nov 1 | PI-004 | Prove integrated determinism/reproducibility across reference repositories. |
| SPRINT-012 | Nov 2–8 | PI-004 | Harden security, performance, compatibility and packaging. |
| SPRINT-013 | Nov 9–15 | PI-004 | Dogfood Monad, finish publication/beta feedback and release automation. |
| SPRINT-014 | Nov 16–22 | PI-004 | Produce and review the Release 1 candidate. |

**Forecast release:** Monday, November 23, 2026, only if release-readiness evidence passes.

## Sprint status vocabulary

`Forecast` → `Planned` → `Active` → `Review` → `Closed`. A Sprint may close with incomplete PBIs; unfinished work returns to backlog and is reordered rather than silently carried as Done.

## Scope-change rule

The Sprint Goal is more stable than the exact task list. Newly discovered work may be added or exchanged when necessary to meet the Goal, but material product/architecture scope changes follow normal authority and backlog processes. Quality gates are not traded for point completion.
