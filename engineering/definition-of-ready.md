# Definition of Ready

A work packet may enter a committed work cycle only when it is understandable,
bounded, testable, safe to begin, and connected to an authorized outcome. Ready
does not mean every implementation detail is known; it means remaining
uncertainty is intentional and affordable inside the packet.

## Required for every work packet

- [ ] Stable ID, concise title, owner, and target increment are assigned.
- [ ] The problem or desired outcome is stated in observable terms.
- [ ] Scope and explicit exclusions fit within one work cycle.
- [ ] Acceptance criteria describe evidence, including failure or boundary
      behavior when applicable.
- [ ] Relevant requirements, specifications, ADRs, risks, and dependencies are
      linked.
- [ ] Preconditions, required access, environments, and test data are available.
- [ ] Security, privacy, accessibility, operations, and documentation impacts
      have been assessed.
- [ ] Unknowns are either resolved or converted into bounded research work.
- [ ] The owner believes the packet can reach Done without hidden external
      approval or another unplanned packet.

## Additional checks for behavior changes

- [ ] User and system behavior is specified for success, invalid input,
      unauthorized action, dependency failure, interruption, and retry as
      relevant.
- [ ] Compatibility and migration impact is understood.
- [ ] Test approach includes the appropriate unit, contract, integration,
      acceptance, accessibility, performance, or security level.
- [ ] Required telemetry and support behavior are explicit.

## Additional checks for architecture or infrastructure

- [ ] Decision drivers and quality scenarios are identified.
- [ ] Strategic choices have an ADR or an assigned decision packet.
- [ ] Deployment, configuration, rollback, capacity, cost, and ownership are
      addressed.
- [ ] Dependency risk and exit or containment strategy are understood.

## Readiness authority

The packet owner performs the initial check. Product accepts user outcome and
scope; engineering accepts feasibility and evidence; security or operations
review when their risk threshold is crossed. A reviewer may mark a packet not
ready with a specific unmet criterion and the smallest corrective action.

## Expedite policy

An active security incident or production outage may bypass normal readiness to
contain harm. The incident commander records the authority, scope, risk, and
verification plan. Missing traceability, tests, documentation, and follow-up
work are restored immediately after stabilization.
