# System Context

## System of interest

MonadV2 is the system of interest. It accepts authorized user intent,
coordinates the primary workflow, integrates with bounded external services,
and returns a verifiable outcome with appropriate evidence.

## Actors

| Actor | Uses the system to | Trust and access considerations |
| --- | --- | --- |
| Responsible Practitioner | Complete and recover the primary workflow | Access limited to authorized resources and actions |
| Accountable Owner | Review outcomes, risk, adoption, and evidence | Aggregate access does not imply unrestricted payload access |
| Service Operator | Deploy, diagnose, mitigate, and restore | Privileged access is time-bounded, audited, and separated |
| Maintainer | Change code, configuration, and documentation | Changes require review and protected release paths |
| Affected Stakeholder | Exercise applicable data or decision rights | May not hold an ordinary product account |

## External systems

### Identity authority

Authenticates users and supplies stable subject and authentication context. The
product remains responsible for resource authorization. Unavailability blocks
new privileged sessions but does not erase established audit context.

### Data store

Persists authoritative domain and workflow state. Encryption, backup, restore,
schema compatibility, and access isolation are owned operational concerns, not
assumed provider properties.

### Communication or integration services

Deliver optional notifications or exchange bounded data with the surrounding
workflow. Their failures cannot be mistaken for completed domain outcomes.
Outbound data is minimized and classified before transmission.

### Observability system

Receives metrics, logs, and traces needed to operate the service. It must not
become an uncontrolled secondary store for secrets or business payloads.

### Source and artifact services

Host reviewed source, dependencies, build evidence, and release artifacts.
Protected branches, immutable provenance, least-privilege automation, and
artifact verification establish the software supply-chain boundary.

## Trust boundaries

1. Public or user-controlled clients to the application boundary.
2. Application runtime to privileged data and secret stores.
3. Product-controlled runtime to third-party services.
4. Build and release automation to production deployment authority.
5. Ordinary support access to restricted evidence and administrative actions.

Every crossing authenticates its peer where feasible, validates input, limits
authority, protects data in transit, and produces sufficient security evidence.

## Data flows

User input enters through a versioned contract, is classified and validated,
and is stored only by the owning capability. Derived results retain provenance
needed for verification. Evidence records identifiers and decisions rather than
unnecessary payloads. Exports and deletion follow the data lifecycle rather
than bypassing it through ad hoc operator access.

## Dependency policy

An external dependency receives an owner, purpose, data classification,
availability and latency expectation, failure behavior, cost budget, exit
strategy, and review date. The project does not treat a vendor service level as
an end-to-end guarantee.
