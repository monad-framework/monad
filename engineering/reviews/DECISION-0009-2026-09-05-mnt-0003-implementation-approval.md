# DECISION-0009-2026-09-05 — MNT-0003 Implementation Approval

**Record type:** Governance authority decision
**Date:** 2026-09-05
**Subject:** MNT-0003 implementation authorization
**Authority:** Human Project Steward / Architecture Owner
**Disposition:** **APPROVED**
**Related:** MNT-0003, MNT-0006, DECISION-0006, DECISION-0008

## Decision

Implementation of:

`MNT-0003 — EOS event ledger is not merge-safe across divergent append histories`

is **APPROVED**.

The explicit human authority statement was:

> I approve the MNT-0003 merge-safe event-ledger plan for implementation.

## Approved Governing Invariant

> A merge, synchronization, or reconciliation operation MUST NOT silently remove a previously recorded valid EOS event.

For a resulting history `R` and immediate parent histories `P1...Pn`:

```text
events(P1) ∪ ... ∪ events(Pn) ⊆ events(R)

Inherited event identity and immutable event content must be preserved.

A result that cannot satisfy this condition must fail closed.

Approved Architecture

The approved implementation may:

retain .eos/events.jsonl as the append-only EOS mutation-history ledger;
add repository-native Git union behavior for that ledger;
introduce a focused event-ledger semantic validation utility;
validate inherited parent-event preservation;
reject conflicting duplicate event identities;
detect incompatible divergent lifecycle histories for the same EOS entity;
integrate event-history integrity into canonical reconciliation;
integrate appropriate event-history checks into EOS verification;
add deterministic regression and real Git-merge tests;
reproduce the original CR-0003 event-loss failure class.
Approved Git Behavior

The repository may establish:

.eos/events.jsonl merge=union

using Git's built-in union merge behavior.

This is a first-line preservation mechanism only.

It does not by itself establish semantic validity.

Conflict Semantics

Independent divergent histories may coexist when they do not create an unresolved lifecycle conflict.

For example:

branch A:
WP-X lifecycle event

branch B:
MNT-Y lifecycle event

may be preserved together.

By contrast:

base:
WP-X DRAFT

branch A:
DRAFT -> READY

branch B:
DRAFT -> BLOCKED

must preserve both historical events but must fail closed for authoritative reconciliation.

Line ordering must not choose the winner.

Stable Authority Boundary

This implementation does not change:

.eos/state/current.json as sole canonical current operational state;
EOS lifecycle authority;
human approval requirements;
MNT-0006 transaction-local atomicity;
Git's role as version-history and integrity ledger.

The event ledger remains historical mutation evidence and reconstruction input, not a competing current-state authority.

Scope Boundary

This approval does not authorize:

replacement of Git;
replacement of the event ledger with a database;
distributed consensus;
distributed transaction semantics;
external-side-effect atomicity;
arbitrary automatic resolution of conflicting lifecycle histories;
event deletion as conflict resolution;
unrelated EOS redesign.
Relationship to MNT-0006

MNT-0006 governs:

one local transaction
    -> COMMITTED
       or
    -> ROLLED_BACK

MNT-0003 governs:

valid committed history A
                   \
                    merge / synchronization
                   /
valid committed history B

The invariants remain independent.

Authority Consequence

EOS may transition:

MNT-0003
PLANNED
    ↓
IN_PROGRESS

and implementation may proceed within the approved MNT-0003 scope.

No additional implementation approval is required unless the architecture or scope materially changes.

Final verification, review, and closure remain separate authority gates.
