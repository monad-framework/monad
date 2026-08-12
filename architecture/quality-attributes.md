# Quality Attributes

**Status:** Proposed stabilization baseline

## Determinism

Equivalent supported inputs, configuration, tool/Monad versions, and declared environment dimensions produce equivalent semantic identities, graph/KIR serialization, diagnostics, and context membership.

## Correctness

The semantic model must reject or visibly represent unsupported/ambiguous states rather than silently normalize them into misleading truth. Conformance fixtures exercise positive, negative, boundary, and contradiction cases.

## Explainability

Every consequential derived relationship, diagnostic, query/explanation path, context selection, or execution decision can identify its canonical inputs and governing rule.

## Performance

MVP establishes measured budgets for cold startup, repository discovery, full graph compilation on reference repositories, common query latency, context generation, and peak memory. Budgets are ratcheted from evidence rather than guessed into false SLOs.

## Scalability

Design targets repository sizes materially beyond toy fixtures without assuming distributed infrastructure. Indexing/incrementality should allow later scaling before remote execution is considered necessary.

## Reliability and recovery

Derived state corruption or interruption is recoverable through validation/rebuild. Atomic writes protect canonical generated artifacts. Unknown/partial execution state is never represented as clean success.

## Security

Inspection is non-executing by default, path/symlink handling is defensive, external commands/plugins are explicit capabilities, secrets/context are minimized, dependency provenance is controlled, and AI/remote boundaries are opt-in and auditable.

## Portability

The local core should support major developer platforms through a deliberately bounded compatibility matrix. Platform-specific variance cannot contaminate canonical semantic identity without being declared.

## Evolvability

Core semantic concepts, adapters, storage/indexes, CLI, and AI integrations have boundaries enabling replacement. Public contracts gain versioning before external reliance.

## Usability / developer experience

First-run behavior, diagnostics, command naming, structured output, shell completion, and explanations reduce cognitive load rather than expose internal compiler architecture unnecessarily.

## Testability

Pure semantic transformations are preferred where practical; golden/conformance/property tests cover canonicalization and graph invariants; end-to-end fixtures prove clean-clone behavior.