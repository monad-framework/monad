# Specifications

Specifications turn approved product and architecture intent into precise,
testable contracts. They describe required behavior at a boundary or within an
owned concern without duplicating implementation code.

## Classification

- `functional/` — domain behavior, rules, states, and user-visible outcomes.
- `technical/` — runtime protocols, algorithms, resource budgets, and platform
  constraints.
- `interfaces/` — synchronous APIs, events, files, commands, and compatibility.
- `data/` — canonical models, ownership, classification, retention, and quality.
- `security/` — control behavior, identities, permissions, crypto, and evidence.
- `operations/` — deployment, telemetry, service objectives, backup, and
  recovery contracts.

## Identifier and filename

Use `<CLASS>-<AREA>-NNNN-short-title.md`, for example
`FUN-WORKFLOW-0001-state-model.md`. IDs are never reused. A specification states
its status, owner, reviewers, version, related requirements, decisions, risks,
and verification assets.

## Required anatomy

1. **Purpose and scope** — the contract and what it excludes.
2. **Definitions** — precise terms, units, and identifiers.
3. **Preconditions and invariants** — truths required before and during use.
4. **Normative behavior** — inputs, outputs, states, rules, errors, and timing.
5. **Security and data** — classification, authority, privacy, and evidence.
6. **Failure and recovery** — invalid, denied, transient, partial, unknown, and
   terminal behavior.
7. **Compatibility** — versioning, consumer obligations, and migration.
8. **Verification** — tests, examples, telemetry, and acceptance mapping.

## Normative language

`MUST` and `MUST NOT` are mandatory; `SHOULD` and `SHOULD NOT` require a
documented reason for deviation; `MAY` is optional. Use these terms only for
verifiable behavior. Examples clarify a rule but do not silently expand it.

## Lifecycle

Statuses are `draft`, `review`, `approved`, `implemented`, `deprecated`, and
`retired`. Approved meaning changes require version impact, affected-consumer
analysis, updated verification, and change approval. Code and tests may reveal
a specification defect, but they do not silently supersede the approved text.

## Traceability

Every committed product requirement maps to at least one specification or a
documented reason none is needed. Each normative rule maps to automated or
manual evidence. Release review reports missing, failed, or waived evidence.
