---
artifact_id: "GOV-PLAN-0001"
title: "EOS Planning and Dependency Engine"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-09-05"
---
# EOS Planning and Dependency Engine

EOSP treats PI/WC/WP planning as a dependency graph rather than a flat backlog.

Work-packet dependencies may be declared explicitly:

```markdown
- depends-on: WP-CORE-0006
```

## Commands

```bash
./scripts/eos planning check PI-002
./scripts/eos planning order PI-002
./scripts/eos planning critical-path PI-002
./scripts/eos planning graph PI-002 --format mermaid
./scripts/eos planning size WP-CORE-0007
```

## Planning Invariants

- work-packet dependency cycles are invalid;
- referenced dependency WPs must exist;
- dependency execution order must place prerequisites first;
- READY or later work packets must have bounded, non-TBD definitions;
- authorization state must be consistent with parent lifecycle state;
- oversized work packets should be decomposed before execution where practical.

Sizing is heuristic advisory evidence, not a substitute for engineering
judgment.

## Adaptive AI-Driven Pathway Planning

The planning engine MAY derive or accept an inspectable adaptive engineering
pathway under `EOS-AI-0001` and `FUN-AIENG-0001`.

Pathway derivation SHOULD consider materially applicable:

- governed intent;
- lifecycle state;
- requirements and specifications;
- ADRs and decisions;
- authority and policy;
- dependencies and blockers;
- risk and consequence;
- uncertainty and novelty;
- reversibility;
- evidence;
- unresolved decisions;
- autonomy profile.

A pathway SHOULD identify:

- proposed activities and sequencing;
- mandatory versus optional activities;
- unresolved material questions;
- required decisions and approvals;
- expected verification and review obligations;
- escalation conditions;
- structured rationale for material changes in rigor.

The pathway is a derived planning projection.

It MUST NOT become a second lifecycle state authority, and pathway optimization
MUST NOT bypass mandatory EOS gates.

Low-risk reversible work MAY receive a lightweight pathway. Higher-consequence,
security-sensitive, uncertain, or difficult-to-reverse work SHOULD receive
deeper planning, evidence, authority, and review where applicable.
