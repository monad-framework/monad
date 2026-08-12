# Operations

Operations defines how MonadV2 is configured, released, observed,
kept reliable, and restored. Operational readiness is part of product
acceptance because users experience the running system, not the source tree.

## Operating documents

- `environments.md` — purpose, boundaries, data, access, and promotion.
- `deployment.md` — artifact promotion, migration, verification, and rollback.
- `observability.md` — signals, semantics, dashboards, alerts, and privacy.
- `reliability.md` — objectives, error budgets, capacity, continuity, and toil.
- `incident-response.md` — detection through learning and corrective work.

## Ownership

Each production capability has a service owner, support expectation, escalation
path, critical dependencies, dashboards, alerts, and runbooks. Ownership covers
user-impact outcomes and recovery, not just process uptime.

## Operational readiness gate

Before external production exposure:

- configuration and secrets are controlled and validated;
- release and rollback are automated and rehearsed;
- authoritative data backup and restore meet approved objectives;
- critical journeys, dependencies, and resource saturation are observable;
- alerts are actionable and routed to an available owner;
- capacity and unit cost are tested at expected and failure load;
- incident roles, communication, and evidence access are practiced;
- known risk and manual toil are accepted by accountable owners.

## Operating principle

Prefer simple, observable components and tested procedures over theoretical
resilience. Redundancy is useful only when failure is isolated, state remains
correct, and the team can operate and verify it under pressure.
