# Architecture System

Architecture defines the system's significant structures, boundaries, quality
decisions, and evolutionary constraints. It exists to make change safer and
trade-offs explicit, not to prescribe implementation detail that can remain
local to a component.

## Architecture set

| Artifact | Purpose | Normative status |
| --- | --- | --- |
| `overview.md` | Major components, responsibilities, flows, and deployment shape | Baselined architecture |
| `context.md` | Actors, external systems, trust relationships, and dependencies | Baselined context |
| `principles.md` | Rules that guide structural decisions | Normative |
| `system-boundaries.md` | Ownership and allowed dependency directions | Normative |
| `quality-attributes.md` | Measurable runtime and change scenarios | Acceptance input |
| `diagrams/` | Maintained visual views with sources | Explanatory unless cited as normative |
| `decisions/` | Accepted and superseded ADRs | Normative decision history |
| `explorations/` | Time-bounded options and experiments | Informative until accepted |

## Decision threshold

Create an ADR when a choice changes a public contract, system boundary, data
ownership, trust boundary, runtime topology, strategic dependency, quality
budget, or operating model; is costly to reverse; or constrains multiple work
packets. Local implementation choices remain with the owning component when
they preserve established contracts and attributes.

## Review method

Review architecture from drivers to evidence:

1. Confirm the user outcome and constraints.
2. Test the proposed boundaries and dependency direction.
3. Walk the primary and failure flows.
4. Evaluate each quality-attribute scenario.
5. Identify threats, operational burden, cost, and migration risk.
6. Record accepted decisions, unresolved risks, and validation work.

## Consistency rules

Diagrams, prose, specifications, and code must use the shared terminology in
`governance/terminology.md`. A component owns authoritative state for its
declared responsibility. Cross-boundary interactions use explicit contracts.
Exceptions are visible, time-bounded, and linked to a remediation decision.
