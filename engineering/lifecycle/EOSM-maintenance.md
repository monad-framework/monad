---
artifact_id: "EOSM"
title: "EOSM Maintenance"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSM — Maintenance

## Purpose

Govern long-lived defects, technical debt, security findings, dependencies,
operations, performance, and documentation maintenance.

## Categories

- bug;
- debt;
- security;
- dependency;
- operations;
- performance;
- documentation.

## Primary Commands

```bash
./scripts/eos maintain create debt "Refactor graph cache ownership"
./scripts/eos maintain close MNT-0001
```

Material maintenance that changes governing behavior or architecture enters
EOSC. Larger bodies of work can be promoted into EOSP.
