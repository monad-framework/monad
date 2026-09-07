# Governed Execution C2 Codex Live Activation Binding

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Precondition:** `GEH-CF-038-CONFINEMENT`  
**Runtime:** `crates/monad-codex-runtime`  
**Confinement verifier:** `crates/monad-codex-confinement`  
**Activation layer:** `crates/monad-codex-live-activation`

## Purpose

Bind a successful provider-effect confinement result to the actual App Server connection and thread selected for live governed execution.

A certificate from an earlier process is not accepted as a perpetual authorization token. The activation layer reruns confinement immediately before activation, then starts a fresh App Server connection and requires the same build identity, platform, named permission profile, provider runtime cwd, and Monad dynamic-tool boundary.

This slice establishes activation binding only. It does not yet claim that a real model turn has completed a Monad-governed dogfood task.

## GEH-CF-040-LIVE-ACTIVATION

**Type:** activation / attributable binding / fail-closed  
**Expected:** pass before the first live governed Codex turn

The activation command MUST:

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
13. emit an activation binding containing the confinement certificate digest and the exact activation thread/profile identity.

The confinement certificate remains evidence, not capability, authority, approval, or completion.

## Deterministic gate

CI exercises deterministic transports only. It MUST NOT claim to certify GitHub-hosted runners or the developer's local Codex installation as the provider boundary.

Required commands:

```text
cargo metadata --locked --no-deps
cargo fmt --check
cargo test --locked -p monad-codex-live-activation
cargo test --locked -p monad-codex-confinement
cargo test --locked -p monad-codex-runtime
```

## Live activation command

On the already-certified Linux workstation, from the Monad repository root:

```text
cargo run -p monad-codex-live-activation -- verify \
  --profile monad-geh-confinement \
  --provider-cwd /absolute/isolated/provider-cwd \
  --forbidden-path /absolute/governed/repository/.monad/confinement-sentinel \
  --forbidden-marker MONAD_FORBIDDEN_SENTINEL_<unique>
```

The command exits nonzero and emits `activated: false` on any failure.

A successful result MUST contain `activated: true`, a verified nested confinement certificate, a certificate digest, the activation App Server identity, the exact activation thread id, and matching requested/active permission profile ids.

## Activation rule

The first real read-only Codex dogfood turn remains blocked until:

1. deterministic C0/C1/C2 suites are green;
2. `GEH-CF-038-CONFINEMENT` passes against the selected live build/profile;
3. `GEH-CF-040-LIVE-ACTIVATION` passes immediately before the dogfood run;
4. the dogfood execution path consumes the activated connection/thread rather than opening an unbound provider thread;
5. every governed workspace observation routes through `monad_workspace_read_text` and the C1 Tool Gateway;
6. provider completion remains advisory;
7. Monad's independent Verification Controller determines completion.

The next slice is the attributable read-only dogfood runner that consumes this activation boundary.
