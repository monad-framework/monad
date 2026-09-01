# IFC-HARNESS-0001: Agent Harness Adapter Interface

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Related requirements:** pending harness requirements tranche  
**Governing ADR:** ADR-0007  
**Governing technical specification:** TECH-HARNESS-0001

## Purpose and scope

Defines the transport-neutral interface between Monad's Governed Execution Harness (GEH) and a replaceable agent/executor harness. The interface permits Codex, Claude Code, future agent harnesses, scripted executors, and a future Monad reference agent to consume the same governed execution contract without becoming authoritative for policy, capability, evidence, verification, or EOS lifecycle state.

This interface specifies semantic messages and obligations, not a wire protocol. JSON-RPC, MCP, process stdio, local IPC, HTTP, embedded library calls, or another transport MAY implement the interface if the resulting semantics conform.

## Definitions

- **GEH:** Monad Governed Execution Harness.
- **Adapter:** integration layer translating between a specific executor/harness API and this interface.
- **Executor:** the model-driven, scripted, or human-driven system performing work through the adapter.
- **Execution Envelope:** immutable governed execution contract compiled by Monad.
- **Operation:** requested consequential effect mediated by Monad.
- **Observation:** result/diagnostic returned to the executor without granting additional authority.
- **Candidate output:** executor-produced work product that has not yet been accepted by Monad verification.
- **Escalation:** explicit transfer of a decision/request to accountable authority.

## Interface invariants

1. The adapter MUST NOT broaden, reinterpret, or silently omit governing obligations in the Execution Envelope.
2. The adapter MUST NOT grant capabilities to itself or its executor.
3. Consequential governed effects MUST be requested through the GEH operation interface.
4. Executor-reported completion MUST be treated as a request for verification, not authoritative completion.
5. The adapter MUST preserve attributable run/session identity on every operation, escalation, and terminal request.
6. Adapter-specific state MUST NOT become a second authoritative EOS lifecycle state.
7. Private executor planning/reasoning representations MUST NOT be required by this interface.
8. If an adapter cannot represent a mandatory envelope obligation, initialization MUST fail with an incompatibility diagnostic rather than silently degrade governance.

## Adapter descriptor

Before execution, an adapter MUST expose a descriptor containing at least:

- `adapter_id` — stable adapter family identifier;
- `adapter_version` — implementation/version identifier;
- supported interface version(s);
- supported envelope version(s);
- executor/harness family when known;
- supported operation transport modes;
- checkpoint/resume capability;
- cancellation capability;
- streaming capability where relevant;
- delegation/subagent capability where relevant;
- declared extension namespaces;
- material limitations that affect conformance.

The GEH MUST validate compatibility before binding a run to an adapter.

## Required semantic operations

A conforming adapter interface MUST support semantic equivalents of the following operations.

### `initialize`

Binds an adapter/executor session to a governed run and Execution Envelope.

**Input:**

- run identity;
- envelope or authorized projection;
- interface/protocol version;
- GEH capability/tool descriptors available to this run;
- optional resumable checkpoint reference.

**Output:**

- accepted/rejected;
- adapter session identity;
- negotiated versions/extensions;
- compatibility diagnostics;
- optional executor configuration fingerprint required by policy.

The adapter MUST reject initialization when it cannot honor a mandatory envelope constraint.

### `next`

Allows the executor to produce its next externally observable request or output. Implementations MAY use request/response, event streaming, callback, or equivalent transport.

The executor MAY emit one or more of:

- operation request;
- candidate output/artifact reference;
- progress/status observation;
- question/input request;
- escalation request;
- verification request;
- checkpoint request;
- yield/idle state;
- cancellation request;
- terminal failure request.

No emitted message creates authority by itself.

### `operation.request`

Requests a governed operation through the Tool Gateway.

The request MUST include or inherit:

- run/session identity;
- operation/tool identifier;
- target/resource scope;
- parameters or canonical parameter representation;
- expected result shape where applicable;
- causal/delegation identity where applicable;
- idempotency/replay token when required by operation policy.

The GEH validates authority/capability/policy and returns an `operation.result`.

### `operation.result`

Returns the observable result of an operation request.

The result MUST distinguish at least:

- executed-success;
- executed-failure;
- denied-policy;
- denied-capability;
- denied-scope;
- waiting-approval;
- stale-envelope/suspended;
- cancelled;
- transport/tool failure;
- indeterminate/external verification state where applicable.

A denied result MUST NOT be represented to the executor as though the operation executed.

### `input.request`

Requests additional information or a decision that the executor cannot obtain within its authorized context/capabilities.

The request MUST identify:

- the question/decision needed;
- why it blocks or materially affects execution;
- requested authority/actor when known;
- whether work can continue safely without the answer.

The GEH decides whether to provide context, escalate, suspend, or deny.

### `escalate`

Requests transfer of a decision or action to accountable authority.

The adapter SHOULD include:

- issue/decision statement;
- relevant evidence references;
- options or constraints when available;
- execution impact;
- requested decision scope.

