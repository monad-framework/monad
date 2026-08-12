# Architecture Principles

**Status:** Proposed stabilization baseline

1. **Deterministic semantic kernel.** Parsing, identity, graph construction, validation, canonical serialization, and core planning do not depend on LLM output.
2. **Ports around native tools.** Integrations implement explicit capabilities; native tools are not hidden behind leaky universal abstractions.
3. **Rebuildable derived state.** Graph indexes/caches/publications are disposable when canonical source and declared external evidence remain.
4. **Provenance by construction.** Derived entities/edges/findings retain source/rule identity from creation.
5. **Typed relationships.** Prefer explicit semantic edges to conventions inferred repeatedly by consumers.
6. **Small trusted core.** Keep code that defines canonical meaning narrow, testable, and dependency-conscious.
7. **Separation of knowledge, control, execution, observation, interaction.** Avoid modules that own truth, permission, command execution, and presentation simultaneously.
8. **Stable errors are API.** Diagnostics have identifiers, severity, locations/entities, causes, and machine forms.
9. **Compatibility is explicit.** KIR, config, structured CLI output, plugin APIs, and protocols declare versions/migrations before stability guarantees.
10. **Security at boundaries.** Parsing, path traversal, symlinks, commands, plugins, secrets, AI context, caches, and remote services receive explicit threat treatment.
11. **Local-first architecture.** Core usefulness does not depend on network reachability.
12. **Incremental by design, not premature optimization.** Record content/dependency identity now; optimize invalidation/execution after correctness.
13. **Modularize early, distribute late.** A monolithic deployable with clear internal boundaries is preferable to premature distributed complexity.
14. **Explainability over magic.** A user can inspect why Monad concluded, selected, invalidated, or executed something.