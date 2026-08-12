# Monad

**Engineering Knowledge Compilation Platform**

Monad is a local-first engineering intelligence and execution system that turns the knowledge contained in a software project into a canonical, queryable semantic model. From that model Monad can explain architecture and dependencies, calculate change impact, prepare bounded context for AI agents, derive deterministic execution plans, invoke native development tools, and preserve evidence about what happened and why.

> **Current phase:** Foundation stabilization / pre-implementation  
> **MVP target:** Release 1 — deterministic semantic engineering loop

## Product thesis

Software development is governed by far more than source code. Requirements, architecture decisions, specifications, repository structure, configuration, dependencies, tests, work authorization, reviews, risks, CI evidence, releases, runbooks, and human reasoning all constrain what a system means and what changes are safe.

Today those facts are fragmented across files, tools, tickets, conversations, and memory. Humans repeatedly reconstruct context, and AI systems are often given large but poorly bounded snapshots without reliable authority, provenance, or change impact.

Monad treats **engineering knowledge as a first-class artifact** and compiles it through an explicit lifecycle:

```text
human intent and canonical engineering artifacts
        ↓
workspace discovery and artifact ingestion
        ↓
semantic extraction, normalization, identity, provenance
        ↓
Monad Semantic Graph (MSG)
        ↓
Kernel Intermediate Representation (KIR)
        ↓
validation · query · explanation · impact · policy · agent context
        ↓
execution planning
        ↓
native tools · humans · AI agents
        ↓
evidence, diagnostics, reviews, releases
        ↓
new canonical engineering knowledge
```

The graph and KIR do not replace the human-readable repository. They are deterministic machine representations derived from canonical engineering sources and used to coordinate understanding and execution.

## MVP Release 1

Release 1 proves one complete engineering loop. Given a representative repository, Monad must be able to:

1. discover the workspace and relevant canonical artifacts;
2. assign stable semantic identity and retain provenance;
3. compile a deterministic engineering semantic graph;
4. validate graph and artifact consistency with structured diagnostics;
5. query and explain entities, relationships, authority, and provenance;
6. calculate a useful affected set for a bounded repository change;
7. serialize a versioned machine representation and KIR;
8. produce a minimal, bounded context package for an authorized AI-agent task;
9. derive an explainable execution plan and delegate work to native tools;
10. reproduce the same semantic result and evidence from the same declared inputs;
11. expose the workflow through a stable CLI suitable for humans and automation.

Release 1 is intentionally local-first. Remote execution, hosted collaboration, enterprise administration, and commercial services are later horizons unless evidence proves that one is required to validate the local semantic kernel.

## Core principles

- **Knowledge is the primary engineering artifact.** Code is essential, but it exists inside a larger network of intent, constraints, decisions, verification, and evidence.
- **Human-readable sources remain canonical.** Generated machine views are reproducible projections, never a competing editable truth.
- **Local-first is a product boundary.** Core inspection, compilation, validation, planning, and execution cannot require a Monad cloud service.
- **Determinism lives below AI.** Parsing, normalization, graph construction, identity, KIR, diagnostics, planning, and verification are normal deterministic software. AI consumes their outputs; it does not define their semantics.
- **AI-native does not mean AI-dependent.** Providers and models are replaceable. Human authority is explicit and preserved.
- **Native tools remain native.** Monad coordinates Cargo, Go, Bun, Python, Biome, Terraform, Docker, Git, and other ecosystem tools rather than reimplementing them.
- **Explainability is part of correctness.** Important results should answer not only *what* but also *why*, *from which evidence*, and *what would change the result*.
- **Semantic incrementality beats blind reruns.** Monad should understand the affected engineering subgraph and execute the smallest correct plan.
- **Architecture is modularized early; repositories are split late.** Independent repositories are justified by independent lifecycle, distribution, security, or ownership—not by diagram aesthetics.

## Human, ChatGPT, Codex, and GitHub

Monad is being built with a deliberate division of responsibility:

- **Project Steward / Product Owner:** sets direction, accepts outcomes, owns product priorities and high-consequence decisions.
- **ChatGPT:** architecture, specifications, decomposition, backlog refinement, work-packet preparation, review, governance, and cross-artifact consistency.
- **Codex:** bounded repository inspection and implementation under explicit work-packet scope, tests, commands, and prohibited changes.
- **GitHub:** durable system of record for source, review, issues, project tracking, automation, releases, and public collaboration.

Neither ChatGPT nor Codex gains authority merely by generating a plausible result. Material decisions are promoted through the repository's governance and review system.

## Canonical knowledge and machine projection

Files outside `machine/` are canonical unless an approved artifact states otherwise. The `machine/` directory is generated by `scripts/sync-machine-docs.py` and contains document companions, a manifest, a semantic graph, and a section corpus for deterministic retrieval and agent context.

```bash
python3 scripts/sync-machine-docs.py --write
python3 scripts/sync-machine-docs.py --check
```

A machine companion is trustworthy only when its source hash matches the canonical file and the synchronization check passes.

## Start here

1. [`idea.md`](idea.md) — product hypothesis and falsification conditions.
2. [`vision/product-vision.md`](vision/product-vision.md) — intended future and strategic boundaries.
3. [`vision/problem-statement.md`](vision/problem-statement.md) — engineering problem Monad exists to solve.
4. [`product/product-requirements.md`](product/product-requirements.md) — proposed Release 1 requirements.
5. [`architecture/overview.md`](architecture/overview.md) — target architecture and five-plane model.
6. [`architecture/decisions/`](architecture/decisions/) — accepted and proposed architectural decisions.
7. [`engineering/engineering-plan.md`](engineering/engineering-plan.md) — stabilization and MVP delivery strategy.
8. [`engineering/project-status.md`](engineering/project-status.md) — current executable status.
9. [`artifact-system/README.md`](artifact-system/README.md) — complete artifact taxonomy and lifecycle.
10. [`machine/README.md`](machine/README.md) — deterministic human/machine synchronization contract.

## Working rule

Do not confuse **existence** with **authority**. The repository intentionally contains a broad artifact taxonomy so that important engineering concerns have a known home, but most artifacts begin as Draft. A Draft becomes governing only through the review and approval lifecycle defined by `governance/`.

## License

Copyright © 2026 Thomas Carter. Released under the MIT License; see [`LICENSE`](LICENSE).
