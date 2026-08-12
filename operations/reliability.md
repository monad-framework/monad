# Reliability

Reliability means the intended user outcome succeeds within its defined
conditions and can be restored when it does not. Service objectives manage the
trade between product change and operational stability.

## Service indicators

- valid primary-journey completion rate;
- availability of required synchronous interactions;
- interactive and end-to-end latency distributions;
- workflow recovery and reconciliation success;
- freshness and correctness of user-visible state;
- durability and restore success for authoritative data;
- dependency contribution to failure and latency;
- cost and saturation per successful outcome.

## Initial objectives

Provisional targets are 99.9% monthly availability for the supported service
window, 99.5% valid primary-journey completion, p95 interactive latency below
400 ms, 15-minute RPO, and 60-minute RTO. These become commitments only after
representative baselining and accountable approval.

## Error-budget policy

The allowed unreliability is the difference between perfect service and the
approved objective. Fast burn pauses risky releases and prioritizes containment.
Sustained budget exhaustion requires corrective reliability work before feature
expansion. A healthy budget does not justify known critical safety or security
risk.

## Resilience controls

Use bounded timeouts, retries with jitter only for safe transient operations,
idempotency, concurrency and rate limits, bulkheads, circuit behavior, backpressure,
capacity margin, graceful degradation, and reconciliation. Each control must
have telemetry and a failure-mode test; retries are not resilience when they
amplify dependency failure.

## Continuity

Back up authoritative state according to classification and recovery point.
Protect backups with separate access and integrity controls. Restore into an
isolated environment, verify application-level correctness, and exercise the
full recovery decision at least quarterly before production maturity.

## Capacity and cost

Test expected, peak, burst, dependency-degraded, and recovery load with
representative data. Define saturation thresholds and scaling delay. Protect
the service with per-actor and global budgets so an error loop or abusive client
cannot exhaust shared capacity or cost.

## Toil

Track repetitive manual operational work, interruption burden, privileged
repair, alert load, and deployment effort. Automate high-frequency, well-
understood procedures while preserving review and rollback for consequential
actions.
