# IFC-HARNESS-0002: Codex App Server Adapter Profile

**Status:** proposed  
**Version:** 0.1.3  
**Owner:** Monad Core / EOS  
**Parent interface:** IFC-HARNESS-0001  
**Governing ADR:** ADR-0007  
**Governing technical specification:** TECH-HARNESS-0001  
**Concrete operation profile:** TECH-HARNESS-0002

## Purpose and scope

Defines Monad's first concrete C2 external-harness adapter profile for OpenAI Codex App Server while preserving the governing rule that Monad governs agent execution but does not prescribe agent cognition.

This profile binds Codex to the generic `IFC-HARNESS-0001` semantics. It does not make Codex, App Server, model output, a Codex thread, or a Codex turn authoritative for Monad capability, policy, evidence, verification, or EOS lifecycle state.

Version 0.1.x is deliberately read-only. The only model-invocable governed operation exposed by this profile is the already-defined `workspace.read_text` operation from `TECH-HARNESS-0002`.

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

The read-only live-activation profile additionally requires a machine-verifiable confinement certificate conforming to:

```text
org.monad.codex.provider-effect-confinement@0.1.0
```

This namespaced confinement extension is a Monad activation contract. It identifies the tested certificate semantics; it does not claim that OpenAI versions the upstream permissions API using Monad's extension version.

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

Unknown argument fields are rejected in version 0.1.x.

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

A runtime SHOULD additionally reject an observed provider-native consequential server request or item lifecycle event as a protocol/confinement failure rather than allow the run to continue under a governed label.

If provider-effect confinement cannot be demonstrated for the selected App Server configuration and build, the read-only dogfood run is not eligible for governed-execution claims.

## Inference transport versus governed effects

Network communication required to reach the selected model/provider is an executor-runtime/provider boundary, not an implicit grant of general `network` effect capability to the model.

The adapter MUST keep provider inference transport distinguishable from model-requested consequential network operations. A model/tool request to access an arbitrary network resource remains unauthorized unless a future Execution Envelope and Monad operation family explicitly grant and mediate it.

Provider/privacy/data-handling policy remains independently applicable to context sent to the model.

## Process-launch boundary

`monad-core` owns deterministic adapter semantics and untrusted-request translation only.

Launching `codex app-server`, managing child-process stdio, provider authentication, runtime version discovery, and process supervision belong in an effectful integration layer outside `monad-core`.

That integration MUST NOT bypass the adapter/session or Tool Gateway boundaries defined here.

The initial implementation of that effectful boundary is `crates/monad-codex-runtime`. Its existence does not move provider-specific process or transport semantics into `monad-core`.

## Effectful runtime profile

The initial App Server runtime profile MUST:

- perform the `initialize` / `initialized` connection handshake;
- request the experimental API needed for dynamic tools;
- create an ephemeral provider thread beneath the already-bound Monad C2 session;
- keep the provider runtime working directory independent from the governed workspace;
- request empty App Server runtime-workspace roots and environments for the restricted profile;
- register only the Monad dynamic tool required by this interface profile;
- disable known provider-native consequential surfaces where the selected Codex runtime exposes supported controls;
- route `item/tool/call` through the deterministic adapter kernel;
- return provider-facing transient results without changing evidence classification;
- map `turn/completed` to independent Monad verification;
- reject unexpected provider approval/server requests rather than interpreting them as Monad grants;
- fail closed when an observed provider-native consequential item starts outside the Monad Tool Gateway.

These runtime controls are necessary defense in depth. They MUST NOT be treated as sufficient activation evidence until the selected live provider build passes the provider-effect confinement gate below.

## Provider-effect confinement certificate

The deterministic certification implementation is `crates/monad-codex-confinement` and its activation fixture is `GEH-CF-038-CONFINEMENT`.

For the initial Linux profile, a successful certificate MUST bind all of the following in one App Server verifier connection:

1. a non-empty Codex/App Server user-agent identity and Linux platform identity;
2. an isolated absolute provider runtime working directory;
3. an absolute forbidden sentinel path whose marker existence is first established by the verifier host;
4. a named Codex permission-profile identifier;
5. a successful harmless `command/exec` positive control under that exact profile;
6. a provider-native `/bin/cat` attempt against the forbidden sentinel under that exact profile that is rejected or exits nonzero without leaking the marker;
7. an ephemeral `thread/start` request selecting that exact named profile;
8. `activePermissionProfile.id` returned by App Server equal to the candidate profile;
9. registration of `monad_workspace_read_text` on the certified thread setup.

A denied sentinel read by itself is insufficient. The positive command control MUST first demonstrate that the candidate profile exists and is usable; otherwise an invalid profile could create a false confinement pass.

The certificate MUST retain digests/classifications rather than the forbidden marker or raw forbidden content. A certificate is attributable activation evidence for the tested build/profile/platform/path boundary. It is not a capability grant, approval, authority token, or perpetual authorization.

