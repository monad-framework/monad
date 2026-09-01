# Governed Execution C2 Codex Runtime Conformance

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Parent matrix:** `testing/governed-execution-conformance.md`  
**Adapter profile:** `IFC-HARNESS-0002`  
**Implementation:** `crates/monad-codex-runtime`

## Purpose

Defines the effectful runtime subfixtures for the concrete OpenAI Codex App Server C2 adapter. These fixtures extend GEH-CF-037 through GEH-CF-039 from deterministic adapter translation into the actual client-owned App Server transport boundary.

This tranche proves runtime protocol behavior. It does **not** by itself activate Codex for live governed execution and does not relax the requirement that all consequential model-requested effects pass through Monad mediation.

## Runtime boundary

`monad-core` remains deterministic and provider-neutral at the authority boundary. `monad-codex-runtime` owns only replaceable integration mechanics:

- child-process launch and supervision;
- JSONL stdio transport;
- App Server initialize/initialized handshake;
- experimental API opt-in required for dynamic tools;
- restricted provider thread creation;
- `item/tool/call` request routing;
- provider-facing dynamic-tool responses;
- turn-completion event routing;
- fail-closed handling of unexpected provider requests/effects.

The runtime MUST NOT create a second capability, policy, evidence, verification, approval, or EOS lifecycle authority.

## Upstream wire contract

The runtime profile is based on the current Codex App Server contract in which:

- stdio uses newline-delimited JSON;
- JSON-RPC 2.0 semantics are used with the `jsonrpc` member omitted on the wire;
- one `initialize` request is required before other methods, followed by `initialized`;
- `initialize.params.capabilities.experimentalApi = true` enables the experimental dynamic-tools surface;
- dynamic tools are registered on `thread/start`;
- the server invokes a client-owned dynamic tool with `item/tool/call`;
- `turn/completed` reports provider turn completion independently of Monad verification.

Runtime compatibility is authoritative over documentation assumptions. A selected Codex build that rejects or materially changes these semantics is incompatible until this profile is revised and reverified.

## Restricted provider thread

The runtime MUST start the provider thread independently of the governed repository workspace.

The initial thread request MUST include, at minimum:

- an explicit provider runtime `cwd` supplied by the host;
- `runtimeWorkspaceRoots: []`;
- `ephemeral: true`;
- legacy sandbox projection `read-only` or an equivalent stricter verified permission profile;
- no automatic approval path that can be mistaken for Monad authority;
- `environments: []`;
- `selectedCapabilityRoots: []`;
- only the Monad dynamic tool required by the current profile;
- provider-native consequential surfaces disabled where the selected Codex build exposes supported configuration controls.

The current runtime disables the same broad native-tool families used by Codex's own temporary structured-thread hardening pattern, including shell/unified execution, web search, MCP servers, plugins, multi-agent paths, image/view-image paths, request-permissions tooling, hooks, and related discoverable tool surfaces.

These controls are defense in depth. Their presence in a request does not by itself prove live provider-effect confinement.

## Runtime subfixtures

### GEH-CF-037-RUNTIME — handshake and restricted thread

**Type:** compatibility / positive / negative-by-omission  
**Expected:** pass

The fixture MUST prove that the runtime:

1. sends `initialize` before other App Server requests;
2. identifies Monad as the client;
3. opts into `experimentalApi`;
4. sends `initialized` only after successful initialization;
5. initializes the generic Monad C2 adapter session;
6. starts an ephemeral provider thread;
7. binds the returned `thread.id` beneath the Monad adapter session;
8. registers `monad_workspace_read_text` with strict arguments;
9. requests empty runtime workspace roots and environments;
10. requests read-only provider sandbox semantics;
11. disables known provider-native consequential tool families.

A provider response that contradicts the required sandbox/thread semantics MUST fail closed.

### GEH-CF-038-RUNTIME — wire request mediation and alternate-effect rejection

**Type:** positive / adversarial

The fixture MUST prove that a real App Server-shaped `item/tool/call` document:

```text
threadId
turnId
callId
tool
arguments
```

is translated through `harness_codex_adapter`, mediated by the C1 Tool Gateway, executed only by `WorkspaceReadBackend` when authorized, and returned to the provider as a transient result.

The fixture MUST additionally prove:

- exact-scope reads succeed;
- provider identity remains subordinate to Monad run/envelope authority;
- unexpected provider approval/server requests are rejected rather than treated as Monad approvals;
- an observed provider-native consequential item start causes the governed runtime to fail closed;
- unknown/malformed dynamic-tool requests never broaden authority.

### GEH-CF-039-RUNTIME — provider turn completion

**Type:** verification / negative

The fixture MUST prove that:

- only the bound thread/turn completion is accepted;
- a provider turn whose status is not `completed` cannot be mapped to executor completion;
- a valid `turn/completed` event still routes to Monad's Verification Controller;
- missing verification evidence leaves the governed work incomplete.

## Transport-order regression

The runtime MUST retain a regression fixture proving that asynchronous notifications received while waiting for a request response cannot starve the response or create an infinite deferred-message loop.

## Live dogfood activation gate

Protocol conformance is not sufficient for a live governed-execution claim.

Until a selected Codex build passes a separate provider-effect confinement activation fixture, `monad-codex-runtime` MUST report live governed dogfood as ineligible.

That future activation proof MUST demonstrate, under adversarial attempts, that provider-native command/filesystem/network/tool paths cannot observe or mutate the governed repository outside Monad's authorized dynamic-tool path. Merely asking the model not to use those tools is insufficient.

The activation proof MAY rely on a selected Codex permission profile, process isolation, or another enforceable mechanism, but the mechanism MUST be machine-verifiable and fail closed when unavailable.

## Required commands

```text
cargo fmt --check
cargo test -p monad-codex-runtime
cargo test -p monad-core harness_codex_adapter
cargo test -p monad-core harness_workspace_read
```

The repository-wide C0, C1, generic C2, EOS, machine-projection, and repository-integrity gates remain required.

## Definition of done

This runtime tranche is complete when:

1. all runtime subfixtures are green;
2. the generic Codex adapter fixtures remain green;
3. workspace-read regressions remain green;
4. generated machine projections are current;
5. EOS evidence is current on the settled source/projection tree;
6. the final exact PR head is green;
7. no unresolved substantive review thread remains.

Completion of this tranche means the **effectful App Server runtime bridge exists and conforms**. It does not mean a live external Codex run has yet been certified as governed.
