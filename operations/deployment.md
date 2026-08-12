# Deployment

## Release artifact

A deployment uses an immutable artifact built once from an identified commit.
The artifact includes or links provenance, dependency inventory, checksums,
test evidence, configuration schema version, and release notes. Production
verifies identity and integrity before activation.

## Standard deployment flow

1. Confirm approved change scope and release quality gates.
2. Verify artifact identity, provenance, vulnerability state, and compatibility.
3. Validate target configuration, secrets references, capacity, and dependency
   health.
4. Apply backward-compatible data changes before behavior that depends on them.
5. Expose the release incrementally when the platform supports safe progressive
   delivery.
6. Run automated smoke, contract, security, and journey checks.
7. Observe user outcomes, errors, latency, saturation, and cost during the
   defined window.
8. Complete, pause, roll back, or initiate incident response using explicit
   thresholds.

## Database and state change

Use expand-migrate-contract: introduce compatible structures, deploy behavior
that can operate across versions, migrate and verify data, then remove old
structures only after rollback and consumer windows close. Destructive changes
require backup or compensating recovery, reconciliation evidence, and major
change approval.

## Rollback

Rollback restores the last known safe artifact and configuration without
assuming data can move backward. Define triggers such as failed journey checks,
error-budget burn, integrity mismatch, security exposure, or unknown state.
When rollback cannot restore correctness, stop exposure and execute a forward
fix or compensation under incident control.

## Deployment evidence

Record change ID, artifact digest, actor, approvals, environment, configuration
version, start and end times, migration result, checks, observed signals,
progressive steps, final decision, and rollback if used. Evidence must be
queryable by incident responders.

## Access and safety

Deployment identities are separate from developer identities, scoped to the
target environment, and protected from untrusted pull-request code. Manual
production deployment is an exception with the same approval and evidence
requirements as automation.
