# DECISION-0010-2026-09-07 — MNT-0003 Closure Approval

**Record type:** Governance authority decision
**Date:** 2026-09-07
**Subject:** MNT-0003 closure authorization
**Authority:** Human Project Steward / Architecture Owner
**Disposition:** **APPROVED**
**Related:** MNT-0003, MNT-0003-VERIFICATION, REV-MNT-0003, DECISION-0009, MNT-0006

## Decision

Closure of:

`MNT-0003 — EOS event ledger is not merge-safe across divergent append histories`

is **APPROVED**.

The explicit human authority statement was:

> I approve MNT-0003 closure.

## Basis

The approval follows:

- implementation of repository-native loss-resistant event-ledger merge behavior;
- deterministic inherited-event and event-identity validation;
- fail-closed handling of conflicting immutable event payloads;
- fail-closed handling of same-entity divergent lifecycle histories;
- successful preservation of independent divergent histories;
- canonical-state and evidence-consensus reconciliation integration;
- EOSV event-history integrity integration;
- real Git-history scenario validation reproducing the historical-loss failure class;
- successful canonical-state, reconciliation, wrapper-dispatch, and identifier-family regression suites;
- deterministic trace-projection convergence;
- `PASS — RECOMMEND MNT-0003 CLOSURE` from the dedicated verification review;
- acceptance of the formal MNT-0003 engineering closure review.

## Accepted Governing Invariant

> A merge, synchronization, or reconciliation operation MUST NOT silently remove a previously recorded valid EOS event.

For a resulting history `R` and immediate parent histories `P1...Pn`:

```text
events(P1) ∪ ... ∪ events(Pn) ⊆ events(R)
```

Inherited event identity and immutable event content remain preserved. A result that cannot satisfy the invariant must fail closed.

## Accepted Scope

The accepted result establishes that:

- `.eos/events.jsonl` remains append-only mutation history rather than canonical current state;
- `.eos/state/current.json` remains the sole canonical current operational state;
- Git `merge=union` provides first-line preservation for ordinary divergent append histories;
- EOS semantic validation remains authoritative for event-history integrity;
- contradictory same-entity lifecycle histories remain blocked pending explicit governed reconciliation;
- independent divergent histories may coexist when semantically compatible;
- MNT-0006 transaction-local atomicity remains a separate invariant.

## Scope Boundary

This approval does not authorize:

- replacement of Git;
- replacement of the event ledger with a database;
- distributed consensus or distributed transaction semantics;
- external-side-effect atomicity;
- automatic authority-bearing resolution of contradictory lifecycle histories;
- event deletion as conflict resolution;
- unrelated EOS redesign.

## Authority Consequence

EOS may transition:

```text
MNT-0003
VERIFYING
    ↓
CLOSED
```

through the ordinary `MNT_CLOSE` gate.

No override is authorized or required.

This decision grants closure authority only. It does not expand implementation authority beyond DECISION-0009 or alter any independent governance boundary.
