# WP-STAB-0004 — Synchronize the Machine Knowledge Layer

**Status:** Review  
**Owner:** Engineering Owner  
**Program:** STAB-0001

## Objective

Make `machine/` a complete deterministic projection of the current canonical repository tree and restore CI as a trustworthy drift gate.

## Scope

### In scope

- per-document machine companions;
- `machine/manifest.json`, `machine/graph.json`, `machine/corpus.jsonl`;
- source and companion hashes, stable document IDs, sections, identifiers, document relations;
- drift/orphan checks and deterministic ordering;
- regeneration after ADR and foundation changes.

### Out of scope

- treating the bootstrap machine graph as the final Monad Semantic Graph implementation;
- model-inferred semantic relations;
- editing machine outputs independently;
- changing source meaning only to satisfy a generator.

## Acceptance criteria

- [ ] Every discoverable canonical source has its expected machine representation.
- [ ] No stale or orphaned generated companions remain.
- [ ] Manifest source count/tree hash correspond to the current canonical source set.
- [ ] Repeated regeneration is idempotent.
- [ ] `python3 scripts/sync-machine-docs.py --check` passes in a clean checkout.
- [ ] CI fails when a canonical change is committed without required regenerated outputs.
- [ ] AI/retrieval guidance states that machine data is valid only when source hashes and sync checks match.

## Validation

Run `--write` then `--check`; modify a representative canonical file without regeneration and verify check failure; regenerate and confirm restoration. Verify ADR relocation and materialized artifact-system sources appear in the current manifest.

## Risks

The bootstrap machine graph may be confused with the future production MSG. Documentation must distinguish repository-document projection from the richer semantic kernel planned for MVP.

## Completion evidence

Successful stabilization materialization workflow runs and synchronized generated corpus on the reviewed stabilization head.
