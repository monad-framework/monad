# Engineering Operating System

Engineering converts approved intent into verified increments while preserving
quality, safety, and decision history. Work is organized by outcomes and
evidence rather than by disconnected task lists.

## Delivery hierarchy

| Level | Purpose | Typical horizon | Closure evidence |
| --- | --- | --- | --- |
| Milestone | A major product or capability outcome | One or more increments | Outcome and readiness review |
| Increment | A releasable, integrated step toward a milestone | Several work cycles | Integrated acceptance evidence |
| Work cycle | A short inspect-and-adapt execution window | One or two weeks | Cycle review and updated forecast |
| Work packet | Smallest authorized unit with one result | Hours to a few days | Acceptance evidence and review |

Milestones contain increments; increments authorize work cycles; work cycles
pull ready work packets. Urgent incident or security work may enter through an
expedited path but must receive traceability and review after containment.

## Sources of truth

- `engineering-plan.md` defines the delivery strategy and phase gates.
- `project-status.md` is the current portfolio-level status snapshot.
- `definition-of-ready.md` controls entry into committed work.
- `definition-of-done.md` controls closure and release eligibility.
- `work-packets/active.md` lists currently authorized work.
- `work-packets/backlog.md` orders qualified candidate work.
- `risks/risk-register.md` contains active delivery and product risks.

## Flow rules

1. Pull only work that advances an authorized increment outcome.
2. Limit work in progress; finishing and integrating outrank starting.
3. Slice vertically through a demonstrable behavior or risk reduction.
4. Build quality, documentation, security, and telemetry into the packet.
5. Surface blocked work within one business day and name the needed decision.
6. Update status from evidence, not percentage-complete intuition.
7. Close work only when acceptance and the Definition of Done are satisfied.

## Review cadence

- Daily: owners update blockers and material scope changes.
- Each work cycle: demonstrate evidence, review flow and risk, and reforecast.
- Each increment: integrate acceptance, architecture, security, operations, and
  product outcome evidence.
- Each milestone: decide whether to proceed, correct, narrow, expand, or stop.

## Engineering values

Prefer a small change that proves an end-to-end claim over a large change that
creates invisible integration risk. Make unsafe states difficult to represent,
make failure diagnosable, and make recovery testable. Record why a constraint
exists so future maintainers can change it deliberately.
