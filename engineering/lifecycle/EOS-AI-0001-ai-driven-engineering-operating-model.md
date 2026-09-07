---
artifact_id: "EOS-AI-0001"
title: "AI-Driven Engineering Operating Model"
type: "governance"
version: "0.1.0"
status: "Accepted"
authority: "governance-authoritative"
created: "2026-09-05"
updated: "2026-09-05"
acceptance_evidence: "engineering/reviews/DECISION-0004-2026-09-05-eos-ai-0001-acceptance.md"
---

# EOS-AI-0001 — AI-Driven Engineering Operating Model

## 1. Purpose

This document defines the cross-layer operating contract by which artificial intelligence participates in the Monad Engineering Operating System.

It operationalizes ADR-0008 — AI-Driven Engineering as the Default EOS Operating Model.

The governing principle is:

> **AI drives the work. EOS governs the work. Humans govern consequential meaning and authority. Evidence governs acceptance.**

This operating model makes capable AI systems proactive participants in engineering analysis, planning, clarification, artifact production, bounded execution, verification assistance, review assistance, observation, learning, and replanning while preserving the authority, state, policy, evidence, and lifecycle boundaries already established by EOS.

This document does not create a new lifecycle.

The permanent EOS lifecycle remains:

```text
EOSB — Bootstrap
EOSP — Planning
EOSE — Execution
EOSV — Verification
EOSR — Review
EOSC — Change Control
EOSL — Release Lifecycle
EOSM — Maintenance
```

`EOS-AI-0001` governs how AI participates across those layers.

## 2. Governing authority

This operating model is subordinate to and constrained by higher-authority Monad governance and accepted architectural decisions.

Primary governing sources include:

* ADR-0006 — EOS Sovereignty and External SDLC Assimilation;
* ADR-0008 — AI-Driven Engineering as the Default EOS Operating Model;
* CR-0003 — Establish Monad AI-Driven Engineering Operating Model;
* `governance/authority.md`;
* `governance/canonical-state-model.md`;
* `governance/decision-process.md`;
* `governance/planning-engine.md`;
* `governance/policy-engine.md`;
* `governance/execution-engine.md`;
* `engineering/definition-of-ready.md`;
* the permanent EOS lifecycle contracts.

ADR-0007 — Governed Execution Harness Architecture remains independently governed while it is Proposed.

If ADR-0007 is later Accepted, its execution-envelope and harness-boundary model SHALL provide a compatible execution realization for the execution portions of this operating model.

Acceptance of this operating model SHALL NOT implicitly accept ADR-0007.

## 3. Operating formula

The Monad AI-Driven Engineering Operating Model is:

```text
Monad Semantic Authority
+ EOS Governance
+ AI-Driven Workflow Initiative
+ Bounded Execution
+ Human Sovereignty
+ Evidence-Based Closure
```

The complete operating loop is:

```text
INTENT
  ↓
CONTEXT COMPILATION
  ↓
PLAN
  ↓
CLARIFY
  ↓
DECIDE
  ↓
AUTHORIZE
  ↓
EXECUTE
  ↓
VERIFY
  ↓
REVIEW
  ↓
INTEGRATE / RELEASE / OPERATE
  ↓
OBSERVE
  ↓
LEARN
  ↓
REPLAN
```

A recurring inner loop is:

```text
PROPOSE
  → CLARIFY
  → DECIDE
  → APPROVE
  → EXECUTE
  → VERIFY
```

Neither representation is a second state machine.

Actual lifecycle state remains owned by EOS.

## 4. Fundamental distinctions

Every implementation conforming to this operating model SHALL preserve the following distinctions:

```text
AI initiative != AI authority

AI output != canonical engineering truth

AI recommendation != decision

Decision != approval

Readiness != authorization

Authorization != execution

Execution != verification

Verification != review

Review != acceptance

Analytical capability != delegated authority

Evidence != authority

Context projection != canonical state

Autonomy != sovereignty

Human sovereignty != mandatory human micromanagement
```

Collapsing any of these distinctions is a conformance failure when doing so changes consequential authority, lifecycle state, accepted engineering meaning, execution rights, or acceptance.

