# Monad Program Hierarchy

**Status:** Proposed canonical planning clarification  
**Scope:** Product planning, governed execution, and GitHub projection

Monad uses multiple related structures because product decomposition, execution scheduling, engineering authority, and verification answer different questions. These structures are linked, but they are not collapsed into one tree.

## 1. Product planning hierarchy

The canonical product/value decomposition is:

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

### Product Goal

Defines a bounded product outcome and its acceptance boundary.

### Initiative

Defines a finite, outcome-oriented program grouping beneath a Product Goal. An Initiative is not an enduring architectural domain, a Program Increment, or a Work Cycle.

### Epic

Defines a substantial product/system outcome that advances an Initiative.

### Feature

Defines a reviewable product-sized capability or engineering outcome. Features are the principal bridge between product planning and governed implementation.

### Story

Defines an observable user, operator, agent, or system outcome that contributes to a Feature.

### Enabler

Defines necessary architectural, infrastructure, governance, research, or engineering-system work that enables a Feature but is not best expressed as a user Story.

### Task

Defines bounded execution decomposition needed to realize a Story or Enabler within an executable Work Packet context.

Tasks are deliberately rolling-wave. Monad does not pre-generate a project-wide speculative task inventory. Formal Tasks are refined as the governing Work Packet approaches Ready.

## 2. Governed execution hierarchy

Execution is orthogonal to the product hierarchy:

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

### Program Increment

Defines an integrated, potentially releasable advance that proves a bounded Product Goal outcome or retires material risk.

Current namespaces are:

- `PI-MVP-*` — MVP Release 1;
- `PI-EXP-*` — approved CR-0002 post-MVP expansion;
- historical bootstrap identifiers remain preserved;
- future programs receive governed namespaces rather than reusing ambiguous historical IDs.

### Work Cycle

Defines a short execution and learning window. For the current roadmap, **Work Cycle == Sprint**. `WC-MVP-*` and `WC-EXP-*` are the canonical active namespaces.

### Work Packet

Defines the smallest authorized unit of governed project work. A Work Packet is independently ready, authorized, executed, reviewed, verified, and closed.

A forecast assignment does not authorize a Work Packet. Ready does not imply Authorized; merged code does not imply Closed.

### Execution

Records the actual bounded attempt to realize an authorized Work Packet, including actor, commands/actions, effects, evidence, review, and verification as applicable.

## 3. How Feature and Work Packet relate

Feature and Work Packet are intentionally different concepts:

```text
Feature
  = product/value outcome

Work Packet
  = governed execution unit
```

The current MVP and expanded rolling-wave backlogs usually pair a forecast Feature with one forecast Work Packet. That one-to-one projection is a planning convenience, not an ontology identity.

```text
Feature F-003-03
        │
        └── realized through ──► WP-MVP-0005
```

Future refinement may legitimately produce:

```text
one Feature
  ├─ Work Packet A
  └─ Work Packet B
```

when separate authorization, risk, verification, or review boundaries are required.

A Work Packet should not span unrelated Features merely to reduce bookkeeping.

## 4. Where Tasks belong

Tasks participate in both views without becoming an additional program-wide scheduling layer:

```text
Product view
Story / Enabler
  └─ Task

Execution view
Work Packet
  └─ bounded Tasks / tests / evidence actions
```

A Task therefore carries both product context and execution context when formalized. The Work Packet remains the governance boundary.

## 5. Engineering authority is orthogonal

Requirements, specifications, ADRs, policies, and architecture do not become parent levels in the product tree.

```text
Requirement ───── satisfied by ─────► Feature / Story
Specification ─── governs ──────────► Work Packet / implementation
ADR ───────────── constrains ───────► Work Packet / implementation
Policy ────────── controls ─────────► planning / execution / release
```

Many-to-many traceability is expected. A single requirement can span several Features; one Work Packet can be governed by several specifications and ADRs.

## 6. Review, correction, and verification are control structures

