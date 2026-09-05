---
artifact_id: "EOSP"
title: "EOSP Planning"
type: "lifecycle-layer"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
---
# EOSP — Planning

## Purpose

Convert accepted product, architecture, and specification intent into bounded,
traceable execution units.

## Managed Objects

- milestones;
- program increments;
- work cycles;
- work packets;
- dependencies;
- risks;
- sequencing;
- readiness gates.

## Primary Commands

```bash
./scripts/eos plan PI-002
./scripts/eos create-wc --pi PI-002
./scripts/eos create-wp --wc WC-0002 --domain CORE
./scripts/eos authorize PI-002
./scripts/eos authorize WC-0002
./scripts/eos authorize WP-CORE-0001
```

## AI-Driven Planning Participation

EOSP is the lifecycle owner for adaptive engineering planning defined by
`EOS-AI-0001` and `FUN-AIENG-0001`.

An AI engineering participant MAY proactively:

- inspect governed planning state;
- compile relevant planning context;
- identify dependencies and sequencing;
- propose an adaptive engineering pathway;
- identify material ambiguity;
- recommend decisions or escalation;
- recommend decomposition, parallelism, or additional investigation;
- propose replanning when evidence or governing inputs change.

A proposed pathway is planning evidence, not lifecycle authority.

Adaptive planning MAY vary optional activity depth according to risk,
consequence, uncertainty, reversibility, dependencies, evidence, policy, and
autonomy profile, but MUST NOT bypass mandatory EOS gates, required authority,
blocking decisions, verification obligations, or review requirements.

Material ambiguity affecting consequential engineering meaning MUST route to
clarification or native decision semantics rather than being silently resolved
by AI inference.

Readiness remains distinct from authorization.