## 5. Core operating invariants

### I01 — Intent traceability

Every governed execution SHALL trace to authorized engineering intent.

An executor SHALL NOT manufacture its own governing intent merely because additional work appears useful.

Emergent work outside authorized scope SHALL route to planning or change control.

### I02 — Initiative without authority

AI MAY proactively:

* inspect governed state;
* identify ambiguity;
* analyze dependencies;
* detect inconsistency;
* propose plans;
* generate alternatives;
* recommend decisions;
* propose lifecycle actions;
* generate candidate artifacts;
* identify follow-on work.

These activities SHALL NOT confer decision, approval, execution, acceptance, or governance authority merely because the AI initiated them.

### I03 — Ambiguity escalation

Material ambiguity SHALL be surfaced rather than silently resolved by probabilistic inference.

Ambiguity is material when alternative interpretations could change consequential:

* product behavior;
* requirements;
* architecture;
* security;
* privacy;
* data handling;
* legal or compliance posture;
* operations;
* accepted risk;
* irreversible action;
* authority;
* acceptance criteria.

### I04 — Adaptive workflow

Engineering pathway depth MAY adapt to:

* risk;
* consequence;
* complexity;
* novelty;
* uncertainty;
* reversibility;
* lifecycle state;
* dependencies;
* unresolved decisions;
* evidence quality;
* security sensitivity;
* operational impact;
* delegated autonomy.

Adaptive workflow SHALL operate inside EOS.

### I05 — Explainable rigor

Materially skipped, reordered, added, or deepened engineering activities SHALL be explainable from governed inputs.

The pathway rationale need not preserve private model reasoning.

It SHALL preserve sufficient structured rationale to explain why the governed engineering pathway differs from the normal or expected pathway.

### I06 — Native decision semantics

Consequential decisions SHALL use existing Monad decision and authority mechanisms.

AI-specific decision stores SHALL NOT be created merely because an AI participated in the decision process.

### I07 — No probabilistic promotion

AI output SHALL NOT become normative or canonical solely because:

* confidence is high;
* several models agree;
* the same answer is repeated;
* a preferred provider produced it;
* a model is considered highly capable;
* a harness labels it complete.

### I08 — Bounded execution

Execution SHALL remain bounded by applicable:

* Work Packet scope;
* authority;
* policy;
* environment;
* capabilities;
* tool access;
* resource limits;
* autonomy limits;
* governing inputs;
* acceptance obligations.

### I09 — Governing drift

Material drift in governing inputs SHALL invalidate or suspend stale execution authority.

Execution SHALL NOT continue under an authorization whose governing assumptions have materially changed.

### I10 — Evidence independence

Executor assertions and executor-owned self-tests SHALL NOT alone satisfy evidence obligations where independent verification is required.

### I11 — Review independence

Review independence SHALL be enforceable as policy.

A second invocation of the same model or harness SHALL NOT automatically constitute independent review.

### I12 — Reconstructability

Consequential engineering activity SHALL remain reconstructable from governed records sufficient to identify:

```text
intent
→ context
→ pathway
→ material questions
→ decisions
→ approvals
→ authorization
→ execution
→ evidence
→ verification
→ review
→ change
→ acceptance
```

### I13 — Transcript non-authority

Raw AI transcripts SHALL NOT be mandatory canonical engineering state.

A transcript MAY be retained for convenience, debugging, research, or audit according to policy.

The structured material consequences of the interaction SHALL be captured through native Monad artifacts where required.

### I14 — Provider neutrality

AI provider, model, harness, or vendor identity SHALL NOT itself create semantic authority.

### I15 — Progressive autonomy

Higher autonomy SHALL be:

* explicit;
* bounded;
* evidence-backed;
* consequence-aware;
* observable;
* attributable;
* policy-controlled;
* revocable.

### I16 — Evidence feedback

Verification, review, operational, incident, maintenance, and performance evidence MAY inform later planning and AI reasoning.

Evidence SHALL retain its actual provenance and authority classification.

Evidence SHALL NOT become policy, architecture, requirements, or accepted truth automatically.

