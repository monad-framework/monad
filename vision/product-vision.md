# Product Vision

**Status:** Proposed stabilization baseline

## Vision

Monad makes software engineering knowledge compilable.

A mature Monad understands a software system not merely as files and commands, but as a connected body of intent, constraints, decisions, implementation, evidence, ownership, history, and operational state. It gives humans and bounded AI agents a common semantic substrate for understanding what exists, why it exists, what governs it, what a proposed change affects, what should execute, and what evidence is required before a change is accepted.

## Desired future

An engineer can enter an unfamiliar repository and ask Monad questions such as:

- What is this system and how is it structured?
- Why does this component exist?
- Which requirement and ADR govern this behavior?
- What depends on this interface?
- What tests prove this specification?
- What changed semantically between these revisions?
- Which parts of the workspace are affected?
- What is missing or contradictory?
- What context should Codex receive for this Work Packet?
- What must pass before this PI/release can close?

The answers are derived from canonical, versioned engineering knowledge with provenance rather than improvised from unbounded repository text.

## Product identity

Monad is best understood simultaneously as:

- an **engineering knowledge compiler** — it turns canonical artifacts into a normalized semantic representation;
- an **engineering intelligence layer** — it supports graph query, explanation, traceability, diagnostics, and impact analysis;
- an **orchestration runtime** — it can derive what native tools/work should run from semantic state;
- an **AI context and governance layer** — it supplies minimal authorized context and evidence boundaries to agents; and
- an **engineering operating system** — not an OS kernel, but a control layer coordinating knowledge, work, tools, and lifecycle state.

## Strategic outcomes

1. **Understandable systems:** repository meaning is queryable without reconstructing it manually.
2. **Governed change:** implementation traces to explicit authority and validation.
3. **Minimal context:** humans and agents receive the relevant semantic neighborhood, not indiscriminate repository dumps.
4. **Deterministic operation:** the same inputs yield equivalent semantic outputs and execution decisions.
5. **Incremental work:** changes drive minimal affected analysis and native tool execution.
6. **Living knowledge:** docs, plans, issues, and AI context can be projected from current engineering reality without becoming competing truths.
7. **Tool independence:** Monad coordinates existing ecosystems through stable adapters rather than replacing every compiler, test runner, package manager, or VCS.

## Three horizons

### Horizon 1 — Compile and understand

Prove repository discovery, semantic graph, KIR foundations, diagnostics, query/explain, agent context, and deterministic local CLI behavior.

### Horizon 2 — Coordinate and enforce

Add semantic diff, incrementality, policy enforcement, execution planning, broader adapters, release evidence, richer publication, and controlled extension mechanisms.

### Horizon 3 — Scale the engineering knowledge system

Add multi-repository intelligence, registries, remote/hosted collaboration where justified, organization knowledge, ecosystem extensions, advanced AI coordination, and enterprise governance.

## Vision test

A capability belongs in Monad when it materially strengthens one or more of: structured engineering knowledge, semantic relationships, deterministic/incremental execution, explainable governance, provenance, or bounded human/AI coordination. Features that do not reinforce those properties should live in another tool.