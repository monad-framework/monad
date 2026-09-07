---
title: "Monad Workbench v0"
status: "Implementation Candidate"
classification: "Implementation Specification"
description: "Defines the local-first read-only Monad Workbench v0 projection environment and its completion boundary."
---

# Monad Workbench v0

## 1. Purpose

Monad Workbench is the internal local-first application used to understand, navigate, and inspect Monad engineering state without repeatedly reconstructing the project from raw files, EOS registries, Git state, and GitHub projections.

Workbench v0 is a **read-only, non-authoritative projection environment**.

Its responsibility is to consume existing Monad and EOS sources, normalize them into a temporary in-memory read model, and present human-comprehensible synchronized projections.

Workbench SHALL NOT become an independent source of product, lifecycle, authority, provenance, evidence, verification, or release truth.

The v0 completion boundary is trustworthy comprehension and navigation. Governed mutations, lifecycle actions, AI execution, editing, and multi-user behavior are deferred.

## 2. Core interaction model

The governing interaction principle is:

> One workspace, one current focus object, many coordinated projections of the same underlying Monad engineering knowledge.

Workbench distinguishes:

1. the engineering object being examined;
2. the projection or lens being used to understand it;
3. the authoritative source from which each displayed claim was derived.

Workbench favors progressive disclosure over attempting to render the entire Monad knowledge graph at once.

## 3. Cognitive questions

Workbench v0 SHOULD make the following questions materially easier to answer:

1. Where am I?
2. What am I looking at?
3. Why does it exist?
4. What governs it?
5. What is its current state?
6. What depends on it?
7. What is it waiting on?
8. What evidence exists?
9. What changed or requires attention?
10. What should happen next?

Workbench MAY be unable to derive every answer for every object. Missing information SHALL be shown as missing or unknown rather than fabricated.

## 4. Authority boundary

Workbench uses the following conceptual flow:

```text
Canonical Monad / EOS sources
            │
            ▼
     Workbench adapters
            │
            ▼
      in-memory read model
            │
            ▼
 projection / object indexes
            │
            ▼
       Workbench UI
```

Workbench-derived state is always a projection unless another governed Monad process explicitly promotes a change into an authoritative artifact or EOS state transition.

### 4.1 Source precedence

When sources overlap, Workbench v0 applies this precedence:

1. `.eos/state/current.json` — live EOS lifecycle state for current Program Increment, Work Cycle, Work Packet, and other current EOS entities.
2. Canonical product planning artifacts — `product/PROGRAM-HIERARCHY.md`, `product/PRODUCT-GOAL.md`, `product/POST-MVP-PRODUCT-GOALS.md`, `product/initiatives.md`, `product/backlog/MVP-BACKLOG.md`, and `product/backlog/EXPANDED-BACKLOG.md`.
3. Authoritative engineering artifacts — Work Packet Markdown and other governed authored artifacts for objectives, acceptance criteria, dependencies, governing authority, implementation boundaries, and narrative context.
4. EOS registries/projections — `.eos/*.tsv`, `.eos/trace-edges.tsv`, evidence registries, execution registries, artifact indexes, decision/change/release registries, and related machine-readable projections.
5. Git workspace metadata — branch and working-tree state.

GitHub Issues and GitHub Projects are coordination projections and are not lifecycle or engineering-knowledge authority for Workbench v0.

### 4.2 Conflict handling

If artifact narrative and canonical EOS current state disagree, Workbench SHALL use canonical EOS current state for lifecycle projection.

Workbench SHOULD preserve the artifact narrative as provenance-bearing authored context rather than silently rewriting or treating it as current lifecycle truth.

## 5. Canonical product hierarchy

Workbench v0 SHALL project the canonical product planning hierarchy as:

```text
Product Goal
  └─ Initiative
       └─ Epic
            └─ Feature
                 ├─ Story
                 │    └─ Task
                 └─ Enabler
                      └─ Task
```

A Feature represents a product/value outcome.

Stories and Enablers are stable product-planning objects.

Detailed Tasks remain rolling-wave and may be absent until the corresponding execution work approaches Ready.

## 6. Governed execution hierarchy

Workbench v0 SHALL separately project the governed execution hierarchy as:

```text
Program Increment
  └─ Work Cycle
       └─ Work Packet
            └─ Execution
                 ├─ implementation
                 ├─ tests
                 ├─ evidence
                 └─ verification / review
```

Product planning and governed execution are orthogonal dimensions.

A Work Packet SHALL NOT be modeled as a child level under Story or Feature merely because the current backlog forecasts a Feature-to-Work-Packet relationship.

One Feature MAY eventually require multiple Work Packets. One Work Packet MAY satisfy or contribute to multiple product or knowledge objects where governance permits.

## 7. Engineering knowledge and control dimensions