## 6. AI participation model

AI participation is divided into logically distinct capability classes.

### 6.1 Inspect

AI MAY inspect engineering information to which the acting identity has been granted access.

Inspection alone SHALL NOT permit mutation.

### 6.2 Reason

AI MAY analyze governed engineering information, infer implications, identify contradictions, evaluate alternatives, and estimate risk.

Reasoning output is advisory until governed otherwise.

### 6.3 Recommend

AI MAY recommend:

* engineering pathways;
* architectural alternatives;
* decisions;
* priorities;
* verification activity;
* escalation;
* change requests;
* maintenance;
* release actions.

Recommendation is not authority.

### 6.4 Propose

AI MAY construct candidate artifacts and proposed lifecycle actions.

A proposed artifact obtains authority only through its applicable governance process.

### 6.5 Execute

AI MAY execute work only when authority, lifecycle, policy, scope, environment, and capability requirements permit execution.

### 6.6 Verify

AI MAY invoke or assist validators and interpret results.

An AI executor's interpretation does not override authoritative validator evidence.

### 6.7 Review

AI MAY participate in review when permitted by review policy.

Required independence SHALL be evaluated separately.

### 6.8 Approve or accept

An AI MAY approve or accept only if explicit governance has delegated that class of binding authority.

No inference capability, benchmark performance, provider status, or historical correctness record SHALL itself grant approval authority.

## 7. Context compilation

AI-driven engineering SHALL operate from governed context rather than unbounded conversational accumulation.

### 7.1 Context source classes

A context compilation MAY include relevant:

* intent;
* requirements;
* architecture;
* specifications;
* ADRs;
* decisions;
* approvals;
* authority;
* policy;
* Program Increment state;
* Work Cycle state;
* Work Packet state;
* dependencies;
* risks;
* acceptance criteria;
* evidence;
* reviews;
* change requests;
* maintenance records;
* release state;
* operational observations;
* repository state;
* execution constraints.

### 7.2 Minimal sufficiency

The context compiler SHOULD select the smallest context sufficient for reliable execution.

More context is not automatically better context.

Irrelevant, stale, superseded, contradictory, or insufficiently authoritative context SHOULD be excluded, downgraded, or explicitly identified.

### 7.3 Authority preservation

Context compilation SHALL preserve enough metadata to distinguish:

* authoritative from informative material;
* accepted from proposed material;
* current from stale material;
* canonical from derived material;
* observation from policy;
* evidence from decision;
* recommendation from approval.

### 7.4 Compiled context is a projection

A compiled context package is derived state.

It SHALL NOT become a second canonical engineering source.

Canonical changes MUST occur through the owning Monad artifact or EOS mechanism.

### 7.5 Context fingerprints

Where execution depends materially on compiled context, implementations SHOULD provide a deterministic fingerprint or equivalent identity for the governing input set.

The fingerprint SHOULD permit detection of governing-input drift.

The exact representation is delegated to subsequent specifications.

## 8. Adaptive engineering pathway

EOSP remains responsible for turning accepted intent into bounded, traceable execution units.

AI-driven planning extends EOSP by enabling AI to propose the appropriate engineering pathway.

### 8.1 Pathway inputs

Pathway derivation SHOULD consider:

```text
intent
+ lifecycle state
+ dependencies
+ authority
+ policy
+ risk
+ complexity
+ uncertainty
+ reversibility
+ evidence
+ unresolved decisions
+ operational consequence
```

### 8.2 Lightweight work

Low-risk, reversible, well-understood work MAY receive a lightweight pathway.

Adaptive planning SHOULD reduce unnecessary ceremony when governance does not require it.

### 8.3 High-consequence work

High-consequence work MAY require additional:

* analysis;
* decision records;
* approval;
* architecture review;
* security review;
* operational planning;
* migration planning;
* verification;
* independent review;
* rollback evidence;
* authority.

### 8.4 Mandatory gates

Adaptive planning SHALL NOT bypass:

* mandatory EOS lifecycle gates;
* required authority;
* required policy;
* required verification;
* required review independence;
* unresolved blocking decisions;
* change-control obligations.

