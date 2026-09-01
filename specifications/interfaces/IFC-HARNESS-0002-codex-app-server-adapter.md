# IFC-HARNESS-0002: Codex App Server Adapter Profile

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Parent interface:** IFC-HARNESS-0001  
**Governing ADR:** ADR-0007  
**Governing technical specification:** TECH-HARNESS-0001  
**Concrete operation profile:** TECH-HARNESS-0002

## Purpose and scope

Defines Monad's first concrete C2 external-harness adapter profile for OpenAI Codex App Server while preserving the governing rule that Monad governs agent execution but does not prescribe agent cognition.

This profile binds Codex to the generic `IFC-HARNESS-0001` semantics. It does not make Codex, App Server, model output, a Codex thread, or a Codex turn authoritative for Monad capability, policy, evidence, verification, or EOS lifecycle state.

Version 0.1.0 is deliberately read-only. The only model-invocable governed operation exposed by this profile is the already-defined `workspace.read_text` operation from `TECH-HARNESS-0002`.

## External protocol basis

As of 2026-09-01, Codex App Server provides a bidirectional JSONL-over-stdio integration surface and an experimental `dynamicTools` facility. Dynamic tools are registered by the App Server client and invoked through the `item/tool/call` server-request flow. Use of `dynamicTools` requires App Server experimental API capability negotiation.

The adapter MUST treat these provider details as replaceable transport mechanics rather than Monad authority semantics. Provider/API changes MUST be absorbed in this concrete adapter when the governing meaning is unchanged.

Current upstream reference:

- `https://developers.openai.com/codex/app-server`

Runtime compatibility checks are authoritative over documentation assumptions. A Codex/App Server version that cannot provide the required profile MUST fail adapter initialization rather than silently degrading behavior.

## Adapter descriptor

The initial adapter descriptor is:

```text
adapter_id          adapter:openai-codex-app-server
adapter_version     0.1.0
harness_family      openai-codex
interface_version   0.1.0
envelope_version    0.1.0
transport_mode      app-server-jsonl-stdio
```

Required generic adapter features:

- checkpoint/resume;
- cancellation;
- streaming.

Required provider-specific extension:

```text
org.monad.codex.app-server.dynamic-tools@0.1.0
```

This namespaced extension means that the connected Codex integration can provide the dynamic-tool semantics required by this Monad adapter profile. It does not claim that OpenAI versions the upstream experimental API using this Monad profile version.

## Initialization and App Server capability negotiation

A concrete runtime integration MUST perform both levels of compatibility validation:

1. generic `IFC-HARNESS-0001` adapter/session negotiation within Monad; and
2. Codex App Server initialization proving the provider/runtime capabilities needed by this profile are actually available.

The App Server client MUST opt in to the experimental API capability required by `dynamicTools`.

If App Server rejects that capability, does not accept the required dynamic tool registration, or otherwise cannot provide the semantics expected by this profile, the adapter MUST fail closed.

The adapter MUST NOT substitute any of the following merely to keep execution moving:

- Codex-native shell execution;
- Codex-native unrestricted filesystem reads;
- Codex-native file writes;
- network tools;
- MCP tools not separately governed by Monad;
- approval prompts interpreted as Monad capability grants.

A provider feature being available does not make it authorized by the Execution Envelope.

## Provider thread binding

One active Codex thread MAY be bound as opaque provider state beneath a Monad C2 adapter session.

The binding MUST preserve:

```text
Monad run
  -> immutable Execution Envelope
    -> C2 adapter session
      -> opaque Codex thread identity
```

A Codex `threadId` MUST NOT replace or redefine:

- Monad `run_id`;
- Execution Envelope identity;
- executor actor identity;
- EOS execution identity;
- governing-state identity.

A dynamic tool request whose `threadId` does not match the bound provider thread MUST fail before governed operation compilation.

## Initial dynamic tool

The initial model-visible dynamic tool name is:

```text
monad_workspace_read_text
```

Its model-authored arguments are exactly:

```json
{
  "path": "repository/relative/path.txt"
}
```

Unknown argument fields are rejected in version 0.1.0.

In particular, model-authored arguments cannot set or override:

- run identity;
- envelope identity;
- executor actor;
- capability;
- Monad tool family;
- Monad operation type;
- approval state;
- policy decision;
- governing-state digest;
- operation disposition;
- evidence classification.

## Untrusted request translation

An App Server `item/tool/call` request is untrusted executor input.

The adapter may receive provider fields such as:

```text
threadId
turnId
callId
tool
arguments
```

The adapter MUST validate provider/session binding and then reconstruct the authoritative Monad `OperationRequest` from the bound C2 session and Execution Envelope.

For `monad_workspace_read_text`, the resulting authoritative request is fixed to:

```text
capability      workspace.read
tool            workspace
operation_type  read_text
target_scope    arguments.path
```

The adapter MUST derive `run_id`, `envelope_id`, and `executor_actor_id` from Monad-controlled state rather than accepting them from the provider.

