# Governed Execution C2 Adapter Foundation Coverage

**Status:** proposed  
**Version:** 0.1.0  
**Owner:** Monad Core / EOS  
**Interface:** IFC-HARNESS-0001  
**Conformance matrix:** `testing/governed-execution-conformance.md`

## Purpose

Records the transport-neutral Monad-side adapter session/runtime foundation required before a concrete external executor adapter can claim C2 conformance.

This tranche deliberately does **not** certify Codex, Claude Code, or any other external harness as C2-conforming. It encodes the reusable C2 semantics once so every concrete adapter must pass the same compatibility, operation, completion, resume, and cancellation rules rather than reimplementing them provider-by-provider.

## Existing Codex/EOS boundary

The current EOSE v2 `codex` command already provides valuable governed execution infrastructure:

- execution identity;
- isolated branch/worktree preparation;
- governing-input fingerprints and freshness checks;
- bounded work-packet scope;
- environment capture;
- a structured completion-result claim;
- independent comparison of declared and actual Git changes;
- EOS execution lifecycle transitions and verification.

It does not currently provide a live IFC-HARNESS adapter transport. In particular, the command renders a Codex-specific execution contract but does not negotiate an adapter/interface version, bind a live adapter session, transport per-operation requests/results through the GEH Tool Gateway, persist adapter checkpoint identity, or implement explicit adapter disconnect/resume semantics.

Therefore those existing EOSE contracts remain authoritative historical/governance machinery but MUST NOT be relabeled as C2 conformance.

## Foundation semantics

The C2 foundation provides:

1. versioned `AdapterDescriptor` declarations;
2. exact interface-version and Execution Envelope-version compatibility checks;
3. explicit transport-mode compatibility;
4. mandatory adapter-feature negotiation;
5. namespaced mandatory-extension negotiation;
6. immutable run/envelope binding for each adapter session;
7. protocol errors distinct from governed execution outcomes;
8. operation responses that preserve C1 `OperationResult` dispositions;
9. a transient observation transport type separate from durable governed evidence;
10. executor completion requests routed through the independent C1 Verification Controller;
11. disconnect/resume rebinding through the C1 checkpoint/freshness/history validator;
12. cancellation expressed as a governed operation result rather than a generic protocol failure.

## C2 fixture foundation

The reusable tests implement the semantics required by GEH-CF-030 through GEH-CF-036:

- **GEH-CF-030** — compatible initialization binds one adapter session to one run/envelope;
- **GEH-CF-031** — missing mandatory adapter capability/feature explicitly rejects initialization;
- **GEH-CF-032** — governed capability denial remains distinct from backend/tool failure;
- **GEH-CF-033** — `complete.request` invokes independent verification and does not directly complete the run;
- **GEH-CF-034** — disconnected-session resume requires checkpoint, history, envelope, and governing-state revalidation;
- **GEH-CF-035** — unsupported mandatory namespaced extension explicitly rejects initialization;
- **GEH-CF-036** — an operation attempted after authoritative cancellation returns the governed `cancelled` disposition and never reaches the backend.

A concrete adapter MUST exercise these semantics with its own descriptor, transport, executor identity/configuration, and lifecycle integration before that adapter/version is C2-conforming.

## Observation boundary

Adapter observations are executor-facing transport data, not automatic durable evidence. The initial generic observation type supports UTF-8 workspace text while preserving resource identity, byte length, and content digest.

Serializability for transport MUST NOT be interpreted as an evidence-retention requirement. Evidence/provenance policy remains independently authoritative over durable retention.

## Protocol versus governance

The foundation distinguishes malformed or invalid adapter/session exchanges from valid requests that governance denies.

Examples of protocol failures include:

- missing event identity;
- inactive/disconnected session use;
- session-to-envelope binding mismatch;
- operation-to-session binding mismatch.

Examples of governed outcomes include:

- denied capability;
- denied policy;
- denied scope;
- waiting approval;
- stale envelope;
- cancellation;
- backend/tool failure.

An adapter MUST NOT collapse these categories into one generic failure channel.

## Next concrete adapter

After this foundation is independently green, the first concrete adapter SHOULD wrap the existing Monad/EOSE Codex execution path while preserving EOS sovereignty.

That adapter must add a real session/transport boundary rather than treating the historical `.codex` contract rendering alone as adapter conformance. Provider/CLI-specific details belong in the Codex adapter and MUST NOT alter the generic C2 semantics established here.