### 8.5 Pathway changes

A pathway MAY change as new evidence emerges.

Material changes SHALL be explainable and SHALL preserve traceability to the evidence, decision, risk, or governing change that caused replanning.

## 9. Clarification and decision routing

AI SHALL distinguish between ordinary implementation discretion and consequential ambiguity.

### 9.1 Implementation discretion

AI MAY independently resolve details when:

* the choice remains inside authorized scope;
* multiple choices conform to governing artifacts;
* the choice is reversible within delegated limits;
* no additional authority is required;
* policy permits the discretion.

### 9.2 Consequential ambiguity

AI SHALL escalate when uncertainty materially affects governed meaning or consequence.

The escalation package SHOULD identify:

* the unresolved question;
* known alternatives;
* applicable governing sources;
* expected consequence of each alternative;
* recommendation if one exists;
* required authority;
* impact of delay.

### 9.3 Decision persistence

Material decisions SHALL be persisted through native Monad semantics such as `DEC`, `APR`, ADR, CR, or other applicable authoritative artifacts.

Conversation history alone SHALL NOT serve as the canonical decision record when governance requires a structured decision.

## 10. Authorization

Authorization is the boundary between potentially useful work and work that may produce governed effects.

### 10.1 Authorization inputs

Authorization MAY depend on:

* lifecycle readiness;
* authority;
* approval;
* policy;
* Work Packet scope;
* dependency state;
* current governing inputs;
* risk;
* capability grants;
* environment;
* evidence;
* autonomy profile.

### 10.2 No inferred authorization

AI SHALL NOT infer permission to perform a consequential action from:

* user silence;
* previous unrelated approvals;
* broad project goals;
* prior model behavior;
* the ability of a tool to perform the action;
* a recommendation being uncontested.

### 10.3 Authorization scope

Authorization SHALL be sufficiently bounded to determine what is and is not permitted.

If authorization scope cannot be determined safely, execution SHALL fail closed or escalate.

## 11. Execution

EOSE remains responsible for executing authorized work without allowing implementation convenience to redefine governing product or architecture intent.

Existing EOSE behavior requiring execution to stop when governing requirements, specifications, ADRs, security constraints, or authorized scope must change remains authoritative.

### 11.1 Executor neutrality

The executor MAY be:

* a human;
* a script;
* Codex;
* Claude Code;
* another AI harness;
* a future Monad reference agent;
* a multi-agent system;
* another conforming executor.

Executor type SHALL NOT alter governing semantics.

### 11.2 Execution boundaries

Execution SHALL respect applicable:

* scope;
* files;
* commands;
* environment;
* network access;
* credentials;
* tools;
* resource budgets;
* time budgets;
* side-effect constraints;
* policy;
* acceptance criteria.

### 11.3 Unexpected work

Unexpected work SHALL be classified before being silently incorporated.

Possible dispositions include:

```text
inside authorized implementation discretion
→ continue

inside scope but requires explicit decision
→ clarify / decide

changes governing intent
→ EOSC

new independent work
→ EOSP

security or operational exception
→ escalate under applicable authority
```

### 11.4 Execution completion

Executor completion is a claim.

It SHALL NOT be treated as accepted completion until required verification and review obligations are satisfied.

## 12. Verification

EOSV remains authoritative for verification evidence.

AI MAY:

* recommend validation profiles;
* invoke permitted validators;
* analyze failures;
* identify likely causes;
* propose corrective work;
* assess evidence coverage.

AI SHALL NOT:

* fabricate evidence;
* silently modify failed evidence into passing evidence;
* override validator output because the model disagrees;
* treat self-report as independent evidence;
* promote stale evidence into current evidence.

Verification evidence retains its EOSV lifecycle and provenance.

## 13. Review

EOSR remains authoritative for governed review.

### 13.1 AI review participation

AI MAY perform technical, architecture, security, requirements, or consistency review according to policy.

### 13.2 Independence

Required independence MAY consider:

* execution identity;
* reviewer identity;
* model;
* provider;
* harness;
* context isolation;
* prompt isolation;
* organizational role;
* human involvement.

