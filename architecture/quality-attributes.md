# Quality Attributes

**Status:** Expanded product baseline

## Determinism

Equivalent supported inputs, configuration, tool/Monad versions, declared environment dimensions, and governed policy state produce equivalent semantic identities, graph/KIR serialization, diagnostics, context membership, and reproducible execution records. Parallel execution may change wall-clock timing but not canonical result/evidence ordering where determinism is declared.

## Correctness

The semantic model must reject or visibly represent unsupported/ambiguous states rather than silently normalize them into misleading truth. Conformance fixtures exercise positive, negative, boundary, contradiction, stale-memory, policy, and agent-disagreement cases.

## Explainability

Every consequential derived relationship, diagnostic, score change, query/explanation path, context selection, policy/autonomy decision, automation action, and execution decision can identify its canonical inputs, external evidence where applicable, and governing rule.

## Performance

MVP establishes measured budgets for cold startup, repository discovery, full graph compilation on reference repositories, common query latency, context generation, and peak memory. Post-MVP benchmark profiles extend this to parallel scheduling, caches, provider routing, state finalization, and large workspace workloads.

A long-range scale profile targets at least 10,000 lightweight internal scheduler/graph operations per second on declared reference hardware. Eligible local governed state transitions target 400 ms p95 finalization after all required inputs are available. These are evidence-driven benchmark targets, not substitutes for correctness and not promises about external tool or network latency.

## Scalability

Design targets repository sizes materially beyond toy fixtures without assuming distributed infrastructure. Indexing/incrementality should allow scaling locally first. Optional external graph/vector backends, distributed caches, and multi-tenant services are introduced through versioned adapters only when evidence justifies them.

## Reliability and recovery

Derived state corruption or interruption is recoverable through validation/rebuild. Atomic writes protect canonical generated artifacts. Unknown/partial execution state is never represented as clean success. Remote/provider/integration workflows use timeout/cancellation, bounded retries, exponential backoff, idempotency-aware retry, circuit breakers, and failure isolation.

## Security

Inspection is non-executing by default; path/symlink handling is defensive; external commands/plugins/integrations are explicit capabilities; secrets/context are minimized; dependency provenance is controlled; and AI/remote boundaries are opt-in and auditable. Agent/tool capability sandboxing, prompt-injection defenses, secret masking, tenant/workspace isolation, signed attestations, and least-authority defaults apply to consequential execution paths.

## Cryptographic agility

Attestation and privileged-identity mechanisms must support versioned algorithm profiles, key rotation/revocation, multi-party approval/signature policies, and migration to post-quantum algorithms such as ML-DSA without rewriting semantic history. Conventional profiles may include Ed25519, P-256, and secp256k1 where appropriate.

## Auditability

Human actions, agent executions, policy evaluations, autonomy changes, attestations, changes, rollbacks, release decisions, and resulting artifacts must be reconstructable from durable correlated evidence. Audit exports should be tamper-evident and distinguish canonical repository history from external operational evidence.

## Privacy

Hosted analytics, vector memory, semantic/result caches, files/media, agent execution records, and integrations must have explicit workspace/tenant isolation, retention, classification, and access rules. Optional visitor/geography/device analytics are never required for local core operation.

## Portability

The local core should support major developer platforms through a deliberately bounded compatibility matrix and remain useful offline. Optional deployment profiles include containers, Nix, air-gapped/on-prem, and major clouds. Platform-specific variance cannot contaminate canonical semantic identity without being declared.

## Provider independence

AI, storage, automation, cloud, IDE, and integration capabilities use explicit contracts so no single external provider becomes a prerequisite for canonical semantic operation.

## Evolvability

Core semantic concepts, adapters, storage/indexes, CLI, AI integrations, policy, execution, observation, MCP/LSP, plugins, registries, and deployment surfaces have boundaries enabling replacement. Public contracts gain versioning before external reliance. Modular-first evolution precedes repository/service splitting.

## Progressive trust

Agents and automations begin with minimal authority. Promotion to stronger autonomy requires defined reliability evidence and policy approval; demotion/revocation remains possible. Cross-harness agreement is evidence, not authority by itself.

## Observability

Operational components expose structured logs, metrics, and traces through OpenTelemetry-compatible boundaries where applicable. Records correlate to product goals, epics/features, Work Packets, executions, providers, costs/tokens where available, evidence, and resulting state.

## Usability / developer experience

First-run behavior, diagnostics, command naming, structured output, shell completion, score/health explanations, dashboards, IDE integrations, and automation reviews reduce cognitive load rather than expose internal compiler architecture unnecessarily.

## Accessibility of evidence

Dashboards, scores, summaries, embeddings, caches, and AI explanations must link back to underlying canonical or explicitly external evidence. Derived intelligence may accelerate understanding but may not become the only route to inspect a consequential claim.

## Testability

Pure semantic transformations are preferred where practical; golden/conformance/property tests cover canonicalization and graph invariants; end-to-end fixtures prove clean-clone behavior. Security, agent, integration, deployment, cryptographic, parallelism, cache isolation, recovery, and performance profiles gain dedicated conformance/acceptance suites as they enter refinement.
