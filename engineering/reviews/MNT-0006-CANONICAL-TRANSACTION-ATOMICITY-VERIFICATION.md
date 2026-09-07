---
title: "MNT-0006 Canonical Transaction Atomicity Verification"
artifact_id: "MNT-0006-VERIFICATION"
version: "1.0.0"
status: "COMPLETE"
classification: "Maintenance Verification Review"
target: "MNT-0006"
date: "2026-09-05"
disposition: "PASS"
---

# MNT-0006 — Canonical Transaction Atomicity Verification

## Purpose

This review verifies the implementation of MNT-0006:

> EOS canonical transaction failure leaves rejected projection and event mutations.

The required invariant is:

> Either the entire EOS mutation is captured as one consistent canonical transaction, or all transaction-local mutations are automatically returned to their exact pre-transaction state.

This verification concerns local repository and EOS transaction atomicity. It does not claim distributed transaction atomicity for irreversible external effects such as GitHub writes, publication, release distribution, or other external systems.

## Governing Approval

Implementation was authorized by:

- `engineering/reviews/DECISION-0006-2026-09-05-eos-hardening-maintenance-implementation-approval.md`

The approved sequencing required MNT-0006 to be implemented and verified before MNT-0005 proceeds.

## Implementation Under Review

Primary implementation commits:

- `2672b6969ed4cf258cf5851acf6f9d6e51364062` — `fix(eos): make canonical transactions locally atomic`
- `3a1f67b825a4c7b1184a6e5a7fbd791488501ef2` — `fix(eos): correct transaction rollback verification`

Evidence checkpoint:

- `c186ff4c00fd9961e30fdccd57db26a44a493a8d` — `test(eos): checkpoint transaction atomicity evidence`

Principal implementation surfaces:

- `scripts/eos`
- `tools/eos/canonical_state.py`
- `tools/eos/test_canonical_state.py`
- `tools/eos/test_wrapper_dispatch.py`

## Implemented Transaction Semantics

The implementation establishes a transaction-scoped before-image mechanism for local EOS-governed mutation surfaces.

At canonical preflight:

1. the current canonical revision and digest are recorded;
2. local EOS/governance files potentially owned by the transaction are snapshotted;
3. each before-image is checksummed;
4. the transaction receipt references the snapshot set.

On successful execution:

1. the selected EOS runtime executes;
2. canonical post-validation checks projection consistency;
3. canonical state is advanced only if the resulting state is valid;
4. the active transaction receipt and before-images are removed only after postconditions succeed.

On rejected execution:

1. all before-image checksums are validated before restoration;
2. files created by the rejected transaction within transaction-owned surfaces are removed;
3. pre-existing files are restored byte-for-byte;
4. canonical/projection consistency is revalidated;
5. successful rollback removes the active receipt and before-images;
6. rollback failure retains recovery material and fails closed.

## Automated Test Verification

The canonical-state suite verifies:

- successful transaction progression;
- rejected lifecycle transition rollback;
- exact canonical/projection/event restoration;
- rejected entity-creation rollback;
- removal of transaction-created artifacts;
- preservation of pre-existing dirty governance bytes;
- successful receipt and before-image cleanup;
- corrupt before-image detection;
- fail-closed preservation of recovery material.

The wrapper-dispatch suite verifies:

- normal runtime dispatch;
- runtime failure rollback dispatch;
- canonical post-validation failure rollback dispatch;
- preservation of the original failure status when rollback succeeds;
- fail-closed wrapper status when rollback itself fails;
- explicit recovery-required diagnostics.

Observed result:

