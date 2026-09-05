# EOS-AI-0001 — AI-Driven Engineering Operating Model Review

**Review date:** 2026-09-05
**Subject:** `engineering/lifecycle/EOS-AI-0001-ai-driven-engineering-operating-model.md`
**Governing ADR:** ADR-0008 — AI-Driven Engineering as the Default EOS Operating Model
**Change authority:** CR-0003 — Establish Monad AI-Driven Engineering Operating Model
**Disposition:** **PASS — ACCEPTED**

## Purpose

Review `EOS-AI-0001` for consistency with accepted ADR-0008, ADR-0006, existing EOS lifecycle semantics, canonical-state authority, evidence-based acceptance, human sovereignty, and the scope authorized by CR-0003.

This review determines whether `EOS-AI-0001` is suitable to become the governance-authoritative cross-layer operating contract for AI-driven engineering before requirements and detailed AIENG specifications are derived from it.

## Review findings

### 1. EOS lifecycle sovereignty

**PASS**

`EOS-AI-0001` explicitly preserves the existing eight permanent EOS layers:

* EOSB — Bootstrap;
* EOSP — Planning;
* EOSE — Execution;
* EOSV — Verification;
* EOSR — Review;
* EOSC — Change Control;
* EOSL — Release Lifecycle;
* EOSM — Maintenance.

The document defines AI participation across those layers rather than introducing an additional lifecycle or competing state machine.

This satisfies the controlling constraint established by ADR-0006 and ADR-0008.

### 2. Canonical-state sovereignty

**PASS**

`EOS-AI-0001` explicitly preserves `.eos/state/current.json` as the sole current EOS operational authority.

Compiled context, conversation state, execution checkpoints, embeddings, caches, model memory, temporary plans, and other AI working state are correctly classified as derived or transient state rather than competing canonical engineering authority.

### 3. AI initiative versus authority

**PASS**

The document distinguishes:

* inspect;
* reason;
* recommend;
* propose;
* execute;
* verify;
* review;
* approve;
* accept.

It explicitly prevents AI initiative, analytical capability, model confidence, provider identity, or repeated agreement from creating binding authority.

This correctly operationalizes the ADR-0008 rule:

> AI initiative != AI authority.

### 4. Human sovereignty

**PASS**

Human sovereignty is defined through accountable authority, delegation, accepted risk, irreversible commitment, mission, and escalation rather than mandatory human execution of routine work.

The contract allows bounded delegation while preserving the rule that delegated AI authority cannot exceed the delegator's authority.

This supports increasing automation without collapsing accountability.

### 5. Adaptive engineering pathway

**PASS**

The document permits engineering pathway rigor to vary according to risk, consequence, complexity, uncertainty, reversibility, lifecycle state, dependencies, evidence, security sensitivity, and delegated autonomy.

It also explicitly prohibits adaptive pathways from bypassing:

* mandatory EOS gates;
* required authority;
* required policy;
* required verification;
* required review independence;
* unresolved blocking decisions;
* change-control obligations.

Adaptive planning therefore changes pathway depth, not lifecycle authority.

### 6. Ambiguity handling

**PASS**

Material ambiguity affecting product behavior, requirements, architecture, security, privacy, operations, legal posture, accepted risk, irreversible action, authority, or acceptance criteria must be surfaced.

Ordinary implementation discretion remains delegable.

Consequential ambiguity routes to native Monad decision, approval, ADR, Change Request, or escalation semantics.

This prevents AI-generated assumptions from silently becoming governed engineering meaning.

### 7. Execution boundary

**PASS**

EOSE remains authoritative for execution.

Executor completion is explicitly treated as a claim rather than accepted completion.

Unexpected work is classified into:

* authorized implementation discretion;
* decision-required work;
* EOSC-governed change;
* EOSP-governed new work;
* security or operational escalation.

This preserves authorized Work Packet scope and prevents execution convenience from redefining governing intent.

### 8. Verification and evidence

**PASS**

EOSV remains authoritative for verification evidence.

The operating model explicitly prohibits AI from:

* fabricating evidence;
* rewriting failed evidence into passing evidence;
* overriding deterministic validator output;
* treating self-report as independent verification;
* treating stale evidence as current.

Acceptance remains evidence-driven rather than executor-driven.

### 9. Review independence

**PASS**

EOSR remains authoritative for review.

The contract correctly avoids defining a second model invocation as automatically independent.