The exact predicate is delegated to policy and specification.

### 13.3 Review disposition

An AI reviewer MAY recommend:

```text
ACCEPTED
ACCEPTED_WITH_FOLLOW_UP
REJECTED
BLOCKED
```

where those dispositions are supported by the applicable review contract.

The recommendation SHALL NOT replace reserved human acceptance authority.

## 14. Change control

EOSC remains responsible for controlled change to governing engineering meaning.

AI-driven work SHALL route to EOSC when execution or evidence reveals a need to change governing:

* requirements;
* architecture;
* specifications;
* security constraints;
* operational commitments;
* accepted risk;
* authorized scope;
* release obligations.

AI SHALL NOT silently broaden an active Work Packet in order to avoid change control.

## 15. Release and operation

EOSL remains responsible for governed release progression.

AI MAY:

* assemble release-readiness context;
* identify blockers;
* summarize evidence;
* identify rollback concerns;
* recommend release progression;
* analyze deployment results.

AI SHALL NOT acquire release authority merely by performing these activities.

Operational observations MAY become evidence inputs for later reasoning.

They SHALL NOT directly rewrite requirements, architecture, or policy.

## 16. Maintenance

EOSM remains responsible for maintenance lifecycle.

AI MAY:

* detect maintenance concerns;
* propose maintenance items;
* classify likely causes;
* propose priority;
* propose remediation;
* execute authorized remediation;
* analyze closure evidence.

Maintenance records remain native EOS maintenance entities.

Parallel AI-maintenance stores SHALL NOT be introduced without a separately established semantic need.

## 17. Learning and replanning

Learning in this operating model means incorporation of new governed evidence into future reasoning.

It does not mean silent mutation of canonical engineering truth.

### 17.1 Learning inputs

Learning MAY consume:

* verification outcomes;
* review findings;
* defects;
* incidents;
* maintenance outcomes;
* performance measurements;
* security findings;
* rollback outcomes;
* operational observations;
* user feedback;
* execution success or failure.

### 17.2 Learning outputs

Learning MAY produce:

* revised recommendations;
* changed risk estimates;
* proposed policy changes;
* proposed requirements changes;
* proposed architecture changes;
* proposed planning changes;
* autonomy recommendations.

These outputs remain proposals until governed.

### 17.3 Replanning

When evidence invalidates a planning assumption, the system SHOULD re-enter EOSP or EOSC as appropriate.

Failure SHALL be treated as information, not as justification for bypassing governance.

## 18. Autonomy profiles

The operating model defines three principal profiles.

### 18.1 AI-assisted

The human drives progression.

AI primarily analyzes, recommends, drafts, and assists.

Binding actions generally require direct human initiation.

### 18.2 AI-driven

AI proactively drives workflow progression.

AI:

* identifies next useful actions;
* proposes pathways;
* requests clarification;
* surfaces decisions;
* produces candidate artifacts;
* performs authorized execution;
* invokes verification;
* interprets results;
* proposes replanning.

Humans intervene where authority, accountability, policy, risk, or irreversible consequence requires them.

This is the default profile established by ADR-0008 where suitable AI capability is available.

### 18.3 Bounded AI-autonomous

AI may progress work without synchronous human interaction inside an explicitly delegated boundary.

The boundary SHALL define applicable:

* scope;
* authority;
* capabilities;
* environment;
* policy;
* resource limits;
* approval thresholds;
* escalation conditions;
* evidence obligations;
* review obligations;
* revocation mechanism.

Bounded autonomy SHALL NOT create unrestricted sovereignty.

## 19. Progressive trust

Autonomy SHOULD increase only from evidence relevant to the class of work being delegated.

Relevant evidence MAY include:

* conformance success;
* validation success;
* defect rate;
* unauthorized-action rate;
* rollback rate;
* review findings;
* requirement-conformance rate;
* reproducibility;
* security outcomes;
* escalation behavior;
* recovery behavior;
* operational outcomes.

Good performance in one class of work SHALL NOT automatically authorize higher autonomy in another materially different class.

