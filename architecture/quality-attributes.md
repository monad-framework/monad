# Quality Attributes

Quality attributes are evaluated as scenarios: source, stimulus, environment,
artifact, response, and measurable response. Initial budgets are provisional
until representative load and risk analysis approve the production baseline.

## QA-01 — Functional correctness

Given a valid, authorized request under normal operation, the system reaches one
allowed terminal state, applies each consequential effect at most once, and
returns evidence matching authoritative state. Property, example, and contract
tests cover invariants and boundary conditions.

## QA-02 — Availability and reliability

During the supported service window, the primary journey targets 99.9% monthly
availability and at least 99.5% valid-attempt completion excluding declared
maintenance. Measurement is end-to-end and cannot be inferred solely from
process uptime.

## QA-03 — Performance

At reference load, synchronous user interactions target p95 below 400 ms and
p99 below 1 s, excluding explicitly asynchronous work. Progress acknowledgment
occurs within 2 seconds. End-to-end workflow budgets are specified per use case
and include dependency time.

## QA-04 — Recoverability

For authoritative production data, the provisional recovery point objective is
15 minutes and recovery time objective is 60 minutes. Workflow recovery must
distinguish known uncommitted, committed, and unknown external effects. Restore
and reconciliation are exercised before production readiness and quarterly.

## QA-05 — Security

An unauthenticated or unauthorized actor cannot read or change protected
resources. Authentication, authorization, input, secret, cryptographic, and
audit controls fail closed for consequential operations. Critical findings
block release; high findings require remediation or explicit time-bounded risk
acceptance.

## QA-06 — Privacy

For a data-subject or administrator request, the system can identify purpose,
location, access, retention, export, and deletion behavior for in-scope data.
Telemetry and lower environments do not retain undeclared copies.

## QA-07 — Usability and accessibility

A representative new user can complete the primary journey without private
coaching. The supported interface targets WCAG 2.2 AA, full keyboard operation,
predictable focus, programmatic names and errors, and non-color communication.

## QA-08 — Observability

When journey success declines or latency exceeds budget, owned signals identify
the affected cohort, workflow state, dependency, and recent change without
requiring sensitive payload inspection. Critical alerts map to a runbook and
actionable owner.

## QA-09 — Modifiability

A compatible change inside one boundary should require changes only in that
boundary and its tests. Contract changes identify consumers through automated
compatibility evidence and follow a documented deprecation window.

## QA-10 — Cost efficiency

The system measures infrastructure and external-service cost per successful
primary outcome. Capacity protections prevent an individual tenant, actor, or
failure loop from exhausting the approved budget or degrading all users.

## Review and evidence

Each release maps these scenarios to tests, telemetry, exercises, or accepted
risk. A target may be tightened through normal baselining; weakening a target
requires product, architecture, and operational approval with user impact.
