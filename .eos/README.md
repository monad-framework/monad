# .eos

Internal Engineering Operating System control state.

Canonical human-authored engineering artifacts remain authoritative. `.eos/` records lifecycle/control projections, durable events, policy state, verification evidence, and execution metadata; it MUST NOT silently supersede accepted canonical requirements, decisions, specifications, or Work Packet contracts.

## Bootstrap and adoption

- `workflow.tsv` — ordered EOSB bootstrap workflow and its reconciled completion state;
- `adoptions/` — reviewed manifests used to adopt already-approved canonical program horizons into EOS without replaying obsolete bootstrap/planning work;
- `events.jsonl` — append-only lifecycle/event ledger, including adoption and supersession evidence.

An adoption is an explicit control-state transition, not a new source of product authority. It requires canonical evidence, validates parent relationships and lifecycle states, preserves existing matching objects, and is designed to be idempotent.

EOS 0.8 supports namespaced lifecycle identifiers such as `PI-MVP-001`, `WC-MVP-0001`, and `WP-MVP-0001` while preserving historical unqualified identifiers. Historical planning objects displaced by a stronger accepted baseline are retained as `SUPERSEDED`, never silently deleted or reused.

## Permanent lifecycle state

- `layers.tsv` — EOSB/EOSP/EOSE/EOSV/EOSR/EOSC/EOSL/EOSM;
- `program-increments.tsv` — PI state;
- `work-cycles.tsv` — WC state;
- `work-packets.tsv` — WP state;
- `change-requests.tsv` — EOSC state;
- `maintenance.tsv` — EOSM state;
- `releases.tsv` — EOSL state;
- `decisions.tsv` — gate/closure decision log;
- `trace-edges.tsv` — generated traceability graph;
- `contracts/` — bounded execution/review contracts;
- `evidence/` and `evidence.tsv` — verification/review evidence;
- `sync/` — external projection synchronization records;
- `state-machines/` — declarative lifecycle states and transitions;
- `schemas/` — lifecycle/control-state validation schemas;
- `policies/` — named policy-as-code gates.

## Rolling-wave rule

The full MVP roadmap remains canonical planning in human-authored product/engineering artifacts. EOS lifecycle registries SHOULD adopt only the execution horizon that is sufficiently refined to govern current work. A forecast date or backlog entry does not itself create lifecycle readiness or authorization.

## Read-only commands

Commands such as `status`, `next`, and gate inspection are observational. Some verification/trace operations may rebuild deterministic generated projections; when canonical inputs are unchanged, the resulting bytes must remain stable.

## History

- `artifact-changelog.tsv` — semantic artifact version changes;
- `history/` — retained prior governed artifact bodies;
- `checkpoints/` — checkpoint metadata;
- `prompts/` — generated prompt material.

This directory is intentionally committed to Git except for explicitly ephemeral files so control-state history remains reviewable and reproducible.
