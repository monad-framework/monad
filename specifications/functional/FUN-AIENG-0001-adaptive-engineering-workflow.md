# FUN-AIENG-0001: Adaptive Engineering Workflow

**Status:** approved
**Version:** 0.1.0
**Owner:** Monad Core / EOS
**Reviewers:** Product Owner, Architecture Owner, Engineering Owner, Security Owner, Operations Owner, Verification Owner as affected
**Related requirements:** FR-007, FR-012, FR-013, FR-014, FR-015, FR-016, FR-023, FR-024, FR-043, QR-008, QR-010
**Governing ADRs:** ADR-0006, ADR-0008
**Governing operating model:** EOS-AI-0001
**Change authority:** CR-0003
**Approval evidence:** `engineering/reviews/DECISION-0005-2026-09-05-aieng-normative-baseline-approval.md`

## Purpose and scope

This specification defines the functional behavior by which Monad derives, presents, revises, and governs an adaptive engineering pathway for AI-driven engineering work.

The adaptive workflow converts governed engineering intent and repository knowledge into an inspectable proposal for how work should progress through the existing Monad Engineering Operating System.

It defines:

* pathway derivation inputs;
* workflow initiative;
* activity selection;
* rigor adaptation;
* clarification behavior;
* consequential decision routing;
* dependency-aware sequencing;
* escalation;
* replanning;
* evidence feedback;
* governing-input drift behavior;
* interaction with EOS lifecycle layers;
* observable pathway rationale;
* conformance behavior.

This specification does not define:

* a new EOS lifecycle;
* a second canonical state machine;
* Execution Envelope serialization;
* tool mediation internals;
* provider-specific prompting;
* private model reasoning;
* model-selection algorithms;
* detailed capability semantics;
* detailed approval security rules.

Those concerns remain owned by existing EOS governance or subsequent AIENG/interface/security specifications.

## Definitions

### Engineering intent

A governed statement of desired engineering outcome, requirement, change, Work Packet objective, maintenance concern, operational need, or other authorized engineering purpose.

### Engineering pathway

An inspectable proposed sequence and set of engineering activities sufficient to move governed intent toward an EOS-governed outcome.

A pathway is a plan or projection. It is not canonical lifecycle state.

### Activity

A meaningful engineering action or gate such as:

* inspect;
* analyze;
* clarify;
* decide;
* design;
* specify;
* plan;
* authorize;
* execute;
* validate;
* verify;
* review;
* integrate;
* release;
* observe;
* maintain;
* replan.

### Mandatory activity

An activity required by EOS lifecycle state, authority, policy, accepted architecture, specification, security requirement, dependency condition, or other governing rule.

### Optional activity

An activity that may be omitted, reordered, combined, or deepened when doing so preserves all governing obligations.

### Material ambiguity

Uncertainty for which plausible interpretations may change consequential product meaning, architecture, security, privacy, legal/compliance posture, operations, accepted risk, irreversible effects, authority, scope, or acceptance obligations.

### Pathway rationale

Structured, inspectable information sufficient to explain why material engineering activities were selected, omitted, reordered, added, or deepened.

Pathway rationale is not private chain-of-thought.

### Governing-input set

The authoritative and materially relevant inputs on which a pathway depends, including applicable requirements, specifications, ADRs, decisions, approvals, policy, lifecycle state, Work Packet scope, dependencies, security constraints, evidence, and acceptance criteria.

### Governing drift

A material change in the governing-input set after a pathway or authorization was derived.

### Autonomy profile

The currently authorized participation mode governing how proactively AI may progress work:

* AI-assisted;
* AI-driven;
* bounded AI-autonomous.

## Architectural invariant

The adaptive workflow MUST preserve:

> **AI drives the work. EOS governs the work. Humans govern consequential meaning and authority. Evidence governs acceptance.**

The workflow engine MAY exercise initiative.

It MUST NOT manufacture authority.

## Preconditions

Pathway derivation requires:

1. a resolvable engineering subject or intent;
2. readable applicable repository/EOS state;
3. sufficient identity to attribute the pathway request or initiating actor;
4. sufficient governing context to identify known mandatory constraints;
5. explicit representation of unresolved material ambiguity where applicable.

Pathway derivation MAY occur before execution authorization.

Execution-ready progression MUST NOT occur merely because a pathway can be generated.

If required governing context cannot be resolved, the workflow MUST surface that condition rather than silently treating missing information as permission.

