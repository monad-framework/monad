# Product Constraints

**Status:** Expanded product baseline

## PC-001 — Local-first core

Repository discovery, semantic compilation, validation, query/explain, MVP context generation, and core governance must operate without mandatory hosted services.

## PC-002 — Deterministic semantic core

Equivalent supported inputs/configuration/Monad version must produce equivalent canonical semantic identity and output. Probabilistic AI output cannot define core graph truth.

## PC-003 — Human-readable canonical source

MVP assumes human-readable Git artifacts are canonical. Machine companions are generated derivatives with source hashes/provenance.

## PC-004 — Git-native history

Monad does not replace Git history/branching/PR review. It may enrich, automate, attest, validate, and restore through governed policies.

## PC-005 — Native-tool authority

Language compilers, package managers, test runners, formatters, and other domain tools remain authoritative for their native semantics unless an accepted adapter contract says otherwise.

## PC-006 — Bounded AI authority

Agents must receive explicit scope and may not silently accept architecture, specifications, risk, policy exceptions, security posture, or releases.

## PC-007 — Explainability

Consequential diagnostics, graph relationships, context selections, policy/execution decisions, autonomy promotions, score changes, and automation actions must retain enough provenance to explain their basis.

## PC-008 — Security and secret minimization

Repository ingestion and context generation must honor exclusions, data classification, capability sandboxing, prompt-injection defenses, secret masking, and least-context principles; secrets are never considered ordinary engineering context.

## PC-009 — Polyglot evolution

The architecture must not hard-code one implementation language/toolchain as the product model. MVP implementation may choose a narrow stack while interfaces remain explicit.

## PC-010 — Bootstrap resource discipline

The project should prefer best-of-breed open-source dependencies and avoid unnecessary paid infrastructure/API requirements for the local core.

## PC-011 — Backward-compatible evolution

Public schemas, KIR, configuration, CLI structured output, plugin APIs, registry protocols, MCP/LSP surfaces, adapters, attestations, storage backends, and provider contracts must establish explicit versioning before external stability is promised.

## PC-012 — No false completeness

Unsupported constructs, incomplete graph knowledge, uncertain relationships, stale memory, reviewer disagreement, and missing evidence must be visible rather than guessed into a complete-looking model.

## PC-013 — Progressive trust only

No agent, provider, plugin, integration, or automation begins with unrestricted authority. Stronger authority requires explicit policy, evidence, approval, and a reversible demotion path.

## PC-014 — Operator decision stewardship

Automation may reduce typing and routine coordination, but humans remain responsible for framing unresolved decisions and for disposition of architecture, risk, security, policy exceptions, and release authority unless governance explicitly delegates a bounded decision class.

## PC-015 — Modular-first ecosystem evolution

Stable module/contracts precede repository/service splitting. Additional repositories, services, plugins, packs, registries, and hosted controls require evidence of ownership, deployment, scale, or compatibility need.

## PC-016 — Provider and vendor independence

Canonical core operation must not require a single AI provider, cloud vendor, hosted database, automation vendor, IDE, or integration platform.

## PC-017 — Optional remote/hosted surfaces

Hosted analytics, custom domains, galleries, managed deployment, multi-tenant caches, and cloud storage are optional interaction/operations capabilities. Their absence cannot invalidate local semantic truth.

## PC-018 — Air-gapped viability

Security-sensitive deployments must have a path to no-network/no-exfiltration operation with local models/tools or disabled AI features and auditable attempts to cross the boundary.

## PC-019 — Cryptographic agility

Attestation and identity algorithms are versioned profiles rather than permanent semantic assumptions. Key rotation, revocation, multi-party policy, and post-quantum migration must be possible without rewriting historical engineering meaning.

## PC-020 — Isolation boundaries

Worktrees/branches, tenants/workspaces, caches, vector stores, files, plugins, integrations, and agent capabilities must have explicit isolation and provenance boundaries.

## PC-021 — Rebase/merge policy is declarative

A rebase-first branch policy may be mandatory for configured autonomous execution profiles, but Git integration strategy remains a governed repository policy rather than an unconditional semantic law of Monad.

## PC-022 — Performance targets never weaken correctness

Parallelism, throughput, caching, and fast state-finalization targets may not weaken determinism, safety, provenance, native-tool authority, or release evidence.

## PC-023 — External runtime compatibility is adapter-scoped

Compatibility with external bytecode/runtime ecosystems, including any EVM profile, must remain isolated behind an adapter contract and may not redefine the knowledge/control planes.

## PC-024 — Privacy-governed analytics

Hosted traffic/geography/device analytics must be optional, minimized, separable from canonical engineering data, and controlled by explicit retention/access/privacy policies.

## PC-025 — Generated intelligence is not sole authority

Scores, dashboards, embeddings, caches, AI summaries, and automation state are derived views. Users must be able to inspect the underlying canonical evidence or explicit external evidence record.
