# System Boundaries

## Boundary model

Boundaries isolate reasons to change, authority, data ownership, and failure.
They are logical before they are physical: two modules in one process can have
a stronger boundary than two services sharing a database.

## Owned boundaries

| Boundary | Owns | Does not own |
| --- | --- | --- |
| Experience | Presentation, interaction state, accessibility | Domain truth, authorization policy |
| Application | Use-case orchestration and contract mapping | Business invariants, vendor behavior |
| Workflow | Durable workflow state and transition policy | Domain data, presentation |
| Policy | Versioned rule evaluation and explanations | Workflow progression, identity proofing |
| Domain | Business invariants and authoritative domain state | Transport, deployment, external SDKs |
| Evidence | Append-oriented evidence, access, retention | Primary business state |
| Adapters | Translation to external systems | Core policy or cross-provider abstractions |
| Operations | Deployment, telemetry, continuity, response | Product behavior decisions |

## Allowed dependency direction

- Experience depends on published application contracts.
- Application depends on domain, workflow, policy, and evidence ports.
- Domain code depends only on domain-owned abstractions and stable shared
  primitives with no infrastructure behavior.
- Adapters implement inward-facing ports and translate external failure models.
- Operations configures and observes deployables without importing product
  policy into delivery automation.

Reverse dependencies use interfaces, events, or explicit composition. Direct
imports, shared mutable storage, and hidden callbacks across ownership
boundaries are prohibited.

## Data ownership

A boundary may read another owner's data only through an approved contract or
owned replica. Cross-owner writes are not permitted. Derived views identify
their source, freshness, rebuild procedure, and behavior when lagged or
unavailable.

## Transaction boundaries

Atomic transactions remain within one data owner. Multi-owner outcomes use a
durable coordinator and explicit steps. Each step states whether it is
idempotent, retryable, compensatable, or irreversible. Unknown outcomes enter
reconciliation rather than blind retry.

## Trust and privilege boundaries

User, operator, service, build, and deployment identities are distinct. Service
identity does not grant unrestricted domain access. Administrative actions use
separate authorization, stronger authentication when warranted, auditable
purpose, and a bounded session.

## Boundary change test

A change to ownership, dependency direction, data authority, public contract,
or trust relationship requires an ADR and migration plan. Deployment separation
alone does not create ownership; merging deployables does not remove it.
