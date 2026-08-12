# Engineering Plan

**Status:** Proposed delivery baseline  
**Delivery target:** MVP Release 1  
**Aggressive forecast:** 2026-11-23, subject to evidence and quality gates

## Objective

Move Monad from the current transitional documentation-heavy foundation to a stable, executable MVP as quickly as possible without trading away the properties that define the product: semantic correctness, determinism, reproducibility, explicit authority, explainability, and local-first operation.

## Delivery model

Monad uses a Scrum-aligned product backlog together with a stricter engineering-authority layer.

```text
Product Goal
  ↓
Milestone / Product Increment
  ↓
Epic
  ↓
Feature
  ↓
User Story / Enabler / Bug / Spike
  ↓
Sprint selection
  ↓
Work Packet (engineering authorization)
  ↓
Tasks / Codex execution units
  ↓
Pull Request
  ↓
Tests + review + evidence
  ↓
Accepted Increment
```

Epics, Features, Stories, and backlog ordering describe product value and delivery. ADRs, specifications, Work Packets, tests, and reviews define engineering authority and evidence. GitHub Issues and Projects are operational projections, not a replacement for canonical repository artifacts.

## Cadence

- **Sprint length:** one week, Monday through Sunday.
- **Planning:** select an outcome-oriented Sprint Goal and only Ready work that fits the capacity/risk envelope.
- **Daily inspection:** completed, active, blocked, decisions needed, next action.
- **Review:** demonstrate integrated behavior and acceptance evidence.
- **Retrospective:** identify process/system changes and update the backlog when evidence changes sequencing.
- **Refinement horizon:** all foreseeable Epics and Features; detailed Stories/Enablers through the next several Sprints; full task decomposition only for the current Sprint and immediate execution horizon.

Planning reserves capacity for review, discovery, integration, and correction. Scope is the primary lever when capacity changes; correctness and safety gates are not silently reduced.

## Stabilization transition — August 12–16, 2026

**Goal:** establish one coherent, synchronized source of truth from which implementation can be planned safely.

Outcomes:

- one Monad product thesis rather than competing generic and engineering-knowledge definitions;
- single canonical ADR location at `architecture/decisions/`;
- all `artifact-system/*.md` files populated with substantive Draft baselines;
- deterministic `machine/` projection synchronized to the current canonical tree;
- MVP Release 1 requirements/capabilities/architecture agreed enough for planning;
- GitHub backlog/project/wiki configuration prepared and live projections started;
- stabilization risks, inconsistencies, and transition debt visible.

This transition is not an implementation Sprint and does not count generated Draft files as accepted architecture.

## PI-001 — Stabilized Foundation

**Dates:** 2026-08-17 through 2026-08-23  
**Sprint:** SPRINT-001  
**Goal:** convert the transition baseline into an accepted C0/C1 foundation and a Ready implementation backlog.

Key outcomes:

- approve/revise product thesis, MVP scope, principles, authority hierarchy, terminology, and success criteria;
- disposition the minimum architecture decisions required for semantic-kernel implementation;
- finalize the initial domain/semantic ontology and configuration direction sufficiently for the first vertical slice;
- complete GitHub repository/project/wiki/issue operating baseline;
- make the first implementation Work Packets Ready.

**Exit:** no unresolved foundational contradiction blocks semantic-kernel implementation; required first-slice ADRs/specs are accepted; CI baseline is green.

## PI-002 — Semantic Kernel

**Dates:** 2026-08-24 through 2026-09-27  
**Sprints:** SPRINT-002 through SPRINT-006  
**Goal:** compile repository engineering knowledge into a deterministic, queryable graph and KIR.

### SPRINT-002 — Workspace and artifact inventory — Aug 24–30

Deliver deterministic workspace root/repository identity, configuration bootstrap, artifact discovery/adapters, and inspectable inventory.

### SPRINT-003 — Semantic identity and provenance — Aug 31–Sep 6

Deliver stable document/entity identity, normalization, canonical hashing, source coordinates, aliases/collision diagnostics, and provenance.

### SPRINT-004 — Semantic graph and invariants — Sep 7–13

Deliver the core ontology, graph construction, typed relationships, deterministic ordering, graph invariants, snapshot/serialization, and representative fixtures.

### SPRINT-005 — KIR and semantic validation — Sep 14–20

Deliver KIR charter/schema, canonical serialization, MSG→KIR lowering, versioning/compatibility baseline, and conformance validation.

### SPRINT-006 — Query, explanation, and first impact slice — Sep 21–27

Deliver entity lookup, relationship traversal, provenance/why explanation, structured query output, Git change ingestion, and first conservative affected-set calculation.

**PI exit:** clean repeated compilation is deterministic; representative semantic relationships are explainable; KIR is versioned/conformant; first useful affected-set scenario passes.

## PI-003 — Executable Engineering Loop

**Dates:** 2026-09-28 through 2026-10-25  
**Sprints:** SPRINT-007 through SPRINT-010  
**Goal:** turn semantic knowledge into bounded context and deterministic native-tool execution.

### SPRINT-007 — Diagnostics and affected-set hardening — Sep 28–Oct 4

