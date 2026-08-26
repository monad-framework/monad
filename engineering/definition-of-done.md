# Definition of Done

Done means the intended behavior or evidence is integrated, verified,
documented, operable, traceable, and accepted. Code complete, review requested,
PR merged, or works on one machine are intermediate states.

## Required for every work packet

- [ ] Every acceptance criterion has linked passing evidence.
- [ ] The change is reviewed and all blocking findings are resolved.
- [ ] Automated checks pass in the protected integration path.
- [ ] New and changed behavior has appropriate positive, negative, boundary,
      determinism, security/privacy, and regression tests.
- [ ] Documentation, specifications, diagrams, decisions, policies, and
      changelog entries are accurate where affected.
- [ ] No credential, sensitive data, generated noise, debug bypass, unexplained
      warning, hidden authority expansion, or untracked external state is
      introduced.
- [ ] Known limitations and follow-up work are recorded with owners.
- [ ] The packet owner and required acceptance authority mark the work complete.
- [ ] Consequential actions, decisions, reviews, executions, and resulting
      artifacts are linked through the required audit/evidence model.
- [ ] When policy requires it, DSSE-compatible attestations are valid, linked to
      exact source/artifact/evidence identities, and accepted by the protected
      integration/release gate.

## Product quality

- [ ] The result is demonstrated through the supported user or system contract.
- [ ] Errors and recovery are actionable and consistent with the product model.
- [ ] Accessibility checks pass for affected user interactions.
- [ ] Compatibility is preserved or the approved migration path is complete.
- [ ] Scores, dashboards, AI summaries, and automation views link back to the
      underlying governed evidence rather than becoming opaque truth.

## Agent, AI, plugin, and integration quality

- [ ] Agent/provider/plugin/integration capabilities stay within the authorized
      least-privilege boundary.
- [ ] Canonical fact, derived fact, proposal, uncertain inference, stale state,
      and external evidence remain distinguishable.
- [ ] Prompt-injection, secret masking, capability escalation, and untrusted-input
      controls pass relevant negative tests.
- [ ] Retry/idempotency, timeout/cancellation, circuit-breaker, cost/rate budget,
      and failure-isolation behavior is verified where applicable.
- [ ] Required cross-harness/human review is complete and disagreements have an
      explicit disposition.
- [ ] Autonomy promotion evidence is recorded; newly demonstrated unreliability
      triggers demotion/revocation or an explicit risk disposition.

## Security, identity, cryptography, and data

- [ ] Threats introduced or changed by the work are reviewed.
- [ ] Authentication, authorization, validation, secrets, encryption,
      attestations, evidence, tenant/workspace isolation, and privacy controls
      are tested where relevant.
- [ ] Data ownership, classification, retention, migration, deletion, cache
      invalidation, and rebuild/recovery remain correct.
- [ ] Key generation/use/rotation/revocation and multi-party approval rules are
      verified for cryptographic changes.
- [ ] Algorithm/version identifiers are explicit; post-quantum or other crypto
      migration does not rewrite historical semantic meaning.
- [ ] Dependency, plugin, adapter, and artifact provenance checks pass with no
      unaccepted blocking finding.

## Operations, observability, and reliability

- [ ] Health, demand, errors, saturation, journey, execution, and cost/token
      telemetry are present where relevant and contain no prohibited sensitive
      payload.
- [ ] Required structured logs, metrics, and traces correlate to Work
      Packet/execution/evidence identifiers through OpenTelemetry-compatible
      boundaries where applicable.
- [ ] Alerts are actionable, owned, and linked to response guidance.
- [ ] Deployment, configuration, migration, rollback/restore, air-gap boundary,
      and recovery behavior is tested at the appropriate level.
- [ ] Performance and cost remain within approved budgets or have explicit
      evidence/risk disposition.
- [ ] Any throughput or state-finalization claim names the exact reference
      hardware/workload/profile and cannot be inferred from a different class of
      operation.

## Increment and release completion

In addition to packet completion, an increment is Done only when integrated
acceptance passes, unresolved work is explicitly re-planned, risk and status are
updated, and the review decision is recorded. A release also requires security,
privacy, operational, product, change, compatibility, provenance, and
attestation approvals defined by its quality gates.

Release completion cannot be inferred from merged code, model consensus,
performance headline numbers, or a dashboard score.

## Waivers

A waiver names the unmet criterion, reason, user and operational impact,
compensating control, accountable approver, expiration, and corrective work.
Waivers cannot conceal an unaccepted critical risk, cannot grant unbounded agent
authority, and do not redefine Done.