Operation identity and parameter digest MUST be deterministic. Provider call identity MAY contribute to operation/replay identity but MUST NOT contribute authority.

## Effect mediation

The translated request MUST pass through the existing C1 Tool Gateway and `WorkspaceReadBackend`.

The adapter MUST NOT read the target file before the Tool Gateway admits the operation.

The existing C1 invariant remains controlling:

> A denied governed operation does not invoke its effect backend.

The backend retains all `TECH-HARNESS-0002` path, type, size, UTF-8, symlink, containment, and observation/evidence constraints.

## Provider-facing result

Monad MUST preserve the authoritative `OperationResult` disposition internally.

The App Server response MAY render that result into provider-facing text/content items so Codex can continue reasoning. The rendering MUST retain enough information for the executor to distinguish a governed denial from a backend/tool failure.

For a successful read, the provider-facing transient response may contain:

1. governed operation-result metadata; and
2. the transient UTF-8 workspace observation.

For a denied or failed read, the provider-facing response MUST NOT fabricate an observation.

Serialization into the transient App Server response does not make raw workspace text durable audit evidence. Durable evidence retention remains controlled independently by Monad evidence/provenance policy.

## Completion mapping

Codex turn completion is advisory executor state.

A `turn/completed` notification MAY cause the adapter to issue the semantic equivalent of `complete.request`, but it MUST NOT directly establish:

- Monad run completion;
- EOS Work Packet completion;
- verification success;
- approval satisfaction.

The existing C1 Verification Controller remains authoritative.

## Disconnect and resume

A transport disconnect MUST mark the adapter transport/session unavailable without creating a second EOS lifecycle.

Before resuming a Codex thread, the runtime integration MUST first satisfy the generic C2 resume path, including:

- run-state validation;
- envelope identity/freshness validation;
- checkpoint integrity;
- journal/history validation;
- applicable policy.

Only after Monad authorizes resume may the provider thread be resumed or rebound.

Provider persistence is not proof that Monad authority is still current.

## Cancellation

Monad cancellation remains authoritative.

A Codex request received after the run is cancelled MUST receive the governed `cancelled` outcome and MUST NOT reach the operation backend.

Best-effort provider turn/thread interruption SHOULD follow, but provider interruption does not substitute for Monad cancellation state.

## Built-in Codex tools

The first read-only dogfood profile MUST NOT rely on Codex built-in command execution, file mutation, network access, or other consequential provider-native tools for governed effects.

Those tools MAY exist in the provider runtime, but a conforming Monad launch configuration must restrict or disable them sufficiently that they cannot form an unmediated alternate effect path while the run is represented as governed.

If that cannot be demonstrated for the selected App Server configuration, the read-only dogfood run is not eligible for governed-execution claims.

## Inference transport versus governed effects

Network communication required to reach the selected model/provider is an executor-runtime/provider boundary, not an implicit grant of general `network` effect capability to the model.

The adapter MUST keep provider inference transport distinguishable from model-requested consequential network operations. A model/tool request to access an arbitrary network resource remains unauthorized unless a future Execution Envelope and Monad operation family explicitly grant and mediate it.

Provider/privacy/data-handling policy remains independently applicable to context sent to the model.

## Process-launch boundary

`monad-core` owns deterministic adapter semantics and untrusted-request translation only.

Launching `codex app-server`, managing child-process stdio, provider authentication, runtime version discovery, and process supervision belong in an effectful integration layer outside `monad-core`.

That integration MUST NOT bypass the adapter/session or Tool Gateway boundaries defined here.

## Conformance fixtures

The first Codex-specific fixture tranche is:

- **GEH-CF-037** — Codex profile initialization negotiates the mandatory App Server dynamic-tools profile;
- **GEH-CF-038** — Codex dynamic `workspace.read_text` request is reconstructed from bound authority, exact-scope mediated, and cannot smuggle broader authority through arguments;
- **GEH-CF-039** — Codex turn completion is routed to independent verification rather than direct governed completion.

The complete generic C2 foundation fixtures GEH-CF-030 through GEH-CF-036 remain required for this adapter version.

## Explicit exclusions

Version 0.1.0 does not authorize or implement:

- workspace writes;
- arbitrary shell/process execution;
- model-requested network access;
- deployment or release effects;
- governance mutation;
- subagent delegation;
- a Monad reference agent;
- a second adapter family;
- C3 cross-adapter portability certification;
- C4 evaluation harnessing.

## Next implementation layer

After this deterministic adapter kernel is green, the next slice SHOULD implement the effectful App Server client/runtime integration that:

1. launches or connects to a pinned/identified Codex App Server;
2. completes App Server initialization with required capability negotiation;
3. starts a restricted read-only thread with the Monad dynamic tool registered;
4. translates `item/tool/call` requests through this adapter kernel;
5. returns transient governed results to Codex;
6. routes turn completion to Monad verification;
7. performs one read-only dogfood run with attributable evidence.
