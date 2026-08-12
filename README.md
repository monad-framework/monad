# Monad

Monad is an **Engineering Knowledge Compilation Platform**: a local-first, AI-native software-engineering knowledge compiler and orchestration runtime that turns canonical engineering knowledge into a deterministic semantic model from which humans, agents, tools, validation, planning, execution decisions, and documentation can operate.

## Current state

Monad is in **foundation stabilization / pre-implementation**. The repository is intentionally establishing one coherent product thesis, authoritative artifact model, machine-readable knowledge layer, GitHub operating surface, and MVP execution backlog before broad implementation begins.

The current MVP goal is defined in [`product/MVP-RELEASE-1.md`](product/MVP-RELEASE-1.md).

## Core thesis

Software systems are governed by far more than source code. Requirements, decisions, specifications, ownership, risks, work authorization, tests, provenance, releases, and operational evidence all affect what a change means and whether it is safe.

Monad treats that body of engineering knowledge as a compilable system.

```text
Human engineering knowledge
        ↓
Canonical artifacts
        ↓
Discovery + parsing + semantic analysis
        ↓
Monad Semantic Graph
        ↓
KIR / query / diagnostics / context packages
        ↓
Humans + ChatGPT + Codex + native tools
        ↓
Validated engineering change and evidence
```

The mature product should answer not only **what exists**, but also **why it exists, what governs it, what depends on it, what a change affects, what evidence proves it, and what an authorized agent needs to act safely**.

## Architectural commitments already carried forward

- Knowledge is a first-class engineering artifact.
- Human-readable canonical source remains the project source of truth.
- Machine representations are deterministic derivatives with provenance.
- Local operation must remain useful without a hosted control plane.
- AI is a bounded consumer/producer of engineering context, not an authority above accepted human decisions.
- Monad coordinates native tools instead of replacing every language/build ecosystem.
- Determinism, explainability, traceability, and reproducibility are product properties.
- Architecture should be modular before repositories are split prematurely.

## Repository map

| Path | Purpose |
| --- | --- |
| `vision/` | Why Monad exists and the durable principles constraining it |
| `product/` | Users, outcomes, capabilities, MVP, requirements, and roadmap |
| `architecture/` | System context, boundaries, architecture, and ADRs |
| `specifications/` | Normative testable contracts |
| `engineering/` | Milestones, increments, work cycles, Work Packets, status, reviews, and risks |
| `artifact-system/` | Comprehensive catalog of engineering artifact contracts |
| `governance/` | Authority, change control, terminology, decisions, and document lifecycle |
| `research/` | Questions, experiments, evidence, findings, and trade studies |
| `security/` | Threats, controls, supply chain, and security model |
| `testing/` | Test strategy, quality gates, performance, and acceptance |
| `operations/` | Deployment, observability, reliability, incidents, and environments |
| `journal/` | Historical design narrative; informative unless promoted |
| `machine/` | Deterministic semantic projections for AI, search, validation, and graph use |
| `.monad/` | Monad repository identity/configuration bootstrap state |

## Canonical vs machine representation

Canonical human-readable source is edited directly. `machine/` is generated with:

```bash
python3 scripts/sync-machine-docs.py --write
python3 scripts/sync-machine-docs.py --check
```

AI tools may use machine companions for retrieval and graph navigation, but must read the canonical source before making meaning-changing edits. A stale machine companion has no authority.

## Engineering workflow

```text
Product intent
  → accepted decisions/specifications
  → ordered backlog
  → ready Work Packet
  → bounded ChatGPT/Codex context
  → implementation
  → deterministic verification
  → PR/review
  → merge/release evidence
```

GitHub is the durable collaboration and review surface. Canonical requirements, decisions, specifications, and Work Packets remain versioned in Git; GitHub Issues/Projects project and coordinate that work rather than silently replacing its authority.

## Transitional note

The repository is undergoing a controlled re-foundation. Draft and Proposed documents may change substantially until the Foundation Stabilization Review. Accepted decisions are migrated or superseded explicitly rather than erased. `architecture/decisions/` is the intended canonical ADR root.

## Start here

1. [`engineering/stabilization/STABILIZATION-CHARTER.md`](engineering/stabilization/STABILIZATION-CHARTER.md)
2. [`vision/product-vision.md`](vision/product-vision.md)
3. [`vision/problem-statement.md`](vision/problem-statement.md)
4. [`product/MVP-RELEASE-1.md`](product/MVP-RELEASE-1.md)
5. [`architecture/overview.md`](architecture/overview.md)
6. [`engineering/project-status.md`](engineering/project-status.md)
7. [`engineering/work-packets/active.md`](engineering/work-packets/active.md)

## License

Copyright © 2026 Thomas Carter. Released under the MIT License; see [`LICENSE`](LICENSE).