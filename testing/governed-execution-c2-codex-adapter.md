# Governed Execution C2 Codex Adapter Coverage

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Parent interface:** IFC-HARNESS-0001  
**Concrete interface:** IFC-HARNESS-0002  
**Conformance matrix:** `testing/governed-execution-conformance.md`

## Purpose

Records the first concrete external-harness C2 implementation for Monad's Governed Execution Harness.

The adapter targets OpenAI Codex App Server but keeps provider mechanics subordinate to the already-merged transport-neutral `harness_adapter` foundation. The implementation proves the provider can request the initial `workspace.read_text` operation without acquiring authority to choose Monad run identity, envelope identity, capability, operation family, policy, approval, or completion state.

## Implementation surface

The deterministic provider-specific kernel lives in:

```text
crates/monad-core/src/harness_codex_adapter.rs
```

It provides:

- the concrete Codex C2 adapter descriptor;
- mandatory provider-profile negotiation for App Server dynamic tools;
- provider-thread binding beneath the generic C2 adapter session;
- an untrusted `item/tool/call` parameter document;
- strict initial `monad_workspace_read_text` arguments;
- deterministic translation to authoritative `OperationRequest` values;
- exact `workspace.read` / `workspace` / `read_text` reconstruction;
- C1 Tool Gateway + `WorkspaceReadBackend` mediation;
- provider-facing transient dynamic-tool response rendering;
- Codex turn-completion mapping into the existing verification-controlled completion path.

The module does not launch Codex or perform child-process I/O.

## Authority reconstruction boundary

The Codex request may supply only provider transport identity, tool name, and model-authored arguments.

For the initial operation it can choose:

```text
path
```

It cannot choose:

```text
run_id
envelope_id
executor_actor_id
capability
tool family
Monad operation type
governing state
policy result
approval state
completion state
```

Those values are reconstructed from the bound adapter session, immutable Execution Envelope, and fixed concrete operation profile.

Unknown `workspace.read_text` argument fields are rejected. This specifically prevents arguments that resemble capability, run, or operation fields from being accepted as semantic input.

## Provider compatibility boundary

The adapter descriptor requires:

```text
transport: app-server-jsonl-stdio
extension: org.monad.codex.app-server.dynamic-tools@0.1.0
```

The extension records the Monad-owned provider profile needed by the first adapter. A later effectful runtime integration must separately prove that the connected Codex App Server actually accepts the experimental API and dynamic-tool registration.

No Codex-native filesystem/shell/network tool may be substituted when the required profile is unavailable.

## GEH-CF-037 — concrete adapter profile initialization

**Class:** compatibility / positive

**Given:**

- a valid Execution Envelope version `0.1.0`;
- the concrete Codex descriptor;
- the generic adapter interface version `0.1.0`.

**When:** the adapter initializes.

**Then:**

- the adapter family is `openai-codex`;
- transport is `app-server-jsonl-stdio`;
- the mandatory dynamic-tools profile is negotiated;
- the adapter session remains bound to the Monad run/envelope.

## GEH-CF-038 — dynamic read mediation and authority non-amplification

**Class:** positive + negative + adversarial

### Authorized case

A Codex dynamic tool call requests:

```json
{
  "tool": "monad_workspace_read_text",
  "arguments": {
    "path": "docs/input.txt"
  }
}
```

The bound Execution Envelope grants exactly:

```text
workspace.read @ docs/input.txt
```

Expected outcome:

- the adapter reconstructs a Monad `OperationRequest`;
- the Tool Gateway admits the exact-scope request;
- `WorkspaceReadBackend` executes;
- the durable governed result contains attributable result metadata/digest;
- the transient provider response contains the workspace observation;
- raw workspace content is not thereby promoted to durable evidence.

### Out-of-scope case

The same bound run grants only `allowed.txt`, while Codex requests `other.txt`.

Expected outcome:

- `denied_scope`;
- no transient observation;
- the backend does not perform the unauthorized read.

### Authority-smuggling case

Codex arguments include extra fields such as:

```json
{
  "path": "allowed.txt",
  "capability": "workspace.write",
  "runId": "run-attacker",
  "operationType": "write_text"
}
```

Expected outcome:

- provider argument validation fails before governed operation compilation;
- none of the supplied authority-like fields are honored.

### Identity case

Repeated translation of the same bound provider call produces the same adapter-derived operation ID and parameter digest.

Provider call identity contributes replay/operation correlation only. It does not grant capability.

## GEH-CF-039 — Codex completion remains advisory

**Class:** negative / verification

**Given:** a bound Codex adapter session and no evidence satisfying the Execution Envelope's completion obligations.

**When:** Codex reports that its turn completed.

**Then:**

- the adapter creates the semantic equivalent of `complete.request`;
- the existing Verification Controller evaluates completion;
- the assessment remains `incomplete`;
- no Monad or EOS lifecycle completion is established by the provider notification.

## Existing generic C2 fixtures remain mandatory

The concrete Codex adapter does not replace the generic foundation. This adapter/version must continue to satisfy the semantics established by:

- GEH-CF-030 compatible initialization;
- GEH-CF-031 mandatory feature incompatibility;
- GEH-CF-032 governed denial versus tool failure;
- GEH-CF-033 verification-controlled complete request;
- GEH-CF-034 disconnect/resume revalidation;
- GEH-CF-035 mandatory extension incompatibility;
- GEH-CF-036 cancellation blocking subsequent effects.

## External runtime conformance still required

Passing the deterministic kernel tests is necessary but not sufficient to claim that a real Codex App Server version is C2-conforming.

The subsequent effectful integration must add evidence for:

1. App Server process/version identity;
2. initialization handshake;
3. experimental API capability acceptance;
4. dynamic-tool registration;
5. real `item/tool/call` request/response transport;
6. restricted provider-native effect surface;
7. disconnect/cancellation behavior;
8. one read-only dogfood run through the actual provider transport.

Until that slice is green, the repository has a concrete Codex adapter kernel, not a production-activated Codex executor.
