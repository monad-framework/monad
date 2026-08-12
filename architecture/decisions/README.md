# Architecture Decision Records

`architecture/decisions/` is the **canonical Architecture Decision Record (ADR) root for Monad**. The former root-level `adrs/` directory is retired and MUST NOT be recreated.

Architecture Decision Records preserve the context and consequences of significant choices. An ADR explains why the accepted option was reasonable at the time; it is not a retrospective claim that alternatives had no merit.

## Authority

Accepted ADRs are normative architectural authority subject to higher-order constitutional, legal, security, and explicitly governing project constraints. Lower-authority implementation, planning, generated material, GitHub metadata, EOS machine state, or agent output MUST NOT silently contradict an accepted ADR.

Moving an ADR into this directory changes its canonical repository location, not its historical identity, acceptance state, or decision meaning. Git history preserves prior locations and provenance.

## Naming and lifecycle

Use `ADR-NNNN-short-kebab-title.md` with monotonically increasing numbers. Stable ADR identifiers MUST NOT be reused for a different decision.

Statuses are:

- Proposed
- Accepted
- Rejected
- Deprecated
- Superseded

Accepted records are immutable in decision meaning. Factual corrections, metadata normalization, location migration, and explicit status/supersession links may be added without rewriting the historical decision. A materially changed decision receives a new ADR that supersedes the old one.

## Process

1. Copy `ADR-0000-template.md` and assign the next available number.
2. State the decision pressure, constraints, and relevant governing authority before presenting options.
3. Compare credible alternatives, including continuing the current state when relevant.
4. Describe positive, negative, neutral, operational, security, compatibility, migration, and reversibility consequences as applicable.
5. Identify evidence required to validate uncertain claims.
6. Obtain reviews from affected owners and record the decision authority and effective status.
7. Link downstream specifications, Work Packets, implementation, validation, migration, and supersession work.
8. Update the decision index in the same change that accepts, rejects, deprecates, or supersedes an ADR.

## Decision index

| ADR | Title | Status | Date | Supersedes |
| --- | --- | --- | --- | --- |
| [`ADR-0001`](ADR-0001-knowledge-engine-core.md) | The Knowledge Engine Is the Core of Monad | Accepted | 2026-08-03 | — |

## Machine and EOS projections

Machine companions, semantic-graph nodes, `.eos/` records, GitHub Issues/Projects, and generated indexes MAY reference ADRs by stable identifier and canonical path. Those projections MUST retain provenance to the canonical ADR and MUST NOT become a competing editable source of decision truth.

If a projection references the retired `adrs/` path, the reference should be migrated to `architecture/decisions/` while preserving the ADR identifier. A stale projection has no authority over the canonical source.

## ADR quality test

A reader unfamiliar with the original discussion should be able to determine:

- what problem or decision pressure existed;
- what authority and constraints governed the decision;
- which option was chosen and why;
- which credible alternatives were rejected and why;
- what trade-offs and consequences were accepted;
- what downstream artifacts and implementation are affected; and
- how success, failure, supersession, or required reconsideration can be recognized.

Vague preferences, technology lists without drivers, or records that merely restate existing implementation are returned for revision.
