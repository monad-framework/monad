---
artifact_id: "REV-MNT-0003"
title: "MNT-0003 Engineering Review"
type: "review"
version: "0.1.0"
status: "Accepted"
authority: "review-authoritative"
created: "2026-09-07"
updated: "2026-09-07"
---

# MNT-0003 — Engineering Review

**Decision:** ACCEPTED

## Target

- Maintenance item: `engineering/maintenance/MNT-0003.md`
- Verification review: `engineering/reviews/MNT-0003-EVENT-LEDGER-MERGE-SAFETY-VERIFICATION.md`
- Current lifecycle state: `VERIFYING`

## Review Basis

This review evaluates whether MNT-0003 may be formally closed after implementation and verification of merge-safe EOS event-history preservation and fail-closed divergent-history semantics.

Production checkpoints:

- `3fb8b8995e3d92ddab28115190fd6ad21ac4cd4c` — enforce event-history integrity;
- `0072d7f4bed954f2832db7403933b5fb9bf37e31` — remove temporary MNT-0003 integration machinery;
- `8a9deb9fbc5c49458605aa8e1a73e63947263ab8` — synchronize normal machine projection after production integration;
- `2d2247c673dd7f48c210a8063afe9135e4cd7ea8` — refresh pre-existing deterministic trace projection separately from MNT-0003 verification;
- `7dfe8323153f1d4bbbd93183f932b194e216775b` — formal MNT-0003 verification checkpoint.

## Governing Invariant

> Merge, synchronization, or reconciliation MUST NOT silently remove a previously recorded valid EOS event.

## Deterministic Verification

**Result:** PASS

Verified surfaces include:

- event identifier uniqueness and immutable payload semantics;
- inherited-event preservation in descendants and working trees;
- Git `merge=union` preservation for ordinary divergent append histories;
- immediate-parent preservation for committed merge history;
- merge-base validation for divergent histories;
- in-progress merge validation using `HEAD`, `MERGE_HEAD`, and merge base;
- fail-closed handling of same-entity concurrent lifecycle divergence;
- safe acceptance of independent concurrent lifecycle histories;
- fail-closed octopus-merge handling;
- canonical-state pre/post/status enforcement;
- evidence-consensus reconciliation enforcement;
- EOSV event-history integrity reporting;
- deterministic generated trace convergence after verification-artifact discovery.

## Scope Conformance

**PASS**

The repair remains bounded to MNT-0003 event-history merge safety.

It does not:

- make `.eos/events.jsonl` the canonical current-state authority;
- replace `.eos/state/current.json` as the sole canonical operational state;
- weaken EOS lifecycle transition rules;
- infer authority from Git merge behavior;
- automatically choose between contradictory same-entity lifecycle histories;
- replace MNT-0006 transaction atomicity;
- silently discard a parent event history during merge or reconciliation.

The pre-existing trace-projection drift discovered during verification was repaired in its own projection-only commit before the final MNT-0003 verification baseline and is not treated as MNT-0003 implementation scope.

## Architecture Conformance

**PASS**

The resulting architecture preserves the intended separation:

```text
.eos/state/current.json
    sole canonical current operational state

.eos/events.jsonl
    append-only mutation history plus Git provenance

Git merge=union
    preservation mechanism for divergent append histories

EOS event-history validation
    semantic integrity and conflict detection

Human-governed reconciliation
    authority boundary for unresolved same-entity divergence
```

Git preservation does not itself constitute semantic reconciliation.

## Event Preservation Findings

**PASS**

A previously recorded valid event cannot be silently removed from a descendant working history without event-history validation failing.

A merge result must contain each inherited parent event with its immutable payload intact.

Conflicting payloads for the same `event_id` fail closed.

## Divergent Lifecycle Findings

**PASS**

Independent lifecycle activity on different EOS entities can coexist after divergent development.

Concurrent lifecycle activity affecting the same EOS entity is preserved in history but rejected as semantically ambiguous until explicit governed reconciliation occurs.

This avoids converting merge order or filesystem behavior into lifecycle authority.

## Real Git-History Evidence

**PASS**

Verified scenarios include:

1. independent branch appends survive an actual Git merge;
2. a descendant commit that removes an inherited event is rejected;
3. same-entity concurrent lifecycle changes remain preserved but fail semantic reconciliation;
4. independent concurrent lifecycle changes remain acceptable;
5. working-tree removal of an inherited committed event is rejected before a subsequent EOS transaction can normalize over it.

## Canonical-State / Reconciliation Findings

**PASS**

Canonical state remains authoritative for current operational lifecycle state.

Evidence-consensus reconciliation cannot bypass event-history integrity: unsafe inherited or divergent event history fails before lifecycle evidence may be reconciled into canonical state.

## MNT-0006 Separation

**PASS**

MNT-0003 and MNT-0006 remain distinct controls:

- MNT-0003 protects event-history preservation across divergent Git histories and requires explicit reconciliation when semantic lifecycle histories conflict;
- MNT-0006 protects atomic rollback of a single failed local EOS transaction.

Neither control substitutes for the other.

## Test / Validation Evidence

Verified automated evidence:

```text
event-ledger merge-safety suite       16 tests PASS
canonical-state suite                 12 tests PASS
canonical reconciliation suite         3 tests PASS
EOS wrapper dispatch                  PASS
identifier-family suite               20 tests PASS
Git event-ledger merge attribute      merge=union
canonical EOS state                    CONSISTENT
evidence-consensus reconciliation     CONVERGED
EOSV core verification                 PASS
EOSV event-history integrity           PASS
verification trace determinism         PASS
EOSV overall result                    PASS
```

Dedicated verification artifact:

`engineering/reviews/MNT-0003-EVENT-LEDGER-MERGE-SAFETY-VERIFICATION.md`

Disposition:

**PASS — RECOMMEND MNT-0003 CLOSURE**

## Security / Reliability Findings

No blocking security or reliability finding remains within MNT-0003 scope.

The repair fails closed when inherited history is lost, when an immutable event payload changes, or when divergent lifecycle histories for the same entity require authority-bearing reconciliation.

## Blocking Findings

None.

## Non-Blocking Findings

1. Explicit reconciliation policy for contradictory same-entity lifecycle histories remains intentionally governed rather than automatic.
2. Git union merge is necessary preservation behavior but is not by itself semantic reconciliation.
3. Existing unrelated EOSV stale-evidence warnings remain outside MNT-0003 scope.
4. Future multi-parent/octopus reconciliation semantics may be expanded deliberately; the current implementation fails closed instead of guessing.

## Recommendation

**RECOMMEND ACCEPTED / CLOSED**

Implementation and verification evidence support formal closure of MNT-0003.

## Decision

**ACCEPTED — HUMAN PROJECT STEWARD — 2026-09-07**

Permitted final disposition:

- `ACCEPTED` — authorize formal MNT-0003 closure;
- `REJECTED` — return MNT-0003 to implementation;
- `BLOCKED` — retain `VERIFYING` pending additional evidence.

Closure authority was explicitly granted by the Human Project Steward:

> I approve MNT-0003 closure.

Durable authority record:

`engineering/reviews/DECISION-0010-2026-09-07-mnt-0003-closure-approval.md`
