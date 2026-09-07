# Governed Execution C2 Codex Runtime Conformance

**Status:** proposed  
**Version:** 0.1.2  
**Owner:** Monad Core / EOS  
**Parent matrix:** `testing/governed-execution-conformance.md`  
**Adapter profile:** `IFC-HARNESS-0002`  
**Implementation:** `crates/monad-codex-runtime`  
**Activation verifier:** `crates/monad-codex-confinement`  
**Live activation layer:** `crates/monad-codex-live-activation`

## Purpose

Defines the effectful runtime subfixtures for the concrete OpenAI Codex App Server C2 adapter. These fixtures extend GEH-CF-037 through GEH-CF-039 from deterministic adapter translation into the actual client-owned App Server transport boundary.

This tranche proves runtime protocol behavior. It does **not** by itself activate Codex for live governed execution and does not relax the requirement that all consequential model-requested effects pass through Monad mediation.

The separate `GEH-CF-038-CONFINEMENT` activation fixture now provides the machine-verifiable mechanism for proving provider-native read isolation against a selected real Codex/App Server build/profile. Runtime conformance and live confinement certification remain deliberately distinct obligations.

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

## Provider-effect confinement activation gate

Protocol conformance is not sufficient for a live governed-execution claim.

The implemented `monad-codex-confinement` verifier defines `GEH-CF-038-CONFINEMENT`. For the initial Linux profile it directly exercises the same App Server permission-profile/sandbox execution path with:

1. host verification of a unique forbidden sentinel;
2. a successful harmless positive `command/exec` control under the candidate named permission profile;
3. a provider-native forbidden sentinel read under the same profile that must be rejected or exit nonzero without leaking the marker;
4. an ephemeral `thread/start` that must report the exact same `activePermissionProfile.id`.

This prevents an invalid permission profile from false-passing merely because all commands fail and prevents profile substitution between the direct sandbox probe and the provider-thread setup.

A deterministic test of the verifier implementation is not a live activation certificate. The selected real Codex/App Server build/profile must itself pass the fixture before the run may be represented as governed.

The raw runtime's existing `require_live_governed_dogfood_eligibility()` remains intentionally fail-closed. The live activation layer does not toggle that raw-runtime guard. Instead, `LiveActivatedRuntime` owns the exact App Server connection/thread that passed activation and is the only wrapper allowed to expose positive live-dogfood eligibility for the initial profile.

Runtime adoption of that exact connection MAY replay initialize/thread metadata locally to construct existing `CodexAppServerRuntime` bookkeeping, but it MUST NOT send a second provider `initialize` or `thread/start`. The adopted runtime session thread MUST equal the activation binding thread before eligibility succeeds.

A successful confinement certificate and live activation binding are evidence for the exact tested provider build/profile/platform/path/connection/thread boundary. They MUST NOT broaden the Execution Envelope, grant an approval, authorize a new tool, or establish completion. Material provider or confinement changes, or replacement of the bound provider connection/thread, require recertification/rebinding.

## Required commands

```text
cargo fmt --check
cargo test -p monad-codex-runtime
cargo test -p monad-core harness_codex_adapter
cargo test -p monad-core harness_workspace_read
cargo test -p monad-codex-confinement
cargo test -p monad-codex-live-activation
```

The repository-wide C0, C1, generic C2, EOS, machine-projection, and repository-integrity gates remain required.

## Definition of done

The runtime bridge remains conforming when:

1. all runtime subfixtures are green;
2. the generic Codex adapter fixtures remain green;
3. workspace-read regressions remain green;
4. confinement-verifier deterministic fixtures remain green;
5. retained-session activation fixtures remain green and prove no second provider handshake/thread creation during adoption;
6. generated machine projections are current;
7. EOS evidence is current on the settled source/projection tree;
8. the final exact PR head is green;
9. no unresolved substantive review thread remains.

Completion of the confinement-verifier and retained-session activation tranches means the **mechanisms for live provider-effect certification and exact-session runtime binding exist and conform**. It does not mean a live external Codex turn has yet completed governed dogfood; that claim requires an actual successful `GEH-CF-038-CONFINEMENT` plus in-process `GEH-CF-038-LIVE-ACTIVATION` against the selected live build/profile and the subsequent attributable dogfood execution.
