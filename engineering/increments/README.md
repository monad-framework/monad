# Product Increments

An increment is an integrated, potentially releasable advance that proves a
bounded product outcome or retires a material risk. It combines all work needed
for acceptance rather than handing partially complete layers between teams.

## Naming and duration

Use `INC-NNNN-short-outcome.md`. An increment typically spans two to six work
cycles. If useful evidence cannot be demonstrated within that horizon, split
the outcome or authorize a separate exploration.

## Required content

- objective and parent milestone;
- user, system, or risk outcome;
- included and excluded requirements;
- architecture decisions and specifications;
- ordered work packets and dependency chain;
- acceptance, quality, security, operations, and documentation evidence;
- release or exposure strategy and rollback;
- capacity assumption, forecast, and decision dates;
- active risks and stop conditions.

## Increment review

The review demonstrates the integrated result in a representative environment,
not a slide summary or collection of component reports. Reviewers inspect
acceptance evidence, failed or waived gates, user findings, service behavior,
cost, and risks. The recorded decision is `accept`, `accept with corrective
work`, `continue`, `re-scope`, or `stop`.

## Closure

An increment closes only after its review decision, status, risk changes,
changelog impact, and unfinished work are recorded. Work that no longer advances
the outcome is removed rather than carried as historical obligation.
