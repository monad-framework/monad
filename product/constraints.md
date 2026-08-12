# Product Constraints

Constraints are facts or commitments that bound acceptable solutions. Each
constraint should have an owner and be revisited when its underlying condition
changes.

## User and experience constraints

- The primary journey must remain understandable without internal technical
  knowledge.
- Supported accessibility modes are part of release acceptance.
- Consequential actions require visible effect, authority, and confirmation.
- Interruption and low-confidence states must not be presented as success.

## Scope constraints

- The first release supports one primary persona and one end-to-end journey.
- Unsupported workflows stop explicitly rather than being approximated.
- New integrations require measured outcome or adoption evidence.
- Administrative breadth follows operational need, not speculative completeness.

## Data constraints

- Collect only data required for a declared purpose.
- Classify inputs and outputs before production use.
- Define residency, retention, deletion, export, and backup behavior.
- Never use production personal or confidential data in development or tests
  without an approved protected process.

## Security and compliance constraints

- All access is authenticated and authorized at the protected resource.
- Secrets are managed outside source code and ordinary configuration files.
- Critical dependencies and release artifacts require provenance and integrity
  checks.
- Compliance claims require mapped obligations and control evidence; the
  repository does not imply certification.

## Technical constraints

- Public interfaces are explicitly versioned and compatibility-tested.
- Components expose health and correlation signals for critical journeys.
- State-changing operations are idempotent or have a documented compensation.
- Deployment and rollback are automated and produce reviewable evidence.

## Delivery constraints

- The project favors a small team and low coordination overhead.
- Work is sliced vertically so each increment can demonstrate user or risk
  value.
- A strategic dependency must have an exit, containment, or continuity plan.
- Cost is measured per successful outcome and must remain within an approved
  budget.

## Constraint review

Review constraints at product-baseline, architecture, and release-readiness
gates. A proposed exception names the affected scope, duration, risk, controls,
owner, and removal date. Permanent exceptions become explicit decisions rather
than lingering waivers.
