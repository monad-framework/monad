# Governed Execution C2 Codex Live Activation Binding

**Status:** proposed  
**Version:** 0.1.1  
**Owner:** Monad Core / EOS  
**Precondition:** `GEH-CF-038-CONFINEMENT`  
**Runtime:** `crates/monad-codex-runtime`  
**Confinement verifier:** `crates/monad-codex-confinement`  
**Activation layer:** `crates/monad-codex-live-activation`

## Purpose

Bind a successful provider-effect confinement result to the exact App Server connection and thread that the governed runtime will use.

A confinement certificate is not a perpetual authorization token, and a metadata-only activation record is not sufficient. The activation layer reruns confinement immediately before activation, starts a fresh App Server connection, requires the same build identity, platform, named permission profile, provider runtime cwd, forbidden boundary, and Monad dynamic-tool boundary, and then retains ownership of that exact connection/thread while constructing the governed runtime session.

This slice establishes the fail-closed retained-session activation boundary. It does not yet claim that a real model turn has completed a Monad-governed dogfood task.

## GEH-CF-038-LIVE-ACTIVATION

**Type:** C2 activation / attributable binding / fail-closed  
**Expected:** pass before the first live governed Codex turn

The activation path MUST:

1. rerun `GEH-CF-038-CONFINEMENT` against the selected live Codex executable, named permission profile, isolated provider cwd, and governed sentinel;
2. require a verified confinement certificate;
3. start a fresh App Server process from the same selected Codex executable;
4. initialize the activation connection with experimental API support;
5. require the activation App Server user-agent identity to equal the confinement certificate identity;
6. require platform family and OS to equal the certificate values;
7. start an ephemeral activation thread with `permissions = <certified profile>` explicitly supplied;
8. require empty runtime workspace roots, environments, and selected capability roots;
9. register only the Monad governed workspace-read dynamic tool for governed observations;
10. keep known provider-native consequential feature surfaces disabled;
11. require `activePermissionProfile.id == <certified profile>` on the activation thread;
12. fail closed on any identity, platform, profile, cwd, boundary, protocol, or tool mismatch;
13. emit an activation binding containing the confinement certificate digest and the exact activation thread/profile identity;
14. retain the exact activation transport and thread in-process when constructing the governed runtime;
15. construct runtime bookkeeping without sending a second provider `initialize` or `thread/start` that could substitute an unbound connection or thread;
16. require the adopted runtime session thread id to equal the activation binding thread id before live eligibility is exposed.

The confinement certificate and activation binding remain evidence, not capability, authority, approval, or completion.

## Runtime ownership invariant

The initial live profile has one eligible runtime shape:

```text
GEH-CF-038-CONFINEMENT
  -> live activation App Server connection
    -> exact certified-profile activation thread
      -> LiveActivatedRuntime
        -> existing CodexAppServerRuntime mediation
          -> Monad adapter / Tool Gateway / Verification Controller
```

`LiveActivatedRuntime` MUST own the exact App Server transport and thread produced during activation. Runtime adoption MAY replay the already-proven initialize/thread metadata locally for deterministic runtime bookkeeping, but it MUST NOT send a second provider initialization or create a replacement provider thread.

A new provider process, connection, thread, profile, provider cwd, or materially changed provider configuration is outside the binding and requires recertification/rebinding before it may carry a governed-execution claim.

The ordinary `monad-codex-runtime` live-dogfood eligibility guard remains intentionally fail-closed. Only the activation-owned wrapper may expose positive live eligibility for this profile.

## Deterministic gate

CI exercises deterministic transports only. It MUST NOT claim to certify GitHub-hosted runners or the developer's local Codex installation as the provider boundary.

The deterministic suite MUST prove both metadata binding and retained-session behavior, including that a governed workspace read can execute on the same activated thread without a second provider handshake/thread creation and that provider completion remains subordinate to Monad verification.

Required commands:

```text
cargo metadata --locked --no-deps
cargo fmt --check
cargo test --locked -p monad-codex-live-activation
cargo test --locked -p monad-codex-confinement
cargo test --locked -p monad-codex-runtime
```

## Preflight diagnostic command

On a Linux workstation, the CLI can exercise live recertification and activation metadata before the dogfood runner exists:

```text
cargo run -p monad-codex-live-activation -- verify \
  --profile monad-geh-confinement \
  --provider-cwd /absolute/isolated/provider-cwd \
  --forbidden-path /absolute/governed/repository/.monad/confinement-sentinel \
  --forbidden-marker MONAD_FORBIDDEN_SENTINEL_<unique>
```

The command exits nonzero and emits `activated: false` on any failure. A successful result contains `activated: true`, a verified nested confinement certificate, a certificate digest, the activation App Server identity, the exact activation thread id, and matching requested/active permission profile ids.

This standalone command is **preflight evidence only**. Because the CLI process exits and therefore cannot retain its App Server transport/thread, its successful output MUST NOT by itself satisfy `GEH-CF-038-LIVE-ACTIVATION` for a subsequent dogfood process.

The first real dogfood runner MUST call the in-process activation API (`certify_and_activate_runtime`) and execute through the returned `LiveActivatedRuntime` without replacing the activated provider connection/thread.

## Activation rule

The first real read-only Codex dogfood turn remains blocked until:

1. deterministic C0/C1/C2 suites are green;
2. `GEH-CF-038-CONFINEMENT` succeeds against the selected live build/profile;
3. the dogfood process itself completes `GEH-CF-038-LIVE-ACTIVATION` in-process;
4. the execution path consumes the exact retained activation connection/thread rather than opening or resuming an unbound provider thread;
5. every governed workspace observation routes through `monad_workspace_read_text` and the C1 Tool Gateway;
6. provider completion remains advisory;
7. Monad's independent Verification Controller determines completion;
8. attributable activation, operation, and verification evidence identifies the exact provider/build/profile/thread boundary used.

The next slice is the first attributable read-only dogfood runner built directly on `LiveActivatedRuntime`.