Requirements, specifications, ADRs, policies, evidence, reviews, findings, risks, change requests, verification, and releases are orthogonal knowledge/control structures rather than additional decomposition levels in either hierarchy.

A useful reasoning model is:

```text
WHY
Product Goal / Requirement

WHAT
Initiative → Epic → Feature → Story / Enabler

HOW
Specification / ADR / Policy

WHEN / THROUGH WHAT EXECUTION
Program Increment → Work Cycle → Work Packet → Execution

WHAT CONCRETE ACTIONS
Task / test / evidence action

DID IT WORK
Review → Finding → Verification / Evidence → Closure → Release
```

## 8. Application shell

Workbench v0 uses an IDE-like persistent application shell:

```text
┌──────────────────────────────────────────────────────────────────────────┐
│ File   Edit   View   Navigate   Help                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ active projection / future tab strip                                    │
├──────────────────────────────────────────────────────────────────────────┤
│ Monad / projection-or-focus / branch                    Search  Ctrl+K   │
├──────────────┬──────────────────────────────────────────┬────────────────┤
│ Navigator    │                Workspace                 │ Inspector      │
│              │                                          │                │
│ projections  │          active projection               │ focus metadata │
│ object types │                                          │ relations      │
│              │                                          │ provenance     │
├──────────────┴──────────────────────────────────────────┴────────────────┤
│ branch / working-tree / Workbench status                                │
└──────────────────────────────────────────────────────────────────────────┘
```

The Navigator and Inspector are collapsible and their collapsed state MAY persist in browser-local UI preferences.

Browser-local layout preferences are non-authoritative Workbench state.

Persistent multi-tab workspaces are deferred beyond v0; the tab strip exists as future application chrome only.

## 9. Implemented v0 routes

### 9.1 Now — `/`

The Now projection provides current orientation across product, execution, governing knowledge, repository state, and current Focus context.

Current lifecycle state SHALL derive from canonical EOS current state.

### 9.2 Plan — `/plan`

The Plan projection renders the canonical product hierarchy from Product Goal through Story/Enabler with progressive disclosure.

It MAY show related forecast Work Packet and Work Cycle identifiers as orthogonal metadata, but SHALL NOT place them inside the canonical product decomposition hierarchy.

### 9.3 Execution — `/execution`

The Execution projection renders Program Increment → Work Cycle → Work Packet → Execution and summarizes associated evidence.

Execution/evidence registries SHALL be interpreted as EOS machine projections rather than authored product hierarchy.

### 9.4 Knowledge — `/knowledge`

The Knowledge projection provides catalog access to requirements, specifications, ADRs, policies, and evidence.

Category links MAY filter the projection using URL query state.

### 9.5 Control — `/control`

The Control projection surfaces risks, change requests, reviews, verification-related state, releases, and associated control/provenance information that can be reliably derived from current sources.

### 9.6 Focus — `/focus/[id]`

Focus is the object-centric notebook/projection surface.

It identifies the selected object, presents incoming/outgoing relationships, source/provenance, semantic document blocks, lifecycle state, governing authority, dependencies, acceptance criteria, execution/evidence state where applicable, and remaining artifact narrative.

Focus identifiers SHALL be validated before use and resolved paths SHALL remain inside the repository boundary.

## 10. Semantic Focus projection

Workbench SHOULD distinguish semantic information from raw authored document sections.

For a Work Packet, Focus MAY project blocks such as:

- objective;
- governing authority;
- dependencies;
- acceptance criteria;
- lifecycle reconciliation;
- execution and evidence;
- validation;
- implementation boundary;
- source/provenance.

For ADRs and other decision artifacts, headings such as Context, Decision, and Consequences SHOULD be represented as semantically labeled blocks where possible.

Unknown or unsupported sections MAY remain artifact-text blocks.

The projection layer owns semantic presentation; Markdown headings are ingestion hints, not the Monad ontology.

## 11. Navigator

The left Navigator exposes:

### Workspace projections

- Now
- Plan
- Execution
- Knowledge
- Control
- Focus

### Product

- Product Goals
- Initiatives
- Epics
- Features
- Stories & Enablers

### Execution

- Program Increments
- Work Cycles
- Work Packets
- Executions

### Knowledge

- Requirements
- Specifications
- ADRs
- Policies
- Evidence

### Control

- Risks
- Changes
- Reviews
- Verification
- Releases

Navigator entries SHOULD route, filter, or anchor into a real projection rather than represent false affordances.

## 12. Inspector

The right Inspector displays contextual information for the current focus object without replacing the center projection.

Typical fields include:

- identifier;
- object type;
- lifecycle/status;
- authority;
- source;
- incoming/outgoing relationships;
- repository branch/version context;
- Workbench navigation back to the current Work Packet or Focus route.

The Inspector is contextual metadata, not an authority surface.

## 13. Command palette and search

Workbench v0 includes a command palette opened through `Ctrl/Cmd+K` or the Search button.