A material change to Codex/App Server build, sandbox behavior, permission profile, platform, provider runtime path model, or relevant configuration invalidates reuse of the prior activation proof and requires recertification.

Version 0.1.0 of the confinement certificate supports Linux only. Other platforms MUST fail closed until a platform-specific confinement profile is defined and verified.

## Conformance fixtures

The first Codex-specific deterministic fixture tranche is:

- **GEH-CF-037** — Codex profile initialization negotiates the mandatory App Server dynamic-tools profile;
- **GEH-CF-038** — Codex dynamic `workspace.read_text` request is reconstructed from bound authority, exact-scope mediated, and cannot smuggle broader authority through arguments;
- **GEH-CF-039** — Codex turn completion is routed to independent verification rather than direct governed completion.

The effectful runtime refines those scenarios with:

- **GEH-CF-037-RUNTIME** — App Server handshake, dynamic-tool registration, and restricted provider-thread setup;
- **GEH-CF-038-RUNTIME** — App Server wire request mediation plus fail-closed handling of unexpected or provider-native alternate effect paths;
- **GEH-CF-039-RUNTIME** — App Server turn completion remains subordinate to independent Monad verification.

The activation layer additionally requires:

- **GEH-CF-038-CONFINEMENT** — positive-control validation of a named permission profile, adversarial provider-native sentinel-read denial without content leakage, and exact active-profile identity binding on the provider thread;
- **GEH-CF-038-LIVE-ACTIVATION** — immediate recertification followed by retention of the exact activation App Server connection/thread and adoption into the governed runtime without a second provider handshake or replacement thread.

The complete generic C2 foundation fixtures GEH-CF-030 through GEH-CF-036 remain required for this adapter version. Runtime subfixtures are specified in `testing/governed-execution-c2-codex-runtime.md`; provider confinement is specified in `testing/governed-execution-c2-codex-confinement.md`; retained-session activation is specified in `testing/governed-execution-c2-codex-live-activation.md`.

## Live governed-execution activation gate

Passing deterministic adapter tests, effectful runtime protocol tests, and deterministic tests of the confinement verifier implementation is necessary but not sufficient to certify a live Codex run as governed execution.

Before the first read-only live dogfood run may carry a governed-execution claim, the selected real Codex/App Server build and named permission profile MUST first produce a successful `GEH-CF-038-CONFINEMENT` certificate under an adversarial provider-native read attempt. The dogfood process MUST then perform `GEH-CF-038-LIVE-ACTIVATION` in-process and execute through the returned activation-owned runtime.

Prompt instructions, a requested sandbox setting, a verifier unit test, or a standalone preflight activation command are insufficient substitutes for a certificate and retained provider session produced inside the actual dogfood process.

The live activation wrapper MUST retain the exact App Server transport/thread created under the certified profile. It MAY replay equivalent initialize/thread metadata locally to construct deterministic runtime bookkeeping, but it MUST NOT send a second provider initialization or create a replacement thread before the governed turn.

If live certification or retained-session activation is unavailable, incompatible, ambiguous, or fails, the runtime MUST remain blocked from live governed dogfood activation. Replacement of the provider process, connection, thread, profile, provider cwd, or materially relevant configuration invalidates the binding and requires recertification/rebinding.

The actual dogfood run MUST continue to route governed workspace observations through `monad_workspace_read_text`. Provider turn completion remains advisory and independent Monad verification remains authoritative.

## Explicit exclusions

Version 0.1.x does not authorize or implement:

- workspace writes;
- arbitrary shell/process execution as governed effects;
- model-requested network access;
- deployment or release effects;
- governance mutation;
- subagent delegation;
- a Monad reference agent;
- a second adapter family;
- C3 cross-adapter portability certification;
- C4 evaluation harnessing.

## Next implementation layer

With the deterministic adapter kernel, effectful App Server runtime bridge, machine-verifiable confinement verifier, and retained-session live activation wrapper in place, the next slice is the first attributable read-only dogfood runner:

1. select and identify the concrete Codex/App Server build to run;
2. configure the dedicated named permission profile that excludes the governed repository and permits only runtime-essential reads;
3. create or verify the unique non-secret sentinel inside the governed repository;
4. invoke `certify_and_activate_runtime` inside the dogfood process so `GEH-CF-038-CONFINEMENT` and `GEH-CF-038-LIVE-ACTIVATION` bind the exact provider connection/thread that will execute;
5. retain the successful certificate/binding as attributable evidence without retaining sentinel contents;
6. execute one real read-only governed dogfood task through the returned `LiveActivatedRuntime` and `monad_workspace_read_text`;
7. prove the workspace observation traversed Monad's Tool Gateway on that exact activated thread;
8. route provider completion through Monad verification and retain attributable execution/verification evidence;
9. fail closed and recertify/rebind after any material provider build/profile/confinement/session change.
