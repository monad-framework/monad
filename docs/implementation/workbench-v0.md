---
title: "Monad Workbench v0"
status: "Draft"
classification: "Implementation Specification"
description: "Defines the initial internal workbench for reducing cognitive load while planning and developing Monad."
---

# Monad Workbench v0

## 1. Purpose

Monad Workbench is an internal development application designed to reduce the cognitive load required to understand, plan, navigate, and execute work on Monad.

Its primary responsibility is to present existing Monad engineering knowledge through human-comprehensible projections.

Workbench v0 is not the authoritative store for Monad engineering state.

It reads, normalizes, relates, and projects information that already exists elsewhere in the Monad repository.

The initial implementation exists to become immediately useful during Monad's own development while establishing interaction patterns that may later become native Monad capabilities.

---

## 2. Problem

Monad contains multiple overlapping dimensions of engineering information, including:

* product goals;
* initiatives;
* epics;
* stories;
* tasks;
* work cycles;
* work packets;
* requirements;
* specifications;
* architecture decisions;
* reviews;
* schemas;
* risks;
* open questions;
* implementation artifacts;
* executions;
* verification results;
* releases;
* provenance;
* authority;
* repository state.

These artifacts are individually understandable but increasingly difficult to hold simultaneously in working memory.

The current development process therefore requires repeated reconstruction of questions such as:

* What are we currently trying to accomplish?
* Where does the current work fit within the larger program?
* What work is active?
* What is blocked?
* What decision led to this artifact?
* Which requirements govern this work?
* Which artifacts depend on this decision?
* What changed recently?
* What remains unresolved?
* What should happen next?

Workbench exists to answer those questions without requiring the user to mentally reconstruct the project from files, conversations, GitHub issues, and repository history.

---

## 3. Design Principle

The fundamental interaction model is:

> One workspace, one current focus object, many synchronized projections.

Workbench SHALL distinguish between:

1. the engineering object being examined; and
2. the projection through which that object is being viewed.

A user may therefore retain the same focus object while changing between planning, hierarchy, dependency, knowledge, execution, verification, timeline, risk, or other projections.

Workbench SHALL favor progressive disclosure over simultaneous presentation of the complete Monad knowledge graph.

---

## 4. Status

Workbench v0 is:

* internal development tooling;
* experimental;
* local-first;
* repository-oriented;
* read-mostly;
* non-authoritative;
* replaceable.

Workbench v0 is explicitly permitted to use temporary ingestion and normalization mechanisms that may later be replaced by native Monad services.

---

## 5. Authority Boundary

Workbench SHALL NOT become an independent source of truth for Monad engineering knowledge.

The initial authority model is:

```text
Repository artifacts
        │
        ▼
Workbench ingestion
        │
        ▼
Normalized read model
        │
        ▼
Projections
        │
        ▼
Workbench UI
```

Workbench-derived state SHALL be considered a projection unless explicitly promoted into an authoritative Monad artifact through another governed process.

---

## 6. Initial Sources

Workbench v0 MAY consume information from:

* Markdown and MDX documents;
* YAML frontmatter;
* JSON;
* YAML;
* TOML;
* repository directory structure;
* Git metadata;
* GitHub-derived metadata when available;
* `.monad/` metadata;
* existing scripts and generated indexes.

Workbench v0 SHOULD initially prefer local repository sources over remote services.

Remote synchronization is not required for the first usable release.

---

## 7. Core Concepts

### 7.1 Focus Object

The focus object is the engineering object currently being examined.

Examples include:

* Goal
* Initiative
* Epic
* Story
* Task
* Work Cycle
* Work Packet
* Requirement
* Specification
* ADR
* Review
* Schema
* Release
* Risk
* Open Question

Workbench SHALL maintain an explicit current focus object whenever practical.

---

### 7.2 Projection

A projection is a representation of engineering knowledge optimized to answer a particular question.

Examples include:

* overview;
* hierarchy;
* plan;
* dependency graph;
* artifact list;
* timeline;
* execution history;
* verification state;
* risk state;
* traceability.

Multiple projections MAY represent the same focus object.

---

### 7.3 Lens

A lens is a named projection configuration optimized for a recurring engineering concern.

Initial conceptual lenses include:

#### Planning Lens

```text
Goal
  ↓
Initiative
  ↓
Epic
  ↓
Story
  ↓
Work Packet
  ↓
Task
```

#### Knowledge Lens

```text
Requirement
  ↓
Decision
  ↓
Specification
  ↓
Implementation
```

#### Execution Lens

```text
Work Packet
  ↓
Operation
  ↓
Execution
  ↓
Effect
  ↓
Verification
```

#### Traceability Lens

