# WP-NNNN: Outcome-oriented title

- **Status:** candidate
- **Owner:** one accountable person
- **Parent increment:** INC-NNNN
- **Target work cycle:** WC-NNNN
- **Reviewers:** product, engineering, security, operations, or domain owners
- **Created:** YYYY-MM-DD
- **Target decision:** YYYY-MM-DD

## Outcome

Describe the observable result this packet will create and why it matters to the
increment. Use one paragraph that can later be evaluated as true or false.

## Context

Summarize current behavior, relevant evidence, constraints, and prior decisions.
Link requirements, specifications, ADRs, research findings, incidents, or risks
rather than duplicating them.

## Scope

- Included behavior, boundaries, artifacts, and environments.
- Required quality, security, data, operations, and documentation work.
- Integration or migration needed for a complete result.

## Exclusions

- Name tempting adjacent work that this packet will not perform.
- State where deferred work is recorded and what would trigger it.

## Acceptance criteria

1. Given explicit preconditions, when the supported action occurs, then the
   expected observable result and evidence are produced.
2. Invalid, unauthorized, boundary, and dependency-failure behavior is verified
   where relevant.
3. Affected quality budgets, compatibility, accessibility, telemetry, and
   recovery expectations pass their defined checks.
4. Documentation and sources of truth describe the delivered behavior.

## Evidence plan

| Claim | Evidence | Location | Reviewer |
| --- | --- | --- | --- |
| Primary behavior works | Acceptance test or demonstration | Link when produced | Product owner |
| Boundary contract holds | Contract or integration test | Link when produced | Engineering reviewer |
| Risk is controlled | Security, performance, or recovery evidence | Link when produced | Concern owner |

## Execution plan

List the smallest ordered steps, emphasizing early integration and the earliest
point at which the riskiest assumption can be tested. This is a plan, not a
commit-by-commit prescription.

## Dependencies and access

Name blocking decisions, upstream artifacts, environments, test data, accounts,
or reviewers. Confirm availability before marking Ready.

## Risks and rollback

Describe failure impact, containment, reversibility, data migration, feature
exposure, and the condition that stops or rolls back the work.

## Completion record

- **Final status:** done, cancelled, or superseded
- **Completed:** YYYY-MM-DD
- **Evidence:** links to tests, reviews, release, or findings
- **Decisions and deviations:** what changed from the packet and why
- **Follow-up:** separately identified work with owners
