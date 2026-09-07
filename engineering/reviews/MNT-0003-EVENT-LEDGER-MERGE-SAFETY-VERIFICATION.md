---
artifact_id: "MNT-0003-VERIFICATION"
title: "MNT-0003 Event Ledger Merge-Safety Verification"
type: "review"
version: "0.1.0"
status: "COMPLETE"
authority: "verification-authoritative"
created: "2026-09-07"
updated: "2026-09-07"
target: "MNT-0003"
disposition: "PASS"
---

# MNT-0003 — Event Ledger Merge-Safety Verification

**Disposition:** PASS — RECOMMEND MNT-0003 CLOSURE

## Target

`engineering/maintenance/MNT-0003.md`

## Verification Baseline

Stable post-integration baseline:

`8a9deb9fbc5c49458605aa8e1a73e63947263ab8`

Production integration checkpoints:

- `3fb8b8995e3d92ddab28115190fd6ad21ac4cd4c` — enforce event-history integrity;
- `0072d7f4bed954f2832db7403933b5fb9bf37e31` — remove temporary integration machinery;
- `8a9deb9fbc5c49458605aa8e1a73e63947263ab8` — synchronize normal machine projection after integration.

## Invariant Under Review

> Merge, synchronization, or reconciliation MUST NOT silently remove a previously recorded valid EOS event.

## Verified Controls

PASS:

- `.eos/events.jsonl` uses Git `merge=union` for ordinary divergent append preservation;
- inherited event identity is immutable;
- a child/working ledger may not silently delete an event inherited from `HEAD`;
- a merge result must preserve every event from each parent ledger;
- conflicting payloads for the same `event_id` fail closed;
- independent divergent lifecycle histories are preserved;
- divergent lifecycle changes to the same EOS entity fail closed for explicit governed reconciliation;
- octopus event-history merges fail closed rather than guessing reconciliation semantics;
- committed merge history is checked against immediate parents and merge base;
- in-progress Git merge history is checked against `HEAD`, `MERGE_HEAD`, and the merge base;
- canonical-state pre/post/status paths enforce event-history integrity;
- evidence-consensus canonical reconciliation enforces event-history integrity;
- EOSV exposes event-history integrity as a first-class verification dimension.

## Deterministic Regression Evidence

PASS:

- event-ledger merge-safety suite: 16 tests;
- canonical-state suite: 12 tests;
- canonical reconciliation suite: 3 tests;
- EOS wrapper dispatch: PASS;
- identifier-family suite: 20 tests;
- Git merge attribute: `.eos/events.jsonl merge=union`;
- canonical operational state: CONSISTENT;
- evidence-consensus reconciliation: already converged;
- EOSV core verification: PASS;
- EOSV event-history integrity: PASS;
- generated trace projection converges after verification-artifact discovery and remains byte-stable on the subsequent identical verification pass;
- EOSV overall result: PASS.

## Real Git-History Scenarios

PASS:

1. Independent branch appends survive an actual Git merge.
2. A descendant commit that removes an inherited event is rejected.
3. Same-entity concurrent lifecycle changes are retained by Git but rejected semantically as ambiguous.
4. Independent concurrent lifecycle changes remain acceptable.
5. Working-tree deletion of a committed event is rejected before a later EOS transaction can normalize over it.

## Canonical-State / Reconciliation Findings

PASS.

The repair does not make the event ledger the canonical current-state authority. `.eos/state/current.json` remains the sole canonical operational state. Event history remains append-only mutation history plus Git provenance.

Evidence reconciliation cannot be used to bypass the history invariant: unsafe event history fails before accepted lifecycle evidence may be reconciled into canonical state.

## Scope Findings

PASS.

MNT-0003 remains distinct from MNT-0006:

- MNT-0003 governs preservation and semantic reconciliation of divergent committed event histories;
- MNT-0006 governs atomic rollback of one failed local EOS transaction.

The implementation does not replace MNT-0006 transaction atomicity and does not broaden the event ledger into canonical current state.

## Blocking Findings

None.

## Non-Blocking Findings

1. Explicit governed reconciliation policy for a same-entity divergent lifecycle history remains intentionally outside automatic merge semantics; the system fails closed instead of inventing authority.
2. Git union merge is a preservation mechanism, not sufficient semantic reconciliation by itself; EOS semantic validation remains authoritative.
3. Existing unrelated EOSV stale-evidence warnings remain outside MNT-0003 scope and do not invalidate event-history verification.

## Recommendation

**PASS — RECOMMEND MNT-0003 CLOSURE**

Formal closure remains subject to ordinary EOS maintenance closure gates and an explicit Human Project Steward decision.