The palette supports:

- navigation to primary Workbench projections;
- object search by stable ID, title, and indexed object metadata;
- direct navigation to object Focus pages.

Search indexes are derived from the same Workbench projection adapters and SHALL NOT create a competing persistence layer.

## 14. Menus and context menu

Workbench v0 includes application menus and a shell-level right-click context menu.

Supported operations are non-authoritative UI/navigation operations such as:

- navigate to projections;
- open current Focus;
- copy Focus ID;
- copy source path;
- show/hide panels;
- refresh the read model.

Governed lifecycle or repository mutation actions are explicitly deferred.

## 15. Local-first runtime

The v0 runtime remains:

```text
Monad repository
      │
      ▼
filesystem / EOS adapters
      │
      ▼
normalization + object index
      │
      ▼
in-memory projections
      │
      ▼
Next.js server/client UI
```

No database is required.

No authentication system is required.

No cloud infrastructure is required.

No Supabase or Payload dependency is required.

Workbench discovers the Monad repository root by walking upward until it finds `monad.toml`.

## 16. Technical baseline

Workbench v0 uses:

- Next.js 16;
- React 19;
- TypeScript;
- Bun;
- Biome;
- Lucide React icons;
- server-side filesystem adapters;
- URL-addressed Focus and projection routes.

The application lives at:

```text
apps/workbench/
```

Reusable code SHOULD remain inside the application until stable reuse boundaries emerge.

## 17. Security and containment

Workbench v0 SHALL:

- validate Focus identifiers before resolving them;
- prevent resolved artifact paths from escaping the repository root;
- treat malformed/missing projection data as missing/error state rather than executing content;
- never evaluate environment interpolation, command substitution, network includes, or arbitrary authored commands merely to display an artifact;
- remain read-only with respect to authoritative Monad/EOS state.

## 18. Error and empty-state semantics

Workbench SHALL distinguish:

- no records exist;
- records are unknown/unresolved;
- source parsing failed;
- canonical state is inconsistent;
- verification/evidence is absent;
- verification/evidence explicitly failed.

For example, zero execution/evidence records on a current Work Packet means "none recorded yet," not "verification failed."

## 19. Verification baseline

The Workbench v0 branch SHALL provide a repeatable local verification gate:

```bash
bun run check
```

The gate SHALL include:

1. Biome lint/check;
2. unit/fixture tests for high-risk adapters;
3. a production Next.js build.

High-risk adapter coverage SHOULD include at minimum:

- TSV normalization;
- product-plan hierarchy parsing;
- governed execution hierarchy/evidence parsing;
- repository root discovery;
- Focus document parsing and repository path containment.

A path-filtered GitHub Actions workflow SHOULD run the same gate for Workbench-affecting pull requests.

## 20. v0 completion criteria

Workbench v0 is complete when a user can open a local Monad checkout and, without manually reconstructing the repository, reliably answer:

1. What Product Goal are we pursuing?
2. Which Initiative, Epic, Feature, Story/Enabler does current work support?
3. Which Program Increment, Work Cycle, and Work Packet are active?
4. What is the canonical current lifecycle state?
5. What requirements, ADRs, specifications, and policies govern the work?
6. What dependencies and related objects exist?
7. What executions and evidence exist?
8. Which risks, change requests, reviews, verification records, or releases require attention?
9. Where did each important displayed value come from?
10. How do I navigate directly to the relevant object or source context?

The application MUST remain a read-only projection consumer while answering those questions.

## 21. Non-goals for v0

Workbench v0 SHALL NOT require or implement:

- authoritative lifecycle mutation;
- direct EOS transitions;
- requirement/ADR/specification editing;
- Git or GitHub writes;
- autonomous AI execution;
- generalized AI-agent orchestration;
- production authentication;
- SaaS tenancy;
- cloud persistence;
- realtime collaboration;
- persistent multi-tab workspaces;
- split-view editor state;
- generalized plugin architecture;
- generalized graph database infrastructure;
- a replacement code editor;
- production hosted deployment.

## 22. Evolution toward v1

The intended architectural evolution is:

```text
v0
Repository / EOS sources
        ↓
Workbench-specific adapters
        ↓
read-only projections
        ↓
Workbench
```

then progressively:

```text
v1+
Monad semantic kernel / stable local query interfaces
        ↓
projection engine
        ↓
Workbench command + interaction layer
        ↓
governed actions / supervised AI execution
```

The v0 interaction model should survive this transition even where temporary ingestion adapters do not.

The conceptual version boundary is:

> v0 asks Monad what is true.
>
> v1 lets an authorized operator safely do something about it.

## 23. Guiding constraint

Workbench SHALL optimize for cognitive clarity before feature count.

When choosing between exposing more data and making the current engineering situation easier to understand, Workbench SHOULD choose comprehension.
