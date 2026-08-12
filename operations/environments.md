# Environments

Environments provide controlled levels of fidelity and exposure. Configuration
changes across environments; the released artifact does not.

## Local development

Used for fast implementation and deterministic tests. Uses synthetic or
approved sanitized data, least-privilege developer credentials, reproducible
dependency versions, and no implicit production access. Local success is not
release evidence.

## Continuous integration

Created from clean source to run static analysis, unit, contract, integration,
security, and packaging checks. Jobs receive short-lived, scoped credentials.
Artifacts are immutable, identified, and accompanied by provenance and test
evidence.

## Test or integration

Validates component interaction, migrations, and dependency adapters with
representative topology. Test data is controlled and resettable. Shared state
must not make tests order-dependent or leak between contributors.

## Staging

Mirrors the production architecture and configuration shape closely enough for
release, performance, security, recovery, and operational checks. It does not
receive uncontrolled production copies. Differences from production are
documented and included in risk review.

## Production

Processes real authorized use under published service, security, data, and
support commitments. Access is strongly authenticated, least-privilege,
time-bounded where possible, and audited. Direct mutation bypassing the product
or approved operational procedure is prohibited except during an authorized
incident.

## Promotion

Source produces one verified artifact. The artifact is promoted through
environments with environment-specific configuration and approval. Rebuilding
for production is prohibited because it breaks provenance. Schema and contract
changes remain compatible through the promotion and rollback window.

## Data and access matrix

Every environment records permitted data classes, identity source, network
boundary, secret source, retention, backup, external integrations, logging
level, and access approvers. Review the matrix before a new data class,
integration, or privileged role is enabled.

## Ephemeral environments

Short-lived review environments use isolated names, data, credentials, and
budgets. They expire automatically and produce no dependency for production or
long-term evidence.