It identifies executor identity, model, provider, harness, context isolation, prompt isolation, organizational role, and human participation as possible independence dimensions while delegating exact predicates to later policy/specification work.

### 10. Governing-input drift

**PASS**

The model requires material governing-input drift to invalidate, suspend, or trigger reevaluation of stale execution authority.

Requirements, specifications, ADRs, decisions, approvals, policies, Work Packet scope, dependencies, security constraints, and acceptance criteria are correctly treated as possible governing inputs.

This establishes the required basis for later execution-contract fingerprinting.

### 11. Provider and harness neutrality

**PASS**

AI providers, models, harnesses, scripts, humans, and future executors remain replaceable execution participants rather than sources of semantic authority.

Provider failure is treated as an execution failure rather than canonical-state failure.

ADR-0007 is referenced conditionally and remains independently governed.

`EOS-AI-0001` does not implicitly accept ADR-0007.

### 12. Transcript and reasoning boundary

**PASS**

Private model chain-of-thought is not required as governance evidence.

Raw AI transcripts are noncanonical by default.

Auditability instead depends on material structured records including intent, material questions, decisions, approvals, authorization, executor identity, observable effects, evidence, verification, review, change, and acceptance.

This produces reconstructability without making provider-specific cognition part of Monad's normative model.

### 13. Native semantic reuse

**PASS**

The operating model explicitly reuses native Monad concepts including:

* PI;
* WC;
* WP;
* CR;
* DEC;
* APR;
* DEP;
* REV;
* EVID;
* TRC;
* MNT.

It prohibits creating parallel AI-specific plan, task, decision, approval, evidence, workflow, context, or state stores merely because AI participates.

This satisfies the one-model/one-control-plane constraint.

### 14. Progressive autonomy

**PASS**

The three participation profiles are correctly represented as modes within one operating model:

1. AI-assisted;
2. AI-driven;
3. bounded AI-autonomous.

Higher autonomy remains explicit, bounded, evidence-backed, observable, consequence-aware, policy-controlled, and revocable.

Trust is scoped to relevant classes of work rather than generalized automatically.

### 15. Conformance scenarios

**PASS**

All ten conformance scenarios required by CR-0003 and ADR-0008 are represented:

* low-risk reversible change;
* ambiguous product intent;
* architecture change discovered during execution;
* bounded autonomous Work Packet;
* security-sensitive work;
* independent review;
* governing-input drift;
* provider failure;
* human denial;
* evidence invalidating a planning assumption.

Detailed behavioral ownership is correctly deferred to the AIENG specification tranche.

### 16. Implementation authorization boundary

**PASS**

`EOS-AI-0001` explicitly states that normative definition does not authorize machine implementation.

Possible machine implications are listed as future implementation surfaces only.

Active MVP Work Packets retain their current scope.

Implementation still requires EOSP planning and separately authorized Work Cycles and Work Packets.

## Identified follow-on work

The review confirms the next normative tranche should include:

1. product requirement refinements;
2. FR-037 — Adaptive AI-Driven Engineering Workflow Planning;
3. specification-baseline amendment;
4. FUN-AIENG-0001 — Adaptive Engineering Workflow;
5. IFC-AIENG-0001 — Engineering Agent Contract;
6. SEC-AIENG-0001 — Autonomy, Authority, and Approval Gates;
7. targeted EOS/governance contract amendments;
8. explicit traceability;
9. executable conformance scenarios;
10. EOSP implementation planning only after the normative baseline stabilizes.

These are follow-on obligations, not blockers to accepting `EOS-AI-0001`.

## Blocking findings

None.

## Review conclusion

`EOS-AI-0001` is consistent with ADR-0008, preserves ADR-0006, preserves EOS as the sole engineering lifecycle/control plane, preserves one canonical operational state, distinguishes AI initiative from authority, maintains evidence-based acceptance, supports bounded progressive autonomy, and provides a coherent cross-layer contract for AI-driven engineering.

No material architectural contradiction or authority bypass was identified.

## Recommendation

**ACCEPT `EOS-AI-0001` as the governance-authoritative AI-Driven Engineering Operating Model baseline.**

Acceptance should not authorize product-runtime implementation and should not alter the independent Proposed status of ADR-0007.

## Decision

**ACCEPTED — Human Project Steward / Architecture Owner, 2026-09-05.**

Acceptance evidence: `engineering/reviews/DECISION-0004-2026-09-05-eos-ai-0001-acceptance.md`
