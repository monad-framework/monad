---
artifact_id: "EOSR"
title: "EOSR Review"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
---
# EOSR — Review

## Purpose

Determine whether work conforms to its governing intent and whether it may
advance, close, release, or must return to planning/change control.

## Review Levels

- work packet;
- work cycle;
- program increment;
- architecture/change;
- release readiness;
- maintenance closure.

## Primary Commands

```bash
./scripts/eos review WP-CORE-0001
./scripts/eos close WP-CORE-0001
./scripts/eos close-cycle WC-0003
./scripts/eos close-pi PI-002
```

Deterministic checks are automated. Human authority is retained for final gates
that require risk acceptance or material tradeoffs.

## AI-Driven Review Participation

AI MAY participate in EOSR review when applicable policy permits it.

Where independent review is required, independence MUST be evaluated from the
actual review relationship rather than assumed from a second model invocation.

Relevant independence dimensions MAY include:

- executor identity;
- reviewer identity;
- model;
- provider;
- harness;
- context isolation;
- prompt isolation;
- organizational role;
- human participation.

A second invocation of the same model or harness MUST NOT automatically satisfy
an independent-review obligation.

AI review findings and dispositions are recommendations unless governance
explicitly delegates the applicable binding authority.

Reserved human acceptance, risk, architecture, security, operations, or release
authority remains reserved according to `governance/authority.md`.
