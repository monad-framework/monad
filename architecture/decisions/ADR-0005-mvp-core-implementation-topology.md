# ADR-0005: MVP Core Implementation Topology

**Status:** Accepted
**Date:** 2026-08-12
**Decision scope:** implementation language and source topology for the Monad MVP semantic kernel

## Context

The first six MVP Work Packets now have language-independent behavioral contracts, but implementation authorization requires an exact source/test boundary. The MVP target favors a single local binary, deterministic parsing/graph work, strong memory/type safety, predictable distribution, and later growth into performance-sensitive semantic infrastructure. The repository's EOS control tooling is Python and should remain operationally separate from the product runtime.

## Proposed decision

1. Implement the Monad MVP product runtime in **Rust** using the stable toolchain and Cargo.
2. Start with a deliberately small workspace rather than one crate per conceptual subsystem:
   - `crates/monad-core` — library containing explicit modules for workspace/config, source identity, ingestion, graph/KIR/query/context as those capabilities arrive;
   - `crates/monad-cli` — the `monad` binary and presentation/argument boundary.
3. Keep semantic behavior in `monad-core`; CLI code may adapt inputs/outputs but must not own duplicate semantic rules.
4. Add crates only when a boundary has an independent compilation/API/ownership reason. Architectural modularity precedes repository/crate proliferation.
5. EOS remains under `tools/eos`/`scripts/eos` and is not linked into the Monad runtime. EOS governs development; Monad is the product being developed.
6. MVP distribution targets one `monad` executable per supported platform. Hosted services, dynamic plugin loading, FFI, and multi-process decomposition are out of scope for this decision.

## Rationale

Rust fits the product's single-binary/local-first target, provides strong type/memory safety for parsers and graph structures, allows tight control over deterministic data representation and performance, and avoids introducing a runtime service dependency for the semantic kernel. Two starting crates preserve separation between semantics and CLI without fragmenting the codebase prematurely.

## Alternatives considered

### Go core/CLI

Go offers excellent build simplicity and a strong single-binary story. It remains credible, but the semantic kernel is expected to become parser/graph/IR heavy and benefit from Rust's stronger algebraic data modeling and ownership discipline. If implementation evidence shows unacceptable complexity/productivity cost, this proposal should be reconsidered before public compatibility surfaces harden.

### TypeScript/Bun core

Excellent for developer tooling and UI-adjacent work, but a JS runtime dependency and weaker control over low-level representation make it less aligned with the intended long-lived semantic kernel. TypeScript remains suitable for future integrations/UI where appropriate.

### Python core

Excellent for iteration and already used by EOS, but distribution/runtime reproducibility and performance characteristics are less aligned with the single-binary product target. Python remains appropriate for engineering automation and research.

## Acceptance gate

Accept this ADR only after confirming the team is willing to standardize MVP product implementation on Rust. Until then, Work Packets may be semantically refined but MUST NOT claim a Rust file boundary as authorized implementation scope.
