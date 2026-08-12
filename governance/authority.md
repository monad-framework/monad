# Authority Model

## Roles

Roles describe decision responsibility and may be held by one person in a small
project. When one person holds conflicting roles, the decision record states the
exception and obtains independent review for high-consequence changes.

| Role | Accountable for | May approve |
| --- | --- | --- |
| Project Steward | Mission, governance, sustainability, and final escalation | Vision and existential direction |
| Product Owner | User outcomes, requirements, priorities, and acceptance | Product baseline and scope within strategy |
| Architecture Owner | Boundaries, quality trade-offs, and strategic technical choices | Architecture baseline and ADRs |
| Engineering Owner | Delivery method, implementation quality, and technical integration | Engineering plans and completed technical work |
| Security Owner | Security risk, controls, vulnerability response, and exceptions | Security baseline and risk treatment within delegated limit |
| Operations Owner | Service objectives, deployment, continuity, and incident readiness | Operational readiness and production changes |
| Document Owner | Accuracy, review, and lifecycle of an assigned record | Editorial and scoped document changes |

## Decision rights

Routine, reversible decisions remain with the owner closest to the work when
they preserve approved requirements, contracts, budgets, and controls. Changes
crossing ownership boundaries require affected owners. A decision changing
vision, public promise, accepted risk, legal posture, or irreversible commitment
requires the accountable role identified by governance.

## Approval matrix

| Decision | Accountable | Required concurrence |
| --- | --- | --- |
| Vision or non-goal change | Project Steward | Product Owner |
| Product baseline or release scope | Product Owner | Engineering; Security/Operations when affected |
| System boundary or strategic dependency | Architecture Owner | Owning components; Security/Operations when affected |
| Production release | Product Owner | Engineering, Security, and Operations readiness |
| Security risk acceptance | Security Owner within limit; Steward above limit | Affected product and operations owners |
| Emergency mitigation | Incident Commander | Retrospective approval after stabilization |
| Data-purpose or retention change | Product Owner | Security/privacy authority and data owner |

## Separation of duties

No person should unilaterally author, approve, and deploy a high-consequence
production change. Releases, privileged access, security exceptions, and
destructive data operations use independent confirmation where practical.
Automation may enforce approval but does not own the decision.

## Delegation

Delegation states scope, permitted decisions, limits, start and end dates,
reporting expectations, and revocation. Delegated authority cannot be
re-delegated unless explicitly allowed and never exceeds the delegator's own
authority.

## Escalation

Escalate when owners disagree on a cross-boundary risk, a decision exceeds
delegated limits, a required owner is unavailable beyond the decision window,
or evidence reveals a legal, ethical, or safety concern. Escalation packages the
decision, options, evidence, deadline, impact of delay, and recommendation.
