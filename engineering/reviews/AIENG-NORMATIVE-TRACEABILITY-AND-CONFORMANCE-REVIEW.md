# AIENG Normative Traceability and Conformance Review

**Review date:** 2026-09-05
**Change authority:** CR-0003
**Architecture authority:** ADR-0008 — Accepted
**Operating-model authority:** EOS-AI-0001 — Accepted
**Specifications reviewed:** FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001
**Disposition:** **PASS — APPROVED WITH TRACEABILITY FOLLOW-UP**

## Purpose

Determine whether the AI-driven engineering normative tranche is internally
consistent, traceable from accepted architecture through product requirements
into specifications, covers all required AIENG conformance scenarios, preserves
EOS sovereignty, and is ready for human approval.

This review does not authorize implementation.

## Governing chain

The normative derivation chain is:

```text
CR-0003
approved change authority
    ↓
ADR-0008
accepted architecture
    ↓
EOS-AI-0001
accepted cross-layer operating model
    ↓
product/product-requirements.md
    ↓
FUN-AIENG-0001
IFC-AIENG-0001
SEC-AIENG-0001
    ↓
AIENG conformance scenarios
    ↓
future verification assets
    ↓
EOSP implementation planning
    ↓
separately authorized WC/WP
```

## Architectural consistency

### EOS sovereignty

**PASS**

The tranche preserves the permanent eight-layer EOS:

* EOSB;
* EOSP;
* EOSE;
* EOSV;
* EOSR;
* EOSC;
* EOSL;
* EOSM.

No ninth AI lifecycle has been created.

### Canonical-state sovereignty

**PASS**

No AIENG specification establishes an alternative canonical operational state.

AI contexts, sessions, pathways, model memory, transcripts, checkpoints, and
provider-local state remain projections or transient state.

### Authority sovereignty

**PASS**

The specifications preserve the distinction among:

```text
inspect
analyze
recommend
propose
decide
approve
authorize
execute
verify
review
accept
```

AI initiative and analytical capability do not themselves create binding
authority.

### Native semantic reuse

**PASS**

The tranche reuses existing EOS planning, decision, approval, execution,
verification, review, change-control, evidence, maintenance, and release
semantics.

No parallel AI-specific lifecycle, decision, approval, evidence, or authority
store is introduced.

## Requirement-to-specification traceability

| Requirement | Primary AIENG ownership                                               |
| ----------- | --------------------------------------------------------------------- |
| FR-007      | FUN-AIENG-0001, IFC-AIENG-0001                                        |
| FR-012      | FUN-AIENG-0001, IFC-AIENG-0001                                        |
| FR-013      | FUN-AIENG-0001, IFC-AIENG-0001                                        |
| FR-014      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| FR-015      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| FR-016      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| FR-017      | IFC-AIENG-0001                                                        |
| FR-022      | SEC-AIENG-0001                                                        |
| FR-023      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| FR-024      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| FR-037      | SEC-AIENG-0001 plus existing execution specifications                 |
| FR-038      | SEC-AIENG-0001 plus existing execution specifications                 |
| FR-039      | existing execution/interface specifications                           |
| FR-040      | IFC-AIENG-0001, SEC-AIENG-0001 plus existing execution specifications |
| FR-041      | IFC-AIENG-0001, SEC-AIENG-0001 plus existing execution specifications |
| FR-042      | existing harness/model conformance specifications                     |
| FR-043      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| QR-003      | SEC-AIENG-0001                                                        |
| QR-008      | FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001                        |
| QR-010      | all three AIENG specifications                                        |
| QR-011      | SEC-AIENG-0001                                                        |

The existing FR-037 through FR-042 Governed Execution Harness tranche is
complementary rather than duplicated.

FR-043 owns adaptive AI-driven engineering workflow planning and hands
authorized execution into the existing governed execution boundary.

## Specification responsibility boundaries

### FUN-AIENG-0001

Owns:

* adaptive engineering pathway derivation;
* rigor adaptation;
* material ambiguity detection;
* clarification;
* decision routing;
* dependency-aware progression;
* replanning;
* evidence feedback;
* governing-input drift behavior.

### IFC-AIENG-0001

Owns:

* provider-neutral engineering participant interaction;
* context exchange;
* pathway proposals;
* clarification requests;
* decision proposals;
* candidate artifact proposals;
* lifecycle proposals;
* execution requests;
* evidence interpretation;
* review participation;
* replanning messages.

It does not redefine execution-harness mediation.

### SEC-AIENG-0001

Owns:

* capability versus authority;
* autonomy profiles;
* delegation;
* approval;
* revocation;
* fail-closed authorization;
* least privilege;
* prompt/instruction trust boundaries;
* sensitive effects;
* separation of duties;
* independent review;
* progressive trust.

## Conformance coverage

### AIENG-CONF-A — Low-risk reversible change

**Owned by:**

* FUN-AIENG-V01.

**Coverage:** complete.

### AIENG-CONF-B — Ambiguous product intent

**Owned by:**

* FUN-AIENG-V02;
* AIENG-IFC-V02.

**Coverage:** complete.

### AIENG-CONF-C — Architecture change discovered during execution

**Owned by:**

* FUN-AIENG-V03.

**Coverage:** complete.

### AIENG-CONF-D — Bounded autonomous Work Packet

**Owned by:**

* FUN-AIENG-V04;
* AIENG-IFC-V10;
* AIENG-SEC-V01;
* AIENG-SEC-V02.

