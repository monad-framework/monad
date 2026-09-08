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
- [ ] Relevant requirements, specifications, ADRs, risks, policies, and
      dependencies are linked.
- [ ] Task/test/evidence decomposition is bounded enough that implementation can
      begin without guessing about public semantics or authority.
- [ ] Preconditions, required access, environments, test data, external
      resources, provider capabilities, and integration dependencies are
      available or explicitly simulated.
- [ ] Security, privacy, accessibility, operations, documentation, data
      classification, secret handling, and audit impacts have been assessed.
- [ ] Agent/plugin/integration capabilities and the least-authority boundary are
      explicit where automation is involved.
- [ ] Required autonomy level is named; any level above advisory has an accepted
      promotion basis and a demotion/revocation path.
- [ ] Unknowns are either resolved or converted into bounded research work.
- [ ] The owner believes the packet can reach Done without hidden external
      approval or another unplanned packet.

## Additional checks for behavior changes

- [ ] User and system behavior is specified for success, invalid input,
      unauthorized action, dependency failure, interruption, timeout,
      cancellation, retry, and circuit-breaker behavior as relevant.
- [ ] Compatibility and migration impact is understood.
- [ ] Test approach includes the appropriate unit, contract, integration,
      acceptance, accessibility, performance, determinism, privacy, or security
      level.
- [ ] Required telemetry, audit events, health behavior, and support behavior are
      explicit.
- [ ] Cache/vector/file/hosted state has declared provenance, isolation,
      invalidation/retention, and rebuild/recovery behavior where applicable.

## Additional checks for agent, AI, plugin, or integration work

- [ ] Canonical facts, derived facts, proposals, uncertain inference, and
      external evidence cannot be conflated silently.
- [ ] Prompt-injection, secret-exposure, tool escalation, and untrusted-input
      threats have explicit negative tests where relevant.
- [ ] Provider/model selection constraints include capability, privacy, cost,
      latency, locality, and fallback expectations as applicable.
- [ ] Retry/idempotency, timeout/cancellation, rate/cost budgets, and side-effect
      risk are defined.
- [ ] Cross-harness or human review requirements and disagreement-disposition
      rules are explicit for consequential work.

## Additional checks for architecture or infrastructure

- [ ] Decision drivers and quality scenarios are identified.
- [ ] Strategic choices have an ADR or an assigned decision packet.
- [ ] Deployment, configuration, rollback, capacity, cost, ownership, isolation,
      and air-gap/on-prem/cloud implications are addressed as applicable.
- [ ] Dependency risk and exit or containment strategy are understood.
- [ ] Public protocol/schema/plugin/storage/MCP/LSP/attestation surfaces have an
      explicit versioning/compatibility plan before stability is promised.
- [ ] Cryptographic work states algorithm profile, key lifecycle, rotation,
      revocation, migration, and multi-party policy requirements where relevant.
- [ ] Performance claims name a reproducible reference workload/profile rather
      than relying on an unqualified headline number.

## Readiness authority

The packet owner performs the initial check. Product accepts user outcome and
scope; engineering accepts feasibility and evidence; security, privacy,
operations, or governance review when their risk threshold is crossed. A
reviewer may mark a packet not ready with a specific unmet criterion and the
smallest corrective action.

Agent-generated readiness assessments are advisory unless a separately accepted
policy grants a bounded machine-enforcement role. Readiness never authorizes
execution by itself.

## Expedite policy

An active security incident or production outage may bypass normal readiness to
contain harm. The incident commander records the authority, scope, risk,
capability boundary, and verification plan. Missing traceability, tests,
documentation, audit evidence, and follow-up work are restored immediately after
stabilization.

## Additional AI-Driven Engineering Readiness Checks

For work executed under the AI-driven operating model:

- [ ] The applicable autonomy profile is explicit: AI-assisted, AI-driven, or
      bounded AI-autonomous.
- [ ] The governed context basis is identifiable and preserves authority,
      freshness, provenance, and material unresolved contradictions.
- [ ] Material ambiguity has been resolved or has an explicit
      clarification/decision route.
- [ ] The proposed engineering pathway identifies mandatory gates and does not
      treat optional pathway adaptation as authority to bypass them.
- [ ] Consequential AI decisions/effects are bounded by explicit authority,
      capability, policy, and escalation conditions.
- [ ] Any bounded AI-autonomous delegation defines scope, limits, evidence,
      reporting, revocation, and expiration/termination behavior as applicable.
- [ ] Governing-input drift has an explicit suspend, recompile, reauthorize,
      replan, EOSC, or cancellation disposition.
- [ ] Required review independence is defined in a way that cannot be satisfied
      through trivial executor self-review.
- [ ] Executor completion cannot satisfy acceptance solely through self-report.
- [ ] Provider/model/harness replacement does not broaden authority or weaken
      governing obligations.
