---
artifact_id: "EOSC"
title: "EOSC Change Control"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
---

# EOSC — Change Control

## Purpose

Allow requirements, architecture, specifications, plans, and scope to evolve
without silently rewriting history or invalidating downstream work.

## Flow

`discovery -> impact analysis -> change request -> review -> approval ->
versioned artifact updates -> dependent replanning/reverification -> closure`

## Primary Commands

```bash
./scripts/eos impact ADR-0014
./scripts/eos change create ADR-0014 "Revise persistence boundary"
./scripts/eos change approve CR-0001
./scripts/eos change close CR-0001
```