```text
Goal
  ↓
Requirement
  ↓
Decision
  ↓
Specification
  ↓
Implementation
  ↓
Verification
  ↓
Evidence
```

#### Risk Lens

The Risk Lens highlights:

* blocked work;
* unresolved decisions;
* failed verification;
* stale artifacts;
* missing dependencies;
* missing authority;
* missing provenance;
* critical unresolved questions.

Lenses are conceptual in v0 and do not require a generalized lens-definition engine.

---

### 7.4 Inspector

The inspector presents contextual metadata for the currently selected object without requiring navigation away from the current projection.

Typical inspector information includes:

* identifier;
* type;
* title;
* lifecycle state;
* status;
* parent;
* children;
* dependencies;
* dependents;
* authority;
* provenance;
* related artifacts;
* verification state;
* risks;
* source location.

---

### 7.5 Context Trail

Workbench SHALL maintain visible hierarchical context where possible.

Example:

```text
Monad
  › Initiative
    › Epic
      › Story
        › Work Packet
```

The context trail SHALL support navigation toward broader scopes.

---

## 8. Primary Cognitive Questions

Workbench SHOULD make the following questions easy to answer:

### Where am I?

Show the focus object's position within the larger Monad program and knowledge structure.

### What am I looking at?

Identify the object, its type, state, and purpose.

### Why does it exist?

Expose goals, requirements, decisions, parent relationships, and governing artifacts.

### What is its current state?

Expose lifecycle, progress, verification, risks, blockers, and recent changes.

### What should happen next?

Expose unresolved decisions, ready work, dependencies, next actions, and recommended continuation points.

---

## 9. Application Shell

The initial Workbench shell SHOULD follow this conceptual structure:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ Monad Workbench                                   Search / Command       │
├──────────────┬──────────────────────────────────────────┬────────────────┤
│              │                                          │                │
│ NAVIGATOR    │                WORKSPACE                 │   INSPECTOR    │
│              │                                          │                │
│ hierarchy    │          active projection               │ metadata       │
│ knowledge    │                                          │ relations      │
│ work         │                                          │ state          │
│              │                                          │ provenance     │
│              │                                          │ dependencies   │
│              │                                          │                │
├──────────────┴──────────────────────────────────────────┴────────────────┤
│ AI / ACTIVITY / EXECUTION / VERIFICATION / GIT                          │
└──────────────────────────────────────────────────────────────────────────┘
```

The bottom activity region MAY be deferred until later iterations.

---

## 10. Initial Navigation

Workbench v0 SHALL begin with four primary destinations:

### Now

A current-state projection optimized for answering what deserves attention now.

### Plan

A hierarchical projection of goals, initiatives, epics, stories, work packets, and tasks.

### Knowledge

A projection of requirements, specifications, ADRs, reviews, schemas, and related engineering artifacts.

### Focus

A context-preserving projection of the currently selected engineering object.

These may initially be implemented as routes, tabs, or equivalent navigation primitives.

---

## 11. Now Projection

The Now view is the initial home screen for active Monad development.

It SHOULD eventually present:

* current objective;
* current initiative;
* current epic;
* active work cycle;
* active work packet;
* next action;
* blockers;
* unresolved decisions;
* recently completed work;
* recent changes;
* upcoming work;
* items requiring attention.

The initial implementation MAY populate only the subset that can be reliably derived from current repository state.

Workbench SHALL prefer missing or unknown values over fabricated state.

---

## 12. Plan Projection

The Plan view SHALL provide a hierarchical planning representation.

The initial planning hierarchy is:

```text
Goal
└── Initiative
    └── Epic
        └── Story
            └── Work Packet
                └── Task
```

Work Cycles MAY cross-cut this hierarchy rather than appearing as strict parents.

Workbench SHALL preserve this distinction.

A Work Cycle represents a governed period or unit of execution.

A Work Packet represents a bounded unit of executable engineering work.

Neither SHOULD be forced into the product decomposition hierarchy where doing so would misrepresent the underlying model.

---

## 13. Knowledge Projection

The Knowledge view SHOULD provide structured access to engineering artifacts including:

* requirements;
* specifications;
* ADRs;
* reviews;
* schemas;
* policies;
* risks;
* open questions.

The view SHOULD allow users to move from artifact categories to individual artifacts without requiring knowledge of repository paths.

---

## 14. Focus Projection

The Focus view SHALL render a selected engineering object as a collection of projection blocks.

Example blocks include:

* summary;
* state;
* parent context;
* children;
* progress;
* requirements;
* decisions;
* specifications;
* dependencies;
* work packets;
* risks;
* open questions;
* verification;
* source;
* history.

The initial implementation MAY use a fixed block layout.

Future implementations MAY allow configurable or user-defined block arrangements.

---

## 15. Progressive Disclosure

Workbench SHALL avoid displaying every available relationship or artifact simultaneously.

Information SHOULD be exposed according to cognitive relevance.

The interface SHOULD optimize for:

* immediate orientation;
* current task comprehension;
* nearby dependencies;
* unresolved conditions;
* next actions.

Full graph exploration is secondary.

---

## 16. Graph Usage

Monad's semantic graph SHOULD NOT become the default visual representation of Workbench.

Graph views are appropriate when answering:

> How is this connected?

Graph views are generally inappropriate when answering:

> What should I do next?

Workbench SHALL therefore treat graph visualization as one projection among many.

---

## 17. Initial Normalized Model

Workbench v0 MAY begin with a deliberately minimal normalized representation.

Example:

```ts
export type MonadObjectType =
  | "goal"
  | "initiative"
  | "epic"
  | "story"
  | "task"
  | "work-cycle"
  | "work-packet"
  | "requirement"
  | "specification"
  | "adr"
  | "review"
  | "schema"
  | "risk"
  | "open-question"
  | "release";

