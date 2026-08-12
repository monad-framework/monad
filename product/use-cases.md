# Use Cases

**Status:** Proposed stabilization baseline

## UC-001 — Inspect a repository

An engineer runs Monad on a supported repository and receives repository identity, discovered artifact classes, configuration resolution, semantic summary, and blocking diagnostics.

## UC-002 — Build and inspect the semantic graph

Monad compiles canonical artifacts into stable nodes/relationships with provenance and exposes graph statistics and selected neighborhoods.

## UC-003 — Validate engineering knowledge

Monad reports missing identifiers, unresolved references, invalid status/authority relationships, stale generated projections, or other MVP invariants using machine-readable diagnostics.

## UC-004 — Explain an engineering entity

A user asks why a requirement/spec/component/Work Packet exists or what governs it. Monad traverses typed relationships and returns a provenance-backed explanation.

## UC-005 — Query traceability

A user asks questions such as specifications without tests, requirements without implementation evidence, work without authority, or dependents of an interface.

## UC-006 — Determine semantic impact

Given a change set, Monad identifies affected semantic entities and relevant validation/tooling scope. Full optimized execution may mature after MVP, but impact understanding begins in the semantic kernel.

## UC-007 — Generate bounded Codex context

Given an authorized Work Packet, Monad returns governing requirements/ADRs/specifications, in-scope targets, dependencies, prohibitions, relevant graph neighborhood, acceptance criteria, and validation commands while excluding unrelated content by default.

## UC-008 — Verify reproducibility

A clean checkout with equivalent inputs reproduces the same semantic identity/graph/diagnostic results within documented platform allowances.

## UC-009 — Project engineering state

Later, Monad can derive documentation, GitHub status, dashboards, or publication views from canonical semantic state while preserving their non-authoritative projection status.

## MVP use-case gate

UC-001 through UC-005, UC-007, and UC-008 are required MVP vertical-slice behavior. UC-006 may begin with impact reporting; optimized execution is not required to prove MVP. UC-009 is represented by the current machine/documentation mechanisms but does not need a general projection engine in MVP.