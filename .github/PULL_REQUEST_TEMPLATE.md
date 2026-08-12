## Outcome

Describe the observable result of this change and why it is needed. Link the
issue, work packet, requirement, specification, risk, incident, or ADR that
authorizes it.

- Related record:
- Intended outcome:
- Affected users or operators:

## Change

Summarize the implementation and important design choices. Identify changed
contracts, state, data, dependencies, configuration, permissions, or deployment
behavior. List explicit exclusions so reviewers can distinguish omitted scope
from missed work.

## Acceptance evidence

For each acceptance criterion, link or describe the test, demonstration,
analysis, or review evidence. Include success, invalid input, unauthorized,
boundary, failure, retry, and recovery behavior when relevant.

## Risk and impact

- Security/privacy impact:
- Data/schema/migration impact:
- Compatibility/deprecation impact:
- Reliability/performance/cost impact:
- Accessibility and documentation impact:
- Deployment, observation, and rollback plan:

## Verification checklist

- [ ] Scope is authorized and satisfies the Definition of Ready.
- [ ] Tests cover changed behavior at the appropriate levels.
- [ ] Formatting, lint, type, contract, dependency, and secret checks pass.
- [ ] Requirements, specifications, ADRs, risk, and changelog are updated where
      needed.
- [ ] Errors, telemetry, and evidence contain no secrets or unnecessary
      sensitive data.
- [ ] Accessibility behavior is verified for affected interactions.
- [ ] Migration, configuration, deployment, and rollback are tested where
      applicable.
- [ ] No unrelated generated files, debug code, bypasses, or warnings remain.

## Reviewer guidance

Please distinguish blocking findings from advisory suggestions. Review the user
outcome, boundary and invariant correctness, failure and recovery, security and
data handling, tests, operability, and maintainability. Approval means the
change is safe to merge within the evidence provided; it does not transfer
ownership from the author or component owner.
