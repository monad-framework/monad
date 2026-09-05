# IFC-AIENG-0001: Engineering Agent Contract

**Status:** review
**Version:** 0.1.0
**Owner:** Monad Core / EOS
**Reviewers:** Product Owner, Architecture Owner, Engineering Owner, Security Owner, Operations Owner, Verification Owner as affected
**Related requirements:** FR-007, FR-012, FR-013, FR-014, FR-015, FR-016, FR-017, FR-023, FR-024, FR-043, QR-008, QR-010
**Related execution requirements:** FR-037, FR-038, FR-039, FR-040, FR-041, FR-042
**Governing ADRs:** ADR-0006, ADR-0008
**Governing operating model:** EOS-AI-0001
**Related specifications:** FUN-AIENG-0001, IFC-HARNESS-0001, TECH-HARNESS-0001
**Change authority:** CR-0003

## Purpose and scope

This specification defines the provider-neutral semantic contract between Monad's Engineering Operating System and an AI engineering participant.

An AI engineering participant may inspect governed context, reason about engineering state, propose pathways, request clarification, recommend decisions, draft candidate artifacts, recommend execution, interpret evidence, participate in review where authorized, and propose replanning.

This interface governs those interactions without making the AI participant an independent lifecycle, state, authority, decision, evidence, or execution system.

The core relationship is:

```text
Monad governed engineering state
        ↓
bounded context
        ↓
engineering participant
        ↓
proposal / question / recommendation / candidate artifact
        ↓
EOS authority / policy / decision semantics
        ↓
authorized execution where applicable
```

The interface is transport-neutral.

A conforming implementation MAY use:

* local process invocation;
* embedded library calls;
* MCP;
* JSON-RPC;
* HTTP;
* message queues;
* provider APIs;
* IDE integration;
* CLI mediation;
* another transport.

Transport choice MUST NOT alter the semantic authority model.

## Relationship to IFC-HARNESS-0001

`IFC-HARNESS-0001` defines the interface between the Governed Execution Harness and an executor/harness after governed execution has been bound.

`IFC-AIENG-0001` has a broader and earlier responsibility.

It governs AI engineering participation including:

* context consumption;
* engineering analysis;
* adaptive-pathway proposal;
* clarification;
* decision recommendation;
* candidate artifact generation;
* requested lifecycle progression;
* requested execution;
* evidence interpretation;
* review participation;
* replanning.

The boundary is:

```text
IFC-AIENG-0001
engineering participation
        ↓
EOS decisions / authority / readiness
        ↓
execution authorization
        ↓
FR-037..FR-042
        ↓
IFC-HARNESS-0001
governed executor interaction
```

`IFC-AIENG-0001` MUST NOT redefine:

* Execution Envelope semantics;
* Tool Gateway operation mediation;
* harness run lifecycle;
* governed operation requests;
* execution checkpoints;
* execution completion semantics.

Those concerns remain owned by the governed-execution contracts.

## Definitions

### Engineering participant

A human, AI model, agent, agent harness, composite agent system, script-assisted intelligence layer, or future Monad-native participant capable of contributing engineering reasoning or candidate work.

This specification primarily governs AI participants.

### Participant adapter

The integration component that converts a provider/model/harness-specific API into the semantic operations defined by this interface.

### Engineering session

A bounded interaction between Monad and an engineering participant concerning one or more governed subjects.

An engineering session is transient operational context.

It is not EOS lifecycle state.

### Governing context

A bounded projection of applicable engineering knowledge and state supplied to or made queryable by a participant.

### Context identity

An identifier, digest, revision, or equivalent reference sufficient to identify the materially governing inputs represented in a context projection.

### Proposal

A non-binding candidate engineering outcome submitted by a participant.

Examples include:

* pathway proposal;
* decision recommendation;
* artifact draft;
* execution request;
* replanning proposal.

### Material question

A question whose answer could change consequential engineering meaning, authority, risk, scope, architecture, security, operations, acceptance, or irreversible effect.

### Candidate artifact

