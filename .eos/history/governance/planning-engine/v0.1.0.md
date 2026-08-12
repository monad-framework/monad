---
artifact_id: "GOV-PLAN-0001"
title: "EOS Planning and Dependency Engine"
type: "governance"
version: "0.1.0"
status: "Draft"
authority: "governance-authoritative"
created: "2026-08-12"
updated: "2026-08-12"
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
