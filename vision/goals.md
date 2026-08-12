# Goals

**Status:** Proposed foundation baseline

Monad's goals describe durable outcomes. They do not authorize specific implementation technologies or imply that every long-term capability belongs in MVP Release 1.

## G-01 — Build a trustworthy semantic model of engineering knowledge

Monad must represent meaningful engineering entities, relationships, authority, identity, and provenance in a deterministic graph derived from canonical project artifacts.

**Evidence:** equivalent inputs produce equivalent graph semantics; representative relationships are correct and explainable; invalid or ambiguous input produces diagnostics rather than fabricated certainty.

## G-02 — Make impact inspectable before execution

A user must be able to ask what a change affects and understand why those artifacts, tests, tasks, or policies are included.

**Evidence:** affected-set results are conservative, explainable, and validated against representative repository changes.

## G-03 — Coordinate native tools deterministically

Monad should decide what work should run, why, and in which dependency order while leaving language- and ecosystem-specific mechanics to native tools.

**Evidence:** one polyglot vertical slice produces a serializable execution plan, invokes real native tools, captures outcomes, and is reproducible from declared inputs.

## G-04 — Give humans and AI agents bounded engineering context

Monad should calculate task-relevant context from semantic relationships, governing artifacts, authorization, and acceptance criteria instead of relying on arbitrary repository dumps.

**Evidence:** context packages are minimal enough to review, sufficient for representative tasks, attributable to canonical sources, and reproducible.

## G-05 — Preserve engineering history and provenance

A reviewer should be able to trace meaningful behavior from intent and decisions through implementation, tests, releases, and evidence.

**Evidence:** stable identifiers and machine-readable relationships connect requirements, specifications, ADRs, work, implementation, verification, and produced artifacts where those links exist.

## G-06 — Remain local-first and provider-agnostic

The semantic kernel, validation, query, planning, and local execution loop must work without a Monad-hosted service and without a particular AI provider.

**Evidence:** Release 1 acceptance can run locally with network access disabled except where a deliberately external native dependency is part of the tested scenario.

## G-07 — Support progressive adoption

A repository should receive useful inspection and validation before it has been rewritten around Monad-specific formats. Explicit Monad metadata should deepen the model rather than be required for basic value.

**Evidence:** a representative existing repository can be inspected and modeled through adapters and conventions, then gains stronger semantics when explicit specifications or configuration are added.

## G-08 — Dogfood Monad on Monad

Monad should increasingly operate the engineering system used to build itself.

**Evidence:** by Release 1, Monad can inspect significant portions of its own repository, validate its semantic artifacts, generate useful agent context, and execute at least part of its own verification plan.

## G-09 — Deliver through vertical slices

Planning should prefer end-to-end usable capabilities over large horizontal subsystems with no integrated user outcome.

**Evidence:** every implementation increment produces demonstrable behavior that crosses the minimum required layers and includes tests, diagnostics, and documentation.

## G-10 — Make governance useful rather than ceremonial

Authority, ADRs, specifications, work packets, reviews, and machine projections must reduce ambiguity and improve decisions, not become paperwork detached from delivery.

**Evidence:** controlled artifacts are referenced by executable work, validation, or decisions; unused controls are simplified or retired.