```text
Work Packet
  └─ Execution
       └─ Review
            └─ Finding
                 ├─ no action
                 ├─ Task
                 ├─ Change / Correction Request
                 └─ new Work Packet

Work Packet
  └─ Verification / Evidence
       └─ closure decision
```

A finding or correction request is not a product hierarchy level. It creates or changes work according to its scope.

## 7. Milestones and releases

Milestones and releases describe delivery, not decomposition:

- a **Milestone** records achievement of a meaningful program/product outcome;
- a **Release** records shipped software and its accepted evidence;
- either may span several Epics, Work Cycles, or Work Packets.

## 8. Complete trace model

Monad's planning and execution questions are therefore separated as follows:

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

## 9. Current MVP example

The current structured-configuration-parser work demonstrates the crosswalk:

```text
Product planning
PG-001
  └─ INIT-002
       └─ EPIC-003
            └─ F-003-03
                 ├─ US-015 — parse Monad config
                 ├─ US-016 — schema errors
                 └─ US-017 — deterministic normalization

Execution planning
PI-MVP-001
  └─ WC-MVP-0002
       └─ WP-MVP-0005
            └─ bounded Tasks/tests/evidence refined in the packet
```

The Feature and Work Packet are linked representations of the same forecast delivery slice, but the Feature expresses the outcome while the Work Packet carries executable authority and lifecycle state.

## 10. Current roadmap namespaces

### MVP Release 1

- Product Goal: `PG-001`
- Initiatives: `INIT-001` through `INIT-006`
- Epics: `EPIC-001` through `EPIC-014`
- Work Packets: `WP-STAB-0001`, `WP-MVP-0001` through `WP-MVP-0033`
- Stories: `US-001` through `US-105`, plus `EN-001` through `EN-003`
- Work Cycles: `WC-MVP-0000` through `WC-MVP-0012` in the forecast schedule
- Program Increments: `PI-MVP-001` through `PI-MVP-003`

### Approved post-MVP expansion

- Product Goals: `PG-002` through `PG-004`
- Epics: `EPIC-015` through `EPIC-024`
- Work Packets: `WP-EXP-0001` through `WP-EXP-0040` in forecast catalogs
- Stories: `US-106` through `US-237`
- Work Cycles: `WC-EXP-0001` through `WC-EXP-0014`
- Program Increments: `PI-EXP-001` through `PI-EXP-003`

The post-MVP backlog has not yet assigned a canonical Initiative layer. That mapping should be added through governed rolling-wave planning before those Epics approach active execution rather than invented as an incidental documentation change.

## 11. Source-of-truth map

| Concern | Canonical source |
| --- | --- |
| Current Product Goal | `product/PRODUCT-GOAL.md` |
| Post-MVP Product Goals | `product/POST-MVP-PRODUCT-GOALS.md` |
| MVP Initiatives | `product/initiatives.md` |
| MVP backlog | `product/backlog/MVP-BACKLOG.md` |
| Expanded backlog | `product/backlog/EXPANDED-BACKLOG.md` |
| Program Increments | `engineering/increments/` |
| Work Cycles | `engineering/work-cycles/` |
| Work Packets | `engineering/work-packets/` |
| Readiness / Done | `engineering/definition-of-ready.md`, `engineering/definition-of-done.md` |
| GitHub projection | `engineering/github/PROJECT-V2-CONFIGURATION.md` |
| Live lifecycle authority | canonical Git/EOS control state and evidence |

## 12. GitHub projection rule

GitHub Issues and Projects are coordination projections of this model, not replacement authority.

The desired visible product hierarchy is:

```text
Initiative
  └─ Epic
       └─ Feature
            ├─ Story
            │    └─ Task when refined
            └─ Enabler
                 └─ Task when refined
```

Each projected item may additionally carry orthogonal fields such as Product Goal, Program Increment, Work Cycle, Work Packet, lifecycle, specification, ADR, risk, executor, and target release.

If GitHub cannot represent one relationship cleanly, preserve the canonical identifier and relationship in Git/EOS rather than changing Monad's ontology to fit GitHub.
