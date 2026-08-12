# Observability

Observability connects internal behavior to user outcomes and operator action.
Collect the minimum signals needed to detect, diagnose, explain, and improve the
service without turning telemetry into an uncontrolled sensitive-data store.

## Signal model

- **Metrics:** aggregate demand, success, latency, errors, saturation, cost, and
  business-outcome rates.
- **Logs:** structured discrete events with severity, service, environment,
  correlation, event name, outcome, and safe diagnostic attributes.
- **Traces:** end-to-end causality and latency across the primary journey and
  dependencies.
- **Profiles or diagnostics:** restricted, time-bounded evidence for measured
  resource problems.

## Required journey signals

Instrument eligibility, start, validation result, confirmation, durable state
transition, dependency attempt, verification, terminal outcome, recovery, and
repeat use. Event names and outcome categories must match product and data
specifications.

## Correlation

Propagate a non-secret correlation ID across supported boundaries. Keep workflow
and request IDs distinct where their lifetimes differ. Do not use email,
username, access token, or raw business data as a correlation key.

## Dashboards

The service overview shows user-impact success, latency distributions, error-
budget burn, demand, saturation, dependency health, deployment markers, and
unit cost. Drill-down follows the workflow state and error taxonomy. Dashboard
panels state source, unit, aggregation, and freshness.

## Alerts

Page only for actionable conditions requiring timely human response. Each alert
states user impact, urgency, owning service, runbook, and safe first checks.
Ticket sustained lower-urgency degradation. Review noisy, unactionable, or
duplicate alerts as operational defects.

## Data protection

Default to deny-list plus allow-list structured fields at boundaries; redact
secrets and sensitive values before emission. Set retention by diagnostic and
legal need, restrict access, audit privileged queries, and test that prohibited
data does not enter telemetry.

## Telemetry reliability

The product must continue safely when optional telemetry is degraded. Buffer or
sample within bounded resource limits, expose dropped-signal health, and never
block a critical user result solely to preserve nonessential observability.