export interface MonadRelationship {
  type: string;
  target: string;
}

export interface MonadObject {
  id: string;
  type: MonadObjectType;
  title: string;
  status?: string;
  description?: string;
  parent?: string;
  children?: string[];
  relationships?: MonadRelationship[];
  source?: string;
}
```

This model is provisional.

It SHALL NOT be treated as the canonical Monad semantic model.

---

## 18. Technical Architecture

Workbench v0 SHOULD use:

* TypeScript;
* React;
* Next.js;
* Bun;
* Biome.

The application SHOULD initially live at:

```text
apps/workbench/
```

The application MAY read repository files directly from server-side code.

No database is required for the first release.

No authentication system is required for the first release.

No cloud infrastructure is required for the first release.

---

## 19. Initial Runtime Model

The expected v0 runtime is:

```text
Monad repository
      │
      ▼
repository scanner
      │
      ▼
artifact parsers
      │
      ▼
normalization
      │
      ▼
in-memory read model
      │
      ▼
projection functions
      │
      ▼
Workbench UI
```

The normalized read model MAY initially be regenerated on application startup or request.

Optimization and incremental indexing are outside the first milestone.

---

## 20. Repository Placement

Initial structure:

```text
monad/
├── apps/
│   └── workbench/
├── docs/
├── schemas/
├── scripts/
├── packages/
└── .monad/
```

Reusable functionality SHOULD remain inside the Workbench application until meaningful reuse boundaries emerge.

Premature extraction into packages SHOULD be avoided.

Potential future packages include:

```text
packages/
├── workbench-model/
├── workbench-ingest/
├── workbench-projections/
└── workbench-ui/
```

These SHALL NOT be created merely to satisfy speculative architecture.

---

## 21. Non-Goals for v0

Workbench v0 SHALL NOT require:

* complete implementation of the Monad semantic kernel;
* authoritative state mutation;
* production authentication;
* billing;
* SaaS tenancy;
* remote synchronization;
* generalized plugin architecture;
* generalized graph database infrastructure;
* GitHub synchronization;
* autonomous AI execution;
* production deployment;
* complete editing workflows;
* realtime collaboration.

---

## 22. Evolution Path

The temporary architecture is expected to evolve from:

```text
Repository
   ↓
Workbench adapters
   ↓
Normalized read model
   ↓
Workbench
```

toward:

```text
Monad Semantic Kernel
        ↓
Projection Engine
        ↓
Workbench
```

The UI concepts and interaction model SHOULD survive this transition even when the ingestion layer does not.

---

## 23. First Vertical Slice

The first usable implementation SHALL prioritize a complete narrow workflow over broad incomplete coverage.

The first vertical slice is:

```text
Application shell
      ↓
Repository ingestion
      ↓
Minimal normalized model
      ↓
Now projection
      ↓
Hierarchy navigator
      ↓
Focus-object selection
      ↓
Inspector
```

The first version does not need comprehensive artifact support.

It needs enough real Monad data to provide immediate cognitive value.

---

## 24. Initial Success Criteria

Workbench v0.1 is useful when opening it allows the user to answer, without manually reconstructing repository context:

1. What are we currently building?
2. Why are we building it?
3. Where are we in the project hierarchy?
4. What work is active?
5. What is blocked?
6. What decisions remain unresolved?
7. What changed recently?
8. What should happen next?
9. What artifacts govern the current work?
10. Where are those artifacts located?

---

## 25. Guiding Constraint

Workbench SHALL optimize for cognitive clarity before feature count.

When choosing between displaying more information and making the current engineering situation easier to understand, Workbench SHOULD choose comprehension.
