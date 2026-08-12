# Monad Artifact System

**Status:** Proposed taxonomy baseline

The `artifact-system/` tree is the complete planning and governance taxonomy for the engineering artifacts Monad may need as it evolves. Its purpose is to give every consequential concern a known canonical home before implementation pressure causes decisions to disappear into chats, issue comments, source code, or maintainer memory.

The presence of a file does **not** mean its contents are approved, implemented, required for MVP, or equally important.

## Canonicality

Human-readable Markdown in `artifact-system/` is canonical for the artifact it represents **only after that artifact reaches an approved status under `governance/document-lifecycle.md`**.

Every materialized baseline begins as:

```text
Status: Draft
Authority: Proposed baseline; not authoritative until approved
```

Generated representations under `machine/` are deterministic derivatives and never become an independently editable authority.

## Why the complete taxonomy exists now

Monad is intended to become an engineering knowledge compiler and operating system. A mature product may eventually need formal artifacts for KIR, semantic graph, compiler/language, execution, APIs, plugins, registry, AI agents, security, testing, releases, operations, program management, community, legal, commercial, and historical concerns.

Creating the taxonomy early provides:

- stable destinations for later knowledge;
- discoverability for humans and agents;
- a way to expose missing decisions intentionally;
- predictable machine projection and search;
- consistent ownership/lifecycle metadata;
- protection against ad hoc document naming and duplicated authority.

It does **not** justify trying to approve or implement the entire taxonomy before MVP.

## Materialization policy

`scripts/populate-artifact-system.py` deterministically fills empty Markdown files with substantive Draft baselines. It never overwrites an already-authored non-empty artifact unless explicitly invoked with `--force`.

```bash
python3 scripts/populate-artifact-system.py
python3 scripts/populate-artifact-system.py --check
```

A generated Draft contains purpose, scope, governing principles, inputs, domain-specific contract sections, traceability, failure/exception handling, lifecycle, verification, acceptance criteria, review triggers, and canonicality. These are reviewable starting points, not synthetic approval.

After materialization, normal authorship edits the Markdown directly. The generator is not the ongoing source of meaning.

## Criticality model

Artifact *criticality* describes when a concern must become sufficiently authoritative relative to delivery—not how important it is in the abstract.

### C0 — Constitutional / product authority

Must be coherent before consequential implementation can be authorized.

Examples:

- product thesis, vision, problem statement, scope/non-goals;
- principles and terminology;
- authority, decision, artifact, and human/agent governance;
- Product Goal and success criteria.

### C1 — Architecture / semantic-kernel authority

Must be accepted before or alongside the first implementation that depends on it.

Examples:

- system context/boundaries;
- domain and semantic graph model;
- identity/provenance;
- KIR;
- diagnostics;
- configuration/workspace;
- execution model;
- trust/security boundaries;
- public compatibility direction.

### C2 — MVP delivery authority

Must mature as Release 1 capabilities become executable.

Examples:

- command specifications;
- native-tool adapter contracts;
- testing/conformance;
- incrementality/cache;
- agent context contract;
- CI/release engineering;
- packaging/install/upgrade;
- observability and performance.

### C3 — Post-MVP ecosystem authority

May remain Draft through Release 1 unless implementation or user evidence pulls it forward.

Examples:

- plugin marketplace/registry;
- remote execution/cache;
- broad SDK strategy;
- distributed repository coordination;
- community certification.

### C4 — Future/conditional authority

Exists to preserve a known concern but does not belong on the current critical path.

Examples:

- hosted enterprise control plane;
- commercial packaging/pricing;
- fleet analytics;
- mature federation;
- specialized legal/compliance programs not currently applicable.

## Approval policy

Artifacts move from Draft only when their information is needed and sufficiently supported by evidence.

A review should ask:

1. Is this artifact needed to govern current or near-term work?
2. Does it conflict with higher authority?
3. Are its normative statements precise and testable?
4. Are assumptions labeled rather than converted into facts?
5. Does it duplicate another artifact's authority?
6. Are affected downstream artifacts and consumers known?
7. Is the cost of maintaining this artifact justified by decisions or automation that consume it?

Approval is not a bulk operation. The goal is a **complete taxonomy with selectively authoritative content**, not hundreds of ceremonial approvals.

## Relation to specifications and ADRs

`artifact-system/` describes the classes and contracts the overall engineering system may need. Concrete normative product behavior should live in the canonical specification hierarchy under `specifications/`. Consequential architectural choices live in `architecture/decisions/`.

An artifact-system document may therefore:

- define how a class of specifications works;
- define an architecture concern that later produces an ADR;
- provide a template or policy used by Work Packets/reviews;
- become a canonical architecture or operating document itself when approved;
- remain an informative Draft until needed.

It must not silently override an accepted ADR or approved specification.

## Relation to the backlog

The artifact taxonomy is not the product backlog. A Markdown file does not automatically become a task.

Backlog items are created when producing, reviewing, implementing, or validating an artifact advances the Product Goal. This distinction prevents “complete every document” from displacing the actual MVP semantic loop.

## Machine-readable projection

After any canonical source change:

```bash
python3 scripts/sync-machine-docs.py --write
python3 scripts/sync-machine-docs.py --check
```

The machine layer gives agents and automation structured access to the artifact corpus while retaining source hashes and provenance.

## Long-term direction

Today the artifact taxonomy is primarily path- and document-oriented. Monad should progressively make these relationships graph-native: requirement → specification → decision → work packet → issue/branch/PR → implementation → test → release → evidence. The filesystem remains readable, while the semantic graph becomes the executable relationship layer.
