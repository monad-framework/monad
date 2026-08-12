# Performance and Capacity Testing

Performance testing determines whether the product meets user, reliability, and
cost budgets under representative and adverse conditions. It is not a race for
the highest synthetic request count.

## Workload model

Define active users, request and workflow mix, payload distributions, state
cardinality, concurrency, arrival pattern, read/write ratio, dependency latency
and error behavior, background work, cache state, and data volume. Base the
model on measured or explicitly forecast use and preserve its version.

## Test types

- **Baseline:** one-user and low-load cost and latency by operation.
- **Load:** expected sustained and daily peak demand.
- **Stress:** increasing demand to identify saturation and failure shape.
- **Spike:** rapid demand change and scaling response.
- **Soak:** sustained execution to expose leaks, drift, queues, and cost growth.
- **Dependency degradation:** timeout, throttle, partial response, and outage.
- **Recovery:** backlog drain, restart, failover, restore, and reconciliation.

## Provisional budgets

- p95 interactive response below 400 ms and p99 below 1 second at reference
  load, excluding explicitly asynchronous completion;
- progress acknowledgment within 2 seconds;
- no correctness loss or duplicate effect under supported concurrency;
- resource utilization remains below the approved saturation threshold with
  recovery margin;
- unit cost remains within the product-approved successful-outcome budget.

Workflow-specific completion budgets are defined in technical specifications
after the baseline is measured.

## Method

Use the release artifact and production-like topology, warm and cold cases,
representative data, controlled background load, synchronized clocks, and
instrumented dependencies. Run enough iterations to report distributions and
confidence, not a single favorable sample. Record test-client limits and verify
the generator is not the bottleneck.

## Analysis

Report throughput, concurrency, latency percentiles, errors by class, queue
depth, saturation, scaling, retry amplification, dependency time, resource and
external-service cost, and successful outcomes. Compare with the previous
accepted baseline and explain regressions.

## Pass and stop rules

Pass only when budgets hold with no integrity or guardrail failure. Stop a test
that threatens shared systems, exceeds cost authorization, corrupts state, or
invalidates measurement. A waiver includes user impact, exposure, evidence,
owner, and corrective deadline.