## Core invariants

### AIENG-FUN-I01 — EOS sovereignty

Adaptive workflow MUST operate inside EOS.

It MUST NOT create a ninth EOS lifecycle layer.

### AIENG-FUN-I02 — Pathway non-authority

A pathway is a proposal until applicable EOS authority, decision, readiness, and authorization semantics make its actions executable.

### AIENG-FUN-I03 — Initiative without approval authority

AI MAY proactively identify and recommend next useful engineering actions.

Proactivity MUST NOT itself grant approval or execution authority.

### AIENG-FUN-I04 — Mandatory-gate preservation

No pathway adaptation may omit or bypass a mandatory EOS gate.

### AIENG-FUN-I05 — Material ambiguity escalation

Material ambiguity MUST be surfaced through clarification or native decision semantics.

### AIENG-FUN-I06 — Explainable adaptation

Material changes to normal pathway rigor MUST have structured rationale.

### AIENG-FUN-I07 — Governing freshness

A pathway derived from materially stale governing inputs MUST NOT be represented as current.

### AIENG-FUN-I08 — Evidence classification

Evidence may change recommendations and planning assumptions while retaining its actual authority class.

### AIENG-FUN-I09 — Native semantic reuse

The workflow MUST reuse native EOS entities and relationships where their semantics are sufficient.

### AIENG-FUN-I10 — No transcript authority

Conversation history alone MUST NOT become a canonical decision, approval, or lifecycle transition when native governed persistence is required.

## Pathway derivation inputs

The workflow SHOULD evaluate all materially applicable inputs available to it, including:

### Intent and scope

* desired outcome;
* subject;
* Work Packet scope where applicable;
* explicit exclusions;
* acceptance criteria.

### Repository knowledge

* requirements;
* architecture;
* specifications;
* ADRs;
* decisions;
* approvals;
* authoritative explanatory context.

### Lifecycle state

* PI state;
* WC state;
* WP state;
* CR state;
* maintenance state;
* release state;
* relevant EOS gates.

### Authority and policy

* accountable owner;
* delegated authority;
* approval requirements;
* prohibited actions;
* autonomy profile;
* capability constraints.

### Dependency state

* prerequisites;
* blockers;
* sequencing constraints;
* conflicting work;
* parallelizable work.

### Risk and consequence

* security sensitivity;
* privacy sensitivity;
* operational consequence;
* reversibility;
* blast radius;
* novelty;
* uncertainty;
* migration impact;
* external commitment.

### Evidence

* current verification evidence;
* stale evidence;
* failed evidence;
* review findings;
* incidents;
* operational observations;
* maintenance findings;
* performance results.

Unresolved or contradictory inputs MUST remain visible when they are material to pathway behavior.

## Pathway output

A pathway representation MUST be able to communicate at least:

1. pathway subject;
2. governing-input identity or equivalent references;
3. proposed activities;
4. proposed sequencing/dependencies;
5. mandatory activities/gates;
6. optional activities;
7. material unresolved questions;
8. required decision points;
9. applicable authority/approval boundaries;
10. expected verification obligations;
11. expected review obligations;
12. escalation conditions;
13. material rationale for adapted rigor;
14. current autonomy profile;
15. freshness or drift state.

The representation MAY be transient until persistence is required.

A persisted pathway MUST NOT become a competing lifecycle authority.

## Adaptive rigor

The workflow MAY vary engineering rigor according to consequence and governing constraints.

### Lightweight pathway

Low-risk, reversible, well-understood work MAY omit unnecessary optional ceremony.

A lightweight pathway MUST still preserve:

* required scope;
* applicable authority;
* mandatory gates;
* required validation;
* required evidence;
* required review.

### Deepened pathway

The workflow SHOULD increase rigor when relevant conditions include:

* architecture impact;
* security sensitivity;
* privacy sensitivity;
* irreversible effect;
* production impact;
* high uncertainty;
* novel technology;
* weak evidence;
* unresolved dependencies;
* broad blast radius;
* legal/compliance consequence;
* high autonomy;
* difficult rollback.

Deepened rigor MAY introduce:

* research;
* explicit decision records;
* additional design;
* threat analysis;
* operational planning;
* migration planning;
* rollback planning;
* additional verification;
* independent review;
* human approval.

### Adaptation boundaries

The workflow MUST NOT classify a mandatory activity as optional merely to shorten the pathway.

