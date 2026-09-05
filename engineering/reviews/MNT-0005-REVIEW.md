---
artifact_id: "REV-MNT-0005"
title: "MNT-0005 Engineering Review"
type: "review"
version: "0.1.0"
status: "In Review"
authority: "review-authoritative"
created: "2026-09-05"
updated: "2026-09-05"
---

# MNT-0005 — Engineering Review

**Decision:** PENDING

## Target

- Maintenance item: `engineering/maintenance/MNT-0005.md`
- Verification review: `engineering/reviews/MNT-0005-IDENTITY-RESOLUTION-VERIFICATION.md`
- Current lifecycle state: `VERIFYING`

## Review Basis

This review evaluates whether MNT-0005 may be formally closed after implementation and verification of canonical repository-native Requirement and Specification identity semantics.

Implementation checkpoints:

- `a530c135c066c15ed08ef13d25d01d2cd7661e0e` — recognize native requirement/specification identifiers
- `c513606cff15ec8ec4605b1ecfab7b0345d7c699` — tighten native identifier semantics

Verification checkpoint:

- `589d67478d1002c76116885ce203a099205ac41c` — verify native identity resolution

Implementation authority:

- `engineering/reviews/DECISION-0006-2026-09-05-eos-hardening-maintenance-implementation-approval.md`

## Deterministic Verification

**Result:** PASS

Verified surfaces include:

- canonical Requirement identifier-family recognition;
- canonical Specification identifier-family recognition;
- canonical identifier grammar;
- Requirement and Specification JSON Schema validation;
- EOS domain-model family semantics;
- core EOS identifier extraction;
- EOSE governed-context identifier extraction;
- EOSV identifier and evidence-reference recognition;
- semantic trace edge inference;
- trace coverage classification;
- impact traversal;
- generated trace determinism;
- malformed native-ID rejection;
- verification-scenario/specification disambiguation;
- stable identity preservation;
- duplicate-definition checks;
- canonical EOS state consistency.

## Scope Conformance

**PASS**

The implementation remains bounded to the MNT-0005 Requirement/Specification identity mismatch.

The repair:

- recognizes existing governed native IDs as first-class canonical identities;
- preserves `REQ-*` and `SPEC-*` compatibility;
- adds `FR-*` and `QR-*` as Requirement families;
- adds `FUN-*`, `IFC-*`, `SEC-*`, `TECH-*`, `DATA-*`, and `MKE-*` as Specification families;
- centralizes Requirement/Specification classification semantics;
- updates dependent trace, EOSE, and EOSV behavior where demonstrated necessary.

The implementation does not:

- renumber existing requirements;
- renumber existing specifications;
- create parallel `REQ-*` or `SPEC-*` aliases;
- create an independent alias registry;
- create a second identity authority;
- weaken duplicate-ID detection;
- manually manufacture trace edges;
- broaden MNT-0005 into unrelated EOS redesign.

## Requirements / Governing Conformance

**PASS**

The implementation conforms to the governing MNT-0005 principle:

> Established repository-native Requirement and Specification identifiers are first-class canonical identifiers of their existing entity type, not aliases for newly invented identities.

The repaired canonical model is:

