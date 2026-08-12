# Success Criteria

**Status:** Proposed stabilization baseline

## MVP success

MVP Release 1 succeeds when a new user can install Monad, inspect a representative repository, obtain a deterministic semantic graph, receive actionable validation, query/explain meaningful relationships, and generate a bounded agent context package without a hosted dependency.

Required evidence includes:

- identical supported inputs yield equivalent canonical semantic output;
- graph entities/relationships cite canonical source locations/hashes;
- invalid or contradictory engineering knowledge yields stable diagnostics;
- query/explain answers can show their provenance;
- context packages materially reduce irrelevant repository content while retaining governing constraints;
- a clean-clone test reproduces the demonstrated workflow;
- security tests show secrets/ignored sensitive data are not included by default;
- first-run documentation can be followed by someone outside the implementation session.

## Product utility indicators

Track, once representative trials exist:

- time to answer common repository-understanding questions;
- percentage of graph/query answers with complete provenance;
- useful contradictions/traceability gaps found before PR review;
- context-package size compared with naïve repository context;
- false-positive/false-negative rates for semantic validation;
- incremental execution avoided compared with broad baseline execution;
- reproducibility failures across supported environments;
- user repeat usage for supported engineering tasks.

## Guardrails

Monad must not achieve apparent utility by:

- uploading canonical repositories by default;
- hiding unsupported syntax or uncertain inference;
- allowing agents to exceed Work Packet authority;
- weakening native compiler/test results;
- making generated machine state an editable competing truth;
- requiring excessive metadata maintenance for trivial value; or
- producing nondeterministic graph identity for equivalent input.

## Post-MVP success

Later releases should demonstrate scalable repository size, richer semantic diff/incrementality, broader toolchain adapters, policy enforcement, plugin conformance, cross-repository knowledge, and safe hosted collaboration. Each requires its own measurable target rather than inheriting MVP claims.