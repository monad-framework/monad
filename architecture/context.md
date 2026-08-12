# System Context

**Status:** Proposed stabilization baseline

## System of interest

Monad is a local-first Engineering Knowledge Compilation Platform operating against one or more software repositories/workspaces. Its deterministic core discovers canonical engineering artifacts, compiles them into semantic representations, validates them, and serves derived intelligence/execution decisions to humans, AI agents, and native engineering tools.

## Primary actors

| Actor | Goal | Authority boundary |
| --- | --- | --- |
| Software Engineer | Understand, validate, and change a repository | May act within repository/project permissions |
| Project/Product Steward | Define intent, priorities, and acceptance | Human product/governance authority |
| Architecture/Engineering Owner | Define technical contracts and authorize implementation | Accepted ADR/spec/WP boundaries |
| ChatGPT | Architecture, planning, specification, decomposition, review assistance | Advisory/generative; no implicit approval |
| Codex | Repository inspection and bounded implementation | Work Packet/file/tool scope; evidence required |
| CI/Automation | Deterministic validation and projection | Mechanical enforcement only |
| Native Tool | Compile/test/build/format/deploy its domain | Native result remains authoritative |

## External systems

### Git and repository hosting

Git stores canonical history; GitHub provides collaboration, Issues/Projects projections, PR review, Actions, releases, and organization governance.

### Native language/build ecosystems

Compilers, package managers, task/build systems, test frameworks, formatters/linters, infrastructure tools, containers, and other integrations are invoked through explicit adapters/capabilities.

### AI model/provider services

Optional AI providers may assist with reasoning/authoring. Core semantic truth and validation cannot depend on a provider being reachable or deterministic.

### Registries and artifact stores

Package/plugin/Monad registries and caches may distribute trusted artifacts later. Their metadata, signatures, and compatibility become explicit boundaries when activated.

## Trust boundaries

1. repository-controlled data → Monad parser/semantic core;
2. Monad core → executable native tools/processes;
3. canonical repository → generated machine/cache state;
4. Monad → AI provider context boundary;
5. local engine → optional remote/hosted services;
6. work authorization → agent implementation authority;
7. build/release automation → distributable artifacts.

## Core data flow

```text
Canonical repository
    ↓
Discovery + configuration resolution
    ↓
Parsing / normalization / identity
    ↓
Semantic graph + diagnostics
    ↓
KIR / query / explain / context / execution plan
    ↓
Human + agent + native tools
    ↓
Evidence and canonical change
```

Every derived stage retains provenance sufficient to identify the canonical inputs and rules that produced it.