Participant-generated content that may become a governed artifact only through the artifact's applicable authority and lifecycle process.

### Authority disposition

The governed result of evaluating whether an actor or proposal possesses or has received sufficient authority for a particular action.

### Engineering observation

Information returned to or produced by a participant that does not itself change governing authority.

## Interface invariants

### AIENG-IFC-I01 — EOS sovereignty

The interface MUST NOT establish a parallel lifecycle or control plane.

### AIENG-IFC-I02 — Canonical-state sovereignty

Participant session state, memory, caches, transcripts, provider state, or internal plans MUST NOT override canonical Monad/EOS state.

### AIENG-IFC-I03 — Proposal non-authority

A participant message MUST NOT become authoritative merely because it is validly formatted, high-confidence, repeated, or generated by a preferred model.

### AIENG-IFC-I04 — Explicit authority separation

The interface MUST preserve the distinction among:

```text
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

### AIENG-IFC-I05 — Context provenance

Material governing context supplied to a participant MUST remain attributable to its source or governing identity.

### AIENG-IFC-I06 — Stale-context safety

A participant MUST NOT be allowed to represent materially stale context as current without explicit stale-state handling.

### AIENG-IFC-I07 — No private-reasoning dependency

The interface MUST NOT require private model chain-of-thought for governance, auditability, or conformance.

### AIENG-IFC-I08 — Provider neutrality

Provider, model, or harness identity MUST NOT confer semantic authority.

### AIENG-IFC-I09 — Native decision routing

Material decisions MUST route through existing Monad decision/approval/governance semantics rather than an AI-specific authority mechanism.

### AIENG-IFC-I10 — Execution handoff

A participant request for consequential execution MUST route into the applicable governed execution boundary.

### AIENG-IFC-I11 — Human denial integrity

A governed denial MUST be communicated as an authoritative constraint within its scope and MUST NOT be silently reinterpreted as approval.

### AIENG-IFC-I12 — Revocability

Participant capability, autonomy, or authorization represented through this interface MUST support revocation or invalidation according to governing policy.

## Participant descriptor

Before material engineering interaction, a participant adapter SHOULD expose a descriptor.

The descriptor MUST be capable of identifying:

* `participant_adapter_id`;
* adapter version;
* supported interface version(s);
* provider family where applicable;
* model/harness family where applicable;
* declared engineering capabilities;
* supported context modes;
* streaming support;
* structured-output support;
* tool/execution handoff support;
* checkpoint or resumable-session support where applicable;
* review participation support;
* delegation/subagent support where applicable;
* declared limitations;
* extension namespaces.

The descriptor is descriptive.

It does not grant capabilities or authority.

## Capability classes

The contract distinguishes the following logical classes.

### Inspect

Consume authorized engineering information.

### Analyze

Reason about engineering meaning, relationships, risks, alternatives, contradictions, or likely consequences.

### Recommend

Recommend an engineering action or decision.

### Propose

Construct a candidate pathway, artifact, change, decision, or other governed object.

### Request

Request context, clarification, decision, authorization, execution, verification, or review.

### Execute

Perform governed effects only through an applicable separately authorized execution boundary.

### Verify

Invoke or assist verification where policy permits.

### Review

Participate in review where applicable independence and authority requirements are satisfied.

### Approve or accept

Perform a binding approval/acceptance only where explicit governance delegates that authority.

A participant's descriptor MAY declare technical ability to support any class.

Technical ability MUST NOT be interpreted as authority.

## Common message envelope

Every consequential semantic exchange SHOULD support a common envelope containing equivalent fields to:

```text
message_id
message_type
interface_version
session_id
subject_id
actor_or_participant_id
timestamp_or_logical_time
causal_parent_id
context_identity
autonomy_profile
authority_classification
payload
```

Not every field is mandatory for every transport.

However, implementations MUST retain sufficient identity and causality to reconstruct consequential exchanges.

## Session initialization

### `session.initialize`

Establishes a bounded engineering interaction.

#### Input

The initialization request SHOULD provide:

* session identity;
* engineering subject or intent;
* interface version;
* participant descriptor requirements;
* current autonomy profile;
* authorized context-access mode;
* relevant policy constraints;
* relevant confidentiality/data-handling constraints;
* initial governing-context identity where available.

#### Output

The participant adapter MUST return:

* accepted or rejected;
* negotiated interface version;
* participant/session identity;
* declared capability profile;
* material compatibility limitations;
* supported extension namespaces;
* any initialization diagnostics.

Initialization success does not authorize execution.

## Context interface

### `context.offer`

Provides a bounded context projection to the participant.

The projection SHOULD preserve sufficient information to distinguish:

* canonical material;
* derived material;
* proposed material;
* accepted decisions;
* approvals;
* evidence;
* observations;
* stale material;
* contradictory material;
* informative material.

The context MUST identify its governing basis or context identity where consequential reasoning depends on it.

### `context.request`

Allows a participant to request additional context.

The request SHOULD identify:

* information sought;
* relevance to the engineering subject;
* whether absence blocks progress;
* desired granularity where applicable.

Monad MAY:

* provide the context;
* provide a reduced/redacted projection;
* deny the request;
* require escalation;
* identify that the information does not exist.

Missing information MUST NOT be interpreted as unrestricted freedom.

### `context.result`

The result MUST distinguish at least:

* supplied;
* supplied-redacted;
* unavailable;
* denied-policy;
* denied-authority;
* not-found;
* stale;
* contradictory;
* escalation-required.

## Pathway proposal

### `pathway.propose`

Allows an engineering participant to propose an adaptive engineering pathway.

The proposal SHOULD include:

* subject;
* context identity;
* proposed activities;
* ordering/dependencies;
* mandatory activities identified;
* optional activities identified;
* unresolved material questions;
* expected decisions;
* proposed authority boundaries;
* expected verification obligations;
* expected review obligations;
* escalation conditions;
* autonomy assumptions;
* structured rationale for material rigor adaptation.

The proposal is non-binding.

Monad evaluates it against `FUN-AIENG-0001`, EOS lifecycle state, authority, and policy.

### `pathway.disposition`

Monad MUST be able to return a disposition equivalent to:

* accepted-for-planning;
* accepted-with-modification;
* clarification-required;
* decision-required;
* blocked;
* stale-context;
* rejected-policy;
* rejected-authority;
* invalid;
* superseded.

`accepted-for-planning` MUST NOT mean execution-authorized.

## Clarification interface

### `clarification.request`

The participant uses this operation when information or meaning cannot safely be inferred.

A material clarification request SHOULD contain:

* question;
* affected subject;
* relevant governing sources;
* known alternatives;
* material consequences;
* recommendation if one exists;
* authority believed necessary;
* whether other work can safely continue.

### `clarification.response`

A response MUST identify whether it is:

* informative;
* governing;
* provisional;
* rejected;
* unresolved;
* superseded.

If a response constitutes a consequential decision, the canonical decision MUST be persisted through the applicable native mechanism.

The conversational response alone MUST NOT replace required decision persistence.

## Decision proposal interface

### `decision.propose`

A participant MAY recommend a decision.

The proposal SHOULD identify:

* decision question;
* alternatives considered;
* relevant evidence;
* relevant constraints;
* recommendation;
* expected consequences;
* required accountable authority.

A decision proposal MUST be clearly distinguishable from an actual decision.

### `decision.disposition`

Monad may respond with:

* recorded;
* approved;
* rejected;
* deferred;
* clarification-required;
* escalation-required;
* insufficient-authority;
* superseded.

When a native `DEC`, `APR`, ADR, CR, or other record is created, its identifier SHOULD be returned to the participant.

## Candidate artifact interface

### `artifact.propose`

The participant MAY submit:

* full candidate content;
* patch/diff;
* structured artifact model;
* reference to generated content.

The request SHOULD identify:

* proposed artifact type;
* proposed canonical path where applicable;
* governing subject;
* relevant requirements/decisions;
* context identity;
* claimed purpose.

Submission does not make the artifact canonical or accepted.

### `artifact.disposition`

Monad MUST be able to distinguish:

* candidate-received;
* validation-failed;
* review-required;
* authority-required;
* accepted-into-governed-workflow;
* rejected;
* superseded.

Canonical artifact creation or lifecycle transition remains owned by the applicable Monad/EOS mechanism.

## Lifecycle-action proposal

### `lifecycle.propose`

A participant MAY recommend that EOS perform a lifecycle action such as:

* create planning work;
* mark readiness;
* request authorization;
* begin execution;
* enter verification;
* request review;
* enter change control;
* create maintenance;
* prepare release.

The proposal MUST contain:

* target;
* requested action;
* rationale;
* context identity;
* known prerequisite status;
* evidence references where relevant.

The proposal MUST NOT directly mutate EOS lifecycle state.

### `lifecycle.disposition`

Monad MUST return an explicit governed result such as:

* accepted;
* rejected;
* blocked-prerequisite;
* insufficient-authority;
* policy-denied;
* invalid-transition;
* stale-context;
* escalation-required.

## Execution request and handoff

### `execution.request`

An engineering participant MAY request governed execution.

The request SHOULD identify:

* work subject;
* intended outcome;
* applicable pathway reference;
* governing context identity;
* candidate scope;
* known constraints;
* required capabilities if known;
* relevant decisions/approvals;
* requested executor profile.

This message is an execution request, not an Execution Envelope.

Monad MUST independently determine whether:

* the work is ready;
* authority exists;
* required decisions are resolved;
* policy permits execution;
* an Execution Envelope can be compiled;
* the requested executor/harness is compatible.

### `execution.disposition`

Possible dispositions include:

* authorized-for-envelope-compilation;
* clarification-required;
* decision-required;
* approval-required;
* blocked-dependency;
* policy-denied;
* authority-denied;
* stale-context;
* invalid-scope;
* rejected.

If execution proceeds, subsequent executor interaction SHALL use the applicable governed-execution contracts, including `IFC-HARNESS-0001` where that architecture applies.

## Evidence interpretation

### `evidence.interpret`

A participant MAY analyze governed evidence.

Input MAY include:

* evidence identifiers;
* verification results;
* review findings;
* operational observations;
* incident or maintenance records.

Output MAY include:

* interpretation;
* inferred implications;
* changed risk recommendation;
* replanning recommendation;
* proposed follow-up work.

Interpretation MUST remain distinguishable from the underlying evidence.

AI interpretation MUST NOT alter evidence state or result.

## Verification assistance

### `verification.recommend`

A participant MAY recommend:

* validators;
* validation profiles;
* additional evidence;
* likely failure causes;
* remediation.

### `verification.request`

Where permitted, a participant MAY request invocation of verification.

Actual validator execution and authoritative verification state remain governed by EOSV.

### `verification.result`

The participant MAY receive authoritative or projected results including:

* passed;
* failed;
* incomplete;
* stale;
* blocked;
* skipped;
* indeterminate.

The participant MUST NOT convert a failed or stale result into success.

## Review participation

### `review.request`

Monad MAY request AI review of a governed subject.

The request SHOULD provide:

* review subject;
* review criteria;
* context identity;
* required independence properties;
* expected output shape.

### `review.result`

A participant MAY return:

* findings;
* severity;
* evidence references;
* recommendation;
* unresolved concerns.

A participant's result MUST identify enough participant/provider/harness context to evaluate required independence.

An AI review recommendation does not itself constitute reserved human acceptance.

## Replanning interface

### `replan.propose`

A participant SHOULD use replanning when material evidence or governing change invalidates the current pathway.

The proposal SHOULD identify:

* prior pathway or plan;
* triggering evidence/change;
* assumptions invalidated;
* proposed revised activities;
* changed decision/approval needs;
* changed verification/review needs;
* changed execution implications.

### `replan.disposition`

Monad may return:

* accepted-for-planning;
* change-control-required;
* clarification-required;
* decision-required;
* blocked;
* rejected;
* superseded.

Replanning MUST NOT silently modify an authorized Work Packet's governing scope.

## Governing-input drift

A context or pathway exchange SHOULD be bound to a context identity where material correctness depends on governing inputs.

When Monad determines that context has materially drifted, it MUST be able to communicate a stale-context disposition.

The participant MUST then:

* stop representing the prior context as current;
* refresh context;
* reassess affected recommendations;
* replan where necessary;
* request reauthorization where required.

The interface MUST NOT permit a participant to override a stale-context determination based solely on model confidence.

## Autonomy profile interaction

The session MUST be capable of communicating the applicable autonomy profile:

```text
AI-assisted
AI-driven
bounded-AI-autonomous
```

The autonomy profile controls what classes of progression may occur without synchronous human interaction.

It does not redefine authority.

A participant MUST NOT self-promote to a stronger autonomy profile.

A changed profile MUST originate from governed authority/policy.

## Human denial semantics

A denial MUST be represented as a durable or attributable governed disposition when consequential.

The participant MUST treat the denial as binding within its scope.

The participant MAY:

* accept the denial;
* propose a different conforming approach;
* request clarification about its scope;
* revisit only when new material governed evidence justifies reevaluation.

The participant MUST NOT repeatedly resubmit the same materially unchanged rejected proposal in an attempt to obtain a different answer.

## Provider failure

Provider or participant failure MUST NOT corrupt EOS state.

A session may terminate or become unavailable while:

* canonical state remains valid;
* material decisions remain persisted;
* evidence remains preserved;
* lifecycle state remains authoritative;
* another compatible participant may resume from governed context.

Provider-local memory MUST NOT be required for authoritative recovery.

## Session completion

### `session.yield`

A participant MAY indicate that it has no currently authorized useful action.

Yield is not failure.

### `session.close`

Closes the transient engineering session.

Closing a session MUST NOT:

* close a Work Packet;
* accept an artifact;
* verify execution;
* approve a decision;
* release software;
* alter canonical lifecycle state.

## Event identity and causality

Consequential messages MUST have identity sufficient for:

* deduplication;
* correlation;
* causal reconstruction;
* auditability.

A conforming implementation SHOULD provide either:

* monotonic session sequence numbers;
* causal parent references;
* another deterministic causal mechanism.

Retries MUST NOT create duplicate governed decisions or effects.

## Error model

The interface MUST distinguish protocol errors from governed outcomes.

### Protocol errors

Examples:

* unsupported interface version;
* malformed message;
* unknown mandatory message type;
* invalid session identity;
* unsupported mandatory extension;
* incompatible participant adapter;
* serialization failure;
* transport failure.

### Governed outcomes

Examples:

* insufficient authority;
* policy denial;
* material ambiguity;
* stale context;
* decision required;
* approval required;
* blocked dependency;
* verification failure;
* review rejection;
* human denial.

A governed denial MUST NOT be collapsed into a generic technical error.

## Extension model

Extensions MUST:

1. use a namespace;
2. declare version;
3. declare whether optional or mandatory;
4. be negotiated where necessary;
5. preserve all core invariants.

Extensions MUST NOT:

* create hidden authority;
* bypass EOS lifecycle gates;
* bypass execution mediation;
* convert proposals into approvals;
* weaken evidence obligations.

## Security and data

The interface MUST support least-context operation.

Implementations MUST be able to enforce:

* authorized context access;
* sensitive-data minimization;
* secret exclusion;
* provider data-handling constraints;
* repository/path access limits;
* retention policy;
* participant identity;
* audit attribution.

The interface MUST NOT treat a participant's request for more context as permission to disclose it.

Detailed authority, delegation, capability, approval, revocation, and security requirements are owned by `SEC-AIENG-0001`.

## Transcript policy

Implementations MAY retain transcripts according to configured policy.

Transcripts are noncanonical by default.

Conformance and auditability MUST NOT depend on preserving private chain-of-thought.

Material outcomes MUST instead be reconstructable from structured records such as:

```text
context identity
proposal
material question
decision
approval or denial
authorization
execution handoff
evidence
verification
review
replanning
acceptance
```

## Compatibility

Interface compatibility MUST be explicit.

A participant adapter SHOULD advertise:

* supported interface versions;
* required extensions;
* optional extensions;
* context capabilities;
* structured-output capabilities;
* known limitations.

An adapter unable to preserve a mandatory semantic obligation MUST fail compatibility rather than silently weaken the contract.

Minor implementation variation is allowed where observable semantics remain compatible.

## Versioning

Breaking changes include changes that materially alter:

* authority semantics;
* message meaning;
* required fields;
* context classification;
* execution handoff;
* denial behavior;
* lifecycle proposal semantics;
* compatibility obligations.

Breaking changes require an interface version change and governed consumer-impact analysis.

## Observability

Consequential sessions SHOULD expose:

* session identity;
* participant identity;
* provider/model/harness identity where applicable;
* subject;
* context identity;
* autonomy profile;
* proposal identities;
* clarification events;
* decision references;
* lifecycle requests/dispositions;
* execution handoffs;
* evidence interpretation;
* review participation;
* replanning;
* terminal session state.

Observability MUST NOT require private chain-of-thought.

## Verification

### AIENG-IFC-V01 — Proposal is not authority

Submit a pathway or lifecycle proposal and verify that no binding state change occurs solely from receipt.

### AIENG-IFC-V02 — Material clarification

Given materially ambiguous intent, verify that `clarification.request` can surface the question without silently choosing a consequential interpretation.

Contributes to `AIENG-CONF-B`.

### AIENG-IFC-V03 — Native decision routing

Submit a consequential decision proposal and verify that the canonical outcome is represented through native decision/approval semantics.

### AIENG-IFC-V04 — Execution handoff

Submit `execution.request` and verify that consequential execution does not begin until EOS authorization and downstream governed execution requirements are satisfied.

### AIENG-IFC-V05 — Stale context

Change a materially governing input after context issuance and verify that stale-context handling invalidates current-use assumptions.

Contributes to `AIENG-CONF-G`.

### AIENG-IFC-V06 — Human denial

Return a governed denial and verify that the participant does not treat it as approval or repeatedly resubmit the unchanged rejected action.

Covers the interface portion of `AIENG-CONF-I`.

### AIENG-IFC-V07 — Provider replacement

Terminate one participant/provider and verify another compatible participant can resume from governed context without provider-local state becoming authoritative.

Contributes to `AIENG-CONF-H`.

### AIENG-IFC-V08 — Evidence interpretation

Provide failed verification evidence and verify that AI interpretation cannot mutate the failure into a passing authoritative result.

Contributes to `AIENG-CONF-J`.

### AIENG-IFC-V09 — Review independence metadata

Given an AI review request, verify that enough participant identity/context metadata is retained to evaluate applicable independence policy.

Contributes to `AIENG-CONF-F`.

### AIENG-IFC-V10 — Autonomy non-self-promotion

Verify that a participant cannot change itself from AI-driven to bounded AI-autonomous through its own message.

Contributes to `AIENG-CONF-D`.

## Traceability

Primary relationships:

```text
FR-043
  → FUN-AIENG-0001
  → IFC-AIENG-0001
```

Context relationships:

```text
FR-007
FR-012
FR-013
FR-014
FR-015
FR-016
FR-017
FR-023
FR-024
QR-008
QR-010
  → IFC-AIENG-0001
```

Execution handoff:

```text
IFC-AIENG-0001
  → EOS authority/readiness
  → FR-037
  → FR-038
  → IFC-HARNESS-0001 / conforming execution boundary
  → FR-040
```

Security refinement:

```text
IFC-AIENG-0001
  → SEC-AIENG-0001
```

## Implementation boundary

This specification defines the semantic interface required for conforming AI engineering participation.

It does not authorize implementation.

Provider adapters, APIs, MCP tools, CLI commands, schemas, runtime services, or harness integrations MUST be planned through EOSP and implemented only through separately authorized Work Cycles and Work Packets.