Escalation MUST preserve the run and envelope relationship and MUST NOT be treated as an implicit failure.

### `checkpoint`

Requests or reports a resumable execution checkpoint.

A checkpoint MUST be bound to:

- run identity;
- envelope identity/version;
- adapter/session identity;
- last acknowledged governed operation/event;
- adapter-specific opaque state if needed;
- integrity digest where required.

Opaque adapter checkpoint data MAY be stored, but Monad MUST separately retain authoritative operation/evidence history.

### `verify`

Requests evaluation of current candidate outputs/evidence against the envelope's verification obligations.

The adapter MAY provide:

- candidate output references;
- evidence references;
- executor-declared claims about what was completed.

The Verification Controller determines the result independently. The response MUST distinguish passed, failed, incomplete, blocked, and escalation-required states where applicable.

### `complete.request`

Indicates that the executor believes no further work is required.

This request MUST NOT directly set the run or EOS work item to completed. The GEH MUST invoke verification/approval rules first.

### `cancel`

Requests termination of the run. The GEH remains authoritative for cancellation state and any required recovery/rollback operations.

## Event identity and ordering

Every consequential adapter/GEH exchange MUST have an event/message identity sufficient for deduplication and audit reconstruction.

Within a run, the interface MUST provide either:

- a monotonic logical sequence number; or
- a causal ordering mechanism sufficient to reconstruct dependencies between requests/results.

Retries MUST NOT cause a previously executed non-idempotent operation to be executed again unless the operation contract explicitly permits replay.

## Error model

The interface MUST distinguish protocol/incompatibility errors from governed execution outcomes.

Protocol/incompatibility errors include:

- unsupported interface version;
- unsupported mandatory envelope feature;
- malformed message;
- unknown mandatory field/semantic extension;
- invalid run/session identity;
- ordering/replay violation;
- adapter crash/disconnect.

Governed execution outcomes include policy denial, capability denial, verification failure, approval wait, escalation, tool failure, and cancellation. These MUST NOT be collapsed into generic protocol errors.

## Extensions

Adapter- or provider-specific extensions MUST:

1. use a namespaced identifier;
2. declare whether the extension is optional or mandatory;
3. be negotiated during initialization;
4. preserve core GEH invariants;
5. fail compatibility checks if mandatory semantics cannot be honored.

An extension MUST NOT weaken capability, policy, evidence, or verification requirements defined by the core contract.

## Context projection

The adapter MAY receive either the complete Execution Envelope or a semantically equivalent, capability-limited projection optimized for that executor/provider.

A projection MUST preserve all obligations relevant to the executor. Sensitive data MAY be omitted or replaced by mediated references when the executor does not require direct access.

The adapter MUST NOT infer that omitted information is unconstrained.

## Delegation and subagents

Delegation support is optional in interface version 0.1.0.

If supported:

1. every child execution MUST receive a child run/session identity;
2. child capabilities MUST be equal to or narrower than the parent unless separately granted by accountable Monad authority;
3. child operation/evidence history MUST remain attributable;
4. the parent adapter MUST NOT use subagents as a path around Tool Gateway mediation;
5. recursive delegation limits MAY be imposed by policy/budget.

Full multi-agent orchestration semantics are deferred.

## Cancellation and disconnect behavior

The adapter MUST support best-effort cancellation notification. Once the GEH marks a run cancelled/suspended, new operation requests MUST be rejected except explicitly authorized recovery operations.

After transport disconnect, the adapter MUST NOT assume the previous session remains authorized. Resume requires GEH validation of run state, envelope freshness, checkpoint integrity, and applicable policy.

## Compatibility

Interface compatibility is versioned independently from any provider SDK.

A backward-compatible change MAY add optional fields/events whose absence preserves existing semantics. Removing/renaming mandatory semantics, changing authorization meaning, changing completion authority, or permitting previously prohibited bypass behavior requires a new incompatible interface version.

Provider SDK/API churn SHOULD be absorbed by provider-specific adapter implementations without changing this interface when governing semantics are unchanged.

## Verification

Conformance fixtures MUST include:

1. compatible initialization;
2. incompatible mandatory envelope feature rejection;
3. capability-denied operation represented distinctly from tool failure;
4. policy approval wait and resume;
5. stale-envelope suspension;
6. operation idempotency/replay handling;
7. executor complete request followed by independent verification failure;
8. escalation without run failure;
9. checkpoint/disconnect/resume;
10. cancellation blocking new operations;
11. optional extension negotiation;
12. mandatory extension incompatibility;
13. child delegation with narrowed capabilities;
14. two adapter families executing the same conformance scenario under semantically equivalent envelopes.

## Initial adapter targets

The first production implementation SHOULD target one existing executor already used by Monad so migration can be incremental. A second materially different harness SHOULD then be implemented specifically to test whether the interface is genuinely portable rather than accidentally shaped around the first adapter.

The Monad reference agent SHOULD follow only after those two integrations establish the contract's independence from any one external harness.
