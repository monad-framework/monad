---
artifact_id: "EOSC"
title: "EOSC Change Control"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
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

## AI-Driven Replanning and Governing Drift

AI-driven work MUST enter EOSC when execution, verification, review, operational
evidence, or newly compiled context reveals that governing engineering meaning
must change.

Examples include changes to:

- requirements;
- accepted architecture;
- specifications;
- security constraints;
- accepted risk;
- operational commitments;
- authorized scope;
- acceptance criteria;
- release obligations.

An AI participant MAY identify the need for change, perform impact analysis,
recommend alternatives, and draft a Change Request.

It MUST NOT silently mutate governing meaning in order to keep execution
moving.

When material governing-input drift invalidates an existing pathway or
authorization, dependent work MUST be suspended, replanned, reauthorized,
reverified, or otherwise explicitly dispositioned before relying on stale
authority.

Evidence that invalidates a planning assumption is a trigger for replanning or
change control, not permission to bypass governance.
