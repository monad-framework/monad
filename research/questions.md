# Research Questions

Questions are ordered by the cost of being wrong and their ability to change a
near-term decision. Each question closes when evidence supports a decision,
not merely when research activity ends.

## Priority 1 — Product viability

### RQ-001 — Is the core problem recurring and material?

- **Decision:** proceed, narrow, pivot, or stop the product hypothesis.
- **Method:** recent-event interviews, workflow observation, and artifact review.
- **Evidence threshold:** consistent failure pattern across representative
  users plus a quantified baseline and committed participation in a test.

### RQ-002 — Which user and journey should define the first release?

- **Decision:** freeze the primary persona and use case.
- **Method:** compare frequency, consequence, current alternatives, authority,
  reachability, and measurable improvement.
- **Evidence threshold:** one segment has a coherent high-value journey that can
  be tested end to end within initial constraints.

### RQ-003 — What does a verified successful outcome mean?

- **Decision:** approve product acceptance and measurement semantics.
- **Method:** domain interviews, existing evidence review, error analysis, and
  observed downstream use.
- **Evidence threshold:** practitioners and accountable owners agree on
  postconditions, tolerances, and partial or failed states.

## Priority 2 — Adoption and safety

### RQ-004 — Which trust signals and controls are required for adoption?

- **Decision:** confirmation, explanation, evidence, and human-review design.
- **Method:** prototype usability tests across normal and failure scenarios.
- **Evidence threshold:** representative users correctly understand outcome,
  limits, next action, and reversibility without private coaching.

### RQ-005 — Which data and authority does the journey actually require?

- **Decision:** data model, integration, identity, and privacy baseline.
- **Method:** task decomposition, data inventory, permission mapping, and least-
  privilege walkthrough.
- **Evidence threshold:** every field and privilege has a purpose, owner,
  lifecycle, and safe failure behavior.

## Priority 3 — Technical and operational feasibility

### RQ-006 — Can the primary workflow meet reliability and recovery needs?

- **Decision:** workflow and persistence architecture.
- **Method:** state-model exploration, fault injection, idempotency tests, and
  recovery exercise.

### RQ-007 — Can the product meet latency, capacity, and unit-cost budgets?

- **Decision:** implementation shape and dependency selection.
- **Method:** representative benchmark with realistic data and dependency
  behavior, including tail latency and failure loops.

### RQ-008 — Can a small team operate the service safely?

- **Decision:** pilot exposure and operational model.
- **Method:** deployment rehearsal, alert review, incident simulation, backup
  restore, and measured manual toil.

## Maintenance

Each question has one decision owner and review date in its linked finding or
experiment. Retire questions when the decision disappears, and add a new
question when material uncertainty is discovered rather than rewriting the old
question to match the answer.