Trust SHALL be revocable.

## 20. Human sovereignty

Human sovereignty is an authority and accountability principle.

It is not a requirement that humans perform all reasoning themselves.

Humans retain governance responsibility for consequential matters according to assigned roles, including:

* mission;
* product commitments;
* architecture authority;
* accepted risk;
* security exceptions;
* legal posture;
* operational accountability;
* irreversible commitments;
* delegation;
* revocation;
* final escalation.

AI MAY surpass a human participant in analytical ability without thereby obtaining additional authority.

Authority derives from governance and delegation, not analytical performance.

## 21. Provider, model, and harness neutrality

Monad SHALL remain provider-neutral at the semantic and governance level.

Provider and harness selection MAY consider:

* capability;
* reliability;
* privacy;
* security;
* latency;
* cost;
* context capacity;
* tool support;
* availability;
* evaluation evidence.

Provider choice SHALL NOT change the semantics of:

* requirements;
* authority;
* decision;
* approval;
* Work Packet;
* evidence;
* verification;
* review;
* acceptance.

A provider outage SHALL NOT corrupt canonical Monad state.

## 22. Transcript and reasoning policy

Monad SHALL NOT require private model chain-of-thought as a governance artifact.

Raw transcripts are also noncanonical by default.

Auditability SHALL rely on material structured records such as:

```text
governing intent
governing context identity
material question
decision
approval
authorization
executor identity
observable effect
execution result
evidence
verification
review
change
acceptance
```

Transcript retention MAY be configured separately for debugging, product experience, legal, research, or operational purposes.

Sensitive information in transcripts SHALL be governed according to applicable security and privacy policy.

## 23. Canonical-state boundary

This operating model SHALL NOT create a parallel AI state authority.

`.eos/state/current.json` remains the sole current EOS operational authority according to the canonical-state model.

AI working state MAY exist transiently.

Examples include:

* conversation state;
* scratch reasoning;
* temporary plans;
* embeddings;
* caches;
* model-specific memory;
* execution checkpoints.

Such state SHALL NOT override canonical EOS state.

Where transient state produces a consequential engineering outcome, the outcome SHALL be projected into the appropriate native Monad artifact or EOS record.

## 24. Native semantic reuse

Existing Monad entities SHALL be reused wherever their semantics are sufficient.

Relevant native concepts include:

```text
PI
WC
WP
CR
DEC
APR
DEP
REV
EVID
TRC
MNT
```

Implementations SHALL NOT introduce canonical entity families such as:

```text
AI-PLAN
AI-TASK
AI-DECISION
AI-APPROVAL
AI-EVIDENCE
AI-WORKFLOW
AI-CONTEXT
AI-STATE
```

solely because AI participates in the process.

A new canonical entity family requires a separately demonstrated semantic gap and governed approval.

## 25. Governing-input drift

A governed execution depends on a set of governing inputs.

Examples include:

* requirements;
* specifications;
* ADRs;
* decisions;
* approvals;
* policies;
* Work Packet scope;
* dependencies;
* security constraints;
* acceptance criteria.

Implementations SHOULD produce an identity or fingerprint for this governing set.

When a governing input materially changes:

```text
active authorization
→ stale or suspect
→ execution suspended when required
→ context recompiled
→ impact assessed
→ reauthorization or replanning
```

A stale authorization SHALL NOT be silently treated as current.

## 26. Reconstructable accountability

For consequential work, Monad SHALL preserve enough structured information to reconstruct:

* what was intended;
* which governing sources applied;
* who or what proposed the work;
* which ambiguity was identified;
* what decision was made;
* who held authority;
* what was authorized;
* which executor acted;
* what effects occurred;
* which evidence was produced;
* which verification passed or failed;
* which review occurred;
* what changed;
* who or what accepted the result.

Raw internal reasoning is not required for this reconstruction.

## 27. Failure and recovery

AI failure SHALL be treated as an execution concern rather than canonical-state failure.

Possible failures include:

* model error;
* hallucination;
* provider outage;
* context exhaustion;
* tool failure;
* execution timeout;
* invalid output;
* contradictory recommendations;
* policy denial;
* governing drift;
* incomplete evidence;
* failed verification.

