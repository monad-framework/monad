# Product Vision

**Status:** Proposed foundation baseline

## Vision statement

Monad is a **local-first Engineering Knowledge Compilation Platform** that understands a software system as structured engineering knowledge and uses that knowledge to coordinate humans, AI agents, source code, native tools, workflows, and infrastructure.

The long-term product is not merely a monorepo CLI, build wrapper, documentation site, or AI assistant. Monad is the control system that makes software engineering intent, constraints, relationships, work authorization, execution, and evidence explicit enough to be queried, validated, reproduced, and safely automated.

## Desired future

A maintainer can enter an unfamiliar repository and ask Monad:

- what the system is and why its parts exist;
- which requirements, specifications, decisions, owners, tests, and risks govern a component;
- what changed and what is semantically affected;
- which validation must run and why;
- whether implementation and documentation disagree;
- which promises lack tests or evidence;
- what context an AI agent needs for an authorized task;
- which native-tool actions form the smallest correct execution plan;
- how a delivered artifact was produced and which evidence proves it.

The answers are derived from a deterministic engineering model rather than improvised independently by each tool or model.

## Product principles

### Knowledge is primary

Source code is one projection of the software system. Requirements, ADRs, specifications, dependency relationships, work authorization, tests, releases, diagnostics, operational evidence, and rationale are also engineering knowledge and must participate in the model.

### Local-first

The canonical engineering loop runs from Git, the local filesystem, the Monad engine, and installed native toolchains. Cloud services may add collaboration, remote execution, registry, indexing, analytics, or fleet governance later; they may not be required for the semantic kernel to function.

### Deterministic core, probabilistic assistants

Workspace discovery, parsing, normalization, identity, graph construction, KIR, diagnostics, affected-set computation, planning, hashing, and conformance belong to deterministic software. AI may help author, explain, propose, and navigate, but does not define canonical semantics.

### AI-native, not model-dependent

Monad is intentionally designed for AI-assisted engineering. It exposes bounded context, capabilities, work contracts, provenance, and machine-readable evidence. Provider-specific features remain behind replaceable interfaces.

### Native tools remain authoritative for their mechanics

Monad coordinates ecosystem tools rather than reimplementing Cargo, Go, Bun, Python, compilers, linters, test runners, Terraform, Docker, Git, and similar systems. Monad owns *what should run, why, in what order, under which constraints, and what the result means*.

### Explainability is a product feature

Important results should expose provenance and reasoning structure: why an entity exists, why a relationship was inferred, why a check is required, why a change affects another artifact, and why a cache or plan is valid.

### Human authority is explicit

Automation does not acquire decision rights because it is fast or confident. High-consequence changes remain subject to the authority and review model in `governance/`.

### Semantic incrementality

A change should lead to the smallest safe recomputation and execution plan derivable from the semantic dependency graph. Conservative uncertainty expands the plan; it never silently omits required work.

### Generated views are disposable

Machine companions, indexes, publication views, dashboards, and agent packages are regenerated from canonical sources. A generated artifact cannot silently become a second editable source of truth.

### Modularize architecture early; split repositories late

Internal boundaries should be clean from the start. Independent repositories are introduced only when lifecycle, distribution, security, ownership, or community evidence justifies them.

## Strategic horizons

### Horizon 1 — Semantic kernel

Compile canonical repository knowledge into a stable graph and KIR; validate, query, explain, calculate impact, and produce structured diagnostics.

### Horizon 2 — Executable engineering model

Turn semantic impact into explainable execution plans, verified caches, native-tool orchestration, artifact production, and reproducible evidence.

### Horizon 3 — Human/AI engineering operating system

Generate bounded agent context, govern capabilities, support work packets and reviews, project engineering state into GitHub and documentation, and let Monad increasingly operate the engineering system used to build Monad.

### Horizon 4 — Distributed ecosystem

Add registry, plugins, SDKs, remote execution/cache, collaboration, hosted services, enterprise governance, and multi-repository knowledge where validated demand justifies them.

## MVP promise

Release 1 succeeds when a user can point Monad at a representative repository and complete a deterministic loop from workspace discovery to semantic graph, explanation, change impact, bounded AI context, execution plan, native validation, and reproducible evidence through a coherent CLI.

## Strategic boundary

Monad is not trying to replace Git, an IDE, a package manager, a programming language, every build tool, GitHub, or human engineering judgment. Features belong when they strengthen the semantic engineering model, deterministic execution, governed automation, or the reliable projection of engineering knowledge.
