# Monad Engineering Program — GitHub Project Configuration

**Status:** Proposed  
**Scope:** organization-level GitHub Project for `monad-framework`

## Project identity

Preferred title: **Monad Engineering Program**.

The setup process MUST reuse a Project with this exact title if one already exists in the organization. It MUST NOT create a duplicate solely because the repository or backlog was refounded.

## Purpose

The Project is the portfolio and execution view over canonical Git engineering records and projected GitHub Issues. It is not an authority source for requirements, decisions, specifications, or Work Packet semantics.

## Fields

Retain GitHub's built-in Title, Assignees, Status, Labels, Milestone, Repository, and linked pull-request data. Create the following custom fields when missing:

| Field | Type | Values / meaning |
| --- | --- | --- |
| Item Type | Single select | Epic, Feature, Story, Enabler, Work Packet, Bug, Change Request |
| Priority | Single select | P0, P1, P2, P3 |
| Criticality | Single select | C0, C1, C2, C3, C4, C5 |
| Product Area | Text | semantic/product area |
| Increment | Text | e.g. PI-MVP-001 |
| Sprint | Text | e.g. WC-MVP-0001 |
| Story Points | Number | optional relative estimate; never hours/productivity |
| Risk | Single select | Critical, High, Medium, Low |
| Executor | Single select | Human, ChatGPT, Codex, Mixed |
| Work Packet | Text | canonical WP identifier |
| Specification | Text | governing specification identifiers |
| ADR | Text | governing ADR identifiers |
| Target Release | Text | e.g. MVP Release 1 |
| Start Date | Date | forecast/actual start |
| Target Date | Date | forecast target |

## Recommended status workflow

`Backlog → Ready → Active → Review → Blocked → Done`

Blocked is exceptional and may be exited to the appropriate prior/next state. Scheduling alone does not move an item to Ready. A Work Packet may become Ready only after its canonical readiness gates pass.

## Required views

Create these views in the Project UI after fields exist:

1. **Product Roadmap** — roadmap layout, grouped by Increment, date fields visible.
2. **Epics** — table filtered to `Item Type:Epic`.
3. **Product Backlog** — table/board for non-Done MVP items, ordered by Priority then Sprint.
4. **Current PI** — filtered to the active `PI-MVP-*` increment.
5. **Current Sprint** — board filtered to active Sprint, grouped by Status.
6. **Next Sprint** — refinement queue for the next Sprint.
7. **Refinement** — Backlog items without Ready state or missing planning metadata.
8. **Architecture & Specs** — items labeled/typed for architecture, ADR, specification, or governance work.
9. **Bugs & Debt** — Bug, defect, technical-debt work.
10. **Blocked** — `Status:Blocked`.
11. **Codex Queue** — `Executor:Codex` or `Executor:Mixed`, Ready/Active only.
12. **Release Readiness** — target MVP Release 1, grouped by milestone/status.
13. **Risks & Decisions** — Critical/High Risk and change/decision work.

## Hierarchy

Use native GitHub sub-issues as the primary visible hierarchy:

```text
Epic
  └─ Feature / Work Packet projection
       ├─ Story
       └─ Enabler
```

Do not create a second Project-only hierarchy that contradicts Issue sub-issue relationships.

## Automation boundary

Repository workflows may update repository-owned labels, milestones, Issues, and hierarchy. Organization Project field/view mutations require organization authority. The owner setup script creates/reuses the Project, creates missing fields, links the repository, and adds Issues. View layout remains an explicit UI configuration because it is presentation rather than canonical authority.