Failure handling SHOULD preserve:

* canonical engineering state;
* prior decisions;
* event history;
* evidence;
* provenance;
* current lifecycle state;
* recovery options.

A conforming alternate executor MAY resume governed work when policy and execution contracts permit.

## 28. Security and least privilege

AI-driven engineering increases the importance of explicit effect control.

Implementations SHALL preserve:

* least privilege;
* explicit capability grants;
* deny-by-default behavior where authority is unresolved;
* secret protection;
* bounded filesystem access;
* bounded process access;
* bounded network access;
* explicit external-service permissions;
* sensitive-context minimization;
* cancellation;
* resource limits;
* timeout;
* escalation;
* incident reconstructability.

Tool availability SHALL NOT itself imply authority to use the tool.

## 29. Relationship to a Governed Execution Harness

ADR-0007 is currently Proposed.

If accepted, its Governed Execution Harness SHOULD implement the execution boundary required by this operating model.

The intended relationship is:

```text
EOS-AI-0001
cross-layer AI-driven operating model
        ↓
EOSP planning / authority / policy
        ↓
governed execution boundary
        ↓
replaceable executor or harness
        ↓
observable effects and evidence
        ↓
EOSV verification
        ↓
EOSR review
        ↓
EOSC / EOSL / EOSM as applicable
```

If ADR-0007 is rejected or superseded, another execution mechanism MAY satisfy this operating model provided all relevant invariants remain intact.

## 30. Required conformance scenarios

### AIENG-CONF-A — Low-risk reversible change

Given a small, reversible, well-understood change:

* AI proposes a lightweight pathway;
* optional ceremony may be omitted;
* mandatory EOS gates remain;
* execution remains bounded;
* evidence still controls acceptance.

### AIENG-CONF-B — Ambiguous product intent

Given materially ambiguous product behavior:

* AI identifies the ambiguity;
* AI does not silently select a consequential interpretation;
* a native decision route is produced;
* affected execution waits for the required decision.

### AIENG-CONF-C — Architecture change discovered during execution

Given an authorized Work Packet whose implementation reveals a required architecture change:

* execution does not silently broaden scope;
* EOSC is invoked;
* governing architecture changes are separately authorized;
* execution resumes only under current governing inputs.

### AIENG-CONF-D — Bounded autonomous Work Packet

Given an explicitly authorized low-risk Work Packet under a bounded-autonomous profile:

* AI progresses without unnecessary synchronous human intervention;
* capability remains within the authorized envelope;
* required evidence is produced;
* escalation occurs when the envelope is exceeded.

### AIENG-CONF-E — Security-sensitive work

Given security-sensitive work:

* planning increases required rigor;
* security authority and policy are applied;
* execution capabilities narrow as required;
* verification and independent review increase where policy requires.

### AIENG-CONF-F — Independent review

Given work requiring independent review:

* the executor cannot satisfy the requirement through trivial self-review;
* independence policy is evaluated;
* review is attributable.

### AIENG-CONF-G — Governing-input drift

Given an active execution whose governing requirement changes materially:

* drift is detected;
* stale execution authority is invalidated or suspended;
* context is recompiled;
* impact is assessed;
* reauthorization or replanning occurs.

### AIENG-CONF-H — Provider failure

Given an AI provider failure during work:

* canonical engineering state remains valid;
* partial execution is attributable;
* another conforming executor may resume when permitted;
* provider state does not become the recovery authority.

### AIENG-CONF-I — Human denial

Given a consequential proposal denied by authorized human authority:

* the denial becomes a governed input;
* AI does not repeatedly pressure for the same rejected outcome;
* replanning respects the decision unless new governed evidence legitimately reopens it.

### AIENG-CONF-J — Evidence invalidates an assumption

Given verification or operational evidence that invalidates a planning assumption:

* the evidence remains evidence;
* the assumption is not silently preserved;
* the work routes to replanning or change control;
* any resulting governing change follows native authority semantics.

## 31. Specification ownership

Detailed implementation contracts are delegated to subsequent normative specifications.

