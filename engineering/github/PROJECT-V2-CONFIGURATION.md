# Monad Engineering Program — GitHub Project Configuration

**Status:** Proposed  
**Scope:** organization-level GitHub Project for `monad-framework`

## Project identity

Preferred title: **Monad Engineering Program**.

The setup process MUST reuse a Project with this exact title if one already exists in the organization. It MUST NOT create a duplicate solely because the repository or backlog was refounded.

## Purpose

The Project is the portfolio and execution view over canonical Git engineering records and projected GitHub Issues. It is not an authority source for requirements, decisions, specifications, Initiative semantics, Work Packet semantics, EOS lifecycle state, or verification truth.

The canonical relationship among planning dimensions is defined in `product/PROGRAM-HIERARCHY.md`.

The primary product-planning hierarchy projected into GitHub is:

```text
Product Goal
  └─ Initiative
       └─ Epic
            └─ Feature
                 ├─ Story
                 │    └─ Task when refined
                 └─ Enabler
                      └─ Task when refined
```

Governed execution remains orthogonal:

```text
Program Increment
  └─ Work Cycle
       └─ Work Packet
            └─ Execution / review / verification / evidence
```

A Feature and a Work Packet are linked but not identical. The current rolling-wave backlog commonly pairs one forecast Feature with one forecast Work Packet; the Feature expresses the product outcome while the Work Packet carries governed execution authority and lifecycle state.

Canonical Initiative definitions and mappings live in `product/initiatives.md`. Current backlog mappings live in `product/backlog/`.

## Fields

Retain GitHub's built-in Title, Assignees, Status, Labels, Milestone, Repository, and linked pull-request data. Create the following custom fields when missing:

| Field | Type | Values / meaning |
| --- | --- | --- |
| Item Type | Single select | Initiative, Epic, Feature, Story, Enabler, Task, Work Packet, Bug, Defect, Change Request |
| Product Goal | Text | canonical PG identifier, e.g. PG-001 |
| Initiative | Text | canonical Initiative identifier, e.g. INIT-002 |
| Epic | Text | canonical Epic identifier, e.g. EPIC-003 |
| Feature | Text | canonical Feature identifier, e.g. F-003-03 |
| Priority | Single select | P0, P1, P2, P3 |
| Criticality | Single select | C0, C1, C2, C3, C4, C5 |
| Product Area | Text | product/capability area |
| Domain | Text | orthogonal enduring domain such as identity, semantic graph, AI, CLI, verification |
| Increment | Text | canonical Program Increment, e.g. PI-MVP-001 |
| Work Cycle | Text | canonical Work Cycle, e.g. WC-MVP-0002 |
| Lifecycle | Single select | Backlog, Refining, Ready, Authorized, Running, Review, Verified, Closed, Blocked |
| Story Points | Number | optional relative estimate; never hours/productivity |
| Risk | Single select | Critical, High, Medium, Low |
| Executor | Single select | Human, ChatGPT, Codex, Mixed |
| Work Packet | Text | canonical WP identifier |
| Specification | Text | governing specification identifiers |
| ADR | Text | governing ADR identifiers |
| Target Release | Text | e.g. MVP Release 1 |
| Start Date | Date | forecast/actual start |
| Target Date | Date | forecast target |

`Product Goal`, `Initiative`, `Epic`, `Feature`, `Work Cycle`, `Work Packet`, and lifecycle identifiers in GitHub are projections. Their canonical definitions remain in repository/EOS artifacts.

### Compatibility and field migration

`Work Cycle` is the canonical Project field. The term `Sprint` remains a planning/UI compatibility synonym because Work Cycle == Sprint for the current roadmap, but setup/synchronization automation MUST NOT create or write a second competing Sprint field.

Historical Project configurations may contain legacy fields such as `Work-Cycle`, `Work-Packet`, `Sprint`, or `PI` alongside the canonical `Work Cycle`, `Work Packet`, or `Increment` fields. During migration:

1. projection automation prefers an exact canonical field name when present;
2. a single punctuation-only legacy equivalent may be reused temporarily;
3. ambiguous normalized duplicates must be reported rather than updated nondeterministically;
4. once canonical field values have been verified, obsolete duplicate fields should be removed from the Project UI;
5. deleting a Project field never deletes the canonical Git/EOS identifier or artifact.

## Status and lifecycle semantics

GitHub's built-in Status is a presentation/work-management convenience. Do not let it erase distinctions required by Monad governance.

At minimum preserve these semantic distinctions in the projected metadata and issue text:

1. **Planning/readiness** — Backlog, Refining, Ready.
2. **Authorization/execution** — Authorized, Running, Blocked.
3. **Review/evidence/completion** — Review, Verified, Closed.

