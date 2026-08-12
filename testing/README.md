# Testing and Quality Assurance

Testing produces evidence about product promises, system invariants, risks, and
operational readiness. It cannot prove the absence of every defect, so the test
system prioritizes consequence, uncertainty, and representative behavior.

## Test documents

- `strategy.md` defines levels, ownership, data, environments, and evidence.
- `acceptance.md` makes the primary user and system outcomes executable.
- `performance.md` defines workload, method, budgets, and analysis.
- `quality-gates.md` states the evidence required at change and release stages.

## Quality principles

- Test behavior at the cheapest level that gives trustworthy evidence.
- Keep most tests deterministic, isolated, fast, and diagnosable.
- Use contract tests at ownership boundaries and a smaller number of integrated
  journey tests for composition.
- Test failure, retry, interruption, concurrency, and recovery—not only the
  successful demonstration path.
- Use production-like structure and synthetic representative data without
  copying uncontrolled sensitive data.
- Treat flaky tests as defects; quarantine only with owner and repair deadline.
- Preserve evidence by artifact, environment, configuration, and source version.

## Ownership

Authors own tests for their changes. Component owners maintain contract and
invariant suites. Product owns acceptance meaning. Security owns elevated
security assurance. Operations owns deployment, resilience, backup, and restore
exercises. Quality is shared; no testing role is a downstream gatekeeper for
work designed without testability.
