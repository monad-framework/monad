# Risk Register

Risks are uncertain events or conditions that could affect user outcomes,
safety, delivery, operation, or viability. Issues that have already occurred
belong in active work or incident management, with any remaining uncertainty
tracked here.

## Scale

Likelihood and impact are scored 1 (low) through 5 (very high). Exposure is
their product. Scores of 15–25 require immediate owner attention, 8–14 require
planned treatment, and 1–7 are monitored. Safety or legal severity may override
the numeric band.

## Active risks

| ID | Risk | L | I | Exposure | Response and leading indicator | Owner | State |
| --- | --- | ---: | ---: | ---: | --- | --- | --- |
| R-001 | Product is built before the core problem is validated | 4 | 5 | 20 | Complete WP-0001 before broad build; watch untested requirement count | Product owner | Treating |
| R-002 | Scope expands beyond one coherent primary journey | 4 | 4 | 16 | Enforce non-goals and increment gates; watch active personas and workflows | Product owner | Treating |
| R-003 | Workflow interruption causes duplicate or unknown effects | 3 | 5 | 15 | Specify idempotency, durable states, reconciliation, and failure tests | Architecture owner | Open |
| R-004 | Sensitive data is collected or copied without defined lifecycle | 3 | 5 | 15 | Approve inventory, classification, purpose, retention, and telemetry rules | Security owner | Open |
| R-005 | Generic quality targets are accepted without representative evidence | 4 | 4 | 16 | Baseline with reference load and recovery exercises before release | Engineering owner | Open |
| R-006 | External dependency failure becomes end-to-end product failure | 3 | 4 | 12 | Define budgets, timeouts, isolation, fallback, and exit strategy | Operations owner | Open |
| R-007 | Small-team operational load is unsustainable | 3 | 4 | 12 | Measure alerts, support, deployment effort, and toil during pilot | Operations owner | Open |
| R-008 | Documentation and implementation diverge | 3 | 3 | 9 | Trace requirements to tests; review docs in behavior changes | Engineering owner | Monitoring |

## Risk record requirements

Each risk includes cause, uncertain event, consequence, affected scope,
likelihood, impact, indicators, prevention, contingency, owner, review date, and
residual risk after treatment. Link corrective work and decision records.

## Review cadence

Review high exposure weekly and all active risks at each work-cycle and
increment review. Escalate when exposure increases, a trigger fires, treatment
misses its date, or a decision exceeds the owner's acceptance authority. Closed
risks retain final evidence and any resulting lesson or control.
