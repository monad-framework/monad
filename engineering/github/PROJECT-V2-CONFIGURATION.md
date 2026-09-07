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

`Product Goal`, `Initiative`, `Epic`, `Feature`, `Increment`, `Work Cycle`, `Work Packet`, and lifecycle identifiers in GitHub are projections. Their canonical definitions remain in repository/EOS artifacts.

### Compatibility and field migration

`Work Cycle` is the canonical Project field. The term `Sprint` remains a planning/UI compatibility synonym because Work Cycle == Sprint for the current roadmap, but setup/synchronization automation MUST NOT create or write a second competing Sprint field.

Historical Project configurations may contain legacy fields such as `Work-Cycle`, `Work-Packet`, `Sprint`, or `PI` alongside the canonical `Work Cycle`, `Work Packet`, or `Increment` fields.

Migration rules:

1. projection automation prefers an exact canonical field name;
2. when only one punctuation-equivalent field exists, `project-complete` renames it in place to the canonical name so field identity and existing values are preserved;
3. ambiguous normalized duplicates are blocking and MUST be reported rather than updated nondeterministically;
4. `PI` and `Sprint` are deprecated compatibility fields and are not automatically deleted because they may contain historical values;
5. deletion of `PI` or `Sprint` requires a separate value audit/migration proving that no unique Project-only information would be lost;
6. deleting or renaming a Project field never changes the canonical Git/EOS identifier or artifact.

## Status and lifecycle semantics

GitHub's built-in Status is a presentation/work-management convenience. Do not let it erase distinctions required by Monad governance.

At minimum preserve these semantic distinctions in the projected metadata and issue text:

1. **Planning/readiness** — Backlog, Refining, Ready.
2. **Authorization/execution** — Authorized, Running, Blocked.
3. **Review/evidence/completion** — Review, Verified, Closed.

Scheduling alone does not authorize implementation. A Work Packet may become Ready only after canonical readiness gates pass, and Ready does not imply Authorized.

## Required views

The required Project configuration contains 21 named views. The first six are the normal daily-use views; the rest are scoped projections for investigation and agent-assisted explanation.

1. **Program** — table emphasizing Initiatives and overall Product Goal progress.
2. **MVP Roadmap** — roadmap grouped by Initiative, showing Epics and Feature outcomes.
3. **Current Work** — board for Ready, Authorized, Running, Review, and Blocked work.
4. **Next Up** — Ready items near the executable horizon.
5. **Defects** — Bug/Defect and engineering-control-plane maintenance work.
6. **Release 1** — all items contributing to MVP Release 1.
7. **Work Cycles** — grouped by canonical Work Cycle.
8. **By Initiative** — grouped by Initiative.
9. **By Epic** — grouped by Epic.
10. **By Feature** — grouped by Feature where useful for Stories/Enablers/Tasks.
11. **Work Packets** — Feature/Work Packet projections with Work Packet and Lifecycle visible.
12. **Product Backlog** — non-Closed MVP items ordered by Priority then Work Cycle.
13. **Blocked** — Lifecycle Blocked.
14. **Dogfooding** — Monad-on-Monad work, especially GitHub projection/dogfooding.
15. **AI / Agents** — AI context, agent governance, execution, and related work.
16. **Semantic Core** — workspace, ingestion, graph, KIR, diagnostics, query/explanation.
17. **Architecture & Specs** — governance-oriented work with ADR and Specification fields visible.
18. **Codex Queue** — Codex/Mixed items in Ready, Authorized, or Running lifecycle states.
19. **Release Readiness** — MVP Release 1 release/acceptance work.
20. **Risks & Decisions** — Critical/High Risk work with ADR and Specification context visible.
21. **Recently Completed** — Verified/Closed work updated within the recent window.

The default view definitions are encoded in `scripts/configure-github-project.py`. An existing same-named view is preserved rather than overwritten so intentional user layout/filter customization is not destroyed. Verification reports material differences from canonical defaults as notes.

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

## Automation

Organization Project configuration is a coordination projection and requires organization Project write authority. The repository provides two complementary automation layers:

- `scripts/setup-github-owner.sh` is the owner-facing entry point;
- `scripts/configure-github-project.py` manages Project-specific option, view, migration, and verification behavior;
- `scripts/sync-github-project-metadata.py` derives and writes planning metadata from the GitHub Issue corpus.

### Core synchronization

```bash
./scripts/setup-github-owner.sh project
```

The core pass:

- creates/reuses the Project;
- links the repository;
- creates missing canonical fields;
- canonicalizes safe punctuation-only field aliases;
- adds missing required Item Type/Lifecycle options while preserving existing option identities;
- adds repository Issues idempotently;
- projects the hierarchy-first core surface: Initiatives, Epics, Features, Work Packets, defects, bugs, and change requests.

### Full synchronization

```bash
./scripts/setup-github-owner.sh project-full
```

The full pass additionally projects Story, Enabler, Task, and other deeper issue metadata. Formal Tasks remain rolling-wave objects and are projected only when such Task issues actually exist.

### Project completion

```bash
./scripts/setup-github-owner.sh project-complete
```

The completion pass is the acceptance path for the GitHub Project configuration. It:

1. converges canonical fields and required single-select options;
2. ensures every repository Issue is present;
3. runs the full metadata projection;
4. creates every missing required Project view through GitHub's supported Project view API;
5. verifies canonical fields and options;
6. verifies all 21 required view names;
7. verifies repository-issue coverage;
8. runs representative Project queries for Initiatives, MVP Release 1, Tasks, and Ready/active work.

The command is idempotent: rerunning it MUST converge without creating duplicate fields, duplicate Project items, or duplicate named views.

### Verification only

```bash
./scripts/setup-github-owner.sh project-verify
```

This performs the non-destructive Project acceptance checks without running the metadata synchronization first.

## Automation boundary

The automation MAY manage repository-owned labels, milestones, Issues, native hierarchy, Project fields, Project select options, Project items, and missing named Project views when supported by GitHub APIs.

It MUST NOT:

- make GitHub Project state authoritative over canonical Git/EOS state;
- infer authorization from scheduling;
- manufacture Work Packets or Tasks outside rolling-wave refinement;
- delete potentially data-bearing legacy fields without an explicit value migration;
- overwrite an existing same-named view merely to enforce presentation preferences;
- force unrelated control-plane defects into product hierarchy fields.

View layout remains a presentation concern after the canonical default view has been created. Users may customize an existing view without changing Monad's planning ontology.