Expected initial owners are:

```text
FUN-AIENG-0001
Adaptive Engineering Workflow

IFC-AIENG-0001
Engineering Agent Contract

SEC-AIENG-0001
Autonomy, Authority, and Approval Gates
```

Those specifications SHALL refine this operating model without creating a competing lifecycle or authority model.

## 32. Product requirement ownership

The operating model is expected to refine existing requirement ownership around:

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

A new requirement is expected to own the currently missing adaptive-workflow behavior:

```text
FR-037 — Provide Adaptive AI-Driven Engineering Workflow Planning
```

Requirement text remains governed by the product requirements baseline and is not created merely by this section.

## 33. Machine-level implications

This document defines normative behavior but does not itself authorize machine implementation.

Future separately authorized implementation MAY require changes to:

* context compilation;
* context fingerprints;
* governing-input fingerprints;
* adaptive-pathway representation;
* decision and approval predicates;
* autonomy policies;
* review-independence predicates;
* execution contracts;
* provider-neutral harness adapters;
* observability;
* evidence linkage;
* conformance fixtures;
* CLI operations.

No item in this section constitutes implementation authorization.

## 34. Active-program protection

This operating model SHALL NOT silently alter the active MVP critical path.

In particular:

* existing authorized Work Packets retain their current scope;
* AI operating-model design does not broaden an existing execution contract;
* runtime implementation requires separately planned and authorized work;
* normative documentation work remains distinct from product-runtime authorization.

## 35. Non-goals

This operating model does not:

* create AGI or ASI authority;
* create unrestricted autonomous development;
* require one AI provider;
* require one model;
* require one harness;
* require raw transcript storage;
* require chain-of-thought storage;
* create a ninth EOS layer;
* replace SDLC concepts where those concepts remain useful;
* make AI output canonical by default;
* eliminate human accountability;
* eliminate deterministic policy;
* eliminate verification;
* eliminate independent review;
* authorize product-runtime implementation;
* resolve ADR-0007.

## 36. Conformance

An implementation conforms to `EOS-AI-0001` only when it preserves all applicable operating invariants and does not create a competing authority, lifecycle, canonical state, evidence system, approval system, or execution authority.

Conformance SHALL be evaluated from observable governed behavior rather than private agent reasoning.

A system claiming conformance MUST be able to demonstrate, as applicable:

* traceability to authorized intent;
* bounded execution;
* explicit authority;
* ambiguity routing;
* adaptive-pathway rationale;
* governing-input freshness;
* evidence provenance;
* verification independence;
* review independence;
* provider neutrality;
* revocable autonomy;
* reconstructable accountability.

## 37. Validation before implementation planning

Before implementation Work Packets for the AI-driven operating model are authorized, the normative tranche SHALL establish that:

* ADR-0006 remains intact;
* ADR-0008 remains satisfied;
* EOS remains the sole lifecycle/control plane;
* one canonical current-state authority remains;
* no duplicate AI-specific native entity system has been introduced;
* AI initiative and binding authority remain distinct;
* adaptive pathways cannot bypass mandatory EOS gates;
* consequential ambiguity routes to native decision semantics;
* autonomy is bounded and revocable;
* provider/harness identity remains non-authoritative;
* evidence controls acceptance;
* review independence is expressible;
* governing drift can invalidate execution authority;
* all ten required conformance scenarios have normative specification ownership;
* requirement and specification traceability is complete.

## 38. Evolution

Material changes to this operating model SHALL proceed through EOSC and applicable architecture/governance authority.

Changes SHALL NOT silently weaken an accepted ADR.

If future AI capability materially changes assumptions about autonomy, authority, cognition, or human participation, Monad SHOULD reconsider the operating model explicitly rather than allowing implementation behavior to redefine governance through precedent.

## 39. Governing statement

The final governing interpretation of this operating model is:

> **AI is expected to exercise initiative, intelligence, and increasing bounded autonomy. EOS remains the control plane. Authority remains explicit and accountable. Canonical engineering meaning remains governed. Execution remains bounded. Acceptance remains evidence-based.**