```text
Canonical state tests: PASS
Canonical reconciliation tests: PASS
EOS wrapper dispatch: PASS
````

## Independent Isolated Fault Verification

Verification was repeated against corrected implementation commit:

`3a1f67b825a4c7b1184a6e5a7fbd791488501ef2`

using two disposable detached Git worktrees.

### Scenario A — Canonical Post-Validation Failure

Fault injected:

* runtime lifecycle mutation was allowed to proceed;
* MNT-0006 TSV/event/visible lifecycle state moved toward `VERIFYING`;
* frontmatter remained deliberately inconsistent at `IN_PROGRESS`.

Observed rejection:

```text
ERROR: Successful command left inconsistent projections; canonical state was NOT advanced:
- MNT-0006 cannot be captured: TSV=VERIFYING frontmatter=IN_PROGRESS
```

Observed rollback:

```text
EOS canonical transaction rolled back; local projections consistent.
```

Post-rollback result:

```text
SCENARIO A: PASS
RESULT: CONSISTENT
```

The verification compared pre- and post-command fingerprints for:

* `.eos/state/current.json`
* `.eos/state/projections.json`
* `.eos/maintenance.tsv`
* `.eos/events.jsonl`
* `engineering/maintenance/MNT-0006.md`
* a pre-existing dirty governance file

All compared equal after rollback.

The test also verified:

* MNT-0006 remained `IN_PROGRESS`;
* no active transaction receipt remained;
* no transaction backup directory remained;
* a rollback diagnostic was retained.

### Scenario B — Runtime Failure After Local Mutation

Fault injected:

* the runtime first mutated the MNT-0006 lifecycle surfaces;
* the runtime then deliberately raised an error before successful completion.

Observed failure:

```text
ERROR: forced MNT-0006 runtime failure after local mutation
```

Observed rollback:

```text
EOS canonical transaction rolled back; local projections consistent.
```

Post-rollback result:

```text
SCENARIO B: PASS
RESULT: CONSISTENT
```

The same canonical, registry, event, Markdown, and dirty-user bytes were verified unchanged after rollback.

The test also verified:

* MNT-0006 remained `IN_PROGRESS`;
* transaction-created local mutations did not survive;
* no active transaction receipt remained;
* no transaction backup directory remained.

## Verified Invariants

### INV-MNT6-01 — Canonical State Does Not Advance on Rejection

**PASS**

Rejected transactions leave the canonical revision and digest unchanged.

### INV-MNT6-02 — Projection Mutations Are Atomic

**PASS**

Rejected TSV and Markdown lifecycle mutations are restored to their exact pre-transaction values.

### INV-MNT6-03 — Event Mutations Are Atomic

**PASS**

Events appended by rejected local transactions do not remain in the live event ledger after successful rollback.

### INV-MNT6-04 — Created Artifacts Are Removed

**PASS**

Files created solely by a rejected transaction within transaction-owned governance surfaces are removed.

### INV-MNT6-05 — Pre-existing Dirty Work Is Preserved

**PASS**

Files existing before the transaction are restored from transaction before-images rather than through Git reset or destructive repository-wide rollback.

### INV-MNT6-06 — Rollback Failure Fails Closed

**PASS**

Invalid or unavailable before-images prevent rollback completion, retain recovery state, and require explicit recovery.

### INV-MNT6-07 — Successful Transactions Clean Up Recovery State

**PASS**

A successful transaction removes its active receipt and transaction before-images only after canonical post-validation succeeds.

### INV-MNT6-08 — Post-Rollback State Is Canonically Consistent

**PASS**

Both isolated failure scenarios ended with:

```text
RESULT: CONSISTENT
```

## Scope Boundary

The implementation provides **local EOS transaction atomicity**.

It does not establish distributed atomic commit semantics for external side effects including:

* GitHub mutations;
* remote publication;
* release distribution;
* external APIs;
* irreversible third-party operations.

Those effects require separate idempotency, compensation, prepare/commit, or reconciliation semantics where applicable.

This limitation is not a failure of MNT-0006 because MNT-0006 addresses rejected mutation of the local canonical EOS transaction and its governed repository projections.

## Relationship to MNT-0003

MNT-0006 and MNT-0003 remain distinct:

* MNT-0006 governs atomic rollback of the **current local transaction**.
* MNT-0003 governs preservation and merge-safety of **divergent committed event histories**.

This verification does not close or supersede MNT-0003.

## Findings

### Finding MNT6-V01

The initial implementation omitted a module-scope `shutil` import.

Disposition:

**RESOLVED**

Corrected by commit:

`3a1f67b825a4c7b1184a6e5a7fbd791488501ef2`

### Finding MNT6-V02

The initial wrapper rollback-failure test used brittle self-modification and did not reliably force canonical rollback failure.

Disposition:

**RESOLVED**

The test now uses explicit deterministic rollback-failure injection.

### Finding MNT6-V03

Distributed/external side-effect atomicity remains outside the implemented transaction boundary.

Disposition:

**NON-BLOCKING SCOPE BOUNDARY**

Any future external-effect transaction semantics should be handled by the relevant integration, execution, synchronization, or publication design rather than broadening MNT-0006 retroactively.

## Verification Disposition

**PASS — RECOMMEND MNT-0006 CLOSURE**

The implementation satisfies the authorized MNT-0006 local canonical-transaction atomicity invariant.

The maintenance item may proceed through its remaining review/closure authority gate.

No runtime implementation authority beyond the scope already granted by DECISION-0006 is implied by this verification.

## Next Sequenced Work

After MNT-0006 is formally closed:

1. begin MNT-0005 implementation;
2. verify and close MNT-0005;
3. rebuild machine traceability;
4. execute the AIENG A–J conformance suite;
5. establish stable normative verification/evidence;
6. proceed to EOSP runtime implementation planning.
