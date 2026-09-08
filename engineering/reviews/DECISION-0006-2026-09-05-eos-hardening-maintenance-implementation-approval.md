# DECISION-0006-2026-09-05 — EOS Hardening Maintenance Implementation Approval

**Record type:** Governance authority decision
**Date:** 2026-09-05
**Subject:** MNT-0005 and MNT-0006 implementation authorization
**Authority:** Human Project Steward / Architecture Owner
**Disposition:** **APPROVED**
**Related:** CR-0003, ADR-0003, ADR-0006, ADR-0008, EOS-AI-0001, MNT-0003, MNT-0005, MNT-0006, AIENG-TRC-001

## Decision

Implementation of the following planned EOS maintenance work is **Approved**:

1. `MNT-0005 — EOS canonical REQ/SPEC identity model excludes repository-native requirement and specification identifiers`;
2. `MNT-0006 — EOS canonical transaction failure leaves rejected projection and event mutations`.

The explicit human authority statement was:

> I approve the MNT-0005 identity-resolution plan and the MNT-0006 canonical-transaction atomicity plan for implementation.

## MNT-0005 Approved Resolution Principle

The implementation SHALL preserve established repository-native requirement and
specification identifiers as their canonical governed identities.

The repair SHALL NOT create parallel `REQ-*` or `SPEC-*` shadow identities for
artifacts that already possess stable governed identifiers.

Requirement entity identity shall support the established requirement families,
including:

```text
REQ-*
FR-*
QR-*
```

Specification entity identity shall support established specification families,
including the currently identified:

```text
SPEC-*
FUN-*
IFC-*
SEC-*
TECH-*
DATA-*
MKE-*
```

Implementation MUST deterministically inspect the existing repository before
freezing the complete accepted family set.

The entity type and identifier family SHALL remain distinct concepts.

Existing artifact IDs and history MUST remain unchanged.

## MNT-0006 Approved Resolution Principle

Rejected canonical EOS transactions SHALL become transactionally atomic.

The required external semantic contract is:

```text
successful transaction
    -> COMMITTED

rejected transaction
    -> ROLLED_BACK
```

The system SHALL NOT retain a third externally observable state equivalent to:

```text
canonical rejected
+
transaction-owned projections/events remain mutated
```

Rollback MUST be:

* transaction-scoped;
* deterministic;
* exact for transaction-owned mutations;
* safe in a dirty working tree;
* incapable of deleting unrelated user work;
* fail-closed if rollback itself cannot complete.

The implementation SHOULD prefer staged mutation followed by atomic publication
where practical.

An interim exact transaction-scoped rollback mechanism is acceptable if it
satisfies all MNT-0006 completion criteria and does not establish conflicting
architecture.

## Execution Order

The approved execution order is:

```text
MNT-0006
transaction atomicity
        ↓
verification
        ↓
review / closure
        ↓
MNT-0005
identity and traceability
        ↓
verification
        ↓
review / closure
```

The rationale is that MNT-0005 changes EOS schemas and trace semantics.

Repairing failed-transaction behavior first reduces governance risk while
performing those later machine-model changes.

MNT-0005 is authorized now but SHOULD remain `PLANNED` until MNT-0006 reaches
an accepted terminal disposition unless a new governed decision explicitly
changes the sequence.

## Scope Authority

### MNT-0006

Implementation authority includes only changes necessary to satisfy the
approved MNT-0006 transaction-atomicity contract.

Likely affected areas include:

```text
scripts/eos
tools/eos/canonical_state.py
tools/eos/eos.py
tools/eos/execution_v2.py
tools/eos/verification_v2.py
```

Only files demonstrated to participate in the defect should be changed.

Tests and narrowly necessary fixtures are included.

### MNT-0005

After MNT-0006 closure, implementation authority includes only changes required
to reconcile canonical Requirement/Specification identity and trace behavior.

Likely affected areas include:

```text
.eos/domain-model.json
.eos/schemas/core/requirement.schema.json
.eos/schemas/core/specification.schema.json
tools/eos/eos.py
```

and any additional files demonstrated by repository inspection to contain the
same hard-coded identity assumption.

## Non-Effect

This approval does **not**:

* authorize general AIENG runtime implementation;
* authorize an AIENG implementation Work Cycle;
* authorize an AIENG implementation Work Packet;
* accept ADR-0007;
* close CR-0003;
* close MNT-0003;
* permit unrelated EOS refactoring;
* authorize silent requirement/specification renumbering;
* create a second canonical state authority;
* create a parallel event or trace system;
* waive verification or review;
* permit MNT-0005 to broaden beyond the approved identity/traceability defect;
* permit MNT-0006 to replace unrelated EOS architecture.

## Verification Requirement

Each maintenance item requires its own:

1. bounded implementation;
2. deterministic tests;
3. EOS consistency check;
4. verification evidence;
5. engineering review;
6. accepted closure.

Approval of implementation is not approval of completion.

## Decision Status

**APPROVED — effective 2026-09-05.**
