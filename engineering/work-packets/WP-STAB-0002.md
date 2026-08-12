# WP-STAB-0002 — Consolidate ADR and Authority Structure

**Status:** Review  
**Owner:** Architecture Owner  
**Program:** STAB-0001

## Objective

Make `architecture/decisions/` the single canonical ADR location and remove contradictory decision-path/status information from active repository authority.

## Scope

### In scope

- move/preserve ADR-0001 under `architecture/decisions/`;
- retire the top-level `adrs/` path;
- update `.monad/manifest.yaml`, ADR index, repository guidance, and machine projection;
- preserve accepted ADR history and status.

### Out of scope

- silently rewriting ADR-0001 meaning;
- accepting additional architecture decisions;
- broad C1 architecture review, which belongs to WP-STAB-0008/WP-ARCH-0001.

## Acceptance criteria

- [ ] One live ADR root exists: `architecture/decisions/`.
- [ ] ADR-0001 exists there with its Accepted status/history preserved.
- [ ] `.monad` points to the same decision path.
- [ ] ADR index recognizes ADR-0001 and does not claim the accepted-decision set is empty.
- [ ] No canonical guidance points contributors to the retired `adrs/` path.
- [ ] Machine projection reflects the canonical move without stale/orphaned companions.

## Validation

Search canonical repository content and generated manifest for live references to the retired ADR path; verify only historical/explanatory references remain where intentionally preserved.

## Risks

Path migration can create duplicate document identities or broken links. Treat the move as lineage-preserving architectural history and regenerate all derived representations.

## Completion evidence

User ADR-move commit, stabilization merge/reconciliation commit, updated ADR index/manifest, and green machine synchronization check.
