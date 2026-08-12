# EOS Single Canonical State Model

**Status:** Implemented  
**Authority:** Normative  
**Version:** 1.0.0

## Decision

`.eos/state/canonical.json` is the sole authority for current EOS operational state.

All other representations have narrower roles:

| Representation | Role | Authority over current operational state |
|---|---|---|
| `.eos/state/canonical.json` | Machine-readable current state | **Canonical** |
| `.eos/events.jsonl` | Immutable mutation/audit history | Historical evidence; not current-state authority |
| TSV registries | Compatibility/query projections | None |
| Markdown | Governed human-readable artifacts | Content authority; embedded operational metadata is projected |
| Git | Versioned history and provenance | None by itself |
| GitHub Issues/Projects/milestones/labels | Collaboration projection | None |

## Mutation rule

Operational state changes must enter EOS through a governed mutation and be represented in canonical machine metadata. An event must record the mutation. TSV, Markdown, and GitHub are then synchronized from canonical state. Editing a projection is never sufficient to change EOS state.

## Drift rule

A mismatch is not resolved by guessing which copy is newest. It is classified as **state drift**, verification fails, and repair proceeds from canonical state outward. Silent reconciliation is forbidden.

`python tools/eos/state_model.py verify` checks:

- canonical lifecycle states against the domain model;
- canonical state against the append-only event history;
- canonical state against TSV compatibility registries;
- lifecycle/status markers in governed Markdown artifacts;
- registry entities that lack canonical entities;
- GitHub synchronization revision and entity fingerprints when GitHub mappings exist.

The `EOS State Integrity` GitHub Actions workflow makes drift CI-blocking.

## Initial migration decision

At introduction time PI-001 and WC-0001 already demonstrated the problem this model addresses: their machine registry/event state was `DRAFT` while their Markdown displayed `Planned`. Operational history and registries were used to establish `DRAFT` as the migration state, and Markdown was repaired as a projection. Human-facing titles were retained as canonical titles and the TSV title columns were repaired from them.

## GitHub synchronization contract

`.eos/sync/github-projection.json` records synchronized GitHub entities. Each synchronized entry must carry the canonical state revision and a SHA-256 fingerprint of its canonical entity. GitHub-originated changes to operational fields are treated as proposed collaboration input, not authoritative state changes, until converted into an EOS mutation.

## Non-negotiable invariant

There is one current operational truth. Everything else is either governed human content, history, evidence, or a projection.