Scheduling alone does not authorize implementation. A Work Packet may become Ready only after canonical readiness gates pass, and Ready does not imply Authorized.

## Required views

Create these views in the Project UI after fields exist:

1. **Program** — table/roadmap emphasizing Initiatives and overall Product Goal progress.
2. **MVP Roadmap** — roadmap grouped by Initiative, showing Epics and Feature outcomes.
3. **Current Work** — board/table for Ready, Authorized, Running, Review, and Blocked work.
4. **Next Up** — Ready items that are not blocked and are near the active Work Cycle horizon.
5. **Work Cycles** — grouped by `Work Cycle` / `WC-MVP-*` or `WC-EXP-*`.
6. **By Initiative** — grouped by Initiative.
7. **By Epic** — grouped by Epic.
8. **By Feature** — grouped by Feature where useful for Stories/Enablers/Tasks.
9. **Work Packets** — Feature/Work Packet projections with Work Packet and Lifecycle visible.
10. **Product Backlog** — non-Closed MVP items ordered by Priority then Work Cycle.
11. **Defects** — Bug/Defect and engineering-control-plane maintenance work.
12. **Blocked** — Lifecycle or Status Blocked.
13. **Release 1** — all items contributing to `PG-001` / MVP Release 1.
14. **Dogfooding** — Monad-on-Monad work, especially EPIC-012 and related defects/evidence.
15. **AI / Agents** — AI context, agent governance, execution, and related work.
16. **Semantic Core** — workspace, ingestion, identity, graph, KIR, diagnostics, query/explanation.
17. **Architecture & Specs** — architecture, ADR, specification, requirement, or governance work.
18. **Codex Queue** — `Executor:Codex` or `Executor:Mixed`, Ready/Authorized/Running only.
19. **Release Readiness** — target MVP Release 1, focused on packaging, acceptance, risk, and verification.
20. **Risks & Decisions** — Critical/High Risk and change/decision work.
21. **Recently Completed** — recently Verified/Closed work.

The initial daily views should be **Program**, **MVP Roadmap**, **Current Work**, **Next Up**, **Defects**, and **Release 1**. The remainder are scoped projections for investigation and agent-assisted explanation.

## Hierarchy

Use native GitHub issue/sub-issue relationships where they are practical and do not contradict canonical planning data. The desired visible hierarchy is:

```text
Initiative
  └─ Epic
       └─ Feature
            ├─ Story
            │    └─ Task when refined
            └─ Enabler
                 └─ Task when refined
```

A Feature issue may carry its associated Work Packet identifier and execution fields. This does not make Work Packet an additional product-parent level.

Do not create a Project-only hierarchy that contradicts canonical Initiative/Epic/Feature relationships. If native GitHub hierarchy cannot represent a level cleanly, preserve the canonical IDs in fields and issue metadata rather than changing Monad's ontology to fit GitHub.

## Product delivery vs engineering-system work

Keep product-delivery hierarchy separate from control-plane maintenance/defect projection.

```text
Monad Development
├─ Product Delivery
│  └─ PG → Initiative → Epic → Feature → Story/Enabler → Task
└─ Engineering System / Control Plane
   ├─ Defects
   ├─ Maintenance
   ├─ Infrastructure
   ├─ Governance corrections
   └─ Tooling corrections
```

Control-plane defects may be release relevant, but they should not be forced into a product Epic when they are not semantically part of that Epic.

## Current planning position

At the time this configuration was amended, the projected planning position was:

`PG-001 → INIT-002 → EPIC-003 → F-003-03 / WP-MVP-0005`

The canonical Work Packet state was **Ready, not Authorized**. This statement is historical context only; live EOS state is authoritative.

## Automation boundary

Repository workflows may update repository-owned labels, milestones, Issues, hierarchy, and projections. Organization Project field/view mutations require organization authority.

The owner setup script:

- creates/reuses the Project;
- links the repository;
- creates missing canonical fields;
- does not create a separate Sprint field;
- adds repository Issues idempotently;
- derives Product Goal, Initiative, Epic, Feature, Work Packet, Work Cycle, item type, and explicit lifecycle metadata from the existing issue corpus;
- populates those Project fields idempotently with `gh project item-edit` where the corresponding canonical/projection data is explicit;
- leaves unrelated control-plane defects unforced into product hierarchy fields;
- warns when a legacy single-select field needs a one-time new option added in the Project UI;
- reports ambiguous duplicate field names rather than choosing nondeterministically.

View layout remains an explicit UI configuration because it is presentation rather than canonical authority. If GitHub later exposes a sufficiently stable supported automation path for views, it may be added without changing the canonical planning model.
