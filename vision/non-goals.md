# Non-Goals

**Status:** Proposed foundation baseline

Non-goals protect Monad from becoming a collection of adjacent engineering features before its semantic core proves value. They may be reconsidered only through explicit product and architecture review.

## NG-01 — Replace Git

Git remains the source/history transport for repository content. Monad may model Git state and changes but does not invent a competing version-control system.

## NG-02 — Replace native language and ecosystem tools

Monad does not reimplement Cargo, Go tooling, Bun/npm, TypeScript, Python tooling, JVM build systems, Terraform, Docker, or similar mature tools merely to own their mechanics. It coordinates them through explicit adapters and execution plans.

## NG-03 — Become a universal package manager

Dependency knowledge and policy are in scope; replacing every ecosystem's package distribution semantics is not.

## NG-04 — Require a hosted Monad service

Core workspace discovery, semantic compilation, validation, query, impact analysis, context generation, planning, and local execution must remain useful offline.

## NG-05 — Make an LLM the source of semantic truth

Models may assist authorship and explanation, but canonical identity, graph semantics, KIR, diagnostics, planning, and conformance cannot depend on nondeterministic model output.

## NG-06 — Define a universal programming language

Monad may define specification/configuration languages and machine representations when justified, but it does not seek to replace general-purpose programming languages.

## NG-07 — Replace the IDE

IDE integrations may expose Monad knowledge, but the product is not an editor or an attempt to own the entire coding interface.

## NG-08 — Become a general ticketing or project-management application

Monad models authorized engineering work and projects state into systems such as GitHub. It does not replace mature issue trackers with an unrelated proprietary planning system.

## NG-09 — Split the ecosystem into many repositories during architectural instability

Release 1 remains centered on the canonical `monad` repository. New repositories require independent lifecycle, distribution, security, ownership, or community evidence.

## NG-10 — Remote execution in MVP Release 1

The architecture should leave room for remote cache and execution, but Release 1 only needs deterministic local execution and serializable plans.

## NG-11 — Enterprise fleet administration in MVP Release 1

SSO administration, organization policy fleets, centralized analytics, and multi-tenant enterprise control planes are later horizons.

## NG-12 — Autonomous high-consequence engineering authority

An AI agent cannot approve its own architecture changes, security exceptions, releases, destructive operations, or other decisions reserved for human authority.

## NG-13 — Perfect semantic understanding of arbitrary repositories

Monad should expose confidence boundaries, unknowns, unsupported artifact classes, and adapter limits. Conservative partial knowledge is preferable to fabricated completeness.

## NG-14 — Optimize every workflow before proving the semantic kernel

Remote collaboration, rich TUI, marketplace, hosted services, broad SDK coverage, and advanced commercial features do not outrank proving the deterministic repository → graph → impact → plan → evidence loop.

## Reconsideration rule

A non-goal may move into scope when user evidence demonstrates material value, the semantic kernel is stable enough to support it, its dependencies and risks are understood, and the Product Owner explicitly authorizes the scope change. Architectural consequences receive an ADR when required.