Deliver diagnostic registry/format, semantic drift diagnostics, conservative impact explanation, negative/boundary corpus, and uncertainty behavior.

### SPRINT-008 — Incrementality, fingerprints, and execution plans — Oct 5–11

Deliver change invalidation, first incremental graph update, content/semantic fingerprints, cache-validity contract, execution-plan schema, and deterministic plan construction.

### SPRINT-009 — Native tool orchestration and evidence — Oct 12–18

Deliver local execution runtime, native-tool adapter contract, representative real adapters, dependency ordering, failure/cancellation semantics, command/environment evidence, and verified-cache first slice.

### SPRINT-010 — CLI and AI-agent context vertical slice — Oct 19–25

Deliver coherent Release 1 CLI workflow plus deterministic task/work-packet context packaging suitable for bounded Codex execution, explicit capabilities/exclusions, and provenance.

**PI exit:** a user can go from repository change/task to affected semantic knowledge, inspectable plan, native validation, evidence, and bounded agent context.

## PI-004 — MVP Hardening and Release

**Dates:** 2026-10-26 through 2026-11-22  
**Sprints:** SPRINT-011 through SPRINT-014  
**Goal:** make the integrated loop safe, reproducible, installable, documented, dogfooded, and release-ready.

### SPRINT-011 — Integrated conformance scenarios — Oct 26–Nov 1

Complete reference repositories, end-to-end acceptance suite, determinism/property/golden tests, configuration/graph/KIR compatibility fixtures, failure/recovery paths, and CI/local parity.

### SPRINT-012 — Performance, security, compatibility, packaging — Nov 2–8

Establish performance baselines, threat/control verification, secret/context safety, supply-chain gates, public compatibility policy, installable artifacts, and upgrade/rollback behavior.

### SPRINT-013 — Dogfood, documentation, beta, release automation — Nov 9–15

Run Monad against Monad, close high-value self-hosting gaps, complete user/maintainer docs, generated publication/search, beta feedback, changelog/release notes, provenance/SBOM/signing automation as applicable.

### SPRINT-014 — Release candidate and readiness — Nov 16–22

Freeze Release 1 scope, run clean-machine reproducibility, resolve release blockers, conduct security/operability/performance/release-readiness reviews, tag/sign the accepted candidate, and prepare rollback/support path.

## MVP Release 1 — November 23, 2026

The date is an aggressive forecast, not authority to ship red or unverified software. Release occurs only when the acceptance criteria in `product/product-requirements.md` and the Definition of Done are satisfied.

## Parallel workstreams

1. **Foundation/governance:** product thesis, ADRs, specifications, authority, terminology.
2. **Knowledge plane:** workspace, artifacts, identity, provenance, graph, KIR.
3. **Control/execution:** impact, incrementality, planning, cache, native tools.
4. **Interaction/AI:** CLI, diagnostics, query/explain, agent context.
5. **Quality/security:** tests, conformance, threat controls, supply chain, performance.
6. **Publication/project:** machine docs, human docs, GitHub issues/project/wiki, releases.

Parallelism is allowed only when work does not depend on unresolved semantics from another stream. Integration and vertical-slice evidence outrank maximizing work-in-progress.

## Human / ChatGPT / Codex workflow

### Product Owner / Project Steward

Owns priorities, scope acceptance, strategic decisions, risk acceptance, and release authorization.

### ChatGPT

Maintains architectural/product consistency, prepares and refines canonical artifacts, decomposes work, creates Work Packets, projects planning into GitHub, reviews evidence, and identifies decisions/risks requiring human authority.

### Codex

Receives bounded implementation packets with authorized files/scope, governing specs/ADRs, prohibited changes, acceptance criteria, tests, and validation commands. It inspects and implements locally, returns evidence, and does not silently expand scope.

### GitHub

Stores source/history, Issues/Project status, Pull Requests, CI evidence, Wiki projection, and releases. A GitHub status is not stronger authority than its canonical governing artifact.

## Backlog policy

All foreseeable Epics and Features are enumerated early to expose scope and dependencies. MVP Stories and Enablers are refined progressively. Tasks are decomposed close to execution. Estimates are comparative planning aids, not hour promises. Anything too large to verify independently is split before Sprint commitment.

Backlog ordering uses:

1. existential correctness/security risk;
2. assumptions that could invalidate the architecture/product;
3. dependency critical path to an end-to-end MVP outcome;
4. user value and learning value;
5. enablement of later work;
6. effort and reversibility.

## Definition of implementation readiness

A Work Packet may enter implementation when its objective and scope are bounded, governing requirements/specifications/ADRs are identified and sufficiently stable, dependencies and prohibited changes are explicit, acceptance criteria are executable or objectively reviewable, validation commands are known, and unresolved questions do not require the implementer to invent product/architecture authority.

## Definition of release readiness

Release requires integrated acceptance, deterministic/reproducible evidence, security and supply-chain gates, compatibility/versioning review, install/upgrade/rollback evidence, documented known limitations, user/maintainer documentation, no unaccepted critical/high risk, and explicit Product Owner acceptance.