Cost, latency, model preference, user impatience, or executor confidence alone MUST NOT justify bypassing governance.

## Workflow initiative

Under AI-driven operation, the workflow MAY proactively:

* inspect current governed state;
* identify the next useful action;
* identify missing information;
* detect contradictions;
* propose an engineering pathway;
* identify dependent or parallel work;
* request clarification;
* recommend a decision;
* draft candidate artifacts;
* recommend validation;
* analyze evidence;
* identify a changed assumption;
* propose replanning.

Such initiative does not authorize consequential effects.

## Clarification

The workflow MUST distinguish ordinary implementation discretion from material ambiguity.

### Ordinary discretion

The workflow MAY resolve a detail without additional human decision when:

* it remains within authorized scope;
* all plausible choices satisfy governing artifacts;
* the choice is reversible within delegated limits;
* policy permits the discretion;
* no additional authority is required.

### Material clarification

When ambiguity is material, the workflow MUST surface:

* the question;
* relevant governing sources;
* plausible alternatives when known;
* material consequences;
* required authority;
* a recommendation if appropriate.

The workflow MUST NOT fabricate agreement or infer consequential consent from silence.

## Decision routing

When a material question requires a governed decision, the workflow MUST route it to an existing appropriate Monad mechanism.

Possible mechanisms include:

* `DEC`;
* `APR`;
* ADR;
* CR;
* EOS review;
* accountable-owner escalation.

The workflow MUST NOT create an AI-specific decision system when native semantics are sufficient.

## Human denial

A governed denial is an authoritative input within its scope.

After denial:

1. the rejected pathway/action MUST NOT continue as though approved;
2. the workflow MAY propose a materially different conforming alternative;
3. the workflow MUST NOT repeatedly pressure for the same rejected outcome without new material governed evidence;
4. new evidence MAY legitimately trigger reevaluation according to existing authority and change-control rules.

## Dependency-aware progression

The workflow SHOULD determine:

* prerequisites;
* blocked activities;
* activities eligible for parallel work;
* sequencing constraints;
* downstream impact.

Proposed concurrency MUST preserve:

* dependency correctness;
* scope boundaries;
* resource limits;
* isolation requirements;
* authority;
* evidence attribution.

Emergent independent work MUST route to EOSP rather than silently becoming part of an active Work Packet.

## Handoff to execution

When a pathway reaches an executable action, it MUST hand off through existing EOS readiness, authorization, and execution semantics.

The workflow MUST NOT treat the pathway itself as an Execution Envelope.

Where governed execution applies:

```text
adaptive pathway
    ↓
EOS readiness / decisions / authorization
    ↓
Execution Envelope compilation
    ↓
governed execution boundary
```

Existing requirements `FR-037` through `FR-042` remain authoritative for the downstream governed-execution behavior they own.

## Replanning

Replanning MUST occur when material new information invalidates or materially changes the current pathway assumptions.

Triggers MAY include:

* failed verification;
* review findings;
* governing-input drift;
* new dependency;
* new risk;
* denied approval;
* changed architecture;
* changed requirement;
* security finding;
* provider/executor failure;
* operational evidence.

Replanning MUST preserve the history or traceability required to explain why the pathway changed.

## Governing-input drift

The workflow MUST be able to distinguish at least:

* unchanged governing inputs;
* changed but immaterial inputs;
* materially changed governing inputs;
* unresolved freshness.

For material drift, the workflow MUST NOT silently continue to present the old pathway or authorization as current.

Applicable outcomes include:

* pathway recomputation;
* execution suspension;
* clarification;
* reauthorization;
* EOSC;
* cancellation.

Exact fingerprint representation is delegated to technical/interface specifications.

## Evidence feedback

Evidence MAY influence:

* risk assessment;
* recommended rigor;
* sequencing;
* autonomy recommendations;
* validation recommendations;
* replanning.

Evidence MUST retain its provenance and status.

Examples:

* failed evidence remains failed evidence;
* stale evidence remains stale until superseded or refreshed;
* operational observation remains observation unless governed elevation occurs;
* AI interpretation of evidence remains interpretation.

## Failure behavior

### Missing context

If required context cannot be resolved, the workflow MUST report the missing dependency and MUST NOT represent the pathway as execution-ready.

### Contradictory authority

If applicable authorities conflict or cannot be resolved, the workflow MUST escalate.

### Policy denial

A denied action MUST remain denied. The workflow MAY replan around the denial only if the alternative is independently conforming.