```text
Requirement
├── REQ-*
├── FR-*
└── QR-*

Specification
├── SPEC-*
├── FUN-*
├── IFC-*
├── SEC-*
├── TECH-*
├── DATA-*
└── MKE-*
This preserves the stable-identity semantics governed by ADR-0003.

Implementation authority derives from DECISION-0006.

No additional runtime or lifecycle authority is inferred.

Architecture Conformance
PASS

The repair preserves the distinction between:

￼
entity type
and:

￼
identifier family
Requirement and Specification remain canonical EOS entity types.

Their established native prefixes express stable identifier families rather than creating new entity types or alternate canonical namespaces.

The repair also preserves:

.eos/state/current.json as canonical operational state;

generated trace state as a projection;

human-authored governed identifiers as stable source identity;

provider- and harness-neutral EOS semantics;

existing EOS lifecycle and authority boundaries.

Stable Identity Findings
PASS

Existing governed identifiers remain unchanged.

Examples remain:

￼
FR-043
QR-010
FUN-AIENG-0001
IFC-AIENG-0001
SEC-AIENG-0001
TECH-HARNESS-0001
DATA-SOURCE-0001
MKE-CORE-0001
No parallel canonical identity was created for any of these artifacts.

Identifier Grammar Findings
PASS

The final grammar distinguishes canonical artifact IDs from nearby noncanonical identifiers.

For example:

￼
FUN-AIENG-0001
is a canonical Specification identity, while:

￼
FUN-AIENG-V01
is not misclassified as a Specification identity.

Likewise, filename separators following a canonical identifier are not incorporated into the identifier itself.

Traceability Findings
PASS

The generated trace now recognizes repository-native Requirement and Specification identifiers.

The original finding:

AIENG-TRC-001 — Requirement/specification identifier namespace mismatch

is resolved.

Machine traceability now exposes the governed relationships:

￼
FUN-AIENG-0001 --satisfies--> FR-043
IFC-AIENG-0001 --satisfies--> FR-043
SEC-AIENG-0001 --satisfies--> FR-043
according to the source relationships in the approved AIENG specifications.

Trace Determinism
PASS

Repeated trace generation over unchanged governed source produces identical generated trace bytes.

.eos/trace-edges.tsv remains generated state.

No hand-authored trace repair was used.

EOSE / EOSV Findings
PASS

EOSE and EOSV recognize the accepted native Requirement and Specification families where their existing semantics require those identifiers.

Their unrelated identifier vocabularies were not broadened merely as a side effect of the repair.

Acceptance / Completion Evidence
Verified:

accepted identifier-family semantics are implemented;

existing governed IDs remain unchanged;

Requirement schema accepts established Requirement families;

Specification schema accepts established Specification families;

EOS extraction recognizes accepted native families;

trace inference uses semantic Requirement/Specification classification;

trace coverage includes native Requirement and Specification families;

impact traversal recognizes native families;

deterministic regression coverage exists;

generated trace projection rebuilds deterministically;

AIENG-TRC-001 is resolved;

canonical EOS state remains consistent;

dedicated verification review reports PASS.

Remaining authority conditions:

completion checklist and closure evidence must be finalized as part of accepted closure;

ordinary MNT_CLOSE gate conditions must pass;

final maintenance closure must be explicitly accepted by the Human Project Steward.

Test / Validation Evidence
Automated verification:

￼
Identifier-family regression suite: PASS
Canonical state tests: PASS
Canonical reconciliation tests: PASS
EOS wrapper dispatch: PASS
Canonical REQ/SPEC identity model: PASS
Cross-subsystem native identity recognition: PASS
Stable / duplicate identity check: PASS
Trace native-ID hygiene: PASS
Trace determinism: PASS
AIENG-TRC-001 resolution: PASS
EOS canonical state: CONSISTENT
Dedicated verification artifact:

engineering/reviews/MNT-0005-IDENTITY-RESOLUTION-VERIFICATION.md

Disposition:

PASS — RECOMMEND MNT-0005 CLOSURE

Security / Reliability Findings
No blocking security or reliability finding remains within MNT-0005 scope.

The repair is fail-closed with respect to the defined canonical identifier grammar: unrelated or malformed identifiers are not accepted merely because they resemble an established Requirement or Specification family.

Blocking Findings
None.

Non-Blocking Findings
Future introduction of a new Requirement or Specification family requires deliberate governed evolution of the domain model and schemas.

MNT-0003 remains independently open and continues to govern divergent committed event-ledger merge safety.

Resolution of MNT-0005 resolves the AIENG normative traceability namespace finding but does not itself authorize AIENG runtime implementation.

Recommendation
RECOMMEND ACCEPTED / CLOSED

The implementation and verification evidence support closure of MNT-0005.

Decision
PENDING HUMAN PROJECT STEWARD DECISION

Permitted final disposition:

ACCEPTED — authorize formal MNT-0005 closure;

REJECTED — return MNT-0005 to implementation;

BLOCKED — retain VERIFYING pending additional evidence.

No closure authority is inferred from implementation approval, successful verification, or this recommendation.

An explicit Human Project Steward closure decision is required.