**Coverage:** complete.

### AIENG-CONF-E — Security-sensitive work

**Owned by:**

* FUN-AIENG-V05;
* AIENG-SEC-V06.

**Coverage:** complete.

### AIENG-CONF-F — Independent review

**Owned by:**

* AIENG-IFC-V09;
* AIENG-SEC-V07.

**Coverage:** complete.

### AIENG-CONF-G — Governing-input drift

**Owned by:**

* FUN-AIENG-V06;
* AIENG-IFC-V05;
* AIENG-SEC-V04.

**Coverage:** complete.

### AIENG-CONF-H — Provider failure

**Owned by:**

* FUN-AIENG-V07;
* AIENG-IFC-V07;
* AIENG-SEC-V11.

**Coverage:** complete.

### AIENG-CONF-I — Human denial

**Owned by:**

* FUN-AIENG-V08;
* AIENG-IFC-V06;
* AIENG-SEC-V08.

**Coverage:** complete.

### AIENG-CONF-J — Evidence invalidates assumption

**Owned by:**

* FUN-AIENG-V09;
* AIENG-IFC-V08.

**Coverage:** complete.

## Cross-cutting invariants

### Initiative without authority

**PASS**

AI may proactively reason, plan, clarify, recommend, draft, and request
progression without acquiring approval authority.

### Adaptive workflow without gate bypass

**PASS**

Optional engineering rigor may adapt while mandatory EOS gates remain binding.

### Bounded autonomy

**PASS**

AI-assisted, AI-driven, and bounded AI-autonomous operation remain profiles of
one governed model.

### Governing drift

**PASS**

Material governing-input changes cause stale authority/pathway treatment rather
than silent continuation.

### Evidence-based closure

**PASS**

Executor completion remains a claim until required evidence, verification,
review, and acceptance obligations are satisfied.

### Review independence

**PASS**

Trivial self-review is explicitly insufficient where independent review is
required.

### Provider neutrality

**PASS**

Provider, model, and harness identity do not confer authority.

### Transcript non-authority

**PASS**

Raw transcript and private chain-of-thought retention are not required for
canonical auditability.

## Machine-traceability finding

### Finding AIENG-TRC-001 — Requirement/specification identifier namespace mismatch

**Status:** OPEN FOLLOW-UP

The human-authored product requirements use identifiers including:

```text
FR-*
QR-*
```

The human-authored specification convention uses class-specific identifiers
including:

```text
FUN-*
IFC-*
SEC-*
TECH-*
```

The EOS canonical domain model currently defines canonical Requirement and
Specification identities as:

```text
REQ-*
SPEC-*
```

This creates an identity-model mismatch between the current human-authored
product/specification corpus and the canonical EOS entity model.

This review does not determine that either convention should replace the other.

A governed reconciliation is required.

Acceptable future solutions may include, subject to architecture review:

* canonical REQ/SPEC entities that retain FR/QR/FUN/IFC/SEC identifiers as
  stable native aliases;
* extension of canonical namespace semantics to recognize the existing
  class-specific identifiers;
* an explicit mapping layer between human artifact identifiers and canonical
  REQ/SPEC entities;
* another solution preserving identity, history, and deterministic traceability.

The resolution MUST NOT silently renumber existing requirements or
specifications.

### Effect of AIENG-TRC-001

The finding does **not** invalidate the semantic AIENG requirements or
specifications.

It does prevent the program from claiming complete canonical machine-level
REQ-to-SPEC traceability until reconciled.

The finding MUST be resolved or formally dispositioned before AIENG runtime
implementation planning is authorized.

## Generated trace projection

`.eos/trace-edges.tsv` is a generated, rebuildable EOS projection.

It MUST NOT be manually edited to manufacture AIENG trace coverage.

At the stable normative checkpoint EOS should rebuild/inspect traceability from
canonical artifacts and report actual coverage.

Any missing edges after deterministic rebuild are evidence of a traceability
gap, not permission to hand-author generated state.

## Remaining normative gaps

No additional AIENG functional, interface, security, lifecycle, authority, or
policy specification is currently required.

The remaining pre-implementation concerns are:

1. resolve or formally disposition `AIENG-TRC-001`;
2. approve the AIENG specification baseline;
3. establish executable conformance assets from the verification clauses;
4. rebuild and inspect EOS traceability;
5. run the stable-checkpoint EOS verification;
6. refresh stale evidence once;
7. only then enter EOSP implementation planning.

## Review conclusion

The AI-driven engineering normative tranche is semantically coherent and
complete enough for governance approval.

All ten required AIENG conformance scenarios have normative specification
ownership.

No ninth lifecycle, parallel canonical state, AI-specific authority system, or
gate-bypass mechanism was identified.

The existing identifier namespace mismatch is a real machine-traceability
follow-up and must not be hidden.

## Recommendation

**APPROVE:**

* `SPEC-BASE-0001`;
* `FUN-AIENG-0001`;
* `IFC-AIENG-0001`;
* `SEC-AIENG-0001`;

as the normative AI-driven engineering specification baseline.

Approval does not authorize runtime implementation.

`AIENG-TRC-001` remains an explicit pre-implementation traceability follow-up.

## Decision

**APPROVED — Human Project Steward / Architecture Owner, 2026-09-05.**

Approval evidence: `engineering/reviews/DECISION-0005-2026-09-05-aieng-normative-baseline-approval.md`

`AIENG-TRC-001` remains OPEN FOLLOW-UP.