### Provider failure

Failure of one AI provider or model MUST NOT corrupt canonical state.

Another conforming reasoning/execution participant MAY resume from governed state.

### Invalid pathway output

Malformed or incomplete AI output MUST be treated as candidate output and rejected or repaired before governed use.

### Excessive uncertainty

Where consequence is material and uncertainty remains too high to safely select a path, the workflow MUST request clarification, research, evidence, or accountable decision.

## Security and data

The adaptive workflow MUST apply least-context principles.

It SHOULD:

* minimize sensitive information supplied to external providers;
* preserve classification metadata;
* respect secret-exclusion rules;
* respect repository/path access restrictions;
* avoid unnecessary raw transcript persistence.

The workflow MUST NOT:

* grant capabilities;
* expose secrets merely because they are contextually relevant;
* infer authority from tool availability;
* allow untrusted prompt content to redefine governing policy.

Detailed control requirements are owned by `SEC-AIENG-0001`.

## Compatibility

The semantic meaning of a pathway MUST remain provider-neutral.

Different conforming AI systems MAY produce different recommendations from the same non-deterministic reasoning problem.

However:

* mandatory gates MUST remain equivalent;
* governing sources MUST remain identifiable;
* denied authority MUST remain denied;
* required decisions MUST remain required;
* required evidence/review obligations MUST remain intact.

Provider/model change MUST NOT require changes to canonical Monad authority semantics.

## Observability

For materially consequential pathways, the system SHOULD expose:

* pathway identity if persisted;
* governing-input identity;
* autonomy profile;
* major pathway activities;
* material rationale;
* clarification events;
* decision/approval references;
* replanning events;
* drift state;
* executor/harness/provider identity where relevant.

Observability MUST NOT require private chain-of-thought.

## Verification

### FUN-AIENG-V01 — Lightweight pathway

Given low-risk reversible work with satisfied prerequisites, verify that the workflow can propose reduced optional ceremony while preserving mandatory gates.

Covers `AIENG-CONF-A`.

### FUN-AIENG-V02 — Material ambiguity

Given two consequentially different interpretations of product intent, verify that the workflow surfaces a clarification/decision instead of selecting one silently.

Covers `AIENG-CONF-B`.

### FUN-AIENG-V03 — Architecture change during execution

Given execution evidence that implementation requires a governing architecture change, verify routing to EOSC rather than silent scope broadening.

Covers `AIENG-CONF-C`.

### FUN-AIENG-V04 — Bounded autonomous progression

Given explicit bounded-autonomous authority for a low-risk work subject, verify that the workflow can progress optional actions without unnecessary synchronous approval while stopping at boundaries it cannot cross.

Contributes to `AIENG-CONF-D`.

### FUN-AIENG-V05 — Increased rigor

Given security-sensitive or irreversible work, verify that the pathway increases appropriate review, authority, evidence, or planning obligations.

Contributes to `AIENG-CONF-E`.

### FUN-AIENG-V06 — Governing drift

Given a material governing requirement change after pathway derivation, verify that the old pathway is marked stale/suspect and replanning or reauthorization occurs.

Covers `AIENG-CONF-G`.

### FUN-AIENG-V07 — Provider failure

Given loss of the reasoning provider, verify that canonical state remains valid and another conforming participant can continue from governed state.

Contributes to `AIENG-CONF-H`.

### FUN-AIENG-V08 — Human denial

Given an authorized human denial, verify that the rejected action is not continued and that replanning respects the denial.

Covers `AIENG-CONF-I`.

### FUN-AIENG-V09 — Evidence invalidates assumption

Given verification or operational evidence invalidating a pathway assumption, verify that the workflow routes to replanning or change control.

Covers `AIENG-CONF-J`.

## Traceability

Primary requirement ownership:

```text
FR-043
  → FUN-AIENG-0001
```

Supporting requirements:

```text
FR-007
FR-012
FR-013
FR-014
FR-015
FR-016
FR-023
FR-024
QR-008
QR-010
```

Downstream governed-execution handoff:

```text
FUN-AIENG-0001
  → FR-037
  → FR-038
  → FR-039
  → FR-040
  → FR-041
  → FR-042
```

## Implementation boundary

This specification defines required behavior.

It does not authorize implementation.

Implementation MUST be decomposed through EOSP and executed only through separately authorized Work Cycles and Work Packets after the AIENG normative baseline and conformance traceability are accepted.
