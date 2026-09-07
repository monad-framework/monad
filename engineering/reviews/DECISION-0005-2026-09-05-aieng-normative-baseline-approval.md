# DECISION-0005-2026-09-05 — AIENG Normative Specification Baseline Approval

**Record type:** Governance authority decision
**Date:** 2026-09-05
**Subject:** AI-Driven Engineering Normative Specification Baseline
**Authority:** Human Project Steward / Architecture Owner
**Disposition:** **APPROVED**
**Related:** CR-0003, ADR-0006, ADR-0008, EOS-AI-0001, SPEC-BASE-0001, FUN-AIENG-0001, IFC-AIENG-0001, SEC-AIENG-0001, AIENG-TRC-001

## Decision

The AI-Driven Engineering normative specification baseline is **Approved**.

The explicit human authority statement was:

> I approve the AIENG normative specification baseline.

The approved baseline consists of:

* `SPEC-BASE-0001 — Specification Baseline`;
* `FUN-AIENG-0001 — Adaptive Engineering Workflow`;
* `IFC-AIENG-0001 — Engineering Agent Contract`;
* `SEC-AIENG-0001 — Autonomy, Authority, and Approval Gates`.

## Effect

This decision establishes the initial AIENG specifications as the approved normative contracts derived from:

* accepted `ADR-0008`;
* accepted `EOS-AI-0001`;
* the AI-driven engineering requirement refinements in `product/product-requirements.md`;
* the change authority granted by `CR-0003`.

The approved baseline establishes the following division of responsibility.

### FUN-AIENG-0001

Normatively owns:

* adaptive engineering pathway derivation;
* rigor adaptation;
* material ambiguity handling;
* clarification;
* decision routing;
* dependency-aware progression;
* replanning;
* evidence feedback;
* governing-input drift behavior.

### IFC-AIENG-0001

Normatively owns:

* provider-neutral engineering-participant interaction;
* governed context exchange;
* pathway proposals;
* clarification and decision proposals;
* candidate artifact proposals;
* lifecycle requests;
* execution requests;
* evidence interpretation;
* review participation;
* replanning interaction.

### SEC-AIENG-0001

Normatively owns:

* capability versus authority;
* autonomy profiles;
* delegation;
* approval;
* least privilege;
* revocation;
* fail-closed authorization;
* prompt and instruction trust boundaries;
* sensitive effects;
* separation of duties;
* independent review;
* progressive trust.

## Conformance effect

The baseline provides normative ownership for all ten required AIENG conformance scenarios:

1. low-risk reversible change;
2. ambiguous product intent;
3. architecture change discovered during execution;
4. bounded autonomous Work Packet;
5. security-sensitive work;
6. independent review;
7. governing-input drift;
8. provider failure;
9. human denial;
10. evidence invalidating a planning assumption.

This approval establishes normative ownership only.

Executable conformance assets and resulting verification evidence remain future governed work.

## Existing execution-governance relationship

This approval does not replace or duplicate the existing governed-execution requirement tranche.

The relationship remains:

```text
AI-driven engineering intent
        ↓
FUN-AIENG-0001
adaptive pathway
        ↓
IFC-AIENG-0001
participant interaction
        ↓
SEC-AIENG-0001
authority / autonomy / approval constraints
        ↓
EOS readiness and authorization
        ↓
FR-037 .. FR-042
governed execution semantics
        ↓
verification / review / change control
```

## AIENG-TRC-001

Approval explicitly preserves the open traceability finding:

**AIENG-TRC-001 — Requirement/specification identifier namespace mismatch**

The human-authored corpus uses:

```text
FR-*
QR-*

FUN-*
IFC-*
SEC-*
TECH-*
```

while the EOS canonical domain model currently defines canonical Requirement and Specification entity identities as:

```text
REQ-*
SPEC-*
```

The baseline approval does not choose a resolution and does not waive the mismatch.

The eventual resolution MUST:

* preserve established artifact identity and history;
* avoid silent renumbering;
* preserve deterministic traceability;
* preserve existing semantic classifications;
* establish an explicit relationship between human-authored identifiers and canonical EOS requirement/specification entities.

`AIENG-TRC-001` MUST be resolved or formally dispositioned before AIENG runtime implementation planning is authorized.

## Non-effect

This approval does **not**:

* authorize runtime implementation;
* authorize an implementation Work Cycle;
* authorize an implementation Work Packet;
* broaden an existing MVP Work Packet;
* accept ADR-0007;
* create a ninth EOS lifecycle layer;
* create a second canonical state authority;
* create AI-specific lifecycle, decision, approval, evidence, or authority systems;
* waive `AIENG-TRC-001`;
* resolve MNT-0003;
* close CR-0003;
* establish complete machine-level REQ-to-SPEC traceability;
* make draft executable conformance tests authoritative evidence.

## Remaining pre-implementation obligations

Before AIENG runtime implementation planning may be authorized, the program must:

1. resolve or formally disposition `AIENG-TRC-001`;
2. establish the required executable conformance assets;
3. rebuild and inspect EOS traceability from canonical sources;
4. run the stable normative checkpoint verification;
5. resolve or refresh stale verification evidence as required;
6. perform a normative-baseline closure review;
7. enter EOSP implementation planning only after those gates are satisfied.

## Evidence

* `architecture/decisions/ADR-0008-ai-driven-engineering-as-default-eos-operating-model.md`
* `engineering/lifecycle/EOS-AI-0001-ai-driven-engineering-operating-model.md`
* `product/product-requirements.md`
* `specifications/baseline.md`
* `specifications/functional/FUN-AIENG-0001-adaptive-engineering-workflow.md`
* `specifications/interfaces/IFC-AIENG-0001-engineering-agent-contract.md`
* `specifications/security/SEC-AIENG-0001-autonomy-authority-and-approval-gates.md`
* `engineering/reviews/AIENG-NORMATIVE-TRACEABILITY-AND-CONFORMANCE-REVIEW.md`
* explicit human approval in the governing interaction on 2026-09-05.

## Decision status

**APPROVED — effective 2026-09-05.**
