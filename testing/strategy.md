# Test Strategy

## Risk model

Test depth increases with user harm, security or data consequence, complexity,
change frequency, dependency uncertainty, irreversibility, and defect history.
Trace critical risks to explicit tests or exercises and record residual risk.

## Test levels

### Static assurance

Formatting, linting, type and schema checks, policy checks, secret detection,
dependency analysis, license rules, and architecture constraints provide fast
feedback without executing the product.

### Unit and property tests

Verify domain invariants, policy decisions, state transitions, transformations,
and error classification in isolation. Property tests explore broad input and
sequence spaces for high-value invariants.

### Contract tests

Verify request, response, event, error, compatibility, timeout, and security
behavior at every owned boundary. Consumer and provider evidence must use the
same versioned contract.

### Integration tests

Verify adapters with real or production-faithful dependencies, including
schema, transaction, identity, network, and failure behavior. Emulators are not
accepted when they omit the behavior under test.

### Acceptance and journey tests

Verify the primary use cases through supported interfaces in a representative
environment. Include accessibility and human evaluation where automation cannot
establish the claim.

### Nonfunctional assurance

Performance, capacity, reliability, recovery, security, accessibility, and
operational exercises verify the quality scenarios and threat controls.

## Test data

Generate deterministic synthetic fixtures representing valid, invalid,
boundary, adversarial, legacy, and high-volume cases. Assign classification and
retention to test evidence. Production data requires exceptional documented
approval, minimization or protection, and a deletion plan.

## Environments

Unit and contract tests run on every change. Integration tests use isolated
ephemeral dependencies. Staging provides production-like topology for release,
performance, migration, security, and recovery checks. Environment differences
are recorded with the evidence they may invalidate.

## Failure and flakiness

A failed required test blocks its gate until behavior is corrected, the test is
proven invalid, or an authorized waiver exists. Rerunning to obtain a pass does
not erase failure. Flaky tests receive an owner, diagnosis evidence, containment,
and repair deadline; critical-path flaky tests block release confidence.

## Evidence retention

Record source revision, artifact, configuration, dependency versions,
environment, test selection, timestamps, results, logs, and reports. Retain
release evidence long enough to investigate the supported version and satisfy
applicable obligations.
