# Architecture Decision Records

Architecture Decision Records preserve the context and consequences of
significant choices. An ADR explains why the accepted option was reasonable at
the time; it is not a retrospective claim that alternatives had no merit.

## Naming and lifecycle

Use `ADR-NNNN-short-kebab-title.md` with monotonically increasing numbers.
Statuses are `proposed`, `accepted`, `rejected`, `deprecated`, and `superseded`.
Accepted records are immutable except for factual corrections and status links.
A changed decision receives a new ADR that supersedes the old one.

## Process

1. Copy `ADR-0000-template.md` and assign the next number.
2. State the decision pressure and constraints before presenting options.
3. Compare at least two credible options, including continuing the current
   state when relevant.
4. Describe positive, negative, neutral, operational, security, and migration
   consequences.
5. Identify evidence required to validate uncertain claims.
6. Obtain reviews from affected owners and record the decision.
7. Link implementation and validation work.

## Decision index

| ADR | Title | Status | Date | Supersedes |
| --- | --- | --- | --- | --- |
| None | No architecture decision has been accepted yet | — | — | — |

Update the index in the same change that accepts or supersedes an ADR.

## ADR quality test

A reader unfamiliar with the discussion should understand the problem, forces,
chosen option, rejected options, trade-offs, and how success or failure will be
recognized. Vague preferences, technology lists without drivers, and decisions
that merely restate existing implementation are returned for revision.
