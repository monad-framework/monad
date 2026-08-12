# Acceptance Model

Acceptance confirms that the integrated product satisfies approved user and
system outcomes. Scenarios use stable requirement and use-case IDs and execute
through supported contracts.

## AC-001 — Authorized successful journey

Given an authenticated practitioner with valid authority and inputs, when the
primary workflow is confirmed, then one workflow instance reaches a verified
successful state, the expected result is available, and minimum necessary
evidence links actor, policy, state, and outcome.

## AC-002 — Invalid input

Given missing, malformed, out-of-range, or inconsistent input, when validation
runs, then no consequential effect occurs and the response identifies the
specific correction without exposing sensitive internals.

## AC-003 — Unauthorized action

Given an authenticated actor without permission for the resource or action,
when the request is attempted, then access is denied at the resource owner,
protected existence is not disclosed unnecessarily, and security evidence is
recorded.

## AC-004 — Duplicate request

Given an operation that has been accepted or completed, when the same
idempotency identity is submitted again, then no duplicate consequential effect
occurs and the caller receives the existing result or authoritative status.

## AC-005 — Interruption and recovery

Given an interruption at each durable workflow state, when the user reconnects
or the system retries, then completed work is preserved, allowed next actions
are accurate, and the workflow reaches a verified terminal or escalated state.

## AC-006 — Dependency failure

Given a timeout, throttling response, invalid dependency result, or unavailable
external service, when the workflow executes, then failure is contained,
bounded retry policy is honored, unknown effects enter reconciliation, and the
user receives an actionable status.

## AC-007 — User cancellation or reversal

Given a cancellable state, when the user cancels, then no disallowed later step
starts, compensation occurs where required, and the terminal outcome accurately
describes completed and reversed effects.

## AC-008 — Evidence access

Given an authorized accountable owner, when outcome evidence is requested, then
the system returns only permitted records with consistent definitions and
records the access. Unauthorized and over-broad queries are denied.

## AC-009 — Accessible primary journey

Given keyboard-only and supported screen-reader operation, when a representative
user completes the primary journey and encounters errors, then controls, focus,
status, validation, confirmation, and recovery remain understandable and
operable without relying on color or pointer input.

## AC-010 — Operational diagnosis

Given a simulated primary-journey failure, when the operator follows the alert
and runbook, then correlation and signals identify affected state, dependency,
and recent change without inspecting prohibited sensitive payloads.

## Acceptance evidence

Each scenario records environment, artifact, configuration, data set, result,
supporting logs or reports, reviewer, and deviations. Product accepts user
meaning; engineering accepts technical integrity; security and operations
accept their relevant evidence before release.
