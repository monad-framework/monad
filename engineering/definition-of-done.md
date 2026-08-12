# Definition of Done

Done means the intended behavior or evidence is integrated, verified,
documented, operable, and accepted. Code complete, review requested, or works on
one machine are intermediate states.

## Required for every work packet

- [ ] Every acceptance criterion has linked passing evidence.
- [ ] The change is reviewed and all blocking findings are resolved.
- [ ] Automated checks pass in the protected integration path.
- [ ] New and changed behavior has appropriate positive, negative, boundary,
      and regression tests.
- [ ] Documentation, specifications, diagrams, decisions, and changelog entries
      are accurate where affected.
- [ ] No credential, sensitive data, generated noise, debug bypass, or
      unexplained warning is introduced.
- [ ] Known limitations and follow-up work are recorded with owners.
- [ ] The packet owner and required acceptance authority mark the work complete.

## Product quality

- [ ] The result is demonstrated through the supported user or system contract.
- [ ] Errors and recovery are actionable and consistent with the product model.
- [ ] Accessibility checks pass for affected user interactions.
- [ ] Compatibility is preserved or the approved migration path is complete.

## Security and data

- [ ] Threats introduced or changed by the work are reviewed.
- [ ] Authentication, authorization, validation, secrets, encryption, evidence,
      and privacy controls are tested where relevant.
- [ ] Data ownership, classification, retention, migration, and deletion remain
      correct.
- [ ] Dependency and artifact checks pass with no unaccepted blocking finding.

## Operations and reliability

- [ ] Health, demand, errors, saturation, and journey telemetry are present and
      contain no prohibited sensitive payload.
- [ ] Alerts are actionable, owned, and linked to response guidance.
- [ ] Deployment, configuration, migration, rollback, and recovery behavior is
      tested at the appropriate level.
- [ ] Performance and cost remain within budgets or have approved evidence.

## Increment and release completion

In addition to packet completion, an increment is Done only when integrated
acceptance passes, unresolved work is explicitly re-planned, risk and status are
updated, and the review decision is recorded. A release also requires security,
operational, product, and change approvals defined by the quality gates.

## Waivers

A waiver names the unmet criterion, reason, user and operational impact,
compensating control, accountable approver, expiration, and corrective work.
Waivers cannot conceal an unaccepted critical risk and do not redefine Done.
