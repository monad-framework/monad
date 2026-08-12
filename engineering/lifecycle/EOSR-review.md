---
artifact_id: "EOSR"
title: "EOSR Review"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
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
