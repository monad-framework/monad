# Product Increments

A Program/Product Increment is an integrated, potentially releasable advance that proves a bounded product outcome or retires a material risk. It combines all work needed for acceptance rather than handing partially complete layers between teams.

## Active naming

Monad uses namespaced immutable IDs:

- `PI-MVP-NNN` for MVP Release 1 increments;
- `PI-EXP-NNN` for the approved CR-0002 post-MVP expansion;
- future programs introduce a namespace through governed planning rather than reusing ambiguous bootstrap IDs.

An increment typically spans two to six Work Cycles. If useful evidence cannot be demonstrated within that horizon, split the outcome or authorize a separate exploration. A longer forecast requires explicit rationale and frequent reforecasting.

## Current roadmap

### MVP Release 1 / PG-001

- PI-MVP-001 — Semantic Foundation
- PI-MVP-002 — Intelligence and Agent Context
- PI-MVP-003 — Integration and MVP Release

### Expanded roadmap / CR-0002

- PI-EXP-001 — Living Intelligence — PG-002 / M-004
- PI-EXP-002 — Governed Automation & Trust — PG-003 / M-005
- PI-EXP-003 — Ecosystem, Deployment & Scale — PG-004 / M-006

## Required content

- objective, parent Product Goal, and parent milestone;
- user, system, or risk outcome;
- included and excluded requirements;
- architecture decisions and specifications;
- ordered Work Packets and dependency chain;
- acceptance, quality, security, privacy, operations, documentation, audit, and provenance evidence as applicable;
- release/exposure strategy and rollback;
- capacity assumption, forecast, and decision dates;
- active risks and stop conditions.

## Increment review

The review demonstrates the integrated result in a representative environment, not a slide summary or collection of component reports. Reviewers inspect acceptance evidence, failed or waived gates, user findings, system behavior, security/privacy posture, cost, performance claims, audit/attestation evidence where applicable, and risks. The recorded decision is `accept`, `accept with corrective work`, `continue`, `re-scope`, or `stop`.

## Closure

An increment closes only after its review decision, status, risk changes, changelog impact, unfinished work, milestone/Product Goal implications, and required evidence/attestations are recorded. Work that no longer advances the outcome is removed rather than carried as historical obligation.
