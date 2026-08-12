# Project Idea: Monad

**Status:** Proposed foundation baseline  
**Product:** Monad — Engineering Knowledge Compilation Platform

## One-sentence hypothesis

If software teams can deterministically compile the authoritative knowledge of a project into a semantic graph that explains relationships, provenance, constraints, impact, and authorized work, then humans and AI agents can make and execute engineering changes with less context reconstruction, less drift, and stronger reproducibility than today's file-, ticket-, and conversation-centric workflows.

## Opportunity

A software project is an interconnected body of knowledge, but most development environments expose only fragments of it at a time. Source files know little about the requirement that justified them. Issues know little about accepted architecture. CI knows that a command failed but often cannot explain which promise is threatened. An AI agent may receive thousands of tokens of repository text without a trustworthy model of authority, ownership, dependencies, or why a file exists.

The result is repeated context reconstruction. Engineers search, ask, infer, reread, rerun, and manually correlate artifacts before they can safely act. As projects scale across languages, repositories, tools, humans, and AI agents, that reconstruction becomes slower and less reliable.

Monad proposes a different foundation: **compile software engineering knowledge itself**.

## Product loop

```text
intent
  ↓
canonical artifacts
  ↓
semantic compilation
  ↓
engineering knowledge graph
  ↓
validation / explanation / impact / context / policy
  ↓
execution plan
  ↓
humans + AI agents + native tools
  ↓
verified evidence
  ↓
updated canonical knowledge
```

The repository remains understandable without Monad. Monad adds a deterministic machine layer that makes relationships and consequences computable.

## Intended users

### Primary — software engineer or maintainer

Needs to understand a repository, change it safely, determine what is affected, run the correct validation, and explain why the result is trustworthy.

### Engineering lead or architect

Needs to preserve boundaries and decisions, detect drift, understand blast radius, and review consequential changes without reconstructing context manually.

### AI-assisted developer

Needs to give an agent the smallest sufficient task context, explicit permissions, governing specifications, and deterministic acceptance criteria rather than an unbounded repository dump.

### CI/release operator

Needs local and automated validation to produce reproducible evidence tied to the exact project state and declared toolchain.

### Tool and plugin author

Needs stable schemas, semantic identities, protocols, and extension boundaries on which to build integrations without coupling to internal implementation details.

## Proposed value

Monad should make these questions cheap and dependable:

- What is this project and how is it structured?
- Why does this artifact or component exist?
- Which requirement, specification, ADR, risk, or work authorization governs it?
- What depends on this change?
- Which tests and commands prove the affected promises?
- What is missing, contradictory, stale, or unverified?
- What context does an AI agent actually need for this task?
- What should run, in what order, and why?
- Can another machine reproduce the same semantic result and execution evidence?

## Critical assumptions

| ID | Assumption | Risk if false | Cheapest useful test |
| --- | --- | --- | --- |
| A-01 | Context reconstruction and engineering drift are recurring, meaningful costs in real software projects. | Weak product need. | Repository task studies and maintainer interviews. |
| A-02 | Enough engineering meaning can be extracted from explicit artifacts and repository structure to produce useful deterministic relationships. | Graph becomes decorative rather than operational. | Compile several representative repositories and evaluate query/impact accuracy. |
| A-03 | Stable identity, provenance, and explicit authority materially improve AI-agent work quality and reviewability. | Agent-context feature adds complexity without value. | Compare bounded semantic context with naive repository context on controlled tasks. |
| A-04 | Semantic affected-set calculation can reduce unnecessary work without missing required validation. | Incrementality becomes unsafe. | Differential tests against conservative full validation over a change corpus. |
| A-05 | Native tool orchestration provides more value than replacing ecosystem build/test tools. | Meta-tool model is too shallow. | Implement one polyglot vertical slice using existing native tools. |
| A-06 | The deterministic kernel can remain useful without a hosted service or a particular AI provider. | Local-first/provider-agnostic thesis fails. | Complete Release 1 acceptance offline except for optional external integrations. |

## MVP hypothesis

The smallest meaningful proof is not a broad platform. It is one end-to-end semantic engineering loop:

1. discover a representative repository;
2. inventory canonical engineering artifacts;
3. assign stable identities and provenance;
4. build a deterministic semantic graph;
5. query and explain the graph;
6. compute the affected set of a bounded change;
7. create a bounded agent context package;
8. derive an explainable execution plan;
9. invoke native validation tools;
10. retain diagnostics and evidence tied to the exact semantic input state.

If this loop does not make a real engineering task more understandable, safer, or faster, Monad should narrow or change before broad ecosystem investment.

## Falsification conditions

The project must reconsider its thesis if representative repository studies show that semantic relationships cannot be made accurate enough for consequential use; if maintaining explicit engineering knowledge costs more than the context it saves; if affected-set optimization cannot be made conservative and explainable; if users consistently prefer existing build/monorepo tools plus conventional documentation; or if AI context quality is not meaningfully improved by semantic selection and provenance.

## Initial scope decision

Release 1 is local-first, single-user, repository-centric, and intentionally bounded. It proves semantic compilation, explanation, affected-set reasoning, agent context, and native execution. Remote collaboration, hosted control planes, enterprise fleet governance, and broad plugin marketplaces remain later horizons until the kernel proves value.
