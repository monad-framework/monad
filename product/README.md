# Product System

The product documents translate durable vision into a coherent, testable
promise for specific users. They govern what the product does and why; the
architecture and specifications govern how that promise is realized.

## Product baseline

| Document | Primary question | Output |
| --- | --- | --- |
| `PRODUCT-GOAL.md` | What outcome defines the current release? | Current Product Goal and achievement evidence |
| `POST-MVP-PRODUCT-GOALS.md` | Which later outcomes are forecast without authorizing implementation? | Post-MVP Product Goal horizon |
| `PROGRAM-HIERARCHY.md` | How do product planning, execution, authority, and verification relate? | Canonical hierarchy and cross-dimensional trace model |
| `initiatives.md` | Which finite program outcomes organize the current Product Goal? | Initiative catalog and Epic mapping |
| `product-requirements.md` | What must the release accomplish? | Prioritized, testable requirements |
| `personas.md` | Whose goals and constraints matter? | Evidence-based user models |
| `use-cases.md` | Which actor-system interactions are supported? | Bounded behavioral contracts |
| `user-journeys.md` | How does the experience unfold over time? | End-to-end journey and recovery paths |
| `capabilities.md` | Which durable abilities must exist? | Capability map and ownership |
| `constraints.md` | Which limits shape feasible solutions? | Explicit design and delivery bounds |
| `roadmap.md` | In what outcome order will work occur? | Now/Next/Later investment sequence |
| `backlog/MVP-BACKLOG.md` | How is the current MVP decomposed for rolling-wave delivery? | Epic, Feature, Work Packet, and Story forecast |

## Planning hierarchy

The primary product-planning hierarchy is:

`Product Goal → Initiative → Epic → Feature → Story / Enabler → Task`

Execution is an orthogonal hierarchy:

`Program Increment → Work Cycle → Work Packet → Execution → Verification / Evidence`

The two views are joined by explicit trace relationships. In the current rolling-wave backlog, a Feature is commonly paired with a forecast Work Packet, but Feature and Work Packet are not the same ontology object: the Feature expresses a product/value outcome while the Work Packet carries governed execution authority and lifecycle state.

See `PROGRAM-HIERARCHY.md` for the normative planning clarification and cross-dimensional trace model.

Initiatives are finite outcome-oriented program groupings. Enduring capability/domain classifications, Program Increments, Work Cycles, Work Packets, executions, and engineering-governance artifacts remain orthogonal dimensions rather than extra hierarchy levels.

## Product decision flow

Research updates personas and problem evidence. Accepted evidence changes
requirements and journeys. Requirements map to capabilities and specifications.
Roadmap items are authorized only when they advance a goal and can be measured
against the success criteria.

Product Goals establish release outcomes. Initiatives organize finite program
outcomes under a Product Goal. Epics and Features decompose those outcomes into
planned delivery, while Work Packets govern executable realization near the
active horizon.

## Requirement rules

- Use stable identifiers; do not reuse retired IDs.
- State observable behavior without prescribing internals unnecessarily.
- Include preconditions, failure behavior, acceptance evidence, and priority.
- Link nonfunctional expectations to quality-attribute scenarios.
- Mark assumptions and unresolved decisions explicitly.
- Trace every committed requirement to a user outcome and at least one test.

## Baseline and change

The product baseline is approved at an increment boundary. Editorial
clarifications may merge through normal review when they do not change meaning.
Scope, behavior, compatibility, risk, or acceptance changes use the change
control process and update affected plans, specifications, and tests.
